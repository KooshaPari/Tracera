# Specification Models Quick Reference

## File Location
`src/tracertm/models/specification.py` (599 lines)

## Quick Stats
- **5 Models Created**: ADR, Contract, Feature, Scenario, StepDefinition
- **6 Enums Created**: ADRStatus, ContractType, ContractStatus, FeatureStatus, ScenarioStatus, StepType
- **Associations**: Feature→Scenario (1:many), Scenario↔TestCase (many:many)
- **Total Columns**: 140+ across all models
- **Total Indexes**: 15+

## Models at a Glance

| Model | Table | Key ID Field | Parent Ref | Status Enum | Purpose |
|-------|-------|--------------|-----------|------------|---------|
| ADR | `adrs` | adr_number | project_id | ADRStatus | Architecture decisions with rationale |
| Contract | `contracts` | contract_number | project_id | ContractStatus | Formal specs with pre/post conditions |
| Feature | `features` | feature_number | project_id | FeatureStatus | BDD user stories |
| Scenario | `scenarios` | scenario_number | feature_id | ScenarioStatus | BDD test scenarios (Given-When-Then) |
| StepDefinition | `step_definitions` | id (no number) | - | - | Gherkin step implementations |

## Core Features in All Models

```python
# All models include:
- id: str (UUID primary key)
- created_at: datetime (auto)
- updated_at: datetime (auto)
- version: int (optimistic locking)
- deleted_at: datetime | None (soft delete)
- {model}_metadata: dict (flexible JSON)
- Status field (except StepDefinition)
```

## ADR Specific

```python
ADR(
    adr_number="ADR-001",           # Unique per project
    project_id="...",
    title="Use microservices",
    status="accepted",              # proposed|accepted|deprecated|superseded|rejected
    context="...",
    decision="...",
    consequences="...",
    decision_drivers=["scalability"],
    considered_options=[{"option": "...", "pros": "...", "cons": "..."}],
    related_adrs=["ADR-002"],
    supersedes="ADR-001",
    superseded_by="ADR-003",
    compliance_score=0.85,
    stakeholders=["team-lead", "architect"],
    tags=["infrastructure", "critical"]
)
```

## Contract Specific

```python
Contract(
    contract_number="CTR-001",
    project_id="...",
    title="User Service API Contract",
    contract_type="interface",      # interface|component|service|system|integration|database
    status="approved",              # draft|review|approved|deprecated|archived
    preconditions="User must be authenticated",
    postconditions="User data is persisted",
    invariants=["user_id must not be null", "email must be valid"],
    states=["idle", "processing", "complete"],
    transitions=[
        {"from": "idle", "to": "processing", "condition": "call_received"},
        {"from": "processing", "to": "complete", "action": "save_data"}
    ],
    executable_spec="contract User { ... }",
    spec_language="alloy",
    verification_result="passed"
)
```

## Feature Specific

```python
Feature(
    feature_number="FEAT-001",
    project_id="...",
    name="User Authentication",
    description="Complete user auth system",
    as_a="user",
    i_want="log in securely",
    so_that="I can access my account",
    status="approved",              # draft|review|approved|deprecated|archived
    file_path="features/auth.feature",
    background="Given I have an active account\nAnd I am on the login page",
    tags=["auth", "critical", "smoke"],
    related_requirements=["REQ-001", "REQ-002"],
    related_adrs=["ADR-005"]
)
```

## Scenario Specific

```python
Scenario(
    scenario_number="SCEN-001",
    feature_id="...",
    title="Login with valid credentials",
    gherkin_text="Given I am on login page\nWhen I enter valid credentials\nThen I see dashboard",
    given_steps=["I am on login page"],
    when_steps=["I enter email 'user@test.com'", "I enter password 'password123'", "I click login"],
    then_steps=["I see the dashboard", "I see welcome message"],
    is_outline=False,               # True for scenario outlines
    examples=None,                  # [{columns: [...], rows: [...]}] for outlines
    tags=["happy-path"],
    status="approved",              # draft|review|approved|deprecated|archived
    requirement_ids=["REQ-001"],
    test_case_ids=["TC-001", "TC-002"],
    pass_rate=0.95,                 # From execution history
    last_executed_at=datetime.now()
)
```

## StepDefinition Specific

```python
StepDefinition(
    step_type="given",              # given|when|then|and|but
    pattern="I have {count} items in my cart",
    regex_pattern=r"I have (\d+) items in my cart",
    implementation_path="tests/steps/cart_steps.py",
    implementation_code="@given('I have {count} items')\ndef step_impl(context, count): ...",
    parameters=["count"],
    documentation="Setup initial cart state",
    examples=["I have 1 item in my cart", "I have 5 items in my cart"],
    usage_count=42,
    last_used_at=datetime.now()
)
```

## Relationships

