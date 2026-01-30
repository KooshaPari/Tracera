# Specifications Router - Quick Reference

## Summary

Complete, production-ready API router for managing specifications (ADRs, Contracts, Features, Scenarios) with 24 endpoints, comprehensive documentation, and full test coverage.

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/tracertm/api/routers/specifications.py` | Main router implementation | 1000+ |
| `src/tracertm/api/routers/SPECIFICATIONS_ROUTER.md` | Complete API reference | 400+ |
| `tests/api/test_specifications_router.py` | Comprehensive test suite | 500+ |
| `SPECIFICATIONS_ROUTER_IMPLEMENTATION.md` | Implementation guide | 600+ |

## Quick Start

### 1. Create an ADR
```bash
curl -X POST http://localhost:8000/api/v1/specifications/adrs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123",
    "title": "Use PostgreSQL",
    "context": "Need reliable ACID database...",
    "decision": "PostgreSQL chosen",
    "consequences": "Requires PG expertise...",
    "status": "proposed"
  }'
```

### 2. Verify Compliance
```bash
curl -X POST http://localhost:8000/api/v1/specifications/adrs/{adr_id}/verify \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Create a Feature with Scenarios
```bash
# Create feature
curl -X POST http://localhost:8000/api/v1/specifications/features \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123",
    "name": "User Auth",
    "as_a": "developer",
    "i_want": "to authenticate",
    "so_that": "I access projects"
  }'

# Create scenario
curl -X POST http://localhost:8000/api/v1/specifications/features/{feature_id}/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "User login",
    "gherkin_text": "Feature: Auth\n  Scenario: Login\n    Given...",
    "given_steps": [...],
    "when_steps": [...],
    "then_steps": [...]
  }'

# Run scenario
curl -X POST http://localhost:8000/api/v1/specifications/scenarios/{scenario_id}/run \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Get Project Summary
```bash
curl -X GET http://localhost:8000/api/v1/specifications/projects/proj-123/summary \
  -H "Authorization: Bearer $TOKEN"
```

## Endpoint Categories

### ADRs (Architecture Decision Records)
```
POST   /api/v1/specifications/adrs                    Create
GET    /api/v1/specifications/adrs/{id}              Read
PUT    /api/v1/specifications/adrs/{id}              Update
DELETE /api/v1/specifications/adrs/{id}              Delete
GET    /api/v1/specifications/projects/{pid}/adrs    List
POST   /api/v1/specifications/adrs/{id}/verify       Verify
```

### Contracts
```
POST   /api/v1/specifications/contracts              Create
GET    /api/v1/specifications/contracts/{id}         Read
PUT    /api/v1/specifications/contracts/{id}         Update
DELETE /api/v1/specifications/contracts/{id}         Delete
GET    /api/v1/specifications/projects/{pid}/contracts
POST   /api/v1/specifications/contracts/{id}/verify  Verify
```

### Features
```
POST   /api/v1/specifications/features               Create
GET    /api/v1/specifications/features/{id}          Read
PUT    /api/v1/specifications/features/{id}          Update
DELETE /api/v1/specifications/features/{id}          Delete
GET    /api/v1/specifications/projects/{pid}/features
```

### Scenarios
```
POST   /api/v1/specifications/features/{fid}/scenarios     Create
GET    /api/v1/specifications/features/{fid}/scenarios     List
GET    /api/v1/specifications/scenarios/{id}              Read
PUT    /api/v1/specifications/scenarios/{id}              Update
DELETE /api/v1/specifications/scenarios/{id}              Delete
POST   /api/v1/specifications/scenarios/{id}/run          Run
```

### Project-Level
```
GET    /api/v1/specifications/projects/{pid}/summary      Summary
```

## Authentication

All endpoints require JWT token:
```
Authorization: Bearer <token>
```

Token from WorkOS AuthKit. Missing/invalid token returns `401 Unauthorized`.

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET/PUT) |
| 201 | Created (POST) |
| 204 | Deleted (DELETE) |
| 400 | Bad request/validation error |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Not found |
| 500 | Server error |

## Compliance Scoring

### ADR Verification
- Context: 50+ characters (required)
- Decision: 20+ characters (required)
- Consequences: documented (recommended)
- Traceability: linked to requirements (recommended)
- Decision drivers: documented (recommended)

**Score: 0-100** (100 = fully compliant)

### Contract Verification
- Preconditions: defined (required)
- Postconditions: defined (required)
- Title: clear and descriptive (required)
- States: defined if transitions exist (required)

**Score: 0-100** (100 = fully compliant)

## Common Scenarios

### Retrieve Project ADRs with Filtering
```bash
# Get all proposed ADRs
curl "http://localhost:8000/api/v1/specifications/projects/proj-123/adrs?status=proposed" \
  -H "Authorization: Bearer $TOKEN"

