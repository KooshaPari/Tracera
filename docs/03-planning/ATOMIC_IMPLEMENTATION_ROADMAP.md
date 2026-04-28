# Atomic Trace Implementation Roadmap

**Version**: 2.0 (Integrated with Atomic Architecture)
**Date**: 2025-11-20
**Duration**: 20 weeks (5 phases × 4 weeks)
**Status**: Ready for execution

---

## Overview

This roadmap integrates **atomic requirements architecture** into the existing 20-week trace implementation plan. The atomic features are introduced progressively, starting with foundation in Phase 1 and reaching full atomic capabilities by Phase 5.

**Integration Strategy**: Extend existing plan with atomic features at each phase rather than treating as separate project.

---

## Phase 1: Foundation + Basic Atoms (Weeks 1-4)

**Goal**: Core infrastructure + basic atomic entity model

### Week 1: Project Setup + Atom Foundation

**Days 1-2: Standard Foundation**
- [x] uv project initialization
- [x] Directory structure (Clean + Hexagonal)
- [x] OpenSpec setup (constitution, AGENTS.md)
- [x] Dependencies (fastmcp, typer, rich, pydantic, sqlalchemy, nats-py)
- [x] Core domain models (UniversalItem, ViewType, LinkType)
- [x] TDD test suite (16 tests, 88%+ coverage)

**Days 3-4: Atomic Entity Model**
- [ ] Define AtomType enum (SUBJECT, ACTION, METHOD, INTERFACE)
- [ ] Define Atom dataclass with full model
- [ ] Create atom library seeds (~20 initial atoms):
  - Subject: user, agent, system, admin, api-client
  - Action: create, read, update, delete, login, logout
  - Method: email-password, api-key, session-cookie
  - Interface: web-ui, rest-api, cli
- [ ] TDD tests for Atom entity (15+ tests)
- [ ] AtomRepository port + SQLite implementation

**Days 5-7: Atomic Requirement Model**
- [ ] Define AtomicRequirement dataclass
- [ ] Template rendering system ([{subject}] can [{action}]...)
- [ ] TDD tests for AtomicRequirement (20+ tests)
- [ ] AtomicRequirementRepository port + SQLite implementation
- [ ] Basic CLI commands:
  - `trace atom list`
  - `trace atom create`
  - `trace requirement create --atomic`

**Deliverables**:
- ✅ Atom entity model (src/trace/domain/atoms.py, ~250 lines)
- ✅ AtomicRequirement model (src/trace/domain/atomic_requirements.py, ~300 lines)
- ✅ Atom library with 20 seed atoms (data/atoms.json)
- ✅ 35+ tests with 85%+ coverage
- ✅ Basic CLI operational

**Quality Gates**:
- [ ] All tests pass (100%)
- [ ] Coverage ≥85%
- [ ] Mypy strict passes
- [ ] Ruff clean
- [ ] Module sizes ≤350 lines
- [ ] Can create/read atoms and atomic requirements

---

### Week 2: Repository Pattern + Basic Integration

**Days 1-3: Repository Layer**
- [ ] ItemRepositoryPort (from existing plan)
- [ ] SQLiteItemRepository implementation
- [ ] Integration tests for repository (15+ tests)
- [ ] AtomRepositoryPort definition
- [ ] SQLiteAtomRepository implementation
- [ ] Integration tests for atom repository

**Days 4-5: Basic UniversalItem ↔ AtomicRequirement Link**
- [ ] DerivedItem entity (links UniversalItem to AtomicRequirement)
- [ ] DerivedItemRepository
- [ ] Create first manual cascade: AtomicReq → FEATURE view UniversalItem
- [ ] Tests for derivation logic (10+ tests)

**Days 6-7: Use Cases**
- [ ] CreateItemUseCase
- [ ] CreateAtomUseCase
- [ ] CreateAtomicRequirementUseCase (with manual view creation)
- [ ] Unit tests with mock repositories (15+ tests)

**Deliverables**:
- ✅ Complete repository layer (4 repositories)
- ✅ DerivedItem traceability model
- ✅ Basic manual cascade (Atomic Req → FEATURE view)
- ✅ 40+ tests total
- ✅ Use cases with dependency injection

**Quality Gates**:
- [ ] Integration tests pass with real SQLite
- [ ] Can create AtomicRequirement and manually create FEATURE view item
- [ ] Traceability links established
- [ ] Coverage ≥85%

---

### Week 3: NATS + Event Foundation

**Days 1-3: NATS Integration**
- [ ] NATS connection management
- [ ] JetStream stream creation (TRACE_EVENTS, TRACE_ATOMIC_EVENTS)
- [ ] Event publisher (async)
- [ ] Event consumer (pull-based)
- [ ] Integration tests for NATS (10+ tests)

**Days 4-5: Basic Event Sourcing**
- [ ] RequirementEvent entity
- [ ] EventStore with PostgreSQL backend
- [ ] RequirementAggregate (event replay)
- [ ] Basic events: RequirementCreated, AtomToggled
- [ ] Event handler registration

**Days 6-7: Event-Driven Use Cases**
- [ ] Refactor use cases to emit events
- [ ] Subscribe to events for async processing
- [ ] Event-driven tests (using test consumer)

**Deliverables**:
- ✅ NATS JetStream operational
- ✅ Event store with 2 event types
- ✅ Event-sourced AtomicRequirement
- ✅ Async event processing working

**Quality Gates**:
- [ ] Events published and consumed successfully
- [ ] Event replay reconstructs requirement state correctly
- [ ] NATS integration tests pass
- [ ] Coverage ≥85%

---

### Week 4: Validation + CLI Enhancement

**Days 1-3: Validation Pipeline**
- [ ] RequirementValidator with regex rules
- [ ] Constraint checking for atoms and requirements
- [ ] Basic ambiguity detection (keyword-based, not BERT yet)
- [ ] Validation tests (15+ tests)

**Days 4-5: Rich CLI**
- [ ] Typer CLI with Rich tables for output
- [ ] Commands:
  - `trace atom list --type subject`
  - `trace atom show <atom-id> --related`
  - `trace req create --interactive` (wizard)
  - `trace req show <req-id> --render`
  - `trace req validate <req-id>`
- [ ] CLI integration tests

**Days 6-7: Phase 1 Polish**
- [ ] Documentation updates
- [ ] Code review and refactoring
- [ ] Performance profiling (baseline metrics)
- [ ] Phase 1 gate review

**Deliverables**:
- ✅ Validation pipeline operational
- ✅ Rich CLI with 10+ commands
- ✅ Phase 1 complete and polished
- ✅ Baseline performance metrics established

**Phase 1 Quality Gates**: ✅ All must pass
- [ ] 100+ tests passing (unit + integration)
- [ ] Coverage ≥85%
- [ ] All modules ≤350 lines (500 hard limit)
- [ ] Mypy strict passes
- [ ] Ruff clean
- [ ] NATS integration working
- [ ] Can create atoms and atomic requirements
- [ ] Basic validation operational
- [ ] CLI functional

