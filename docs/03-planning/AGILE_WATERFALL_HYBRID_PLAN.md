# Trace: Complete Agile-Waterfall Hybrid Implementation Plan
## OpenSpec + Spec Kit Driven Development for Backend/CLI/State System

**Document Version**: 1.0.0
**Date**: 2025-11-20
**Methodology**: Hybrid Agile-Waterfall with OpenSpec Specification Management
**Duration**: 20 weeks (5 phases × 4 weeks)

---

## Executive Summary

This document provides a comprehensive end-to-end implementation plan for the trace multi-view PM system, combining:
- **Waterfall Structure**: Clear phase gates, comprehensive upfront design, formal reviews
- **Agile Execution**: 2-week sprints, continuous integration, working software each sprint
- **OpenSpec Methodology**: Spec-driven development with formal change proposals
- **Spec Kit Principles**: Structured specifications → plans → tasks workflow

### Methodology Hybrid

```
┌─────────────────────────────────────────────────────────────────┐
│                     WATERFALL STRUCTURE                          │
│  Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Production   │
│     ↓         ↓         ↓         ↓         ↓                    │
│   Gate 1   Gate 2   Gate 3   Gate 4   Gate 5                    │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AGILE SPRINTS (within each phase)             │
│  Sprint 1 (2wks) → Sprint 2 (2wks) → Sprint 3 (2wks) → ...      │
│     ↓                ↓                 ↓                          │
│  Working SW      Working SW       Working SW                     │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    OPENSPEC WORKFLOW                             │
│  Propose → Review → Implement → Archive → Repeat                 │
│  (specs/) ← (changes/<id>/) → (implemented) → (archived)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Project Structure & Organization

### 1.1 OpenSpec Directory Structure

```
trace/
├── openspec/
│   ├── AGENTS.md                    # AI assistant instructions
│   ├── constitution.md              # Project principles & standards
│   ├── specs/                       # Current truth (approved specs)
│   │   ├── architecture.md
│   │   ├── data-model.md
│   │   ├── versioning.md
│   │   ├── pm-planning.md
│   │   ├── verification.md
│   │   ├── nats-integration.md
│   │   └── quality-metrics.md
│   ├── changes/                     # Proposed changes (active work)
│   │   ├── 001-foundation/
│   │   │   ├── proposal.md
│   │   │   ├── tasks.md
│   │   │   ├── design.md
│   │   │   └── specs/
│   │   │       ├── data-model.md
│   │   │       └── storage-layer.md
│   │   └── 002-versioning/
│   │       ├── proposal.md
│   │       ├── tasks.md
│   │       └── specs/
│   └── archive/                     # Completed changes
│       └── 001-foundation/
├── server.py                        # FastMCP server entry point
├── tools/                           # MCP tool implementations
│   ├── item_tools.py
│   ├── version_tools.py
│   └── plan_tools.py
├── services/                        # Business logic
│   ├── item_service.py
│   ├── version_service.py
│   └── dag_service.py
├── infrastructure/                  # Adapters & infrastructure
│   ├── storage/
│   │   ├── repositories.py
│   │   └── event_store.py
│   ├── nats/
│   │   ├── client.py
│   │   └── streams.py
│   └── verification/
│       ├── nl_engine.py
│       └── formal_verifier.py
├── cli/                            # Typer CLI
│   ├── main.py
│   └── commands/
├── tests/                          # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── pyproject.toml
└── README.md
```

### 1.2 Constitution Document (Project Principles)

```markdown
# Trace Project Constitution

## Core Principles

1. **Module Size Discipline**: All modules ≤350 lines (500 hard limit)
2. **Test-First Development**: Write tests before implementation
3. **Type Safety**: Full type hints, mypy strict mode
4. **Performance Commitments**: Meet all latency targets
5. **No Technical Debt**: Complete each phase fully before proceeding
6. **Specification-Driven**: All changes start with OpenSpec proposal
7. **Verification-First**: All features have acceptance criteria

## Technology Constraints

- **Runtime**: Python 3.12+
- **Framework**: FastMCP for MCP server
- **CLI**: Typer + Rich (no other CLI frameworks)
- **Database**: SQLite (start) → PostgreSQL (scale)
- **Messaging**: NATS JetStream (no Redis, no Kafka)
- **Testing**: pytest, Hypothesis, coverage.py
- **Linting**: Ruff (no other linters)
- **Type Checking**: mypy strict mode

