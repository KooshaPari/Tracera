# Pre-Flight Checklist - Ready for Agent Execution
**Project:** TraceRTM Code Coverage Enhancement to 85%+
**Execution Start Date:** [Set by team]
**Target Completion:** 8 weeks + 2 week buffer = 10 weeks total

---

## Quick Note for Agents

**New:** See `PRE_STARTUP_VALIDATION.md` for environment validation checklist (required before starting Phase 1). This pre-flight is for leads; agents should use the validation checklist instead.

---

## For Project Lead/Manager

Complete this before agents start work.

### Project Setup
- [ ] Team defined: 4 agents assigned
- [ ] Agent names captured in WORK_PACKAGE_INDEX.md
- [ ] Daily standup scheduled (15 min, same time daily)
- [ ] Weekly review scheduled (1 hour, end of week)
- [ ] Communication channel ready (Slack/Teams)
- [ ] GitHub project created for tracking
- [ ] 8-week calendar with phases marked

### Infrastructure Ready
- [ ] Repository access verified for all agents
- [ ] Test database (SQLite) configured
- [ ] CI/CD pipeline running and passing current tests
- [ ] Coverage reporting tool (coverage.py) installed
- [ ] pytest plugins installed (pytest-cov, pytest-asyncio, pytest-timeout)
- [ ] All dependencies in pyproject.toml verified

### Documentation Prepared
- [ ] WORK_PACKAGES_AGENTS.md distributed to all agents
- [ ] AGENT_QUICK_START.md shared with all agents
- [ ] WORK_TICKET_TEMPLATE.md available as reference
- [ ] WORK_PACKAGE_INDEX.md sent to agents
- [ ] COVERAGE_PROGRESS_DASHBOARD.md accessible to all
- [ ] AGENT_WORK_PACKAGE_SUMMARY.md shared with team

### Tools & Resources Verified
- [ ] `tests/integration-full/TEMPLATE.py` exists and is usable
- [ ] `tests/integration-full/conftest.py` has required fixtures
- [ ] `tests/fixtures.py` available for shared fixtures
- [ ] Git workflow documented (branching strategy)
- [ ] PR review process defined
- [ ] Coverage thresholds documented (80%+ for each WP)

### Initial Training Done
- [ ] All agents read AGENT_QUICK_START.md
- [ ] All agents ran `pytest --version` successfully
- [ ] All agents ran `coverage --version` successfully
- [ ] All agents can checkout a branch
- [ ] All agents understand test patterns (5 patterns from guide)
- [ ] All agents know NOT to mock service layer

### Risk Mitigation
- [ ] Backup plan if agent unavailable identified
- [ ] Escalation path for blockers defined
- [ ] Database recovery process documented
- [ ] Git recovery process known (git reset, revert)
- [ ] Performance monitoring baseline established

### Metrics & Tracking
- [ ] Dashboard initialized with start date
- [ ] Initial coverage baseline: 12.10% recorded
- [ ] Week 1 target: 25% set in dashboard
- [ ] Daily reporting format documented
- [ ] Weekly summary template prepared
- [ ] Status update frequency: Daily standup + weekly review

### Automation Scripts & Infrastructure
- [ ] Read TRACKING_AUTOMATION_SETUP.md (overview of scripts)
- [ ] Read ESCALATION_PROTOCOL.md (blocker tiers and SLAs)
- [ ] `scripts/` directory created
- [ ] 4 automation scripts installed:
  - [ ] `scripts/update_coverage_daily.py`
  - [ ] `scripts/generate_weekly_report.py`
  - [ ] `scripts/check_blockers.sh`
  - [ ] `scripts/dashboard_snapshot.py`
- [ ] All scripts tested locally (see TRACKING_AUTOMATION_SETUP.md)
- [ ] GitHub Actions workflows created:
  - [ ] `.github/workflows/coverage.yml`
  - [ ] `.github/workflows/escalation-monitor.yml`
