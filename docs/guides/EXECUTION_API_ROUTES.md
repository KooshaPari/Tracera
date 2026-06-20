# Execution System API Routes

## Overview

The Execution system API provides FastAPI endpoints for managing executions, artifacts, and environment configuration in TracerTM. The routes are located in `/src/tracertm/api/routers/execution.py` and are registered with the main FastAPI application.

## Base Path

All execution endpoints are prefixed with:
```
/api/v1/projects/{project_id}/executions
```

## Authentication

All endpoints require authentication via:
- **Bearer Token**: `Authorization: Bearer <token>`
- **API Key**: `X-API-Key: <key>` header

Authentication is enforced by the `auth_guard` dependency injection.

## Data Models

### ExecutionResponse
- `id`: str (UUID)
- `project_id`: str
- `test_run_id`: str | None
- `item_id`: str | None
- `execution_type`: str (vhs|playwright|codex|custom)
- `trigger_source`: str (github_pr|github_push|webhook|manual)
- `trigger_ref`: str | None (PR number, commit SHA, etc.)
- `status`: str (pending|running|passed|failed|cancelled)
- `container_id`: str | None
- `container_image`: str | None
- `config`: dict[str, Any] | None
- `started_at`: datetime | None
- `completed_at`: datetime | None
- `duration_ms`: int | None (milliseconds)
- `exit_code`: int | None
- `error_message`: str | None
- `output_summary`: str | None
- `created_at`: datetime
- `updated_at`: datetime
- `artifact_count`: int (computed)

### ExecutionArtifactResponse
- `id`: str
- `execution_id`: str
- `item_id`: str | None
- `artifact_type`: str (screenshot|video|gif|log|trace|tape)
- `file_path`: str (local filesystem path)
- `thumbnail_path`: str | None
- `file_size`: int | None (bytes)
- `mime_type`: str | None
- `metadata`: dict[str, Any] | None (dimensions, duration, etc.)
- `captured_at`: datetime
- `created_at`: datetime
- `url`: str | None (computed, for frontend)
- `thumbnail_url`: str | None (computed)

### ExecutionEnvironmentConfigResponse
- `id`: str
- `project_id`: str
- `docker_image`: str
- `resource_limits`: dict[str, Any] | None
- `working_directory`: str | None
- `network_mode`: str (bridge|host|none)
- `vhs_enabled`, `playwright_enabled`, `codex_enabled`: bool
- `auto_screenshot`, `auto_video`: bool
- `vhs_theme`: str (Dracula, Nord, etc.)
- `vhs_font_size`: int (8-72)
- `vhs_width`, `vhs_height`: int (display dimensions)
- `vhs_framerate`: int (10-60)
- `playwright_browser`: str (chromium|firefox|webkit)
- `playwright_headless`: bool
- `codex_sandbox_mode`: str
- `artifact_retention_days`: int
- `execution_timeout`: int (seconds)

## Endpoints

### Execution CRUD

#### POST /api/v1/projects/{project_id}/executions
**Create a new execution**

**Request Body:**
```json
{
  "execution_type": "playwright",
  "trigger_source": "manual",
  "trigger_ref": null,
  "test_run_id": "run123",
  "item_id": "item456",
  "config": {
    "playwright_browser": "chromium",
    "playwright_headless": true
  }
}
```

**Response:** 201 Created
```json
{
  "id": "exec123",
  "project_id": "proj123",
  "execution_type": "playwright",
  "status": "pending",
  "artifact_count": 0,
  "created_at": "2026-01-29T10:00:00Z",
  "updated_at": "2026-01-29T10:00:00Z",
  ...
}
```

**Status Codes:**
- 201: Created successfully
- 401: Unauthorized
- 400: Invalid request data

---

#### GET /api/v1/projects/{project_id}/executions
**List executions for a project**

**Query Parameters:**
- `status` (optional): Filter by status (pending|running|passed|failed|cancelled)
- `execution_type` (optional): Filter by type (vhs|playwright|codex|custom)
- `limit` (optional, default=100, max=1000): Number of results
- `offset` (optional, default=0): Pagination offset

