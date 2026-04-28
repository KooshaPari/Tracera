# Specifications API Router Implementation

## Overview

A comprehensive, production-ready FastAPI router for managing all specification-related entities in TraceRTM:
- Architecture Decision Records (ADRs)
- Contracts (pre/post-conditions, invariants, state machines)
- Features (BDD format)
- Scenarios (Gherkin steps and execution)

## Files Created

### 1. Main Router
**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/routers/specifications.py`

**Size:** ~1000 lines of production-grade code

**Key Features:**
- Unified `/api/v1/specifications` namespace for all endpoints
- Proper dependency injection (auth, database)
- Comprehensive error handling with HTTP status codes
- Input validation via Pydantic schemas
- Async/await throughout
- Full docstrings with examples

### 2. Documentation
**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/routers/SPECIFICATIONS_ROUTER.md`

**Contents:**
- Complete API reference for all endpoints
- Request/response examples for each endpoint
- Query parameter documentation
- Authentication and validation details
- Best practices and integration examples

### 3. Test Suite
**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/api/test_specifications_router.py`

**Coverage:**
- ADR CRUD operations
- Contract verification
- Feature management
- Scenario execution and running
- Project-level summary endpoints
- Error handling and validation

## API Endpoints

### ADR Endpoints
```
POST   /api/v1/specifications/adrs                    Create ADR
GET    /api/v1/specifications/adrs/{adr_id}          Get ADR
PUT    /api/v1/specifications/adrs/{adr_id}          Update ADR
DELETE /api/v1/specifications/adrs/{adr_id}          Delete ADR
GET    /api/v1/specifications/projects/{pid}/adrs    List project ADRs
POST   /api/v1/specifications/adrs/{adr_id}/verify   Verify compliance
```

### Contract Endpoints
```
POST   /api/v1/specifications/contracts                        Create contract
GET    /api/v1/specifications/contracts/{contract_id}         Get contract
PUT    /api/v1/specifications/contracts/{contract_id}         Update contract
DELETE /api/v1/specifications/contracts/{contract_id}         Delete contract
GET    /api/v1/specifications/projects/{pid}/contracts        List contracts
POST   /api/v1/specifications/contracts/{id}/verify           Verify compliance
```

### Feature Endpoints
```
POST   /api/v1/specifications/features                        Create feature
GET    /api/v1/specifications/features/{feature_id}          Get feature
PUT    /api/v1/specifications/features/{feature_id}          Update feature
DELETE /api/v1/specifications/features/{feature_id}          Delete feature
GET    /api/v1/specifications/projects/{pid}/features        List features
```

### Scenario Endpoints
```
POST   /api/v1/specifications/features/{fid}/scenarios        Create scenario
GET    /api/v1/specifications/features/{fid}/scenarios        List scenarios
GET    /api/v1/specifications/scenarios/{scenario_id}         Get scenario
PUT    /api/v1/specifications/scenarios/{scenario_id}         Update scenario
DELETE /api/v1/specifications/scenarios/{scenario_id}         Delete scenario
POST   /api/v1/specifications/scenarios/{id}/run              Run scenario
```

### Project-Level Endpoints
```
GET    /api/v1/specifications/projects/{pid}/summary          Get summary
```

## Architecture Decisions

### Design Pattern: Unified Router with Domain-Specific Services

**Decision:** Create a unified `/specifications` router that delegates to existing domain-specific services rather than merging all logic into one service.

**Rationale:**
- Maintains separation of concerns (each service handles its domain)
- Allows independent evolution of each specification type
- Single entry point for specifications enables cross-cutting concerns
- Easier testing and debugging

**Consequences:**
- Service layer remains independent
- Router provides orchestration and common patterns
- Verification endpoints implement business logic locally

### Error Handling Strategy

All endpoints follow consistent error handling:

1. **Validation Errors (400):** Input fails Pydantic validation
2. **Authentication Errors (401):** Missing/invalid JWT token
3. **Not Found (404):** Resource doesn't exist
4. **Server Errors (500):** Unhandled exceptions

Error responses include detail message for debugging.

### Compliance Verification

**ADR Verification Checks:**
- Context presence and minimum detail (50 chars)
- Decision clarity (minimum 20 chars)
- Consequences documentation
- Traceability to requirements/ADRs
- Decision drivers

**Contract Verification Checks:**
- Preconditions defined
- Postconditions defined
- Clear title
- States defined if transitions exist

Scores range 0-100, with penalties for missing elements.

## Integration with Existing Code

### Router Registration
Added to `/src/tracertm/api/main.py`:

```python
from tracertm.api.routers import specifications

