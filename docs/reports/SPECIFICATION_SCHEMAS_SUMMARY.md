# Specification Schemas Implementation Summary

## Overview

Created comprehensive Pydantic schemas for the specification system at `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/schemas/specification.py`.

## What Was Implemented

### 1. ADR (Architecture Decision Record) Schemas

**Enums:**
- `ADRStatus`: proposed, accepted, deprecated, superseded, rejected

**Schemas:**
- `ADRCreate`: Create new ADR with MADR 4.0 format
  - title, status (default: proposed)
  - MADR fields: context, decision, consequences
  - Decision drivers, considered options
  - Traceability: related_requirements, related_adrs, supersedes
  - Metadata: stakeholders, tags, date, metadata dict

- `ADRUpdate`: Update any ADR field (all optional)

- `ADRResponse`: Full ADR response with computed fields
  - All creation fields
  - compliance_score, superseded_by
  - Timestamps: last_verified_at, created_at, updated_at, deleted_at
  - version, adr_number

- `ADRListResponse`: List wrapper with total count

### 2. Contract Schemas

**Enums:**
- `ContractStatus`: draft, review, approved, active, superseded, archived
- `ContractType`: api, function, class, module, workflow, service, other

**Supporting Models:**
- `ContractCondition`: Pre/post conditions with id, description, condition_code, priority
- `StateTransition`: State machine transitions with from_state, to_state, trigger, condition, action

**Schemas:**
- `ContractCreate`: Create formal specification contracts
  - title, contract_type, status (default: draft)
  - Contract definition: preconditions, postconditions, invariants
  - State machine: states, transitions
  - Executable spec: executable_spec, spec_language
  - Metadata: tags, metadata dict

- `ContractUpdate`: Update any contract field (all optional)

- `ContractResponse`: Full contract response
  - All creation fields
  - last_verified_at, verification_result
  - Timestamps and version tracking

- `ContractListResponse`: List wrapper with total count

### 3. Feature Schemas

**Enums:**
- `FeatureStatus`: draft, in_development, ready_for_test, in_test, ready_for_release, released, deprecated

**Supporting Models:**
- `BDDStep`: Individual BDD step with keyword (Given/When/Then/And/But), text, docstring, data_table
- `ScenarioExample`: Examples for scenario outlines with parameters

**Schemas:**
- `FeatureCreate`: Create BDD features
  - name, description, status (default: draft)
  - User story format: as_a, i_want, so_that
  - file_path for tracking source files
  - Traceability: related_requirements, related_adrs
  - Metadata: tags, metadata dict

- `FeatureUpdate`: Update any feature field (all optional)

- `FeatureResponse`: Full feature response
  - All creation fields
  - feature_number, project_id
  - Timestamps and version tracking

- `FeatureListResponse`: List wrapper with total count

### 4. Scenario Schemas

**Enums:**
- `ScenarioStatus`: draft, review, approved, automated, deprecated

**Schemas:**
- `ScenarioCreate`: Create BDD scenarios
  - title, description, gherkin_text
  - status (default: draft)
  - Steps: background, given_steps, when_steps, then_steps
  - Outline support: is_outline flag, examples dict
  - Traceability: requirement_ids, test_case_ids
  - Metadata: tags, metadata dict

- `ScenarioUpdate`: Update any scenario field (all optional)

- `ScenarioResponse`: Full scenario response
  - All creation fields
  - scenario_number, feature_id
  - pass_rate tracking
  - Timestamps and version tracking

- `ScenarioListResponse`: List wrapper with total count

### 5. Step Definition Schemas

**Enums:**
- `StepDefinitionType`: given, when, then, and, but
- `StepDefinitionLanguage`: python, javascript, typescript, java, csharp, gherkin, sql, other

**Supporting Models:**
- `StepDefinitionImplementation`: Code implementation with:
  - language (required)
  - code (required, min 1 char)
  - imports list
  - dependencies list
  - timeout_seconds

