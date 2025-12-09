# Work Package Index & Quick Reference
**Project:** TraceRTM Code Coverage Enhancement to 85%+
**Status:** Ready for Agent Execution
**Last Updated:** December 8, 2025

---

## What This Document Does

This is a **quick lookup** for agents to find their assigned work packages. For detailed execution instructions, see:
- **Getting Started:** Read `AGENT_QUICK_START.md` (1 hour)
- **Your Assignments:** Find your agent name below
- **Detailed Tickets:** Check `WORK_TICKET_TEMPLATE.md`
- **Track Progress:** Update `COVERAGE_PROGRESS_DASHBOARD.md` daily

---

## Quick Reference: Which WP Should I Start With?

### If You're Agent 1 (Foundation & CLI Lead)
**This Week (Week 1):**
- [ ] Start **WP-1.1**: CLI Hooks (16h) → `tests/_disabled_tests/disabled_cli_hooks.py`
- [ ] Continue **WP-1.3**: Event Replay (20h)

**Next Week (Week 2):**
- [ ] Continue **WP-1.4**: Command Aliases (16h)

**Your Direct Path:** WP-1.1 → WP-1.3 → WP-1.4 → WP-2.1 → WP-3.1 → WP-4.2

**Rebalanced Assignment (137h, 22%):** Reduced from 25% for workload equity. WP-1.2 moved to Agent 4.

---

### If You're Agent 2 (Services Specialist)
**This Week (Week 1):**
- [ ] Start **WP-1.6**: Service Integration Setup (24h) → Infrastructure
- [ ] Help with **WP-1.7**: Integration Test Template (8h)

**Your Direct Path:** WP-1.6 → WP-1.7 → WP-2.2 → WP-2.3 → WP-3.3 → WP-4.1

**Rebalanced Assignment (162h, 26%):** Reduced from 33% to prevent concentration. WP-3.4 moved to Agent 3 for better role alignment.

---

### If You're Agent 3 (Integration Lead)
**This Week (Week 1):**
- [ ] Start **WP-1.5**: Remaining Disabled Tests (24h) → `tests/_disabled_tests/`
- [ ] Parallel: Help infrastructure setup

**Your Direct Path:** WP-1.5 → WP-2.4 → WP-2.5 → WP-2.6 → WP-3.4 → WP-3.5 → WP-4.3 → WP-4.5

**Rebalanced Assignment (219h, 35%):** Expanded from 32% to add strategic coverage. WP-3.4 moved from Agent 2 for better integration role alignment.

---

### If You're Agent 4 (Coverage Specialist)
**This Week (Week 1):**
- [ ] Start **WP-1.2**: Database Features (20h) → `tests/_disabled_tests/disabled_database.py`

**Phase 2 (Weeks 3-4):**
- [ ] Coverage Gap Analysis (35h) - Strategic role analyzing test coverage of other agents' work

**Your Direct Path:** WP-1.2 → Coverage Analysis → WP-3.2 → WP-3.6 → WP-4.4 → WP-4.6

**Rebalanced Assignment (135h, 21%):** Clarified from vague Phase 1 role. Now owns WP-1.2 explicitly + strategic Phase 2 coverage analysis.

---

## All 32 Work Packages At a Glance

### Phase 1: Foundation (Weeks 1-2) - Target: 35% coverage

| WP ID | Title | Hours | Tests | Priority | Status |
|-------|-------|-------|-------|----------|--------|
| **1.1** | CLI Hooks | 16 | 25+ | P0 | ⏳ |
| **1.2** | Database Features | 20 | 35+ | P0 | ⏳ |
| **1.3** | Event Replay | 20 | 30+ | P0 | ⏳ |
| **1.4** | Command Aliases | 16 | 20+ | P1 | ⏳ |
| **1.5** | Remaining Disabled | 24 | 80+ | P0 | ⏳ |
| **1.6** | Service Integration Setup | 24 | - | P0 | ⏳ |
| **1.7** | Integration Test Template | 8 | - | P1 | ⏳ |

**Phase 1 Total:** 128 hours, 190+ tests, 7 work packages

---

### Phase 2: Core Services (Weeks 3-4) - Target: 60% coverage

| WP ID | Title | Hours | Tests | Priority | Status |
|-------|-------|-------|-------|----------|--------|
| **2.1** | Query Service | 30 | 80+ | P0 | ⏳ |
| **2.2** | Graph Algorithms | 40 | 120+ | P0 | ⏳ |
| **2.3** | Conflict Resolution | 35 | 100+ | P0 | ⏳ |
| **2.4** | Sync Engine | 30 | 80+ | P0 | ⏳ |
| **2.5** | Export/Import | 25 | 60+ | P1 | ⏳ |
| **2.6** | Search/Progress/Item | 20 | 50+ | P1 | ⏳ |

