# Specification Schemas Quick Reference

## Import Statements

```python
from tracertm.schemas.specification import (
    # ADR
    ADRStatus, ADRCreate, ADRUpdate, ADRResponse, ADRListResponse, ADROption,

    # Contract
    ContractStatus, ContractType, ContractCreate, ContractUpdate,
    ContractResponse, ContractListResponse, ContractCondition, StateTransition,

    # Feature
    FeatureStatus, FeatureCreate, FeatureUpdate, FeatureResponse,
    FeatureListResponse, BDDStep, ScenarioExample,

    # Scenario
    ScenarioStatus, ScenarioCreate, ScenarioUpdate, ScenarioResponse,
    ScenarioListResponse,

    # Step Definition
    StepDefinitionType, StepDefinitionLanguage, StepDefinitionCreate,
    StepDefinitionUpdate, StepDefinitionResponse, StepDefinitionListResponse,
    StepDefinitionImplementation,

    # Other
    RequirementQualityRead,
)
```

## Quick Creation Examples

### ADR (Architecture Decision Record)

```python
# Minimal ADR
adr = ADRCreate(
    title="Switch to event-driven architecture",
    context="Current synchronous approach causes bottlenecks",
    decision="Adopt Kafka for asynchronous messaging",
    consequences="Increased operational complexity, better scalability"
)

# Full ADR with all fields
adr = ADRCreate(
    title="Switch to event-driven architecture",
    status=ADRStatus.PROPOSED,
    context="Current synchronous approach causes bottlenecks",
    decision="Adopt Kafka for asynchronous messaging",
    consequences="Increased operational complexity, better scalability",
    decision_drivers=["Performance", "Scalability", "Future growth"],
    considered_options=[
        {
            "id": "opt-1",
            "title": "RabbitMQ",
            "pros": ["Easy to set up"],
            "cons": ["Less scalable"]
        },
        {
            "id": "opt-2",
            "title": "Kafka",
            "pros": ["Highly scalable", "Good durability"],
            "cons": ["Complex operations"]
        }
    ],
    related_requirements=["REQ-001", "REQ-002"],
    related_adrs=["ADR-003"],
    supersedes="ADR-002",
    stakeholders=["Infra team", "Backend team"],
    tags=["architecture", "messaging"],
    date=date(2026, 1, 29)
)
```

### Contract (Design by Contract)

```python
# Function contract
contract = ContractCreate(
    title="validate_email",
    contract_type=ContractType.FUNCTION,
    preconditions=[
        {"id": "pre-1", "description": "email parameter must be string"}
    ],
    postconditions=[
        {"id": "post-1", "description": "returns boolean"}
    ],
    invariants=[
        {"id": "inv-1", "description": "email format matches RFC 5322"}
    ]
)

# API contract
api_contract = ContractCreate(
    title="POST /users",
    contract_type=ContractType.API,
    status=ContractStatus.ACTIVE,
    preconditions=[
        {"id": "pre-1", "description": "Valid JWT token required"},
        {"id": "pre-2", "description": "Request body must be JSON"}
    ],
    postconditions=[
        {"id": "post-1", "description": "Returns 201 with user ID"}
    ],
    states=["unauthenticated", "authenticated", "admin"],
    transitions=[
        {
            "from_state": "unauthenticated",
            "to_state": "authenticated",
            "trigger": "login",
            "action": "generate_jwt"
        }
    ],
    executable_spec="OpenAPI 3.0",
    spec_language="yaml"
)
```

### Feature (BDD Feature)

```python
# Basic feature
feature = FeatureCreate(
    name="User authentication",
    description="Users should be able to log in securely"
)

# Full feature with user story
feature = FeatureCreate(
    name="User authentication",
    description="Users should be able to log in securely",
    status=FeatureStatus.IN_DEVELOPMENT,
    as_a="user",
    i_want="to log in with my credentials",
    so_that="I can access my personal dashboard",
    file_path="features/auth.feature",
    related_requirements=["REQ-AUTH-001"],
    related_adrs=["ADR-SECURITY-001"],
    tags=["authentication", "critical"],
    metadata={"priority": "high", "owner": "auth-team"}
)
```

### Scenario (BDD Scenario)