## Quality Gates

- **Coverage**: ≥80% line, ≥70% branch
- **Performance**: All operations meet targets
- **Security**: Zero high-severity issues (Bandit)
- **Complexity**: Cyclomatic complexity ≤10
- **Documentation**: All public APIs documented

## Change Management

- All architectural changes require OpenSpec proposal
- All breaking changes require phase gate approval
- All new features require acceptance criteria
- All performance changes require benchmarks
```

---

## 2. Waterfall Phase Structure

### 2.1 Five Major Phases with Gates

```
Phase 1: Foundation (Weeks 1-4)
  ↓ Gate 1: Foundation Complete
Phase 2: Versioning & History (Weeks 5-8)
  ↓ Gate 2: Versioning Complete
Phase 3: PM Planning Features (Weeks 9-12)
  ↓ Gate 3: PM Planning Complete
Phase 4: Verification & Quality (Weeks 13-16)
  ↓ Gate 4: Verification Complete
Phase 5: Integration & Polish (Weeks 17-20)
  ↓ Gate 5: Production Ready
PRODUCTION DEPLOYMENT
```

### 2.2 Phase Gate Criteria

Each phase must pass ALL gate criteria before proceeding:

#### Gate 1: Foundation Complete
- [ ] All data models implemented and tested
- [ ] SQLite database with all tables
- [ ] Event sourcing infrastructure working
- [ ] CLI commands functional
- [ ] NATS basic integration complete
- [ ] Test coverage ≥80%
- [ ] All specs approved and archived
- [ ] Performance: Item creation <200ms

#### Gate 2: Versioning Complete
- [ ] Git-style commit structure working
- [ ] Snapshot system operational
- [ ] Semantic versioning automated
- [ ] Time-travel engine functional
- [ ] Diff engine accurate
- [ ] Test coverage ≥80%
- [ ] All specs approved and archived
- [ ] Performance: Time-travel <500ms

#### Gate 3: PM Planning Complete
- [ ] WBS auto-generation working
- [ ] PERT critical path calculation accurate
- [ ] JetStream work queues operational
- [ ] DAG execution distributed
- [ ] Schedule optimization functional
- [ ] Test coverage ≥80%
- [ ] All specs approved and archived
- [ ] Performance: Critical path <2s for 1000 tasks

#### Gate 4: Verification Complete
- [ ] IntentGuard integrated and working
- [ ] Hybrid verification operational
- [ ] Cryptographic proofs generated
- [ ] Merkle tree audit trail functional
- [ ] Quality metrics dashboard operational
- [ ] Test coverage ≥80%
- [ ] All specs approved and archived
- [ ] Performance: Verification <5s per criterion

#### Gate 5: Production Ready
- [ ] Multi-sig approval working
- [ ] Continuous verification operational
- [ ] TUI complete and functional
- [ ] All performance targets met
- [ ] Complete documentation
- [ ] Security audit passed
- [ ] Load testing passed (1000+ agents)
- [ ] Production deployment tested

---

## 3. Agile Sprint Structure (Within Phases)

### 3.1 Sprint Cadence

- **Sprint Duration**: 2 weeks
- **Sprints per Phase**: 2 sprints (4 weeks per phase)
- **Total Sprints**: 10 sprints (20 weeks)

### 3.2 Sprint Ceremonies

#### Daily (Async Standups)
- What did I accomplish yesterday?
- What will I accomplish today?
- Any blockers?

#### Sprint Planning (Day 1)
- Duration: 2 hours
- Review OpenSpec proposals for sprint
- Break proposals into tasks
- Estimate story points
- Commit to sprint backlog

#### Sprint Review (Day 10)
- Duration: 1 hour
- Demo working software
- Review acceptance criteria
- Collect feedback
- Update specs if needed

#### Sprint Retrospective (Day 10)
- Duration: 1 hour
- What went well?
- What could improve?
- Action items for next sprint

#### Backlog Refinement (Mid-Sprint)
- Duration: 1 hour
- Review upcoming proposals
- Break down large proposals
- Clarify requirements
- Prepare for next sprint

---

## 4. OpenSpec Workflow Integration

### 4.1 Change Proposal Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPENSPEC CHANGE LIFECYCLE                     │
└─────────────────────────────────────────────────────────────────┘

1. DRAFT PROPOSAL
   ├─ Create openspec/changes/<id>/
   ├─ Write proposal.md (what, why, scope)
   ├─ Write design.md (how, architecture)
   ├─ Write tasks.md (implementation steps)
   └─ Write specs/*.md (requirements & scenarios)

2. REVIEW & ALIGN
   ├─ Technical review by team
   ├─ Architecture review if needed
   ├─ Update proposal based on feedback
   └─ Approval from stakeholders

3. IMPLEMENT TASKS
   ├─ Break tasks into sprint backlog
   ├─ Implement with TDD
   ├─ Reference change ID in commits
   └─ Continuous integration

4. ARCHIVE & MERGE
   ├─ All tasks complete and tested
   ├─ Merge specs into openspec/specs/
   ├─ Move change to openspec/archive/
   └─ Update changelog
```

