# QA Integration – Current State & Remainder

**Last updated:** 2026-01-28

---

## Current state summary

| Phase | Item | Status | Notes |
|-------|------|--------|--------|
| **Phase 1** | Database models (STORY-001) | ✅ Done | `execution`, `execution_artifact`, `codex_agent_interaction`, `execution_environment_config` |
| | Alembic migration | ✅ Done | `018_add_execution_system.py` → revision `019_execution` (depends on `018` workflow_runs) |
| | Pydantic schemas | ✅ Done | `tracertm/schemas/execution.py` + `__init__.py` exports |
| | FFmpegPipeline (STORY-006) | ✅ Done | `tracertm/services/recording/ffmpeg_pipeline.py` |
| | TapeFileGenerator (STORY-004) | ✅ Done | `tracertm/services/recording/tape_generator.py` + exported in `recording/__init__.py` |
| **Phase 2** | ExecutionService + Docker (STORY-002) | ✅ Done | `execution/execution_service.py`, `docker_orchestrator.py` |
| | Artifact storage (STORY-003) | ✅ Done | `execution/artifact_storage.py` |
| **Phase 3** | VHSExecutionService (STORY-005) | ✅ Done | `recording/vhs_service.py` |
| | PlaywrightExecutionService (STORY-007) | ✅ Done | `recording/playwright_service.py` |
| **Phase 4** | CodexAgentService (STORY-008) | ✅ Done | `agents/codex_service.py` |
| **Phase 5** | QAEnhancedNode (STORY-009) | ✅ Done | `frontend/.../nodes/QAEnhancedNode.tsx` |
| | NodeExpandPopup (STORY-010) | ✅ Done | `frontend/.../nodes/NodeExpandPopup.tsx` |
| **Polish** | API routes for execution | ✅ Done | `/api/v1/projects/{id}/executions`, config, start, complete, artifacts |
| | Migration chain | ✅ Fixed | 017 → 018 (workflow_runs) → 019_execution (execution_system) |
| | Run migration | ⚠️ Pending | Resolve dual-018; then `alembic upgrade head` |

---

## Migration heads fix

Two migrations both had `revision = "018"` and `down_revision = "017"`:

- `018_add_workflow_runs.py` → stays **018**
- `018_add_execution_system.py` → changed to **019_execution**, `down_revision = "018"`

Chain: `017` → `018` (workflow_runs) → `019_execution` (execution system).

**Next step:** Run:

```bash
alembic upgrade head
```

If you already ran an older `018` (execution) and have a split history, fix with `alembic merge` or re-run from a known good backup.

---

## Remainder – recommended order

### 1. Apply migrations (unblock DB)

- Ensure only one head: `alembic heads` (should show `019_execution`).
- Run: `alembic upgrade head`.

### 2. Phase 2 – Execution infrastructure (STORY-002, STORY-003)

**2a. Artifact storage (STORY-003)**  
- Add `src/tracertm/services/execution/` (or under `services/`).
- Implement `ArtifactStorageService`:
  - Base path from env (e.g. `TRACERTM_ARTIFACT_PATH` or `~/.tracertm/artifacts`).
  - Layout: `{base}/{project_id}/{execution_id}/` with files + optional thumbnails.
  - Methods: `store_artifact(execution_id, file_path, artifact_type, metadata)`, `get_path(artifact_id)`, `delete_old(project_id, retention_days)`.
  - Persist metadata in DB via `ExecutionArtifact` (already have model + schemas).

**2b. Docker orchestrator (part of STORY-002)**  
- Implement `DockerOrchestrator` (e.g. in `execution/docker_orchestrator.py` or `execution_service.py`):
  - Create/start container from `ExecutionEnvironmentConfig` (image, env, resource_limits).
  - Mount project dir (read-only or as configured).
  - Optional: bind-mount artifact output dir.
  - Stop/remove on completion or timeout.
  - Use `docker` Python SDK (add to `pyproject.toml` if missing).

