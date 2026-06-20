# Phase 3 Implementation Guide: Complexity Refactoring

**Status**: Ready for Execution
**Created**: 2026-02-02
**Estimated Duration**: 8-20 agent-hours (wall clock)
**Dependencies**: Phase 1 (Configuration), Phase 2 (Critical Violations)

---

## Executive Summary

Phase 3 focuses on **complexity refactoring** to address P1/P2 linting violations across all three codebases. This phase targets the technical debt captured in Phase 1 baselines but deferred from Phase 2's critical security/correctness focus.

### Baseline Snapshot (Phase 1)

From CHANGELOG.md and baseline files:

- **Python Backend**: 15,952 total violations
  - 248 C901 (complex-structure)
  - 220 PLR0913 (too-many-arguments)
  - 54 PLR0912 (too-many-branches)
  - 42 PLR0915 (too-many-statements)
  - 40 PLR1702 (too-many-nested-blocks)
  - **604 complexity violations** (Phase 3 target)

- **Go Backend**: ~13,000+ violations (from baseline run)
  - funlen (function length: 80 lines, 50 statements)
  - gocyclo (cyclomatic complexity: 10)
  - gocognit (cognitive complexity: 12)
  - dupl (code duplication)
  - goconst (magic strings)
  - mnd (magic numbers)

- **Frontend**: 502,822 baseline lines (oxlint output)
  - jsx-max-depth violations
  - complexity violations  
  - import/no-cycle
  - typescript/no-floating-promises

### Phase 3 Targets

**Primary Goals**:
1. **Reduce Python complexity violations by 70%** (604 → ~180)
2. **Reduce Go complexity violations by 60%** (~2,800 → ~1,100)
3. **Reduce Frontend jsx-depth violations by 50%** (TBD → TBD/2)
4. **No new violations introduced** (strict baseline enforcement)

**Success Criteria**:
- All CI checks pass with new baselines
- Code coverage maintained or improved (>85%)
- No production functionality regressions
- Improved maintainability metrics (complexity scores)

---

## Work Breakdown Structure (WBS)

### Phase 3.1: Discovery & Planning (0.5-1 agent-hour)

**Tasks**:
- [x] Analyze Phase 1/2 completion reports (this document)
- [x] Extract violation counts by category and file
- [ ] Create DAG for workstream dependencies
- [ ] Establish tracking metrics and dashboards

**Deliverables**:
- This implementation guide
- Task dependency graph
- Progress tracking structure

**Agent Assignment**: Strategic planning (no delegation)

---

### Phase 3.2: Python Backend Refactoring (3-6 agent-hours)

#### Workstream 3.2.1: Complex Functions (C901)
**Priority**: P1 (highest impact)
**Target**: 248 violations → 75 violations (70% reduction)
**Complexity**: High

**Approach**:
1. **Extract sub-functions** for complex logic blocks
2. **Apply strategy pattern** for multi-branch conditionals
3. **Create service classes** for stateful operations
4. **Use decorators** for cross-cutting concerns

**High-Impact Files** (from baseline sample):
- `alembic/versions/*.py` - Migration functions (137+ statements)
- `scripts/consolidate-docs/*.py` - Document processing
- API endpoint handlers with complex business logic

**Agent Delegation Strategy**:
- **Agent 1**: Alembic migrations (20-30 files, extract helpers)
- **Agent 2**: Script consolidation (scan_docs, scan_aggressive)
- **Agent 3**: API handlers (identify via grep, extract services)

**Dependencies**: None (parallelizable)

**Success Metrics**:
- McCabe complexity ≤7 for all functions
- New helper functions have tests
- No logic changes (behavior-preserving refactors only)

---

#### Workstream 3.2.2: Too Many Arguments (PLR0913)
**Priority**: P2
**Target**: 220 violations → 65 violations (70% reduction)
**Complexity**: Medium

