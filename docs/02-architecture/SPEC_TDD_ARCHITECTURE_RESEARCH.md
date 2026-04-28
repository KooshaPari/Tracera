# Complete Research: Spec-Driven Development, TDD & Architectural Patterns
## Comprehensive Guide for Trace Implementation

**Document Version**: 1.0.0
**Date**: 2025-11-20
**Purpose**: Research synthesis for methodology and architecture selection

---

## Executive Summary

This document synthesizes comprehensive research on:
- **Spec-Driven Development** (SDD): BMAD-METHOD, Spec Kit, OpenSpec
- **Test-Driven Development** (TDD): Red-Green-Refactor, Kent Beck's patterns
- **Hexagonal Architecture**: Ports & Adapters pattern
- **Clean Architecture**: Uncle Bob's layers and dependency rule
- **Microservices Patterns**: DDD, CQRS, Event Sourcing, Saga

### Key Recommendations for Trace

1. **Methodology**: Use OpenSpec (lightweight) + TDD (test-first)
2. **Architecture**: Clean Architecture with Hexagonal boundaries
3. **Patterns**: Event Sourcing + CQRS for versioning, Saga for distributed tasks
4. **Implementation**: Python 3.12, FastAPI/FastMCP, modular design

---

## PART 1: Spec-Driven Development (SDD)

### 1.1 What is Spec-Driven Development?

**Definition**: A methodology where formal, structured specifications serve as executable blueprints that directly drive code generation, validation, and maintenance.

**Core Principle**: Specifications are your source of truth—they guide automated code creation, not merely document it.

**Difference from Traditional Development**:
```
Traditional:         Requirements → Design → Code → Tests → Docs
Spec-Driven:         Spec (executable) → Plan → Generate → Validate → Iterate
                     ↑_______________ Continuous Loop ________________↓
```

### 1.2 The 10 Critical Things About Specs

Based on AI Native Dev research (2025):

#### 1. What's a Spec, Really?

A spec **formulates your intent as a set of requirements** that agents break into implementation steps.

**Key Insight**: Specs delegate through clear requirements—like handing someone a recipe versus asking them to "make dinner."

**Example**:
```markdown
# ❌ Bad Prompt
"Build a user authentication system"

# ✅ Good Spec
## Requirement: User Authentication

### Scenario: Successful Login
**Given** user exists with email "test@example.com" and valid password
**When** user submits login form
**Then** system returns JWT token valid for 24 hours
**And** token includes user_id and role claims

### Scenario: Failed Login - Invalid Password
**Given** user exists with email "test@example.com"
**When** user submits login form with incorrect password
**Then** system returns 401 Unauthorized
**And** error message is "Invalid credentials"
**And** login attempt is logged for security monitoring
```

#### 2. Specs Come in Different Flavors

Four main types:

**Functional/Technical Specs** (`spec.md`):
- Feature descriptions
- API contracts
- Data models
- Business rules

**Agent Identity Specs** (`Agent.md`):
- AI assistant personality
- Boundaries and constraints
- Expertise areas
- Communication style

**Task/Workflow Specs**:
- Process sequences
- Agent coordination
- State transitions
- Error handling

**Usage/Knowledge Specs**:
- Domain knowledge
- Context for specific environments
- Conventions and standards
- Best practices

**Key Insight**: Mature AI development orchestrates multiple spec types together.

#### 3. Specs Format Matters (But Not Obsessively)

**Popular Formats**:
- **Markdown**: Default, IDE-readable, GitHub-compatible
- **Speclang**: Domain-specific language for specs
- **BMAD patterns**: Structured agent-driven format
- **EARS format** (Kiro): Easy Approach to Requirements Syntax
- **Agents.md conventions**: AI assistant instructions
- **Claude Skills**: Claude-specific formatting

**Key Insight**: "Specs are sensitive to the models being used." What works with Claude may need adjustment for GPT-4.

**Recommendation**: Start with Markdown, prioritize iteration over perfection.

#### 4. Context Window Constraints Are Real

**Problem**: Large or numerous specs overload context windows.

**Solutions**:

**RAG/Context Selection**:
```python
# Grep-based approach (surprisingly effective)
def select_relevant_specs(query: str, spec_dir: str) -> List[str]:
    """Select specs relevant to query using grep"""
    results = subprocess.run(
        ['grep', '-r', '-l', query, spec_dir],
        capture_output=True
    )
    return results.stdout.decode().splitlines()
```

**Subagents**:
```python
# Deploy specialized agents with focused context
class SpecializedAgent:
    def __init__(self, spec_files: List[str]):
        self.context = self.load_specs(spec_files)
        self.max_tokens = 4000  # Small focused context
```

**AST Parsing/LSP Integration**:
```python
# Connect specs to related code
def link_spec_to_code(spec_file: str) -> List[str]:
    """Find code files referenced in spec"""
    # Parse spec for code references
    # Use LSP to find definitions
    # Return related files
```

**Key Insight**: Specs need information architecture—avoid massive single files.

#### 5. Can We Regenerate Apps From Scratch?

**Answer**: Not reliably yet (as of 2025).

**Requirements for Success**:
1. Planning method (Backlog.md) breaking work into chunks
2. Recognition that "spec-driven development is an iterative approach, not a magic generate-once solution"
3. Language/model dependencies heavily impact results

**Current State**: Better for 1→n (modifications) than 0→1 (greenfield).

#### 6. The Tool Ecosystem

**450+ tools** exist in the AI Native Dev Landscape (2025).

**Notable Players**:

**AWS Kiro**:
- Structure: spec → design → tasks → implementation
- Uses EARS format (Easy Approach to Requirements Syntax)
- Automated reasoning for verification
- Still in preview (mid-2025)

**GitHub Spec Kit**:
- Open source, released Sept 2024
- CLI + templates + prompts
- Phases: Specify → Plan → Tasks → Implement
- Works with Copilot, Claude, Cursor, Gemini

