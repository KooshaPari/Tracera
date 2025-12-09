# Onboarding Success Checklist - Agent Verification

**Purpose:** Verify agent is ready to execute coverage work
**Status:** Track completion with checkboxes
**Success Criteria:** All sections complete = Agent is ready
**Estimated Time:** 4-6 hours total

---

## Section 1: Environment Setup Verified (9 checkpoints)

**Goal:** Confirm system and dependencies are working

### Python & Package Installation

- [ ] **Python 3.12+** installed
  - [ ] Run: `python3 --version`
  - [ ] Expected: Python 3.12.x or higher
  - [ ] Issue? → Contact lead for Python upgrade

- [ ] **pip** updated
  - [ ] Run: `python3 -m pip --version`
  - [ ] Expected: pip 24.0 or higher
  - [ ] Issue? → Run: `python3 -m pip install --upgrade pip`

- [ ] **Project dependencies** installed
  - [ ] Run: `python3 -m pip install -e ".[dev,test]"`
  - [ ] Expected: No errors, completes in <5 min
  - [ ] Issue? → Check disk space, re-run command

### Testing & Coverage Tools

- [ ] **pytest** installed correctly
  - [ ] Run: `pytest --version`
  - [ ] Expected: pytest 9.0.0 or higher
  - [ ] Issue? → Run: `python3 -m pip install pytest pytest-asyncio pytest-timeout`

- [ ] **coverage** installed correctly
  - [ ] Run: `coverage --version`
  - [ ] Expected: coverage 7.11.3 or higher
  - [ ] Issue? → Run: `python3 -m pip install coverage`

### Validation Script

- [ ] **PRE_STARTUP_VALIDATION.sh** runs successfully
  - [ ] Run: `bash PRE_STARTUP_VALIDATION.sh`
  - [ ] Expected: All checks show ✅ PASS
  - [ ] Result: [PASS / WARN / FAIL] _____________
  - [ ] Issue? → Review script output, fix reported problems

### Directory & Path Setup

- [ ] **Project root** confirmed
  - [ ] Run: `pwd`
  - [ ] Expected: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
  - [ ] Issue? → Navigate to correct directory before setup

- [ ] **conftest.py** exists
  - [ ] Run: `ls tests/conftest.py`
  - [ ] Expected: File exists and is readable
  - [ ] Issue? → File should be in repo, contact if missing

- [ ] **Git** configured for commits
  - [ ] Run: `git config user.email`
  - [ ] Expected: Your email address (not error)
  - [ ] Issue? → Run: `git config user.email 'your.email@company.com'`

---

## Section 2: First Test Running (3 checkpoints)

**Goal:** Confirm test execution and database operations work

### Hello World Test

- [ ] **HELLO_WORLD_TEST.py** copied and runnable
  - [ ] Run: `pytest HELLO_WORLD_TEST.py -v`
  - [ ] Expected: 1 test PASSED (not FAILED)
  - [ ] Output shows: "test_database_exists_and_works PASSED" ✅
  - [ ] Issue? → Review AGENT_QUICK_START.md troubleshooting

### Test Execution & Coverage

- [ ] **First test** passes locally
  - [ ] Command: `pytest tests/test_hello_world.py -v` (if you created copy)
  - [ ] Expected: All tests pass with ✅
  - [ ] Pass rate: 100% of tests passing
  - [ ] Issue? → Debug using -s flag for output: `pytest -v -s`

- [ ] **Coverage report** generates successfully
  - [ ] Run: `pytest HELLO_WORLD_TEST.py --cov=sqlite3 --cov-report=term-with-missing`
  - [ ] Expected: Coverage report shows (example):
    ```
    Name          Stmts   Miss  Cover   Missing
    sqlite3          42      5    88%
    ```
  - [ ] Database operations are covered
  - [ ] Issue? → Coverage tool may need install: `python3 -m pip install coverage`

---

