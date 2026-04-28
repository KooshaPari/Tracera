# ADR-0003: Gherkin/BDD Parser Selection

**Status:** Accepted
**Date:** 2026-01-29
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM v2 introduces BDD (Behavior-Driven Development) scenario management with Given-When-Then syntax. The system needs to:

1. **Parse** Gherkin feature files (`.feature` files)
2. **Validate** scenario syntax (Given/When/Then structure)
3. **Execute** scenarios against test implementations
4. **Link** scenarios to requirements and test cases
5. **Report** scenario execution results

Gherkin is the de-facto standard for BDD scenarios (Cucumber, Behave, etc.). Parser options include pure-Python implementations, JavaScript parsers, or official Cucumber parsers.

## Decision

We will use **python-gherkin** (pure Python parser) with **pytest-bdd** for execution.

## Rationale

### Parser Strategy

```python
# pyproject.toml - BDD dependencies (not yet added)
dependencies = [
    "gherkin-official>=29.0.0",  # Official Gherkin parser (Python bindings)
    "pytest-bdd>=7.0.0",         # Pytest BDD integration
    "parse>=1.20.0",             # Step definition matching
]
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BDD Scenario Engine                         │
├─────────────────────────────────────────────────────────────┤
│  Feature Files (.feature)                                    │
│    ↓                                                          │
│  gherkin-official parser → AST                               │
│    ↓                                                          │
│  TraceRTM Scenario Model (DB storage)                        │
│    ↓                                                          │
│  pytest-bdd execution → Step Definitions                     │
│    ↓                                                          │
│  Result aggregation → Coverage links                         │
└─────────────────────────────────────────────────────────────┘
```

### Key Advantages

- **Official parser**: `gherkin-official` is maintained by Cucumber team (canonical Gherkin spec)
- **Pure Python**: No external runtime dependencies (Node.js, Ruby)
- **Pytest integration**: `pytest-bdd` works with existing pytest infrastructure
- **Type safety**: Can parse to Python dataclasses for storage
- **Flexibility**: Can store parsed scenarios in PostgreSQL, execute later

### Execution Strategy

**Test Execution (pytest-bdd)**
```python
# Step definition example
from pytest_bdd import given, when, then, scenarios

scenarios('features/auth.feature')

@given('a user "admin" exists')
def user_exists(admin_user):
    return admin_user

@when('the user logs in with valid credentials')
def user_logs_in(client, admin_user):
    response = client.post('/login', json={'username': 'admin', 'password': 'secret'})
    assert response.status_code == 200

@then('the user should be authenticated')
def user_authenticated(client):
    assert client.get('/profile').status_code == 200
```

**Storage Model**
```python
# Parsed scenario stored in DB
class Scenario(Base):
    id: Mapped[str]
    feature_id: Mapped[str]
    title: Mapped[str]
    gherkin_text: Mapped[str]  # Original text

    # Parsed structure
    given_steps: Mapped[list[dict]]  # [{"text": "a user...", "table": null}]
    when_steps: Mapped[list[dict]]
    then_steps: Mapped[list[dict]]

    # Execution
    last_run_at: Mapped[datetime | None]
    last_run_result: Mapped[str]  # pass/fail/pending

    # Traceability
    requirement_ids: Mapped[list[str]]
    test_case_ids: Mapped[list[str]]
```

## Alternatives Rejected

### Alternative 1: behave (Python BDD framework)

- **Description:** Full BDD framework (parser + runner)
- **Pros:** Batteries-included, standalone BDD tool, Python-native
- **Cons:** Separate test runner (not pytest), harder to integrate with existing test suite, opinionated project structure
- **Why Rejected:** pytest-bdd integrates with existing pytest infrastructure. behave requires separate test organization.

### Alternative 2: JavaScript Cucumber parser

- **Description:** Use `@cucumber/gherkin` (Node.js) via subprocess
- **Pros:** Official Cucumber parser, most mature implementation
- **Cons:** Requires Node.js runtime, subprocess overhead, JSON serialization boundary
- **Why Rejected:** No advantage over Python bindings of same parser. Adds Node.js dependency to Python stack.

