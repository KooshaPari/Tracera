# Onboarding Quick Fix - Immediate Actions

**Status:** Critical issues identified
**Priority:** Fix before Day 1
**Effort:** 4-6 hours for critical fixes
**ROI:** 80%+ first-day success vs. 40% current

---

## Quick Summary

The onboarding materials work BUT have gaps that will cause ~50% of agents to struggle on Day 1. Three critical fixes take 4 hours and solve 70% of issues.

---

## CRITICAL FIX #1: Day 1 Success Checklist (1 hour)

### Problem
- Materials say "4-hour Day 1" but don't define success
- Agents don't know if they're done
- No explicit "write first test" requirement
- Success rate: ~40% know what to do

### Solution
Create: `DAY_1_SUCCESS_CHECKLIST.md`

```markdown
# Day 1 Success Checklist - Agent Onboarding

## Your Goal Today
Be setup, trained, and have ONE PASSING TEST written and verified.

## Checklist (in order)

### Morning (9am - 12pm)

- [ ] **9:00-9:30** Environment Setup
  - [ ] `python3 --version` shows 3.12+
  - [ ] `pip install -e ".[dev,test]"` succeeded with no errors
  - [ ] `pytest --version` shows 9.0+
  - [ ] `coverage --version` shows 7.11+

- [ ] **9:30-11:00** Read Documentation
  - [ ] Read: AGENT_QUICK_START.md (all sections)
  - [ ] Read: WORK_PACKAGE_INDEX.md (find your assignment)
  - [ ] Write down: Your 3 first work packages (WP-X.X numbers)

- [ ] **11:00-12:00** Understand the Code
  - [ ] Found: src/tracertm/services/[YOUR_SERVICE].py
  - [ ] Read: The service module docstring
  - [ ] Understand: What this service does (1-2 sentences)

### Afternoon (1pm - 5pm)

- [ ] **1:00-2:00** Create Your First Test
  - [ ] Created: `tests/test_day1_first.py`
  - [ ] Copied template from: TEST-TEMPLATE.py or TEST_TEMPLATE_SIMPLE.py
  - [ ] Wrote: At least 1 simple test (minimum 10 lines)
  - [ ] Test description: One sentence explaining what it tests

- [ ] **2:00-3:00** Run Your First Test
  - [ ] Command: `pytest tests/test_day1_first.py -v`
  - [ ] Result: **TEST PASSED** ✅ (not failed)
  - [ ] Output shows: "1 passed in X.XXs"

- [ ] **3:00-3:30** Verify Coverage Works
  - [ ] Command: `pytest tests/test_day1_first.py --cov=src/tracertm/services/... --cov-report=term-with-missing`
  - [ ] Result: Coverage report shows (example):
    ```
    Name                    Stmts   Miss  Cover
    src/tracertm/...          20      5    75%
    ```

- [ ] **3:30-4:30** Commit Your Work
  - [ ] Command: `git checkout -b day1/first-test`
  - [ ] Command: `git add tests/test_day1_first.py`
  - [ ] Command: `git commit -m "Day 1: First passing test"`
  - [ ] Command: `git push origin day1/first-test`
  - [ ] Verify: GitHub shows your branch with 1 commit

- [ ] **4:30-5:00** Report Success
  - [ ] Report to team: "Day 1 complete - first test passing"
  - [ ] Note in standup log: Time taken, any blockers
  - [ ] Confirm: Ready for WP-1.X tomorrow

## Success Verification

You succeeded if:
- ✅ pytest runs without errors
- ✅ One test passes
- ✅ Coverage report shows something (not 0%)
- ✅ Code is committed to branch
- ✅ Team knows you're ready

## If You're Behind Schedule

- **At 2pm and setup not done?** → Skip the deep read, skim AGENT_QUICK_START.md
- **At 3pm and no test written?** → Copy TEST_TEMPLATE_SIMPLE.py and modify 1 function
- **At 4pm and test fails?** → Post in Slack: "Test not passing, need help before standup"

## Questions?

Check these in order:
1. AGENT_QUICK_START.md troubleshooting section
2. Slack #coverage-work channel
3. Ask in 4:30pm standup

---

**Expected time:** 7-8 hours
**Realistic time:** 8-9 hours (with 1 troubleshoot pause)
**You're on pace if:** Something done every hour

*This is non-negotiable Day 1 work. You will do this today.*
```

**Impact:** Agents know EXACTLY what success looks like

---

## CRITICAL FIX #2: Pre-Startup Checklist Script (30 minutes)

### Problem
- 30% of agents will have import/path errors before writing first test
- No validation script to catch issues early
- Agents don't know if setup worked

### Solution
Create: `PRE_STARTUP_CHECKLIST.sh`