## Section 3: Ready to Start Work Package (2 checkpoints)

**Goal:** Confirm understanding of assignment and ready to execute

### Work Package Assignment

- [ ] **Work package(s)** identified and understood
  - [ ] Read: WORK_PACKAGE_INDEX.md (find your agent number)
  - [ ] Found: Your assigned WP numbers (e.g., WP-1.1, WP-1.2)
  - [ ] Write your WPs here: ___________________________
  - [ ] Understand: What each WP requires
  - [ ] Issue? → Ask lead: "What are my Week 1 packages?"

- [ ] **Git workflow** tested
  - [ ] Create test branch: `git checkout -b test/hello-world`
  - [ ] Made a change to any file
  - [ ] Commit it: `git add . && git commit -m "test commit"`
  - [ ] Branch exists: `git branch` shows your branch
  - [ ] Can push: `git push origin test/hello-world` (creates PR)
  - [ ] Issue? → Review AGENT_QUICK_START.md git section

---

## Sign-Off

**Agent Completion:**

- [ ] All 14 checkpoints above completed and verified
- [ ] Environment fully functional (no blockers)
- [ ] First test passing (HELLO_WORLD_TEST.py)
- [ ] Ready to execute assigned work packages

**Agent Name:** _________________________________
**Date Completed:** _________________________________
**Time Taken:** _________________ hours (typical: 4-6 hours)

**I confirm I am ready to start coverage work packages:**

Signature: _________________________________ Date: __________

---

**Lead Verification (Optional):**

- [ ] Agent demonstrated test execution in sync
- [ ] Environment verified by spot-check
- [ ] Work packages clearly assigned
- [ ] Agent has access to all required resources

**Lead Name:** _________________________________
**Verification Date:** _________________________________

---

## If Not Ready Yet

### Missing Environment?
- [ ] Review Section 1 (Environment Setup)
- [ ] Run: `bash PRE_STARTUP_VALIDATION.sh`
- [ ] Check: Each FAIL item has a reported fix
- [ ] Ask: Lead for help with dependencies

### Test Not Passing?
- [ ] Run: `pytest HELLO_WORLD_TEST.py -v -s`
- [ ] Check: Error message (database? import? path?)
- [ ] Read: AGENT_QUICK_START.md → Troubleshooting section
- [ ] Ask: In daily standup for unblock

### Don't Understand Work Packages?
- [ ] Read: WORK_PACKAGE_INDEX.md (for your agent)
- [ ] Read: Your assigned work package in WORK_PACKAGES_AGENTS.md
- [ ] Ask: Lead to explain your first 2-3 packages
- [ ] Understand: What you're testing and why

### Git/Commit Issues?
- [ ] Read: AGENT_QUICK_START.md → Tools section
- [ ] Review: README_WORK_PACKAGES.md → Essential Commands
- [ ] Verify: You can commit and push before Day 1 work

---

## Success Indicators

**You're ready when:**
- ✅ Environment section: All 9 checkpoints checked
- ✅ Test section: All 3 checkpoints checked (test passes)
- ✅ Work package section: Both checkpoints checked
- ✅ You can run: `pytest [any test] -v` without errors
- ✅ You can run: `git status` and see your branch
- ✅ You can run: `bash PRE_STARTUP_VALIDATION.sh` with all PASS

**If all above verified, you are ready to start!** 🚀

---

## Next Steps

Once this checklist is complete:

1. **Day 1 Afternoon:** Start your first work package
2. **Day 1 Standup:** Report "Onboarding complete, ready for WP-X.X"
3. **Daily:** Update DAILY_STANDUP_LOG.md with progress
4. **Follow:** AGENT_QUICK_START.md test patterns for your work

---

**Document:** ONBOARDING_SUCCESS_CHECKLIST.md
**Purpose:** Verify agent readiness before Day 1 execution
**Created:** December 8, 2025
**For:** All test implementation agents