---

## Phase 2: Versioning + Atom Toggling (Weeks 5-8)

**Goal**: Git-style versioning + atom toggle with basic cascade

### Week 5: Versioning Foundation

**Days 1-3: Commit Structure**
- [ ] Commit entity with pygit2 integration
- [ ] Content-addressable storage
- [ ] Commit repository
- [ ] Version atomic requirements
- [ ] Tests for versioning (15+ tests)

**Days 4-5: Snapshot System**
- [ ] Snapshot strategy (every 100 events)
- [ ] Snapshot storage
- [ ] Snapshot-based read optimization
- [ ] Tests for snapshots

**Days 6-7: Semantic Versioning**
- [ ] Conventional commit parsing
- [ ] Automatic version bumping (MAJOR.MINOR.PATCH)
- [ ] Version tags
- [ ] CHANGELOG generation

**Deliverables**:
- ✅ Git-style commit structure
- ✅ Snapshot system operational
- ✅ Semantic versioning automated
- ✅ 30+ versioning tests

---

### Week 6: Atom Toggle + Impact Analysis

**Days 1-3: AtomChange Model**
- [ ] AtomChange entity
- [ ] AtomicImpactAnalyzer (basic version)
- [ ] Find affected requirements
- [ ] Tests for impact analysis (10+ tests)

**Days 4-5: Basic Cascade**
- [ ] CascadingUpdateEngine (v1: simple cascade)
- [ ] Update affected requirements when atom toggled
- [ ] Emit cascade events
- [ ] Tests for cascade (15+ tests)

**Days 6-7: Toggle CLI**
- [ ] `trace atom toggle <req-id> --atom <type> --new <atom-value>`
- [ ] `trace atom toggle --preview` (dry run)
- [ ] Interactive confirmation
- [ ] Integration tests for toggle workflow

**Deliverables**:
- ✅ Atom toggle operational
- ✅ Basic impact analysis (finds affected reqs)
- ✅ Simple cascade (updates requirements only, not views yet)
- ✅ CLI toggle command working

**Quality Gates**:
- [ ] Can toggle atom and see affected requirements
- [ ] Cascade updates all affected requirements
- [ ] Events published for cascades
- [ ] Tests passing, coverage ≥85%

---

### Week 7: Time-Travel + Diff Engine

**Days 1-3: Time-Travel**
- [ ] Time-travel engine (checkout any version)
- [ ] Snapshot + event replay optimization
- [ ] Performance target: <500ms
- [ ] Tests for time-travel (10+ tests)

**Days 4-5: Diff Engine**
- [ ] Structured diff between versions
- [ ] Atom-aware diff (show atom toggles explicitly)
- [ ] Diff visualization in CLI
- [ ] Tests for diff (10+ tests)

**Days 6-7: Versioning CLI**
- [ ] `trace commit -m "message"`
- [ ] `trace log --atomic` (show atom changes in history)
- [ ] `trace checkout <version>`
- [ ] `trace diff <v1> <v2> --atoms-only`

**Deliverables**:
- ✅ Time-travel working (<500ms)
- ✅ Atom-aware diff engine
- ✅ Versioning CLI commands
- ✅ 20+ versioning tests

---

### Week 8: AtomViewMapping + Multi-View Cascade

**Days 1-3: View Mapping Model**
- [ ] AtomViewMapping entity
- [ ] Mapping rules for 64 integration points (16 views × 4 atoms)
- [ ] Seed mappings for core views (FEATURE, CODE, TEST, API)
- [ ] Mapping tests (20+ tests covering each view)

**Days 4-5: Enhanced Cascade**
- [ ] CascadingUpdateEngine v2 (view-aware)
- [ ] Update UniversalItems in derived views when atom toggled
- [ ] Generate ItemUpdateRequired events
- [ ] Tests for multi-view cascade (15+ tests)

**Days 6-7: Phase 2 Polish**
- [ ] Performance optimization (caching, async)
- [ ] Integration tests for full cascade flow
- [ ] Documentation updates
- [ ] Phase 2 gate review

**Deliverables**:
- ✅ 64 view mapping rules defined
- ✅ Multi-view cascade operational
- ✅ Atom toggle updates items in CODE, TEST, API views automatically
- ✅ 35+ cascade tests

**Phase 2 Quality Gates**: ✅ All must pass
- [ ] 180+ tests passing
- [ ] Coverage ≥85%
- [ ] Time-travel <500ms (verified by performance tests)
- [ ] Can toggle atom and see updates cascade to at least 3 views
- [ ] Git-style versioning working
- [ ] Semantic versions auto-generated
- [ ] All modules ≤350 lines

---

## Phase 3: Intelligent CRUD + Feature Flags (Weeks 9-12)

**Goal**: Auto-generation across all 16 views + runtime configuration

### Week 9: Intelligent CRUD Foundation

**Days 1-3: Template System**
- [ ] ScaffoldTemplate base class
- [ ] ReactComponentTemplate (for WIREFRAME → CODE)
- [ ] APIEndpointTemplate (for API view generation)
- [ ] DatabaseTableTemplate (for DATABASE view)
- [ ] Template library with 10 templates
- [ ] Template tests (15+ tests)

**Days 4-5: Generation Engine**
- [ ] IntelligentCRUDEngine v1
- [ ] `_determine_affected_views()` heuristics
- [ ] `_generate_items_for_view()` for CODE, TEST, API views
- [ ] Tests for generation logic (20+ tests)

**Days 6-7: CLI Integration**
- [ ] `trace req create --auto-generate`
- [ ] Preview generated items before confirming
- [ ] Scaffold code files to disk
- [ ] Integration tests

**Deliverables**:
- ✅ Template library with 10 templates
- ✅ Auto-generation for CODE, TEST, API views
- ✅ Code scaffolding to disk
- ✅ 35+ generation tests

---

### Week 10: LLM-Assisted Generation

**Days 1-3: LLM Integration**
- [ ] Claude API client wrapper
- [ ] Prompt templates for code generation
- [ ] Prompt templates for test generation
- [ ] Context extraction from existing codebase
- [ ] LLM tests (with mocks, 10+ tests)

**Days 4-5: Enhanced Generation**
- [ ] LLM-powered `_generate_code_item()`
- [ ] LLM-powered `_generate_test_item()`
- [ ] Context-aware scaffolding (learns from existing patterns)
- [ ] Tests for LLM generation (integration tests)

**Days 6-7: Quality & Cost Optimization**
- [ ] Caching for LLM results (Redis)
- [ ] Rate limiting (100 generations/hour)
- [ ] Cost tracking ($/ generation)
- [ ] Fallback to templates if LLM unavailable

**Deliverables**:
- ✅ LLM-assisted generation operational
- ✅ Context-aware code scaffolding
- ✅ Cost tracking dashboard
- ✅ Cache hit rate >70%

---

### Week 11: Feature Flags Integration

