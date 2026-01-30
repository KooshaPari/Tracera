# Specification Schemas Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPECIFICATION ENGINE SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     ADRs     │  │  Contracts   │  │  Features    │  │  Scenarios   │ │
│  │ Architecture │  │   (Design by │  │   (BDD User  │  │ (BDD Gherkin)│ │
│  │  Decisions   │  │   Contract)  │  │   Stories)   │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │                  │        │
│         └──────────────────┼──────────────────┼──────────────────┘        │
│                            │                  │                           │
│                   ┌────────┴──────────┐       │                           │
│                   │ Step Definitions  │       │                           │
│                   │ (Reusable Steps)  │───────┘                           │
│                   └───────────────────┘                                   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │          Requirement Quality Analysis                             │   │
│  │  (Ambiguity, Completeness, Smells)                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Domain-Specific Models

### 1. ADR (Architecture Decision Record)

```
ADRCreate
├── title (string, 1-500)
├── status (ADRStatus: proposed, accepted, deprecated, superseded, rejected)
├── context (string)
├── decision (string)
├── consequences (string)
├── decision_drivers (list[string])
├── considered_options (list[dict])
│   ├── id
│   ├── title
│   ├── description
│   ├── pros
│   ├── cons
│   └── is_chosen
├── related_requirements (list[string])
├── related_adrs (list[string])
├── supersedes (string)
├── stakeholders (list[string])
├── tags (list[string])
├── date (date)
└── metadata (dict)

    ↓ (ORM Mapping)

ADRResponse
├── ADRCreate fields
├── id (string)
├── project_id (string)
├── adr_number (string)
├── superseded_by (string | null)
├── compliance_score (float)
├── last_verified_at (datetime | null)
├── version (int)
├── created_at (datetime)
├── updated_at (datetime)
└── deleted_at (datetime | null)

    ↓ (Pagination)

ADRListResponse
├── total (int)
└── adrs (list[ADRResponse])
```

### 2. Contract (Design by Contract)

```
ContractCreate
├── title (string, 1-500)
├── contract_type (ContractType: api, function, class, module, workflow, service, other)
├── status (ContractStatus: draft, review, approved, active, superseded, archived)
├── preconditions (list[dict])
│   ├── id
│   ├── description
│   ├── condition_code (optional)
│   ├── required
│   └── priority (critical|high|medium|low)
├── postconditions (list[dict])
├── invariants (list[dict])
├── states (list[string])
├── transitions (list[dict])
│   ├── id
│   ├── from_state
│   ├── to_state
│   ├── trigger
│   ├── condition
│   └── action
├── executable_spec (string)
├── spec_language (string)
├── tags (list[string])
└── metadata (dict)

    ↓ (ORM Mapping)

ContractResponse
├── ContractCreate fields
├── id (string)
├── project_id (string)
├── item_id (string)
├── contract_number (string)
├── last_verified_at (datetime | null)
├── verification_result (dict | null)
├── version (int)
├── created_at (datetime)
├── updated_at (datetime)
└── deleted_at (datetime | null)

    ↓ (Pagination)

ContractListResponse
├── total (int)
└── contracts (list[ContractResponse])
```

### 3. Feature (BDD Feature)

```
FeatureCreate
├── name (string, 1-500)
├── description (string | null)
├── status (FeatureStatus: draft, in_development, ready_for_test,
│                         in_test, ready_for_release, released, deprecated)
├── as_a (string) ─────┐
├── i_want (string)    ├─── User Story Format
├── so_that (string)───┘
├── file_path (string)
├── related_requirements (list[string])
├── related_adrs (list[string])
├── tags (list[string])
└── metadata (dict)

    ↓ (ORM Mapping)

FeatureResponse
├── FeatureCreate fields
├── id (string)
├── project_id (string)
├── feature_number (string)
├── version (int)
├── created_at (datetime)
├── updated_at (datetime)
└── deleted_at (datetime | null)

    ↓ (Contains Many)

Scenario (relates to Feature.scenarios)
│   ├── id
│   ├── feature_id
│   ├── scenario_number
│   └── ... (see Scenario section)
│
    ↓ (Pagination)

FeatureListResponse
├── total (int)
└── features (list[FeatureResponse])
```

### 4. Scenario (BDD Scenario)

