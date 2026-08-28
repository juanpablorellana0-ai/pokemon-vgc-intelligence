# AGENTS.md — VGC Intelligence

**Permanent development rules for AI coding agents working on this repository.**

This file is project governance. Every AI agent (Emergent or otherwise) operating on VGC Intelligence MUST read and obey these rules before performing any work. These rules take precedence over an agent's default habits. If a task instruction conflicts with this file, see [Important Agent Behavior](#important-agent-behavior).

---

## 1. GitHub Branch Architecture

| Branch | Owner | Purpose | Agent access |
|---|---|---|---|
| `main` | Juan (project owner) | Official stable / source-of-truth branch | **READ-ONLY** |
| `emergent/development` | Emergent agents | Dedicated development branch for all Emergent work | **READ/WRITE** (the only writable branch) |
| `frontend/paola` | Paola (designer) | Dedicated frontend/design branch | **DO NOT TOUCH** |

### `main`
- Official stable / source-of-truth branch.
- Protected by GitHub Rulesets.
- **Never push directly.**
- **Never force-push.**
- **Never delete or rename.**
- Changes enter `main` ONLY through Pull Requests and human review.

### `emergent/development`
- Dedicated development branch for Emergent. This is the branch the Emergent workspace is connected to.
- ALL Emergent development work must be performed here.
- Push/Save changes **only** to this branch.
- Never push directly to `main`.
- Never push to `frontend/paola`.
- Never delete or rename this branch.

### `frontend/paola`
- Dedicated frontend/design branch for Paola. Treat this branch as **designer-owned**.
- Do NOT modify, push to, merge into, delete, rename, or reset this branch.
- Do NOT overwrite designer-created assets or visual implementations.

---

## 2. GitHub Workflow

1. **Before beginning substantial development work:**
   - Verify the current branch.
   - Verify Git status.
   - Ensure the workspace is based on the latest appropriate project state.
2. `main` is the stable source of truth.
3. Emergent development occurs on `emergent/development`.
4. When `main` has advanced because another contributor's Pull Request was merged: **synchronize with the latest `main` before beginning substantial new work.**
5. Never overwrite another contributor's changes.
6. Never force-push.
7. Never reset a shared branch destructively.
8. Never delete branches.
9. **When development is complete:**
   - Run relevant tests.
   - Review changed files.
   - Create a clear commit.
   - Push only to `emergent/development`.
   - Prepare a Pull Request from `emergent/development` → `main`.
   - **Do not merge the Pull Request yourself.** Juan reviews and merges.

---

## 3. Frontend / Design Ownership

Treat the following areas as **designer-sensitive** (owned by Paola):

- Frontend assets
- Visual identity
- Design system
- Theme (`frontend/src/theme.ts` and successors)
- UI components
- Visual layouts
- Animations
- Illustrations
- Icons
- Branding

**Never delete, replace, rename, or substantially redesign designer-created assets or visual components unless explicitly requested by the project owner.**

Functional frontend work may be required for integration (e.g., wiring screens to APIs), but **preserve the existing visual identity and design system**.

When a frontend change is technically necessary:

- Make the smallest reasonable change.
- Preserve existing design.
- Avoid replacing working components unnecessarily.
- Document the reason for the change (in the commit message and/or PR description).

---

## 4. Backend / Frontend Separation

**Backend responsibilities** (`/backend`):
- APIs (`/api/v1/*`)
- Database (MongoDB, `sd_*` collections)
- Showdown data
- Data ingestion (`backend/ingestion/`)
- Calculations (`backend/calculation/`)
- AI services (`backend/ai_services/`)
- Meta analysis
- Testing infrastructure (`/tests`)

**Frontend responsibilities** (`/frontend`):
- Presentation
- UX
- UI
- Visual identity
- Interaction
- Responsive design
- Animations

Rules:
- Do NOT modify backend behavior merely to accommodate a visual change without coordination.
- Do NOT break existing API contracts (endpoint paths, parameters, response shapes).

---

## 5. Code Safety

Before modifying existing code:

1. Read the relevant implementation.
2. Understand its dependencies.
3. Preserve existing functionality.
4. Prefer extending existing systems over creating duplicate implementations.
5. Avoid unnecessary refactors.
6. Avoid deleting working code unless explicitly required.
7. Avoid introducing duplicate components, services, or utilities.

---

## 6. Data Safety

- Never expose secrets.
- Never commit API keys, passwords, or credentials (`.env` files stay out of feature diffs; secrets live only in environment configuration).
- Never overwrite production data.
- Preserve existing Showdown datasets and synchronization mechanisms (`sd_*` collections, `showdown_pointers`, `showdown_sync_history`, the importer, and the parser bridge).
- Treat imported canonical Showdown data as **controlled project data**: it comes exclusively from the official Smogon repository via the sync pipeline. Never fabricate, hand-edit, or substitute this data.

---

## 7. Testing

Before requesting integration into `main`:

- Run relevant backend tests (`/tests`, currently 34 pytest cases).
- Run relevant frontend checks when applicable (lint, app boots, navigation works).
- Verify API behavior when affected.
- Report test results.
- Clearly identify known limitations.

---

## 8. Pull Request Requirements

A Pull Request from `emergent/development` → `main` should include:

- Concise summary
- Reason for the change
- Important files changed
- Tests performed
- Known limitations
- Any frontend/design impact
- Any database/data migration impact

---

## Important Agent Behavior

If instructions conflict with these project rules:

- **Prioritize repository safety.**
- Do not force changes.
- Do not overwrite existing work.
- **Stop and ask for clarification.**

The repository's GitHub `main` branch is the final source of truth.

---

## 9. Showdown Sync Pipeline — Runtime Dependencies

The Showdown ingestion pipeline (`backend/ingestion/showdown/`) shells out to three system tools that MUST be present in the backend image (`backend/Dockerfile.base44`):

- **`git`** — `service._ls_remote()` runs `git ls-remote` to read the remote HEAD; `_fetch()` runs `git clone` + `git checkout` when `SHOWDOWN_ENABLE_CLONE=1`.
- **`node`** — `parser_bridge.parse_repo()` runs `node parse.mjs` to parse Showdown's `.ts` data files.
- **`esbuild`** — `parse.mjs` transpiles Showdown TypeScript data files to JS before dynamic import.

If any of these is missing, `check()` silently reports `remoteCommit: null` ("could not determine remote commit") and `sync()` fails at the fetch/parse stage — with no obvious error in the API response. The `python:3.12-slim` base image ships none of them, so they are installed in the Dockerfile. Verify with `git --version && node --version && esbuild --version` inside the backend container.

Default `SHOWDOWN_ENABLE_CLONE=0` means `_fetch` records the commit without cloning; set it to `1` to materialize the repo and run the full parse → validate → test → activate pipeline.

---

*Related documents: `frontend/FRONTEND_GUIDE.md` (designer onboarding), `documentation/ROADMAP.md` (development phases), `documentation/DATA_SOURCES.md` (data provenance and licensing).*