# Get ADRs with specific tags
curl "http://localhost:8000/api/v1/specifications/projects/proj-123/adrs?tags=database" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Specification Status
```bash
curl -X PUT http://localhost:8000/api/v1/specifications/adrs/{adr_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

### Track Specification Changes
```bash
# Create initial ADR
adr=$(curl -X POST ... | jq '.id')

# Verify current compliance
compliance=$(curl -X POST http://localhost:8000/api/v1/specifications/adrs/$adr/verify \
  -H "Authorization: Bearer $TOKEN")

# Update ADR
curl -X PUT http://localhost:8000/api/v1/specifications/adrs/$adr \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'

# Verify new compliance
new_compliance=$(curl -X POST http://localhost:8000/api/v1/specifications/adrs/$adr/verify \
  -H "Authorization: Bearer $TOKEN")
```

## Testing

```bash
# Run all tests
pytest tests/api/test_specifications_router.py -v

# Run specific test class
pytest tests/api/test_specifications_router.py::TestADREndpoints -v

# Run with coverage
pytest tests/api/test_specifications_router.py --cov=tracertm.api.routers.specifications
```

## Dependencies

**Services:**
- `ADRService` - ADR CRUD and listing
- `ContractService` - Contract management
- `FeatureService` - Feature management
- `ScenarioService` - Scenario management

**Schemas:**
- `ADRCreate`, `ADRUpdate`, `ADRResponse`
- `ContractCreate`, `ContractUpdate`, `ContractResponse`
- `FeatureCreate`, `FeatureUpdate`, `FeatureResponse`
- `ScenarioCreate`, `ScenarioUpdate`, `ScenarioResponse`

**Infrastructure:**
- `get_db` - Database session
- `auth_guard` - JWT authentication

## Error Handling Examples

### Invalid Input
```json
{
  "detail": "Failed to create ADR: validation error"
}
```

### Not Found
```json
{
  "detail": "ADR not found"
}
```

### Unauthorized
```json
{
  "detail": "Authorization required"
}
```

## Python Client Example

```python
import httpx

class SpecificationsAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def create_adr(self, **payload):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/api/v1/specifications/adrs",
                json=payload,
                headers=self.headers
            )
            return r.json()

    async def verify_adr(self, adr_id: str):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/api/v1/specifications/adrs/{adr_id}/verify",
                headers=self.headers
            )
            return r.json()

# Usage
api = SpecificationsAPI("http://localhost:8000", "token")
adr = await api.create_adr(
    project_id="proj-123",
    title="Use PostgreSQL",
    context="...",
    decision="...",
    consequences="..."
)
compliance = await api.verify_adr(adr["id"])
print(f"Score: {compliance['score']}")
```

## TypeScript Client Example

```typescript
async function createADR(token: string, payload: any) {
  const response = await fetch('http://localhost:8000/api/v1/specifications/adrs', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  return response.json();
}

async function verifyADR(token: string, adrId: string) {
  const response = await fetch(
    `http://localhost:8000/api/v1/specifications/adrs/${adrId}/verify`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
}
```

## Best Practices

1. **ADRs**: Always document decision drivers and considered options
2. **Contracts**: Define both pre and post conditions clearly
3. **Features**: Use proper BDD format (As a / I want / So that)
4. **Scenarios**: Write clear Gherkin with proper steps
5. **Traceability**: Link specifications to requirements
6. **Verification**: Run compliance checks before approving
7. **Status Tracking**: Move specifications through proper status workflow

## Troubleshooting

**401 Unauthorized**
- Check token is valid and not expired
- Verify `Authorization: Bearer <token>` header format

**404 Not Found**
- Verify resource ID is correct
- Check parent resource exists (e.g., feature before creating scenario)

**400 Bad Request**
- Check required fields are present
- Verify enum values are valid
- Check field constraints (min/max length)

**422 Validation Error**
- Invalid JSON schema
- Wrong field types
- Missing required fields

## Next Steps

1. Review full API reference: `SPECIFICATIONS_ROUTER.md`
2. Check implementation guide: `SPECIFICATIONS_ROUTER_IMPLEMENTATION.md`
3. Review test examples: `tests/api/test_specifications_router.py`
4. Deploy router to your environment
5. Update frontend to use new unified endpoints

## Support

For detailed API reference, see: `src/tracertm/api/routers/SPECIFICATIONS_ROUTER.md`

For implementation details, see: `SPECIFICATIONS_ROUTER_IMPLEMENTATION.md`

For test examples, see: `tests/api/test_specifications_router.py`