### 4.2 Proposal Template

```markdown
# Proposal: <Feature Name>

**Change ID**: <nnn>
**Status**: Draft | Review | Approved | Implemented | Archived
**Created**: YYYY-MM-DD
**Author**: <name>
**Sprint**: <sprint number>

## Problem Statement

What problem does this solve? Why is it needed?

## Proposed Solution

High-level solution overview.

## Scope

### In Scope
- Feature A
- Feature B

### Out of Scope
- Feature C (deferred to change-<id>)

## Architecture Impact

Does this affect:
- [ ] Data model
- [ ] Storage layer
- [ ] Event sourcing
- [ ] NATS integration
- [ ] CLI commands
- [ ] Performance targets

## Dependencies

- Requires: change-<id>
- Blocks: change-<id>

## Acceptance Criteria

1. Criterion 1
2. Criterion 2

## Risks

- Risk 1: mitigation strategy
- Risk 2: mitigation strategy

## Estimated Effort

- Story Points: <n>
- Sprints: <n>
```

### 4.3 Spec Format

```markdown
# Spec: <Feature Name>

## ADDED Requirements

### Requirement: <Requirement Title>

Description of requirement.

#### Scenario: <Scenario Name>

**Given** initial conditions
**When** action occurs
**Then** expected outcome

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

#### Scenario: <Another Scenario>

...

## MODIFIED Requirements

### Requirement: <Modified Requirement>

**Before**: Old behavior
**After**: New behavior

#### Scenario: <Updated Scenario>

...

## REMOVED Requirements

### Requirement: <Deprecated Requirement>

**Reason**: Why this is being removed
**Migration**: How to migrate existing usage
```

---

## 5. Detailed Phase Plans

### PHASE 1: Foundation (Weeks 1-4)

#### Phase Overview

**Goal**: Establish core infrastructure, data model, storage, and basic CLI

**OpenSpec Changes**:
- `change-001-data-model`: Define UniversalItem and all enums
- `change-002-storage-layer`: Implement repositories and event store
- `change-003-cli-foundation`: Create Typer CLI with basic commands
- `change-004-nats-basic`: Integrate NATS for basic pub/sub

#### Sprint 1 (Weeks 1-2): Data Model & Storage

**Sprint Goal**: Complete data model and SQLite storage

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   ```bash
   # Create change-001-data-model
   mkdir -p openspec/changes/001-data-model
   # Write proposal.md, design.md, tasks.md, specs/
   ```

   **Proposal Highlights**:
   - Define `UniversalItem` dataclass with all 16 views
   - Define `ViewType` enum (16 values)
   - Define `LinkType` enum (60+ values)
   - Define `EventType` enum for event sourcing
   - Pydantic models for validation

2. **Day 3-4: Review & Align**
   - Technical review of data model
   - Validate against requirements
   - Approve proposal

3. **Day 5-10: Implement**
   - **Task 1.1**: Define enums and dataclasses (2 days)
     - Write tests first (test_data_model.py)
     - Implement UniversalItem
     - Implement ViewType, LinkType, EventType
     - Ensure mypy passes

   - **Task 1.2**: Database schema (2 days)
     - Design SQLite schema
     - Create SQLAlchemy models
     - Write Alembic migrations
     - Test database creation

   - **Task 1.3**: Repository pattern (2 days)
     - Implement ItemRepository
     - Implement LinkRepository
     - Implement EventStore
     - Write repository tests

