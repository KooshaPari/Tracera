# Pre-Startup Validation Checklist for Agents
**Project:** TraceRTM Code Coverage Enhancement to 85%+
**Purpose:** Verify environment readiness BEFORE starting work
**Created:** December 8, 2025

---

## TL;DR - Complete These 5 Steps (15 min)

- [ ] **Step 1:** Run `python3 --version` (must be 3.12+)
- [ ] **Step 2:** Run `pytest --version` (must be 9.0.0+)
- [ ] **Step 3:** Run `coverage --version` (must be 7.11.3+)
- [ ] **Step 4:** Run `git status` (must show main branch)
- [ ] **Step 5:** Run `pytest tests/unit/api/test_advanced_search_endpoint.py -v` (must pass)

If all 5 pass, you're ready to start Phase 1. Go to "Quick Start" section below.

---

## Quick Start After Validation

Once all 5 checks pass:

1. Read: `AGENT_QUICK_START.md` (1 hour)
2. Find: Your assignment in `WORK_PACKAGE_INDEX.md` (5 min)
3. Create: First branch `git checkout -b coverage/WP-X-Y-description`
4. Start: Your first work package

---

## Detailed Validation Steps

### Step 1: Python Version
```bash
python3 --version
# Expected output: Python 3.12.x or higher
# If not: Install Python 3.12+ from python.org
```
- [ ] Python version is 3.12 or higher

### Step 2: Install Dependencies
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
python3 -m pip install -e ".[dev,test]"
# Wait for completion
```
- [ ] Dependencies installed successfully

### Step 3: Verify pytest
```bash
pytest --version
# Expected output: pytest 9.0.0 or higher
# If version is lower, update: python3 -m pip install --upgrade pytest
```
- [ ] pytest version is 9.0.0+

### Step 4: Verify coverage.py
```bash
coverage --version
# Expected output: coverage 7.11.3 or higher
# If version is lower, update: python3 -m pip install --upgrade coverage
```
- [ ] coverage version is 7.11.3+

### Step 5: Verify Git Setup
```bash
git status
# Expected: "On branch main" and "nothing to commit"

git config user.name
# Expected: Your name (not empty)

git config user.email
# Expected: Your email (not empty)

# If name/email missing, set them:
# git config --global user.name "Your Name"
# git config --global user.email "your.email@example.com"
```
- [ ] Git is configured correctly
- [ ] On main branch
- [ ] No uncommitted changes

### Step 6: Verify Database Connection
```bash
python3 << 'EOF'
from src.tracertm.core.database import get_db
try:
    db = get_db()
    print("✅ Database connection working")
except Exception as e:
    print(f"❌ Database error: {e}")
EOF
```
- [ ] Database connection successful

### Step 7: Verify Service Imports
```bash
python3 << 'EOF'
from src.tracertm.services.query_service import QueryService
from src.tracertm.services.graph_service import GraphService
from src.tracertm.repositories.item_repository import ItemRepository
print("✅ All service imports successful")
EOF
```
- [ ] Service imports work correctly

### Step 8: Run Sample Test
```bash
pytest tests/unit/api/test_advanced_search_endpoint.py -v
# Expected: Tests pass, output shows "passed"
# If fails, check error message carefully
```
- [ ] Sample test passes

### Step 9: Verify Test Discovery
```bash
pytest --collect-only tests/unit/ | head -20
# Expected: Shows list of test functions
```
- [ ] Test discovery works

### Step 10: Verify Coverage Tool
```bash
coverage run --version
coverage report --version
# Both should output version info
```
- [ ] Coverage tools ready

---

## Troubleshooting

### "Python 3.12+ not found"
```bash
# Check installed versions
python3 --version
python --version

# Install from python.org or use package manager:
# macOS: brew install python@3.12
# Linux: apt-get install python3.12
# Windows: Download from python.org
```

### "pytest import error"
```bash
# Reinstall pytest
python3 -m pip install --force-reinstall pytest==9.0.0

# Verify installation
pytest --version
```

### "Database connection error"
```bash
# Check if SQLite is available
python3 -c "import sqlite3; print(sqlite3.version)"

# If error, install: python3 -m pip install sqlite3
# Note: sqlite3 usually comes with Python
```

### "Git branch issues"
```bash
# Check current branch
git branch -v

# Switch to main if needed
git checkout main

# Update from remote
git pull origin main
```

### "Test file not found"
```bash
# Verify path
ls tests/unit/api/test_advanced_search_endpoint.py

# If not found, try:
find . -name "test_*.py" -type f | head -5
```

---

## Final Validation Checklist

Complete these before starting actual work:

### Environment Ready
- [ ] Python 3.12+
- [ ] pytest 9.0.0+
- [ ] coverage 7.11.3+
- [ ] All dependencies installed
- [ ] No pip errors during install

### Repository Ready
- [ ] Git configured (name, email)
- [ ] On main branch
- [ ] No uncommitted changes
- [ ] Can pull latest

### Database Ready
- [ ] Database connection works
- [ ] SQLite available
- [ ] Test fixtures accessible

### Code Ready
- [ ] Service imports successful
- [ ] Test discovery works
- [ ] Sample tests pass
- [ ] Coverage tool functional

### Knowledge Ready
- [ ] Understand test patterns (from AGENT_QUICK_START.md)
- [ ] Know your first work package (from WORK_PACKAGE_INDEX.md)
- [ ] Know success criteria (from WORK_PACKAGES_AGENTS.md)
- [ ] Know daily workflow

---

## Sign-Off

**When to Sign Off:** After all 14 items above are checked

**What You Should Be Able To Do:**
- Create a git branch
- Write a simple test
- Run tests with pytest
- Generate coverage reports
- Commit and push to remote

**Next Steps After Sign-Off:**
1. Wait for lead confirmation to start Phase 1
2. Read AGENT_QUICK_START.md if not already done
3. Review your first work package assignment
4. Create first feature branch
5. Attend first daily standup

---

## Need Help?

**Before Contacting Lead:**
1. Re-read this entire checklist
2. Check troubleshooting section above
3. Try the command again (sometimes network issues)
4. Check AGENT_QUICK_START.md FAQ section

**When Contacting Lead:**
- Mention which step failed
- Provide full error message
- State what you've already tried
- Send this checklist with failed items marked

---

## Important Reminders

### DO ✅
- Complete ALL 14 checks
- Fix issues before moving forward
- Ask for help if stuck >15 min
- Document any unusual setup

### DON'T ❌
- Skip validation steps
- Use different Python version than 3.12+
- Ignore error messages
- Start coding until all checks pass

---

## Success Indicator

✅ **You're ready when:**
- All 14 items checked
- Can run sample test successfully
- Can create and switch branches
- Understand test patterns
- Know your first work package

🚀 **Then you can:**
- Start your first work package
- Write your first test
- Begin Phase 1 work
- Attend daily standups

---

**Document:** PRE_STARTUP_VALIDATION.md
**For:** All Test Implementation Agents
**Required Before:** Starting any work package
**Time to Complete:** 15-30 minutes

---

*Review by agent before: Day 1 second hour*
*Validation complete sign-off: Required before Phase 1 start*
*If issues: Contact lead immediately with detailed error messages*