**Approach**:
1. **Introduce parameter objects** (dataclasses/Pydantic models)
2. **Extract configuration classes** for option-heavy functions
3. **Use builder pattern** for complex construction
4. **Apply dependency injection** for services

**Refactoring Patterns**:
```python
# Before: Too many arguments
def process_item(id, name, type, status, config, metadata, user_id, project_id):
    ...

# After: Parameter object
@dataclass
class ItemProcessingParams:
    id: str
    name: str
    type: ItemType
    status: Status
    config: dict
    metadata: dict
    user_id: str
    project_id: str

def process_item(params: ItemProcessingParams):
    ...
```

**Agent Delegation Strategy**:
- **Agent 4**: Identify functions with >5 args, create parameter objects
- **Agent 5**: Update call sites, ensure type safety

**Dependencies**: After Agent 1-3 (function extraction may reduce arg counts)

**Success Metrics**:
- Max 5 arguments per function
- All parameter objects have Pydantic validation
- Type hints maintained

---

#### Workstream 3.2.3: Too Many Branches/Statements (PLR0912/PLR0915)
**Priority**: P2
**Target**: 96 violations → 30 violations (70% reduction)
**Complexity**: Medium

**Approach**:
1. **Extract conditional logic** to separate functions
2. **Use polymorphism** for type-based branching
3. **Apply early returns** to reduce nesting
4. **Create lookup tables** for multi-case logic

**Agent Delegation Strategy**:
- **Agent 6**: Refactor branching logic (PLR0912)
- **Agent 7**: Break down long functions (PLR0915)

**Dependencies**: After Workstream 3.2.1 (overlaps with C901)

---

#### Workstream 3.2.4: Nested Blocks (PLR1702)
**Priority**: P3
**Target**: 40 violations → 12 violations (70% reduction)
**Complexity**: Low

**Approach**:
1. **Invert conditionals** (early exit pattern)
2. **Extract nested loops** to helper functions
3. **Use guard clauses** to reduce indentation

**Agent Delegation Strategy**:
- **Agent 8**: Flatten nested structures

**Dependencies**: After Workstream 3.2.1-3 (may be resolved by earlier refactors)

---

### Phase 3.3: Go Backend Refactoring (3-6 agent-hours)

#### Workstream 3.3.1: Function Length (funlen)
**Priority**: P1
**Target**: ~800 violations → ~250 violations (70% reduction)
**Complexity**: High

**Limits**:
- Max 80 lines per function
- Max 50 statements per function

**Approach**:
1. **Extract helper functions** for logical blocks
2. **Create service methods** for complex operations
3. **Apply builder pattern** for multi-step construction
4. **Use table-driven tests** to reduce test verbosity

**High-Impact Patterns** (from sample):
- Duplicate code in `distributed_coordination.go` (lock release logic)
- Test setup/teardown in `cache_interface_test.go`
- Complex HTTP handlers in API layer

**Agent Delegation Strategy**:
- **Agent 9**: Internal services (agents/, cache/, tracing/)
- **Agent 10**: API handlers (handlers/, middleware/)
- **Agent 11**: Test cleanup (extract test helpers)

**Dependencies**: None (parallelizable)

**Success Metrics**:
- All functions ≤80 lines, ≤50 statements
- Extracted helpers have unit tests
- No performance regressions

---

#### Workstream 3.3.2: Cyclomatic Complexity (gocyclo)
**Priority**: P1
**Target**: ~600 violations → ~180 violations (70% reduction)
**Complexity**: High

**Limit**: Max complexity 10

**Approach**:
1. **Extract conditional branches** to separate functions
2. **Use switch statements** over nested if/else
3. **Apply strategy pattern** for algorithmic variation
4. **Create lookup maps** for multi-case logic

**Agent Delegation Strategy**:
- **Agent 12**: Reduce gocyclo in business logic
- **Agent 13**: Simplify control flow in handlers

**Dependencies**: After Workstream 3.3.1 (function extraction reduces complexity)

