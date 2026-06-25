# Endpoint → Feature → Test Traceability

Source of truth: [`docs/FEATURE_INVENTORY.md`](../../FEATURE_INVENTORY.md)

## Endpoint matrix (target audit set = 24 rows)

| FR | Method | Path | Mounted? | Governance test link |
|---|---|---|---|---|
| FR-API-HEALTH-001 | GET | `/health` | ✅ | `Not covered` |
| FR-API-HEALTH-002 | GET | `/ready` | ✅ | `Not covered` |
| FR-AUTH-001 | GET | `/api/v1/auth/me` | ✅ | `Not covered` |
| FR-TRACE-001 | GET | `/api/v1/code-trace/{component_id}` | ❌ unmounted | `Not covered` |
| FR-EV-001 | GET | `/api/v1/evidence` | ✅ | `Not covered` |
| FR-EV-002 | POST | `/api/v1/evidence` | ✅ | `Not covered` |
| FR-EV-003 | GET | `/api/v1/evidence/health` | ✅ | `Not covered` |
| FR-IMPACT-001 | GET | `/api/v1/impact/forward/{artifact_id}` | ❌ unmounted | `Not covered` |
| FR-IMPACT-002 | GET | `/api/v1/impact/reverse/{artifact_id}` | ❌ unmounted | `Not covered` |
| FR-IMPACT-003 | POST | `/api/v1/impact` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-IMPACT-004 | POST | `/api/v1/impact/blast-radius` | ❌ unmounted | `Not covered` |
| FR-TRACE-005 | POST | `/api/v1/coverage-matrix` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-GOV-001 | POST | `/api/v1/governance/spec-check` | ✅ | `tests/unit/test_governance_and_models.py` |
| FR-CONF-001 | POST | `/api/v1/confidence` | ✅ | `Not covered` |
| FR-ORG-001 | GET | `/api/v1/org-intel/health` | ✅ | `Not covered` |
| FR-ORG-002 | GET | `/api/v1/org-intel/metrics` | ✅ | `Not covered` |
| FR-ORG-003 | GET | `/api/v1/org-intel/teams` | ✅ | `Not covered` |
| FR-PM-001 | GET | `/api/v1/sdlc-pm/health` | ✅ | `Not covered` |
| FR-PM-002 | GET | `/api/v1/sdlc-pm/sprints` | ✅ | `Not covered` |
| FR-PM-003 | GET | `/api/v1/sdlc-pm/stories` | ✅ | `Not covered` |
| FR-PM-004 | POST | `/api/v1/sdlc-pm/sprints` | ✅ | `Not covered` |
| FR-INGEST-001 | POST | `/api/v1/ingest/github` | ❌ unmounted | `Not covered` |
| FR-INGEST-002 | POST | `/api/v1/ingest/jira` | ❌ unmounted | `Not covered` |
| FR-CMT-001 | GET | `/api/v1/items/{item_id}/comments` | ❌ unmounted | `Not covered` |
| FR-CMT-002 | POST | `/api/v1/items/{item_id}/comments` | ❌ unmounted | `Not covered` |
| FR-CMT-003 | DELETE | `/api/v1/items/{item_id}/comments/{comment_id}` | ❌ unmounted | `Not covered` |

## Rule

- `Mounted? = ❌ unmounted` indicates endpoint exists in router file but is not yet wired in `main.py`.
- This matrix is intended to be reviewed as part of each governance PR.