**2c. ExecutionService (STORY-002)**  
- Implement `ExecutionService`:
  - CRUD for `Execution` (create, get, list by project, update status).
  - Start run: create container via orchestrator, update `Execution` (status, `container_id`, `started_at`).
  - Complete run: stop container, collect artifacts, run FFmpeg pipeline (video→GIF) if needed, call ArtifactStorageService, update `Execution` (`completed_at`, `duration_ms`, `exit_code`, `error_message`).
  - Use `ExecutionEnvironmentConfig` per project for image and settings.

### 3. Phase 3 – Recording services (STORY-005, STORY-007)

**3a. VHSExecutionService (STORY-005)**  
- Use `TapeFileGenerator` to build `.tape` content; write to temp file.
- Run `vhs /path/to/file.tape` inside the execution container (or subprocess with same env).
- Collect output GIF/video; store via ArtifactStorageService; attach to `Execution`/artifacts.

**3b. PlaywrightExecutionService (STORY-007)**  
- Use Playwright (Python) to run browser tests or “record” flows.
- Capture screenshot/video/trace; save to temp; optionally run FFmpeg (e.g. video→GIF); store via ArtifactStorageService and link to `Execution`/artifacts.

### 4. Phase 4 – Codex agent (STORY-008)

- Implement `CodexAgentService` (e.g. in `agents/codex_service.py`):
  - OAuth: document or automate `codex login` (or equivalent) for the environment.
  - Subprocess or CLI wrapper: run Codex for tasks like `review_image`, `review_video`, `code_review`, `generate_test`.
  - Map inputs/outputs to `CodexAgentInteraction`; persist in DB.
  - Rate limiting and error handling as per plan.

### 5. Phase 5 – Frontend (STORY-009, STORY-010)

- **QAEnhancedNode (STORY-009):** Extend graph node to show QA metrics (pass rate, duration, coverage), thumbnail/pill image, click to expand.
- **NodeExpandPopup (STORY-010):** Modal with tabs: Artifact gallery, Demo runner, Test results, Metrics, Actions (re-run, download, open in browser). Consume execution/artifact API.

### 6. API and integration

- Add FastAPI routes (e.g. under `/api/v1/` or existing prefix):
  - Executions: create, get, list, start, complete (or webhook).
  - Artifacts: list by execution, get URL/path for download.
  - Config: get/put `ExecutionEnvironmentConfig` per project.
  - Optional: Codex task create/status.
- Wire routes to ExecutionService, ArtifactStorageService, and (later) CodexAgentService.

---

## Quick reference – files added so far

| Path | Purpose |
|------|--------|
| `src/tracertm/models/execution.py` | Execution, ExecutionArtifact models |
| `src/tracertm/models/codex_agent.py` | CodexAgentInteraction model |
| `src/tracertm/models/execution_config.py` | ExecutionEnvironmentConfig model |
| `src/tracertm/schemas/execution.py` | Pydantic schemas for execution API |
| `src/tracertm/services/recording/ffmpeg_pipeline.py` | FFmpeg pipeline (video→GIF, thumbnails, etc.) |
| `src/tracertm/services/recording/tape_generator.py` | VHS .tape generator |
| `src/tracertm/services/recording/__init__.py` | Exports FFmpegPipeline, VideoInfo, FFmpegError, TapeFileGenerator |
| `alembic/versions/018_add_execution_system.py` | Migration (revision `019_execution`) |

---

## Next concrete actions

1. Run `alembic upgrade head` and confirm DB has execution tables.
2. Create `src/tracertm/services/execution/` and implement **ArtifactStorageService** (STORY-003).
3. Implement **DockerOrchestrator** and **ExecutionService** (STORY-002).
4. Add **VHSExecutionService** and **PlaywrightExecutionService** (STORY-005, STORY-007) using existing TapeFileGenerator and FFmpegPipeline.
5. Implement **CodexAgentService** (STORY-008).
6. Add **API routes** and then **QAEnhancedNode** + **NodeExpandPopup** (STORY-009, STORY-010).

Use this file as the single checklist for the remainder of the QA Integration work.
