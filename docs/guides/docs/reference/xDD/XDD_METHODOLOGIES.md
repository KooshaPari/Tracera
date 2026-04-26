# xDD Methodologies Reference

**Comprehensive guide to development methodologies, design principles, and best practices**

---

## Table of Contents

1. [Development Methodologies (xDD)](#development-methodologies-xdd)
2. [Design Principles](#design-principles)
3. [Architecture Patterns](#architecture-patterns)
4. [Quality Assurance](#quality-assurance)
5. [Process & Workflow](#process--workflow)
6. [Documentation](#documentation)
7. [Emerging Practices](#emerging-practices)

---

## Development Methodologies (xDD)

### TDD - Test-Driven Development
**Write tests before implementation**

```
RED -> GREEN -> REFACTOR
```

| Phase | Action |
|-------|--------|
| Red | Write failing test |
| Green | Write minimal code to pass |
| Refactor | Improve code while tests pass |

**When to use:**
- New module development
- Bug fixes (write failing test first)
- Critical paths requiring safety guarantees

### BDD - Behavior-Driven Development
**Define behavior via scenarios**

```gherkin
Feature: User Authentication
  Scenario: Valid login
    Given a user "alice" with password "secret"
    When she logs in with correct credentials
    Then she should have access to dashboard
```

**When to use:**
- Requirements clarification
- Acceptance criteria definition
- Stakeholder communication

### DDD - Domain-Driven Design
**Model domain logic with bounded contexts**

| Concept | Purpose |
|---------|---------|
| Entity | Object with identity |
| Value Object | Immutable, equality by value |
| Aggregate | Cluster of related objects |
| Domain Event | Something meaningful happened |
| Bounded Context | Boundary of a domain model |

**When to use:**
- Complex business domains
- Large-scale system modeling
- Strategic design decisions

### CDD - Contract-Driven Development
**Define interfaces/contracts before implementation**

```python
class StorageContract(ABC):
    """Contract for storage implementations."""

    @abstractmethod
    def write(self, key: str, value: Any) -> None:
        """Write must be atomic and durable."""
        pass
```

**When to use:**
- Plugin architectures
- Multiple implementation options
- API design

### SDD - Specification-Driven Development
**Specifications become executable tests**

| Step | Action |
|------|--------|
| 1 | Write detailed spec |
| 2 | Generate test cases from spec |
| 3 | Implement to pass tests |

**When to use:**
- Regulatory compliance
- Safety-critical systems
- Formal requirements

### FDD - Feature-Driven Development
**Build features incrementally**

```
Feature: [Name]
  - Develop feature list
  - Build by feature
  - Individual feature completion
```

**When to use:**
- Agile teams
- Iterative delivery
- Feature prioritization

### IDD - Interaction-Driven Development
**Design via interactions first**

```python
async def test_user_flow():
    # Design the interaction first
    result = await user.login(credentials)
    assert result.session_token
```

**When to use:**
- API design
- Async systems
- Event-driven architectures

### MDD - Model-Driven Development
**Generate code from models**

| Artifact | Purpose |
|----------|---------|
| UML Class Diagram | Code structure |
| State Machine | Behavior |
| Sequence Diagram | Interactions |

**When to use:**
- Code generation
- Model transformation
- MDA (Model-Driven Architecture)

### RDD - Report-Driven Development
**Let reports guide development**

```markdown
## Quality Report
- Coverage: 45% (target: 80%)
- Complexity: High in auth module
- Recommendation: Refactor auth
```

**When to use:**
- Legacy system improvement
- Quality metrics tracking
- Technical debt prioritization

---

## Design Principles

### SOLID Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **S**ingle Responsibility | One reason to change | Classes have one job |
| **O**pen/Closed | Open for extension, closed for modification | Use interfaces |
| **L**iskov Substitution | Subtypes must be substitutable | Honor contracts |
| **I**nterface Segregation | Many specific > one general | Fine-grained interfaces |
| **D**ependency Inversion | Depend on abstractions | Use DI |

### GRASP Principles

| Principle | Description |
|-----------|-------------|
| Controller | Handle system events |
| Creator | Who creates objects |
| Expert | Assign responsibility to information holder |
| High Cohesion | Related responsibilities together |
| Indirection | Intermediate object mediates |
| Low Coupling | Minimize dependencies |
| Polymorphism | Handle variations |

### KISS - Keep It Simple, Stupid

```python
# Complex
result = list(filter(lambda x: x > 0, map(lambda x: x * 2, data)))

# Simple (KISS)
doubled = [x * 2 for x in data]
positive = [x for x in doubled if x > 0]
```

### YAGNI - You Aren't Gonna Need It

> Implement things when you actually need them, never when you just foresee that you might need them.

### DRY - Don't Repeat Yourself

```python
# VIOLATION
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-z]+\.[a-z]{2,}$'
    return re.match(pattern, email)

def validate_email_ui(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-z]+\.[a-z]{2,}$'
    # ... duplicate pattern

# DRY
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-z]+\.[a-z]{2,}$'

def validate_email(email):
    return re.match(EMAIL_PATTERN, email)
```

### PoLA - Principle of Least Astonishment

```python
# VIOLATION - surprising behavior
def get_user(id):
    return create_default_user() if not found  # Returns different type!

# PoLA compliant
def get_user(id):
    if not found:
        raise UserNotFoundError(id)  # Expected behavior
```

### SoC - Separation of Concerns

```
┌─────────────────────────────────────┐
│           Presentation              │
├─────────────────────────────────────┤
│           Application              │
├─────────────────────────────────────┤
│             Domain                  │
├─────────────────────────────────────┤
│          Infrastructure             │
└─────────────────────────────────────┘
```

### Law of Demeter (LoD)

```python
# VIOLATION - train wreck
user.address.city.country.name

# PoLA compliant
user.get_country_name()
```

---

## Architecture Patterns

### Clean Architecture

```
     ┌─────────────────────────────────────┐
     │           External Tools             │
     │   (Web, DB, UI, Devices, Files)     │
     └──────────────────┬──────────────────┘
                        │
     ┌──────────────────▼──────────────────┐
     │         Interface Adapters          │
     │    (Controllers, Gateways, etc)      │
     └──────────────────┬──────────────────┘
                        │
     ┌──────────────────▼──────────────────┐
     │          Application Rules          │
     │       (Use Cases, Input Ports)      │
     └──────────────────┬──────────────────┘
                        │
     ┌──────────────────▼──────────────────┐
     │            Entities                 │
     │     (Enterprise Business Rules)      │
     └─────────────────────────────────────┘
```

### Hexagonal Architecture (Ports & Adapters)

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Input Port │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │      Application       │
              │     (Use Cases)        │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │ Output Port │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │      Adapters          │
              │  ┌─────┐ ┌──────────┐ │
              │  │ SQL │ │  HTTP    │ │
              │  └─────┘ └──────────┘ │
              └────────────────────────┘
```

### Onion Architecture

```
┌─────────────────────────────────────┐
│         UI / Infrastructure         │
├─────────────────────────────────────┤
│            Application              │
├─────────────────────────────────────┤
│              Domain                 │
├─────────────────────────────────────┤
│          Domain Services            │
└─────────────────────────────────────┘
```

### CQRS - Command Query Responsibility Segregation

```
Commands (Write)              Queries (Read)
┌────────────┐               ┌────────────┐
│  Create    │               │  Read      │
│  Update    │───────────────│  Report    │
│  Delete    │   Event Bus   │  Search    │
└────────────┘               └────────────┘
```

### EDA - Event-Driven Architecture

```
┌────────┐    Event    ┌────────┐    Event    ┌────────┐
│Producer│─────────────▶│ Broker │─────────────▶│Consumer│
└────────┘              └────────┘              └────────┘
```

### Microservices Patterns

| Pattern | Purpose |
|---------|---------|
| Strangler Fig | Incremental migration |
| Sidecar | Cross-cutting concerns |
| Circuit Breaker | Fault isolation |
| Saga | Distributed transactions |
| API Gateway | Single entry point |

### Event Sourcing

```
┌─────────┐    Command    ┌──────────┐
│ Aggregate├─────────────▶│  Event   │
│         │              │  Store   │
└─────────┘              └────┬─────┘
                             │
                      ┌──────▼──────┐
                      │  Projections│
                      └─────────────┘
```

---

## Quality Assurance

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=1)))
@settings(max_examples=100)
def test_sorting_properties(nums):
    """Properties that must hold for ALL valid inputs."""
    sorted_nums = sorted(nums)

    # Property 1: Same length
    assert len(sorted_nums) == len(nums)

    # Property 2: All elements preserved
    assert sorted(sorted_nums) == sorted(nums)

    # Property 3: Order is non-decreasing
    assert all(a <= b for a, b in zip(sorted_nums, sorted_nums[1:]))
```

**Tools:** Hypothesis, property-based testing libraries

### Mutation Testing

```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run

# View results
mutmut results
```

**Tools:** mutmut (Python), PIT (Java), Stryker (JS/C#)

### Contract Testing

```python
class DualWriteStorageContract:
    """Contract that all storage implementations must satisfy."""

    def test_write_creates_file(self, storage):
        """Write must create the file."""
        storage.write("key", {"data": "value"})
        assert storage.exists("key")

    def test_read_returns_written_value(self, storage):
        """Read must return exact value."""
        storage.write("key", {"data": "value"})
        assert storage.read("key") == {"data": "value"}

    def test_roundtrip_preserves_data(self, storage):
        """Roundtrip must preserve all data types."""
        original = {"str": "test", "int": 42, "float": 3.14}
        storage.write("key", original)
        assert storage.read("key") == original
```

**Tools:** pytest-httpserver, Pact (consumer-driven)

### Chaos Engineering

```yaml
# Chaos experiment definition
apiVersion: chaos.metrics.googleapis.com/v1
kind: ChaosExperiment
metadata:
  name: pod-kill
spec:
  description: "Kill random pod"
  method:
    pod-kill:
      probability: 0.1
```

**Tools:** Chaos Monkey, Gremlin, LitmusChaos

### Fuzz Testing

```python
import atheris

@atheris.instrument_import()
def TestOneInput(input_bytes):
    """Fuzz test for JSON parser."""
    try:
        json.loads(input_bytes)
    except json.JSONDecodeError:
        pass  # Expected

atheris.TestOneInput()
```

**Tools:** AFL, libFuzzer, atheris

---

## Process & Workflow

### DevOps

```
Plan -> Code -> Build -> Test -> Deploy -> Operate -> Monitor
  ↑___________________________________________|
```

### CI/CD Pipeline

```yaml
stages:
  - lint
  - test
  - security-scan
  - build
  - deploy-staging
  - integration-test
  - deploy-production
```

### Agile Methodologies

| Methodology | Cadence | Focus |
|-------------|---------|-------|
| Scrum | 2-week sprints | Delivery |
| Kanban | Continuous | Flow |
| Scrumban | Hybrid | Flexibility |
| SAFe | 10-week PI | Large teams |

### Code Review Checklist

- [ ] Tests pass
- [ ] Code follows style guide
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] No commented-out code
- [ ] Error handling complete
- [ ] Performance considered

---

## Documentation

### ADR - Architecture Decision Record

```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Accepted

## Context
We need a relational database for...

## Decision
We will use PostgreSQL 14+

## Consequences
### Positive
- ACID compliance
- Rich indexing

### Negative
- Operational overhead
```

### RFC - Request for Comments

```markdown
# RFC-042: GraphQL API Design

## Summary
Propose GraphQL API for...

## Motivation
REST limitations...

## Proposal
type Query {
  user(id: ID!): User
  users(filter: UserFilter): [User!]!
}
```

### Runbook

```markdown
# Service Restart Runbook

## Prerequisites
- SSH access to prod-server-01
- sudo privileges

## Steps
1. Drain traffic: `kubectl drain node-01`
2. Restart service: `systemctl restart myservice`
3. Verify: `curl localhost:8080/health`
```

### SpecDD - Specification-Driven Development

```
Spec (FR) → Test (BDD) → Code → Verify → Deploy
   ↑                                      │
   └──────────────────────────────────────┘
```

---

## Emerging Practices

### AI-DD - AI-Driven Development

```python
# Use AI to generate test cases
@ai.generate_tests(
    prompt="Generate edge cases for password validation",
    model="claude-3"
)
def test_password_validation():
    pass
```

### Prompt-Driven Development

```
User Story → Detailed Prompt → AI Code → Human Review → Merge
```

### StoryDD - Story-Driven Development

```markdown
## User Story
As a user, I want to reset my password

## Scenarios (StoryDD)
1. Valid email → sends reset link
2. Invalid email → shows error
3. Expired token → shows expiration message
```

### TraceDD - Traceability-Driven Development

```
FR-001 ─┬─→ Test-001 ─┬─→ Code-A ─┬─→ Build-001
        ├─→ Test-002 ─┤
        └─→ Doc-001 ◄─┘
```

---

## Quick Reference Card

| Category | Principle | When to Apply |
|----------|-----------|---------------|
| Architecture | Clean/Hexagonal | New project, refactor |
| Testing | TDD + Property | New features, bug fixes |
| Design | SOLID | Code review, refactor |
| Process | CI/CD | All projects |
| Documentation | ADR | Major decisions |
| Quality | Mutation testing | Pre-release |

---

## See Also

- [ADR-017: Hexagonal Architecture](./ADR-017-hexagonal-architecture.md)
- [ADR-018: Testing Strategy](./ADR-018-testing-strategy.md)
- [AgilePlus Workflow](../guides/AGILE_WORKFLOW.md)