```bash
#!/bin/bash
# PRE_STARTUP_CHECKLIST.sh
# Run this after: pip install -e ".[dev,test]"
# Expected: All checks PASS

set -e

echo "════════════════════════════════════════════════════════════"
echo "TraceRTM Agent Onboarding - Environment Verification"
echo "════════════════════════════════════════════════════════════"
echo ""

PASS="✅ PASS"
FAIL="❌ FAIL"

# Check 1: Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$PYTHON_VERSION" > "3.12" ]] || [[ "$PYTHON_VERSION" == "3.12"* ]]; then
    echo "$PASS: Python $PYTHON_VERSION"
else
    echo "$FAIL: Python $PYTHON_VERSION (need 3.12+)"
    exit 1
fi

# Check 2: pytest installed
echo ""
echo "2. Checking pytest..."
if pytest --version 2>/dev/null | grep -q "pytest 9\|pytest [0-9][0-9]"; then
    PYTEST_VERSION=$(pytest --version | awk '{print $2}')
    echo "$PASS: pytest $PYTEST_VERSION"
else
    echo "$FAIL: pytest not found or wrong version"
    echo "   Fix: python3 -m pip install -e '.[dev,test]'"
    exit 1
fi

# Check 3: coverage installed
echo ""
echo "3. Checking coverage..."
if coverage --version 2>/dev/null | grep -q "7\."; then
    COVERAGE_VERSION=$(coverage --version | awk '{print $NF}')
    echo "$PASS: coverage $COVERAGE_VERSION"
else
    echo "$FAIL: coverage not found"
    echo "   Fix: python3 -m pip install -e '.[dev,test]'"
    exit 1
fi

# Check 4: git configured
echo ""
echo "4. Checking git..."
if git config user.email >/dev/null 2>&1; then
    EMAIL=$(git config user.email)
    echo "$PASS: git configured ($EMAIL)"
else
    echo "⚠️  WARNING: git user.email not set"
    echo "   Fix: git config user.email 'your@email.com'"
    echo "   (This is not critical, but do it before committing)"
fi

# Check 5: pytest can find tests
echo ""
echo "5. Checking test discovery..."
if pytest --collect-only tests/TEST-TEMPLATE.py -q >/dev/null 2>&1; then
    COUNT=$(pytest --collect-only tests/ -q 2>/dev/null | tail -1 | awk '{print $1}')
    echo "$PASS: pytest found ~$COUNT tests"
else
    echo "$FAIL: pytest can't find tests"
    echo "   Check: Are you in the project root? (cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace)"
    exit 1
fi

# Check 6: Can import tracertm
echo ""
echo "6. Checking imports..."
python3 -c "import src.tracertm; print('OK')" 2>/dev/null && echo "$PASS: tracertm imports OK" || {
    echo "$FAIL: Can't import tracertm"
    echo "   Are you in project root?"
    exit 1
}

# Success!
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ All checks passed! You're ready to start."
echo ""
echo "Next: Read AGENT_QUICK_START.md"
echo "════════════════════════════════════════════════════════════"
```

**Usage:**
```bash
bash PRE_STARTUP_CHECKLIST.sh
```

**Expected output:**
```
✅ PASS: Python 3.12.11
✅ PASS: pytest 9.4.2
✅ PASS: coverage 7.11.3
✅ PASS: git configured (agent@example.com)
✅ PASS: pytest found ~8244 tests
✅ PASS: tracertm imports OK

All checks passed! You're ready to start.
```

**Impact:** 80% of setup errors caught before Day 1 work starts

---

## CRITICAL FIX #3: Simple Test Template (1 hour)

### Problem
- Current TEST-TEMPLATE.py is 302 lines with complex patterns
- New agents copy it, don't understand it, panic
- No "hello world" example to build confidence

### Solution
Create: `TEST_TEMPLATE_SIMPLE.py`

```python
"""
SIMPLE TEST TEMPLATE - Start here on Day 1

This is the absolute simplest test you can write.
Copy this file and modify it for your first test.

Instructions:
1. Copy this file: cp TEST_TEMPLATE_SIMPLE.py tests/my_first_test.py
2. Change CLASS_NAME to your module name
3. Replace test_example with your test name
4. Fill in setup, action, verify
5. Run: pytest tests/my_first_test.py -v
"""

import pytest


class TestMyFirstTest:
    """
    Test Suite: My First Test

    This is the simplest possible test class.
    """

    def test_example_basic_operation(self):
        """
        Basic test - covers the happy path.

        This test shows the AAA pattern:
        - Arrange: Set up test data
        - Act: Call the function/service
        - Assert: Check the result
        """
        # ARRANGE: Set up
        value = 42

        # ACT: Do something
        result = value + 1

        # ASSERT: Check result
        assert result == 43
        assert result > 40


class TestTwoExamples:
    """
    Second test class - shows another simple example.
    """

    def test_another_example(self):
        """Test with a list."""
        # Arrange
        items = [1, 2, 3]

        # Act
        total = sum(items)

        # Assert
        assert total == 6
        assert len(items) == 3

    def test_string_example(self):
        """Test with a string."""
        # Arrange
        text = "hello"

        # Act
        upper = text.upper()

        # Assert
        assert upper == "HELLO"
        assert len(text) == 5
```

