# Specification Services Guide

Comprehensive guide for the backend services that handle Architecture Decision Records (ADR), Contracts, Features, Scenarios, and Step Definitions.

## Overview

The specification services provide a complete implementation for managing specification entities in TraceRTM. Each service follows a consistent pattern with full CRUD operations, business logic validation, and async/await patterns.

**File Location:** `/src/tracertm/services/specification_service.py`

## Service Classes

### 1. ADRService

Service for managing Architecture Decision Records (MADR 4.0 format).

#### Methods

##### `create()`
Creates a new ADR with sequential numbering.

```python
adr = await service.create(
    project_id="proj-1",
    title="Use async/await for I/O operations",
    context="Need to handle asynchronous database operations",
    decision="Adopt Python async/await pattern with asyncio",
    consequences="Requires asyncio knowledge from team",
    status="proposed",  # proposed, accepted, deprecated, superseded
    decision_drivers=["Performance", "Code clarity", "Team expertise"],
    considered_options=[
        {"name": "Callbacks", "pros": ["Traditional"], "cons": ["Callback hell"]},
        {"name": "Promises", "pros": ["Chainable"], "cons": ["Complex"]},
    ],
    related_requirements=["REQ-001", "REQ-002"],
    related_adrs=["ADR-0001"],
    stakeholders=["Backend team", "DevOps"],
    tags=["architecture", "python"],
    date_value=date.today(),
)
```

**Returns:** `ADR` object with auto-generated ADR number (ADR-0001, ADR-0002, etc.)

##### `get(adr_id: str)`
Retrieve an ADR by ID.

```python
adr = await service.get("adr-uuid")
```

##### `list_by_project(project_id: str, status: Optional[str] = None, skip: int = 0, limit: int = 50)`
List ADRs for a project with optional filtering and pagination.

```python
adrs, total = await service.list_by_project(
    "proj-1",
    status="accepted",
    skip=0,
    limit=20
)
```

**Returns:** Tuple of (list of ADR objects, total count)

##### `update(adr_id: str, **updates)`
Update ADR with optimistic locking (retries on version conflicts).

```python
adr = await service.update(
    "adr-uuid",
    title="Updated title",
    status="accepted",
    compliance_score=0.95
)
```

##### `delete(adr_id: str)`
Delete an ADR.

```python
success = await service.delete("adr-uuid")
```

##### `verify_compliance(adr_id: str, compliance_score: float, verified_at: Optional[datetime] = None)`
Verify ADR compliance and update compliance score (0.0-1.0).

```python
adr = await service.verify_compliance(
    "adr-uuid",
    compliance_score=0.85,
    verified_at=datetime.now()
)
```

##### `link_requirements(adr_id: str, requirement_ids: list[str])`
Link multiple requirements to an ADR (maintains uniqueness).

```python
adr = await service.link_requirements(
    "adr-uuid",
    ["REQ-003", "REQ-004"]
)
```

##### `supersede(adr_id: str, superseded_by_number: str)`
Mark ADR as superseded by another ADR.

```python
adr = await service.supersede("adr-uuid", "ADR-0005")
```

---

### 2. ContractService

Service for managing Design-by-Contract specifications.

#### Methods

##### `create()`
Create a new Contract with state machines and verification specs.

```python
contract = await service.create(
    project_id="proj-1",
    item_id="item-1",
    title="User Authentication API",
    contract_type="api",  # api, function, state_machine, etc.
    preconditions=[
        {"name": "auth_token", "type": "string", "required": True},
        {"name": "user_id", "type": "string", "required": True},
    ],
    postconditions=[
        {"name": "response_code", "type": "integer", "value": 200},
        {"name": "response_body", "type": "json", "schema": {...}},
    ],
    invariants=[
        {"name": "user_must_be_active", "check": "SELECT active FROM users WHERE id=?"},
    ],
    states=["INIT", "AUTHENTICATING", "AUTHENTICATED", "ERROR"],
    transitions=[
        {"from": "INIT", "to": "AUTHENTICATING"},
        {"from": "AUTHENTICATING", "to": "AUTHENTICATED"},
        {"from": "AUTHENTICATING", "to": "ERROR"},
    ],
    executable_spec="def authenticate(token): ...",
    spec_language="python",
)
```

**Returns:** `Contract` object with auto-generated contract number

##### `get(contract_id: str)`
Retrieve a Contract by ID.

##### `list_by_project(project_id: str, contract_type: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 50)`
List contracts for a project with filtering.

