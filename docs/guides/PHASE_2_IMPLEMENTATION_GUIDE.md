# Phase 2 Implementation Guide - Critical Violation Fixes

**Phase**: 2 of 4
**Timeline**: Weeks 2-3 (after Phase 1 completion)
**Effort**: 80-120 agent-hours (parallelizable)
**Prerequisites**: Phase 1 complete (baselines captured, configs active)

---

## Overview

Phase 2 focuses on **fixing critical violations** identified in Phase 1 baselines. This phase prioritizes security, correctness, and type safety issues that could cause runtime errors or security vulnerabilities.

**Key Principle**: Fix violations in **priority order** (security → correctness → complexity → style), with maximum parallelization across independent areas.

---

## Quick Reference

| Priority | Category | Est. Violations | Effort (agent-hours) | Parallelizable? |
|----------|----------|-----------------|----------------------|-----------------|
| **P0** | Security | ~50-100 | 10-20 | Yes (by file) |
| **P1** | Type Safety | ~200-400 | 20-40 | Yes (by module) |
| **P1** | Correctness | ~300-600 | 30-50 | Yes (by language) |
| **P2** | Complexity (critical only) | ~100-200 | 20-30 | Partially |

**Total**: ~650-1,300 violations, 80-140 agent-hours

---

## Top Priority Violations (P0 - Security)

### Python: Bandit Security Issues

**Source**: CI workflow Bandit checks (exact count TBD after baseline run)

**Common Issues**:
1. Hardcoded secrets/passwords
2. SQL injection vulnerabilities
3. Shell injection (e.g., `subprocess` with shell=True)
4. Insecure random number generation
5. Use of `pickle` (arbitrary code execution risk)

**Fix Strategy**:

```python
# ❌ BEFORE (Security violation)
import subprocess
cmd = f"rm -rf {user_input}"
subprocess.run(cmd, shell=True)  # Shell injection risk

# ✅ AFTER (Fixed)
import subprocess
import shlex
subprocess.run(['rm', '-rf', shlex.quote(user_input)])
```

**Effort**: 2-4 agent-hours per security category
**Parallelization**: Split by file (max 5 parallel agents)

---

## High Priority Violations (P1)

### 1. Python: Type Safety Issues

**Rule**: `PLR0913` - Too many arguments (>5)

**Count**: ~800 violations
**Impact**: Reduces testability, increases coupling
**Fix Strategy**: Extract parameter objects or configuration classes

**Example**:

```python
# ❌ BEFORE (8 parameters)
def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str,
    department: str,
    manager_id: int
) -> User:
    pass

# ✅ AFTER (Parameter object pattern)
from dataclasses import dataclass

@dataclass
class UserCreateParams:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    role: str
    department: str
    manager_id: int

def create_user(params: UserCreateParams) -> User:
    pass
```

**Effort**: 30-40 agent-hours
**Parallelization**: Split by module (max 10 parallel agents)

---

### 2. Python: Complexity (Critical Functions Only)

**Rules**:
- `C901` - Too complex (>7 cyclomatic complexity)
- `PLR0915` - Too many statements (>50)
- `PLR0912` - Too many branches (>12)

**Count**:
- C901: ~200 violations
- PLR0915: ~400 violations
- PLR0912: ~150 violations

**Focus**: Fix **critical path** functions only (auth, payment, data mutation)

**Example** (Extract Method Refactoring):

