# Comprehensive Linting/Formatting Audit - Master Plan

**Project**: TraceRTM (AI-Coded, Multi-Language)
**Date**: 2026-02-02
**Audit Scope**: All code quality tools across Python, Go, TypeScript/JavaScript

---

## Executive Summary

### Audit Completion Status

✅ **Python Audit**: Complete (docs/reports/PYTHON_LINTING_AI_CODING_AUDIT.md)
✅ **Go Audit**: Complete (docs/reports/GO_LINTING_AUDIT_AI_CODING.md)
✅ **Frontend Audit**: Complete (docs/reports/FRONTEND_TOOLS_AUDIT.md)
✅ **Tool Inventory**: Complete (20 tools catalogued)

### Overall Project Grade: C+ (Needs Urgent Hardening)

| Language | Grade | Status | Critical Issues |
|----------|-------|--------|-----------------|
| **Python** | B+ | ⚠️ Missing complexity | Zero complexity limits |
| **Go** | C+ | ⚠️ Too permissive | Missing 7 critical linters |
| **Frontend** | D | 🔴 Gutted config | AI-strict not active, Biome disabled |

---

## Critical Findings Across All Languages

### 🚨 Universal Issues (Affect ALL Languages)

#### 1. **NO NAMING EXPLOSION PREVENTION** ❌

**Impact**: AI agents creating `Dashboard.py`, `Dashboard_v2.py`, `NewDashboard.py` across Python, Go, and TypeScript.

**Current State**:
- Python: No ruff rules, no semgrep checks
- Go: No golangci-lint detection
- Frontend: AI-strict config exists but NOT ACTIVE

**Solution**: Implemented detection script (`scripts/check-naming-explosion.sh`) but needs language-specific integration.

#### 2. **INCONSISTENT COMPLEXITY ENFORCEMENT** ❌

**Current State**:
- Python: **Zero** complexity limits (AI can generate 1000-line functions)
- Go: Limits exist (15/20) but TOO LENIENT
- Frontend: AI-strict has limits (50 lines) but NOT ACTIVE

**Target State** (AI-Coding Standards):
- Max function length: 50 lines (Python/TS), 80 lines (Go)
- Max cyclomatic complexity: 7-10
- Max parameters: 3-5
- Max nesting depth: 3-4

#### 3. **MAGIC NUMBER DETECTION MISSING** ⚠️

**Current State**:
- Python: PLR2004 disabled
- Go: `mnd` linter disabled
- Frontend: `no-magic-numbers` in AI-strict but NOT ACTIVE

**Impact**: Literal numbers everywhere (`if retries > 3`, `setTimeout(5000)`) without named constants.

---

## Tool Inventory & Status

### Python Tools (8 tools)

| Tool | Type | Version | Status | Grade |
|------|------|---------|--------|-------|
| **ruff** | Linter | >=0.14.14 | ✅ Active | B (needs complexity) |
| **mypy** | Type Checker | >=1.19.1 | ✅ Strict | A+ |
| **basedpyright** | Type Checker | >=1.37.2 | ✅ Ultra-strict | A+ |
| **bandit** | Security | >=1.7.10 | ✅ Active | A |
| **interrogate** | Docstrings | pyproject.toml | ✅ 85% threshold | A |
| **tach** | Architecture | >=0.33.2 | ✅ Active | A |
| **pycln** | Cleanup | pre-commit | ✅ Active | B |
| **pip-audit** | Vulnerability | >=2.7.4 | ✅ CI only | A |

**Missing**: Complexity linters (C90, PLR rules)

### Go Tools (5+ tools)

| Tool | Type | Version | Status | Grade |
|------|------|---------|--------|-------|
| **golangci-lint** | Meta-linter | .golangci.yml | ⚠️ Active | C+ |
| **govet** | Correctness | default | ✅ Enabled | B |
| **staticcheck** | Quality | default | ✅ Enabled | B |
| **gosec** | Security | enabled | ✅ Active | B |
| **revive** | Style | enabled | ⚠️ Lenient | C |

**Missing**: dupl, goconst, funlen, mnd, nolintlint, gochecknoglobals

### Frontend Tools (6 tools)

| Tool | Type | Version | Status | Grade |
|------|------|---------|--------|-------|
| **oxlint** | Linter | ^1.42.0 | 🔴 Permissive mode | D |
| **oxlint (ai-strict)** | Linter | config exists | ❌ NOT ACTIVE | N/A |
| **Biome** | Linter/Formatter | ^2.3.13 | 🔴 Linting DISABLED | F (linter), A (formatter) |
| **stylelint** | CSS Linter | ^17.1.0 | ⚠️ Basic | C |
| **TypeScript** | Type Checker | 5.7.2 | ✅ Active | B |
| **oxfmt** | Formatter | ^0.27.0 | ✅ Active | A |