**Days 1-3: Unleash Setup**
- [ ] Unleash server deployment (Docker)
- [ ] Python SDK integration (UnleashClient)
- [ ] FeatureFlag entity model
- [ ] FlagStrategy implementation (environment, tenant, gradual rollout)
- [ ] Flag tests (15+ tests)

**Days 4-5: Product Derivation**
- [ ] ProductDerivationEngine
- [ ] EvalContext model
- [ ] Flag-based requirement filtering
- [ ] Configuration validation
- [ ] Product derivation tests (20+ tests)

**Days 6-7: Flag CLI**
- [ ] `trace flag create --key ff_oauth2 --default false`
- [ ] `trace flag list --requirement FR-001`
- [ ] `trace product derive --env production --tenant acme`
- [ ] `trace product export --env prod --output .env.prod`

**Deliverables**:
- ✅ Unleash integrated
- ✅ Product derivation operational
- ✅ Can derive product configs from flags
- ✅ Flag management CLI

**Quality Gates**:
- [ ] Unleash server running
- [ ] Can create/evaluate feature flags
- [ ] Product derivation <100ms
- [ ] Flag evaluation cached (Redis)
- [ ] Tests passing, coverage ≥85%

---

### Week 12: Implementation Variants + Future Flags

**Days 1-3: Implementation Variant System**
- [ ] ImplementationVariant entity
- [ ] ImplementationRegistry
- [ ] Toggle mechanism (switch between auth0 ↔ authkit)
- [ ] Tests for variant toggling (15+ tests)

**Days 4-5: Future Implementation Tracking**
- [ ] FutureImplementationFlag entity
- [ ] FutureImplementationTracker
- [ ] Roadmap generation from future flags
- [ ] Tests (10+ tests)

**Days 6-7: Phase 3 Polish**
- [ ] Complete view mapping for all 16 views
- [ ] Integration tests (full atomic req → 16 views)
- [ ] Performance benchmarks
- [ ] Documentation updates
- [ ] Phase 3 gate review

**Deliverables**:
- ✅ Implementation variant toggle working
- ✅ Future flags tracked with roadmap
- ✅ Auto-generation across all 16 views
- ✅ 250+ tests total

**Phase 3 Quality Gates**: ✅ All must pass
- [ ] 250+ tests passing
- [ ] Coverage ≥85%
- [ ] Can create atomic requirement and see items generated in 10+ views
- [ ] Can toggle implementation variant
- [ ] Future flags generate roadmap
- [ ] Performance targets met:
  - Product derivation <100ms
  - Impact analysis <500ms
  - Code generation <5s with LLM
- [ ] All modules ≤350 lines

---

## Phase 4: Advanced Cascade + NLP Validation (Weeks 13-16)

**Goal**: Full cascading updates + intelligent validation

### Week 13: Complete Cascade Implementation

**Days 1-3: Enhanced Impact Analysis**
- [ ] Impact analysis for all 64 integration points (16 views × 4 atoms)
- [ ] Migration generation (for DATABASE view changes)
- [ ] Config change generation (for INFRASTRUCTURE changes)
- [ ] Effort estimation algorithm
- [ ] Risk assessment algorithm
- [ ] Tests (25+ tests)

**Days 4-5: Full Cascade Execution**
- [ ] CascadingUpdateEngine v3 (complete)
- [ ] Dependency-ordered updates (topological sort)
- [ ] Parallel execution where possible (NATS work queue)
- [ ] Rollback on failure
- [ ] Tests (20+ tests)

**Days 6-7: Cascade CLI**
- [ ] `trace atom toggle --preview` (show full impact)
- [ ] `trace cascade execute <req-id> --dry-run`
- [ ] `trace cascade status` (show in-progress cascades)
- [ ] Cascade progress visualization

**Deliverables**:
- ✅ Complete cascade across all 16 views
- ✅ Migration generation
- ✅ Rollback on failure
- ✅ 45+ cascade tests

---

### Week 14: NLP Validation (IntentGuard)

**Days 1-3: IntentGuard Integration**
- [ ] IntentGuard setup and configuration
- [ ] Natural language assertion validation
- [ ] AcceptanceCriterion entity with NL validation
- [ ] Tests for NL validation (10+ tests)

**Days 4-5: BERT-Based Checks**
- [ ] sentence-transformers setup
- [ ] Semantic similarity for duplicate detection
- [ ] Embedding cache (Redis)
- [ ] Tests (10+ tests)

**Days 6-7: Validation CLI**
- [ ] `trace validate <req-id>` (run all checks)
- [ ] `trace validate --check-duplicates`
- [ ] `trace validate --nl-assertions`
- [ ] Batch validation for all requirements

**Deliverables**:
- ✅ IntentGuard integrated
- ✅ Duplicate detection with BERT
- ✅ NL assertion validation
- ✅ 20+ NLP tests

---

### Week 15: LLM Validation Pipeline

**Days 1-3: LLM Quality Checks**
- [ ] Claude API integration for requirement analysis
- [ ] Prompt engineering for quality checks
- [ ] Structured output parsing (JSON schema)
- [ ] LLM response caching (Redis, 1 hour TTL)
- [ ] Tests with mocked LLM (10+ tests)

**Days 4-5: Layered Validation**
- [ ] ValidationPipeline (regex → BERT → LLM)
- [ ] Cost tracking ($/ validation)
- [ ] Rate limiting (100/hour/user)
- [ ] Fallback when LLM unavailable
- [ ] Tests (15+ tests)

**Days 6-7: Validation Dashboard**
- [ ] TUI with validation statistics
- [ ] Show validation results in real-time
- [ ] LLM cost tracking display
- [ ] Cache hit rate monitoring

**Deliverables**:
- ✅ Complete validation pipeline (3 layers)
- ✅ LLM cost <$0.01/validation with caching
- ✅ Validation dashboard (TUI)
- ✅ 25+ validation tests

---

### Week 16: Holistic Quality Metrics

**Days 1-3: Coverage Integration**
- [ ] Test coverage tracking per requirement
- [ ] Code coverage → Requirement coverage mapping
- [ ] Untested requirement detection
- [ ] Coverage dashboard

**Days 4-5: Complexity & Security**
- [ ] Radon/Lizard integration for complexity
- [ ] Bandit for security scanning
- [ ] Ruff for quality metrics
- [ ] Per-requirement quality scores

**Days 6-7: Phase 4 Polish**
- [ ] Quality metrics API endpoints
- [ ] Quality dashboard (TUI with Rich)
- [ ] Integration tests for full validation + quality flow
- [ ] Phase 4 gate review

**Deliverables**:
- ✅ Quality metrics integrated
- ✅ Real-time quality dashboard
- ✅ Requirement coverage tracking
- ✅ Phase 4 complete

**Phase 4 Quality Gates**: ✅ All must pass
- [ ] 330+ tests passing
- [ ] Coverage ≥85%
- [ ] Full cascade working (atom toggle → all 16 views updated)
- [ ] IntentGuard validation <5s
- [ ] LLM validation pipeline working
- [ ] Cost tracking <$0.01/validation
- [ ] Quality metrics dashboard operational
- [ ] All modules ≤350 lines

