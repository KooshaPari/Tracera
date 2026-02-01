# Specification Services Implementation Index

Complete index and overview of all specification services implemented for TraceRTM.

## Files Overview

### 1. Core Service Implementation
**File:** `/src/tracertm/services/specification_service.py` (25 KB, 820 lines)

Main service file containing all five specification service classes:
- **ADRService** - Architecture Decision Records (MADR 4.0 format)
- **ContractService** - Design-by-Contract specifications
- **FeatureService** - BDD Features (user stories)
- **ScenarioService** - BDD Scenarios (Gherkin steps)
- **StepDefinitionService** - Reusable step definitions

All services implement:
- AsyncIO patterns with async/await
- SQLAlchemy ORM integration
- Optimistic locking with retry logic
- Sequential numbering
- Comprehensive CRUD operations
- Business logic validation
- Pagination and filtering

### 2. Test Suite
**File:** `/tests/unit/services/test_specification_service.py` (19 KB, 650 lines)

Comprehensive unit tests covering:
- All CRUD operations
- Business logic validation
- Edge cases and error handling
- Mock-based testing with pytest
- AsyncMock for async methods
- Pagination and filtering
- Relationship management

Test classes:
- `TestADRService` - 7 test methods
- `TestContractService` - 5 test methods
- `TestFeatureService` - 4 test methods
- `TestScenarioService` - 6 test methods
- `TestStepDefinitionService` - 6 test methods

### 3. Documentation Files

#### SPECIFICATION_SERVICES_GUIDE.md (19 KB)
**Purpose:** Complete API reference and usage guide

Contains:
- Detailed method signatures for all services
- Parameter descriptions with types
- Return value documentation
- Code examples for each method
- Complete workflow examples
- Design patterns explanation
- Error handling guide
- Best practices
- Testing information

**Sections:**
1. Overview and file location
2. Service Classes (5 major sections)
   - ADRService (8 methods documented)
   - ContractService (8 methods documented)
   - FeatureService (7 methods documented)
   - ScenarioService (8 methods documented)
   - StepDefinitionService (7 methods documented)
3. Usage Examples
4. Design Patterns (5 major patterns)
5. Error Handling
6. Testing
7. Best Practices
8. Integration with tRPC

#### SPECIFICATION_SERVICES_INTEGRATION_EXAMPLE.md (31 KB)
**Purpose:** Practical integration examples and implementation patterns

Contains:
- tRPC router implementations (5 complete routers)
- FastAPI app setup
- Dependency injection patterns
- Request/Response schemas
- Error handling implementation
- Real-world workflow examples
- Testing integration examples

**Sections:**
1. tRPC Router Integration
   - ADRRouter (8 endpoints)
   - FeatureRouter (3 endpoints)
   - ScenarioRouter (3 endpoints)
   - ContractRouter (4 endpoints)
2. Service Dependency Injection
3. Request/Response Types (with Pydantic schemas)
4. Error Handling
5. Real-World Workflows
6. Testing Integration

---

## Service Reference

### ADRService

**Purpose:** Manage Architecture Decision Records (MADR 4.0 format)

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `create()` | Create ADR with auto-numbering (ADR-0001, etc.) |
| `get()` | Retrieve ADR by ID |
| `list_by_project()` | List with pagination and filtering |
| `update()` | Update with optimistic locking |
| `delete()` | Delete ADR |
| `verify_compliance()` | Track compliance scores (0.0-1.0) |
| `link_requirements()` | Link requirements to ADR |
| `supersede()` | Mark ADR as superseded by another |

**Auto-generated Fields:**
- `adr_number` - Sequential (ADR-0001, ADR-0002, etc.)
- `version` - Incremented on each update
- `created_at`, `updated_at` - Timestamps

**Key Data:**
- MADR fields: context, decision, consequences
- Decision drivers, considered options
- Compliance score, last verified date
- Related requirements and ADRs
- Stakeholders, tags, date

**Example:**
```python
adr = await adr_service.create(
    project_id="proj-1",
    title="Use async/await for I/O operations",
    context="Need async database operations",
    decision="Adopt Python async/await pattern",
    consequences="Requires asyncio knowledge",
    decision_drivers=["Performance", "Code clarity"],
)
```