**Sprint Deliverables**:
- ✅ Complete data models with 100% test coverage
- ✅ SQLite database with all tables
- ✅ Repository pattern implemented
- ✅ Event sourcing foundation

**Acceptance Criteria**:
- [ ] Can create UniversalItem for all 16 views
- [ ] All enums defined and validated
- [ ] Database migrations run successfully
- [ ] All repository CRUD operations work
- [ ] Test coverage ≥80%

#### Sprint 2 (Weeks 3-4): CLI & NATS Integration

**Sprint Goal**: Functional CLI with NATS event publishing

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-003-cli-foundation`
   - `change-004-nats-basic`

2. **Day 3-4: Review & Align**
   - Review CLI command structure
   - Validate NATS integration approach

3. **Day 5-10: Implement**
   - **Task 2.1**: CLI structure (2 days)
     - Create cli/main.py with Typer
     - Implement command groups
     - Add Rich formatting
     - Test CLI commands

   - **Task 2.2**: Basic CLI commands (2 days)
     - `trace item create`
     - `trace item list`
     - `trace item show`
     - `trace item update`
     - `trace item delete`

   - **Task 2.3**: NATS integration (2 days)
     - Create NATSClient wrapper
     - Publish item change events
     - Test event publishing
     - Add basic subscriber

**Sprint Deliverables**:
- ✅ Functional CLI with core commands
- ✅ NATS client integrated
- ✅ Events published on item changes

**Acceptance Criteria**:
- [ ] Can manage items via CLI
- [ ] Output formatted with Rich
- [ ] NATS events published correctly
- [ ] Basic event subscription works

#### Phase 1 Gate Review

**Gate 1 Checklist**:
- [ ] All Sprint 1 & 2 deliverables complete
- [ ] Test coverage ≥80%
- [ ] All proposals archived
- [ ] Performance: Item creation <200ms
- [ ] Documentation updated
- [ ] Demo to stakeholders

**Go/No-Go Decision**:
- **GO**: Proceed to Phase 2
- **NO-GO**: Fix issues, re-test, re-review

---

### PHASE 2: Versioning & History (Weeks 5-8)

#### Phase Overview

**Goal**: Implement Git-style versioning with time-travel

**OpenSpec Changes**:
- `change-005-commit-structure`: Git-style commits and DAG
- `change-006-snapshot-system`: Performance snapshots
- `change-007-semantic-versioning`: Auto-version bumping
- `change-008-time-travel`: Time-travel engine

#### Sprint 3 (Weeks 5-6): Commit Structure & Snapshots

**Sprint Goal**: Working commit system with snapshots

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-005-commit-structure`
   - `change-006-snapshot-system`

2. **Day 3-4: Review & Align**
   - Validate commit DAG design
   - Review snapshot strategy

3. **Day 5-10: Implement**
   - **Task 3.1**: Commit model (2 days)
     - Define Commit dataclass
     - Implement SHA-256 hashing
     - Create commit graph
     - Test commit creation

   - **Task 3.2**: Tree structure (1 day)
     - Define Tree for views
     - Implement tree serialization
     - Test tree diffing

   - **Task 3.3**: Snapshot system (2 days)
     - Implement snapshot creation
     - Add zstandard compression
     - Delta vs full storage logic
     - Test snapshot recovery

**Sprint Deliverables**:
- ✅ Commit structure operational
- ✅ Snapshot system working
- ✅ Content-addressable storage

**Acceptance Criteria**:
- [ ] Can create commits with parent references
- [ ] Commits are content-addressable
- [ ] Snapshots created every 100 events
- [ ] State recovery <500ms

#### Sprint 4 (Weeks 7-8): Semantic Versioning & Time-Travel

