# Specification Repositories Documentation

Complete implementation of specification repositories for TraceRTM, providing CRUD operations and advanced queries for Architecture Decision Records (ADRs), Contracts, Features, and Scenarios.

## Overview

The specification repositories provide a comprehensive layer for managing formal specifications and BDD artifacts:

- **ADRRepository**: Architecture Decision Records with compliance tracking
- **ContractRepository**: Design by Contract specifications with state machines
- **FeatureRepository**: BDD Features with user story format
- **ScenarioRepository**: Gherkin scenarios with execution tracking

All repositories implement:
- Async SQLAlchemy patterns with proper session handling
- Optimistic locking with version tracking
- Status transition validation
- Comprehensive querying and filtering
- Activity logging where applicable

## File Location

```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/repositories/specification_repository.py
```

## Repository Classes

### ADRRepository

Manages Architecture Decision Records following MADR 4.0 format.

#### Core Methods

```python
# Creation
adr = await repo.create(
    project_id="proj-123",
    title="Use PostgreSQL for database",
    context="Need stable relational database",
    decision="PostgreSQL 14+",
    consequences="Better performance, learning curve",
    status="proposed",
    decision_drivers=["performance", "reliability"],
    considered_options=[...],
    related_requirements=["REQ-001"],
    related_adrs=["ADR-001"],
    compliance_score=0.9,
    stakeholders=["backend-team"],
    tags=["database"]
)

# Retrieval
adr = await repo.get_by_id("adr-123")
adr = await repo.get_by_number("ADR-20250120-ABCD1234", project_id="proj-123")

# Listing
adrs = await repo.list_by_project(project_id="proj-123", status="accepted")
adrs = await repo.find_by_status(project_id="proj-123", status="proposed")
related = await repo.find_related(adr_id="adr-123")

# Status transitions
adr = await repo.transition_status(adr_id="adr-123", to_status="accepted")

# Verification
adr = await repo.verify_compliance(adr_id="adr-123", compliance_score=0.95)

# Updates
adr = await repo.update(adr_id="adr-123", expected_version=1, title="New Title")

# Deletion
deleted = await repo.delete(adr_id="adr-123")

# Analytics
counts = await repo.count_by_status(project_id="proj-123")
# Returns: {"proposed": 2, "accepted": 3, "deprecated": 1}
```

#### Status Transitions

Valid state machine:
- `proposed` → `accepted`, `rejected`
- `accepted` → `deprecated`
- `rejected` → `proposed`
- `deprecated` → terminal

#### Key Features

- Unique ADR numbering: `ADR-YYYYMMDD-XXXXXXXX`
- Supersedes tracking for ADR relationships
- Compliance scoring (0.0-1.0 range)
- Stakeholder tracking
- Decision drivers and considered options as JSON

### ContractRepository

Manages formal contracts with Design by Contract patterns.

#### Core Methods

```python
# Creation
contract = await repo.create(
    project_id="proj-123",
    item_id="item-456",
    title="Payment API Contract",
    contract_type="api",
    status="draft",
    preconditions=[
        {"name": "user_authenticated", "type": "boolean"},
        {"name": "amount_valid", "type": "numeric"}
    ],
    postconditions=[
        {"name": "transaction_recorded", "type": "boolean"},
        {"name": "notification_sent", "type": "boolean"}
    ],
    invariants=[
        {"name": "balance_non_negative", "type": "numeric"}
    ],
    states=["pending", "processing", "completed", "failed"],
    transitions=[
        {"from": "pending", "to": "processing", "trigger": "process"}
    ],
    executable_spec="function processPayment(amount) { ... }",
    spec_language="javascript"
)

# Retrieval
contract = await repo.get_by_id("contract-123")
contract = await repo.get_by_number("CTR-20250120-ABCD1234")

# Listing
contracts = await repo.list_by_project(
    project_id="proj-123",
    contract_type="api",
    status="approved"
)
contracts = await repo.list_by_item(item_id="item-456")

# Verification
contract = await repo.verify(
    contract_id="contract-123",
    verification_result={
        "passed": True,
        "checks": ["preconditions_ok", "postconditions_ok"],
        "warnings": []
    }
)

# Status transitions
contract = await repo.transition_status(
    contract_id="contract-123",
    to_status="approved"
)

# Updates
contract = await repo.update(
    contract_id="contract-123",
    expected_version=1,
    executable_spec="new spec"
)

# Deletion
deleted = await repo.delete(contract_id="contract-123")

# Analytics
counts = await repo.count_by_type(project_id="proj-123")
# Returns: {"api": 5, "function": 3, "service": 2}
```