---

#### Workstream 3.3.3: Code Duplication (dupl)
**Priority**: P2
**Target**: ~400 violations → ~120 violations (70% reduction)
**Complexity**: Medium

**Approach**:
1. **Extract common logic** to shared functions
2. **Create generic helpers** for repeated patterns
3. **Apply template pattern** for similar structures
4. **Use interfaces** for polymorphic behavior

**Example** (from baseline):
```go
// Duplicate: CompleteCoordinatedUpdate and CancelOperation
// Extract common pattern:
func (dc *DistributedCoordinator) updateOperationStatus(
    ctx context.Context, operationID, agentID, status string,
) error {
    // Common logic for both completion and cancellation
    // Release locks, update status, clean up
}
```

**Agent Delegation Strategy**:
- **Agent 14**: Extract duplicated logic across services

**Dependencies**: After Workstream 3.3.1-2 (may reduce duplication)

---

#### Workstream 3.3.4: Magic Numbers/Strings (mnd, goconst)
**Priority**: P3
**Target**: ~1,000 violations → ~300 violations (70% reduction)
**Complexity**: Low

**Approach**:
1. **Define constants** for magic values
2. **Create enums** for string/number sets
3. **Use configuration** for environment-specific values
4. **Extract to constants package** for shared values

**Agent Delegation Strategy**:
- **Agent 15**: Replace magic numbers with named constants
- **Agent 16**: Replace magic strings with const declarations

**Dependencies**: None (low risk, parallelizable)

---

### Phase 3.4: Frontend Refactoring (2-4 agent-hours)

#### Workstream 3.4.1: JSX Depth (jsx-max-depth)
**Priority**: P1
**Target**: TBD violations → 50% reduction
**Complexity**: High

**Approach**:
1. **Extract sub-components** for nested JSX
2. **Create container/presentational split** for complex views
3. **Use composition** over deep nesting
4. **Apply compound component pattern** for related elements

**Example Pattern**:
```tsx
// Before: Deep nesting
<div>
  <div>
    <div>
      <div>
        <div>
          <span>{content}</span>
        </div>
      </div>
    </div>
  </div>
</div>

// After: Component extraction
const ContentWrapper = ({ children }) => <div><span>{children}</span></div>;
const NestedContainer = ({ children }) => <div><div>{children}</div></div>;
// Compose instead of nest
```

**Agent Delegation Strategy**:
- **Agent 17**: Refactor complex view components (ItemsTableView, etc.)
- **Agent 18**: Extract reusable presentational components

**Dependencies**: None (parallelizable)

---

#### Workstream 3.4.2: Complexity (complexity-related rules)
**Priority**: P2
**Target**: TBD violations → 60% reduction
**Complexity**: Medium

**Approach**:
1. **Extract custom hooks** for complex logic
2. **Move business logic** to services/utils
3. **Simplify conditional rendering** (guard clauses)
4. **Use lookup objects** for multi-case rendering

**Agent Delegation Strategy**:
- **Agent 19**: Extract hooks and simplify components
- **Agent 20**: Move logic to services

**Dependencies**: After Workstream 3.4.1 (component extraction may reduce complexity)

---

#### Workstream 3.4.3: Import Cycles (import/no-cycle)
**Priority**: P2
**Target**: Resolve all cycles
**Complexity**: Medium

**Approach**:
1. **Identify cycle groups** (via oxlint output)
2. **Extract shared types** to separate files
3. **Apply dependency inversion** for circular deps
4. **Restructure modules** for unidirectional dependencies

**Agent Delegation Strategy**:
- **Agent 21**: Analyze and break import cycles

**Dependencies**: After Workstream 3.4.1-2 (restructuring may introduce/resolve cycles)

---

## Dependency Graph (DAG)