**Sprint Goal**: Auto-versioning and time-travel functional

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-007-semantic-versioning`
   - `change-008-time-travel`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 4.1**: Conventional commits (2 days)
     - Parse commit messages
     - Implement version bump logic
     - Generate changelog
     - Test versioning

   - **Task 4.2**: Baseline management (1 day)
     - Create baseline model
     - Tag commits
     - Protect baselines

   - **Task 4.3**: Time-travel engine (2 days)
     - Implement time-travel to timestamp
     - Implement time-travel to baseline
     - Generate diffs
     - Optimize performance

**Sprint Deliverables**:
- ✅ Semantic versioning automated
- ✅ Time-travel operational
- ✅ Diff engine working

**Acceptance Criteria**:
- [ ] Versions auto-increment correctly
- [ ] Can time-travel to any point
- [ ] Diff accurately shows changes
- [ ] Performance: Time-travel <500ms

#### Phase 2 Gate Review

**Gate 2 Checklist**:
- [ ] All Sprint 3 & 4 deliverables complete
- [ ] Test coverage ≥80%
- [ ] All proposals archived
- [ ] Performance targets met
- [ ] Documentation updated

---

### PHASE 3: PM Planning Features (Weeks 9-12)

#### Phase Overview

**Goal**: PERT/WBS/DAG planning with distributed execution

**OpenSpec Changes**:
- `change-009-wbs-engine`: Work breakdown structure
- `change-010-pert-cpm`: Critical path analysis
- `change-011-jetstream-tasks`: JetStream work queues
- `change-012-dag-execution`: Distributed DAG execution

#### Sprint 5 (Weeks 9-10): WBS & Critical Path

**Sprint Goal**: WBS auto-generation and critical path calculation

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-009-wbs-engine`
   - `change-010-pert-cpm`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 5.1**: WBS engine (2 days)
     - Define WBSTree structure
     - Implement decomposition
     - Enforce 100% rule
     - Integrate BERT NLP

   - **Task 5.2**: PERT/CPM (2 days)
     - Build dependency DAG
     - Forward/backward pass
     - Calculate slack
     - Identify critical path

   - **Task 5.3**: Schedule optimization (1 day)
     - Parallelize tasks
     - Resource leveling
     - Generate optimized schedule

**Sprint Deliverables**:
- ✅ WBS auto-generation working
- ✅ Critical path calculated
- ✅ Schedule optimization

**Acceptance Criteria**:
- [ ] WBS correctly decomposes features
- [ ] Critical path identified
- [ ] Performance: <2s for 1000 tasks

#### Sprint 6 (Weeks 11-12): JetStream & DAG Execution

**Sprint Goal**: Distributed task execution with NATS

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-011-jetstream-tasks`
   - `change-012-dag-execution`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 6.1**: JetStream setup (2 days)
     - Configure TRACE_TASKS stream
     - Create pull consumers
     - Implement task publisher
     - Test work queue

   - **Task 6.2**: Worker pool (1 day)
     - Create worker loop
     - Implement task execution
     - Add retry logic
     - Handle timeouts

   - **Task 6.3**: DAG coordination (2 days)
     - Dependency resolution
     - Schedule ready tasks
     - Track execution state
     - Handle completion

**Sprint Deliverables**:
- ✅ JetStream work queues operational
- ✅ Worker pool executing tasks
- ✅ DAG execution distributed

**Acceptance Criteria**:
- [ ] Tasks execute in parallel
- [ ] Dependencies resolved correctly
- [ ] No deadlocks
- [ ] Status tracking accurate

#### Phase 3 Gate Review

**Gate 3 Checklist**:
- [ ] All Sprint 5 & 6 deliverables complete
- [ ] Test coverage ≥80%
- [ ] All proposals archived
- [ ] Performance targets met
- [ ] Load testing passed

---

### PHASE 4: Verification & Quality (Weeks 13-16)

#### Phase Overview

**Goal**: NL assertions, formal verification, cryptographic proofs

**OpenSpec Changes**:
- `change-013-intentguard`: IntentGuard integration
- `change-014-formal-verification`: Hypothesis + Z3
- `change-015-cryptographic-proofs`: Proof generation
- `change-016-quality-dashboard`: Metrics dashboard

#### Sprint 7 (Weeks 13-14): IntentGuard & Formal Verification

**Sprint Goal**: Hybrid verification operational

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-013-intentguard`
   - `change-014-formal-verification`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 7.1**: IntentGuard setup (2 days)
     - Add IntentGuard dependency
     - Configure model
     - Implement NL engine
     - Test verification

   - **Task 7.2**: Property-based testing (1 day)
     - Integrate Hypothesis
     - Convert criteria to properties
     - Generate tests

   - **Task 7.3**: Symbolic execution (2 days)
     - Integrate Z3
     - Convert to formulas
     - Find counterexamples
     - Hybrid reconciliation