---

### ContractService

**Purpose:** Manage Design-by-Contract specifications with state machines

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `create()` | Create contract with state machines |
| `get()` | Retrieve contract by ID |
| `list_by_project()` | List with filtering by type/status |
| `list_by_item()` | List all contracts for an item |
| `update()` | Update with optimistic locking |
| `delete()` | Delete contract |
| `verify()` | Verify contract with test results |
| `execute_transition()` | Execute valid state transitions |

**Auto-generated Fields:**
- `contract_number` - Sequential (CONTRACT-0001, etc.)
- `version` - Incremented on each update
- `created_at`, `updated_at` - Timestamps

**Key Data:**
- Preconditions, postconditions, invariants
- States and transitions
- Executable specification code
- Verification results and timestamp
- Contract metadata

**Example:**
```python
contract = await contract_service.create(
    project_id="proj-1",
    item_id="item-1",
    title="Authentication API",
    contract_type="api",
    preconditions=[{"name": "token", "type": "string"}],
    postconditions=[{"name": "user_id", "type": "string"}],
    states=["INIT", "AUTHENTICATING", "AUTHENTICATED"],
    transitions=[{"from": "INIT", "to": "AUTHENTICATING"}],
)
```

---

### FeatureService

**Purpose:** Manage BDD Features (user stories in Gherkin format)

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `create()` | Create feature with user story format |
| `get()` | Retrieve feature by ID |
| `list_by_project()` | List with pagination and filtering |
| `update()` | Update with optimistic locking |
| `delete()` | Delete feature |
| `get_with_scenarios()` | Get feature with related scenarios |
| `calculate_pass_rate()` | Calculate average scenario pass rate |

**Auto-generated Fields:**
- `feature_number` - Sequential (FEAT-0001, FEAT-0002, etc.)
- `version` - Incremented on each update
- `created_at`, `updated_at` - Timestamps

**Key Data:**
- User story format: as_a, i_want, so_that
- Description, status
- File path for .feature file
- Related requirements and ADRs
- Tags

**Example:**
```python
feature = await feature_service.create(
    project_id="proj-1",
    name="User Login",
    as_a="Registered user",
    i_want="to login to the application",
    so_that="I can access my account",
)
```

---

### ScenarioService

**Purpose:** Manage BDD Scenarios with Gherkin steps

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `create()` | Create scenario with Gherkin steps |
| `get()` | Retrieve scenario by ID |
| `list_by_feature()` | List scenarios for a feature |
| `update()` | Update with optimistic locking |
| `delete()` | Delete scenario |
| `run()` | Execute scenario and record results |
| `update_pass_rate()` | Update pass rate metric |
| `link_test_cases()` | Link test cases to scenario |

**Auto-generated Fields:**
- `scenario_number` - Relative to feature (FEAT-0001-SC-001, etc.)
- `version` - Incremented on each update
- `created_at`, `updated_at` - Timestamps

**Key Data:**
- Gherkin text and description
- Background, Given, When, Then steps
- Scenario outline and examples
- Pass rate (0.0-1.0)
- Status (draft, executed)
- Related requirements and test cases
- Execution results in metadata

**Example:**
```python
scenario = await scenario_service.create(
    feature_id="feat-1",
    title="Successful login",
    gherkin_text="Given user is on login page\n...",
    given_steps=[{"text": "user is on login page"}],
    when_steps=[{"text": "user enters credentials"}],
    then_steps=[{"text": "user is logged in"}],
)
```

---

### StepDefinitionService

**Purpose:** Manage reusable BDD step definitions

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `create()` | Create step definition with pattern |
| `get()` | Retrieve step definition |
| `find_matching()` | Find definitions matching text |
| `list_by_project()` | List with filtering by type |
| `update()` | Update step definition |
| `delete()` | Delete step definition |
| `increment_usage()` | Track usage metrics |

**Key Data:**
- Step pattern (regex)
- Step type (given, when, then)
- Implementation code
- Language (python, javascript, etc.)
- Parameters and description
- Usage count tracking
- Version tracking