```python
contracts, total = await service.list_by_project(
    "proj-1",
    contract_type="api",
    status="active"
)
```

##### `list_by_item(item_id: str)`
List all contracts for a specific item.

```python
contracts = await service.list_by_item("item-uuid")
```

##### `update(contract_id: str, **updates)`
Update a Contract with optimistic locking.

##### `delete(contract_id: str)`
Delete a Contract.

##### `verify(contract_id: str, verification_result: dict)`
Verify contract and store verification results.

```python
verification = {
    "status": "passed",
    "checks": 10,
    "passed": 10,
    "failed": 0,
    "details": [...]
}
contract = await service.verify("contract-uuid", verification)
```

##### `execute_transition(contract_id: str, from_state: str, to_state: str)`
Execute a valid state transition in the contract.

```python
contract = await service.execute_transition(
    "contract-uuid",
    from_state="INIT",
    to_state="AUTHENTICATING"
)
# Validates transition exists in contract.transitions
# Updates metadata with current_state
```

---

### 3. FeatureService

Service for managing BDD Features (user stories).

#### Methods

##### `create()`
Create a new BDD Feature with user story format.

```python
feature = await service.create(
    project_id="proj-1",
    name="User Registration",
    description="Allow new users to create accounts",
    as_a="New user",
    i_want="to create an account",
    so_that="I can access the platform",
    status="draft",  # draft, active, deprecated
    file_path="/features/auth/registration.feature",
    tags=["authentication", "user-management"],
    related_requirements=["REQ-001"],
    related_adrs=["ADR-0003"],
)
```

**Returns:** `Feature` object with auto-generated feature number (FEAT-0001, etc.)

##### `get(feature_id: str)`
Retrieve a Feature by ID.

##### `list_by_project(project_id: str, status: Optional[str] = None, skip: int = 0, limit: int = 50)`
List features for a project.

```python
features, total = await service.list_by_project("proj-1", status="active")
```

##### `update(feature_id: str, **updates)`
Update a Feature with optimistic locking.

##### `delete(feature_id: str)`
Delete a Feature.

##### `get_with_scenarios(feature_id: str)`
Get Feature with all related scenarios.

```python
feature_data = await service.get_with_scenarios("feat-uuid")
# Returns: {
#     "feature": Feature object,
#     "scenarios": [Scenario, ...],
#     "scenario_count": 5
# }
```

##### `calculate_pass_rate(feature_id: str)`
Calculate average pass rate across all scenarios.

```python
pass_rate = await service.calculate_pass_rate("feat-uuid")
# Returns: 0.0 to 1.0
```

---

### 4. ScenarioService

Service for managing BDD Scenarios (test cases written in Gherkin).

#### Methods

##### `create()`
Create a new Scenario with Gherkin steps.

```python
scenario = await service.create(
    feature_id="feat-1",
    title="User login with valid credentials",
    description="Verify successful login with correct email/password",
    gherkin_text="""Given user is on login page
When user enters valid email
And user enters valid password
And user clicks login button
Then user is redirected to dashboard
And user profile is displayed""",
    background=[
        {"text": "Given database is in clean state", "status": "pending"}
    ],
    given_steps=[
        {"text": "user is on login page", "status": "pending"},
        {"text": "user has registered account", "status": "pending"},
    ],
    when_steps=[
        {"text": "user enters valid email", "status": "pending"},
        {"text": "user enters valid password", "status": "pending"},
        {"text": "user clicks login button", "status": "pending"},
    ],
    then_steps=[
        {"text": "user is redirected to dashboard", "status": "pending"},
        {"text": "user profile is displayed", "status": "pending"},
    ],
    is_outline=False,
    tags=["smoke", "critical"],
    requirement_ids=["REQ-002"],
    test_case_ids=["TC-001"],
)
```

**Returns:** `Scenario` object with auto-generated scenario number (FEAT-0001-SC-001, etc.)

##### `get(scenario_id: str)`
Retrieve a Scenario by ID.

##### `list_by_feature(feature_id: str, status: Optional[str] = None)`
List scenarios for a feature.

```python
scenarios = await service.list_by_feature("feat-uuid", status="active")
```

##### `update(scenario_id: str, **updates)`
Update a Scenario with optimistic locking.

##### `delete(scenario_id: str)`
Delete a Scenario.

##### `run(scenario_id: str, results: dict)`
Run scenario and record execution results.

```python
results = {
    "passed_steps": 5,
    "failed_steps": 0,
    "skipped_steps": 0,
    "execution_time": 2.5,
    "environment": "staging",
}
scenario = await service.run("scenario-uuid", results)
# Calculates pass_rate = passed_steps / total_steps
# Sets status = "executed"
# Stores results in metadata["last_run"]
```