---

## Phase 5: Complete System + Production Ready (Weeks 17-20)

**Goal**: Full atomic capabilities + production deployment

### Week 17: Graph Traceability Complete

**Days 1-3: Advanced Graph Queries**
- [ ] Implement all PostgreSQL CTE patterns
- [ ] Circular dependency detection
- [ ] Critical path analysis (longest chain)
- [ ] Orphaned requirement detection
- [ ] High fan-out detection (bottlenecks)
- [ ] Tests (20+ tests)

**Days 4-5: Graph Algorithms**
- [ ] Transitive atom closure (`find_all_related_atoms`)
- [ ] Requirement compatibility checker
- [ ] Conflict resolution suggestions
- [ ] Tests (15+ tests)

**Days 6-7: Graph Visualization**
- [ ] TUI graph rendering with Textual
- [ ] Dependency graph export (GraphViz DOT)
- [ ] Interactive graph navigation
- [ ] Graph query CLI commands

**Deliverables**:
- ✅ Advanced graph queries (<500ms)
- ✅ Graph algorithms operational
- ✅ Graph visualization TUI
- ✅ 35+ graph tests

---

### Week 18: Complete Auto-Generation

**Days 1-3: All 16 Views**
- [ ] Complete IntelligentCRUDEngine for all 16 views
- [ ] Templates for every view type
- [ ] View-specific generation logic
- [ ] Tests for each view (16 × 5 = 80 tests)

**Days 4-5: Batch Operations**
- [ ] Batch atom toggle (multiple atoms at once)
- [ ] Batch requirement creation (CRUD template)
- [ ] Optimize cascade (combined impact analysis)
- [ ] Tests (15+ tests)

**Days 6-7: Smart Defaults**
- [ ] Infer atoms from natural language description
- [ ] Template matching (find best template for requirement)
- [ ] Auto-suggest related atoms
- [ ] Tests (10+ tests)

**Deliverables**:
- ✅ Generation for all 16 views
- ✅ Batch operations optimized
- ✅ Smart defaults working
- ✅ 105+ generation tests

---

### Week 19: External Integrations

**Days 1-3: GitHub Sync**
- [ ] GitHub webhook handler
- [ ] Sync requirements → GitHub Issues (one-way)
- [ ] Markdown formatting for requirements
- [ ] Link preservation
- [ ] Tests (15+ tests)

**Days 4-5: VS Code Extension** (optional)
- [ ] Extension setup (TypeScript)
- [ ] Inline requirement viewing (hover)
- [ ] Trace link navigation
- [ ] Extension tests

**Days 6-7: GraphQL API**
- [ ] GraphQL schema for atomic requirements
- [ ] Resolvers for atoms, requirements, derived items
- [ ] Subscription support (real-time updates)
- [ ] GraphQL tests

**Deliverables**:
- ✅ GitHub sync operational (<5s for 1K requirements)
- ✅ VS Code extension (optional)
- ✅ GraphQL API
- ✅ 30+ integration tests

---

### Week 20: Production Ready + Documentation

**Days 1-2: Performance Optimization**
- [ ] Profile all critical paths
- [ ] Optimize hot spots (caching, indexing, async)
- [ ] Verify all performance targets met
- [ ] Load testing (1000 requirements, 100 concurrent updates)

**Days 3-4: Security & Compliance**
- [ ] Security audit (Bandit scan)
- [ ] Input validation at all boundaries
- [ ] Rate limiting on API endpoints
- [ ] Audit log completeness verification

**Days 5-6: Documentation**
- [ ] Complete API documentation (OpenAPI)
- [ ] CLI reference guide
- [ ] Architecture diagrams (all 16 views + atomic layer)
- [ ] Tutorial: "Building Your First Atomic Requirement"
- [ ] Migration guide (non-atomic → atomic)

**Day 7: Final Review**
- [ ] Phase 5 gate review
- [ ] Production readiness checklist
- [ ] Deployment guide
- [ ] Handoff to operations

**Deliverables**:
- ✅ All performance targets met
- ✅ Security audit clean
- ✅ Complete documentation
- ✅ Production ready

**Phase 5 Quality Gates**: ✅ All must pass
- [ ] 450+ tests passing
- [ ] Coverage ≥85%
- [ ] All performance targets met (verified by benchmarks)
- [ ] Full atomic system operational (atoms, toggle, cascade, flags, generation)
- [ ] Documentation complete
- [ ] Security audit clean
- [ ] Load tests pass (1000 reqs, 100 concurrent)
- [ ] Ready for production deployment

---

## Success Criteria

### Atomic Functionality

- [ ] **Atom Management**
  - Create/read/update atoms
  - 20+ atoms in library across all 4 types
  - Semantic relationships working (synonyms, antonyms, related)

- [ ] **Atomic Requirements**
  - Create requirements with atom composition
  - Template rendering works
  - Can toggle any atom type
  - Validation prevents invalid compositions

- [ ] **Cascading Updates**
  - Atom toggle triggers impact analysis (<500ms)
  - Updates cascade to all affected views
  - Events published via NATS
  - Rollback on failure

- [ ] **Feature Flags**
  - Create/evaluate flags via Unleash
  - Derive product configs from base + flags (<100ms)
  - Export configs to .env files
  - A/B testing supported

- [ ] **Intelligent CRUD**
  - Auto-generate items in 16 views
  - LLM-assisted scaffolding
  - Context-aware generation (learns from codebase)
  - Code files written to disk

- [ ] **Multi-View Integration**
  - All 64 integration points (16 views × 4 atoms) working
  - Changes in any view propagate correctly
  - Traceability links maintained
  - View consistency enforced

- [ ] **Graph Traceability**
  - Recursive queries <500ms
  - Circular dependency detection
  - Impact analysis working
  - Graph visualization in TUI

- [ ] **Versioning**
  - Git-style commits
  - Semantic versioning
  - Time-travel <500ms
  - Atom-aware diffs

- [ ] **Validation**
  - 3-layer pipeline (regex → BERT → LLM)
  - >90% accuracy
  - <$0.01/validation with caching
  - Real-time feedback in CLI

- [ ] **Performance**
  - All targets met (see table below)
  - Load tests pass (1000 reqs, 100 concurrent)
  - Cache hit rates >70%

### Performance Targets

| Operation | Target | Verified By |
|-----------|--------|-------------|
| Atom lookup | <5ms | Benchmark tests |
| Requirement creation | <200ms | Benchmark tests |
| Impact analysis | <500ms | Performance tests |
| Cascade execution | <5s | Integration tests |
| Product derivation | <100ms | Benchmark tests |
| Time-travel | <500ms | Performance tests |
| LLM validation | <3s | Integration tests |
| Graph query (impact) | <500ms | Performance tests |
| Code generation | <10s | Integration tests |

### Quality Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Test count | >400 | TBD |
| Code coverage | ≥85% | TBD |
| Type coverage (mypy) | 100% | TBD |
| Linting (ruff) | Clean | TBD |
| Security (bandit) | Clean | TBD |
| Max module size | ≤350 lines | TBD |
| API endpoints | ~50 | TBD |
| CLI commands | ~30 | TBD |