**Schemas:**
- `StepDefinitionCreate`: Create reusable step definitions
  - name, description, step_type (required)
  - Pattern matching: pattern, pattern_type (regex|literal|glob, default: regex)
  - Implementation details: StepDefinitionImplementation (optional)
  - Parameters list, return_type
  - Traceability: related_step_definitions, test_case_ids
  - Metadata: tags, examples, metadata dict

- `StepDefinitionUpdate`: Update any step definition field (all optional)

- `StepDefinitionResponse`: Full step definition response
  - All creation fields
  - step_definition_number, project_id
  - Usage tracking: usage_count, last_used_at
  - Timestamps and version tracking

- `StepDefinitionListResponse`: List wrapper with total count

### 6. Requirement Quality Schemas

**Schemas:**
- `RequirementQualityRead`: Analysis results
  - id, item_id
  - smells list (detected requirement issues)
  - ambiguity_score (0.0-1.0)
  - completeness_score (0.0-1.0)
  - suggestions list
  - last_analyzed_at, created_at, updated_at timestamps

## Key Design Patterns

### 1. Pydantic Configuration
All schemas use modern Pydantic v2 patterns:
```python
model_config = ConfigDict(from_attributes=True, protected_namespaces=())
```

- `from_attributes=True`: Enables ORM model conversion
- `protected_namespaces=()`: Allows custom field names without warnings

### 2. Field Validation
- Required fields: `Field(...)` with constraints
  - `min_length`, `max_length` for strings
  - `ge`, `le` for numeric ranges
  - `pattern` regex validation
- Optional fields: `field: Type | None = None`
- List defaults: `Field(default_factory=list)`
- Dict defaults: `Field(default_factory=dict)`

### 3. Schema Naming Convention
Each domain has 4 core schemas:
- `{Domain}Create`: Input schema for creation (required fields only)
- `{Domain}Update`: Input schema for updates (all optional)
- `{Domain}Response`: Output schema (includes IDs, timestamps, computed fields)
- `{Domain}ListResponse`: Pagination wrapper with `total` count

### 4. Enums
All enums inherit from `str` for string serialization and are used as defaults:
```python
status: ADRStatus = ADRStatus.PROPOSED
```

### 5. Metadata & Extensibility
All creation schemas include:
```python
metadata: dict[str, Any] = Field(default_factory=dict)
```

This provides flexibility for future extensions without schema changes.

## Validation Examples

### ADR Creation
```python
adr = ADRCreate(
    title="Use async/await for IO operations",
    status=ADRStatus.PROPOSED,
    context="Performance issues with blocking calls",
    decision="Implement async patterns throughout",
    consequences="Requires Python 3.7+, changes callback chains",
    decision_drivers=["Performance", "Maintainability"],
    stakeholders=["Backend Team", "Infra Team"]
)
```

### Contract Creation
```python
contract = ContractCreate(
    title="User Authentication API",
    contract_type=ContractType.API,
    preconditions=[
        {"description": "Valid credentials required"}
    ],
    postconditions=[
        {"description": "JWT token returned"}
    ],
    states=["unauthenticated", "authenticated"],
    transitions=[
        {"from_state": "unauthenticated", "to_state": "authenticated"}
    ]
)
```

### Feature Creation
```python
feature = FeatureCreate(
    name="User Dashboard",
    as_a="regular user",
    i_want="to see my profile information",
    so_that="I can manage my account settings",
    related_requirements=["REQ-001"],
    related_adrs=["ADR-001"]
)
```

### Scenario Creation
```python
scenario = ScenarioCreate(
    title="Successful login",
    gherkin_text="Given I am on the login page...",
    given_steps=[{"text": "I am on the login page"}],
    when_steps=[{"text": "I enter valid credentials"}],
    then_steps=[{"text": "I should see the dashboard"}]
)
```

