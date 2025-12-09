# Code Coverage Work Packages - Agent Execution Guide
**Project:** TraceRTM Enhancement to 85%+ Code Coverage
**Status:** ✅ READY FOR EXECUTION
**Created:** December 8, 2025

---

## 🚀 Quick Start

**Are you an Agent?** Start here:
1. Read this file (5 min)
2. Read `AGENT_QUICK_START.md` (1 hour)
3. Find your assignment in `WORK_PACKAGE_INDEX.md` (5 min)
4. Start your first work package!

**Are you a Project Lead?** Start here:
1. Read this file (5 min)
2. Read `AGENT_WORK_PACKAGE_SUMMARY.md` (30 min)
3. Use `PRE_FLIGHT_CHECKLIST.md` before Day 1 (1 hour)
4. Launch agents on Day 1!

---

## What's This Project?

### The Challenge
- **Current State:** 12.10% code coverage (2,092 lines covered)
- **Current Tests:** 8,244 tests exist BUT are heavily mocked
- **Problem:** Tests don't exercise real code - coverage is artificially low
- **Target:** 85-100% real coverage in 8 weeks
- **Solution:** 1,500+ new integration tests using real database

### The Scope
- **Timeline:** 8 weeks core + 2 week buffer = 10 weeks total
- **Team:** 4 agents working in parallel
- **Effort:** 618 hours development (with 182 hours infrastructure/overhead = 800 total)
- **Work Packages:** 25 organized in 4 phases
- **Tests to Add:** 1,500+ integration tests
- **Coverage Gain:** 12% → 85%+

---

## 📚 Document Guide

### Core Documents (Start Here)

| Document | For | Purpose | Time |
|----------|-----|---------|------|
| **AGENT_QUICK_START.md** | Agents | Get productive in 1 hour | 1h |
| **WORK_PACKAGE_INDEX.md** | Agents | Find your assignment | 5m |
| **AGENT_WORK_PACKAGE_SUMMARY.md** | Leads | Understand full scope | 30m |
| **PRE_FLIGHT_CHECKLIST.md** | Leads | Verify readiness | 1h |

### Execution Documents

| Document | For | Purpose | When |
|----------|-----|---------|------|
| **WORK_PACKAGES_AGENTS.md** | Agents | Detailed WP specs | Reference |
| **WORK_TICKET_TEMPLATE.md** | Agents | Ticket format & examples | Reference |
| **COVERAGE_PROGRESS_DASHBOARD.md** | Leads | Track metrics | Daily |
| **DAILY_STANDUP_LOG.md** | Team | Progress log | Daily |

### Context Documents

| Document | For | Purpose |
|----------|-----|---------|
| **CODE_COVERAGE_EVALUATION_85-100.md** | Everyone | Why 12% is low |
| **TEST_COVERAGE_AUDIT_2025.md** | Everyone | Test infrastructure |
| **WORK_PACKAGE_DELIVERABLES_SUMMARY.md** | Leads | Delivery verification |

---

## 🎯 For Agents

### Pre-Day 1: Run Validation (30 minutes)

**Complete these before Day 1 execution:**
1. `bash PRE_STARTUP_VALIDATION.sh` - Catch setup errors early
2. `pytest HELLO_WORLD_TEST.py -v` - Verify first test passes
3. Complete `ONBOARDING_SUCCESS_CHECKLIST.md` - 14-point verification

**Reference:** `HELLO_WORLD_TEST.py` - 10-line starter test you can run immediately

### Your Day 1 (4 hours)

1. **Setup Environment** (30 min)
   ```bash
   cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   python3 -m pip install -e ".[dev,test]"
   pytest --version  # Verify: 9.0.0+
   coverage --version  # Verify: 7.11.3+
   bash PRE_STARTUP_VALIDATION.sh  # All checks must PASS
   ```

2. **Read AGENT_QUICK_START.md** (60 min)
   - PRE-STARTUP VALIDATION section (run validation script first!)
   - TL;DR section
   - Environment setup + IDE guides (VS Code, PyCharm)
   - Test patterns (6 patterns including async Pattern 6)
   - Import error troubleshooting (covers 80% of issues)
   - Git configuration validation

3. **Run Hello World Test** (10 min)
   ```bash
   pytest HELLO_WORLD_TEST.py -v
   # Expected: test_database_exists_and_works PASSED ✅
   ```