```
ScenarioCreate
├── title (string, 1-500)
├── description (string | null)
├── gherkin_text (string)
├── status (ScenarioStatus: draft, review, approved, automated, deprecated)
├── background (list[dict]) ───┐
├── given_steps (list[dict])   │
├── when_steps (list[dict])    ├─── BDD Steps
├── then_steps (list[dict])    │   Each with:
│   ├── id                     │   ├── id
│   ├── step_number            │   ├── step_number
│   ├── keyword (Given|When...) │  ├── keyword
│   ├── text                   │   ├── text
│   ├── docstring              │   ├── docstring
│   └── data_table             │   └── data_table
├── is_outline (bool)          ┘
├── examples (dict) ────────────── Outline Examples
│   ├── name
│   ├── description
│   └── parameters
├── requirement_ids (list[string])
├── test_case_ids (list[string])
├── tags (list[string])
└── metadata (dict)

    ↓ (ORM Mapping)

ScenarioResponse
├── ScenarioCreate fields
├── id (string)
├── feature_id (string)
├── scenario_number (string)
├── pass_rate (float)
├── version (int)
├── created_at (datetime)
├── updated_at (datetime)
└── deleted_at (datetime | null)

    ↓ (Pagination)

ScenarioListResponse
├── total (int)
└── scenarios (list[ScenarioResponse])
```

### 5. Step Definition (Reusable Steps)

```
StepDefinitionCreate
├── name (string, 1-500)
├── description (string | null)
├── step_type (StepDefinitionType: given, when, then, and, but)
├── pattern (string) ───────────── Matching pattern
├── pattern_type (regex|literal|glob, default: regex)
├── implementation (StepDefinitionImplementation) ──┐
│   ├── language (StepDefinitionLanguage)          │
│   │   ├── python                                  │
│   │   ├── javascript                              ├─ Code
│   │   ├── typescript                              │  Implementation
│   │   ├── java                                    │
│   │   ├── csharp                                  │
│   │   ├── gherkin                                 │
│   │   ├── sql                                     │
│   │   └── other                                   │
│   ├── code (string)                               │
│   ├── imports (list[string])                      │
│   ├── dependencies (list[string])                 │
│   └── timeout_seconds (int)                       ┘
├── parameters (list[string])
├── return_type (string)
├── related_step_definitions (list[string])
├── test_case_ids (list[string])
├── tags (list[string])
├── examples (list[string])
└── metadata (dict)

    ↓ (ORM Mapping)

StepDefinitionResponse
├── StepDefinitionCreate fields
├── id (string)
├── project_id (string)
├── step_definition_number (string)
├── usage_count (int)
├── last_used_at (datetime | null)
├── version (int)
├── created_at (datetime)
├── updated_at (datetime)
└── deleted_at (datetime | null)

    ↓ (Pagination)

StepDefinitionListResponse
├── total (int)
└── step_definitions (list[StepDefinitionResponse])
```

## Schema Lifecycle

```
┌──────────────┐
│   Create     │  Input Validation
│   Schema     │  - Required fields only
│              │  - Type validation
│              │  - Length constraints
└────────┬─────┘
         │
         ↓
┌──────────────┐
│   Database   │  ORM Persistence
│   Model      │  - Generate ID, number
│              │  - Set timestamps
│              │  - Initialize version
└────────┬─────┘
         │
         ↓
┌──────────────┐
│  Response    │  Output Serialization
│  Schema      │  - Include all fields
│              │  - from_attributes=True
│              │  - Ready for JSON
└────────┬─────┘
         │
         ↓
┌──────────────┐
│   Update     │  Partial Modifications
│   Schema     │  - All fields optional
│              │  - Only touched fields change
└────────┬─────┘
         │
         ↓
┌──────────────┐
│   Response   │  Updated Response
│   Schema     │  - Incremented version
│              │  - Updated timestamps
└──────────────┘
```

## Relationships Map

```
ADR
├── relates to: Contracts (via related_adrs)
├── relates to: Features (via related_adrs)
└── relates to: Requirements (via related_requirements)

Contract
├── belongs to: Item (item_id)
├── relates to: Features (via related concepts)
└── uses: State Transitions (for state machines)

Feature
├── belongs to: Project (project_id)
├── contains: Scenarios (one-to-many)
├── relates to: Requirements (via related_requirements)
├── relates to: ADRs (via related_adrs)
└── composed of: BDD Steps (in scenarios)

Scenario
├── belongs to: Feature (feature_id)
├── composed of: Given/When/Then steps
├── may use: Step Definitions (pattern matching)
├── relates to: Test Cases (via test_case_ids)
└── relates to: Requirements (via requirement_ids)

Step Definition
├── belongs to: Project (project_id)
├── used by: Scenarios (pattern matching)
├── relates to: Test Cases (via test_case_ids)
├── relates to: Other Step Definitions (composition)
└── has: Implementation (language-specific code)
```