**OpenSpec**:
- TypeScript-based
- Lightweight (250 lines vs Spec Kit's 800 lines)
- `openspec/specs/` for truth, `openspec/changes/` for proposals
- Three commands: /openspec:proposal, /openspec:apply, /openspec:archive

**BMAD-METHOD**:
- 19 specialized agents (PM, Architect, Developer, etc.)
- Scale-adaptive intelligence
- Analysis → Planning → Architecture → Implementation
- Each agent is a Markdown file with persona

**Recommendation**: "Pick one tool that fits your workflow and go deep before exploring alternatives."

#### 7. Registries and Spec Sharing

**Current Approaches**:
- Git Submodules (functional but inelegant)
- IDE team features (risk of lock-in)
- Internal package repositories
- Public registries (Tessl exploring this)

**Future**: Like npm/PyPI for common patterns (auth, API design, etc.).

#### 8. Code Review is Still Essential

**Why**: "Someone on the team needs to know if the generated implementation makes sense, is maintainable, and follows best practices."

**Best Practice**: "The implementation agent and the testing agent should have different perspectives."

**Key Insight**: Human oversight catches edge cases both agents miss.

#### 9. Legacy Applications

**Reality**: Specs work partially for legacy systems.

**Strangler Pattern**:
```
Legacy System
  ├─ Old Code (untouched)
  └─ New Features (spec-driven)
      ├─ Spec: feature-1.md
      ├─ Spec: feature-2.md
      └─ Bridge: adapters to legacy
```

**Key Factors**:
- Language-specific models matter significantly
- Tool integration bridging existing and new code is key
- Specs systematize incremental improvement

**Not**: Won't magically modernize systems.

#### 10. We're Not There Yet (But It's Already Useful)

**Current State**: Early adopter phase with real immediate value.

**Value**: Specs provide "structure to AI-assisted development" versus unstructured prompting.

**Variability**: Output varies across tools and models.

**Future Needs**:
- Spec evaluation metrics
- Better knowledge capture practices
- Standardization

**Key Insight**: "The process of writing specs together as a team helps not only your agents, but also aligns humans inside your team."

### 1.3 BMAD-METHOD Deep Dive

**Full Name**: Breakthrough Method for Agile AI-Driven Development

**Core Philosophy**: Addresses "vibe coding" (unstructured prompts to AI) with structured, battle-tested workflows.

#### Architecture

**19 Specialized Agents**:
```
Strategic Layer:
  - Product Manager: Defines features and priorities
  - Solution Architect: Designs system architecture
  - Security Architect: Ensures security best practices

Planning Layer:
  - Scrum Master: Manages sprint planning
  - Feature Analyst: Breaks down requirements

Development Layer:
  - Senior Developer: Implements complex features
  - Backend Developer: API and business logic
  - Frontend Developer: UI components
  - Database Engineer: Schema and queries
  - DevOps Engineer: CI/CD and infrastructure

Quality Layer:
  - QA Engineer: Test strategy and automation
  - Test Automation Engineer: Test implementation
  - Performance Engineer: Load testing and optimization

Support Layer:
  - Technical Writer: Documentation
  - UX Designer: User experience
  - Code Reviewer: Quality assurance
  - Release Manager: Deployment coordination
```

**Each Agent**:
- Self-contained Markdown file
- Well-defined persona
- Specific responsibilities
- Clear boundaries

#### Workflow

```
1. Analysis
   ├─ Feature Analyst: Breaks down request
   └─ Solution Architect: Designs approach

2. Planning
   ├─ Scrum Master: Creates sprint plan
   └─ PM: Prioritizes features

3. Architecture
   ├─ Solution Architect: System design
   └─ Security Architect: Security review

4. Implementation
   ├─ Developers: Write code
   ├─ QA: Write tests
   └─ DevOps: Set up infrastructure

5. Review & Deploy
   ├─ Code Reviewer: Quality check
   └─ Release Manager: Deploy
```

#### Scale-Adaptive Intelligence

**Bug Fix**:
```
Agents: Developer, QA
Depth: Minimal planning
Time: Minutes
```

**Feature Addition**:
```
Agents: Analyst, Developer, QA, Reviewer
Depth: Medium planning
Time: Hours
```

**Enterprise System**:
```
Agents: All 19 agents
Depth: Comprehensive planning
Time: Weeks
```

#### Integration with Spec-Driven Development

**Key Innovation**: BMAD + SDD = Single Source of Truth (SSoT)

**Implementation**:
```markdown
# bmad-specs/feature-001-auth.md

## Specification (BMAD SSoT)

### Functional Requirements
- FR-001: User can log in with email/password
- FR-002: JWT token valid for 24 hours
- FR-003: Failed attempts logged

### Acceptance Criteria
- AC-001: Login with valid credentials returns 200 + token
- AC-002: Login with invalid credentials returns 401
- AC-003: Login attempt logged in security_events table

### Architecture Constraints
- Must use bcrypt for password hashing (cost factor 12)
- JWT must use HS256 algorithm
- Tokens stored in Redis with 24h TTL

### Test Requirements
- Unit tests for authentication logic
- Integration tests for API endpoints
- Load test: 1000 concurrent logins

## Implementation Tasks
Generated by: Backend Developer Agent
Reviewed by: Code Reviewer Agent

- [ ] Task 1: Implement password hashing (backend-dev)
- [ ] Task 2: Implement JWT generation (backend-dev)
- [ ] Task 3: Create login endpoint (backend-dev)
- [ ] Task 4: Write unit tests (qa-engineer)
- [ ] Task 5: Write integration tests (qa-engineer)
```

**Benefits**:
- Specs drive code generation
- Specs validate implementation
- Agents refer to same spec
- Version-controlled truth

### 1.4 OpenSpec vs Spec Kit vs BMAD

#### Comparison Matrix

| Feature | OpenSpec | Spec Kit | BMAD-METHOD |
|---------|----------|----------|-------------|
| **Output Size** | 250 lines | 800 lines | Varies by scale |
| **Learning Curve** | Low | Medium | Medium-High |
| **Structure** | Lightweight | Comprehensive | Hierarchical |
| **Best For** | 0→1 & 1→n | Platform teams | Enterprise projects |
| **Agent Model** | Generic AI | Generic AI | 19 specialized agents |
| **Workflow** | Propose→Review→Implement | Specify→Plan→Task | Analysis→Plan→Arch→Impl |
| **Documentation Burden** | Low | High | Medium |
| **Flexibility** | High | Medium | Medium |
| **Team Size** | 1-3 | 3-10 | 5-20 |

#### OpenSpec Workflow

```
1. Draft Proposal
   openspec/changes/001-feature/
   ├── proposal.md     # What, why, scope
   ├── design.md       # How, architecture
   ├── tasks.md        # Implementation steps
   └── specs/          # Requirements & scenarios
       ├── api.md
       └── data.md

2. Review & Align
   - Technical review
   - Stakeholder approval
   - Refine based on feedback

3. Implement Tasks
   - Reference change ID in commits
   - TDD implementation
   - Continuous integration

4. Archive & Merge
   - Move specs to openspec/specs/
   - Archive change to openspec/archive/
   - Update changelog
```

**Key Files**:

**AGENTS.md**:
```markdown
# OpenSpec Instructions

AI assistants open this when:
- Planning or proposals mentioned
- New capabilities or breaking changes
- Architecture shifts
- Big performance/security work

## Workflow
1. Draft: Create openspec/changes/<id>/proposal.md
2. Review: Get approval before implementing
3. Implement: Reference change ID in commits
4. Archive: Move to openspec/archive/
```

**constitution.md**:
```markdown
# Project Constitution

## Principles
1. Module Size: ≤350 lines (500 max)
2. Test-First: Write tests before code
3. Type Safety: Full type hints
4. Performance: Meet all targets
5. Spec-Driven: All changes start with proposal
```

### 1.5 SDD Best Practices (2025)

#### Quality and Precision

**Target**: 95%+ accuracy in implementing specs on first go, with error-free, unit-tested code.

**How to Achieve**:
```markdown
## Spec Quality Checklist

### Clarity
- [ ] Requirements use clear, unambiguous language
- [ ] All terms defined in glossary
- [ ] Examples provided for complex scenarios

### Completeness
- [ ] All happy paths covered
- [ ] All error scenarios specified
- [ ] Edge cases documented
- [ ] Performance requirements stated

### Testability
- [ ] Each requirement has acceptance criteria
- [ ] Criteria are measurable
- [ ] Test data provided
- [ ] Expected outputs defined

### Consistency
- [ ] Terminology consistent throughout
- [ ] No contradictions between sections
- [ ] Cross-references validated
```

#### Specification Time Investment

**Research Finding**: Specification time is typically **20-40%** of manual implementation time.

**ROI**: Becomes positive when AI generates code **50-80%** faster than manual coding.

**Calculation**:
```
Manual Development: 40 hours
Spec Time: 10 hours (25%)
AI Generation: 5 hours (AI is 8x faster)
Total with SDD: 15 hours

Savings: 25 hours (62.5% faster)
```

#### Risk Mitigation Strategies

**Phased Adoption**:
```
Phase 1 (Month 1): Pilot project (1 feature, 1 team)
  ├─ Learn SDD workflow
  ├─ Refine spec templates
  └─ Measure results

Phase 2 (Month 2-3): Expand (3 features, 2 teams)
  ├─ Apply learnings
  ├─ Build spec library
  └─ Train more developers

Phase 3 (Month 4+): Scale (all new features)
  ├─ Mandatory for new development
  ├─ Continuous improvement
  └─ Measure productivity gains
```

**Comprehensive Validation**:
- Automated spec validation (linting, consistency checks)
- Peer review of all specs
- Acceptance criteria testing
- Human code review

**Hybrid Workflows**:
```
New Features: 100% SDD
Bug Fixes: Manual (too small for specs)
Refactoring: SDD for complex, manual for simple
Prototypes: Vibe coding (speed over precision)
```

#### When to Use SDD

**✅ Use SDD For**:
- Complex business logic
- APIs with clear contracts
- Data transformations
- Integration points
- Features with strict requirements

**❌ Don't Use SDD For**:
- Highly exploratory work (research, prototyping)
- Rapidly changing requirements
- Novel algorithms needing experimentation
- Performance-critical code needing manual optimization
- Creative decisions (UI design nuances)

---

## PART 2: Test-Driven Development (TDD)

### 2.1 What is TDD?

**Definition**: An approach where you write tests first, then use those tests to drive the design and development of your application.

**Inventor**: Kent Beck (late 1990s, part of Extreme Programming)

**Mantra**: "Red/Green/Refactor"
- **Red**: Write a failing test
- **Green**: Make it pass (simplest way)
- **Refactor**: Clean up code

### 2.2 The Red-Green-Refactor Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                     TDD CYCLE                                │
└─────────────────────────────────────────────────────────────┘

1. RED: Write a Failing Test
   ├─ Think about desired behavior
   ├─ Write test for that behavior
   ├─ Run test → Should FAIL (no implementation yet)
   └─ Verify test fails for right reason

2. GREEN: Make It Pass
   ├─ Write minimum code to pass test
   ├─ Don't worry about perfection yet
   ├─ Run test → Should PASS
   └─ Commit if green

3. REFACTOR: Clean Up
   ├─ Improve code structure
   ├─ Remove duplication
   ├─ Improve names
   ├─ Run tests → Still PASS
   └─ Commit clean code

4. REPEAT
   └─ Go to step 1 for next behavior
```

### 2.3 TDD Example: Trace Item Creation

**Red Phase**:
```python
# tests/test_item_service.py
import pytest
from services.item_service import ItemService
from models import ViewType

def test_create_item_returns_item_with_id():
    """Test that creating an item returns item with generated ID"""
    # Arrange
    service = ItemService()
    title = "Test Feature"
    view_type = ViewType.FEATURE

    # Act
    item = service.create_item(title=title, view_type=view_type)

    # Assert
    assert item.id is not None
    assert item.title == title
    assert item.view_type == ViewType.FEATURE

# Run: pytest tests/test_item_service.py
# Result: FAIL - ItemService doesn't exist yet ✓ (Expected failure)
```

**Green Phase**:
```python
# services/item_service.py
from uuid import uuid4
from models import UniversalItem, ViewType
from datetime import datetime

class ItemService:
    def create_item(self, title: str, view_type: ViewType) -> UniversalItem:
        """Create new item - simplest implementation"""
        return UniversalItem(
            id=uuid4(),
            title=title,
            view_type=view_type,
            description="",
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system"
        )

# Run: pytest tests/test_item_service.py
# Result: PASS ✓
```

**Refactor Phase**:
```python
# services/item_service.py
from uuid import uuid4, UUID
from models import UniversalItem, ViewType, ItemStatus
from datetime import datetime
from typing import Optional

class ItemService:
    """Service for managing items across all views"""

    def __init__(self, repository: 'ItemRepository'):
        self.repository = repository

    def create_item(
        self,
        title: str,
        view_type: ViewType,
        description: str = "",
        created_by: str = "system"
    ) -> UniversalItem:
        """
        Create new item with generated ID and timestamps

        Args:
            title: Item title
            view_type: Type of view (feature, code, etc.)
            description: Optional description
            created_by: User/agent creating item

        Returns:
            Created UniversalItem with generated ID
        """
        item = UniversalItem(
            id=uuid4(),
            title=title,
            view_type=view_type,
            description=description,
            status=ItemStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by
        )

        # Save to repository
        self.repository.save(item)

        return item

# Run: pytest tests/test_item_service.py
# Result: Still PASS ✓ (refactoring didn't break anything)
```

### 2.4 Kent Beck's TDD Patterns

#### Isolated Tests

**Principle**: Tests should not affect each other.

**Why**: Tests can run independently, leading to faster feedback and effective debugging.

**Implementation**:
```python
# ✅ Good: Isolated tests
class TestItemService:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Fresh database for each test"""
        self.db = create_test_database()
        self.service = ItemService(self.db)
        yield
        self.db.cleanup()

    def test_create_item(self):
        item = self.service.create_item("Test")
        assert item.id is not None

    def test_delete_item(self):
        item = self.service.create_item("Test")
        self.service.delete_item(item.id)
        assert self.service.get_item(item.id) is None

# Each test gets fresh database, no interference
```

```python
# ❌ Bad: Tests share state
class TestItemService:
    db = create_database()  # Shared!
    service = ItemService(db)

    def test_create_item(self):
        item = self.service.create_item("Test")
        assert item.id is not None

    def test_delete_item(self):
        # Assumes item from test_create_item exists!
        # Will fail if tests run in different order
        items = self.service.list_items()
        self.service.delete_item(items[0].id)
```

#### One Step at a Time

**Principle**: Choose a test that will contribute to your overall goal and that you feel confident you can implement.

**Why**: Each test should signify a single step towards progress.

**Implementation**:
```python
# Test sequence for item creation feature:

# Step 1: Basic creation
def test_create_item_returns_item():
    pass

# Step 2: ID generation
def test_create_item_generates_unique_id():
    pass

# Step 3: Timestamps
def test_create_item_sets_timestamps():
    pass

# Step 4: Persistence
def test_create_item_saves_to_database():
    pass

# Step 5: Validation
def test_create_item_validates_title_not_empty():
    pass

# Each test builds on previous, incrementally
```

#### Test-Driven Design

**Principle**: Tests drive design decisions.

**Example**:
```python
# Test reveals design need:
def test_create_item_publishes_event():
    """Creating item should publish ITEM_CREATED event"""
    service = ItemService()
    event_bus = Mock()

    # This test reveals we need event publishing!
    item = service.create_item("Test", event_bus=event_bus)

    event_bus.publish.assert_called_once_with(
        EventType.ITEM_CREATED,
        item_id=item.id
    )

# Test forced us to add event_bus parameter
# Good! Tests drove design towards event-driven architecture
```

### 2.5 TDD Best Practices (2025)

#### Test Pyramid

```
        /\
       /  \       E2E Tests (10%)
      /    \      - Full user workflows
     /------\     - Slow, expensive
    /        \
   /          \   Integration Tests (30%)
  /            \  - Component interactions
 /--------------\ - Database, API, NATS
/                \
/________________\ Unit Tests (60%)
                   - Pure functions
                   - Fast, cheap
```

#### Test Naming Conventions

**Pattern**: `test_<method>_<scenario>_<expected_result>`

**Examples**:
```python
# ✅ Good names
def test_create_item_with_valid_data_returns_item():
    pass

def test_create_item_with_empty_title_raises_ValueError():
    pass

def test_time_travel_to_past_timestamp_returns_correct_state():
    pass

# ❌ Bad names
def test_create():
    pass

def test_1():
    pass

def test_it_works():
    pass
```

#### Arrange-Act-Assert (AAA)

```python
def test_commit_creates_snapshot_after_100_events():
    # Arrange
    repo = create_test_repository()
    versioning = VersioningService(repo)
    create_99_events(versioning)

    # Act
    versioning.create_event(EventType.ITEM_UPDATED, item_id=123)

    # Assert
    snapshots = repo.get_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0].event_count == 100
```

#### Test Doubles

**Types**:
- **Stub**: Returns canned data
- **Mock**: Verifies interactions
- **Fake**: Simplified working implementation
- **Spy**: Records calls

**Example**:
```python
from unittest.mock import Mock, patch

def test_item_service_publishes_to_nats():
    # Mock NATS client
    nats_client = Mock()

    service = ItemService(nats_client=nats_client)
    item = service.create_item("Test")

    # Verify interaction
    nats_client.publish.assert_called_once_with(
        subject="TRACE_EVENTS.feature.created",
        payload=item.to_dict()
    )
```

#### Continuous Testing

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          uv run pytest tests/ \
            --cov \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=80
```

---

## PART 3: Hexagonal Architecture (Ports & Adapters)

### 3.1 What is Hexagonal Architecture?

**Inventor**: Alistair Cockburn (2005)
**Book**: Published April 2024 (with Juan Manuel Garrido de Paz)

**Goal**: Create loosely coupled application components that can be easily connected to their software environment.

**Core Idea**: Application at center, surrounded by adapters for external systems.

### 3.2 Key Concepts

#### Ports

**Definition**: Technology-agnostic entry points into an application component.

**Types**:

**Driving Ports (Primary)**: Application offers functionality
```python
# Port: Application service interface
class ItemServicePort(Protocol):
    """Port for item management operations"""

    def create_item(self, title: str, view_type: ViewType) -> UniversalItem:
        """Create new item"""
        ...

    def get_item(self, item_id: UUID) -> Optional[UniversalItem]:
        """Retrieve item by ID"""
        ...
```

**Driven Ports (Secondary)**: Application needs functionality
```python
# Port: Repository interface
class ItemRepositoryPort(Protocol):
    """Port for item persistence"""

    def save(self, item: UniversalItem) -> None:
        """Save item"""
        ...

    def find_by_id(self, item_id: UUID) -> Optional[UniversalItem]:
        """Find item by ID"""
        ...
```

#### Adapters

**Definition**: Concrete implementations of ports using specific technology.

**Driving Adapters (Primary)**: Initiate interaction
```python
# Adapter: FastAPI/FastMCP adapter
class FastMCPAdapter:
    """HTTP adapter for item service"""

    def __init__(self, item_service: ItemServicePort):
        self.item_service = item_service

    @mcp.tool()
    def create_item(self, title: str, view_type: str) -> Dict[str, Any]:
        """MCP tool for creating items"""
        view = ViewType(view_type)
        item = self.item_service.create_item(title, view)
        return item.to_dict()
```

**Driven Adapters (Secondary)**: Provide functionality
```python
# Adapter: SQLite repository
class SQLiteItemRepository(ItemRepositoryPort):
    """SQLite implementation of item repository"""

    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")

    def save(self, item: UniversalItem) -> None:
        with Session(self.engine) as session:
            session.add(item)
            session.commit()

    def find_by_id(self, item_id: UUID) -> Optional[UniversalItem]:
        with Session(self.engine) as session:
            return session.query(UniversalItem).get(item_id)
```

### 3.3 Hexagonal Architecture in Trace

```
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTERS (Infrastructure)                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastMCP    │  │     CLI      │  │     TUI      │      │
│  │   (HTTP)     │  │   (Typer)    │  │  (Textual)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                     PORTS (Application)                      │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Application Services                       │    │
│  │  - ItemService                                       │    │
│  │  - VersioningService                                 │    │
│  │  - PlanningService                                   │    │
│  │  - VerificationService                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                       DOMAIN (Core)                          │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        Domain Model (Business Logic)                │    │
│  │  - UniversalItem                                    │    │
│  │  - Commit                                           │    │
│  │  - WBSTree                                          │    │
│  │  - AcceptanceCriterion                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                     PORTS (Infrastructure)                   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      Infrastructure Interfaces                      │    │
│  │  - ItemRepositoryPort                               │    │
│  │  - EventStorePort                                   │    │
│  │  - MessageBusPort                                   │    │
│  │  - VerificationEnginePort                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    ADAPTERS (Infrastructure)                 │
│                           │                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │     NATS     │  │  IntentGuard │      │
│  │  Repository  │  │  Event Bus   │  │  Verifier    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Hexagonal Architecture Benefits

**Testability**:
```python
# Easy to test with fake adapters
def test_create_item_saves_to_repository():
    # Use in-memory fake repository (no database needed)
    fake_repo = InMemoryItemRepository()
    service = ItemService(repository=fake_repo)

    item = service.create_item("Test")

    saved_items = fake_repo.items
    assert len(saved_items) == 1
    assert saved_items[0].id == item.id
```

**Flexibility**:
```python
# Easy to swap adapters
# Development: SQLite
service = ItemService(repository=SQLiteRepository("dev.db"))

# Testing: In-memory
service = ItemService(repository=InMemoryRepository())

# Production: PostgreSQL
service = ItemService(repository=PostgreSQLRepository(url))

# Same service, different adapters!
```

**Independence**:
- Domain logic doesn't know about SQLite, NATS, or FastMCP
- Can change database without touching business logic
- Can test without external dependencies

### 3.5 Hexagonal Architecture in Python (FastAPI Example)

**Directory Structure**:
```
trace/
├── domain/              # Domain logic (business rules)
│   ├── models.py        # UniversalItem, Commit, etc.
│   └── services.py      # Business logic
├── application/         # Use cases (application logic)
│   ├── ports.py         # Port interfaces
│   └── services.py      # Application services
├── infrastructure/      # Adapters (external concerns)
│   ├── repositories/
│   │   ├── sqlite_repository.py
│   │   └── postgresql_repository.py
│   ├── messaging/
│   │   └── nats_adapter.py
│   └── web/
│       └── fastmcp_adapter.py
└── tests/
    ├── unit/            # Test domain logic
    ├── integration/     # Test adapters
    └── e2e/            # Test full system
```

**Implementation**:

```python
# domain/models.py (Pure domain logic, no dependencies)
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum

class ViewType(Enum):
    FEATURE = "feature"
    CODE = "code"
    # ... 14 more

@dataclass
class UniversalItem:
    id: UUID
    title: str
    view_type: ViewType
    description: str
    created_at: datetime
    updated_at: datetime

    def update_title(self, new_title: str) -> None:
        """Business logic: update title"""
        if not new_title.strip():
            raise ValueError("Title cannot be empty")
        self.title = new_title
        self.updated_at = datetime.utcnow()
```

```python
# application/ports.py (Port definitions)
from typing import Protocol, Optional
from uuid import UUID
from domain.models import UniversalItem

class ItemRepositoryPort(Protocol):
    """Port for item persistence"""

    def save(self, item: UniversalItem) -> None: ...
    def find_by_id(self, item_id: UUID) -> Optional[UniversalItem]: ...
    def list_all(self) -> list[UniversalItem]: ...

class EventBusPort(Protocol):
    """Port for event publishing"""

    def publish(self, subject: str, payload: dict) -> None: ...
```

```python
# application/services.py (Application logic)
from uuid import uuid4
from datetime import datetime
from domain.models import UniversalItem, ViewType
from application.ports import ItemRepositoryPort, EventBusPort

class ItemService:
    """Application service for managing items"""

    def __init__(
        self,
        repository: ItemRepositoryPort,
        event_bus: EventBusPort
    ):
        self.repository = repository
        self.event_bus = event_bus

    def create_item(self, title: str, view_type: ViewType) -> UniversalItem:
        """Create new item"""
        item = UniversalItem(
            id=uuid4(),
            title=title,
            view_type=view_type,
            description="",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save via port (doesn't know about SQLite, PostgreSQL, etc.)
        self.repository.save(item)

        # Publish event via port (doesn't know about NATS, Redis, etc.)
        self.event_bus.publish(
            subject=f"TRACE_EVENTS.{view_type.value}.created",
            payload={"item_id": str(item.id), "title": title}
        )

        return item
```

```python
# infrastructure/repositories/sqlite_repository.py (Adapter)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from domain.models import UniversalItem
from application.ports import ItemRepositoryPort

class SQLiteItemRepository(ItemRepositoryPort):
    """SQLite adapter implementing repository port"""

    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")

    def save(self, item: UniversalItem) -> None:
        with Session(self.engine) as session:
            session.add(item)
            session.commit()

    def find_by_id(self, item_id: UUID) -> Optional[UniversalItem]:
        with Session(self.engine) as session:
            return session.query(UniversalItem).get(item_id)

    def list_all(self) -> list[UniversalItem]:
        with Session(self.engine) as session:
            return session.query(UniversalItem).all()
```

```python
# infrastructure/messaging/nats_adapter.py (Adapter)
import nats
from application.ports import EventBusPort

class NATSEventBus(EventBusPort):
    """NATS adapter implementing event bus port"""

    def __init__(self, nats_url: str):
        self.nc = None
        self.nats_url = nats_url

    async def connect(self):
        self.nc = await nats.connect(self.nats_url)

    def publish(self, subject: str, payload: dict) -> None:
        """Publish event to NATS"""
        if not self.nc:
            raise RuntimeError("Not connected to NATS")
        await self.nc.publish(subject, json.dumps(payload).encode())
```

```python
# infrastructure/web/fastmcp_adapter.py (Adapter)
from fastmcp import FastMCP
from application.services import ItemService
from domain.models import ViewType

class FastMCPAdapter:
    """FastMCP adapter for exposing items via MCP"""

    def __init__(self, item_service: ItemService):
        self.item_service = item_service
        self.mcp = FastMCP("trace")

    def setup_tools(self):
        @self.mcp.tool()
        def create_item(title: str, view_type: str) -> dict:
            """Create new item"""
            view = ViewType(view_type)
            item = self.item_service.create_item(title, view)
            return {
                "id": str(item.id),
                "title": item.title,
                "view_type": item.view_type.value
            }

        @self.mcp.tool()
        def get_item(item_id: str) -> dict:
            """Get item by ID"""
            from uuid import UUID
            item = self.item_service.get_item(UUID(item_id))
            if not item:
                raise ValueError("Item not found")
            return {
                "id": str(item.id),
                "title": item.title,
                "view_type": item.view_type.value
            }
```

```python
# main.py (Wiring)
from infrastructure.repositories.sqlite_repository import SQLiteItemRepository
from infrastructure.messaging.nats_adapter import NATSEventBus
from infrastructure.web.fastmcp_adapter import FastMCPAdapter
from application.services import ItemService

# Create adapters
repository = SQLiteItemRepository("trace.db")
event_bus = NATSEventBus("nats://localhost:4222")

# Create service with injected adapters
item_service = ItemService(
    repository=repository,
    event_bus=event_bus
)

# Create web adapter
mcp_adapter = FastMCPAdapter(item_service)
mcp_adapter.setup_tools()

# Run server
if __name__ == "__main__":
    mcp_adapter.mcp.run()
```

---

## PART 4: Clean Architecture

### 4.1 What is Clean Architecture?

**Creator**: Robert C. Martin (Uncle Bob), 2012
**Book**: "Clean Architecture: A Craftsman's Guide to Software Structure and Design" (2017)

**Goal**: Create systems that are:
- Framework-independent
- Testable
- UI-independent
- Database-independent
- Independent of external agencies

**Foundation**: Builds on Hexagonal Architecture, Onion Architecture, and SOLID principles.

### 4.2 The Dependency Rule

**The Core Principle**: Source code dependencies must point only inward.

**Rule**: Nothing in an inner circle can know anything about something in an outer circle.

```
┌─────────────────────────────────────────────────────────────┐
│            Frameworks & Drivers (Blue)                       │
│  Database, Web, UI, External APIs, Devices                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │     Interface Adapters (Green)                     │     │
│  │  Controllers, Presenters, Gateways, Repositories   │     │
│  │                                                     │     │
│  │  ┌────────────────────────────────────────────┐    │     │
│  │  │  Application Business Rules (Red)          │    │     │
│  │  │  Use Cases, Application Services           │    │     │
│  │  │                                             │    │     │
│  │  │  ┌────────────────────────────────────┐   │    │     │
│  │  │  │  Enterprise Business Rules (Yellow)│   │    │     │
│  │  │  │  Entities, Domain Model            │   │    │     │
│  │  │  │                                     │   │    │     │
│  │  │  │  Pure Business Logic               │   │    │     │
│  │  │  └────────────────────────────────────┘   │    │     │
│  │  │                                             │    │     │
│  │  └────────────────────────────────────────────┘    │     │
│  │                                                     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Dependencies flow INWARD only:
Blue → Green → Red → Yellow
(never reversed)
```

**Key Rules**:
1. Inner layers define interfaces
2. Outer layers implement interfaces
3. Names, functions, classes from outer layers NEVER mentioned in inner layers
4. Data formats from outer layers NEVER used in inner layers

### 4.3 The Four Layers

#### Layer 1: Entities (Domain)

**Purpose**: Enterprise-wide business rules

**Characteristics**:
- Pure business objects
- No external dependencies
- Most stable code
- Changes only when business rules change

**Example**:
```python
# entities/item.py (Clean Architecture - Domain Layer)
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum

class ViewType(Enum):
    FEATURE = "feature"
    CODE = "code"

@dataclass
class UniversalItem:
    """Domain entity - pure business logic"""
    id: UUID
    title: str
    view_type: ViewType
    description: str
    created_at: datetime
    updated_at: datetime

    def change_title(self, new_title: str) -> None:
        """Business rule: title cannot be empty"""
        if not new_title or not new_title.strip():
            raise ValueError("Title cannot be empty")

        self.title = new_title
        self.updated_at = datetime.utcnow()

    def is_recent(self) -> bool:
        """Business rule: item is recent if created within 24 hours"""
        age = datetime.utcnow() - self.created_at
        return age.total_seconds() < 86400  # 24 hours
```

#### Layer 2: Use Cases (Application)

**Purpose**: Application-specific business rules

**Characteristics**:
- Orchestrates flow of data
- Directs entities to use business rules
- Knows nothing about outer layers (database, web, etc.)
- Changes when application functionality changes

**Example**:
```python
# use_cases/create_item.py (Clean Architecture - Use Case Layer)
from uuid import uuid4
from datetime import datetime
from entities.item import UniversalItem, ViewType
from typing import Protocol

# Use case defines interfaces it needs (Dependency Inversion)
class ItemRepository(Protocol):
    """Interface for item persistence (port)"""
    def save(self, item: UniversalItem) -> None: ...

class EventPublisher(Protocol):
    """Interface for event publishing (port)"""
    def publish(self, event_type: str, data: dict) -> None: ...

class CreateItemUseCase:
    """Use case: Create new item"""

    def __init__(
        self,
        repository: ItemRepository,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, title: str, view_type: ViewType, created_by: str) -> UniversalItem:
        """Execute use case"""
        # Business logic: create entity
        item = UniversalItem(
            id=uuid4(),
            title=title,
            view_type=view_type,
            description="",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Use case orchestration: save via repository
        self.repository.save(item)

        # Use case orchestration: publish event
        self.event_publisher.publish(
            event_type="ItemCreated",
            data={
                "item_id": str(item.id),
                "title": title,
                "view_type": view_type.value,
                "created_by": created_by
            }
        )

        return item
```

#### Layer 3: Interface Adapters (Controllers, Presenters, Gateways)

**Purpose**: Convert data between use cases and external world

**Characteristics**:
- Adapts external format to internal format
- No business logic
- Changes when external interfaces change

**Example**:
```python
# adapters/controllers/item_controller.py (Clean Architecture - Adapter Layer)
from use_cases.create_item import CreateItemUseCase
from entities.item import ViewType
from typing import Dict, Any

class ItemController:
    """Controller: Adapts HTTP/MCP requests to use cases"""

    def __init__(self, create_item_use_case: CreateItemUseCase):
        self.create_item = create_item_use_case

    def handle_create_item_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt HTTP/MCP request to use case

        Input (from MCP):
        {
            "title": "New Feature",
            "view_type": "feature",
            "created_by": "user_123"
        }

        Output (to MCP):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "New Feature",
            "view_type": "feature",
            "status": "success"
        }
        """
        # Validate request
        if "title" not in request or "view_type" not in request:
            return {
                "status": "error",
                "message": "Missing required fields"
            }

        # Convert external format to internal format
        try:
            view_type = ViewType(request["view_type"])
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid view_type: {request['view_type']}"
            }

        # Execute use case
        try:
            item = self.create_item.execute(
                title=request["title"],
                view_type=view_type,
                created_by=request.get("created_by", "system")
            )

            # Convert internal format to external format
            return {
                "status": "success",
                "id": str(item.id),
                "title": item.title,
                "view_type": item.view_type.value,
                "created_at": item.created_at.isoformat()
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

```python
# adapters/repositories/sqlite_item_repository.py (Clean Architecture - Adapter Layer)
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import Session, declarative_base
from uuid import UUID
from entities.item import UniversalItem, ViewType
from datetime import datetime

Base = declarative_base()

# ORM Model (external format)
class ItemModel(Base):
    __tablename__ = 'items'
    id = Column(String, primary_key=True)
    title = Column(String)
    view_type = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Repository (implements interface from use case layer)
class SQLiteItemRepository:
    """Repository: Adapts SQLite to domain entities"""

    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)

    def save(self, item: UniversalItem) -> None:
        """Adapt domain entity to database model"""
        with Session(self.engine) as session:
            # Convert entity to ORM model
            model = ItemModel(
                id=str(item.id),
                title=item.title,
                view_type=item.view_type.value,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            session.add(model)
            session.commit()

    def find_by_id(self, item_id: UUID) -> UniversalItem | None:
        """Adapt database model to domain entity"""
        with Session(self.engine) as session:
            model = session.query(ItemModel).get(str(item_id))
            if not model:
                return None

            # Convert ORM model to entity
            return UniversalItem(
                id=UUID(model.id),
                title=model.title,
                view_type=ViewType(model.view_type),
                description=model.description,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
```

#### Layer 4: Frameworks & Drivers (Infrastructure)

**Purpose**: External tools and frameworks

**Characteristics**:
- Database engines
- Web frameworks
- UI frameworks
- External APIs
- Devices

**Example**:
```python
# infrastructure/fastmcp_server.py (Clean Architecture - Infrastructure Layer)
from fastmcp import FastMCP
from adapters.controllers.item_controller import ItemController
from typing import Dict, Any

class FastMCPServer:
    """FastMCP framework wrapper"""

    def __init__(self, item_controller: ItemController):
        self.item_controller = item_controller
        self.mcp = FastMCP("trace")
        self._setup_tools()

    def _setup_tools(self):
        @self.mcp.tool()
        def create_item(
            title: str,
            view_type: str,
            created_by: str = "system"
        ) -> Dict[str, Any]:
            """MCP tool for creating items"""
            return self.item_controller.handle_create_item_request({
                "title": title,
                "view_type": view_type,
                "created_by": created_by
            })

    def run(self):
        """Start FastMCP server"""
        self.mcp.run()
```

### 4.4 Dependency Inversion in Practice

**Problem**: Use cases need repositories, but can't depend on concrete implementations.

**Solution**: Use cases define interfaces; adapters implement them.

```python
# Layer 2: Use Case (defines interface)
class ItemRepository(Protocol):
    """Interface defined by use case"""
    def save(self, item: UniversalItem) -> None: ...

class CreateItemUseCase:
    def __init__(self, repository: ItemRepository):
        self.repository = repository  # Depends on interface, not implementation
```

```python
# Layer 3: Adapter (implements interface)
class SQLiteItemRepository(ItemRepository):  # Implements interface from inner layer
    """Concrete implementation"""
    def save(self, item: UniversalItem) -> None:
        # SQLite-specific code
        pass
```

```python
# Wiring (Composition Root)
# Outer layer knows about all layers
repository = SQLiteItemRepository("trace.db")  # Concrete implementation
use_case = CreateItemUseCase(repository)        # Injected

# Dependency points inward:
# SQLiteItemRepository → ItemRepository (interface) ← CreateItemUseCase
```

### 4.5 Clean Architecture Benefits for Trace

**Testability**:
```python
# Test use case without database
def test_create_item_use_case():
    # Fake repository (no database needed)
    fake_repo = InMemoryItemRepository()
    fake_events = InMemoryEventPublisher()

    use_case = CreateItemUseCase(fake_repo, fake_events)

    item = use_case.execute("Test", ViewType.FEATURE, "user_1")

    assert item.title == "Test"
    assert len(fake_repo.items) == 1
    assert len(fake_events.events) == 1
```

**Flexibility**:
```python
# Easy to swap implementations
# Development
use_case = CreateItemUseCase(
    repository=SQLiteRepository("dev.db"),
    events=ConsoleEventPublisher()  # Print to console
)

# Production
use_case = CreateItemUseCase(
    repository=PostgreSQLRepository(url),
    events=NATSEventPublisher(nats_url)
)
```

**Maintainability**:
- Business logic isolated in entities
- Framework changes don't affect business logic
- Database changes don't affect business logic
- Can delay technical decisions

---

## PART 5: Microservices Patterns

### 5.1 Domain-Driven Design (DDD) Fundamentals

**Inventor**: Eric Evans (2003 book)

**Goal**: Align software structure with business domain.

#### Strategic DDD: Bounded Contexts

**Definition**: Explicit boundaries around domain models.

**In Trace**:
```
┌──────────────────────────────────────────────────────────┐
│                   TRACE SYSTEM                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Item Management │  │   Versioning    │              │
│  │  Bounded Context│  │ Bounded Context │              │
│  │                 │  │                 │              │
│  │ - UniversalItem │  │ - Commit        │              │
│  │ - Link          │  │ - Snapshot      │              │
│  │ - View          │  │ - Baseline      │              │
│  └────────┬────────┘  └────────┬────────┘              │
│           │                     │                       │
│           └──────────┬──────────┘                       │
│                      │                                  │
│  ┌─────────────────┴──────────────┐                    │
│  │      PM Planning                │                    │
│  │    Bounded Context              │                    │
│  │                                 │                    │
│  │ - WBSTree                       │                    │
│  │ - TaskDAG                       │                    │
│  │ - CriticalPath                  │                    │
│  └─────────────────┬───────────────┘                    │
│                    │                                    │
│  ┌─────────────────┴───────────────┐                    │
│  │     Verification                │                    │
│  │   Bounded Context               │                    │
│  │                                 │                    │
│  │ - AcceptanceCriterion           │                    │
│  │ - VerificationProof             │                    │
│  │ - MerkleTree                    │                    │
│  └─────────────────────────────────┘                    │
│                                                          │
└──────────────────────────────────────────────────────────┘

Note: For monolith (trace), bounded contexts are modules, not services
```

**Key Points**:
- Each context has its own model
- Same concept may exist in multiple contexts (e.g., "Item")
- Contexts communicate via well-defined interfaces
- Helps manage complexity

#### Tactical DDD: Building Blocks

**Entities**:
```python
# Entity: Has identity, lifecycle
class UniversalItem:
    id: UUID  # Identity
    title: str
    # ... other attributes

    def __eq__(self, other):
        # Identity-based equality
        return isinstance(other, UniversalItem) and self.id == other.id
```

**Value Objects**:
```python
# Value Object: Immutable, no identity, equality based on attributes
@dataclass(frozen=True)
class Link:
    source_id: UUID
    target_id: UUID
    link_type: LinkType

    # Equality based on all attributes
    # No identity - two links with same attributes are identical
```

**Aggregates**:
```python
# Aggregate: Cluster of entities with one root
class Commit:
    """Aggregate root"""
    id: str  # Root identity
    parent_commits: List[str]
    trees: Dict[ViewType, Tree]  # Owned entities
    author: str
    timestamp: datetime

    def add_tree(self, view_type: ViewType, tree: Tree):
        """Aggregate enforces consistency"""
        if view_type in self.trees:
            raise ValueError("Tree already exists for view")
        self.trees[view_type] = tree

    # Outside world accesses trees only through Commit (root)
```

**Domain Services**:
```python
# Domain Service: Business logic that doesn't belong to entity
class CriticalPathCalculator:
    """Service: Calculate critical path from DAG"""

    def calculate(self, dag: TaskDAG) -> List[UUID]:
        # Complex algorithm spanning multiple entities
        earliest = self._forward_pass(dag)
        latest = self._backward_pass(dag, earliest)
        slack = self._calculate_slack(earliest, latest)
        return [task_id for task_id, s in slack.items() if s == 0]
```

**Domain Events**:
```python
# Domain Event: Something happened in domain
@dataclass(frozen=True)
class ItemCreated:
    """Event: Item was created"""
    item_id: UUID
    title: str
    view_type: ViewType
    created_at: datetime
    created_by: str

# Events published when domain state changes
class ItemService:
    def create_item(self, ...):
        item = UniversalItem(...)
        self.repository.save(item)

        # Publish domain event
        event = ItemCreated(
            item_id=item.id,
            title=item.title,
            view_type=item.view_type,
            created_at=item.created_at,
            created_by=item.created_by
        )
        self.event_publisher.publish(event)
```

### 5.2 CQRS (Command Query Responsibility Segregation)

**Principle**: Separate read and write models.

**Why**: Different optimization needs for reads vs writes.

**In Trace**:

```
┌─────────────────────────────────────────────────────────────┐
│                      WRITE MODEL                             │
│  (Optimized for consistency and business rules)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Commands                          Event Store               │
│  ├─ CreateItem          ────────▶  ItemCreated              │
│  ├─ UpdateItem          ────────▶  ItemUpdated              │
│  └─ DeleteItem          ────────▶  ItemDeleted              │
│                                                              │
│  Domain Model                                                │
│  - UniversalItem (full validation, business rules)          │
│  - Commit (complex version control logic)                   │
│                                                              │
└───────────────────────┬────────────────────────────────────┘
                        │
                        │ Events Published
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      READ MODEL                              │
│  (Optimized for queries and performance)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Queries                           Read Database             │
│  ├─ ListItems            ────────▶ Denormalized views       │
│  ├─ GetItem              ────────▶ Cached aggregates        │
│  ├─ SearchItems          ────────▶ Indexed for search       │
│  └─ GetCriticalPath      ────────▶ Pre-computed graphs      │
│                                                              │
│  Projections (Event Handlers)                                │
│  - ItemProjection: Updates read model from events           │
│  - GraphProjection: Builds query-optimized graph            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
# Write Side (Commands)
class CreateItemCommand:
    title: str
    view_type: ViewType
    created_by: str

class ItemCommandHandler:
    def handle(self, command: CreateItemCommand):
        # Complex validation and business rules
        item = UniversalItem(...)

        # Save to write database (event store)
        self.event_store.append(ItemCreated(...))

        # Publish event
        self.event_bus.publish(ItemCreated(...))

# Read Side (Queries)
class ListItemsQuery:
    view_type: Optional[ViewType]
    limit: int

class ItemQueryHandler:
    def handle(self, query: ListItemsQuery):
        # Query optimized read database
        # No business logic, just data retrieval
        return self.read_db.query("""
            SELECT id, title, view_type, status
            FROM items_read_model
            WHERE view_type = ?
            LIMIT ?
        """, query.view_type, query.limit)

# Projection (Updates read model from events)
class ItemProjection:
    def on_item_created(self, event: ItemCreated):
        # Update read database
        self.read_db.insert("""
            INSERT INTO items_read_model
            (id, title, view_type, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, event.item_id, event.title, ...)

    def on_item_updated(self, event: ItemUpdated):
        self.read_db.update(...)

    def on_item_deleted(self, event: ItemDeleted):
        self.read_db.delete(...)
```

**Benefits**:
- Read model optimized for queries (denormalized, cached)
- Write model optimized for consistency (normalized, validated)
- Can scale reads and writes independently
- Perfect for event sourcing

### 5.3 Event Sourcing

**Principle**: Store state as sequence of events, not current state.

**In Trace**: Already designed for versioning!

```
Traditional Storage:
  items table: [id, title, view_type, status, ...]
  Only current state stored

Event Sourcing:
  events table: [event_id, event_type, aggregate_id, data, timestamp, ...]
  All state changes stored

To get current state: Replay all events
```

**Implementation**:

```python
# Event Store
class EventStore:
    def append(self, event: DomainEvent) -> None:
        """Append event to immutable log"""
        self.db.execute("""
            INSERT INTO events
            (event_id, event_type, aggregate_id, data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, event.id, event.type, event.aggregate_id,
            json.dumps(event.data), event.timestamp)

    def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        """Get all events for aggregate"""
        rows = self.db.query("""
            SELECT event_id, event_type, data, timestamp
            FROM events
            WHERE aggregate_id = ?
            ORDER BY timestamp
        """, aggregate_id)

        return [self._deserialize(row) for row in rows]

# Aggregate reconstructed from events
class ItemAggregate:
    def __init__(self, item_id: UUID, event_store: EventStore):
        self.id = item_id
        self.version = 0
        self.state = None

        # Replay all events to reconstruct state
        events = event_store.get_events(item_id)
        for event in events:
            self._apply(event)

    def _apply(self, event: DomainEvent):
        """Apply event to state"""
        if isinstance(event, ItemCreated):
            self.state = UniversalItem(
                id=event.item_id,
                title=event.title,
                view_type=event.view_type,
                ...
            )
        elif isinstance(event, ItemTitleUpdated):
            self.state.title = event.new_title
            self.state.updated_at = event.timestamp
        elif isinstance(event, ItemDeleted):
            self.state = None

        self.version += 1
```

**Benefits**:
- Complete audit trail (already in trace design!)
- Time-travel (already in trace design!)
- Can rebuild state at any point in time
- Natural fit with CQRS

**Optimization: Snapshots**:
```python
# Avoid replaying 10,000 events every time
class SnapshotStore:
    def save_snapshot(self, aggregate_id: UUID, state: Any, version: int):
        """Save snapshot every N events"""
        pass

    def load_snapshot(self, aggregate_id: UUID) -> Tuple[Any, int]:
        """Load latest snapshot"""
        pass

# Optimized aggregate loading
class ItemAggregate:
    def __init__(self, item_id: UUID, event_store: EventStore, snapshot_store: SnapshotStore):
        # Load snapshot
        self.state, self.version = snapshot_store.load_snapshot(item_id)

        # Replay events since snapshot
        events = event_store.get_events_since(item_id, self.version)
        for event in events:
            self._apply(event)
```

**Already in Trace Design**: Hybrid event sourcing + snapshots (every 100 events)!

### 5.4 Saga Pattern (Distributed Transactions)

**Problem**: Need to coordinate transactions across multiple bounded contexts.

**Traditional Solution**: Distributed transactions (2PC) - complex, slow, brittle.

**Saga Solution**: Sequence of local transactions, coordinated by events.

**Two Styles**:

**Choreography**: Each service publishes events, others react
```
CreateItem ────▶ ItemCreated Event
                     │
                     ├──▶ Version Service: Creates first commit
                     ├──▶ Planning Service: Creates initial WBS
                     └──▶ Notification Service: Sends notification

Decentralized, loose coupling
```

**Orchestration**: Central coordinator manages flow
```
ItemCreationSaga (Orchestrator)
  │
  ├─ 1. Create item in Item Service
  │      Success? → Continue
  │      Failure? → Done (nothing to compensate)
  │
  ├─ 2. Create commit in Version Service
  │      Success? → Continue
  │      Failure? → Compensate: Delete item
  │
  └─ 3. Create WBS in Planning Service
         Success? → Done
         Failure? → Compensate: Delete commit, delete item

Centralized, explicit flow
```

**Implementation (Choreography)**:

```python
# In trace: Use NATS for saga coordination
class ItemCreationSaga:
    """Saga for creating item across contexts"""

    def __init__(self, nats_client):
        self.nats = nats_client

    async def start(self, item_data: dict):
        """Start saga"""
        # Step 1: Create item
        item_id = await self._create_item(item_data)

        # Publish event (triggers next steps)
        await self.nats.publish(
            "TRACE_SAGA.item_created",
            {"saga_id": str(uuid4()), "item_id": str(item_id)}
        )

# Version Service listens for item_created event
class VersionServiceSagaHandler:
    async def on_item_created(self, event):
        """React to item creation"""
        try:
            # Step 2: Create first commit
            commit_id = await self.create_initial_commit(event.item_id)

            # Publish success event
            await self.nats.publish(
                "TRACE_SAGA.commit_created",
                {"saga_id": event.saga_id, "commit_id": commit_id}
            )
        except Exception as e:
            # Publish failure event (triggers compensation)
            await self.nats.publish(
                "TRACE_SAGA.commit_failed",
                {"saga_id": event.saga_id, "error": str(e)}
            )

# Item Service listens for failure events
class ItemServiceSagaHandler:
    async def on_commit_failed(self, event):
        """Compensate: delete item"""
        await self.delete_item(event.item_id)
```

**For Trace**: Orchestration likely better (explicit flow, easier debugging).

### 5.5 Microservices Patterns Summary

For **Trace** (monolith with bounded contexts):

**Use**:
- ✅ DDD Bounded Contexts (as modules)
- ✅ CQRS (separate read/write models for versioning)
- ✅ Event Sourcing (already designed!)
- ✅ Domain Events (NATS for coordination)

**Don't Use** (yet):
- ❌ Microservices (monolith is fine for start)
- ❌ Saga (not needed within monolith)
- ❌ Service Mesh (not needed for monolith)

**Future**: If trace scales massively, can split into microservices along bounded context boundaries.

---

## PART 6: Synthesis & Recommendations for Trace

### 6.1 Recommended Architecture

**Combine All Patterns**:

```
┌─────────────────────────────────────────────────────────────┐
│             SPECIFICATION LAYER (OpenSpec)                   │
│  openspec/specs/ - Truth                                     │
│  openspec/changes/ - Proposals                               │
│  AGENTS.md - AI instructions                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│             TEST LAYER (TDD Red-Green-Refactor)              │
│  tests/unit/ - Domain logic                                  │
│  tests/integration/ - Adapters                               │
│  tests/e2e/ - Full workflows                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│         CLEAN ARCHITECTURE LAYERS                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DOMAIN (Entities - DDD Building Blocks)             │  │
│  │  - UniversalItem (Entity)                            │  │
│  │  - Link (Value Object)                               │  │
│  │  - Commit (Aggregate Root)                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │  USE CASES (Application Business Rules)             │   │
│  │  - CreateItemUseCase                                 │   │
│  │  - CommitChangesUseCase                              │   │
│  │  - CalculateCriticalPathUseCase                      │   │
│  │  - VerifyAcceptanceCriterionUseCase                  │   │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │  INTERFACE ADAPTERS (Hexagonal Ports)               │   │
│  │  - Controllers (MCP, CLI, TUI)                       │   │
│  │  - Repositories (SQLite, PostgreSQL)                 │   │
│  │  - Event Publishers (NATS)                           │   │
│  │  - Verification Engines (IntentGuard, Z3)            │   │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │  FRAMEWORKS & DRIVERS                                │   │
│  │  - FastMCP                                           │   │
│  │  - SQLAlchemy                                        │   │
│  │  - NATS JetStream                                    │   │
│  │  - Typer + Rich + Textual                            │   │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│         MICROSERVICES PATTERNS (within monolith)             │
│  - DDD Bounded Contexts (as modules)                         │
│  - CQRS (separate read/write for versioning)                │
│  - Event Sourcing (with snapshots)                           │
│  - Domain Events (via NATS)                                  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Directory Structure

```
trace/
├── openspec/                    # Specification layer
│   ├── AGENTS.md
│   ├── constitution.md
│   ├── specs/
│   ├── changes/
│   └── archive/
│
├── domain/                      # Clean Architecture: Entities
│   ├── models/                  # DDD: Entities, Value Objects
│   │   ├── item.py
│   │   ├── commit.py
│   │   ├── wbs.py
│   │   └── criterion.py
│   ├── services/                # DDD: Domain Services
│   │   ├── critical_path.py
│   │   └── consistency.py
│   └── events/                  # DDD: Domain Events
│       ├── item_events.py
│       └── version_events.py
│
├── application/                 # Clean Architecture: Use Cases
│   ├── ports/                   # Hexagonal: Port interfaces
│   │   ├── repositories.py
│   │   ├── event_bus.py
│   │   └── verification.py
│   ├── use_cases/
│   │   ├── create_item.py
│   │   ├── commit_changes.py
│   │   └── verify_criterion.py
│   └── queries/                 # CQRS: Query handlers
│       ├── list_items.py
│       └── get_critical_path.py
│
├── infrastructure/              # Clean Architecture: Adapters
│   ├── persistence/             # Hexagonal: Repository adapters
│   │   ├── sqlite/              # Write model (event store)
│   │   │   ├── event_store.py
│   │   │   └── snapshot_store.py
│   │   └── read_model/          # CQRS: Read database
│   │       └── projections.py
│   ├── messaging/               # Hexagonal: Event bus adapter
│   │   └── nats_adapter.py
│   ├── verification/            # Hexagonal: Verification adapters
│   │   ├── intentguard.py
│   │   └── z3_adapter.py
│   └── web/                     # Hexagonal: Controller adapters
│       ├── fastmcp_adapter.py
│       ├── cli_adapter.py
│       └── tui_adapter.py
│
├── tests/                       # TDD: Test suite
│   ├── unit/                    # Test domain logic
│   ├── integration/             # Test adapters
│   └── e2e/                     # Test full workflows
│
└── server.py                    # Composition root (wiring)
```

### 6.3 Implementation Workflow

**For Each Feature**:

```
1. SPEC (OpenSpec)
   ├─ Write openspec/changes/<id>/proposal.md
   ├─ Write openspec/changes/<id>/specs/<feature>.md
   └─ Review & approve

2. TEST (TDD Red)
   ├─ Write failing tests
   │  ├─ tests/unit/domain/test_<entity>.py
   │  ├─ tests/unit/application/test_<use_case>.py
   │  └─ tests/integration/test_<adapter>.py
   └─ Run: All tests fail ✓

3. DOMAIN (Clean Architecture Layer 1)
   ├─ Implement entities (domain/models/)
   ├─ Implement value objects
   ├─ Implement aggregates
   └─ Run tests: Some pass ✓

4. USE CASES (Clean Architecture Layer 2)
   ├─ Define ports (application/ports/)
   ├─ Implement use cases (application/use_cases/)
   └─ Run tests: More pass ✓

5. ADAPTERS (Clean Architecture Layer 3)
   ├─ Implement repositories (infrastructure/persistence/)
   ├─ Implement event bus (infrastructure/messaging/)
   ├─ Implement controllers (infrastructure/web/)
   └─ Run tests: All pass ✓

6. REFACTOR (TDD Green→Refactor)
   ├─ Clean up code
   ├─ Remove duplication
   ├─ Improve names
   └─ Run tests: Still all pass ✓

7. INTEGRATE (Composition Root)
   ├─ Wire adapters in server.py
   ├─ Run e2e tests
   └─ Deploy

8. ARCHIVE (OpenSpec)
   ├─ Move specs to openspec/specs/
   ├─ Archive change to openspec/archive/
   └─ Update changelog
```

### 6.4 Key Principles Summary

**Spec-Driven Development**:
- ✅ All changes start with OpenSpec proposal
- ✅ Specs define acceptance criteria
- ✅ AI agents reference specs for implementation
- ✅ Specs version-controlled and reviewed

**Test-Driven Development**:
- ✅ Write tests before implementation
- ✅ Red → Green → Refactor cycle
- ✅ 80% test coverage minimum
- ✅ Test pyramid: 60% unit, 30% integration, 10% e2e

**Hexagonal Architecture**:
- ✅ Ports define interfaces
- ✅ Adapters implement interfaces
- ✅ Domain independent of infrastructure
- ✅ Easy to test, easy to change

**Clean Architecture**:
- ✅ Dependency rule: inward only
- ✅ Entities → Use Cases → Adapters → Frameworks
- ✅ Inner layers define interfaces
- ✅ Outer layers implement interfaces

**DDD Patterns**:
- ✅ Bounded contexts as modules
- ✅ Entities, Value Objects, Aggregates
- ✅ Domain events via NATS
- ✅ Ubiquitous language

**CQRS**:
- ✅ Separate read/write models for versioning
- ✅ Write: Event store with full validation
- ✅ Read: Denormalized views for queries
- ✅ Projections update read model from events

**Event Sourcing**:
- ✅ Already designed for trace versioning!
- ✅ Events stored in immutable log
- ✅ Snapshots every 100 events
- ✅ Time-travel by replaying events

---

## PART 7: Conclusion & Next Steps

### 7.1 Complete Technology Stack

**Methodology**:
- Spec-Driven: OpenSpec
- Test-Driven: pytest + Hypothesis
- Architecture: Clean + Hexagonal + DDD

**Frameworks**:
- Server: FastMCP (stdio)
- CLI: Typer + Rich
- TUI: Textual
- Database: SQLAlchemy

**Infrastructure**:
- Storage: SQLite → PostgreSQL
- Messaging: NATS JetStream
- Verification: IntentGuard + Z3
- Quality: Ruff, mypy, Bandit, coverage.py

### 7.2 Implementation Priority

**Phase 1**: Foundation with Clean Architecture + Hexagonal
- Domain models (entities, value objects)
- Use cases with ports
- SQLite adapter
- Basic NATS adapter
- TDD from day 1
- OpenSpec change-001 to change-004

**Phase 2**: Versioning with Event Sourcing + CQRS
- Event store implementation
- Snapshot system
- Read model projections
- Git-style commit DAG
- Time-travel engine
- OpenSpec change-005 to change-008

**Phase 3**: PM Planning with DDD
- Bounded context: Planning
- WBS aggregate
- TaskDAG aggregate
- Critical path domain service
- JetStream coordination
- OpenSpec change-009 to change-012

**Phase 4**: Verification with Hexagonal Adapters
- IntentGuard adapter
- Z3 adapter
- Hybrid verification use case
- Cryptographic proof domain service
- Merkle tree aggregate
- OpenSpec change-013 to change-016

**Phase 5**: Polish
- TUI adapter
- Optimization
- Documentation
- OpenSpec change-017 to change-021

### 7.3 Key Takeaways

**Spec-Driven Development**:
- Prevents "vibe coding"
- Provides structure for AI assistance
- Aligns team through shared specifications
- 20-40% spec time, 50-80% faster implementation

**Test-Driven Development**:
- Design driver, not just testing
- Red-Green-Refactor cycle
- Safety net for refactoring
- Faster feedback than manual testing

**Hexagonal Architecture**:
- Domain independent of infrastructure
- Easy to test (fake adapters)
- Easy to change (swap adapters)
- Delays technical decisions

**Clean Architecture**:
- Dependency rule keeps code maintainable
- Inner layers stable, outer layers flexible
- Framework-independent business logic
- Testable without external dependencies

**DDD + CQRS + Event Sourcing**:
- Aligns software with business domain
- CQRS optimizes reads and writes separately
- Event Sourcing provides audit trail and time-travel
- Perfect fit for trace versioning system

### 7.4 Resources

**Books**:
- "Test Driven Development: By Example" - Kent Beck
- "Clean Architecture" - Robert C. Martin
- "Domain-Driven Design" - Eric Evans
- "Implementing Domain-Driven Design" - Vaughn Vernon

**Online**:
- Martin Fowler's blog: https://martinfowler.com/
- Alistair Cockburn's Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Microservices.io patterns: https://microservices.io/patterns/

**Tools**:
- OpenSpec: https://github.com/Fission-AI/OpenSpec
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
- GitHub Spec Kit: https://github.com/github/spec-kit

---

This research document provides the complete foundation for implementing trace using modern best practices in spec-driven development, test-driven development, and architectural patterns. All patterns work together synergistically to create a maintainable, testable, and evolvable system.