app.include_router(specifications.router, prefix="/api/v1")
```

### Dependencies Used
- `tracertm.api.deps.get_db` - Database session injection
- `tracertm.api.deps.auth_guard` - JWT authentication
- `tracertm.schemas.specification` - Pydantic models
- `tracertm.services.adr_service.ADRService`
- `tracertm.services.contract_service.ContractService`
- `tracertm.services.feature_service.FeatureService`
- `tracertm.services.scenario_service.ScenarioService`

### Schema Integration
Uses existing Pydantic schemas:
- `ADRCreate`, `ADRUpdate`, `ADRResponse`
- `ContractCreate`, `ContractUpdate`, `ContractResponse`
- `FeatureCreate`, `FeatureUpdate`, `FeatureResponse`
- `ScenarioCreate`, `ScenarioUpdate`, `ScenarioResponse`

## Usage Examples

### Python Client Example

```python
import httpx
from datetime import date

class SpecificationsClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def create_adr(self, project_id: str, title: str, **details):
        """Create an ADR."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/specifications/adrs",
                json={
                    "project_id": project_id,
                    "title": title,
                    **details
                },
                headers=self.headers
            )
            return response.json()

    async def verify_adr(self, adr_id: str):
        """Verify ADR compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/specifications/adrs/{adr_id}/verify",
                headers=self.headers
            )
            return response.json()

    async def get_project_summary(self, project_id: str):
        """Get project specifications summary."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/specifications/projects/{project_id}/summary",
                headers=self.headers
            )
            return response.json()

# Usage
client = SpecificationsClient("http://api.example.com", "your_token_here")

# Create ADR
adr = await client.create_adr(
    project_id="proj-123",
    title="Use PostgreSQL",
    context="Need reliable database...",
    decision="PostgreSQL chosen",
    consequences="Requires expertise..."
)

# Verify compliance
result = await client.verify_adr(adr['id'])
print(f"Compliance Score: {result['score']}")

# Get project summary
summary = await client.get_project_summary("proj-123")
print(f"Total ADRs: {summary['adr_count']}")
```

### JavaScript/TypeScript Client Example

```typescript
interface SpecificationClientOptions {
  baseUrl: string;
  token: string;
}

class SpecificationsClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(options: SpecificationClientOptions) {
    this.baseUrl = options.baseUrl;
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${options.token}`
    };
  }

  async createADR(projectId: string, adr: any) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/specifications/adrs`,
      {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          project_id: projectId,
          ...adr
        })
      }
    );
    return response.json();
  }

  async listProjectADRs(projectId: string, status?: string) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);

    const response = await fetch(
      `${this.baseUrl}/api/v1/specifications/projects/${projectId}/adrs?${params}`,
      {
        method: 'GET',
        headers: this.headers
      }
    );
    return response.json();
  }

  async createScenario(featureId: string, scenario: any) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/specifications/features/${featureId}/scenarios`,
      {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(scenario)
      }
    );
    return response.json();
  }

  async runScenario(scenarioId: string) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/specifications/scenarios/${scenarioId}/run`,
      {
        method: 'POST',
        headers: this.headers
      }
    );
    return response.json();
  }
}

// Usage
const client = new SpecificationsClient({
  baseUrl: 'http://api.example.com',
  token: 'your_token_here'
});

// Create and list ADRs
const adr = await client.createADR('proj-123', {
  title: 'Use PostgreSQL',
  context: 'Need reliable database...',
  decision: 'PostgreSQL chosen',
  consequences: 'Requires expertise...'
});

const adrs = await client.listProjectADRs('proj-123', 'proposed');
console.log(`Found ${adrs.total} proposed ADRs`);

// Work with scenarios
const scenario = await client.createScenario('feature-123', {
  title: 'User login',
  gherkin_text: 'Feature: Authentication...',
  given_steps: [{ ... }],
  when_steps: [{ ... }],
  then_steps: [{ ... }]
});

const result = await client.runScenario(scenario.id);
console.log(`Scenario passed: ${result.passed}`);
```

### cURL Examples

```bash
# Create ADR
curl -X POST http://localhost:4000/api/v1/specifications/adrs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123",
    "title": "Use PostgreSQL",
    "context": "Need reliable database for traceability system...",
    "decision": "PostgreSQL chosen for ACID compliance",
    "consequences": "Requires PostgreSQL expertise on team",
    "status": "proposed",
    "decision_drivers": ["ACID requirement", "Team expertise"]
  }'

# List project ADRs
curl -X GET "http://localhost:4000/api/v1/specifications/projects/proj-123/adrs?status=proposed" \
  -H "Authorization: Bearer $TOKEN"

# Verify ADR compliance
curl -X POST "http://localhost:4000/api/v1/specifications/adrs/{adr_id}/verify" \
  -H "Authorization: Bearer $TOKEN"

# Get project summary
curl -X GET "http://localhost:4000/api/v1/specifications/projects/proj-123/summary" \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

### Run All Specification Tests
```bash
pytest tests/api/test_specifications_router.py -v
```

### Run Specific Test Class
```bash
pytest tests/api/test_specifications_router.py::TestADREndpoints -v
```

### Run with Coverage
```bash
pytest tests/api/test_specifications_router.py --cov=tracertm.api.routers.specifications
```

## Performance Considerations

### Database Queries
- List operations load full result set (no pagination in v1)
- Consider adding pagination for large projects
- Scenario execution is simulated - integrate with actual test runner

### Compliance Verification
- Computed on-demand during verification request
- Could be cached or pre-computed for large projects
- Verify operations are O(1) relative to specification size

### Recommendations
1. Add cursor-based pagination to list endpoints
2. Pre-compute compliance scores for dashboard queries
3. Implement async scenario execution with queue system
4. Add caching for frequently accessed specifications

## Security Considerations

### Authentication
- All endpoints require valid JWT token
- Token verified via `auth_guard` dependency
- WorkOS AuthKit integration enforced

### Authorization
- Future: Implement project-level access control
- Future: Role-based access to sensitive fields

### Input Validation
- All inputs validated via Pydantic
- Type checking enforced at runtime
- Enum values restricted to valid options

## Future Enhancements

1. **Pagination:** Add cursor-based pagination to list endpoints
2. **Filtering:** Enhance filtering on list endpoints (date range, multiple tags)
3. **Bulk Operations:** Batch create/update specifications
4. **Versioning:** Track specification versions and changes
5. **Comments:** Add inline comments and discussion threads
6. **Linking:** Enhanced cross-linking between specifications
7. **Templates:** Pre-defined templates for common specification types
8. **Metrics:** Detailed coverage and compliance metrics
9. **Webhooks:** Notify external systems on specification changes
10. **Audit Trail:** Log all changes with user attribution

## Migration Path

If migrating from individual routers:

1. Individual routers continue to work at `/api/v1/adrs`, etc.
2. Unified router available at `/api/v1/specifications`
3. Frontend can gradually adopt new unified endpoints
4. Deprecate individual routers in v2

## Maintenance

### Adding New Endpoints

1. Define Pydantic schemas in `schemas/specification.py`
2. Implement service methods in respective service classes
3. Add endpoint function in `routers/specifications.py`
4. Add comprehensive docstrings with examples
5. Add test cases to `tests/api/test_specifications_router.py`
6. Update `SPECIFICATIONS_ROUTER.md` with endpoint documentation

### Updating Services

The router delegates to existing services. If modifying service signatures:

1. Update router endpoint function
2. Update corresponding test cases
3. Ensure backward compatibility if needed

## Support

For issues or questions:
- Check `SPECIFICATIONS_ROUTER.md` for API reference
- Review test cases in `test_specifications_router.py` for usage examples
- Examine service implementations for business logic details
