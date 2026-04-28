# Specification Repositories - Quick Reference

## Import

```python
from tracertm.repositories.specification_repository import (
    ADRRepository,
    ContractRepository,
    FeatureRepository,
    ScenarioRepository,
)
```

## Initialize

```python
adr_repo = ADRRepository(db_session)
contract_repo = ContractRepository(db_session)
feature_repo = FeatureRepository(db_session)
scenario_repo = ScenarioRepository(db_session)
```

## ADR Operations

### Create
```python
adr = await adr_repo.create(
    project_id="proj-123",
    title="Use PostgreSQL",
    context="...",
    decision="...",
    consequences="...",
    status="proposed",
    decision_drivers=["performance"],
    compliance_score=0.9
)
await db_session.commit()
```

### Read
```python
adr = await adr_repo.get_by_id("adr-123", project_id="proj-123")
adr = await adr_repo.get_by_number("ADR-20250120-ABCD1234", project_id="proj-123")
```

### List
```python
adrs = await adr_repo.list_by_project(project_id="proj-123", status="proposed")
adrs = await adr_repo.find_by_status(project_id="proj-123", status="accepted")
related = await adr_repo.find_related(adr_id="adr-123")
```

### Update
```python
adr = await adr_repo.update(adr_id="adr-123", expected_version=1, title="New Title")
```

### Status Transition
```python
adr = await adr_repo.transition_status(adr_id="adr-123", to_status="accepted")
```

### Verify
```python
adr = await adr_repo.verify_compliance(adr_id="adr-123", compliance_score=0.95)
```

### Delete
```python
deleted = await adr_repo.delete(adr_id="adr-123")
```

### Analytics
```python
counts = await adr_repo.count_by_status(project_id="proj-123")
```

---

## Contract Operations

### Create
```python
contract = await contract_repo.create(
    project_id="proj-123",
    item_id="item-456",
    title="Payment API",
    contract_type="api",
    status="draft",
    preconditions=[{"name": "auth", "type": "bool"}],
    postconditions=[{"name": "logged", "type": "bool"}]
)
await db_session.commit()
```

### Read
```python
contract = await contract_repo.get_by_id("contract-123", project_id="proj-123")
contract = await contract_repo.get_by_number("CTR-20250120-ABCD1234")
```

### List
```python
contracts = await contract_repo.list_by_project(
    project_id="proj-123",
    contract_type="api",
    status="approved"
)
contracts = await contract_repo.list_by_item(item_id="item-456")
```

### Update
```python
contract = await contract_repo.update(
    contract_id="contract-123",
    expected_version=1,
    executable_spec="new spec"
)
```

### Verify
```python
contract = await contract_repo.verify(
    contract_id="contract-123",
    verification_result={"passed": True, "checks": ["ok"]}
)
```

### Status Transition
```python
contract = await contract_repo.transition_status(
    contract_id="contract-123",
    to_status="approved"
)
```

### Delete
```python
deleted = await contract_repo.delete(contract_id="contract-123")
```

### Analytics
```python
counts = await contract_repo.count_by_type(project_id="proj-123")
```

---

## Feature Operations

### Create
```python
feature = await feature_repo.create(
    project_id="proj-123",
    name="User Authentication",
    as_a="user",
    i_want="to log in",
    so_that="I can access my account",
    status="draft"
)
await db_session.commit()
```

### Read
```python
feature = await feature_repo.get_by_id("feature-123", project_id="proj-123")
feature = await feature_repo.get_by_number("FEAT-20250120-ABCD1234")
```

### List
```python
features = await feature_repo.list_by_project(
    project_id="proj-123",
    status="draft"
)
```

### With Scenarios
```python
features_with_scenarios = await feature_repo.list_with_scenarios(
    project_id="proj-123"
)
# Returns: [(Feature, [Scenario, ...]), ...]
```

### Update
```python
feature = await feature_repo.update(
    feature_id="feature-123",
    expected_version=1,
    name="Updated Name"
)
```

### Status Transition
```python
feature = await feature_repo.transition_status(
    feature_id="feature-123",
    to_status="approved"
)
```

### Delete (cascades scenarios)
```python
deleted = await feature_repo.delete(feature_id="feature-123")
```

---

## Scenario Operations

### Create
```python
scenario = await scenario_repo.create(
    feature_id="feature-123",
    title="User logs in",
    gherkin_text="Given... When... Then...",
    given_steps=[{"step": "user on login", "parameter": None}],
    when_steps=[{"step": "enters credentials", "parameter": "email"}],
    then_steps=[{"step": "logged in", "parameter": None}],
    status="draft"
)
await db_session.commit()
```

### Create Outline
```python
scenario = await scenario_repo.create(
    feature_id="feature-123",
    title="Login various users",
    gherkin_text="...",
    is_outline=True,
    examples={
        "header": ["user", "pass", "result"],
        "rows": [["u1", "p1", "ok"], ["u2", "p2", "ok"]]
    }
)
```

### Read
```python
scenario = await scenario_repo.get_by_id("scenario-123")
scenario = await scenario_repo.get_by_number("SC-20250120-ABCD1234")
```

