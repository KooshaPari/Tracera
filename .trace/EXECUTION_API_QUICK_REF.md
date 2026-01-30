# Execution API Routes - Quick Reference

## Base URL
```
/api/v1/projects/{project_id}/executions
```

## Endpoint Summary

| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `` | Create execution | 201 |
| GET | `` | List executions | 200 |
| GET | `/{execution_id}` | Get execution | 200 |
| POST | `/{execution_id}/start` | Start execution | 202 |
| POST | `/{execution_id}/complete` | Complete execution | 200 |
| GET | `/{execution_id}/artifacts` | List artifacts | 200 |
| POST | `/{execution_id}/artifacts` | Add artifact | 201 |
| GET | `/../execution-config` | Get config | 200 |
| PUT | `/../execution-config` | Update config | 200 |
| POST | `/../vhs/generate-tape` | Generate tape | 202 |

## Quick Examples

### Create Execution
```bash
POST /api/v1/projects/proj123/executions
Authorization: Bearer <token>
Content-Type: application/json

{
  "execution_type": "playwright",
  "trigger_source": "manual"
}
```

### Start Execution
```bash
POST /api/v1/projects/proj123/executions/exec123/start
Authorization: Bearer <token>
Content-Type: application/json

{}
```

### Add Screenshot
```bash
POST /api/v1/projects/proj123/executions/exec123/artifacts
Authorization: Bearer <token>
Content-Type: application/json

{
  "artifact_type": "screenshot",
  "file_path": "/tmp/screenshot.png"
}
```

### Complete Execution
```bash
POST /api/v1/projects/proj123/executions/exec123/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "passed",
  "exit_code": 0
}
```

### Get Config
```bash
GET /api/v1/projects/proj123/execution-config
Authorization: Bearer <token>
```

### Update Config
```bash
PUT /api/v1/projects/proj123/execution-config
Authorization: Bearer <token>
Content-Type: application/json

{
  "docker_image": "node:22-alpine",
  "vhs_width": 1600
}
```

## Execution Status Flow

```
pending → running → passed/failed/cancelled
```

Only transitions via:
- `/start` to move from pending to running
- `/complete` to finalize

## Valid Values

**execution_type:**
- `vhs`
- `playwright`
- `codex`
- `custom`

**trigger_source:**
- `manual`
- `github_pr`
- `github_push`
- `webhook`

**status:**
- `pending` (initial)
- `running` (after /start)
- `passed` (successful completion)
- `failed` (error)
- `cancelled` (aborted)

**artifact_type:**
- `screenshot`
- `video`
- `gif`
- `log`
- `trace`
- `tape`

## Response Fields

### Execution
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "execution_type": "string",
  "trigger_source": "string",
  "status": "string",
  "artifact_count": 0,
  "started_at": "datetime|null",
  "completed_at": "datetime|null",
  "duration_ms": "int|null",
  "exit_code": "int|null"
}
```

### Artifact
```json
{
  "id": "uuid",
  "execution_id": "uuid",
  "artifact_type": "string",
  "file_path": "string",
  "file_size": "int|null",
  "mime_type": "string|null",
  "captured_at": "datetime"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (validation failed) |
| 401 | Unauthorized (missing/invalid auth) |
| 403 | Forbidden (wrong project) |
| 404 | Not found |
| 409 | Conflict (wrong status for operation) |
| 500 | Server error |

## File Locations

- **Router**: `/src/tracertm/api/routers/execution.py`
- **Tests**: `/tests/test_execution_routes.py`
- **Full Docs**: `/EXECUTION_API_ROUTES.md`
- **Implementation**: `/.trace/EXECUTION_ROUTES_IMPLEMENTATION.md`

## Key Implementation Details

- All endpoints require authentication via `auth_guard`
- All endpoints perform project access control checks
- Artifact counts are computed on-the-fly
- Config supports partial updates
- VHS tape generation is asynchronous (202 Accepted)
- Docker integration is handled by ExecutionService

## Testing

```bash
# Run all tests
pytest tests/test_execution_routes.py -v

# Run specific test
pytest tests/test_execution_routes.py::test_create_execution_success -v

# With coverage
pytest tests/test_execution_routes.py --cov=src/tracertm/api/routers/execution
```

## Integration Checklist

- [x] Router implemented in `execution.py`
- [x] Router registered in `main.py`
- [x] All 10 endpoints implemented
- [x] Error handling for all cases
- [x] Authentication/authorization checks
- [x] Input validation via schemas
- [x] Comprehensive test coverage
- [x] Full API documentation
- [x] Implementation guide
- [x] Quick reference guide

## Configuration Defaults

If no config exists for a project, defaults are:
- `docker_image`: `node:20-alpine`
- `vhs_enabled`: `true`
- `playwright_enabled`: `true`
- `vhs_theme`: `Dracula`
- `vhs_width`: `1200`
- `vhs_height`: `600`
- `execution_timeout`: `600` (seconds)

## Common Patterns

### Workflow: Create → Start → Capture → Complete
```bash
# 1. Create
POST /executions → {id: "exec123"}

# 2. Start
POST /executions/exec123/start → {status: "running"}

# 3. During execution...
POST /executions/exec123/artifacts → {id: "art123"}
POST /executions/exec123/artifacts → {id: "art124"}

# 4. Complete
POST /executions/exec123/complete → {status: "passed"}

# 5. Review
GET /executions/exec123/artifacts
```

### Get Execution State
```bash
GET /executions/exec123 → Full execution details
```

### Filter Executions
```bash
GET /executions?status=failed
GET /executions?execution_type=playwright
GET /executions?limit=50&offset=0
```

## Notes

- Executions are immutable once completed
- Artifact files are copied to artifact storage
- Configuration changes apply to future executions
- All timestamps are UTC ISO 8601
- Project access is strictly enforced