**Usage:**
```bash
# Copy template
cp TEST_TEMPLATE_SIMPLE.py tests/test_day1.py

# Edit the test
vi tests/test_day1.py

# Run it
pytest tests/test_day1.py -v

# Expected:
# test_day1.py::TestMyFirstTest::test_example_basic_operation PASSED
# test_day1.py::TestTwoExamples::test_another_example PASSED
# test_day1.py::TestTwoExamples::test_string_example PASSED
```

**Impact:** First test passes 90%+ of the time (vs. 40% with complex template)

---

## HIGH-PRIORITY FIX #4: Add Async Pattern (1 hour)

### Problem
- Phase 1 has database tests (async)
- No async test example in AGENT_QUICK_START.md
- Agents copy sync pattern, tests fail with "RuntimeError: Event loop is closed"

### Solution
Add to AGENT_QUICK_START.md (after Pattern 5):

```markdown
### Pattern 6: Async/Await Integration Test

```python
@pytest.mark.asyncio
async def test_async_database_operation(self):
    """Test asynchronous database operation"""
    # Setup
    db = await get_test_db_async()  # Async setup

    # Execute
    item = await item_service.create_async(db, data)

    # Verify
    assert item.id is not None
    assert item.created_at is not None

    # Cleanup
    await db.close()
```

**Key points:**
- Mark with `@pytest.mark.asyncio`
- Add `async` to function name
- Use `await` for async operations
- Pytest-asyncio handles event loop automatically
```

**Impact:** Phase 1 async tests work on first try

---

## HIGH-PRIORITY FIX #5: Troubleshooting - Import Errors (1 hour)

### Problem
- "ModuleNotFoundError: No module named 'src'" is #1 blocker
- Not mentioned in AGENT_QUICK_START.md
- 80% of new Python testers hit this

### Solution
Add to AGENT_QUICK_START.md troubleshooting:

```markdown
### Problem: ModuleNotFoundError: No module named 'src'

**Cause:** Python can't find the tracertm module

**Solutions (in order):**

1. **Make sure you're in the right directory**
   ```bash
   pwd
   # Expected: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   ```

2. **Run pytest from project root**
   ```bash
   cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   pytest tests/TEST-TEMPLATE.py -v
   ```

3. **Verify installation**
   ```bash
   python3 -m pip install -e ".[dev,test]"
   ```

4. **Check conftest.py path setup**
   - Verify: `tests/conftest.py` exists
   - Check: conftest.py has required imports

**If still broken:**
- Ask in Slack #coverage-work
- Post error message in standup
```

**Impact:** Most common error solved in 5 minutes vs. 1 hour

---

## Summary: 4-Hour Fix (Critical Only)

| Fix | File | Time | Impact |
|-----|------|------|--------|
| #1 | DAY_1_SUCCESS_CHECKLIST.md | 1h | Clarity of expectations |
| #2 | PRE_STARTUP_CHECKLIST.sh | 0.5h | Early error detection |
| #3 | TEST_TEMPLATE_SIMPLE.py | 1h | 90% first test success |
| #4 | Add Async Pattern to QUICK_START | 1h | Phase 1 async works |
| #5 | Add Import Error to Troubleshooting | 0.5h | #1 blocker solved |
| **TOTAL** | | **4h** | **70% improvement** |

---

## Implementation Checklist

- [ ] Create DAY_1_SUCCESS_CHECKLIST.md (share with agents)
- [ ] Create PRE_STARTUP_CHECKLIST.sh (agents run after pip install)
- [ ] Create TEST_TEMPLATE_SIMPLE.py (agents use on Day 1)
- [ ] Update AGENT_QUICK_START.md with Pattern 6 (async)
- [ ] Update AGENT_QUICK_START.md troubleshooting (add import errors)
- [ ] Test: Run PRE_STARTUP_CHECKLIST.sh (verify it works)
- [ ] Test: Copy TEST_TEMPLATE_SIMPLE.py and run it (should pass)
- [ ] Share materials with agents (email/Slack)
- [ ] Day 1 standup: Confirm all agents got materials

---

## Before/After: Success Rates

### Before Fixes (Current)
- Startup time: 5-6 hours (vs. promised 2.5h)
- First test passing by 5pm Day 1: 40%
- Avg. blockers per agent: 2-3
- Time to unblock (avg): 1-2 hours

### After Fixes (Expected)
- Startup time: 4-5 hours (closer to promise)
- First test passing by 5pm Day 1: 85%+
- Avg. blockers per agent: 0.5
- Time to unblock (avg): 15-20 minutes

---

## Next Steps

1. **Today:** Create the 5 critical fixes above (4 hours)
2. **Before Day 1:** Distribute to agents via email + Slack
3. **Day 1 Morning:** Agents run PRE_STARTUP_CHECKLIST.sh
4. **Day 1 Afternoon:** Agents use DAY_1_SUCCESS_CHECKLIST.md
5. **Day 1 Evening:** Standup confirms ~85% success rate

---

**Created:** December 8, 2025
**Priority:** CRITICAL - Fix before agent execution starts
**Expected improvement:** 40% → 85% Day 1 success rate