```python
# Feature → Scenario (one-to-many)
feature = Feature(...)
scenario1 = Scenario(feature_id=feature.id, ...)
scenario2 = Scenario(feature_id=feature.id, ...)
# Access via: feature.scenarios

# Scenario ↔ TestCase (many-to-many)
scenario = Scenario(test_case_ids=["TC-001", "TC-002"])
# Or use relationship when available:
scenario.test_cases  # → List[TestCase]
```

## Querying Examples

```python
from tracertm.models.specification import ADR, ADRStatus

# Find accepted ADRs
adrs = session.query(ADR).filter(
    ADR.project_id == "proj-123",
    ADR.status == ADRStatus.ACCEPTED.value,
    ADR.deleted_at.is_(None)
).all()

# Find feature with scenarios
feature = session.query(Feature).filter_by(feature_number="FEAT-001").first()
print(feature.scenarios)  # → List[Scenario]

# Find active contracts by type
contracts = session.query(Contract).filter(
    Contract.project_id == "proj-123",
    Contract.contract_type == "interface",
    Contract.status.in_(["approved", "review"]),
    Contract.deleted_at.is_(None)
).all()
```

## Metadata Usage

```python
# All models support metadata alias
adr = ADR(
    adr_number="ADR-001",
    project_id="...",
    title="...",
    metadata={"custom_field": "value", "internal_notes": "..."}
)

# Access via metadata property (alias)
adr.metadata["custom_field"]  # → "value"

# Or via the full field name
adr.adr_metadata["custom_field"]  # → "value"

# Same works for Contract, Feature, Scenario
contract.metadata = {"verification_notes": "..."}
feature.metadata = {"github_issue": "#123"}
scenario.metadata = {"flaky": True, "flakiness_reason": "..."}
```

## Soft Delete Pattern

```python
from datetime import datetime
from sqlalchemy import func

# Soft delete
scenario.deleted_at = datetime.now(timezone.utc)
session.commit()

# Query active only
active_scenarios = session.query(Scenario).filter(
    Scenario.deleted_at.is_(None)
).all()

# Query deleted only
deleted_scenarios = session.query(Scenario).filter(
    Scenario.deleted_at.isnot(None)
).all()
```

## Optimistic Locking Pattern

```python
# Enable concurrency protection
try:
    adr = session.query(ADR).filter_by(id="...").first()
    adr.title = "Updated title"
    adr.version = adr.version + 1  # SQLAlchemy handles this
    session.commit()
except StaleDataError:
    # Someone else updated this record, reload and retry
    session.refresh(adr)
```

## Status Enum Values

### ADRStatus
- "proposed"
- "accepted"
- "deprecated"
- "superseded"
- "rejected"

### ContractStatus / FeatureStatus / ScenarioStatus
- "draft"
- "review"
- "approved"
- "deprecated"
- "archived"

### ContractType
- "interface"
- "component"
- "service"
- "system"
- "integration"
- "database"

### StepType
- "given"
- "when"
- "then"
- "and"
- "but"

## Integration with Existing Code

### Import in __init__.py
```python
try:
    from tracertm.models.specification import (
        ADR, ADRStatus,
        Contract, ContractType, ContractStatus,
        Feature, FeatureStatus,
        Scenario, ScenarioStatus,
        StepDefinition, StepType,
    )
except Exception:
    # Fallback for migrations
    ADR = None
    Contract = None
    Feature = None
    Scenario = None
    StepDefinition = None
```

### Use in Schemas
```python
from pydantic import BaseModel, Field
from tracertm.models.specification import ADRStatus

class ADRSchema(BaseModel):
    adr_number: str
    title: str
    status: ADRStatus
    context: str | None = None
```

### Use in Routers
```python
from tracertm.models.specification import ADR

@router.get("/adrs/{adr_number}")
async def get_adr(adr_number: str):
    adr = session.query(ADR).filter_by(adr_number=adr_number).first()
    return adr
```

## Indexes for Performance

```
ADR table indexes:
- idx_adrs_project_status (project_id, status)
- idx_adrs_project_adr_number (project_id, adr_number)
- idx_adrs_status (status)

Contract table indexes:
- idx_contracts_project_status (project_id, status)
- idx_contracts_project_type (project_id, contract_type)
- idx_contracts_contract_number (project_id, contract_number)

Feature table indexes:
- idx_features_project_status (project_id, status)
- idx_features_project_number (project_id, feature_number)

Scenario table indexes:
- idx_scenarios_feature_status (feature_id, status)
- idx_scenarios_scenario_number (scenario_number)
- idx_scenarios_status (status)
- idx_scenario_test_case (scenario_id, test_case_id) [on association table]

StepDefinition table indexes:
- idx_step_definitions_type (step_type)
- idx_step_definitions_pattern (pattern)
```

## Foreign Key Constraints

All parent references use `CASCADE` delete:
- ADR.project_id → projects.id (CASCADE)
- Contract.project_id → projects.id (CASCADE)
- Feature.project_id → projects.id (CASCADE)
- Scenario.feature_id → features.id (CASCADE)
- scenario_test_case_association both FKs (CASCADE)

This ensures data integrity and automatic cleanup.
