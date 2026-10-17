# Endpoint → Feature → Test Traceability

Source of truth: [`docs/FEATURE_INVENTORY.md`](../../FEATURE_INVENTORY.md)

This table is the 24/26 endpoint governance slice used by Tracera hardening audits:
- **24 API business routes**
- **+2 operational probes** (`/health`, `/ready`) included for runtime governance completeness.

## Endpoint matrix

| FR | Method | Path | Mounted? | Test linkage |
|---|---|---|---|---|
| FR-API-HEALTH-001 | GET | `/health` | ✅ | `Not covered` |
| FR-API-HEALTH-002 | GET | `/ready` | ✅ | `Not covered` |
| FR-AUTH-001 | GET | `/api/v1/auth/me` | ❌ | `Not covered` |
| FR-TRACE-001 | GET | `/api/v1/code-trace/{component_id}` | ❌ unmounted | `Not covered` |
| FR-EV-001 | GET | `/evidence` | ✅ | `Not covered` |
| FR-EV-002 | POST | `/evidence` | ✅ | `Not covered` |
| FR-EV-003 | GET | `/evidence/health` | ✅ | `Not covered` |
| FR-IMPACT-001 | POST | `/api/v1/trace/forward/{artifact_id}` | ✅ | `Not covered` |
| FR-IMPACT-002 | POST | `/api/v1/trace/reverse/{artifact_id}` | ✅ | `Not covered` |
| FR-IMPACT-003 | POST | `/api/v1/impact` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-IMPACT-004 | POST | `/api/v1/blast-radius` | ✅ | `Not covered` |
| FR-TRACE-005 | POST | `/api/v1/coverage-matrix` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-GOV-001 | POST | `/api/v1/governance/spec-check` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-CONF-001 | POST | `/api/v1/confidence` | ✅ | `Not covered` |
| FR-ORG-001 | GET | `/org-intel/health` | ✅ | `Not covered` |
| FR-ORG-002 | GET | `/org-intel/metrics` | ✅ | `Not covered` |
| FR-ORG-003 | GET | `/org-intel/teams` | ✅ | `Not covered` |
| FR-PM-001 | GET | `/sdlc-pm/health` | ✅ | `Not covered` |
| FR-PM-002 | GET | `/sdlc-pm/sprints` | ✅ | `Not covered` |
| FR-PM-003 | GET | `/sdlc-pm/stories` | ✅ | `Not covered` |
| FR-PM-004 | POST | `/sdlc-pm/sprints` | ✅ | `Not covered` |
| FR-INGEST-001 | POST | `/ingest/github` | ✅ | `Not covered` |
| FR-INGEST-002 | POST | `/ingest/jira` | ✅ | `Not covered` |
| FR-CMT-001 | GET | `/api/v1/items/{item_id}/comments` | ❌ unmounted | `Not covered` |
| FR-CMT-002 | POST | `/api/v1/items/{item_id}/comments` | ❌ unmounted | `Not covered` |
| FR-CMT-003 | DELETE | `/api/v1/items/{item_id}/comments/{comment_id}` | ❌ unmounted | `Not covered` |

## Rule

- `Unmounted = ❌` means endpoint contract exists in upstream docs/router plans but is not mounted by
  current `crates/tracera-server/src/main.rs`.
- `Mounted = ✅` means endpoint is currently exposed via active router mounts.