```python
# ❌ BEFORE (Complexity 12, 80 statements)
def process_order(order: Order) -> ProcessResult:
    # Validate order
    if not order.items:
        return ProcessResult(success=False, error="No items")
    if order.total < 0:
        return ProcessResult(success=False, error="Invalid total")
    # ... 10 more validation checks ...

    # Process payment
    if order.payment_method == "credit_card":
        # ... 20 lines of credit card logic ...
    elif order.payment_method == "paypal":
        # ... 20 lines of PayPal logic ...
    # ... etc ...

    # Update inventory
    # ... 30 lines of inventory logic ...

    return ProcessResult(success=True)

# ✅ AFTER (Complexity 4, 15 statements)
def process_order(order: Order) -> ProcessResult:
    validation_result = validate_order(order)
    if not validation_result.is_valid:
        return ProcessResult(success=False, error=validation_result.error)

    payment_result = process_payment(order)
    if not payment_result.success:
        return ProcessResult(success=False, error=payment_result.error)

    inventory_result = update_inventory(order)
    if not inventory_result.success:
        return ProcessResult(success=False, error=inventory_result.error)

    return ProcessResult(success=True)

def validate_order(order: Order) -> ValidationResult:
    # ... extracted validation logic ...
    pass

def process_payment(order: Order) -> PaymentResult:
    # ... extracted payment logic ...
    pass

def update_inventory(order: Order) -> InventoryResult:
    # ... extracted inventory logic ...
    pass
```

**Effort**: 30-50 agent-hours (critical path only, defer non-critical to Phase 3)
**Parallelization**: Split by domain (auth, payments, inventory, etc.)

---

### 3. Go: Missing Error Checks

**Linters**: `errcheck`, `gosec`

**Common Issues**:
1. Ignored error returns (`_, err := ...` without checking `err`)
2. Deferred `Close()` without error check
3. Unchecked type assertions

**Example**:

```go
// ❌ BEFORE (Ignored error)
func SaveUser(user User) {
    data, _ := json.Marshal(user)  // Error ignored
    db.Save(data)
}

// ✅ AFTER (Error handled)
func SaveUser(user User) error {
    data, err := json.Marshal(user)
    if err != nil {
        return fmt.Errorf("marshal user: %w", err)
    }
    if err := db.Save(data); err != nil {
        return fmt.Errorf("save user: %w", err)
    }
    return nil
}
```

**Effort**: 20-30 agent-hours
**Parallelization**: Split by package (max 8 parallel agents)

---

### 4. TypeScript: Floating Promises

**Rule**: `typescript/no-floating-promises`

**Impact**: Unhandled promise rejections can crash Node.js process
**Fix Strategy**: Add `await` or `.catch()` to all promises

**Example**:

```typescript
// ❌ BEFORE (Floating promise)
async function saveUser(user: User) {
    updateCache(user);  // Floating promise (updateCache is async)
    return db.save(user);
}

// ✅ AFTER (Awaited)
async function saveUser(user: User) {
    await updateCache(user);  // Now awaited
    return db.save(user);
}

// OR (Fire-and-forget with error handling)
async function saveUser(user: User) {
    void updateCache(user).catch(err =>
        logger.error('Cache update failed', err)
    );
    return db.save(user);
}
```

**Effort**: 15-25 agent-hours
**Parallelization**: Split by app/package (web, mobile, shared)

---

## Recommended Fix Order

### Week 1: Security & Type Safety

**Days 1-2**: Security Violations (P0)
- Python: Bandit security issues
- Go: `gosec` security issues
- TypeScript: Security-related rules

**Days 3-5**: Type Safety (P1)
- Python: Fix `PLR0913` (too many args) in API routes and services
- TypeScript: Fix floating promises in critical paths
- Go: Add missing error checks in API handlers

**Estimated Agent Effort**: 40-60 agent-hours

---

### Week 2: Correctness & Critical Complexity

**Days 1-3**: Correctness Issues
- Python: Fix incorrect comparison operators
- Go: Fix `dupl` violations in shared utilities
- TypeScript: Fix `import/no-cycle` in core modules

**Days 4-5**: Critical Complexity
- Python: Refactor top 20 most complex functions (C901 >10)
- Go: Refactor functions exceeding `funlen` limits in services
- TypeScript: Split large components (>300 lines)

**Estimated Agent Effort**: 40-60 agent-hours