#### Contract Types

- `api`: REST/GraphQL API contracts
- `function`: Function/method contracts
- `service`: Service-level agreements
- `data`: Data transformation contracts
- `workflow`: Workflow state contracts

#### Status Transitions

Valid state machine:
- `draft` → `review`, `deprecated`
- `review` → `draft`, `approved`, `deprecated`
- `approved` → `review`, `deprecated`, `archived`
- `deprecated` → `draft`
- `archived` → terminal

### FeatureRepository

Manages BDD Features with user story format.

#### Core Methods

```python
# Creation
feature = await repo.create(
    project_id="proj-123",
    name="User Authentication",
    description="Implement user login",
    as_a="user",
    i_want="to log in with email",
    so_that="I can access my account",
    status="draft",
    related_requirements=["REQ-001", "REQ-002"],
    related_adrs=["ADR-001"],
    tags=["authentication", "security"]
)

# Retrieval
feature = await repo.get_by_id("feature-123")
feature = await repo.get_by_number("FEAT-20250120-ABCD1234")

# Listing
features = await repo.list_by_project(
    project_id="proj-123",
    status="draft",
    limit=50,
    offset=0
)

# With scenarios
features_with_scenarios = await repo.list_with_scenarios(
    project_id="proj-123",
    limit=50
)
# Returns: [(Feature, [Scenario, ...]), ...]

# Status transitions
feature = await repo.transition_status(
    feature_id="feature-123",
    to_status="approved"
)

# Updates
feature = await repo.update(
    feature_id="feature-123",
    expected_version=1,
    name="Updated Feature Name"
)

# Deletion (cascades to scenarios)
deleted = await repo.delete(feature_id="feature-123")
```

#### Feature Status

Valid state machine:
- `draft` → `review`, `deprecated`
- `review` → `draft`, `approved`, `deprecated`
- `approved` → `implemented`, `deprecated`
- `implemented` → `deprecated`
- `deprecated` → terminal

#### User Story Format

```gherkin
As a <role>
I want <capability>
So that <benefit>
```

### ScenarioRepository

Manages Gherkin scenarios with execution tracking.

#### Core Methods

```python
# Creation
scenario = await repo.create(
    feature_id="feature-123",
    title="User logs in successfully",
    gherkin_text="Given user is on login page\nWhen user enters credentials\nThen user is logged in",
    status="draft",
    given_steps=[
        {"step": "user is on login page", "parameter": None}
    ],
    when_steps=[
        {"step": "user enters credentials", "parameter": "email"}
    ],
    then_steps=[
        {"step": "user is logged in", "parameter": None}
    ],
    tags=["happy-path", "critical"],
    requirement_ids=["REQ-001"],
    test_case_ids=["TC-001"]
)

# Scenario Outline
scenario = await repo.create(
    feature_id="feature-123",
    title="Login with various users",
    gherkin_text="...",
    is_outline=True,
    examples={
        "header": ["username", "password", "result"],
        "rows": [
            ["user1", "pass1", "success"],
            ["user2", "pass2", "success"],
            ["user3", "invalid", "failure"]
        ]
    }
)

# Retrieval
scenario = await repo.get_by_id("scenario-123")
scenario = await repo.get_by_number("SC-20250120-ABCD1234")

# Listing
scenarios = await repo.list_by_feature(
    feature_id="feature-123",
    status="draft"
)
scenarios = await repo.find_by_status(
    feature_id="feature-123",
    status="ready"
)

# Execution tracking
scenario = await repo.update_pass_rate(
    scenario_id="scenario-123",
    pass_rate=0.95
)

# Status transitions
scenario = await repo.transition_status(
    scenario_id="scenario-123",
    to_status="ready"
)

# Updates
scenario = await repo.update(
    scenario_id="scenario-123",
    expected_version=1,
    title="Updated Title"
)

# Deletion
deleted = await repo.delete(scenario_id="scenario-123")

# Analytics
counts = await repo.count_by_status(feature_id="feature-123")
avg_pass_rate = await repo.get_average_pass_rate(feature_id="feature-123")
```