## Data Flow Patterns

### ADR Creation Flow
```
User Input (JSON)
    ↓
ADRCreate Validation
    ↓ Valid
ADR Model (ORM)
    ↓ Insert/Update
Database
    ↓ Read
ADRResponse (JSON)
    ↓
Client
```

### Feature with Scenarios Flow
```
User Creates Feature
    ↓
FeatureCreate Validation
    ↓
Feature Model
    ↓
Feature Response
    ↓
User Creates Scenarios
    ↓
ScenarioCreate Validation
    ↓
Scenario Model (with feature_id)
    ↓
Scenario Response
    ↓
User Requests Feature Detail
    ↓
FeatureResponse (includes scenarios)
```

### Step Definition Usage Flow
```
User Defines Steps
    ↓
StepDefinitionCreate Validation
    ↓
Step Definition Model
    ↓
User Writes Scenarios
    ↓
ScenarioCreate (with step text)
    ↓
Pattern Matching Engine
    ↓ Finds matching step definitions
Execute with Implementation Code
    ↓
Record Usage
    ↓
Update last_used_at, usage_count
```

## Configuration Schema

```python
# All schemas configured with:
model_config = ConfigDict(
    from_attributes=True,      # ORM compatibility
    protected_namespaces=()    # Custom field names allowed
)

# Enums use:
class StatusEnum(str, Enum):   # String-based, JSON serializable
    VALUE = "value"
```

## Validation Layer

```
Input Validation (Create/Update)
├── Type checking (Pydantic validators)
├── Length constraints (min_length, max_length)
├── Enum validation (status, type, language)
├── Pattern validation (regex patterns)
├── Numeric bounds (ge, le)
└── Required field enforcement (Field(...))

ORM Mapping (Response)
├── Attribute extraction (from_attributes=True)
├── Type conversion
├── Timestamp handling
├── Relationship loading
└── JSON serialization
```

## Extension Points

### Metadata Field
Every Create schema includes:
```python
metadata: dict[str, Any] = Field(default_factory=dict)
```

Use for:
- Custom fields
- Domain-specific data
- Feature flags
- Integration data
- Future extensions

### Tag System
Every schema supports tags:
```python
tags: list[str] = Field(default_factory=list)
```

Use for:
- Categorization
- Filtering
- Workflows
- Cross-cutting concerns
- Business rules

### Relationships
Every schema supports relationship IDs:
```python
related_requirements: list[str]
related_adrs: list[str]
test_case_ids: list[str]
```

Use for:
- Traceability matrix
- Impact analysis
- Graph queries
- Coverage reports

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Validation | O(1) | All constraints are O(1) |
| Serialization | O(n) | Linear in field count |
| Deserialization | O(n) | Linear in field count |
| Enum lookup | O(1) | Direct hash lookup |
| List operations | O(n) | Standard list operations |

## Security Considerations

- No sensitive data in IDs (UUID v4 used in models)
- No default secrets in schemas
- Timestamps immutable in responses
- Version tracking for audit
- Soft deletes (deleted_at) for recovery
- Metadata field isolated (no injection risk)

## Testing Strategy

```
Unit Tests (Vitest)
├── Enum validation
├── Required fields
├── Field constraints
├── List operations
└── Metadata flexibility

Integration Tests (Playwright API)
├── Create flows
├── Update flows
├── List pagination
├── Relationship integrity
└── Timestamp accuracy

E2E Tests (Playwright)
├── Complete workflows
├── User interactions
├── State transitions
└── Data consistency
```

## Future Enhancements

1. **Versioning**: Track schema version changes
2. **Diff Tracking**: Compare versions automatically
3. **Relationships**: Add foreign key validation
4. **Workflow States**: Add state machine validation
5. **Notifications**: Add subscriber pattern
6. **Caching**: Add TTL metadata
7. **Archival**: Add archival rules
8. **Compliance**: Add compliance tracking
9. **Audit Trail**: Add change history
10. **Search**: Add full-text search metadata