---

## Weekly Ceremonies

### Monday: Sprint Planning
- Review previous week's deliverables
- Plan current week's tasks
- Assign work to agents (if using BMAD-METHOD style)
- Update todos in trace (dogfooding)

### Wednesday: Mid-Week Review
- Demo progress
- Address blockers
- Adjust priorities if needed

### Friday: Sprint Review + Retro
- Demo completed deliverables
- Run full test suite
- Review coverage and quality metrics
- Update roadmap if needed
- Retrospective (what went well, what to improve)

---

## Risk Management

### High-Priority Risks

**Risk 1: Cascade Complexity Explosion**
- **Probability**: Medium
- **Impact**: High (cascades could affect hundreds of items)
- **Mitigation**:
  - Limit cascade depth (max 5 levels)
  - User confirmation for large cascades (>20 items)
  - Batch mode for performance
  - Rollback mechanism
- **Monitoring**: Track cascade sizes; alert if >100 items

**Risk 2: LLM Generation Quality**
- **Probability**: Medium
- **Impact**: Medium (generated code may be incorrect)
- **Mitigation**:
  - Always scaffold, never overwrite existing code
  - User reviews before applying
  - Test generation for every code generation
  - Template fallback if LLM fails
- **Monitoring**: Track apply rate (% of generated code user keeps)

**Risk 3: Feature Flag Sprawl**
- **Probability**: High
- **Impact**: Medium (100+ flags becomes unmaintainable)
- **Mitigation**:
  - Enforce naming convention
  - Automatic expiration (90 days)
  - Dashboard showing flag age
  - Require justification for permanent flags
- **Monitoring**: Alert if >50 active flags

**Risk 4: Performance Degradation at Scale**
- **Probability**: Medium
- **Impact**: High (system unusable if slow)
- **Mitigation**:
  - Aggressive caching (L1 local + L2 Redis)
  - Materialized views for common queries
  - Async processing for heavy operations
  - Neo4j migration path prepared
- **Monitoring**: Continuous performance tests; alert if p95 >500ms

---

## Testing Strategy

### Test Pyramid

```
           /\
          /E2\      E2E Tests: 50 tests (10%)
         /----\     - Full workflows with real DB/NATS
        /Integ\    Integration Tests: 150 tests (30%)
       /--------\   - Repository tests with SQLite
      /   Unit  \  Unit Tests: 300 tests (60%)
     /------------\ - Domain logic, pure functions
```

### Test Categories

**Unit Tests (300 tests)**:
- Domain models (Atom, AtomicRequirement, UniversalItem)
- Use cases (mocked repositories)
- Validation logic
- Graph algorithms (in-memory graphs)
- Utility functions

**Integration Tests (150 tests)**:
- Repository with real SQLite
- NATS pub/sub with test server
- Event sourcing (event store + replay)
- API endpoints with test client
- LLM integration with mocked responses

**E2E Tests (50 tests)**:
- Full requirement lifecycle (create → toggle → cascade → validate)
- Multi-view consistency
- Product derivation end-to-end
- GitHub sync workflow
- CLI command workflows

### Property-Based Tests

Using Hypothesis for invariant testing:

```python
from hypothesis import given, strategies as st

@given(
    st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    st.sampled_from(list(ViewType))
)
def test_atom_toggle_preserves_requirement_count(atoms: List[str], view_type: ViewType):
    """Property: Toggling atoms doesn't change requirement count."""
    initial_count = len(repository.find_all())

    # Perform atom toggle
    for atom_value in atoms:
        atom = atom_library.find_by_value(atom_value)
        if atom:
            requirement.toggle_atom(atom.type, atom)

    final_count = len(repository.find_all())
    assert initial_count == final_count
```

### Performance Tests

```python
@pytest.mark.performance
def test_cascade_performance_target():
    """Verify cascade completes within 5s for typical case."""
    req = create_test_requirement_with_50_derived_items()

    start = time()
    cascade_result = cascade_engine.execute_cascade(...)
    duration = time() - start

    assert duration < 5.0, f"Cascade took {duration}s (target: <5s)"
```

---

## Deployment Strategy

### Development Environment

```yaml
# docker-compose.dev.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trace_dev
      POSTGRES_USER: trace
      POSTGRES_PASSWORD: trace_dev_password

  nats:
    image: nats:latest
    command: "-js"  # Enable JetStream

  redis:
    image: redis:7-alpine

  unleash:
    image: unleashorg/unleash-server:latest
    environment:
      DATABASE_URL: postgres://postgres:unleash@unleash-db:5432/unleash

  trace-api:
    build: .
    command: uvicorn api.main:app --reload
    volumes:
      - ./src:/app/src
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://trace:trace_dev_password@postgres:5432/trace_dev
      NATS_URL: nats://nats:4222
      REDIS_URL: redis://redis:6379
      UNLEASH_URL: http://unleash:4242
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
```

### Production Environment

```yaml
# production deployment (Kubernetes/Railway/Fly.io)
services:
  - trace-api (3 replicas, auto-scaling)
  - postgres (managed: Supabase/Neon)
  - nats (managed cluster, 3 nodes)
  - redis (managed: Upstash)
  - unleash (managed or self-hosted)

observability:
  - logs: structured JSON to Datadog
  - metrics: Prometheus + Grafana
  - traces: OpenTelemetry → Jaeger
  - alerts: PagerDuty
```

---

## Migration Path

### From Existing Trace System (Non-Atomic) to Atomic

**Scenario**: User has existing trace installation with 500 requirements in 16 views.

**Strategy**: Progressive migration, not big-bang

**Phase 1: Install Atomic System (Week 1)**
- Deploy atomic tables alongside existing tables
- No breaking changes to existing system
- Users can choose: create old-style req OR atomic req

**Phase 2: Migrate High-Value Requirements (Weeks 2-4)**
- Identify 20 most-referenced requirements
- Use LLM to decompose into atomic format
- Human reviews/approves decomposition
- Link atomic version to original (bidirectional)
- Keep both during transition

**Phase 3: Auto-Convert Remaining (Weeks 5-6)**
- LLM batch-processes remaining 480 requirements
- Human reviews batches of 50
- Auto-conversion for simple requirements
- Manual review for complex ones

**Phase 4: Deprecate Old Model (Week 7)**
- All requirements migrated
- Remove old non-atomic tables
- Update all APIs to atomic-only
- Final data verification