**Critical**: AI-strict config ready but not applied.

---

## Detailed Audit Reports

### Python: Grade B+ (85/100)

**Audit Report**: `docs/reports/PYTHON_LINTING_AI_CODING_AUDIT.md`

**Strengths**:
- ✅ Ultra-strict type checking (mypy + basedpyright)
- ✅ 85% docstring coverage required
- ✅ Comprehensive security (bandit + ruff S rules)
- ✅ Architecture boundaries (tach)

**Critical Gaps**:
- ❌ **Zero complexity enforcement** (Most Critical)
  - No McCabe complexity limit (C901 disabled)
  - No function length limits
  - No parameter count limits
  - No nesting depth limits
- ❌ **No naming explosion detection**
- ❌ **Magic numbers allowed** (PLR2004 disabled)

**Required Changes**:
```toml
[tool.ruff.lint]
select = [
    # ... existing ...
    "C90",      # McCabe complexity
    "PLR0911",  # too-many-return-statements
    "PLR0912",  # too-many-branches
    "PLR0913",  # too-many-arguments (>5)
    "PLR0915",  # too-many-statements
    "PLR1702",  # too-many-nested-blocks
    "PLR2004",  # magic-value-comparison
]

[tool.ruff.lint.mccabe]
max-complexity = 7

[tool.ruff.lint.pylint]
max-args = 5
max-branches = 12
max-returns = 6
max-statements = 50
```

**Effort**: 4 hours configuration + 30-50 hours fixing violations

---

### Go: Grade C+ (70/100)

**Audit Report**: `docs/reports/GO_LINTING_AUDIT_AI_CODING.md`

**Strengths**:
- ✅ Security baseline (gosec)
- ✅ Correctness foundation (govet, staticcheck)
- ✅ Error handling checks

**Critical Gaps**:
- ❌ **Missing 7 critical linters**:
  - `dupl` - Duplicate code detection
  - `goconst` - Repeated strings → constants
  - `funlen` - Function length limits
  - `mnd` - Magic number detection
  - `nolintlint` - Validate //nolint usage
  - `gochecknoglobals` - No global variables
  - `perfsprint` - Performance
