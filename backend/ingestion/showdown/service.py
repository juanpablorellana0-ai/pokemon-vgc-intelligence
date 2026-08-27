"""ShowdownSyncService — versioned sync pipeline.

Pipeline (per spec):

  ls-remote → compare with active → (if changed) fetch → parse/normalize
    → validate → run compatibility tests → create versioned dataset
    → activate only if all checks pass

The service NEVER overwrites the active dataset until validation and
tests pass. On failure the previously active dataset stays active.
On success the previous version is kept as the rollback candidate.

Each import has a unique ``import_id`` (=history id). Normalized data is
written to Mongo carrying that ``import_id``; the active pointer stores
the currently active id. Rollback flips the pointer back.
"""
from __future__ import annotations
import asyncio
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from . import config, lock
from .logger import (
    log,
    EVT_STARTED,
    EVT_UPDATE_AVAILABLE,
    EVT_UP_TO_DATE,
    EVT_IMPORT_STARTED,
    EVT_VALIDATION_STARTED,
    EVT_VALIDATION_FAILED,
    EVT_TESTS_STARTED,
    EVT_TESTS_FAILED,
    EVT_VERSION_ACTIVATED,
    EVT_ROLLBACK_STARTED,
    EVT_ROLLBACK_COMPLETED,
    EVT_LOCKED,
    EVT_ERROR,
)
from .models import ShowdownSyncHistory, SyncStatus, ShowdownActiveDataset
from . import parser_bridge, importer

ACTIVE_POINTER_ID = "showdown_active_dataset"
HISTORY_COLLECTION = "showdown_sync_history"
POINTERS_COLLECTION = "showdown_pointers"