4. **Find Your Assignment** (5 min)
   ```bash
   # Open WORK_PACKAGE_INDEX.md
   # Find your agent name (Agent 1/2/3/4)
   # Write down your Week 1 work packages
   ```

5. **Create First Branch** (30 min)
   ```bash
   git checkout -b coverage/WP-X-Y-description
   # Follow AGENT_QUICK_START.md test patterns
   # Write 1 simple test
   # Run: pytest tests/integration/test_sample.py -v
   ```

6. **Daily Standup** (15 min)
   - Report: "Setup complete, validation passed, ready to start"
   - Questions?
   - Confirm standup time for tomorrow

### Your Workflow (Weekly)

**Monday Morning:**
- Pull latest main
- Check progress dashboard
- Review this week's WPs

**Monday-Friday:**
- Write tests (main work)
- Run tests locally
- Commit progress daily
- Update standup log

**Friday:**
- Fill weekly summary
- Show coverage progress
- Plan next week

### What to Focus On

**DO ✅**
- Write REAL integration tests (no mocks)
- Use real database (SQLite in-memory)
- Test error paths (not just happy path)
- Clean up after tests (teardown)
- Commit progress regularly
- Update standups daily

**DON'T ❌**
- Mock the service layer (defeats purpose)
- Skip error cases
- Leave tests hanging
- Work in isolation
- Push without testing locally

### Success Metrics

You're doing well when:
- ✅ Coverage increases every day
- ✅ Tests pass consistently
- ✅ Standup reports show progress
- ✅ Blockers resolved <24 hours
- ✅ Tests are maintainable

---

## 👔 For Project Leads

### Your Day 1 (2 hours)

1. **Verify Infrastructure** (30 min)
   ```bash
   # Run pre-flight verification from PRE_FLIGHT_CHECKLIST.md
   pytest --version
   coverage --version
   # Verify database works
   # Verify git access for all agents
   ```

2. **Setup Tracking** (45 min)
   - Initialize COVERAGE_PROGRESS_DASHBOARD.md
   - Set coverage baseline: 12.10%
   - Set Week 1 target: 25%
   - Setup DAILY_STANDUP_LOG.md
   - Verify agents can write to dashboard

3. **Brief Agents** (15 min)
   - Send materials
   - Explain timeline
   - Confirm standup schedule
   - Answer setup questions

4. **Day 1 Standup** (15 min)
   - Confirm all agents ready
   - Answer environment questions
   - Set expectations

### Your Weekly Responsibilities

**Daily (15 min):**
- Attend standup
- Note blockers
- Update dashboard with coverage %

**Friday (30 min):**
- Review weekly progress
- Fill weekly summary in DAILY_STANDUP_LOG.md
- Check if on track for phase targets
- Plan any needed adjustments

**Weekly Review (60 min):**
- Run full coverage report
- Analyze progress
- Identify risks
- Report to stakeholders
- Adjust timeline if needed

### What to Track

| Metric | Frequency | Target |
|--------|-----------|--------|
| Line Coverage % | Daily | +15% per week (Phases 1-3), +10% (Phase 4) |
| Tests Added | Daily | See phase targets |
| Work Packages Complete | Weekly | See phase schedule |
| Blockers Active | Daily | <2 at any time |
| Test Pass Rate | Daily | 100% |

### Risk Management

**If Behind:**
- Focus on P0 work packages only
- Skip P2 if needed
- Extend timeline if critical blockers
- Parallelize more aggressively

**If Coverage Plateaus:**
- Run: `pytest --cov=... --cov-report=term-with-missing`
- Find lines marked "0" (not covered)
- Add targeted tests for those lines
- Verify tests don't mock service layer

**If Tests Are Slow:**
- Use SQLite in-memory
- Run in parallel: `pytest -n auto`
- Optimize database queries in tests
- Split into unit/integration runs

---

## 📊 Expected Progress

### Phase 1: Foundation (Weeks 1-2)
```
Start:  12% coverage, 8,244 tests (mocked)
End:    35% coverage, 8,400+ tests (real)
Work:   Enable 10 disabled test files, setup infrastructure
Tests:  190+ new integration tests
WPs:    7 (WP-1.1 through WP-1.7)
```

