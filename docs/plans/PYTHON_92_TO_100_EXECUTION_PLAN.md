# Python Backend: 92/100 → 100/100 Execution Plan

**Current:** 90/100 (A) | **Target:** 100/100 (A+) | **Gap:** 10 points
**Timeline:** 2-3 hours with 3 parallel agents
**Agent Assignment:** Codex (gpt-5.3-codex) for all tracks

---

## PHASED WBS (Work Breakdown Structure)

### Phase 1: Docstring Completion (60 min)
**Goal:** 92% → 100% docstring coverage (+8%)

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| P1-01 | Find remaining functions without docstrings | - | Codex | 10min | List of 180 functions |
| P1-02 | Add docstrings to services/* (60 functions) | P1-01 | Codex | 20min | 100% services coverage |
| P1-03 | Add docstrings to repositories/* (50 functions) | P1-01 | Codex | 15min | 100% repos coverage |
| P1-04 | Add docstrings to remaining modules (70 functions) | P1-01 | Codex | 15min | 100% overall coverage |

**Acceptance:** `interrogate src/tracertm/ --fail-under 100` passes

### Phase 2: Type Hint Completion (30 min)
**Goal:** 99.3% → 100% type hint coverage (+0.7%)

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| P2-01 | Find remaining 15 functions without return types | - | Codex | 5min | List of 15 functions |
| P2-02 | Add return type hints to all 15 functions | P2-01 | Codex | 15min | 100% return type coverage |
| P2-03 | Add parameter type hints (remaining ~200) | P2-01 | Codex | 10min | Full function signatures |

**Acceptance:** Custom script shows 2,230/2,230 functions with return types

### Phase 3: MyPy Error Resolution (60 min)
**Goal:** Reduce mypy errors to 0 (strict mode)

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| P3-01 | Run mypy --strict and categorize errors | P2-02 | Codex | 10min | Error classification report |
| P3-02 | Fix type incompatibilities (est. 50 errors) | P3-01 | Codex | 20min | 50 errors resolved |
| P3-03 | Fix missing imports/undefined names | P3-01 | Codex | 15min | Import errors resolved |
| P3-04 | Add type: ignore where necessary (last resort) | P3-02, P3-03 | Codex | 15min | mypy --strict passes |

**Acceptance:** `mypy src/tracertm/ --strict` returns 0 errors

### Phase 4: Linting Cleanup (30 min)
**Goal:** Reduce ruff errors from 355 to 0

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| P4-01 | Run ruff check --fix (auto-fixable) | - | Codex | 5min | Auto-fixes applied |
| P4-02 | Fix remaining complexity violations | P4-01 | Codex | 10min | McCabe <7, args <5 |
| P4-03 | Fix naming violations | P4-01 | Codex | 10min | PEP 8 compliance |
| P4-04 | Final ruff validation | P4-02, P4-03 | Codex | 5min | 0 errors |

**Acceptance:** `ruff check src/tracertm/` returns 0 errors

---

## DEPENDENCY DAG

```
Phase 1 (Docstrings): P1-01 → [P1-02, P1-03, P1-04] (parallel)
                          ↓
Phase 2 (Type Hints): P2-01 → P2-02 → P2-03
                          ↓
Phase 3 (MyPy): P3-01 → [P3-02, P3-03] (parallel) → P3-04
                          ↓
Phase 4 (Linting): P4-01 → [P4-02, P4-03] (parallel) → P4-04
```

---

## AGENT EXECUTION COMMANDS

### Track 1: Docstrings (Codex - 60 min)
```bash
~/.claude/skills/codex-agent/scripts/run_codex.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Add Google-style docstrings to 180 functions missing them in src/tracertm/. Focus on: services/* (60), repositories/* (50), remaining modules (70). Target: 100% coverage. Verify: interrogate src/tracertm/ --fail-under 100" \
  --mode workspace-write \
  --reasoning high &
```

### Track 2: Type Hints (Codex - 30 min)
```bash
~/.claude/skills/codex-agent/scripts/run_codex.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Add return type hints to remaining 15 functions + parameter types to 200 functions in src/tracertm/. Target: 100% type coverage. Verify with custom AST parser." \
  --mode workspace-write \
  --reasoning medium &
```

### Track 3: MyPy (Codex - 60 min)
```bash
~/.claude/skills/codex-agent/scripts/run_codex.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Fix all mypy --strict errors in src/tracertm/. Categorize, fix type incompatibilities, add imports, use type: ignore sparingly. Target: 0 errors. Verify: mypy src/tracertm/ --strict" \
  --mode workspace-write \
  --reasoning high &
```

---

## SUCCESS CRITERIA

**Phase 1:** ✅ 100% docstrings (interrogate passes)
**Phase 2:** ✅ 100% type hints (all functions annotated)
**Phase 3:** ✅ 0 mypy errors (strict mode)
**Phase 4:** ✅ 0 ruff errors (clean linting)

**Final Score:** **100/100 (A+)**

---

## TIMELINE

**Parallel Execution:**
- Track 1: 60 min
- Track 2: 30 min (starts after Track 1)
- Track 3: 60 min (starts after Track 2)

**Total Wall-Clock:** ~150 min (2.5 hours)

**Ready to launch when approved.**