### List
```python
scenarios = await scenario_repo.list_by_feature(
    feature_id="feature-123",
    status="draft"
)
scenarios = await scenario_repo.find_by_status(
    feature_id="feature-123",
    status="ready"
)
```

### Update
```python
scenario = await scenario_repo.update(
    scenario_id="scenario-123",
    expected_version=1,
    title="Updated Title"
)
```

### Update Pass Rate
```python
scenario = await scenario_repo.update_pass_rate(
    scenario_id="scenario-123",
    pass_rate=0.95
)
```

### Status Transition
```python
scenario = await scenario_repo.transition_status(
    scenario_id="scenario-123",
    to_status="ready"
)
```

### Delete
```python
deleted = await scenario_repo.delete(scenario_id="scenario-123")
```

### Analytics
```python
counts = await scenario_repo.count_by_status(feature_id="feature-123")
avg = await scenario_repo.get_average_pass_rate(feature_id="feature-123")
```

---

## Common Patterns

### Commit After Writes
```python
result = await repo.create(...)
await db_session.commit()  # Always commit
```

### Version-Safe Updates
```python
entity = await repo.get_by_id(id)
updated = await repo.update(id, expected_version=entity.version, **updates)
```

### Handle Concurrency
```python
try:
    updated = await repo.update(id, expected_version=1, **updates)
except ConcurrencyError:
    # Fetch fresh and retry
    pass
```

### Handle Invalid Transitions
```python
try:
    updated = await repo.transition_status(id, new_status)
except ValueError:
    # Log and skip
    pass
```

### Pagination
```python
page1 = await repo.list_by_project(project_id, limit=50, offset=0)
page2 = await repo.list_by_project(project_id, limit=50, offset=50)
```

---

## Status Values

### ADR
- `proposed` (start)
- `accepted`
- `rejected`
- `deprecated` (end)

### Contract
- `draft` (start)
- `review`
- `approved`
- `deprecated`
- `archived` (end)

### Feature
- `draft` (start)
- `review`
- `approved`
- `implemented`
- `deprecated` (end)

### Scenario
- `draft` (start)
- `review`
- `ready`
- `executing`
- `passed` / `failed`
- `deprecated` (end)

---

## Number Formats

- **ADR**: `ADR-YYYYMMDD-XXXXXXXX` (e.g., `ADR-20250120-A1B2C3D4`)
- **Contract**: `CTR-YYYYMMDD-XXXXXXXX` (e.g., `CTR-20250120-A1B2C3D4`)
- **Feature**: `FEAT-YYYYMMDD-XXXXXXXX` (e.g., `FEAT-20250120-A1B2C3D4`)
- **Scenario**: `SC-YYYYMMDD-XXXXXXXX` (e.g., `SC-20250120-A1B2C3D4`)

---

## Testing

```bash
# Run all specification repository tests
bun run test:api tests/integration/test_specification_repositories.py

# Specific test
bun run test:api tests/integration/test_specification_repositories.py -k test_adr_create_basic

# With coverage
bun run test:api tests/integration/test_specification_repositories.py --cov
```

---

## Error Handling

```python
from tracertm.core.concurrency import ConcurrencyError

# Version conflict
try:
    await repo.update(id, expected_version=1, **updates)
except ConcurrencyError as e:
    print(f"Concurrent modification: {e}")

# Invalid transition
try:
    await repo.transition_status(id, invalid_status)
except ValueError as e:
    print(f"Invalid transition: {e}")

# Not found
try:
    await repo.update(id, expected_version=1, **updates)
except ValueError as e:
    print(f"Not found: {e}")
```

---

## Full Example: Feature with Scenarios

```python
# Create feature
feature = await feature_repo.create(
    project_id="proj-123",
    name="Payment Processing",
    as_a="customer",
    i_want="to pay with card",
    so_that="I can complete purchase",
    status="draft"
)
await db_session.commit()

# Create scenarios
scenario1 = await scenario_repo.create(
    feature_id=feature.id,
    title="Successful payment",
    gherkin_text="Given user on checkout\nWhen user enters card\nThen payment processed",
    given_steps=[{"step": "user on checkout page"}],
    when_steps=[{"step": "user enters card details", "parameter": "visa"}],
    then_steps=[{"step": "payment processed successfully"}],
    tags=["happy-path", "critical"],
    status="draft"
)
await db_session.commit()

# Review feature
feature = await feature_repo.transition_status(feature.id, "review")
scenario1 = await scenario_repo.transition_status(scenario1.id, "review")
await db_session.commit()

# Approve feature
feature = await feature_repo.transition_status(feature.id, "approved")
scenario1 = await scenario_repo.transition_status(scenario1.id, "ready")
await db_session.commit()

# Execute scenario
scenario1 = await scenario_repo.transition_status(scenario1.id, "executing")
scenario1 = await scenario_repo.update_pass_rate(scenario1.id, 1.0)
scenario1 = await scenario_repo.transition_status(scenario1.id, "passed")
await db_session.commit()

# Get feature with scenarios
features_with_scenarios = await feature_repo.list_with_scenarios(project_id="proj-123")
for feat, scenarios in features_with_scenarios:
    print(f"Feature: {feat.name}")
    for sc in scenarios:
        print(f"  - {sc.title} ({sc.status}) - {sc.pass_rate}%")
```