**Sprint Deliverables**:
- ✅ IntentGuard integrated
- ✅ Hybrid verification working
- ✅ >85% verification accuracy

**Acceptance Criteria**:
- [ ] NL assertions verified
- [ ] Property-based tests running
- [ ] Symbolic execution finds bugs
- [ ] Performance: <5s per criterion

#### Sprint 8 (Weeks 15-16): Cryptographic Proofs & Quality Dashboard

**Sprint Goal**: Immutable audit trail and quality metrics

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-015-cryptographic-proofs`
   - `change-016-quality-dashboard`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 8.1**: Proof generation (2 days)
     - Generate cryptographic proofs
     - Sign with private key
     - Store in database
     - Publish to NATS

   - **Task 8.2**: Merkle tree (1 day)
     - Build Merkle tree
     - Compute root
     - Generate proofs
     - Verify inclusion

   - **Task 8.3**: Quality dashboard (2 days)
     - Integrate coverage.py
     - Integrate Radon/Lizard
     - Integrate Bandit
     - Generate reports
     - Real-time updates

**Sprint Deliverables**:
- ✅ Cryptographic proofs generated
- ✅ Merkle tree audit trail
- ✅ Quality dashboard operational

**Acceptance Criteria**:
- [ ] All verifications have proofs
- [ ] Merkle tree immutable
- [ ] Coverage ≥80%
- [ ] Zero high-severity issues

#### Phase 4 Gate Review

**Gate 4 Checklist**:
- [ ] All Sprint 7 & 8 deliverables complete
- [ ] Test coverage ≥80%
- [ ] All proposals archived
- [ ] Security audit passed
- [ ] Performance targets met

---

### PHASE 5: Integration & Polish (Weeks 17-20)

#### Phase Overview

**Goal**: Complete system integration, TUI, optimization, documentation

**OpenSpec Changes**:
- `change-017-multi-sig`: Multi-signature approval
- `change-018-continuous-verification`: Watch mode
- `change-019-tui`: Textual TUI
- `change-020-optimization`: Performance tuning
- `change-021-documentation`: Complete docs

#### Sprint 9 (Weeks 17-18): Multi-Sig & TUI

**Sprint Goal**: Advanced features and visualization

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-017-multi-sig`
   - `change-018-continuous-verification`
   - `change-019-tui`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 9.1**: Multi-sig approval (1 day)
     - Implement workflow
     - Request/sign approval
     - Track signatures

   - **Task 9.2**: Continuous verification (1 day)
     - File system watcher
     - Re-verify on changes
     - Incremental verification

   - **Task 9.3**: TUI foundation (3 days)
     - Create Textual app
     - Implement 16 view tabs
     - Real-time updates
     - Gantt chart
     - Merkle tree viz

**Sprint Deliverables**:
- ✅ Multi-sig approval working
- ✅ Continuous verification operational
- ✅ TUI functional and beautiful

**Acceptance Criteria**:
- [ ] Multi-sig workflow completes
- [ ] Watch mode detects changes <1s
- [ ] TUI responsive
- [ ] Real-time updates work

#### Sprint 10 (Weeks 19-20): Optimization & Documentation

**Sprint Goal**: Production-ready system

**OpenSpec Workflow**:

1. **Day 1-2: Draft Proposals**
   - `change-020-optimization`
   - `change-021-documentation`

2. **Day 3-4: Review & Align**

3. **Day 5-10: Implement**
   - **Task 10.1**: Performance optimization (3 days)
     - Multi-tier caching
     - Query optimization
     - Parallel processing
     - Benchmark and profile

   - **Task 10.2**: Documentation (2 days)
     - Generate API docs
     - Write user guide
     - Create example projects
     - Record video tutorials

**Sprint Deliverables**:
- ✅ All performance targets met
- ✅ Complete documentation
- ✅ Example projects

**Acceptance Criteria**:
- [ ] View switch <50ms
- [ ] Commit <100ms
- [ ] Time-travel <500ms
- [ ] All docs complete
- [ ] 3 example projects

#### Phase 5 Gate Review

