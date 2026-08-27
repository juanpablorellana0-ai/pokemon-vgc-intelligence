"""ShowdownSyncService — versioned sync pipeline.

Pipeline (per spec):

  ls-remote → compare with active → (if changed) fetch → parse/normalize
    → validate → run compatibility tests → create versioned dataset
    → activate only if all checks pass

The service NEVER overwrites the active dataset until validation and
tests pass. On failure the previously active dataset stays active.
On success the previous version is kept as the rollback candidate.

This module does NOT import the Showdown dataset yet — ``_fetch`` only
records the commit and creates a dataset directory placeholder. Actual
cloning is gated behind ``SHOWDOWN_ENABLE_CLONE`` for future phases.

Every heavy step (``_ls_remote``, ``_fetch``, ``_validate``, ``_run_tests``)
is a method so tests can monkeypatch it independently.
"""
from __future__ import annotations
import asyncio
import os
import shutil
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

    async def sync(self, force: bool = False) -> ShowdownSyncHistory:
        """Full pipeline. Idempotent when up-to-date unless ``force``."""
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

            remote = await self._ls_remote()
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
                errors = await self._validate(dataset_dir)
            except Exception as exc:  # noqa: BLE001
                errors = [f"validator crashed: {exc}"]
            history.validationErrors = errors
            if errors:
                history.status = SyncStatus.FAILED_VALIDATION
                history.errorMessage = "validation failed"
                log(EVT_VALIDATION_FAILED, errors=errors, commit=remote)
                return history
            history.status = SyncStatus.VALIDATED

            log(EVT_TESTS_STARTED, commit=remote)
            try:
                results = await self._run_tests(dataset_dir)
            except Exception as exc:  # noqa: BLE001
                results = {"error": f"tests crashed: {exc}", "passed": False}
            history.testResults = results
            if not results.get("passed"):
                history.status = SyncStatus.FAILED_TESTS
                history.errorMessage = "compatibility tests failed"
                log(EVT_TESTS_FAILED, results=results, commit=remote)
                return history
            history.status = SyncStatus.TESTED

            await self._activate(remote, dataset_dir, previous=active)
            history.status = SyncStatus.ACTIVATED
            history.activated = True
            log(EVT_VERSION_ACTIVATED, commit=remote, dir=dataset_dir)
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

        log(EVT_ROLLBACK_STARTED, from_commit=active.activeCommit, to_commit=active.previousCommit)

        new_active = ShowdownActiveDataset(
            activeCommit=active.previousCommit,
            activeDir=active.previousDir,
            activatedAt=datetime.now(timezone.utc),
            previousCommit=active.activeCommit,   # keep for redo
            previousDir=active.activeDir,
            rollbackAvailable=True,
        )
        await self._write_active(new_active)

        # Record in history
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
        log(EVT_ROLLBACK_COMPLETED, active=new_active.activeCommit)
        return {
            "rolled_back": True,
            "activeCommit": new_active.activeCommit,
            "previousCommit": new_active.previousCommit,
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

        In this phase we do NOT clone by default — only create a marker
        directory recording the commit. Enable cloning by setting
        ``SHOWDOWN_ENABLE_CLONE=1`` in a future phase.
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

        if config.clone_enabled():
            # Reserved for a future phase — kept minimal on purpose.
            def _clone():
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", config.branch(),
                     config.repo_url(), str(dataset_dir / "repo")],
                    capture_output=True, check=True, timeout=180,
                )
            await asyncio.get_running_loop().run_in_executor(None, _clone)

        return str(dataset_dir)

    async def _validate(self, dataset_dir: str) -> list[str]:
        """Return a list of validation errors. Empty = pass.

        Foundation-phase validator only checks that the dataset directory
        exists and has a MANIFEST. Real schema validation ships with the
        actual importer.
        """
        errors: list[str] = []
        p = Path(dataset_dir)
        if not p.is_dir():
            errors.append(f"dataset dir missing: {dataset_dir}")
        elif not (p / "MANIFEST.json").is_file():
            errors.append("MANIFEST.json missing")
        return errors

    async def _run_tests(self, dataset_dir: str) -> dict:
        """Run compatibility tests against the fetched dataset.

        Foundation-phase stub — returns ``passed: true`` if the manifest
        loads. Real tests ship with the importer.
        """
        try:
            import json as _json
            m = Path(dataset_dir) / "MANIFEST.json"
            data = _json.loads(m.read_text())
            return {"passed": True, "manifest": data}
        except Exception as exc:  # noqa: BLE001
            return {"passed": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Pointer + history persistence
    # ------------------------------------------------------------------
    async def _activate(self, commit: str, dataset_dir: str,
                        previous: ShowdownActiveDataset) -> None:
        new = ShowdownActiveDataset(
            activeCommit=commit,
            activeDir=dataset_dir,
            activatedAt=datetime.now(timezone.utc),
            previousCommit=previous.activeCommit,
            previousDir=previous.activeDir,
            rollbackAvailable=bool(previous.activeCommit),
        )
        await self._write_active(new)

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
        return ShowdownActiveDataset(**doc)

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