### Step Definition Creation
```python
step_def = StepDefinitionCreate(
    name="I click on element",
    step_type=StepDefinitionType.WHEN,
    pattern=r'^I click on ["](.+)["]$',
    pattern_type="regex",
    implementation=StepDefinitionImplementation(
        language=StepDefinitionLanguage.PYTHON,
        code="browser.find_element(By.CSS_SELECTOR, selector).click()",
        imports=["from selenium import webdriver"],
        timeout_seconds=5
    ),
    parameters=["selector"]
)
```

## Type Safety Features

1. **Strict Enum Validation**: Status/type fields only accept valid enum values
2. **Numeric Constraints**: Scores bounded to 0.0-1.0, positive integers for counts
3. **String Constraints**: Length limits on titles (500 chars), descriptions
4. **Pattern Validation**: Regex patterns for pattern_type and priority levels
5. **Keyword Validation**: BDD steps must use valid keywords (Given/When/Then/And/But)

## Integration Points

### With ORM Models
Response schemas use `from_attributes=True` to directly convert SQLAlchemy models:
```python
adr_response = ADRResponse.model_validate(adr_model_instance)
```

### With API Routers
Create/Update schemas act as input validators in tRPC routers:
```python
def create_adr(input: ADRCreate) -> ADRResponse:
    # input is validated and type-safe
```

### With Databases
Response schemas include all database fields for seamless conversion:
- IDs (id, project_id, feature_id, etc.)
- Numbers (adr_number, contract_number, etc.)
- Timestamps (created_at, updated_at, deleted_at)
- Version tracking (version field)

## File Location

**Path:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/schemas/specification.py`

**Size:** ~716 lines

**Syntax:** Validated ✓

**Import:** All schemas importable and properly configured ✓

## Next Steps

1. **Create StepDefinition Model** (if not exists):
   ```sql
   CREATE TABLE step_definitions (
       id VARCHAR(36) PRIMARY KEY,
       project_id VARCHAR(255) NOT NULL,
       step_definition_number VARCHAR(50) NOT NULL,
       name VARCHAR(255) NOT NULL,
       description TEXT,
       step_type VARCHAR(50) NOT NULL,
       pattern TEXT NOT NULL,
       pattern_type VARCHAR(50) DEFAULT 'regex',
       implementation JSONB,
       parameters JSONB DEFAULT '[]',
       return_type VARCHAR(100),
       related_step_definitions JSONB DEFAULT '[]',
       test_case_ids JSONB DEFAULT '[]',
       tags JSONB DEFAULT '[]',
       examples JSONB DEFAULT '[]',
       metadata JSONB,
       usage_count INT DEFAULT 0,
       last_used_at TIMESTAMP,
       version INT DEFAULT 1,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL,
       deleted_at TIMESTAMP,
       FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
   );
   ```

2. **Create tRPC Routers** using these schemas:
   - `adr.router.ts` with CRUD endpoints
   - `contract.router.ts` with CRUD endpoints
   - `feature.router.ts` with CRUD endpoints + scenario management
   - `scenario.router.ts` with CRUD endpoints
   - `step-definition.router.ts` with CRUD endpoints

3. **Create Repositories** following hexagonal architecture:
   - `ADRRepository` with query methods
   - `ContractRepository` with verification methods
   - `FeatureRepository` with scenario relationships
   - `ScenarioRepository` with status transitions
   - `StepDefinitionRepository` with pattern matching

4. **Add Validation Tests** using Vitest:
   - Test enum constraints
   - Test field length validation
   - Test required field enforcement
   - Test optional field handling
   - Test metadata flexibility

## Benefits

✓ **Type Safety**: Full TypeScript/Pydantic type inference
✓ **Validation**: Comprehensive field constraints and patterns
✓ **Consistency**: Uniform Create/Update/Response patterns
✓ **Extensibility**: Metadata fields for future expansion
✓ **Documentation**: Comprehensive docstrings for all schemas
✓ **Traceability**: Built-in relationship tracking between specifications
✓ **Versioning**: Automatic version tracking for all entities
✓ **Timestamps**: Soft deletes with created_at/updated_at/deleted_at