```python
# Minimal scenario
scenario = ScenarioCreate(
    title="Successful login",
    gherkin_text="""
    Given I am on the login page
    When I enter valid credentials
    Then I should see the dashboard
    """
)

# Full scenario with structured steps
scenario = ScenarioCreate(
    title="Successful login",
    description="User logs in with valid credentials",
    gherkin_text="...",  # Gherkin text
    status=ScenarioStatus.APPROVED,
    given_steps=[
        {
            "id": "step-1",
            "text": "I am on the login page",
            "step_number": 1
        }
    ],
    when_steps=[
        {
            "id": "step-2",
            "text": "I enter username",
            "step_number": 2,
            "data_table": [["field", "value"], ["username", "john_doe"]]
        }
    ],
    then_steps=[
        {
            "id": "step-3",
            "text": "I should see the dashboard",
            "step_number": 3
        }
    ],
    is_outline=False,
    requirement_ids=["REQ-001"],
    test_case_ids=["TC-001"],
    tags=["happy-path", "smoke"],
    metadata={"automation": "selenium"}
)

# Scenario outline
scenario_outline = ScenarioCreate(
    title="Login with different users",
    is_outline=True,
    gherkin_text="...",
    examples={
        "users": [
            {"username": "admin", "role": "admin"},
            {"username": "user", "role": "user"},
            {"username": "guest", "role": "guest"}
        ]
    }
)
```

### Step Definition (Reusable Steps)

```python
# Python step definition
step = StepDefinitionCreate(
    name="click element",
    step_type=StepDefinitionType.WHEN,
    pattern=r'^I click on ["]([^"]+)["]$',
    pattern_type="regex",
    implementation=StepDefinitionImplementation(
        language=StepDefinitionLanguage.PYTHON,
        code="""
def click_element(selector):
    element = browser.find_element(By.CSS_SELECTOR, selector)
    element.click()
        """,
        imports=[
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By"
        ],
        dependencies=["selenium>=4.0"],
        timeout_seconds=10
    ),
    parameters=["selector"],
    return_type=None,
    tags=["web", "interaction"],
    examples=[
        'I click on "Submit Button"',
        'I click on ".login-button"'
    ]
)

# JavaScript step definition
js_step = StepDefinitionCreate(
    name="verify element text",
    step_type=StepDefinitionType.THEN,
    pattern=r'^I should see ["]([^"]+)["]$',
    implementation=StepDefinitionImplementation(
        language=StepDefinitionLanguage.TYPESCRIPT,
        code="""
async function verifyElementText(text: string): Promise<void> {
    const elements = await page.$$eval('*', (els) =>
        els.map(el => el.textContent).filter(t => t.includes(text))
    );
    expect(elements.length).toBeGreaterThan(0);
}
        """,
        imports=["expect from 'jest'"],
        dependencies=["jest>=29.0", "puppeteer>=10.0"]
    ),
    parameters=["text"]
)
```

## Update Examples

All Update schemas make all fields optional:

```python
# Update ADR status
adr_update = ADRUpdate(
    status=ADRStatus.ACCEPTED,
    compliance_score=0.95  # Not a real field, just example
)

# Update feature status
feature_update = FeatureUpdate(
    status=FeatureStatus.READY_FOR_RELEASE,
    tags=["authentication", "critical", "approved"]
)

# Update scenario
scenario_update = ScenarioUpdate(
    status=ScenarioStatus.AUTOMATED,
    is_outline=False,
    tags=["automated", "fast"]
)
```

## Response Examples

Responses include all fields from the database:

```python
# ADR Response
adr_response = ADRResponse(
    id="adr-uuid",
    project_id="proj-uuid",
    adr_number="ADR-001",
    title="Switch to event-driven architecture",
    status="accepted",
    date=date(2026, 1, 29),
    context="...",
    decision="...",
    consequences="...",
    decision_drivers=["Performance", "Scalability"],
    considered_options=[...],
    related_requirements=["REQ-001"],
    related_adrs=["ADR-003"],
    supersedes="ADR-002",
    superseded_by=None,
    compliance_score=0.95,
    stakeholders=["Infra team"],
    tags=["architecture"],
    metadata={},
    version=2,
    last_verified_at=datetime(2026, 1, 29, 10, 0),
    created_at=datetime(2026, 1, 28, 15, 0),
    updated_at=datetime(2026, 1, 29, 10, 0),
    deleted_at=None
)

# Feature Response
feature_response = FeatureResponse(
    id="feat-uuid",
    project_id="proj-uuid",
    feature_number="FEAT-001",
    name="User authentication",
    description="...",
    status="in_development",
    as_a="user",
    i_want="to log in",
    so_that="I can access dashboard",
    file_path="features/auth.feature",
    related_requirements=["REQ-001"],
    related_adrs=["ADR-001"],
    tags=["authentication"],
    metadata={},
    version=1,
    created_at=datetime(2026, 1, 28, 15, 0),
    updated_at=datetime(2026, 1, 28, 15, 0),
    deleted_at=None
)
```