##### `update_pass_rate(scenario_id: str, pass_rate: float)`
Update scenario pass rate (0.0-1.0).

```python
scenario = await service.update_pass_rate("scenario-uuid", 0.85)
```

##### `link_test_cases(scenario_id: str, test_case_ids: list[str])`
Link test cases to a scenario.

```python
scenario = await service.link_test_cases(
    "scenario-uuid",
    ["TC-002", "TC-003"]
)
```

---

### 5. StepDefinitionService

Service for managing BDD Step Definitions (reusable step implementations).

#### Methods

##### `create()`
Create a new Step Definition.

```python
step = await service.create(
    project_id="proj-1",
    step_pattern=r"^user enters (.+) in (\w+) field$",
    step_type="when",  # given, when, then
    implementation_code="""
def step_user_enters_value(context, value, field):
    element = context.driver.find_element(field)
    element.send_keys(value)
""",
    language="python",
    description="User enters a value into a form field",
    parameters=[
        {"name": "value", "type": "string"},
        {"name": "field", "type": "string"},
    ],
    tags=["ui-automation"],
)
```

**Returns:** Dictionary representing the step definition

##### `get(step_id: str)`
Retrieve a Step Definition by ID. (Placeholder implementation)

##### `find_matching(project_id: str, step_text: str, step_type: Optional[str] = None)`
Find step definitions matching text pattern.

```python
matches = await service.find_matching(
    project_id="proj-1",
    step_text="user enters email in email field",
    step_type="when"
)
```

**Returns:** List of matching step definitions

##### `list_by_project(project_id: str, step_type: Optional[str] = None, skip: int = 0, limit: int = 50)`
List step definitions for a project.

##### `update(step_id: str, **updates)`
Update a Step Definition.

##### `delete(step_id: str)`
Delete a Step Definition.

##### `increment_usage(step_id: str)`
Increment usage count for tracking popular steps.

---

## Usage Examples

### Complete BDD Feature Workflow

```python
from sqlalchemy.ext.asyncio import AsyncSession
from tracertm.services.specification_service import (
    FeatureService,
    ScenarioService,
)

async def create_feature_workflow(session: AsyncSession, project_id: str):
    """Create a feature with scenarios."""
    feature_service = FeatureService(session)
    scenario_service = ScenarioService(session)

    # Create feature
    feature = await feature_service.create(
        project_id=project_id,
        name="User Login",
        as_a="Registered user",
        i_want="to login to the application",
        so_that="I can access my account",
    )

    # Create scenarios for feature
    scenario1 = await scenario_service.create(
        feature_id=feature.id,
        title="Login with valid credentials",
        gherkin_text="Given user is on login page\nWhen user enters credentials\nThen user is logged in",
        given_steps=[{"text": "user is on login page"}],
        when_steps=[{"text": "user enters credentials"}],
        then_steps=[{"text": "user is logged in"}],
    )

    scenario2 = await scenario_service.create(
        feature_id=feature.id,
        title="Login with invalid credentials",
        gherkin_text="Given user is on login page\nWhen user enters wrong password\nThen error message is shown",
        given_steps=[{"text": "user is on login page"}],
        when_steps=[{"text": "user enters wrong password"}],
        then_steps=[{"text": "error message is shown"}],
    )

    # Get feature with scenarios
    feature_data = await feature_service.get_with_scenarios(feature.id)
    print(f"Feature {feature.name} has {feature_data['scenario_count']} scenarios")

    # Run scenarios
    await scenario_service.run(scenario1.id, {"passed_steps": 3, "failed_steps": 0})
    await scenario_service.run(scenario2.id, {"passed_steps": 3, "failed_steps": 0})

    # Calculate pass rate
    pass_rate = await feature_service.calculate_pass_rate(feature.id)
    print(f"Feature pass rate: {pass_rate * 100}%")

    await session.commit()
```

### ADR Management

```python
async def create_adr_with_compliance(session: AsyncSession, project_id: str):
    """Create ADR and track compliance."""
    adr_service = ADRService(session)

    # Create ADR
    adr = await adr_service.create(
        project_id=project_id,
        title="Microservices Architecture",
        context="Monolith becoming difficult to scale",
        decision="Migrate to microservices",
        consequences="Increased complexity in deployment",
        decision_drivers=["Scalability", "Team autonomy"],
        stakeholders=["Architecture team", "DevOps"],
    )

    # Link requirements
    adr = await adr_service.link_requirements(
        adr.id,
        ["REQ-SCALE-001", "REQ-SCALE-002"]
    )

    # Verify compliance over time
    await adr_service.verify_compliance(adr.id, 0.75)

    # Supersede when newer ADR created
    adr = await adr_service.supersede(adr.id, "ADR-0010")

    await session.commit()
```