- [ ] First workflow run successful (check Actions tab)
- [ ] Dashboard updated automatically (verify COVERAGE_PROGRESS_DASHBOARD.md modified)

---

## For Each Agent

Complete this before starting your first work package.

### Environment Setup
- [ ] Python 3.12+ installed: `python3 --version` ✅
- [ ] pip updated: `python3 -m pip --version` ✅
- [ ] Dependencies installed: `python3 -m pip install -e ".[dev,test]"` ✅
- [ ] pytest working: `pytest --version` ✅ (expect 9.0.0+)
- [ ] coverage working: `coverage --version` ✅ (expect 7.11.3+)
- [ ] Git configured: `git config user.name` ✅

### Repository Access
- [ ] Can clone repository ✅
- [ ] Can checkout branches ✅
- [ ] Can push to remote ✅
- [ ] Can pull latest main ✅
- [ ] Understand git workflow (branch per WP) ✅

### Test Infrastructure
- [ ] Can run existing tests: `pytest tests/unit/ -v` ✅
- [ ] Test discovery works: `pytest --collect-only` ✅
- [ ] Database fixtures work ✅
- [ ] Sample test data creation works ✅

### Knowledge Base
- [ ] Read: AGENT_QUICK_START.md (1 hour) ✅
- [ ] Read: WORK_PACKAGE_INDEX.md to find your assignment ✅
- [ ] Reviewed: WORK_TICKET_TEMPLATE.md (reference) ✅
- [ ] Understand: 5 test patterns from quick start ✅
- [ ] Know: Which WP to start with this week ✅

### IDE Setup (Optional but Recommended)
- [ ] IDE configured (VS Code, PyCharm, etc.)
- [ ] pytest integration working in IDE
- [ ] Coverage report preview available
- [ ] Git integration configured
- [ ] Linter configured (if using)

### First Work Package Prep
- [ ] Know your first WP ID (WP-X.Y)
- [ ] Know your WP effort (X hours)
- [ ] Know your WP target (Y+ tests)
- [ ] Know your target coverage (Z%)
- [ ] Know target completion date (end of week)

### Dry Run
- [ ] Can create branch: `git checkout -b coverage/WP-1-1-test` ✅
- [ ] Can commit: `git add . && git commit -m "test"` ✅
- [ ] Can push: `git push origin coverage/WP-1-1-test` ✅
- [ ] Can run single test file: `pytest tests/unit/test_something.py -v` ✅
- [ ] Can generate coverage: `pytest --cov=src/tracertm --cov-report=term-with-missing` ✅

### Questions Answered
- [ ] Understand: Write REAL tests, not mocked
- [ ] Understand: Use real database (SQLite in-memory)
- [ ] Understand: Tests should be independent
- [ ] Understand: Error cases matter
- [ ] Understand: Coverage % is key metric

---

## During Execution: Weekly Checklist

### Start of Week
- [ ] Read team standup notes from last week
- [ ] Check blockers from last week (resolved?)
- [ ] Review coverage dashboard for last week's results
- [ ] Confirm this week's WP assignment
- [ ] Pull latest main branch
- [ ] Verify all tests still passing on main

### During Week (Daily)
- [ ] Complete daily standup (15 min)
  - What you completed
  - What you're working on
  - Any blockers
- [ ] Run tests locally before pushing
- [ ] Commit progress at least daily
- [ ] Update dashboard daily with coverage %
- [ ] Help teammates if they're blocked

### End of Week
- [ ] All tests passing on your branch
- [ ] Coverage report generated and reviewed
- [ ] PR created with detailed description
- [ ] Dashboard updated with final coverage
- [ ] Weekly summary added to dashboard
- [ ] Blockers identified and escalated if needed

---

## Success Criteria Check

### For Phase 1 (Week 2 End)
- [ ] Coverage: 12% → 35% (minimum +15%)
- [ ] Tests: 190+ tests added
- [ ] Work Packages: WP-1.1 through WP-1.7 complete
- [ ] All tests passing
- [ ] No regressions in existing tests
- [ ] Dashboard updated daily
- [ ] No blockers unresolved >24 hours