---

## Parallelization Strategy

### Language-Based Parallelization (Week 1)

**Agent Team A** (Python):
1. Agent A1: Security fixes (Bandit violations)
2. Agent A2: `PLR0913` fixes (API routes)
3. Agent A3: `PLR0913` fixes (services layer)
4. Agent A4: Type safety (mypy errors)

**Agent Team B** (Go):
1. Agent B1: Security fixes (`gosec`)
2. Agent B2: Error check additions (API handlers)
3. Agent B3: Error check additions (database layer)
4. Agent B4: `dupl` violations (shared code)

**Agent Team C** (TypeScript):
1. Agent C1: Security fixes
2. Agent C2: Floating promises (web app)
3. Agent C3: Floating promises (API client)
4. Agent C4: Import cycles (core modules)

**Total Parallel Agents**: 12 (3 teams × 4 agents)
**Coordination**: Language leads review cross-agent changes

---

### Domain-Based Parallelization (Week 2)

**Agent Team D** (Auth Domain):
- D1: Python auth complexity
- D2: Go auth error handling
- D3: TypeScript auth type safety

**Agent Team E** (API Domain):
- E1: Python API complexity
- E2: Go API error handling
- E3: TypeScript API type safety

**Agent Team F** (Data Domain):
- F1: Python data layer complexity
- F2: Go data layer error handling
- F3: TypeScript data models

**Total Parallel Agents**: 9 (3 teams × 3 agents)
**Coordination**: Domain owners review cross-language consistency

---

## Detailed Violation Categories

### Python Baseline Analysis (15,952 violations)

#### By Severity (Estimated Distribution)

| Priority | Category | Est. Count | % of Total | Phase |
|----------|----------|------------|------------|-------|
| **P0** | Security (Bandit) | 50-100 | 0.5-1% | Phase 2 Week 1 |
| **P1** | Type Safety (mypy) | 200-400 | 1-3% | Phase 2 Week 1 |
| **P1** | Correctness | 300-600 | 2-4% | Phase 2 Week 2 |
| **P2** | Complexity (critical) | 100-200 | 1-2% | Phase 2 Week 2 |
| **P2** | Complexity (non-critical) | 500-800 | 3-5% | Phase 3 |
| **P3** | Magic Numbers (PLR2004) | ~14,000 | 88% | Phase 4 (auto-fix) |
| **P3** | Style (PLR6201, etc.) | ~500 | 3% | Phase 4 (auto-fix) |

**Phase 2 Scope**: ~650-1,300 violations (P0-P2 critical only)
**Deferred to Phase 3-4**: ~14,500-15,100 violations (88-95%)

#### By File Type

| Type | Est. Violations | Priority | Strategy |
|------|-----------------|----------|----------|
| **Alembic Migrations** | ~2,000 | P3 (Low) | Defer to Phase 3-4 (one-time scripts) |
| **API Routes** | ~1,500 | P1 (High) | Fix in Phase 2 (critical path) |
| **Services Layer** | ~2,000 | P1 (High) | Fix in Phase 2 (business logic) |
| **Database Models** | ~1,000 | P2 (Medium) | Partial Phase 2, rest Phase 3 |
| **Tests** | ~3,000 | P3 (Low) | Defer to Phase 4 (test code flexibility) |
| **Scripts/Utils** | ~6,000 | P3 (Low) | Defer to Phase 4 (non-critical) |

**Phase 2 Focus**: API Routes + Services (~3,500 violations → ~500-700 P0-P2)

---

### Go Baseline Analysis (TBD - pending successful capture)

**Expected Distribution** (450-750 violations):

| Linter | Est. Count | Priority | Effort (hrs) |
|--------|------------|----------|--------------|
| `dupl` | 100-150 | P2 | 10-15 |
| `goconst` | 80-120 | P3 | Defer Phase 4 |
| `funlen` | 60-100 | P2 | 15-20 |
| `mnd` | 150-250 | P3 | Defer Phase 4 |
| `errcheck` | 50-80 | P1 | 20-30 |
| `gosec` | 10-20 | P0 | 5-10 |
| `gochecknoglobals` | 5-15 | P2 | 5-10 |