**Phase 2 Total:** 180 hours, 490+ tests, 6 work packages

---

### Phase 3: CLI & Storage (Weeks 5-6) - Target: 80% coverage

| WP ID | Title | Hours | Tests | Priority | Status |
|-------|-------|-------|-------|----------|--------|
| **3.1** | CLI Error Handling | 35 | 80+ | P0 | ⏳ |
| **3.2** | CLI Help System | 20 | 60+ | P1 | ⏳ |
| **3.3** | Storage Edge Cases | 30 | 75+ | P0 | ⏳ |
| **3.4** | TUI Widgets | 40 | 95+ | P0 | ⏳ |
| **3.5** | API Errors | 20 | 65+ | P1 | ⏳ |
| **3.6** | Repository Queries | 25 | 80+ | P1 | ⏳ |

**Phase 3 Total:** 170 hours, 455+ tests, 6 work packages

---

### Phase 4: Advanced & Polish (Weeks 7-8) - Target: 95%+ coverage

| WP ID | Title | Hours | Tests | Priority | Status |
|-------|-------|-------|-------|----------|--------|
| **4.1** | Property-Based Tests | 25 | 30+ | P1 | ⏳ |
| **4.2** | Parametrized Tests | 20 | 75+ | P1 | ⏳ |
| **4.3** | Performance Services | 30 | 55+ | P1 | ⏳ |
| **4.4** | Plugin System | 20 | 45+ | P2 | ⏳ |
| **4.5** | Integration Services | 30 | 92+ | P1 | ⏳ |
| **4.6** | Coverage Reporting | 15 | - | P2 | ⏳ |

**Phase 4 Total:** 140 hours, 297+ tests, 6 work packages

---

## Agent Assignments (Detailed)

### Agent 1: Foundation & CLI Lead
**Total Hours:** 137h (22%)
**Total Tests:** 245+ tests
**Coverage Gain:** 20% contribution to overall target

**Week 1-2 (Phase 1):**
- WP-1.1: Enable CLI Hooks (16h, 25+ tests)
- WP-1.3: Enable Event Replay (20h, 30+ tests)
- WP-1.4: Enable Aliases (16h, 20+ tests)

**Week 3-4 (Phase 2):**
- WP-2.1: Query Service (30h, 80+ tests)

**Week 5-6 (Phase 3):**
- WP-3.1: CLI Error Handling (35h, 80+ tests)

**Week 7-8 (Phase 4):**
- WP-4.2: Parametrized Tests (20h, 75+ tests)

**Status:** Rebalanced for workload equity and risk distribution

---

### Agent 2: Services Specialist
**Total Hours:** 162h (26%)
**Total Tests:** 320+ tests
**Coverage Gain:** 25% contribution to overall target

**Week 1-2 (Phase 1):**
- WP-1.6: Service Integration Setup (24h)
- WP-1.7: Integration Test Template (8h)

**Week 3-4 (Phase 2):**
- WP-2.2: Graph Algorithms (40h, 120+ tests)
- WP-2.3: Conflict Resolution (35h, 100+ tests)

**Week 5-6 (Phase 3):**
- WP-3.3: Storage Edge Cases (30h, 75+ tests)

**Week 7-8 (Phase 4):**
- WP-4.1: Property-Based Tests (25h, 30+ tests)

**Status:** Rebalanced for workload equity and risk distribution. WP-3.4 moved to Agent 3.

---

### Agent 3: Integration Lead
**Total Hours:** 219h (35%)
**Total Tests:** 482+ tests
**Coverage Gain:** 35% contribution to overall target

**Week 1-2 (Phase 1):**
- WP-1.5: Remaining Disabled Tests (24h, 80+ tests)

**Week 3-4 (Phase 2):**
- WP-2.4: Sync Engine (30h, 80+ tests)
- WP-2.5: Export/Import (25h, 60+ tests)
- WP-2.6: Search/Progress/Item (20h, 50+ tests)

**Week 5-6 (Phase 3):**
- WP-3.4: TUI Widgets (40h, 95+ tests) [MOVED from Agent 2]
- WP-3.5: API Errors (20h, 65+ tests)

**Week 7-8 (Phase 4):**
- WP-4.3: Performance Services (30h, 55+ tests)
- WP-4.5: Integration Services (30h, 92+ tests)

**Status:** Rebalanced for workload equity and risk distribution. Expanded coverage with WP-3.4.

---

### Agent 4: Coverage Specialist
**Total Hours:** 135h (21%)
**Total Tests:** 270+ tests
**Coverage Gain:** 20% contribution to overall target

**Week 1-2 (Phase 1):**
- WP-1.2: Database Features (20h, 35+ tests) [MOVED from Agent 1]