### For Phase 2 (Week 4 End)
- [ ] Coverage: 35% → 60% (minimum +15%)
- [ ] Tests: 490+ additional tests
- [ ] Work Packages: WP-2.1 through WP-2.6 complete
- [ ] Services layer substantially covered
- [ ] Team working efficiently
- [ ] Dependencies resolved without issues

### For Phase 3 (Week 6 End)
- [ ] Coverage: 60% → 80% (minimum +15%)
- [ ] Tests: 455+ additional tests
- [ ] Work Packages: WP-3.1 through WP-3.6 complete
- [ ] User-facing systems solid coverage
- [ ] Momentum accelerating
- [ ] Pattern adherence strong

### For Phase 4 (Week 8 End)
- [ ] Coverage: 80% → 95%+ (minimum +10%)
- [ ] Tests: 297+ additional tests
- [ ] Work Packages: WP-4.1 through WP-4.6 complete
- [ ] **TARGET ACHIEVED: 85%+ coverage**
- [ ] All 1,500+ new tests passing
- [ ] Comprehensive reporting complete
- [ ] Automation infrastructure in place

---

## Risk Management

### If Behind Schedule (Early Warning Signs)
**Warning Signs:**
- Coverage not increasing >5% per week
- Tests taking >2x expected time
- Agent blocked >24 hours
- More than 1 critical blocker at once

**Response:**
- [ ] Escalate to lead immediately
- [ ] Review what's slowing progress
- [ ] Adjust priorities (focus on P0 only)
- [ ] Offer additional resources
- [ ] Extend timeline if needed

### If Tests Are Slow (<5% of week actual vs expected)
**Warning Signs:**
- Individual tests taking >5 seconds
- Full WP test suite taking >5 minutes
- Parallel execution slowing things down

**Response:**
- [ ] Profile slow tests: `pytest --durations=10`
- [ ] Check database queries: Are they optimized?
- [ ] Use SQLite in-memory (faster)
- [ ] Consider splitting integration tests

### If Coverage Plateaus (No increase 3+ days)
**Warning Signs:**
- Lots of tests added but coverage not changing
- Tests passing but lines still uncovered

**Response:**
- [ ] Run: `pytest --cov=... --cov-report=term-with-missing`
- [ ] Find uncovered lines (marked with "0")
- [ ] Add specific tests for those lines
- [ ] Review if tests actually exercise code (no mocks)
- [ ] Check if code paths unreachable (dead code?)

### If Tests Fail Unexpectedly
**Warning Signs:**
- Tests pass locally but fail in CI
- Tests interfere with each other
- Database state carries between tests

**Response:**
- [ ] Add `@pytest.fixture(autouse=True)` for cleanup
- [ ] Use fresh database per test: `self.db = get_test_db()`
- [ ] Run tests serially to isolate: `pytest -p no:xdist`
- [ ] Check for global state modifications
- [ ] Review test order: `pytest --collect-only`

---

## Day 1 Execution Plan

### For Lead (Before agents arrive)
1. **Set expectations** - Quick 30 min sync call with all agents
2. **Verify infrastructure** - Confirm database, tests, coverage working
3. **Distribute materials** - Send all 6 documents to agents
4. **Set daily standup** - Calendar invite for same time daily
5. **Create GitHub project** - Link to WORK_PACKAGES_AGENTS.md

### For Each Agent (Day 1)
1. **Setup environment** (30 min)
   - Clone repo
   - `python3 -m pip install -e ".[dev,test]"`
   - Run `pytest tests/unit/api/test_advanced_search_endpoint.py -v`

2. **Read materials** (45 min)
   - AGENT_QUICK_START.md (focus on TL;DR and test patterns)
   - WORK_PACKAGE_INDEX.md (find your assignment)
   - Understand your Week 1 work package