#### Scenario Status

Valid state machine:
- `draft` → `review`, `ready`, `deprecated`
- `review` → `draft`, `ready`, `deprecated`
- `ready` → `executing`, `deprecated`
- `executing` → `ready`, `passed`, `failed`, `deprecated`
- `passed` → `executing`, `deprecated`
- `failed` → `executing`, `deprecated`
- `deprecated` → terminal

#### Step Format

Each step is a dictionary with:
- `step`: The step text
- `parameter`: Optional parameter value or null

## Database Models

### ADR Model

```python
class ADR:
    id: str                           # UUID
    adr_number: str                   # ADR-YYYYMMDD-XXXXXXXX
    project_id: str                   # FK to Project
    title: str
    status: str                       # proposed, accepted, deprecated, rejected
    context: str                      # Decision context
    decision: str                     # Actual decision
    consequences: str                 # Consequences of decision
    decision_drivers: List[str]       # Why this decision
    considered_options: List[dict]    # Options considered
    related_requirements: List[str]   # Related requirement IDs
    related_adrs: List[str]          # Related ADR IDs
    supersedes: Optional[str]         # ADR number it replaces
    superseded_by: Optional[str]      # ADR number that replaces it
    compliance_score: float           # 0.0-1.0
    last_verified_at: Optional[str]   # ISO timestamp
    stakeholders: List[str]           # Involved stakeholders
    tags: List[str]                   # Searchable tags
    date: datetime.date               # Decision date
    version: int                      # Optimistic lock
    metadata_: Optional[dict]         # Custom metadata
    created_at: datetime
    updated_at: datetime
```

### Contract Model

```python
class Contract:
    id: str                           # UUID
    contract_number: str              # CTR-YYYYMMDD-XXXXXXXX
    project_id: str                   # FK to Project
    item_id: str                      # FK to Item
    title: str
    contract_type: str                # api, function, service, data, workflow
    status: str                       # draft, review, approved, archived, deprecated
    preconditions: List[dict]         # {name, type}
    postconditions: List[dict]        # {name, type}
    invariants: List[dict]            # {name, type}
    states: List[str]                 # State machine states
    transitions: List[dict]           # {from, to, trigger}
    executable_spec: Optional[str]    # Executable specification
    spec_language: Optional[str]      # javascript, python, etc.
    last_verified_at: Optional[str]   # ISO timestamp
    verification_result: Optional[dict] # Verification details
    tags: List[str]
    version: int                      # Optimistic lock
    metadata_: Optional[dict]
    created_at: datetime
    updated_at: datetime
```

### Feature Model

```python
class Feature:
    id: str                           # UUID
    feature_number: str               # FEAT-YYYYMMDD-XXXXXXXX
    project_id: str                   # FK to Project
    name: str
    description: Optional[str]
    as_a: Optional[str]               # User story: as_a
    i_want: Optional[str]             # User story: i_want
    so_that: Optional[str]            # User story: so_that
    status: str                       # draft, review, approved, implemented, deprecated
    file_path: Optional[str]          # Path to feature file
    related_requirements: List[str]   # Related requirement IDs
    related_adrs: List[str]          # Related ADR IDs
    tags: List[str]
    version: int                      # Optimistic lock
    metadata_: Optional[dict]
    created_at: datetime
    updated_at: datetime
    scenarios: List[Scenario]         # Relationship
```

### Scenario Model