**Migration Script**:
```python
# scripts/migrate_to_atomic.py

async def migrate_requirement_to_atomic(
    old_req: UniversalItem,  # Old style (FEATURE view)
    llm_client,
    atom_library
) -> AtomicRequirement:
    """Convert non-atomic requirement to atomic format.

    Uses LLM to decompose requirement into atoms.
    """

    # 1. LLM analyzes requirement and extracts atoms
    prompt = f"""
    Decompose this requirement into atomic components:

    Title: {old_req.title}
    Description: {old_req.description}

    Identify:
    - Subject (who/what): [user, agent, system, ...]
    - Action (what is done): [create, login, approve, ...]
    - Method (how): [email-password, oauth2, api-key, ...]
    - Interface (where): [web-ui, mobile-app, rest-api, ...]

    Return JSON with atom values.
    """

    decomposition = await llm_client.complete(prompt, response_format="json")

    # 2. Find matching atoms from library
    atoms = {}
    for atom_type, atom_value in decomposition.items():
        atom = atom_library.find_by_value(atom_value)
        if not atom:
            # Create new atom if doesn't exist
            atom = Atom(
                id=uuid4(),
                type=AtomType(atom_type),
                value=atom_value,
                label=atom_value.replace("-", " ").title(),
                scope=infer_scope(atom_value)
            )
            await atom_library.save(atom)

        atoms[AtomType(atom_type)] = atom

    # 3. Create atomic requirement
    atomic_req = AtomicRequirement(
        id=old_req.id,  # Keep same ID
        template="[{subject}] can [{action}] with [{method}] via [{interface}]",
        atoms=atoms,
        description=old_req.description,
        acceptance_criteria=extract_acceptance_criteria(old_req.description),
        created_at=old_req.created_at,
        created_by=old_req.created_by,
        version=old_req.version if hasattr(old_req, 'version') else 1
    )

    return atomic_req
```

---

## Appendix: Complete CLI Reference

### Atom Management

```bash
# List atoms
trace atom list
trace atom list --type subject
trace atom list --scope authentication

# Create atom
trace atom create --type subject --value user --label "User"
trace atom create --interactive  # Wizard

# Show atom details
trace atom show <atom-id>
trace atom show <atom-id> --related
trace atom show <atom-id> --requirements  # Show reqs using this atom

# Find atoms
trace atom find "oauth"
trace atom find --semantic "authentication"  # Semantic search
```

### Atomic Requirement Management

```bash
# Create atomic requirement
trace req create --template "[{subject}] can [{action}] with [{method}] via [{interface}]" \
  --atom subject=user --atom action=login --atom method=oauth2 --atom interface=web-ui \
  --auto-generate  # Auto-generate across all views

trace req create --interactive  # Wizard

# Show requirement
trace req show FR-001
trace req show FR-001 --render  # Show rendered natural language
trace req show FR-001 --derived  # Show all derived items across views

# Toggle atom
trace atom toggle FR-001 --atom method --new oauth2 --preview  # Dry run
trace atom toggle FR-001 --atom method --new oauth2  # Apply

# Validate
trace validate FR-001
trace validate --all
trace validate --check-duplicates
```

### Feature Flags

```bash
# List flags
trace flag list
trace flag list --requirement FR-001

# Create flag
trace flag create --key ff_oauth2_google --name "Google OAuth" --default false

# Evaluate flag (testing)
trace flag evaluate ff_oauth2_google --env production --tenant acme

# Product derivation
trace product derive --env production --tenant acme --output acme-prod.json
trace product export --config acme-prod.json --output .env.acme.prod
```

### Impact Analysis

```bash
# Analyze impact of proposed change
trace impact analyze FR-001 --toggle method=oauth2

# Show cascade preview
trace cascade preview FR-001 --atom method --new oauth2

# Execute cascade
trace cascade execute FR-001 --atom method --new oauth2
```

### Graph Queries

```bash
# Find requirements using atom
trace graph find-by-atom oauth2

# Dependency analysis
trace graph dependencies FR-001
trace graph dependents FR-001

# Circular dependency detection
trace graph check-cycles

# Critical path
trace graph critical-path

# Visualize
trace graph show FR-001 --depth 3 --format dot
```

### Batch Operations

```bash
# Batch create from template
trace batch create --template crud --entity User --auto-generate

# Batch toggle
trace batch toggle --file atom-toggles.json --preview
```

### GitHub Integration

```bash
# Sync to GitHub
trace github sync FR-001
trace github sync --all

# Generate Issues from requirements
trace github export --filter status=active
```

---

## Appendix: Database Schema

### Complete PostgreSQL Schema with Atomic Extensions