**Response:** 200 OK
```json
{
  "executions": [
    { ... ExecutionResponse ... }
  ],
  "total": 15
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

---

#### GET /api/v1/projects/{project_id}/executions/{execution_id}
**Get execution details**

**Response:** 200 OK
```json
{
  "id": "exec123",
  "project_id": "proj123",
  "status": "running",
  "artifact_count": 2,
  ...
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 403: Forbidden (execution not in project)
- 404: Execution not found

---

### Execution Lifecycle

#### POST /api/v1/projects/{project_id}/executions/{execution_id}/start
**Start an execution (transition from pending to running)**

Loads environment config, creates Docker container, updates status to "running".

**Request Body:**
```json
{
  "container_id": null
}
```

**Response:** 202 Accepted
```json
{
  "id": "exec123",
  "status": "running",
  "container_id": "abc123def456",
  "started_at": "2026-01-29T10:05:00Z",
  ...
}
```

**Status Codes:**
- 202: Started successfully
- 401: Unauthorized
- 403: Forbidden
- 404: Execution not found
- 409: Cannot start (wrong status or not pending)
- 500: Failed to start (Docker unavailable)

---

#### POST /api/v1/projects/{project_id}/executions/{execution_id}/complete
**Complete an execution**

Stops container, computes duration, records final status.

**Request Body:**
```json
{
  "status": "passed",
  "exit_code": 0,
  "error_message": null,
  "output_summary": "All tests passed",
  "duration_ms": 5000
}
```

**Response:** 200 OK
```json
{
  "id": "exec123",
  "status": "passed",
  "completed_at": "2026-01-29T10:10:00Z",
  "duration_ms": 5000,
  "exit_code": 0,
  ...
}
```

**Status Codes:**
- 200: Completed successfully
- 401: Unauthorized
- 403: Forbidden
- 404: Execution not found

---

### Execution Artifacts

#### GET /api/v1/projects/{project_id}/executions/{execution_id}/artifacts
**List artifacts for an execution**

**Query Parameters:**
- `artifact_type` (optional): Filter by type (screenshot|video|gif|log|trace|tape)

**Response:** 200 OK
```json
{
  "artifacts": [
    {
      "id": "art123",
      "execution_id": "exec123",
      "artifact_type": "screenshot",
      "file_path": "/artifacts/screenshot.png",
      "file_size": 102400,
      "captured_at": "2026-01-29T10:05:30Z",
      ...
    }
  ],
  "total": 5
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 403: Forbidden
- 404: Execution not found

---

#### POST /api/v1/projects/{project_id}/executions/{execution_id}/artifacts
**Add an artifact to an execution**

Copies file from source to artifact storage and creates ExecutionArtifact record.

**Request Body:**
```json
{
  "artifact_type": "screenshot",
  "file_path": "/tmp/screenshot.png",
  "thumbnail_path": null,
  "item_id": "item456",
  "file_size": 102400,
  "mime_type": "image/png",
  "metadata": {
    "width": 1280,
    "height": 720
  },
  "captured_at": "2026-01-29T10:05:30Z"
}
```

**Response:** 201 Created
```json
{
  "id": "art123",
  "execution_id": "exec123",
  "artifact_type": "screenshot",
  "file_path": "/artifacts/exec123/screenshot.png",
  "file_size": 102400,
  "created_at": "2026-01-29T10:05:35Z",
  ...
}
```

**Status Codes:**
- 201: Created successfully
- 401: Unauthorized
- 403: Forbidden
- 404: Execution not found
- 500: Failed to store artifact

---

### Execution Environment Configuration

#### GET /api/v1/projects/{project_id}/execution-config
**Get execution environment configuration**

**Response:** 200 OK
```json
{
  "id": "config123",
  "project_id": "proj123",
  "docker_image": "node:20-alpine",
  "vhs_enabled": true,
  "playwright_enabled": true,
  "vhs_theme": "Dracula",
  "vhs_width": 1200,
  "vhs_height": 600,
  ...
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: No config found

---

#### PUT /api/v1/projects/{project_id}/execution-config
**Update execution environment configuration**

Supports partial updates (PATCH semantics). Only provided fields are updated.

**Request Body:**
```json
{
  "docker_image": "node:22-alpine",
  "vhs_theme": "Nord",
  "vhs_width": 1600,
  "vhs_height": 900,
  "execution_timeout": 900
}
```

**Response:** 200 OK
```json
{
  "id": "config123",
  "project_id": "proj123",
  "docker_image": "node:22-alpine",
  "vhs_theme": "Nord",
  "vhs_width": 1600,
  "vhs_height": 900,
  "execution_timeout": 900,
  ...
}
```

**Status Codes:**
- 200: Updated successfully
- 400: Invalid request data
- 401: Unauthorized

---

### VHS Tape Generation

#### POST /api/v1/projects/{project_id}/vhs/generate-tape
**Generate a VHS tape file (terminal recording)**

Asynchronously generates a VHS tape file from execution artifacts. This is a long-running operation.

**Query Parameters:**
- `execution_id` (required): Execution ID to generate tape for

**Response:** 202 Accepted
```json
{
  "status": "accepted",
  "execution_id": "exec123",
  "message": "VHS tape generation queued"
}
```

**Status Codes:**
- 202: Accepted (queued for processing)
- 400: No artifacts found for execution
- 401: Unauthorized
- 403: Forbidden
- 404: Execution not found
- 500: Failed to queue generation

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status | Scenario |
|--------|----------|
| 400 | Invalid request data, validation error |
| 401 | Missing or invalid authentication |
| 403 | Forbidden (wrong project, insufficient permissions) |
| 404 | Resource not found |
| 409 | Conflict (wrong status for operation) |
| 500 | Server error |

## Usage Examples

### Create and Start an Execution

```bash
# Create execution
curl -X POST \
  http://localhost:4000/api/v1/projects/proj123/executions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_type": "playwright",
    "trigger_source": "manual"
  }'

# Response
# {
#   "id": "exec123",
#   "status": "pending",
#   ...
# }

# Start execution
curl -X POST \
  http://localhost:4000/api/v1/projects/proj123/executions/exec123/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response
# {
#   "id": "exec123",
#   "status": "running",
#   "started_at": "2026-01-29T10:05:00Z",
#   ...
# }
```

### Capture Artifacts During Execution

```bash
# Add screenshot
curl -X POST \
  http://localhost:4000/api/v1/projects/proj123/executions/exec123/artifacts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "artifact_type": "screenshot",
    "file_path": "/tmp/screenshot.png",
    "mime_type": "image/png"
  }'

# Response
# {
#   "id": "art123",
#   "artifact_type": "screenshot",
#   ...
# }
```

### Complete Execution

```bash
# Mark as passed
curl -X POST \
  http://localhost:4000/api/v1/projects/proj123/executions/exec123/complete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "passed",
    "exit_code": 0,
    "output_summary": "All tests passed"
  }'

# Response
# {
#   "id": "exec123",
#   "status": "passed",
#   "duration_ms": 5000,
#   ...
# }
```

## Integration Points

### Services Used

- **ExecutionService**: Main orchestration service (`tracertm.services.execution.execution_service`)
  - Manages execution lifecycle (create, start, complete)
  - Stores artifacts
  - Manages environment configuration

- **VHSService**: VHS tape generation (`tracertm.services.recording.vhs_service`)
  - Generates terminal recordings from execution artifacts

### Repositories Used

- **ExecutionRepository**: CRUD for Execution records
- **ExecutionArtifactRepository**: CRUD for ExecutionArtifact records
- **ExecutionEnvironmentConfigRepository**: CRUD for ExecutionEnvironmentConfig records

### Models

- `Execution`: Main execution record
- `ExecutionArtifact`: Artifact metadata and storage info
- `ExecutionEnvironmentConfig`: Project-level execution settings

## Implementation Notes

1. **Artifact Counting**: The `artifact_count` field is computed on-the-fly by querying the artifact repository for each execution.

2. **Status Transitions**: Executions follow this state machine:
   - pending → running (via `/start`)
   - running → passed/failed/cancelled (via `/complete`)

3. **Docker Integration**: The `/start` endpoint uses Docker orchestration to create and start containers. If Docker is unavailable, the execution fails.

4. **Configuration Defaults**: If no configuration exists for a project, the `/start` endpoint uses sensible defaults (e.g., `node:20-alpine` image).

5. **Artifact Storage**: Files are copied from the provided `file_path` to the artifact storage service, which manages lifecycle and retention.

6. **VHS Tape Generation**: The `/vhs/generate-tape` endpoint returns 202 Accepted and queues the job asynchronously.

## Testing

Comprehensive tests are provided in `/tests/test_execution_routes.py`:
- Unit tests for all endpoints
- Mock service tests
- Error condition tests
- Edge case validation

Run tests with:
```bash
pytest tests/test_execution_routes.py -v
```

## Future Enhancements

1. **WebSocket Streaming**: Real-time execution status updates
2. **Batch Operations**: Create/start/complete multiple executions
3. **Execution Queuing**: Rate limiting and job queue integration
4. **Artifact Serving**: HTTP endpoints to download artifacts
5. **Webhooks**: Notify external systems on execution events
6. **Search**: Full-text search on execution logs and artifacts