```python
class Scenario:
    id: str                           # UUID
    scenario_number: str              # SC-YYYYMMDD-XXXXXXXX
    feature_id: str                   # FK to Feature
    title: str
    description: Optional[str]
    gherkin_text: str                 # Full Gherkin text
    background: List[dict]            # Background steps
    given_steps: List[dict]           # Given steps
    when_steps: List[dict]            # When steps
    then_steps: List[dict]            # Then steps
    is_outline: bool                  # Is scenario outline
    examples: Optional[dict]          # {header: [...], rows: [...]}
    tags: List[str]
    requirement_ids: List[str]        # Related requirement IDs
    test_case_ids: List[str]         # Related test case IDs
    status: str                       # draft, review, ready, executing, passed, failed, deprecated
    pass_rate: float                  # 0.0-1.0
    version: int                      # Optimistic lock
    metadata_: Optional[dict]
    created_at: datetime
    updated_at: datetime
    feature: Feature                  # Relationship
```

## Usage Examples

### Creating an ADR

```python
from tracertm.repositories.specification_repository import ADRRepository

adr = await repo.create(
    project_id="proj-123",
    title="Implement API Rate Limiting",
    context="Need to prevent abuse and ensure fair usage",
    decision="Implement token bucket algorithm with Redis",
    consequences="Added Redis dependency, improved scalability",
    decision_drivers=["security", "performance", "scalability"],
    compliance_score=0.9
)
```

### Creating a Feature with Scenarios

```python
from tracertm.repositories.specification_repository import (
    FeatureRepository,
    ScenarioRepository
)

# Create feature
feature = await feature_repo.create(
    project_id="proj-123",
    name="Payment Processing",
    as_a="customer",
    i_want="to pay with credit card",
    so_that="I can complete my purchase"
)

# Create scenarios
scenario1 = await scenario_repo.create(
    feature_id=feature.id,
    title="User pays with valid card",
    gherkin_text="Given user has valid card\nWhen user enters payment\nThen payment is processed",
    given_steps=[{"step": "user has valid card"}],
    when_steps=[{"step": "user enters payment amount", "parameter": "50"}],
    then_steps=[{"step": "payment is processed"}],
    tags=["happy-path", "critical"]
)

# Update pass rate after execution
await scenario_repo.update_pass_rate(scenario1.id, 1.0)
```

### Contract Verification

```python
contract = await contract_repo.create(
    project_id="proj-123",
    item_id="item-456",
    title="Auth API Contract",
    contract_type="api",
    preconditions=[
        {"name": "user_exists", "type": "boolean"}
    ],
    postconditions=[
        {"name": "token_issued", "type": "boolean"}
    ]
)

# Verify contract
result = await contract_repo.verify(
    contract.id,
    verification_result={
        "passed": True,
        "checks": ["preconditions_ok", "postconditions_ok"],
        "warnings": []
    }
)
```

## Optimistic Locking

All repositories use optimistic locking to prevent concurrent modification issues:

```python
# Get current version
adr = await repo.get_by_id("adr-123")

# Update with version check
try:
    updated = await repo.update(
        adr.id,
        expected_version=adr.version,  # Must match
        title="New Title"
    )
except ConcurrencyError:
    # Handle concurrent modification
    pass
```

## Status Transitions

All entities enforce valid status transitions:

```python
# Valid transition
adr = await repo.transition_status(adr.id, "accepted")

# Invalid transition raises ValueError
try:
    adr = await repo.transition_status(adr.id, "proposed")  # Can't go backwards
except ValueError as e:
    print(f"Invalid transition: {e}")
```

## Querying and Filtering

### Project-scoped queries

```python
# List all active ADRs in project
adrs = await adr_repo.list_by_project(project_id="proj-123")

# Filter by status
accepted = await adr_repo.find_by_status(project_id="proj-123", status="accepted")

# With pagination
page = await contract_repo.list_by_project(
    project_id="proj-123",
    limit=50,
    offset=100
)
```

### Count operations