```sql
-- ===== Atoms Table =====
CREATE TABLE atoms (
    id UUID PRIMARY KEY,
    type TEXT NOT NULL,  -- subject, action, method, interface
    value TEXT NOT NULL UNIQUE,  -- Slug: "oauth2", "user", "web-ui"
    label TEXT NOT NULL,  -- Display: "OAuth 2.0", "User", "Web UI"
    description TEXT,
    scope TEXT NOT NULL,  -- authentication, data_storage, etc.

    -- Semantic relationships (JSONB for flexibility)
    synonyms JSONB DEFAULT '[]'::jsonb,
    antonyms JSONB DEFAULT '[]'::jsonb,
    related JSONB DEFAULT '[]'::jsonb,  -- Array of UUIDs
    compatible_with JSONB DEFAULT '{}'::jsonb,  -- {atom_type: [uuid, ...]}
    conflicts_with JSONB DEFAULT '[]'::jsonb,

    -- Implementation tracking
    implementations JSONB DEFAULT '[]'::jsonb,  -- ["auth0", "authkit"]
    default_implementation TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by TEXT DEFAULT 'system',

    CONSTRAINT atoms_value_format CHECK (value ~ '^[a-z0-9-]+$')
);

CREATE INDEX idx_atoms_type ON atoms(type);
CREATE INDEX idx_atoms_value ON atoms(value);
CREATE INDEX idx_atoms_scope ON atoms(scope);
CREATE INDEX idx_atoms_implementations ON atoms USING gin(implementations);

-- ===== Atomic Requirements Table =====
CREATE TABLE atomic_requirements (
    id TEXT PRIMARY KEY,  -- FR-001, STORY-042, REQ-1.2.3
    template TEXT NOT NULL,  -- "[{subject}] can [{action}]..."
    atoms JSONB NOT NULL,  -- {atom_type: {id, value, label, ...}}

    -- Requirement details
    title TEXT,  -- Auto-generated or custom
    description TEXT,
    acceptance_criteria JSONB DEFAULT '[]'::jsonb,
    priority INTEGER DEFAULT 50,
    status TEXT DEFAULT 'draft',

    -- Implementation tracking
    implementation_variant TEXT,  -- "auth0", "authkit", null
    is_implemented BOOLEAN DEFAULT FALSE,
    implementation_status TEXT DEFAULT 'planned',  -- planned, flagged, active, deprecated
    flag_key TEXT,  -- Feature flag controlling activation

    -- Composition
    parent_id TEXT REFERENCES atomic_requirements(id),
    composition_rule TEXT DEFAULT 'AND',  -- AND, OR, XOR

    -- Traceability (to UniversalItems in 16 views)
    derived_items JSONB DEFAULT '{}'::jsonb,  -- {view_type: [uuid, ...]}

    -- Versioning
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by TEXT DEFAULT 'system',

    CONSTRAINT atomic_requirements_atoms_valid CHECK (
        jsonb_typeof(atoms) = 'object'
    )
);

CREATE INDEX idx_atomic_reqs_status ON atomic_requirements(status);
CREATE INDEX idx_atomic_reqs_parent ON atomic_requirements(parent_id);
CREATE INDEX idx_atomic_reqs_flag ON atomic_requirements(flag_key);
CREATE INDEX idx_atomic_reqs_atoms ON atomic_requirements USING gin(atoms);
CREATE INDEX idx_atomic_reqs_derived ON atomic_requirements USING gin(derived_items);

-- ===== Derived Items Table (Traceability Layer) =====
CREATE TABLE derived_items (
    item_id UUID NOT NULL,  -- References universal_items.id
    source_requirement_id TEXT NOT NULL REFERENCES atomic_requirements(id) ON DELETE CASCADE,
    source_atoms JSONB NOT NULL,  -- Array of atom UUIDs that generated this
    view_type TEXT NOT NULL,  -- Which view this item belongs to
    generation_rule TEXT NOT NULL,  -- How this was generated

    -- Synchronization
    auto_update BOOLEAN DEFAULT TRUE,  -- Auto-update when atoms change?
    last_synced TIMESTAMPTZ DEFAULT now(),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),

    PRIMARY KEY (item_id, source_requirement_id),
    FOREIGN KEY (item_id) REFERENCES universal_items(id) ON DELETE CASCADE
);

CREATE INDEX idx_derived_source_req ON derived_items(source_requirement_id);
CREATE INDEX idx_derived_view_type ON derived_items(view_type);
CREATE INDEX idx_derived_source_atoms ON derived_items USING gin(source_atoms);

-- ===== Implementation Variants Table =====
CREATE TABLE implementation_variants (
    id UUID PRIMARY KEY,
    atom_id UUID NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,  -- "auth0", "authkit", "stripe"
    display_name TEXT NOT NULL,

    -- Implementation status
    is_implemented BOOLEAN DEFAULT FALSE,
    library TEXT,  -- NPM/PyPI package
    config_required JSONB DEFAULT '{}'::jsonb,

    -- Toggle control
    is_active BOOLEAN DEFAULT FALSE,
    can_toggle BOOLEAN DEFAULT TRUE,

    -- Metadata
    vendor TEXT,
    cost TEXT,
    docs_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(atom_id, name)
);

CREATE INDEX idx_variants_atom ON implementation_variants(atom_id);
CREATE INDEX idx_variants_active ON implementation_variants(is_active) WHERE is_active = TRUE;

-- ===== Feature Flags Table =====
CREATE TABLE feature_flags (
    key TEXT PRIMARY KEY,  -- ff_oauth2_enabled
    name TEXT NOT NULL,
    description TEXT,
    flag_type TEXT NOT NULL,  -- release, operational, experimental, permission, implementation
    default_enabled BOOLEAN DEFAULT FALSE,

    -- Targeting (Unleash strategies stored as JSONB)
    strategies JSONB DEFAULT '[]'::jsonb,

    -- Associated requirements
    controls_requirements JSONB DEFAULT '[]'::jsonb,

    -- Lifecycle
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,
    owner TEXT,

    -- Metrics
    evaluation_count BIGINT DEFAULT 0,
    last_evaluated TIMESTAMPTZ
);

CREATE INDEX idx_flags_type ON feature_flags(flag_type);
CREATE INDEX idx_flags_expires ON feature_flags(expires_at) WHERE expires_at IS NOT NULL;

-- ===== Atom View Mappings Table =====
CREATE TABLE atom_view_mappings (
    atom_id UUID NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    atom_type TEXT NOT NULL,  -- SUBJECT, ACTION, METHOD, INTERFACE
    view_type TEXT NOT NULL,  -- FEATURE, CODE, TEST, API, etc.

    -- Mapping rules
    affects_title BOOLEAN DEFAULT FALSE,
    affects_description BOOLEAN DEFAULT FALSE,
    affects_code BOOLEAN DEFAULT FALSE,
    affects_tests BOOLEAN DEFAULT FALSE,
    affects_config BOOLEAN DEFAULT FALSE,

    -- Templates
    title_template TEXT,
    description_template TEXT,
    code_template TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),

    PRIMARY KEY (atom_id, atom_type, view_type)
);

CREATE INDEX idx_mappings_view ON atom_view_mappings(view_type);

-- ===== Event Store Table (Atomic Events) =====
CREATE TABLE atomic_requirement_events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id TEXT NOT NULL,  -- Requirement ID
    event_type TEXT NOT NULL,  -- atom.toggled, variant.set, cascade.started, etc.
    timestamp TIMESTAMPTZ DEFAULT now(),
    event_data JSONB NOT NULL,
    user_id TEXT,
    caused_by TEXT,  -- For cascading events

    CONSTRAINT events_aggregate_not_empty CHECK (aggregate_id <> '')
);

CREATE INDEX idx_events_aggregate ON atomic_requirement_events(aggregate_id, timestamp);
CREATE INDEX idx_events_type ON atomic_requirement_events(event_type);
CREATE INDEX idx_events_timestamp ON atomic_requirement_events(timestamp DESC);

-- ===== Future Implementation Flags =====
CREATE TABLE future_implementation_flags (
    id UUID PRIMARY KEY,
    atom_id UUID NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    planned_implementation TEXT NOT NULL,
    target_date DATE,
    assigned_to TEXT,
    priority INTEGER DEFAULT 50,

    -- Blockers
    blocked_by JSONB DEFAULT '[]'::jsonb,
    blocking JSONB DEFAULT '[]'::jsonb,

    -- Status
    status TEXT DEFAULT 'planned',  -- planned, in_progress, implemented, cancelled
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_future_flags_atom ON future_implementation_flags(atom_id);
CREATE INDEX idx_future_flags_status ON future_implementation_flags(status);
CREATE INDEX idx_future_flags_target_date ON future_implementation_flags(target_date);

-- ===== Views for Performance =====

-- Materialized view: Requirements by atom
CREATE MATERIALIZED VIEW requirements_by_atom AS
SELECT
    ar.id AS requirement_id,
    ar.title,
    ar.status,
    ar.implementation_variant,
    jsonb_each_text(ar.atoms) AS atom_entry,
    (jsonb_each_text(ar.atoms)).key AS atom_type,
    (jsonb_each_text(ar.atoms)).value::jsonb->>'value' AS atom_value
FROM atomic_requirements ar;

CREATE INDEX idx_req_by_atom_value ON requirements_by_atom(atom_value);
CREATE INDEX idx_req_by_atom_type ON requirements_by_atom(atom_type);

-- Refresh strategy: on every requirement update (or periodic)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY requirements_by_atom;
```

---

## Appendix: File Structure

### Complete Project Structure with Atomic Extensions