**Week 3-4 (Phase 2):**
- Coverage Gap Analysis (35h) [NEW STRATEGIC ROLE] - Analyze and fill coverage gaps identified in Agents 1-3 work

**Week 5-6 (Phase 3):**
- WP-3.2: CLI Help System (20h, 60+ tests)
- WP-3.6: Repository Queries (25h, 80+ tests)

**Week 7-8 (Phase 4):**
- WP-4.4: Plugin System (20h, 45+ tests)
- WP-4.6: Coverage Reporting (15h)

**Status:** Rebalanced for workload equity and risk distribution. Clarified Phase 1 and added Phase 2 strategic coverage analysis role.

---

## Starting This Week: Your First WP

### To Start Your First Work Package:

1. **Read your assignment** above (find your Agent number)
2. **Get the full ticket details:**
   ```bash
   cat WORK_TICKET_TEMPLATE.md  # See complete ticket structure
   ```
3. **Read the quick start guide:**
   ```bash
   cat AGENT_QUICK_START.md  # Get productive in 1 hour
   ```
4. **Pull detailed WP info:**
   ```bash
   cat WORK_PACKAGES_AGENTS.md | grep "WP-X.Y" -A 50  # Replace X.Y with your WP
   ```
5. **Create your branch:**
   ```bash
   git checkout -b coverage/WP-X-Y-description
   ```
6. **Start coding:**
   - Follow AGENT_QUICK_START.md patterns
   - Use WORK_TICKET_TEMPLATE.md structure
   - Track progress in COVERAGE_PROGRESS_DASHBOARD.md

---

## Daily Standup Template

Use this in your daily 15-minute standup:

```
Agent [Name]:
  Yesterday: Completed [X] tests for [WP], coverage now [Y]%
  Today: Working on [WP], target [X] tests
  Blockers: [If any]
  Next: [What's next]
```

Example:
```
Agent 1:
  Yesterday: Completed 20 tests for WP-1.1, coverage now 15%
  Today: Continue WP-1.1, target 5 more tests (25 total)
  Blockers: None
  Next: Start WP-1.2
```

---

## Critical Success Factors

### DO ✅
- ✅ Write real integration tests (use real database)
- ✅ Run tests locally before pushing
- ✅ Update dashboard daily
- ✅ Commit progress regularly
- ✅ Communicate blockers immediately
- ✅ Follow the patterns in AGENT_QUICK_START.md

### DON'T ❌
- ❌ Mock the service layer (defeats purpose)
- ❌ Skip error cases
- ❌ Leave tests hanging (use timeouts)
- ❌ Work in isolation (standups daily)
- ❌ Forget to clean up database (teardown)
- ❌ Push without testing locally first

---

## Key Files Reference

### For Getting Started
- **AGENT_QUICK_START.md** - Read first (1 hour)
- **This file** - Quick lookup of assignments
- **WORK_TICKET_TEMPLATE.md** - Full ticket details

### For Execution
- **WORK_PACKAGES_AGENTS.md** - All 32 WPs with details
- **tests/integration/TEMPLATE.py** - Test template
- **tests/integration/conftest.py** - Test fixtures

### For Tracking
- **COVERAGE_PROGRESS_DASHBOARD.md** - Track daily progress
- **AGENT_WORK_PACKAGE_SUMMARY.md** - Overview & plan

---

## Expected Weekly Progress

| Week | Coverage Target | Tests Added | Phase |
|------|-----------------|-------------|-------|
| 1-2 | 12% → 35% | 190+ | Phase 1 Complete |
| 3-4 | 35% → 60% | 490+ | Phase 2 Complete |
| 5-6 | 60% → 80% | 455+ | Phase 3 Complete |
| 7-8 | 80% → 95%+ | 297+ | Phase 4 Complete |

---

## Questions?

**Setup Issues?**
- Check: Python 3.12+, pytest --version, coverage --version
- Read: AGENT_QUICK_START.md "Environment Setup" section

**Where do I start?**
- Find your agent name above
- Read your "This Week" assignment
- Read AGENT_QUICK_START.md

**How do I know if my tests are good?**
- Run: `pytest tests/integration/test_YOUR_SERVICE.py -v`
- Check: `pytest --cov=src/tracertm/services/YOUR_SERVICE --cov-report=term-with-missing`
- Look for: >80% coverage, all tests passing

**I'm blocked on something?**
- Mention in standup immediately
- Ask the team/lead
- Work on different WP while waiting

---

## Let's Execute! 🚀

**Your task:** Pick your agent number above and start your assigned work package this week.

**Timeline:** 8 weeks to 85%+ coverage

**Target:** 1,500+ new integration tests covering real code

**Success:** From 12.10% to 85-100% code coverage

---

*Document: WORK_PACKAGE_INDEX.md*
*Created: December 8, 2025*
*For: Test Implementation Agents (Immediate Execution)*