**Phase 2 Scope**: ~125-250 violations (P0-P2)
**Deferred**: ~325-500 violations (P3)

---

### TypeScript Baseline Analysis (TBD - pending capture)

**Expected Distribution** (500-2,000 violations):

| Rule | Est. Count | Priority | Effort (hrs) |
|------|------------|----------|--------------|
| `no-floating-promises` | 100-200 | P1 | 15-25 |
| `no-misused-promises` | 50-100 | P1 | 10-15 |
| `import/no-cycle` | 20-40 | P1 | 10-20 |
| `no-unsafe-*` (type safety) | 150-300 | P1 | 20-30 |
| Complexity (large files) | 50-100 | P2 | 15-25 |
| Style violations | 130-1,260 | P3 | Defer Phase 4 |

**Phase 2 Scope**: ~370-740 violations (P0-P2)
**Deferred**: ~130-1,260 violations (P3)

---

## Automated Fix Strategies

### Auto-Fixable Violations (Use AI Agents)

#### Python

1. **PLR6201** (use set literal): `in [...]` → `in {...}`
   - Auto-fix: 100% safe
   - Command: `ruff check --select PLR6201 --fix`
   - Effort: 1 agent-hour (batch operation)

2. **Import sorting**: Wrong import order
   - Auto-fix: 100% safe
   - Command: `ruff check --select I --fix`
   - Effort: 1 agent-hour

3. **Format violations**: Inconsistent formatting
   - Auto-fix: 100% safe
   - Command: `ruff format .`
   - Effort: 1 agent-hour

**Total Auto-Fix**: ~500 violations, 3 agent-hours

#### Go

1. **gofmt** violations: Inconsistent formatting
   - Auto-fix: 100% safe
   - Command: `gofmt -w .`
   - Effort: 1 agent-hour

2. **goimports** violations: Missing/wrong imports
   - Auto-fix: 100% safe
   - Command: `goimports -w .`
   - Effort: 1 agent-hour

**Total Auto-Fix**: ~100 violations, 2 agent-hours

#### TypeScript

1. **Formatting**: Inconsistent style
   - Auto-fix: 100% safe (if Prettier configured)
   - Command: `prettier --write .`
   - Effort: 1 agent-hour

2. **Import ordering**: Wrong import order
   - Auto-fix: 90% safe
   - Via oxlint `--fix` flag
   - Effort: 2 agent-hours

**Total Auto-Fix**: ~200 violations, 3 agent-hours

---

## Manual Fix Strategies (AI-Assisted)

### Complex Refactoring Pattern

**Use AI agents for guided refactoring**:

1. **Identify violation** (AI reads baseline report)
2. **Generate fix proposal** (AI suggests refactoring)
3. **Apply fix** (AI edits file)
4. **Run tests** (AI verifies no regressions)
5. **Commit** (AI creates descriptive commit message)

**Example Workflow** (Extract Method):

```bash
# AI Agent Workflow
1. Read: src/services/order_service.py:process_order (C901: complexity 12)
2. Analyze: Function has 3 distinct concerns (validate, payment, inventory)
3. Plan: Extract validate_order, process_payment, update_inventory
4. Execute: Create new functions, update process_order
5. Test: Run pytest tests/services/test_order_service.py
6. Commit: "refactor(services): extract order processing sub-functions (C901)"
```

**Effort per Function**: 15-30 minutes (AI-assisted)
**Parallelization**: 5-10 agents working on different functions simultaneously

---

## Testing Strategy

### Test Coverage Requirements

**Rule**: No reduction in test coverage allowed