**Example:**
```python
step = await step_service.create(
    project_id="proj-1",
    step_pattern=r"^user enters (.+) in (\w+) field$",
    step_type="when",
    implementation_code="def step_impl(context, value, field): ...",
    language="python",
)
```

---

## Design Patterns Used

### 1. Sequential Numbering Pattern
- Auto-generates unique identifiers per project
- Query for last entity and increment
- Format: `TYPE-XXXX` (e.g., ADR-0001)

### 2. Optimistic Locking Pattern
- Version field on each entity
- Automatic retry with exponential backoff
- Handles concurrent updates safely

### 3. List/Filter/Paginate Pattern
- Consistent interface: `list_by_*(skip, limit)`
- Filter by status, type, search terms
- Returns tuple: (items, total_count)

### 4. Relationship Management Pattern
- JSON arrays for many-to-many relationships
- Set operations for uniqueness
- Dedicated link/unlink methods

### 5. Error Handling Pattern
- Returns None for not found (instead of exceptions)
- Validates state transitions
- Propagates database errors

---

## Data Models

### ADR Model
```
id (UUID)
project_id (FK)
adr_number (String, unique per project)
title (String)
status (String: proposed, accepted, deprecated, superseded)
context, decision, consequences (Text)
decision_drivers, considered_options (JSON)
related_requirements, related_adrs (JSON)
compliance_score, last_verified_at (Float, DateTime)
stakeholders, tags (JSON)
date (Date)
version, created_at, updated_at
metadata_ (JSON)
```

### Contract Model
```
id (UUID)
project_id (FK)
item_id (FK)
contract_number (String, unique per project)
title, contract_type, status (String)
preconditions, postconditions, invariants (JSON)
states, transitions (JSON)
executable_spec, spec_language (Text, String)
last_verified_at, verification_result (DateTime, JSON)
tags (JSON)
version, created_at, updated_at
metadata_ (JSON)
```

### Feature Model
```
id (UUID)
project_id (FK)
feature_number (String, unique per project)
name, description (String, Text)
as_a, i_want, so_that (String - user story format)
status, file_path (String)
tags, related_requirements, related_adrs (JSON)
version, created_at, updated_at
metadata_ (JSON)
```

### Scenario Model
```
id (UUID)
feature_id (FK)
scenario_number (String, unique per feature)
title, description, gherkin_text (String, Text)
background, given_steps, when_steps, then_steps (JSON)
is_outline, examples (Boolean, JSON)
tags, requirement_ids, test_case_ids (JSON)
status, pass_rate (String, Float)
version, created_at, updated_at
metadata_ (JSON)
```

---

## Quick Start Guide

### 1. Create ADR
```python
from tracertm.services.specification_service import ADRService

service = ADRService(session)
adr = await service.create(
    project_id="proj-1",
    title="Use SQLAlchemy for ORM",
    context="Need Object-Relational Mapping",
    decision="Use SQLAlchemy with async support",
    consequences="Learning curve for team",
)
print(f"Created {adr.adr_number}")  # ADR-0001
```

### 2. Create Feature with Scenarios
```python
from tracertm.services.specification_service import FeatureService, ScenarioService

feature_svc = FeatureService(session)
scenario_svc = ScenarioService(session)

# Create feature
feature = await feature_svc.create(
    project_id="proj-1",
    name="User Registration",
    as_a="New user",
    i_want="to create an account",
    so_that="I can access the platform",
)

# Create scenario
scenario = await scenario_svc.create(
    feature_id=feature.id,
    title="Successful registration",
    gherkin_text="Given user is on signup page\nWhen user enters email\nThen account is created",
)

# Run scenario
await scenario_svc.run(scenario.id, {"passed_steps": 3})
```

### 3. Verify ADR Compliance
```python
# Update compliance
adr = await service.verify_compliance("adr-uuid", 0.85)
print(f"ADR {adr.adr_number} compliance: {adr.compliance_score}")

# Link requirements
adr = await service.link_requirements("adr-uuid", ["REQ-001", "REQ-002"])
```

