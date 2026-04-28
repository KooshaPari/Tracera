# Phase 4: Integration & Cleanup - Quick Reference

**Created**: 2026-02-02
**Full Plan**: [docs/guides/PHASE_4_INTEGRATION_CLEANUP_PLAN.md](../guides/PHASE_4_INTEGRATION_CLEANUP_PLAN.md)

---

## Quick Stats

### Current Baseline
- **Python C901**: 138 violations (down from 248)
- **main.py**: 10,574 lines, 17 C901 violations
- **PLR0913**: 95 violations (too many arguments)
- **Go Tests**: 250 test files, ~10-15% table-driven

### Phase 4 Targets
- **Python C901**: <70 (50% additional reduction)
- **main.py**: <9,000 lines (15% reduction)
- **main.py C901**: <8 violations (53% reduction)
- **PLR0913**: <50 (47% reduction)
- **Go Table Tests**: ~30% (convert 10-15 files)

---

## Execution Waves

### Wave 1: Module Integration (Sequential, 4-6 min)
1. Backup main.py
2. Integrate startup.py
3. Integrate rate_limiting.py
4. Integrate websocket.py
5. Test & verify

### Wave 2: Parallel Work (Mixed, 10-18 min)
**Critical Path (Sequential)**:
- Extract list_links (C901: 53) → links.py
- Extract _list_items_impl (C901: 27) → items.py
- Extract oauth_callback (C901: 16) → oauth.py
- Extract 3 more functions → github.py, health.py, chat.py

**Parallel Tasks**:
- PLR0913: Refactor 20-25 functions (95 → <50)
- Go Tests: Convert 10-15 tests to table-driven
- Go funlen: Baseline + remediate if >30

### Wave 3: Final Verification (Sequential, 3-5 min)
1. Collect final metrics
2. Run full test suite
3. Update documentation
4. Generate completion report

---

## Critical Path Dependencies

```
4.1.1 (Prep) → 4.1.2 (Startup) → 4.1.3 (Rate Limit) → 4.1.4 (WebSocket) → 4.1.5 (Verify)
    ↓
4.2.1 (links) → 4.2.2 (items) → 4.2.3 (oauth) → 4.2.4 (others) → 4.2.5 (Verify)
    ↓
4.6.1 (Metrics) → 4.6.2 (Tests) → 4.6.3 (Docs) → DONE
```

**Parallel Streams** (can run alongside 4.2):
- 4.3 (PLR0913)
- 4.4 (Go Tests)
- 4.5 (Go funlen)

---

## Key Commands

### Check Current Status
```bash
# Python complexity
ruff check --select C901 --statistics
ruff check --select PLR0913 --statistics

# Main.py line count
wc -l src/tracertm/api/main.py

# Main.py C901 count
ruff check src/tracertm/api/main.py --select C901 | wc -l

# Go funlen (if configured)
golangci-lint run backend/ --enable funlen --max-issues-per-linter=0 | grep -c "funlen:"
```

### Integration Steps
```bash
# Backup
cp src/tracertm/api/main.py src/tracertm/api/main.py.phase3.backup

# Test imports
python -c "from tracertm.api.config.startup import startup_initialization; print('OK')"
python -c "from tracertm.api.config.rate_limiting import enforce_rate_limit; print('OK')"
python -c "from tracertm.api.handlers.websocket import websocket_endpoint; print('OK')"

# Run tests
pytest --cov=src --cov-report=term
make test

# Verify reduction
ruff check src/tracertm/api/main.py --select C901
wc -l src/tracertm/api/main.py
```

---

## Timeline Estimates

### Sequential Execution (1 agent)
- **Best Case**: 31 min
- **Expected**: ~40 min
- **Worst Case**: 50 min

### Parallel Execution (3 agents)
- **Best Case**: 17 min
- **Expected**: ~25 min
- **Worst Case**: 34 min

**Recommended**: Parallel with 3 agents

---

## Risk Mitigation

### High Risks
1. **Integration breaks endpoints** → Backup main.py, smoke test each step
2. **Circular dependencies** → Test imports after each extraction
3. **Test failures** → Run tests after each workstream

### Rollback Strategy
- **Per-phase**: Git revert individual commits
- **Emergency**: Restore from `main.py.phase3.backup`
- **Trigger**: >3 test failures, circular imports, coverage <80%

---

## Success Criteria (DoD)

**Phase 4.1** (Module Integration):
- ✅ 3 modules integrated
- ✅ main.py -350 lines
- ✅ C901 -4 violations
- ✅ All tests pass

**Phase 4.2** (High-Complexity):
- ✅ 6 modules created
- ✅ main.py <9,000 lines
- ✅ main.py C901 <8
- ✅ All endpoints tested

**Phase 4.3** (PLR0913):
- ✅ Violations <50
- ✅ Patterns documented

**Phase 4.4** (Go Tests):
- ✅ 10-15 tests converted
- ✅ Pattern guide created

**Phase 4.6** (Final):
- ✅ Python C901 <70
- ✅ main.py <9,000 lines
- ✅ Test coverage ≥85%
- ✅ CI green
- ✅ Docs updated

---

## Quick Decision Matrix

| Metric | Current | Target | On Track? |
|--------|---------|--------|-----------|
| Python C901 | 138 | <70 | ✅ Achievable |
| main.py Lines | 10,574 | <9,000 | ✅ Achievable |
| main.py C901 | 17 | <8 | ✅ Achievable |
| PLR0913 | 95 | <50 | ✅ Achievable |
| Go Table Tests | ~15% | ~30% | ✅ Achievable |
| Go funlen | Unknown | <30 | ⚠️ TBD |

---

## Agent Assignments

**Agent 1: Integration Lead** (Critical Path)
- Phases: 4.1, 4.2, 4.6
- Estimated: 22-32 tool calls, ~17-26 min

**Agent 2: PLR0913 Specialist** (Parallel)
- Phase: 4.3
- Estimated: 8-12 tool calls, ~6-10 min

**Agent 3: Go Test Engineer** (Parallel)
- Phases: 4.4, 4.5
- Estimated: 10-18 tool calls, ~8-14 min

---

## Next Steps

1. **Review** this plan and full implementation guide
2. **Approve** scope and timeline
3. **Launch** Wave 1 (Phase 4.1) - Module Integration
4. **Monitor** CI and test status
5. **Proceed** to Wave 2 after Wave 1 success
6. **Complete** with Phase 4.6 verification

---

**Full Plan**: [PHASE_4_INTEGRATION_CLEANUP_PLAN.md](../guides/PHASE_4_INTEGRATION_CLEANUP_PLAN.md)
**Owner**: BMAD Master / Tech Lead
**Status**: 🟡 READY FOR EXECUTION