### Alternative 3: Custom regex-based parser

- **Description:** Build simple regex parser for Given/When/Then
- **Pros:** Lightweight, full control, no dependencies
- **Cons:** Incomplete Gherkin support (no tables, doc strings, examples), fragile parsing, reinventing wheel
- **Why Rejected:** Gherkin has complex syntax (scenario outlines, tables, tags). Official parser is battle-tested.

### Alternative 4: Store Gherkin text only (no parsing)

- **Description:** Store `.feature` files as text, parse on execution only
- **Pros:** Simplest storage model, no parser dependency for storage
- **Cons:** Can't query scenarios by steps, can't show structured UI, can't validate syntax upfront
- **Why Rejected:** TraceRTM needs structured data for UI (scenario tree, step list) and queries (find all scenarios using step X).

## Consequences

### Positive

- **Standard syntax:** Gherkin is widely known (Cucumber, Behave, SpecFlow)
- **Structured storage:** Can query scenarios by steps, tags, requirements
- **Pytest integration:** Reuses existing test infrastructure (fixtures, markers, reporting)
- **Validation:** Parser catches syntax errors before execution
- **Traceability:** Scenarios link to requirements, test cases automatically

### Negative

- **Parser dependency:** Requires `gherkin-official` library (adds ~1MB to dependencies)
- **Execution coupling:** pytest-bdd execution model is slightly different from Cucumber (Python fixtures vs. context)
- **Step definition registry:** Must maintain step definitions in code (can't auto-generate from scenarios)

### Neutral

- **Feature file storage:** Can store `.feature` files in Git or PostgreSQL (decision deferred to implementation)
- **Step reuse:** Common steps (given a user, when I click) can be shared across features
- **Execution mode:** Scenarios can be executed via pytest (automated) or manually triggered (MCP tool)

## Implementation

### Affected Components

- `src/tracertm/models/scenario.py` - Scenario, Feature, StepDefinition models
- `src/tracertm/services/scenario_service.py` - Scenario parsing, storage, execution
- `src/tracertm/mcp/tools/scenarios.py` - MCP tools for scenario management
- `tests/features/` - Example feature files
- `tests/step_defs/` - Step definition implementations

### Migration Strategy

**Phase 1: Parser Integration (Week 1)**
- Add `gherkin-official` dependency
- Implement parser wrapper
- Create Scenario/Feature models
- Alembic migration for new tables

**Phase 2: Storage & UI (Week 2)**
- Scenario CRUD service
- Feature tree UI component
- Gherkin editor (Monaco with syntax highlighting)

**Phase 3: Execution (Week 3)**
- pytest-bdd integration
- Step definition registry
- Execution reporting

### Rollout Plan

- **Phase 1:** Scenario parsing and storage (UI display only)
- **Phase 2:** Step definition management, execution infrastructure
- **Phase 3:** Automated execution, coverage reporting

### Success Criteria

- [ ] Parse all valid Gherkin syntax (scenarios, outlines, tables, doc strings)
- [ ] Store 1000+ scenarios with <500ms parse time
- [ ] Execute scenarios via pytest-bdd
- [ ] Link scenarios to requirements (many-to-many)
- [ ] Coverage report shows scenario → test case mappings

## References

- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
- [gherkin-official](https://github.com/cucumber/gherkin-python)
- [pytest-bdd](https://github.com/pytest-dev/pytest-bdd)
- [ADR-0001: TraceRTM v2 Architecture](ADR-0001-tracertm-v2-architecture.md)
- [ADR-0005: Test Strategy](ADR-0005-test-strategy-coverage-goals.md)

---

**Notes:**
- Gherkin parser supports 70+ languages (internationalization)
- Scenario outlines (example tables) enable data-driven testing
- Tags (@smoke, @integration) enable selective execution
- Doc strings (""") support multi-line inputs
- Tables (| header | data |) support structured test data