- ⚠️ **Too lenient complexity** (15/20 vs Python's 7/10)
- ⚠️ **All warnings** (should be errors in CI)

**Required Changes**:
```yaml
linters:
  enable:
    # Add missing linters
    - dupl
    - goconst
    - funlen
    - mnd
    - nolintlint
    - gochecknoglobals
    - perfsprint

linters-settings:
  gocyclo:
    min-complexity: 10  # Down from 15
  gocognit:
    min-complexity: 12  # Down from 20
  funlen:
    lines: 80
    statements: 50
  mnd:
    checks: argument,case,condition,operation,return,assign
```

**Effort**: 6 hours configuration + 40-80 hours fixing violations

---

### Frontend: Grade D (60/100)

**Audit Report**: `docs/reports/FRONTEND_TOOLS_AUDIT.md`

**Strengths**:
- ✅ AI-strict config exists and is comprehensive
- ✅ oxfmt formatter working well
- ✅ TypeScript type checking active

**Critical Gaps**:
- 🔴 **AI-strict config NOT ACTIVE** (Most Critical)
  - Current `.oxlintrc.json` has massive overrides disabling 60+ rules
  - Rules that should be ERROR are OFF in src files
- 🔴 **Biome linting completely disabled**
  - Was reactively gutted to avoid conflicts
  - Only formatter remains
- ⚠️ **Stylelint underpowered**
  - Basic presets only
  - No complexity limits for CSS

**Required Changes**:
```bash
# 1. Activate AI-strict config
cd frontend
mv .oxlintrc.json .oxlintrc.json.backup
cp .oxlintrc.json.ai-strict .oxlintrc.json

# 2. Disable Biome linting (keep formatter)
# Edit biome.json - remove all lint rules

# 3. Enhance stylelint
# Add complexity rules, naming conventions
```

**Expected Violations**: 500-2000 errors when activated

**Effort**: 2 hours configuration + 30-50 hours fixing violations

---

## Cross-Language Consistency Analysis

### Strictness Comparison

| Aspect | Python | Go | Frontend (AI-strict) |
|--------|--------|-----|----------------------|
| **Complexity Limit** | 0 (MISSING) | 15/20 (Too lenient) | 10 (NOT ACTIVE) |
| **Function Length** | None | None | 50 lines (NOT ACTIVE) |
| **Max Parameters** | None | None | 3 (NOT ACTIVE) |
| **Type Safety** | A+ (mypy+based) | B+ (Go typing) | A+ (TS strict) |
| **Magic Numbers** | Not enforced | Not enforced | ERROR (NOT ACTIVE) |
| **Naming Explosion** | Not detected | Not detected | ERROR (NOT ACTIVE) |

**Target**: All languages should match AI-strict frontend standards (when activated)

---

## Phased Implementation Plan

### Phase 1: Immediate Actions (Week 1)

**Goal**: Activate existing strict configs, establish baselines

#### Frontend (Priority 1 - CRITICAL)
- [ ] Apply `.oxlintrc.json.ai-strict` as active config
- [ ] Run baseline scan: `bunx oxlint --type-aware . > baseline.txt`
- [ ] Auto-fix: `bunx oxlint --type-aware . --fix`
- [ ] Disable Biome linting in `biome.json`
- [ ] Update CI to use new config

**Effort**: 4 hours
**Owner**: Frontend team / AI agent

#### Python (Priority 2)
- [ ] Add complexity rules to `pyproject.toml` (C90, PLR*)
- [ ] Add magic number detection (PLR2004)
- [ ] Run baseline: `ruff check . --select C90,PLR > baseline.txt`
- [ ] Create `.semgrep/naming-explosion.yml`

**Effort**: 4 hours
**Owner**: Python team / AI agent

#### Go (Priority 3)
- [ ] Add 7 missing linters to `.golangci.yml`
- [ ] Set severity to error (not warning)
- [ ] Run baseline: `golangci-lint run --out-format=json > baseline.json`

**Effort**: 6 hours
**Owner**: Go team / AI agent

### Phase 2: Fix Critical Violations (Weeks 2-3)

**Goal**: Fix Tier 1 violations (correctness, security, type safety)

#### All Languages
- [ ] Fix type safety violations
- [ ] Fix security issues
- [ ] Fix correctness bugs
- [ ] Fix circular dependencies

**Effort**: 40-60 hours across all languages (parallelizable)
**Strategy**: Can be distributed across multiple AI agents

### Phase 3: Complexity Refactoring (Weeks 4-5)

**Goal**: Decompose monolithic functions

#### All Languages
- [ ] Split functions > 50 lines (TS/Python) or > 80 lines (Go)
- [ ] Reduce parameter counts to ≤5
- [ ] Extract nested logic
- [ ] Simplify complex conditionals

**Effort**: 60-80 hours (requires careful refactoring)
**Strategy**: AI agents with code review checkpoints

### Phase 4: Style & Consistency (Week 6)

**Goal**: Achieve consistency across codebase

#### All Languages
- [ ] Fix import ordering
- [ ] Extract magic numbers to constants
- [ ] Standardize naming conventions
- [ ] Remove code duplication

**Effort**: 20-30 hours
**Strategy**: Mostly auto-fixable

---

## Resource Requirements

### Total Effort Estimate

| Phase | Frontend | Python | Go | Total |
|-------|----------|--------|----|-------|
| Phase 1 (Config) | 4h | 4h | 6h | 14h |
| Phase 2 (Critical) | 30-50h | 20-30h | 30-40h | 80-120h |
| Phase 3 (Complexity) | 30-40h | 20-30h | 30-40h | 80-110h |
| Phase 4 (Style) | 10-15h | 5-10h | 10-15h | 25-40h |
| **Total** | **74-109h** | **49-74h** | **76-101h** | **199-284h** |

### Parallelization Strategy

**Can parallelize**:
- Language-specific fixes (Python, Go, Frontend teams work in parallel)
- Auto-fix operations (run simultaneously)
- File-level refactoring (multiple AI agents)

**Must sequence**:
- Phase 1 before Phase 2 (need baselines)
- Critical fixes before complexity refactoring
- Configuration updates before enforcement

**Optimal Timeline**: 6 weeks with 3 parallel workstreams

---

## Risk Assessment

### High Risk

1. **Frontend Activation** (HIGH IMPACT)
   - Risk: 500-2000 new errors when AI-strict activated
   - Mitigation: Phased rollout, auto-fix first, team review
   - Rollback: Keep `.oxlintrc.json.backup`

2. **Python Complexity** (MODERATE IMPACT)
   - Risk: 200-400 functions need refactoring
   - Mitigation: Gradual limits (start at 15, tighten to 7)
   - Rollback: Adjust max-complexity in pyproject.toml

3. **Go Linter Additions** (MODERATE IMPACT)
   - Risk: 300-600 new violations from 7 linters
   - Mitigation: Enable as warnings first, then errors
   - Rollback: Disable specific linters in .golangci.yml

### Medium Risk

4. **Biome Linting Removal**
   - Risk: Lose some checks Biome was catching
   - Mitigation: Oxlint AI-strict covers same ground
   - Rollback: Re-enable Biome linting

5. **Breaking Changes**
   - Risk: Some violations may require API changes
   - Mitigation: Mark as tech debt, fix incrementally
   - Rollback: Case-by-case eslint-disable with tickets

### Low Risk

6. **Auto-fix Safety**
   - Risk: Auto-fixes could introduce bugs
   - Mitigation: Run tests after auto-fix, review diffs
   - Rollback: Git revert

---

## Success Metrics

### Phase 1 Success (Week 1)

- [ ] All 3 languages have strict configs active
- [ ] Baselines captured for all languages
- [ ] CI updated to enforce new rules
- [ ] Auto-fixable violations resolved

### Phase 2 Success (Week 3)

- [ ] Zero type safety violations
- [ ] Zero security violations
- [ ] Zero correctness violations
- [ ] Tests passing

### Phase 3 Success (Week 5)

- [ ] Zero functions > max length
- [ ] Zero functions > max complexity
- [ ] Zero functions > max parameters
- [ ] Code coverage maintained/improved

### Phase 4 Success (Week 6)

- [ ] <1000 total violations across all languages
- [ ] Consistent style enforced
- [ ] Zero magic numbers
- [ ] Zero naming explosions
- [ ] Documentation complete

### Overall Success

**Quantitative**:
- Python: <500 total violations (from current unknown baseline)
- Go: <300 total violations (from current ~150)
- Frontend: <5000 total violations (from current 53,469)

**Qualitative**:
- AI agents constrained from generating poor code
- Consistent patterns across all languages
- Technical debt accumulation prevented
- Code review burden reduced

---

## Governance & Approval

### Approval Required From

- [ ] Tech Lead - Overall strategy
- [ ] Frontend Lead - Frontend changes
- [ ] Backend Lead - Python/Go changes
- [ ] DevOps - CI/CD updates

### Review Checkpoints

1. **Week 1**: Config changes review
2. **Week 3**: Critical fixes review
3. **Week 5**: Complexity refactoring review
4. **Week 6**: Final acceptance

---

## Implementation Delegation

### Subagent Assignments (Following CLAUDE.md)

**Task #13** (Research):
- **Agent**: research-scout
- **Deliverable**: Best practices research for each tool
- **Duration**: 8 hours
- **Status**: Pending

**Task #14** (Python Implementation):
- **Agent**: general-purpose (Python specialist)
- **Deliverable**: Updated pyproject.toml + fixes
- **Duration**: 49-74 hours
- **Status**: Ready to start

**Task #15** (Go Implementation):
- **Agent**: general-purpose (Go specialist)
- **Deliverable**: Updated .golangci.yml + fixes
- **Duration**: 76-101 hours
- **Status**: Ready to start

**Task #16** (Frontend Implementation):
- **Agent**: general-purpose (Frontend specialist)
- **Deliverable**: Activated AI-strict + fixes
- **Duration**: 74-109 hours
- **Status**: Ready to start

**Task #17** (Documentation):
- **Agent**: tech-writer
- **Deliverable**: Unified quality enforcement docs
- **Duration**: 8 hours
- **Status**: Ready to start

---

## Next Steps

### Immediate (Next 24 Hours)

1. **Review this master plan** with tech leads
2. **Get approval** for Phase 1 changes
3. **Assign tasks** to subagents
4. **Start Phase 1** frontend activation (highest priority)

### This Week

1. Complete Phase 1 for all languages
2. Capture baselines
3. Begin Phase 2 critical fixes

### This Month

1. Complete Phases 1-4
2. Achieve success metrics
3. Document learnings
4. Establish ongoing maintenance

---

## Related Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| Python Audit | Detailed Python findings | docs/reports/PYTHON_LINTING_AI_CODING_AUDIT.md |
| Go Audit | Detailed Go findings | docs/reports/GO_LINTING_AUDIT_AI_CODING.md |
| Frontend Audit | Detailed Frontend findings | docs/reports/FRONTEND_TOOLS_AUDIT.md |
| Tool Decision Matrix | When to use what tool | docs/reference/FRONTEND_TOOL_DECISION_MATRIX.md |
| AI Coding Strategy | AI-specific linting philosophy | docs/reports/AI_CODED_LINTING_STRATEGY.md |
| Naming Explosion | Versioned naming prevention | docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md |
| Quick Reference | AI agent quick guide | AI_AGENT_QUICK_REFERENCE.md |

---

## Conclusion

This comprehensive audit reveals **critical gaps** in linting enforcement across all three languages, with **frontend being most urgent** (AI-strict config ready but not applied) and **Python missing all complexity limits**.

**The good news**: Configurations exist or are easy to create. Most issues are fixable through configuration changes and auto-fixing.

**The challenge**: 200-280 hours of work to fully implement, requiring coordination across multiple languages and teams.

**The path forward**: Phased approach starting with frontend activation (Week 1), followed by critical fixes (Weeks 2-3), complexity refactoring (Weeks 4-5), and style consistency (Week 6).

**Status**: Ready for approval and delegation to subagents.