```
Phase 3.1 (Planning)
    ↓
    ├─→ Phase 3.2 (Python) ──┐
    │   ├─→ 3.2.1 (C901) ────┤
    │   ├─→ 3.2.2 (args) ←───┤
    │   ├─→ 3.2.3 (branches) ←┤
    │   └─→ 3.2.4 (nesting) ←─┤
    │                          │
    ├─→ Phase 3.3 (Go) ────────┤
    │   ├─→ 3.3.1 (funlen) ───┤
    │   ├─→ 3.3.2 (gocyclo) ←─┤
    │   ├─→ 3.3.3 (dupl) ←────┤
    │   └─→ 3.3.4 (magic) ────┤ (parallel)
    │                          │
    └─→ Phase 3.4 (Frontend) ──┤
        ├─→ 3.4.1 (jsx-depth) ┤
        ├─→ 3.4.2 (complex) ←─┤
        └─→ 3.4.3 (cycles) ←──┘
            ↓
        Verification & Baselines
```

**Parallelization Opportunities**:
- All Python agents (1-8) can run concurrently after planning
- All Go agents (9-16) can run concurrently after planning
- All Frontend agents (17-21) can run concurrently after planning
- **Max concurrent**: 21 agents (3 language streams)
- **Recommended**: 3-5 agents per wave (monitor quality)

---

## Tracking & Metrics

### Progress Dashboard

**Phase 3.2 - Python Backend**
| Workstream | Target Reduction | Current | Target | Status |
|------------|------------------|---------|--------|--------|
| C901 (complexity) | 70% | 248 | 75 | 🔴 Not Started |
| PLR0913 (args) | 70% | 220 | 65 | 🔴 Not Started |
| PLR0912 (branches) | 70% | 54 | 16 | 🔴 Not Started |
| PLR0915 (statements) | 70% | 42 | 13 | 🔴 Not Started |
| PLR1702 (nesting) | 70% | 40 | 12 | 🔴 Not Started |

**Phase 3.3 - Go Backend**
| Workstream | Target Reduction | Current | Target | Status |
|------------|------------------|---------|--------|--------|
| funlen | 70% | ~800 | ~250 | 🔴 Not Started |
| gocyclo | 70% | ~600 | ~180 | 🔴 Not Started |
| dupl | 70% | ~400 | ~120 | 🔴 Not Started |
| mnd/goconst | 70% | ~1000 | ~300 | 🔴 Not Started |

**Phase 3.4 - Frontend**
| Workstream | Target Reduction | Current | Target | Status |
|------------|------------------|---------|--------|--------|
| jsx-max-depth | 50% | TBD | TBD/2 | 🔴 Not Started |
| complexity | 60% | TBD | TBD | 🔴 Not Started |
| import/no-cycle | 100% | TBD | 0 | 🔴 Not Started |

### Completion Criteria

**Definition of Done (DoD)**:
- [ ] All targeted violations reduced to goal threshold
- [ ] CI passes with updated baselines
- [ ] Test coverage ≥85% (no reduction)
- [ ] All new functions have tests
- [ ] No production regressions (smoke tests pass)
- [ ] Code review completed (architecture validation)
- [ ] Documentation updated (if patterns changed)

**Verification Commands**:
```bash
# Python
ruff check --select C901,PLR0912,PLR0913,PLR0915,PLR1702 --statistics

# Go
cd backend && golangci-lint run --max-issues-per-linter=0 --max-same-issues=0 ./...

# Frontend
bun run --cwd frontend/apps/web lint --max-warnings 0

# Tests
make test  # All suites must pass
```

---

## Risk Management

### High-Risk Areas

1. **Alembic Migrations** (Python)
   - **Risk**: Breaking database upgrades/downgrades
   - **Mitigation**: Test migrations on copy of production schema, keep complexity reduction minimal

2. **API Handlers** (Go)
   - **Risk**: Breaking request/response contracts
   - **Mitigation**: Run integration tests, verify OpenAPI spec unchanged