### Contract Verification

```python
async def manage_contracts(session: AsyncSession, project_id: str, item_id: str):
    """Create and verify contracts."""
    contract_service = ContractService(session)

    # Create contract
    contract = await contract_service.create(
        project_id=project_id,
        item_id=item_id,
        title="Payment API",
        contract_type="api",
        preconditions=[
            {"name": "api_key", "type": "string"},
            {"name": "amount", "type": "float"},
        ],
        states=["INIT", "PROCESSING", "SUCCESS", "FAILED"],
        transitions=[
            {"from": "INIT", "to": "PROCESSING"},
            {"from": "PROCESSING", "to": "SUCCESS"},
            {"from": "PROCESSING", "to": "FAILED"},
        ],
    )

    # Execute state transitions
    contract = await contract_service.execute_transition(
        contract.id,
        from_state="INIT",
        to_state="PROCESSING"
    )

    # Verify contract
    verification = {
        "status": "passed",
        "checks": 5,
        "passed": 5,
        "failed": 0,
    }
    contract = await contract_service.verify(contract.id, verification)

    await session.commit()
```

## Design Patterns

### 1. Sequential Numbering
Each service generates sequential identifiers (ADR-0001, FEAT-0001, etc.) based on the last created entity.

```python
# Handles duplicate creation safely by querying last entity
last_entity = await session.execute(
    select(Entity)
    .where(Entity.project_id == project_id)
    .order_by(Entity.created_at.desc())
    .limit(1)
)
```

### 2. Optimistic Locking
Update operations use version tracking with automatic retry on conflicts.

```python
async def do_update() -> Entity:
    entity = await self.get(entity_id)
    if not entity:
        raise ValueError(f"Entity {entity_id} not found")

    # Apply updates
    entity.version += 1
    self.session.add(entity)
    await self.session.flush()
    return entity

# Retries automatically on ConcurrencyError
return await update_with_retry(do_update)
```

### 3. List with Pagination
All `list_*` methods support filtering and pagination.

```python
query = select(Entity).where(Entity.project_id == project_id)

# Add filters
if status:
    query = query.where(Entity.status == status)

# Count total
count_query = select(func.count()).select_from(query.subquery())
total = await session.execute(count_query)

# Apply pagination
query = query.offset(skip).limit(limit)
```

### 4. Relationship Management
Services maintain many-to-many relationships using JSON arrays.

```python
# Link items
entity.related_items = list(set(entity.related_items or []) | set(new_items))

# Unlink items
entity.related_items = [item for item in entity.related_items if item not in items_to_remove]
```

## Error Handling

Services follow consistent error handling:

1. **Not Found:** Methods return `None` instead of raising exceptions
2. **Validation:** Constructor validates required fields
3. **Concurrency:** Update operations retry automatically on version conflicts
4. **Database:** All errors propagate from SQLAlchemy

```python
# Safe get operations
adr = await service.get("invalid-id")  # Returns None

# Safe update with retry
adr = await service.update("id", title="New")  # Retries on conflict, returns None if not found

# Safe delete
success = await service.delete("id")  # Returns True/False
```

## Testing

Each service includes comprehensive unit tests covering:

- CRUD operations
- Business logic validation
- Error handling
- Pagination and filtering
- Relationship management
- Concurrent updates

See `tests/unit/services/test_specification_service.py`

## Best Practices

1. **Always use async/await:** All methods are async
2. **Explicit session management:** Pass AsyncSession to constructor
3. **Validate input:** Use Zod/Pydantic schemas before service calls
4. **Handle None returns:** List methods return empty lists, get methods return None
5. **Commit explicitly:** Services flush but don't commit; let caller decide
6. **Track versions:** Updates increment version for audit trails
7. **Use filtering:** Leverage status/type filters in list methods
8. **Link relationships:** Use dedicated link methods for many-to-many

## Integration with tRPC

```python
# In tRPC router
@router.post("/adrs")
async def create_adr(
    session: Annotated[AsyncSession, Depends(get_db)],
    input: CreateADRRequest,
) -> ADR:
    service = ADRService(session)
    adr = await service.create(**input.model_dump())
    await session.commit()
    return adr
```