### Phase 2: Core Services (Weeks 3-4)
```
Start:  35% coverage
End:    60% coverage
Work:   6 major services fully covered (Query, Graph, Conflict, Sync, Export, Search)
Tests:  490+ new tests
WPs:    6 (WP-2.1 through WP-2.6)
```

### Phase 3: CLI & Storage (Weeks 5-6)
```
Start:  60% coverage
End:    80% coverage
Work:   CLI/API error handling, Storage, TUI widgets, Repository queries
Tests:  455+ new tests
WPs:    6 (WP-3.1 through WP-3.6)
```

### Phase 4: Advanced & Polish (Weeks 7-8)
```
Start:  80% coverage
End:    95%+ coverage
Work:   Property-based tests, parametrization, plugins, reporting
Tests:  297+ new tests
WPs:    6 (WP-4.1 through WP-4.6)
```

---

## 🔧 Tools & Resources

### Essential Commands

```bash
# Run tests for your module
pytest tests/integration/test_YOUR_SERVICE.py -v

# Check coverage
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=term-with-missing

# Generate HTML report
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=html
open htmlcov/index.html

# Run with timeout (catch hangs)
pytest tests/integration/test_YOUR_SERVICE.py \
    --timeout=10

# Git workflow
git checkout -b coverage/WP-X-Y-description
git add tests/integration/test_YOUR_SERVICE.py
git commit -m "WP-X.Y: [X tests], coverage [%]"
git push origin coverage/WP-X-Y-description
```

### Key Files

```
src/tracertm/                      # Code to test
├── services/                      # 65+ services (main focus)
├── repositories/                  # Data access layer
├── storage/                       # Storage layer
├── cli/                          # CLI implementation
├── tui/                          # Terminal UI
└── api/                          # REST API

tests/integration/
├── TEMPLATE.py                   # Copy this template
├── conftest.py                   # Fixtures & database setup
└── [Your test files]             # Create these

tests/fixtures.py                 # Shared fixtures
tests/_disabled_tests/            # Disabled tests to enable (Phase 1)
```

---

## ❓ FAQ

### Setup Questions

**Q: I can't import pytest**
```bash
A: Run: python3 -m pip install -e ".[dev,test]"
   Then: pytest --version
```

**Q: Tests are timing out**
```bash
A: Add fixture cleanup:
   @pytest.fixture(autouse=True)
   def setup(self):
       self.db = get_test_db()
       yield
       self.db.close()  # Important!
```

**Q: Coverage isn't increasing**
```bash
A: Run: pytest --cov=... --cov-report=term-with-missing
   Find lines marked "0" (uncovered)
   Add tests that exercise those lines
```

### Execution Questions

**Q: Should I mock services?**
```
A: NO! That's the whole point. Use real database and services.
```

**Q: How many tests per WP?**
```
A: Check your WORK_PACKAGE_INDEX.md or WORK_PACKAGES_AGENTS.md.
   Usually 50-120 tests per WP.
```

**Q: What if I'm blocked?**
```
A: Mention in standup immediately.
   Work on different WP while waiting.
   Lead will help unblock.
```

**Q: When do I push?**
```
A: After tests pass locally and coverage is verified.
   Create PR with description and coverage report.
```

---

## 📋 Execution Checklist

### Before Starting (Lead)
- [ ] Infrastructure verified (database, pytest, coverage)
- [ ] All agents have repo access
- [ ] Daily standup scheduled
- [ ] Dashboard initialized
- [ ] DAILY_STANDUP_LOG.md ready
- [ ] Agents briefed on Day 1

### Before Starting (Agent)
- [ ] Environment setup complete
- [ ] Can run: `pytest --version`
- [ ] Can run: `coverage --version`
- [ ] Read: AGENT_QUICK_START.md
- [ ] Found: Your assignment in WORK_PACKAGE_INDEX.md
- [ ] Understand: Your first work package
- [ ] Ready: First branch created

### Phase Completion (Lead)
- [ ] Coverage baseline recorded
- [ ] Phase 1 target: 35% (Week 2)
- [ ] Phase 2 target: 60% (Week 4)
- [ ] Phase 3 target: 80% (Week 6)
- [ ] Phase 4 target: 95%+ (Week 8)
- [ ] Final: 85%+ achieved ✅