3. **Complex Views** (Frontend)
   - **Risk**: Breaking user interactions, state management
   - **Mitigation**: E2E tests for all refactored components, visual regression testing

### Rollback Plan

If Phase 3 introduces regressions:
1. **Revert commits** (work in feature branches)
2. **Restore baselines** from Phase 2
3. **Re-run CI** to confirm clean state
4. **Post-mortem** analysis of failure patterns

---

## Agent Delegation Strategy

### First Wave (3-5 agents, 2-4 hours)

**Goal**: Establish refactoring patterns, validate approach

**Agents**:
1. **Agent 1** (Python): Alembic migration complexity
2. **Agent 9** (Go): Internal service function length
3. **Agent 17** (Frontend): JSX depth in complex views

**Success Indicators**:
- Patterns proven effective
- No test failures
- CI passes for affected areas

**Decision Point**: If first wave succeeds → launch full swarm. If issues → adjust approach.

---

### Second Wave (8-12 agents, 3-6 hours)

**Goal**: Scale refactoring across all languages

**Agents**:
- **Python**: Agents 2-8 (all Python workstreams)
- **Go**: Agents 10-16 (all Go workstreams)
- **Frontend**: Agents 18-21 (all Frontend workstreams)

**Monitoring**:
- Real-time CI status per agent
- Test coverage deltas
- Violation count trends

**Abort Conditions**:
- Test coverage drops >5%
- >10% test failures
- Agent produces non-compiling code

---

## Timeline & Estimates

**Aggressive (Agent-Led)**:
- Planning: 0.5-1 hour (wall clock)
- First Wave: 2-4 hours (3 parallel agents)
- Second Wave: 3-6 hours (10 parallel agents)
- Verification: 1-2 hours (CI + manual checks)
- **Total**: 8-13 hours (wall clock)

**Conservative (Human-in-Loop)**:
- Planning: 2-4 hours (analysis + design)
- Execution: 12-20 hours (review cycles)
- Verification: 2-4 hours (QA + validation)
- **Total**: 16-28 hours (wall clock with checkpoints)

**Recommended**: Aggressive with checkpoints (first wave validation)

---

## Success Metrics

### Quantitative

- **Python**: 604 violations → ~180 violations (70% reduction) ✅
- **Go**: ~2,800 violations → ~1,100 violations (60% reduction) ✅
- **Frontend**: TBD violations → 50% reduction ✅
- **Test Coverage**: Maintained at ≥85% ✅
- **CI Pass Rate**: 100% (no new failures) ✅

### Qualitative

- **Code Readability**: Improved (subjective, peer review)
- **Maintainability**: Easier to modify (reduced cognitive load)
- **Onboarding**: New developers understand code faster
- **Velocity**: Story points per sprint increases (future phases)

---

## Next Steps

1. **Review & Approve** this plan (PM/Architect sign-off)
2. **Create tracking structure** (GitHub project/issues)
3. **Launch First Wave** (Agents 1, 9, 17)
4. **Monitor & Validate** (CI status, test results)
5. **Launch Second Wave** (Full swarm)
6. **Verify & Close** (Baseline updates, reports)

---

## References

- **Phase 1 Completion Report**: `docs/reports/PHASE_1_COMPLETION_REPORT.md` (expected)
- **Phase 2 Implementation Guide**: `docs/guides/PHASE_2_IMPLEMENTATION_GUIDE.md` (expected)
- **Baseline Files**:
  - Python: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/ruff-complexity-baseline.txt`
  - Frontend: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/linting-baseline.txt`
- **CI Configuration**:
  - `.github/workflows/ci.yml`
  - `.github/workflows/quality.yml`
- **Linting Configuration**:
  - Python: `pyproject.toml` (ruff, mypy)
  - Go: `backend/.golangci.yml`
  - Frontend: `frontend/apps/web/.oxlintrc.json`

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Owner**: BMAD Master / Tech Lead
**Status**: Ready for Execution