**Verification**:
- Run pytest coverage before and after fixes
- Ensure coverage % stays same or increases
- Add tests for new extracted functions

### Regression Prevention

**Per-Language Testing**:

#### Python
```bash
# Before fixes
pytest --cov=src --cov-report=json > coverage-before.json

# After fixes
pytest --cov=src --cov-report=json > coverage-after.json

# Compare
python scripts/compare-coverage.py coverage-before.json coverage-after.json
```

#### Go
```bash
# Before fixes
go test -coverprofile=coverage-before.out ./...

# After fixes
go test -coverprofile=coverage-after.out ./...

# Compare
go tool cover -func=coverage-before.out > cov-before.txt
go tool cover -func=coverage-after.out > cov-after.txt
diff cov-before.txt cov-after.txt
```

#### TypeScript
```bash
# Before fixes
bun test --coverage --coverage-reporter=json > coverage-before.json

# After fixes
bun test --coverage --coverage-reporter=json > coverage-after.json

# Compare (using istanbul or similar)
```

---

## Success Criteria (End of Phase 2)

### Quantitative Metrics

- [ ] **P0 (Security)**: 100% fixed (0 remaining)
- [ ] **P1 (Type Safety)**: ≥90% fixed (≤50 remaining)
- [ ] **P1 (Correctness)**: ≥80% fixed (≤120 remaining)
- [ ] **P2 (Critical Complexity)**: ≥70% fixed (≤60 remaining)
- [ ] **Test Coverage**: No reduction (≥current %)
- [ ] **CI Green**: All PR checks passing with new rules

### Qualitative Metrics

- [ ] No new P0/P1 violations introduced
- [ ] All critical path code (auth, payments, API) compliant
- [ ] Code review feedback: "easier to understand" (vs before)
- [ ] AI code generation respects new limits (no violations in new code)

### Documentation

- [ ] Phase 2 completion report published
- [ ] Refactoring patterns documented (for Phase 3)
- [ ] Violation tracking dashboard updated (if using)
- [ ] Team retrospective completed

---

## Risk Mitigation

### Risk 1: Refactoring Introduces Bugs

**Mitigation**:
1. ✅ AI agents run tests after each fix
2. ✅ Require PR reviews for complexity refactoring
3. ✅ Use feature flags for high-risk changes
4. ✅ Gradual rollout (fix 10-20 violations per day max)

### Risk 2: Scope Creep (Too Many Violations)

**Mitigation**:
1. ✅ Strict P0-P2 priority focus (defer P3 to Phase 4)
2. ✅ Time-box each category (e.g., 20 hrs max for `PLR0913`)
3. ✅ Accept partial fixes (70-80% is acceptable for Phase 2)
4. ✅ Use `# noqa` with issue tracking for deferred fixes

### Risk 3: AI Agent Coordination Failures

**Mitigation**:
1. ✅ Assign non-overlapping file sets to agents
2. ✅ Use git branches per agent (merge sequentially)
3. ✅ Daily standup sync (review conflicts)
4. ✅ Human oversight for cross-cutting changes

### Risk 4: Test Suite Instability

**Mitigation**:
1. ✅ Fix flaky tests before starting Phase 2
2. ✅ Run full test suite before and after each agent batch
3. ✅ Revert batch if any test failures
4. ✅ Use test quarantine for known flaky tests

---

## Phase 2 → Phase 3 Handoff Criteria

**Ready to Start Phase 3 When**:

1. ✅ All P0 violations fixed (security)
2. ✅ ≥90% P1 violations fixed (type safety, correctness)
3. ✅ Critical complexity violations addressed (API routes, services)
4. ✅ Test coverage maintained or improved
5. ✅ CI pipeline stable (no random failures)
6. ✅ Team comfortable with refactoring patterns
7. ✅ Phase 2 completion report approved by tech lead

**Phase 3 Focus**: Remaining complexity violations (non-critical functions)

---

## Tools & Resources