3. **Create first branch** (15 min)
   - `git checkout -b coverage/WP-X-Y-description`
   - Create empty test file from TEMPLATE.py

4. **Run first test** (15 min)
   - Follow AGENT_QUICK_START.md pattern
   - Write 1 simple test
   - Run it: `pytest tests/integration-full/test_YOUR_SERVICE.py::TestClass::test_one -v`
   - See it pass

5. **Daily standup** (15 min)
   - Quick sync to confirm everyone ready
   - Report: Setup complete, ready to start

---

## Go-Live Verification

Run this before agents start Phase 1 work:

```bash
# Verify pytest works
pytest --version
# Expected: pytest 9.x.x

# Verify coverage works
coverage --version
# Expected: coverage 7.x.x

# Run existing tests (sanity check)
pytest tests/unit/ -x -v
# Expected: Tests passing

# Verify database
python3 -c "from src.tracertm.core.database import get_db; db = get_db(); print('✅ Database working')"

# Verify imports
python3 -c "from src.tracertm.services.query_service import QueryService; print('✅ Services importable')"

# Verify git
git status
git log --oneline -1
# Expected: On main branch, can see commits

# Verify branch creation
git checkout -b test-branch
git checkout main
git branch -D test-branch
# Expected: All successful
```

---

## Final Checklist Before Starting

**Project Lead Signs Off:**
- [ ] Infrastructure verified and working
- [ ] All 4 agents ready and trained
- [ ] Documentation complete
- [ ] Daily standup scheduled
- [ ] Risk mitigation plan in place
- [ ] Dashboard initialized
- [ ] Go-live verification complete

**Agent Sign-Off:**
- [ ] Environment setup complete
- [ ] Materials read
- [ ] First WP understood
- [ ] Ready to create first branch
- [ ] Knows standup time
- [ ] Knows escalation path

**Team Ready Signal:**
```
All systems GO ✅

Start Phase 1: Foundation Work Packages
Target: Reach 35% coverage by end of Week 2
Target: Add 190+ integration tests
Target: Complete WP-1.1 through WP-1.7

🚀 BEGIN EXECUTION
```

---

## Key Reminders

### Before You Code
- ✅ Pull latest main
- ✅ Create new branch
- ✅ Understand your WP completely
- ✅ Know your target (X tests, Y% coverage)

### While Coding
- ✅ Write real tests (no mocks)
- ✅ Use real database
- ✅ Run tests locally frequently
- ✅ Commit progress daily
- ✅ Update dashboard daily

### Before You Push
- ✅ All tests passing locally
- ✅ Coverage >80% for your module
- ✅ No debug print statements
- ✅ Docstrings complete
- ✅ Coverage report captured

### Before You Submit PR
- ✅ Rebase on latest main
- ✅ Tests still pass after rebase
- ✅ Coverage report in PR description
- ✅ List of test methods added
- ✅ Any issues/learnings noted

---

## Support Resources

**Technical Questions:**
- Check: AGENT_QUICK_START.md troubleshooting section
- Review: WORK_TICKET_TEMPLATE.md common issues
- Ask: In daily standup

**Blockers:**
- Mention immediately in standup
- Don't wait until end of day
- Lead will help unblock

**Coverage Issues:**
- Run: `pytest --cov=... --cov-report=term-with-missing`
- Look at lines marked "0" (uncovered)
- Add tests to cover those lines
- Verify tests actually exercise code (no mocks)

**Git Issues:**
- Ask: Lead for help
- Or: Check git documentation
- Don't force push without asking

---

**Status: READY FOR EXECUTION**

**When to Start:** [Team decision]
**Duration:** 8 weeks
**Success Target:** 85%+ code coverage
**Teams Assigned:** 4 agents
**Work Packages:** 32 total
**Tests to Add:** 1,500+

🚀 Let's build this!

---

*Document: PRE_FLIGHT_CHECKLIST.md*
*Created: December 8, 2025*
*For: Project Leads and All Test Agents*