```
trace/
├── openspec/
│   ├── specs/
│   ├── changes/
│   ├── archive/
│   ├── templates/
│   ├── constitution.md
│   └── AGENTS.md
│
├── src/trace/
│   ├── domain/  # Clean Layer 1: Entities
│   │   ├── models.py               # UniversalItem, ViewType, LinkType (✅ existing)
│   │   ├── atoms.py                # Atom, AtomType, AtomScope (NEW)
│   │   ├── atomic_requirements.py  # AtomicRequirement, AtomChange (NEW)
│   │   ├── feature_flags.py        # FeatureFlag, FlagStrategy (NEW)
│   │   ├── derived_items.py        # DerivedItem, traceability (NEW)
│   │   └── exceptions.py           # Domain exceptions
│   │
│   ├── application/  # Clean Layer 2: Use Cases
│   │   ├── ports/
│   │   │   ├── repository.py            # ItemRepositoryPort (✅ existing)
│   │   │   ├── atom_repository.py       # AtomRepositoryPort (NEW)
│   │   │   ├── atomic_req_repository.py # AtomicRequirementRepositoryPort (NEW)
│   │   │   ├── event_store.py           # EventStorePort (✅ existing)
│   │   │   └── flag_service.py          # FeatureFlagServicePort (NEW)
│   │   │
│   │   └── services/
│   │       ├── item_service.py              # Item CRUD (✅ existing)
│   │       ├── atom_service.py              # Atom CRUD (NEW)
│   │       ├── atomic_requirement_service.py # Atomic req CRUD (NEW)
│   │       ├── impact_analyzer.py           # AtomicImpactAnalyzer (NEW)
│   │       ├── cascading_update_engine.py   # CascadingUpdateEngine (NEW)
│   │       ├── intelligent_crud_engine.py   # Auto-generation (NEW)
│   │       ├── product_derivation_engine.py # ProductDerivationEngine (NEW)
│   │       └── validation_pipeline.py       # ValidationPipeline (NEW)
│   │
│   └── infrastructure/  # Clean Layer 3: Adapters
│       ├── persistence/
│       │   ├── sqlite_repository.py       # SQLiteItemRepository (✅ existing)
│       │   ├── sqlite_atom_repository.py  # Atom persistence (NEW)
│       │   ├── sqlite_atomic_req_repository.py  # Atomic req persistence (NEW)
│       │   ├── event_store_pg.py          # PostgreSQL event store (✅ existing)
│       │   └── schema.sql                 # Complete schema with atomic tables (NEW)
│       │
│       ├── messaging/
│       │   ├── nats_client.py             # NATS connection (✅ existing)
│       │   ├── event_publisher.py         # Publish to NATS (✅ existing)
│       │   ├── event_consumer.py          # Consume from NATS (✅ existing)
│       │   └── cascade_consumer.py        # Handle cascade events (NEW)
│       │
│       ├── external/
│       │   ├── unleash_client.py          # Feature flags (NEW)
│       │   ├── claude_client.py           # LLM integration (NEW)
│       │   ├── github_client.py           # GitHub API (NEW)
│       │   └── sentence_transformer.py    # NLP/BERT (NEW)
│       │
│       ├── cli/
│       │   ├── main.py                    # Typer app (✅ existing)
│       │   ├── atom_commands.py           # Atom management (NEW)
│       │   ├── atomic_req_commands.py     # Atomic req management (NEW)
│       │   ├── flag_commands.py           # Feature flag management (NEW)
│       │   ├── cascade_commands.py        # Cascade operations (NEW)
│       │   └── graph_commands.py          # Graph queries (NEW)
│       │
│       └── tui/
│           ├── main_app.py                # Textual TUI (existing)
│           ├── atom_browser.py            # Browse atoms (NEW)
│           ├── requirement_editor.py      # Edit atomic reqs (NEW)
│           ├── graph_visualizer.py        # Graph rendering (NEW)
│           └── cascade_monitor.py         # Monitor cascades (NEW)
│
├── data/
│   ├── atoms.json           # Seed atom library (NEW)
│   ├── templates/           # Scaffold templates (NEW)
│   │   ├── code/
│   │   ├── test/
│   │   └── api/
│   └── examples/            # Example atomic requirements (NEW)
│
├── docs/
│   ├── ATOMIC_TRACE_ARCHITECTURE.md  # This document
│   ├── ATOMIC_REQUIREMENTS_RESEARCH.md
│   ├── TECH_STACK_VALIDATION.md
│   ├── COMPREHENSIVE_ARCHITECTURE_DESIGN.md  # Update with atomic model
│   └── tutorials/
│       ├── creating-atomic-requirements.md
│       ├── toggling-atoms.md
│       └── using-feature-flags.md
│
└── tests/
    ├── unit/
    │   ├── domain/
    │   │   ├── test_atoms.py               # Atom tests (NEW, 15+ tests)
    │   │   ├── test_atomic_requirements.py # Atomic req tests (NEW, 20+ tests)
    │   │   └── test_feature_flags.py       # Flag tests (NEW, 10+ tests)
    │   ├── application/
    │   │   ├── test_impact_analyzer.py     # Impact tests (NEW, 15+ tests)
    │   │   ├── test_cascade_engine.py      # Cascade tests (NEW, 20+ tests)
    │   │   └── test_intelligent_crud.py    # Generation tests (NEW, 25+ tests)
    │   └── infrastructure/
    │       └── test_unleash_client.py      # Flag service tests (NEW, 10+ tests)
    │
    ├── integration/
    │   ├── test_atomic_repository.py       # Atom persistence (NEW, 15+ tests)
    │   ├── test_cascade_flow.py            # Full cascade (NEW, 20+ tests)
    │   ├── test_product_derivation.py      # Flag-based derivation (NEW, 15+ tests)
    │   └── test_github_sync.py             # GitHub integration (NEW, 10+ tests)
    │
    └── e2e/
        ├── test_atomic_requirement_lifecycle.py  # Create → Toggle → Cascade (NEW, 10 tests)
        ├── test_multi_view_consistency.py        # 16-view sync (NEW, 10 tests)
        └── test_feature_flag_workflow.py         # Flag → Product (NEW, 5 tests)
```

---

## Summary

**Total Duration**: 20 weeks
**Total Tests**: 450+ (300 unit, 150 integration, 50 E2E)
**Total Modules**: ~80 (all ≤350 lines)
**Total Documentation**: ~120,000 words across all docs

**Atomic Features Delivered**:
- ✅ Atom entity model with 115+ atoms
- ✅ Atomic requirement composition
- ✅ Cascading updates across 16 views
- ✅ Feature flag integration (Unleash)
- ✅ Implementation variant toggles
- ✅ Future implementation tracking
- ✅ LLM-assisted generation
- ✅ Graph traceability with impact analysis
- ✅ Event-sourced audit trail
- ✅ Product derivation from base + flags
- ✅ Complete CLI (30+ commands)
- ✅ Rich TUI with graph visualization
- ✅ GitHub integration
- ✅ Performance targets met

**Ready for Production**: After Week 20, system is production-ready for orchestrating 1000+ AI agents with atomic, composable requirements.

---

**Last Updated**: 2025-11-20
**Next Steps**: Begin Week 1 implementation following this roadmap
**Status**: Ready for execution