### 4. Manage Contracts
```python
contract_svc = ContractService(session)

contract = await contract_svc.create(
    project_id="proj-1",
    item_id="item-1",
    title="Payment API",
    contract_type="api",
)

# Execute state transition
contract = await contract_svc.execute_transition(
    contract.id, "INIT", "PROCESSING"
)

# Verify contract
contract = await contract_svc.verify(contract.id, {
    "status": "passed",
    "checks": 10,
    "passed": 10,
})
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/unit/services/test_specification_service.py -v
```

### Run Specific Service Tests
```bash
pytest tests/unit/services/test_specification_service.py::TestADRService -v
pytest tests/unit/services/test_specification_service.py::TestFeatureService -v
```

### Run with Coverage
```bash
pytest tests/unit/services/test_specification_service.py --cov=tracertm.services.specification_service
```

---

## Integration Points

### Database
- SQLAlchemy ORM models
- AsyncSession for async operations
- RLS policies for multi-tenancy
- Migrations in `alembic/versions/`

### API
- FastAPI routers
- tRPC integration
- Pydantic schemas for validation
- OpenAPI documentation

### Authentication
- WorkOS AuthKit JWT tokens
- User context in requests
- Audit trail via created_by fields

### Notifications
- Webhook support (future)
- Event system (future)
- Audit logging (via version field)

---

## Best Practices

1. **Always use async/await**
   ```python
   service = ADRService(session)
   adr = await service.get("adr-id")
   ```

2. **Handle None returns**
   ```python
   adr = await service.get("invalid-id")
   if not adr:
       raise ValueError("ADR not found")
   ```

3. **Commit explicitly**
   ```python
   adr = await service.create(...)
   await session.commit()  # Service flushes but doesn't commit
   ```

4. **Use filtering for lists**
   ```python
   adrs, total = await service.list_by_project(
       "proj-1",
       status="accepted",
       skip=0,
       limit=20
   )
   ```

5. **Track versions for audit**
   ```python
   # Version is auto-incremented on updates
   adr = await service.update("adr-id", title="New title")
   print(f"Updated to version {adr.version}")
   ```

---

## File Locations

| File | Location | Size | Lines |
|------|----------|------|-------|
| Service Implementation | `/src/tracertm/services/specification_service.py` | 25 KB | 820 |
| Unit Tests | `/tests/unit/services/test_specification_service.py` | 19 KB | 650 |
| API Guide | `SPECIFICATION_SERVICES_GUIDE.md` | 19 KB | 500+ |
| Integration Examples | `SPECIFICATION_SERVICES_INTEGRATION_EXAMPLE.md` | 31 KB | 800+ |
| This Index | `SPECIFICATION_SERVICES_INDEX.md` | - | - |

---

## Version Information

- **Python:** 3.10+
- **SQLAlchemy:** 2.0+ (async support)
- **FastAPI:** 0.100+
- **Pydantic:** 2.0+
- **pytest:** 7.4+

---

## Next Steps

1. **Create Schemas**
   - Implement Pydantic models in `/src/tracertm/schemas/`
   - Request/response types
   - Validation rules

2. **Implement tRPC Routers**
   - Create routers in `/src/tracertm/api/routers/`
   - Integrate with dependency injection
   - Add authentication/authorization

3. **Database Migrations**
   - Create Alembic migrations
   - Add any missing indexes
   - Enable RLS policies

4. **E2E Tests**
   - Create Playwright tests
   - Test complete workflows
   - Verify API endpoints

5. **Integration**
   - Connect to frontend components
   - Add webhook support
   - Implement caching

---

## Support & Questions

For detailed information:
- See `SPECIFICATION_SERVICES_GUIDE.md` for API reference
- See `SPECIFICATION_SERVICES_INTEGRATION_EXAMPLE.md` for integration patterns
- See `tests/unit/services/test_specification_service.py` for usage examples

For implementation questions, refer to:
- Service docstrings in `specification_service.py`
- Model definitions in `/src/tracertm/models/`
- Existing service patterns in `/src/tracertm/services/`