### AI Agent Commands

**Python Violation Fix**:
```bash
# Agent command template
ruff check src/path/to/file.py --select <RULE_CODE>
# ... AI analyzes violation ...
# ... AI edits file ...
pytest tests/path/to/test_file.py
git add src/path/to/file.py
git commit -m "fix(<module>): <description> (<RULE_CODE>)"
```

**Go Violation Fix**:
```bash
# Agent command template
golangci-lint run --enable=<LINTER> path/to/package
# ... AI analyzes violation ...
# ... AI edits file ...
go test ./path/to/package/...
git add path/to/package
git commit -m "fix(<package>): <description> (<LINTER>)"
```

**TypeScript Violation Fix**:
```bash
# Agent command template
bunx oxlint --type-aware path/to/file.ts
# ... AI analyzes violation ...
# ... AI edits file ...
bun test path/to/file.test.ts
git add path/to/file.ts
git commit -m "fix(<component>): <description> (oxlint)"
```

### Reference Documents

- **Phase 1 Report**: `docs/reports/PHASE_1_COMPLETION_REPORT.md`
- **Master Audit**: `docs/reports/COMPREHENSIVE_LINTING_AUDIT_MASTER_PLAN.md`
- **Python Audit**: `docs/reports/PYTHON_LINTING_AI_CODING_AUDIT.md`
- **Go Audit**: `docs/reports/GO_LINTING_AUDIT_AI_CODING.md`
- **AI Coding Strategy**: `docs/reports/AI_CODED_LINTING_STRATEGY.md`

### External Resources

- **Ruff Rules**: https://docs.astral.sh/ruff/rules/
- **golangci-lint Linters**: https://golangci-lint.run/usage/linters/
- **Oxlint Rules**: https://oxc-project.github.io/docs/guide/usage/linter.html
- **Refactoring Catalog**: https://refactoring.guru/refactoring/catalog

---

## Appendix: Effort Breakdown by Category

### P0 - Security (10-20 agent-hours)

| Task | Language | Effort (hrs) | Agents |
|------|----------|--------------|--------|
| Bandit violations | Python | 5-10 | 2 |
| gosec violations | Go | 3-6 | 1 |
| Security rules | TypeScript | 2-4 | 1 |

### P1 - Type Safety (50-85 agent-hours)

| Task | Language | Effort (hrs) | Agents |
|------|----------|--------------|--------|
| PLR0913 (too many args) | Python | 30-40 | 3 |
| Floating promises | TypeScript | 15-25 | 2 |
| Error checks | Go | 20-30 | 2 |
| mypy errors | Python | 10-15 | 1 |

### P1 - Correctness (20-35 agent-hours)

| Task | Language | Effort (hrs) | Agents |
|------|----------|--------------|--------|
| Comparison operators | Python | 5-10 | 1 |
| dupl violations | Go | 10-15 | 2 |
| Import cycles | TypeScript | 10-20 | 2 |

### P2 - Critical Complexity (30-50 agent-hours)

| Task | Language | Effort (hrs) | Agents |
|------|----------|--------------|--------|
| Top 20 complex functions | Python | 15-25 | 3 |
| funlen violations (services) | Go | 10-15 | 2 |
| Large components | TypeScript | 10-15 | 2 |

### Auto-Fix (3-8 agent-hours)

| Task | Language | Effort (hrs) | Agents |
|------|----------|--------------|--------|
| PLR6201, imports, format | Python | 2-3 | 1 |
| gofmt, goimports | Go | 1-2 | 1 |
| Prettier, import order | TypeScript | 2-3 | 1 |

---

**Total Estimated Effort**: 113-198 agent-hours
**With Parallelization**: ~2-3 weeks calendar time (12-15 agents working in parallel)

---

**Document Owner**: Platform Engineering Team
**Last Updated**: 2026-02-02
**Next Review**: Phase 2 Kickoff