```python
# Count by status
counts = await adr_repo.count_by_status(project_id="proj-123")
# Returns: {"proposed": 2, "accepted": 5, "deprecated": 1}

# Count by type
type_counts = await contract_repo.count_by_type(project_id="proj-123")
# Returns: {"api": 5, "function": 3, "service": 2}
```

### Feature-scenario relationships

```python
# Get feature with all scenarios
features_with_scenarios = await feature_repo.list_with_scenarios(
    project_id="proj-123"
)

# Get scenarios by status
ready = await scenario_repo.find_by_status(
    feature_id="feature-123",
    status="ready"
)

# Get average pass rate
avg_pass = await scenario_repo.get_average_pass_rate(
    feature_id="feature-123"
)
```

## Error Handling

### ConcurrencyError

Raised when optimistic lock check fails:

```python
from tracertm.core.concurrency import ConcurrencyError

try:
    updated = await repo.update(id, expected_version=1, **updates)
except ConcurrencyError as e:
    # Handle concurrent modification
    print(f"Entity was modified: {e}")
```

### ValueError

Raised for invalid operations:

```python
try:
    # Try to transition to invalid status
    await repo.transition_status(id, "invalid_status")
except ValueError as e:
    print(f"Invalid transition: {e}")

try:
    # Try to update non-existent entity
    await repo.update(id, expected_version=1, **updates)
except ValueError as e:
    print(f"Entity not found: {e}")
```

## Testing

Comprehensive integration tests are provided in:

```
tests/integration/test_specification_repositories.py
```

Run tests with:

```bash
bun run test:api
pytest tests/integration/test_specification_repositories.py -v
```

### Test Coverage

- Basic CRUD operations for all repositories
- Status transitions with validation
- Optimistic locking behavior
- Version conflict detection
- Cascading deletions
- Relationship queries
- Analytics and aggregation
- Metadata handling
- Pagination and filtering

## Best Practices

### 1. Always commit after write operations

```python
adr = await repo.create(...)
await db_session.commit()  # Required for persistence
```

### 2. Use version tracking for updates

```python
adr = await repo.get_by_id(id)
updated = await repo.update(id, expected_version=adr.version, **updates)
```

### 3. Validate status transitions before updating

```python
try:
    updated = await repo.transition_status(id, new_status)
except ValueError as e:
    # Log and handle invalid transition
    pass
```

### 4. Use project_id filters for multi-tenancy

```python
# Always scope queries to project
items = await repo.list_by_project(project_id, status="draft")
```

### 5. Handle concurrent modifications

```python
try:
    updated = await repo.update(id, adr.version, **updates)
except ConcurrencyError:
    # Retry logic or notify user
    pass
```

## Performance Considerations

- Queries are indexed by `project_id`, `status`, and primary keys
- Use pagination for large result sets
- Avoid N+1 queries: use `list_with_scenarios` for feature-scenario relationships
- Lazy-load metadata JSON fields when needed
- Consider caching for frequently accessed ADRs

## Integration with Other Layers

### Services

Specification repositories are used by services:

```python
from tracertm.services.adr_service import ADRService

service = ADRService(adr_repo, db_session)
adr = await service.create_with_validation(...)
```

### API Routers

Repositories are injected through dependency injection:

```python
from tracertm.api.deps import get_adr_repository

async def create_adr(
    project_id: str,
    data: ADRSchema,
    repo: ADRRepository = Depends(get_adr_repository)
):
    return await repo.create(project_id=project_id, **data.dict())
```

## Future Enhancements

- [ ] Full-text search across ADR, Contract descriptions
- [ ] Audit trail for status transitions
- [ ] Compliance metrics aggregation
- [ ] ADR relationship visualization
- [ ] Feature coverage metrics
- [ ] Scenario execution history
- [ ] Contract verification hooks

## Related Files

- **Models**: `src/tracertm/models/{adr,contract,feature,scenario}.py`
- **Schemas**: `src/tracertm/schemas/{specification,test_case}.py`
- **Services**: `src/tracertm/services/{adr_service,feature_service}.py`
- **Tests**: `tests/integration/test_specification_repositories.py`
- **API Routers**: `src/tracertm/api/routers/{specifications,features}.py`