---

## 🎓 Learning Resources

### In These Documents
- **Test Patterns:** AGENT_QUICK_START.md (5 patterns with code)
- **Fixtures & Setup:** WORK_TICKET_TEMPLATE.md
- **Common Issues:** AGENT_QUICK_START.md troubleshooting
- **Architecture:** CODE_COVERAGE_EVALUATION_85-100.md

### In Codebase
- **Example Tests:** `tests/unit/` and `tests/component/`
- **Service APIs:** `src/tracertm/services/`
- **Test Fixtures:** `tests/integration/conftest.py`
- **Data Models:** `src/tracertm/schemas/`

---

## 📞 Support

### For Setup Issues
1. Check: AGENT_QUICK_START.md "Environment Setup" section
2. Review: PRE_FLIGHT_CHECKLIST.md "Dry Run" section
3. Ask: In daily standup

### For Blockers
1. Mention: In daily standup immediately
2. Document: In DAILY_STANDUP_LOG.md under Blockers
3. Escalate: If not resolved in 2 hours
4. Work: On different WP while waiting

### For Questions
1. Check: FAQ section above
2. Search: WORK_TICKET_TEMPLATE.md "Common Issues"
3. Review: AGENT_QUICK_START.md throughout
4. Ask: In daily standup

---

## 🎯 Success Path

```
Week 1:  Setup + Phase 1 Start
         Coverage: 12% → 18%
         Tests: 40+ added
         ✓ Environment ready
         ✓ First WP started

Week 2:  Phase 1 Complete
         Coverage: 18% → 35%
         Tests: 190+ total added
         ✓ Foundation established
         ✓ Infrastructure ready

Week 3:  Phase 2 Start
         Coverage: 35% → 45%
         Tests: Core services started
         ✓ Query, Graph services covered

Week 4:  Phase 2 Complete
         Coverage: 45% → 60%
         Tests: 490+ total added this phase
         ✓ Core services solid

Week 5:  Phase 3 Start
         Coverage: 60% → 70%
         Tests: CLI/Storage started
         ✓ User-facing systems covered

Week 6:  Phase 3 Complete
         Coverage: 70% → 80%
         Tests: 455+ total added this phase
         ✓ Momentum accelerating

Week 7:  Phase 4 Start
         Coverage: 80% → 88%
         Tests: Advanced tests started
         ✓ Edge cases covered

Week 8:  Project Complete
         Coverage: 88% → 95%+
         Tests: 1,500+ total added
         ✅ TARGET: 85%+ ACHIEVED
         ✅ Comprehensive test suite ready
         ✅ System fully tested
```

---

## 🚀 Let's Execute!

**Everything is ready. Here's what happens next:**

1. **Lead:** Run PRE_FLIGHT_CHECKLIST.md verification
2. **Lead:** Brief all agents (30 min meeting)
3. **Agents:** Read AGENT_QUICK_START.md (1 hour)
4. **Agents:** Setup environment (30 min)
5. **Agents:** Create first test branch (30 min)
6. **Team:** Daily standup (15 min)
7. **Agents:** Start Phase 1 work packages

**Target Timeline:**
- Start: [Set by lead]
- Week 2: Phase 1 complete, 35% coverage
- Week 4: Phase 2 complete, 60% coverage
- Week 6: Phase 3 complete, 80% coverage
- Week 8: **Project complete, 85%+ coverage ✅**

---

## 📞 Questions?

**For Agents:**
- First: Check this file and AGENT_QUICK_START.md
- Next: Check WORK_TICKET_TEMPLATE.md
- Then: Ask in daily standup

**For Leads:**
- First: Check AGENT_WORK_PACKAGE_SUMMARY.md
- Next: Check PRE_FLIGHT_CHECKLIST.md
- Then: Check WORK_PACKAGE_DELIVERABLES_SUMMARY.md

---

**Status: READY FOR EXECUTION ✅**

All materials prepared. All agents can start immediately. All leads have tracking tools ready.

**Time to achieve 85%+ code coverage: 8 weeks**

🚀 Let's build this!

---

*Document: README_WORK_PACKAGES.md*
*Entry Point for All Work Package Execution*
*Created: December 8, 2025*
*For: Project Leads and Test Implementation Agents*