**Gate 5 Checklist**:
- [ ] All Sprint 9 & 10 deliverables complete
- [ ] Test coverage ≥80%
- [ ] All proposals archived
- [ ] All performance targets met
- [ ] Security audit passed
- [ ] Load testing passed (1000+ agents)
- [ ] Documentation complete
- [ ] Production deployment tested

---

## 6. Continuous Integration & Testing

### 6.1 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run Ruff
        run: uv run ruff check .

      - name: Run mypy
        run: uv run mypy .

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      - name: Check coverage
        run: |
          uv run coverage report --fail-under=80

      - name: Run Bandit
        run: uv run bandit -r . -ll

      - name: Performance tests
        run: uv run pytest tests/performance/
```

### 6.2 Test Strategy

#### Unit Tests (60%)
- Every function/method
- Pure logic testing
- No external dependencies
- Fast (<1s per test)

#### Integration Tests (30%)
- Component interactions
- Database operations
- NATS integration
- Event sourcing

#### End-to-End Tests (10%)
- Complete workflows
- CLI commands
- TUI interactions
- Performance benchmarks

### 6.3 Test Requirements Per Sprint

Each sprint must deliver:
- [ ] All new code has unit tests
- [ ] Integration tests for new components
- [ ] E2E tests for new workflows
- [ ] Coverage ≥80% maintained
- [ ] All tests pass
- [ ] Performance benchmarks met

---

## 7. Risk Management

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| NATS integration complex | Medium | High | Start with simple pub/sub, add features incrementally | Phase 1 |
| IntentGuard accuracy <85% | Medium | Medium | Hybrid verification with formal methods | Phase 4 |
| Performance targets not met | Low | High | Continuous benchmarking, optimize early | All Phases |
| Module size violations | Low | Medium | Automated checks in CI, proactive decomposition | All Phases |
| Time-travel complexity | Medium | High | Start with snapshots, iterate on replay | Phase 2 |

### 7.2 Schedule Risks

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| Features take longer | Medium | Medium | 20% buffer per phase, de-scope if needed | PM |
| Dependencies block | Low | High | Identify dependencies early, parallel work | Tech Lead |
| Testing reveals issues | Medium | Medium | TDD from day one, test early | All |
| Team availability | Low | High | Cross-train, documentation | PM |

### 7.3 Risk Monitoring

**Weekly Risk Review**:
- Review risk register
- Update probabilities
- Activate mitigation plans
- Escalate if needed

**Sprint Retrospective**:
- Identify new risks
- Review mitigation effectiveness
- Update risk register

---

## 8. Quality Assurance

### 8.1 Definition of Done

A task is "done" when:
- [ ] Code written and committed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Performance benchmarks met
- [ ] OpenSpec change referenced
- [ ] CI pipeline green

### 8.2 Code Review Process

**All code requires review**:
1. Self-review first
2. Peer review (30 min max)
3. Address feedback
4. Approve and merge

**Review Checklist**:
- [ ] Code follows constitution
- [ ] Module size ≤350 lines
- [ ] Tests comprehensive
- [ ] Types correct (mypy passes)
- [ ] Performance acceptable
- [ ] Documentation clear

### 8.3 Quality Metrics Tracking

**Track Weekly**:
- Test coverage % (target ≥80%)
- Cyclomatic complexity (target ≤10)
- Security issues (target 0 high)
- Performance metrics
- Documentation coverage

**Track Per Sprint**:
- Velocity (story points completed)
- Defect rate
- Code churn
- Technical debt

---

## 9. Communication & Collaboration

### 9.1 Communication Channels

**Synchronous**:
- Sprint planning (2 hours, start of sprint)
- Sprint review (1 hour, end of sprint)
- Sprint retrospective (1 hour, end of sprint)
- Technical design reviews (as needed)

**Asynchronous**:
- Daily standups (written)
- Code reviews (GitHub)
- OpenSpec proposals (written)
- Documentation updates

### 9.2 Documentation Requirements

**Must Maintain**:
- OpenSpec specs (always current)
- API documentation (Sphinx)
- User guide (for CLI/TUI)
- Architecture decisions (ADRs)
- Changelog (semantic versioning)

**Update Frequency**:
- OpenSpec specs: Every change
- API docs: Every sprint
- User guide: Every phase
- ADRs: As architectural decisions made
- Changelog: Every release

---

## 10. Deployment & Operations

### 10.1 Deployment Strategy

**Phase 1-4**: Development only
- Local development environment
- CI/CD testing environment
- No production deployment

**Phase 5**: Production preparation
- Staging environment setup
- Load testing (1000+ agents)
- Security audit
- Production deployment test

**Post-Phase 5**: Production deployment
- Gradual rollout
- Monitor metrics
- Rollback plan ready

### 10.2 Monitoring & Observability

**Metrics to Track**:
- Application performance (latency, throughput)
- NATS metrics (messages, lag)
- Database performance (query time)
- Resource usage (CPU, memory)
- Error rates
- User activity

**Tools**:
- NATS monitoring (built-in)
- Python logging (structured)
- Performance profiling (py-spy)
- Coverage tracking (coverage.py)

---

## 11. Success Criteria Summary

### Phase Success Criteria

**Phase 1**: Foundation operational, CLI working, NATS integrated
**Phase 2**: Versioning working, time-travel <500ms
**Phase 3**: PM planning operational, DAG execution distributed
**Phase 4**: Verification >85% accurate, audit trail immutable
**Phase 5**: All performance targets met, production-ready

### Project Success Criteria

The project is successful when:
- ✅ All 5 phases complete
- ✅ All phase gates passed
- ✅ Test coverage ≥80%
- ✅ All performance targets met
- ✅ Security audit passed
- ✅ Documentation complete
- ✅ Production deployment successful
- ✅ Can orchestrate 1000+ agents

---

## 12. Immediate Next Steps

### Week 1, Day 1: Project Kickoff

1. **Morning: Setup**
   ```bash
   cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

   # Create OpenSpec structure
   mkdir -p openspec/{specs,changes,archive}

   # Write constitution
   touch openspec/constitution.md

   # Write AGENTS.md
   touch openspec/AGENTS.md

   # Initialize project
   uv init
   uv add fastmcp typer rich pydantic sqlalchemy nats-py pytest coverage mypy ruff bandit
   ```

2. **Afternoon: First Proposal**
   ```bash
   # Create change-001-data-model
   mkdir -p openspec/changes/001-data-model
   cd openspec/changes/001-data-model

   # Write proposal
   touch proposal.md
   touch design.md
   touch tasks.md
   mkdir specs
   touch specs/data-model.md
   ```

3. **Evening: Review**
   - Review proposal with team
   - Get approval to proceed
   - Plan Sprint 1

### Week 1, Days 2-10: Sprint 1 Execution

Follow Sprint 1 plan (Data Model & Storage)

---

## 13. Appendix

### A. Glossary

- **OpenSpec**: Specification-driven development methodology
- **Spec Kit**: GitHub's toolkit for spec-driven development
- **Phase Gate**: Decision point between major phases
- **Sprint**: 2-week iteration
- **Story Point**: Unit of effort estimation
- **Definition of Done**: Criteria for task completion
- **ADR**: Architecture Decision Record
- **TDD**: Test-Driven Development

### B. References

- OpenSpec Documentation: https://github.com/Fission-AI/OpenSpec
- Spec Kit Documentation: https://github.com/github/spec-kit
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- NATS JetStream: https://docs.nats.io/jetstream
- Agile Manifesto: https://agilemanifesto.org/

### C. Templates

All templates available in `openspec/templates/`:
- `proposal-template.md`
- `spec-template.md`
- `task-template.md`
- `design-template.md`

---

## Summary

This comprehensive hybrid plan combines:
- ✅ **Waterfall**: Clear phases, gates, comprehensive specs
- ✅ **Agile**: 2-week sprints, working software, adaptation
- ✅ **OpenSpec**: Formal change proposals, spec-driven
- ✅ **Quality**: TDD, CI/CD, coverage, security

**Duration**: 20 weeks (5 phases × 4 weeks)
**Sprints**: 10 sprints (2 weeks each)
**Changes**: ~21 OpenSpec changes
**Outcome**: Production-ready system for 1000+ agent orchestration

**Start**: Week 1, Day 1
**End**: Week 20, Day 10
**Production**: Week 21+

This plan is ready for execution. Begin with Week 1, Day 1 project kickoff.