## List Response Examples

All list responses wrap items with total count:

```python
# ADR List
adr_list = ADRListResponse(
    total=5,
    adrs=[
        ADRResponse(...),
        ADRResponse(...),
        ADRResponse(...)
    ]
)

# Feature List
feature_list = FeatureListResponse(
    total=3,
    features=[
        FeatureResponse(...),
        FeatureResponse(...),
        FeatureResponse(...)
    ]
)

# Scenario List
scenario_list = ScenarioListResponse(
    total=12,
    scenarios=[...]
)

# Step Definition List
step_list = StepDefinitionListResponse(
    total=25,
    step_definitions=[...]
)
```

## Validation Rules Summary

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| title | string | min_length=1, max_length=500 | "Use async/await" |
| name | string | min_length=1, max_length=500 | "User authentication" |
| pattern | string | min_length=1 | "^I click on" |
| status | Enum | See specific enums | ADRStatus.PROPOSED |
| step_type | Enum | given\|when\|then\|and\|but | StepDefinitionType.WHEN |
| pattern_type | string | regex\|literal\|glob | "regex" |
| language | Enum | python\|javascript\|etc | StepDefinitionLanguage.PYTHON |
| ambiguity_score | float | 0.0 <= x <= 1.0 | 0.45 |
| completeness_score | float | 0.0 <= x <= 1.0 | 0.78 |
| timeout_seconds | int | >= 0 | 10 |
| step_number | int | >= 1 | 1 |

## Field Availability by Schema Type

### Create Schemas
- Accept only input fields
- Metadata and tags default to empty
- Status fields have sensible defaults
- No ID, number, timestamps, or version

### Update Schemas
- All fields optional
- Can update any aspect
- Omitted fields remain unchanged

### Response Schemas
- Include all fields from database
- Include computed fields (numbers, timestamps)
- Ready for JSON serialization
- `from_attributes=True` enables ORM conversion

### List Response Schemas
- Include total count
- Array of Response objects
- Use for pagination

## Common Patterns

### Creating with defaults
```python
# All these use sensible defaults
adr = ADRCreate(title="...", context="...", decision="...", consequences="...")
feature = FeatureCreate(name="...", description="...")
scenario = ScenarioCreate(title="...", gherkin_text="...")
```

### Partial updates
```python
# Only change what's needed
update = ContractUpdate(
    status=ContractStatus.APPROVED,
    tags=["verified"]
)
```

### Nested objects
```python
step_def = StepDefinitionCreate(
    name="...",
    implementation=StepDefinitionImplementation(
        language=StepDefinitionLanguage.PYTHON,
        code="..."
    )
)
```

### Flexible metadata
```python
adr = ADRCreate(
    # ... required fields ...
    metadata={
        "custom_field": "custom_value",
        "priority": "high",
        "deadline": "2026-02-01"
    }
)
```

## Type Inference

Thanks to Pydantic's type system, you get full IDE support:

```python
# IDE knows adr.status is ADRStatus (not string)
adr = ADRCreate(...)
adr_response = ADRResponse.model_validate(adr)
# response.status autocompletes to ADRStatus options

# IDE knows feature.name is str
feature = FeatureCreate(...)
print(f"Feature: {feature.name}")  # Full string methods available

# IDE knows scenario.given_steps is list[dict[str, Any]]
scenario = ScenarioCreate(...)
for step in scenario.given_steps:
    # Full dict methods available
```

## Error Handling

```python
from pydantic import ValidationError

try:
    # Missing required fields
    adr = ADRCreate(title="...")  # Missing context, decision, consequences
except ValidationError as e:
    print(e.errors())
    # [{
    #   'type': 'missing',
    #   'loc': ('context',),
    #   'msg': 'Field required'
    # }]

try:
    # Invalid enum value
    feature = FeatureCreate(
        name="...",
        status="invalid_status"  # Not a FeatureStatus
    )
except ValidationError as e:
    print(e.errors())
```

## Performance Notes

- Schemas are lightweight (pure data validation)
- No database queries during validation
- Serialization is fast (built-in pydantic optimization)
- List responses include total for pagination calculation
- Metadata dict provides flexibility without schema changes

## File Location

**Path:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/schemas/specification.py`

**Line Count:** ~716 lines

**All imports validated:** ✓