class ShowdownSyncService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def check(self) -> dict:
        """Non-mutating — reports remote HEAD vs active commit."""
        remote = await self._ls_remote()
        active = await self.get_active()
        update_available = bool(
            remote and (active.activeCommit is None or remote != active.activeCommit)
        )
        if update_available:
            log(EVT_UPDATE_AVAILABLE, remote=remote, active=active.activeCommit)
        else:
            log(EVT_UP_TO_DATE, remote=remote, active=active.activeCommit)
        return {
            "repositoryUrl": config.repo_url(),
            "branch": config.branch(),
            "remoteCommit": remote,
            "activeCommit": active.activeCommit,
            "updateAvailable": update_available,
        }

    async def sync(self, force: bool = False, pin_commit: Optional[str] = None) -> ShowdownSyncHistory:
        """Full pipeline. Idempotent when up-to-date unless ``force``.

        If ``pin_commit`` is provided, that exact SHA is used instead of
        the remote HEAD — the connectivity check may return a different
        commit than the one that should be canonically imported.
        """
        owner = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        history = ShowdownSyncHistory(
            repositoryUrl=config.repo_url(),
            branch=config.branch(),
            status=SyncStatus.STARTED,
            importerVersion=config.importer_version(),
            appVersion=config.app_version(),
        )

        if not await lock.acquire(self.db, owner):
            history.status = SyncStatus.FAILED_LOCKED
            history.errorMessage = "another sync is already running"
            history.completedAt = datetime.now(timezone.utc)
            await self._persist_history(history)
            log(EVT_LOCKED)
            return history

        try:
            log(EVT_STARTED, repositoryUrl=history.repositoryUrl, branch=history.branch)
            active = await self.get_active()
            history.previousCommit = active.activeCommit

            remote = pin_commit or await self._ls_remote()
            history.newCommit = remote

            if not remote:
                history.status = SyncStatus.FAILED_FETCH
                history.errorMessage = "could not determine remote commit"
                log(EVT_ERROR, reason=history.errorMessage)
                return history

            if remote == active.activeCommit and not force:
                history.status = SyncStatus.UP_TO_DATE
                log(EVT_UP_TO_DATE, commit=remote)
                return history

            log(EVT_IMPORT_STARTED, commit=remote)
            try:
                dataset_dir = await self._fetch(remote)
                history.status = SyncStatus.FETCHED
            except Exception as exc:  # noqa: BLE001
                history.status = SyncStatus.FAILED_FETCH
                history.errorMessage = f"fetch failed: {exc}"
                log(EVT_ERROR, reason=history.errorMessage)
                return history

            log(EVT_VALIDATION_STARTED, commit=remote)
            try:
                parsed = await self._parse(dataset_dir)
                report = await importer.normalize_and_store(
                    self.db, parsed, import_id=history.id,
                )
                errors = report.validation_errors
                history.recordsDiscovered = sum(report.counts.values())
                history.recordsImported = sum(report.counts.values())
                history.recordsRejected = report.total_rejected()
            except Exception as exc:  # noqa: BLE001
                errors = [f"validator crashed: {exc}"]
                report = None
            history.validationErrors = errors
            if errors:
                history.status = SyncStatus.FAILED_VALIDATION
                history.errorMessage = "validation failed"
                log(EVT_VALIDATION_FAILED, errors=errors[:5], commit=remote)
                # Roll back partial import for this import_id.
                await importer.wipe_import(self.db, history.id)
                return history
            history.status = SyncStatus.VALIDATED

            log(EVT_TESTS_STARTED, commit=remote)
            try:
                results = await self._run_tests(dataset_dir, history.id)
            except Exception as exc:  # noqa: BLE001
                results = {"error": f"tests crashed: {exc}", "passed": False}
            history.testResults = results
            if not results.get("passed"):
                history.status = SyncStatus.FAILED_TESTS
                history.errorMessage = "compatibility tests failed"
                log(EVT_TESTS_FAILED, results=results, commit=remote)
                # Do not activate — wipe this import's docs so nothing lingers.
                await importer.wipe_import(self.db, history.id)
                return history
            history.status = SyncStatus.TESTED

            await self._activate(remote, dataset_dir, previous=active,
                                 import_id=history.id)
            history.status = SyncStatus.ACTIVATED
            history.activated = True
            log(EVT_VERSION_ACTIVATED, commit=remote, dir=dataset_dir,
                import_id=history.id)
            return history
        finally:
            history.completedAt = datetime.now(timezone.utc)
            history.duration_ms = int(
                (history.completedAt - started_at).total_seconds() * 1000
            )
            await self._persist_history(history)
            await lock.release(self.db, owner)

    async def rollback(self) -> dict:
        """Switch active pointer back to the previous known-good dataset."""
        active = await self.get_active()
        if not active.rollbackAvailable or not active.previousCommit:
            return {"rolled_back": False, "reason": "no previous version"}

        log(EVT_ROLLBACK_STARTED, from_commit=active.activeCommit,
            to_commit=active.previousCommit)

        prev_import = getattr(active, "previousImportId", None)
        curr_import = getattr(active, "activeImportId", None)
        new_doc = {
            "_id": ACTIVE_POINTER_ID,
            "activeCommit": active.previousCommit,
            "activeDir": active.previousDir,
            "activatedAt": datetime.now(timezone.utc),
            "previousCommit": active.activeCommit,
            "previousDir": active.activeDir,
            "rollbackAvailable": True,
            "activeImportId": prev_import,
            "previousImportId": curr_import,
        }
        await self.db[POINTERS_COLLECTION].replace_one(
            {"_id": ACTIVE_POINTER_ID}, new_doc, upsert=True,
        )

        h = ShowdownSyncHistory(
            repositoryUrl=config.repo_url(),
            branch=config.branch(),
            previousCommit=active.activeCommit,
            newCommit=active.previousCommit,
            status=SyncStatus.ROLLED_BACK,
            activated=True,
            completedAt=datetime.now(timezone.utc),
            importerVersion=config.importer_version(),
            appVersion=config.app_version(),
        )
        await self._persist_history(h)
        log(EVT_ROLLBACK_COMPLETED, active=active.previousCommit)
        return {
            "rolled_back": True,
            "activeCommit": active.previousCommit,
            "previousCommit": active.activeCommit,
        }

    async def status(self) -> dict:
        """Data health report — for admin dashboards."""
        active = await self.get_active()
        last_ok = await self.db[HISTORY_COLLECTION].find_one(
            {"activated": True}, sort=[("completedAt", -1)], projection={"_id": 0}
        )
        last_any = await self.db[HISTORY_COLLECTION].find_one(
            {}, sort=[("startedAt", -1)], projection={"_id": 0}
        )
        return {
            "activeCommit": active.activeCommit,
            "activatedAt": active.activatedAt,
            "previousCommit": active.previousCommit,
            "rollbackAvailable": active.rollbackAvailable,
            "lastSuccessfulSync": last_ok,
            "lastAttemptedSync": last_any,
            "importerVersion": config.importer_version(),
            "appVersion": config.app_version(),
            "locked": await lock.is_locked(self.db),
        }

    # ------------------------------------------------------------------
    # Internal — safe to monkeypatch from tests
    # ------------------------------------------------------------------
    async def _ls_remote(self) -> Optional[str]:
        """Ask GitHub for the current HEAD of ``branch`` — no credentials."""
        def _run() -> Optional[str]:
            try:
                out = subprocess.run(
                    ["git", "ls-remote", config.repo_url(), f"refs/heads/{config.branch()}"],
                    capture_output=True,
                    text=True,
                    timeout=25,
                    check=False,
                )
                if out.returncode != 0 or not out.stdout.strip():
                    return None
                # Output: "<sha>\trefs/heads/master"
                sha = out.stdout.strip().split()[0]
                # Sanity — a SHA is 40 hex chars.
                if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha):
                    return sha
                return None
            except Exception:
                return None

        return await asyncio.get_running_loop().run_in_executor(None, _run)

    async def _fetch(self, commit: str) -> str:
        """Materialize a dataset directory for ``commit`` and return its path.

        Clones the public Showdown repo at the exact commit SHA when
        ``SHOWDOWN_ENABLE_CLONE`` is enabled. The cloned tree is the RAW
        SNAPSHOT preserved on disk and reused as-is for parsing.
        """
        root = Path(config.datasets_dir())
        root.mkdir(parents=True, exist_ok=True)
        dataset_dir = root / f"showdown_dataset_{commit[:12]}"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        marker = dataset_dir / "MANIFEST.json"
        marker.write_text(
            '{"commit": "%s", "branch": "%s", "clone_enabled": %s}\n'
            % (commit, config.branch(), "true" if config.clone_enabled() else "false")
        )

        repo_dir = dataset_dir / "repo"
        if config.clone_enabled() and not (repo_dir / ".git").is_dir():
            def _clone_at_sha() -> None:
                # Anonymous clone of a public repo, then checkout the exact SHA
                # so the dataset is deterministic (never blindly "latest").
                subprocess.run(
                    ["git", "clone", "--quiet", config.repo_url(), str(repo_dir)],
                    capture_output=True, check=True, timeout=300,
                )
                subprocess.run(
                    ["git", "-C", str(repo_dir), "checkout", "--quiet", commit],
                    capture_output=True, check=True, timeout=60,
                )
            await asyncio.get_running_loop().run_in_executor(None, _clone_at_sha)

        return str(dataset_dir)

    async def _parse(self, dataset_dir: str) -> dict:
        """Invoke the Node parser and return the parsed data dict."""
        repo_dir = Path(dataset_dir) / "repo"
        if not repo_dir.is_dir():
            raise RuntimeError(f"repo not present at {repo_dir}")

        def _do():
            return parser_bridge.parse_repo(str(repo_dir), dataset_dir)

        result, errors = await asyncio.get_running_loop().run_in_executor(None, _do)
        if errors and any(v and v != "file not present" for v in errors.values()):
            log(EVT_ERROR, reason="parser reported per-file errors",
                errors={k: v for k, v in errors.items() if v})
        return result

    async def _validate(self, dataset_dir: str) -> list[str]:
        """Legacy hook — kept for callers/tests that stub this directly.

        The real validation now happens inside
        :func:`importer.normalize_and_store` and its result is threaded
        through the ``sync`` flow. This method just checks the on-disk
        layout for callers that need a lightweight check.
        """
        errors: list[str] = []
        p = Path(dataset_dir)
        if not p.is_dir():
            errors.append(f"dataset dir missing: {dataset_dir}")
        elif not (p / "MANIFEST.json").is_file():
            errors.append("MANIFEST.json missing")
        return errors

    async def _run_tests(self, dataset_dir: str, import_id: str | None = None) -> dict:
        """Compatibility tests against persisted data.

        When ``import_id`` is provided we run the full smoke suite over
        the imported docs. Otherwise fall back to a manifest-only check
        (used by legacy tests that stub the fetch pipeline).
        """
        if import_id is None:
            try:
                import json as _json
                m = Path(dataset_dir) / "MANIFEST.json"
                data = _json.loads(m.read_text())
                return {"passed": True, "manifest": data}
            except Exception as exc:  # noqa: BLE001
                return {"passed": False, "error": str(exc)}
        return await importer.smoke_tests(self.db, import_id)

    # ------------------------------------------------------------------
    # Pointer + history persistence
    # ------------------------------------------------------------------
    async def _activate(self, commit: str, dataset_dir: str,
                        previous: ShowdownActiveDataset,
                        import_id: str) -> None:
        new = ShowdownActiveDataset(
            activeCommit=commit,
            activeDir=dataset_dir,
            activatedAt=datetime.now(timezone.utc),
            previousCommit=previous.activeCommit,
            previousDir=previous.activeDir,
            rollbackAvailable=bool(previous.activeCommit),
        )
        # Attach the active import_id in the pointer document so read
        # endpoints can filter by it directly.
        doc = new.model_dump()
        doc["activeImportId"] = import_id
        doc["previousImportId"] = getattr(previous, "activeImportId", None)
        doc["_id"] = ACTIVE_POINTER_ID
        await self.db[POINTERS_COLLECTION].replace_one(
            {"_id": ACTIVE_POINTER_ID}, doc, upsert=True,
        )

    async def _write_active(self, ptr: ShowdownActiveDataset) -> None:
        doc = ptr.model_dump()
        doc["_id"] = ACTIVE_POINTER_ID
        await self.db[POINTERS_COLLECTION].replace_one(
            {"_id": ACTIVE_POINTER_ID}, doc, upsert=True,
        )

    async def get_active(self) -> ShowdownActiveDataset:
        doc = await self.db[POINTERS_COLLECTION].find_one(
            {"_id": ACTIVE_POINTER_ID}, {"_id": 0},
        )
        if not doc:
            return ShowdownActiveDataset()
        # Preserve import ids on the returned object (as ad-hoc attributes)
        import_id = doc.pop("activeImportId", None)
        prev_import_id = doc.pop("previousImportId", None)
        obj = ShowdownActiveDataset(**doc)
        object.__setattr__(obj, "activeImportId", import_id)
        object.__setattr__(obj, "previousImportId", prev_import_id)
        return obj

    async def get_active_import_id(self) -> Optional[str]:
        doc = await self.db[POINTERS_COLLECTION].find_one(
            {"_id": ACTIVE_POINTER_ID}, {"_id": 0, "activeImportId": 1},
        )
        return (doc or {}).get("activeImportId")

    async def _persist_history(self, h: ShowdownSyncHistory) -> None:
        doc = h.model_dump()
        # Never leak Mongo _id back to callers — use our own id.
        doc.pop("_id", None)
        await self.db[HISTORY_COLLECTION].insert_one(doc)


# For manual cleanup in tests
def _wipe_local_datasets() -> None:  # pragma: no cover - test helper
    root = Path(config.datasets_dir())
    if root.exists():
        shutil.rmtree(root)
