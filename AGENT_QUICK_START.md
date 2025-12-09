# Agent Quick Start Guide - Code Coverage Work

**Welcome, Agent!** You've been assigned coverage work. This guide gets you moving quickly.

---

## PRE-STARTUP VALIDATION (Run First!)

Before reading anything, run this quick validation:

```bash
# Step 1: Run validation script (catches 80% of setup issues)
bash PRE_STARTUP_VALIDATION.sh

# Expected: All checks show ✅ PASS
# If any ❌ FAIL: Read the fix suggestion and run it

# Step 2: Run Hello World test (proves environment works)
pytest HELLO_WORLD_TEST.py -v

# Expected: test_database_exists_and_works PASSED ✅
# If FAILED: See troubleshooting section below
```

**Not ready yet?** Complete the ONBOARDING_SUCCESS_CHECKLIST.md first (4-6 hours)

---

## TL;DR - Start Here

1. **Run validation:** `bash PRE_STARTUP_VALIDATION.sh` (must all pass)
2. **Run first test:** `pytest HELLO_WORLD_TEST.py -v` (must pass)
3. **Read your work package:** `WORK_PACKAGES_AGENTS.md` (find your WP-X.Y)
4. **Create your test file** from template
5. **Write 50-100 tests** covering your assigned service/module
6. **Run tests locally:** `pytest tests/integration/test_*.py -v`
7. **Check coverage:** `pytest --cov=src/tracertm/services/X --cov-report=term-with-missing`
8. **Submit PR** with coverage report
9. **Repeat** for next work package

**Time per work package:** 16-40 hours

---

## Environment Setup (First Time Only)

### 1. Verify Python 3.12+
```bash
python3 --version
# Expected: Python 3.12.x or higher
```

### 2. Install Dependencies
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
python3 -m pip install -e ".[dev,test]"
```

### 3. Verify Installation
```bash
pytest --version
# Expected: pytest 9.0.0 or higher

python3 -m coverage --version
# Expected: coverage 7.11.3 or higher
```

### 4. Run Existing Tests (Sanity Check)
```bash
pytest tests/unit/api/test_advanced_search_endpoint.py -v
# Expected: All tests pass
```

### 5. IDE Setup (Optional but Recommended)

**VS Code Setup:**
```bash
# 1. Open project folder
code /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# 2. Install extensions:
#    - Python (Microsoft)
#    - Pylance
#    - pytest (LittleFox Team)

# 3. Create .vscode/settings.json:
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.python"
    }
}

# 4. Select Python interpreter: Cmd+Shift+P → "Python: Select Interpreter"
```

**PyCharm Setup:**
```bash
# 1. Open project
File → Open → /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# 2. Configure interpreter
PyCharm → Preferences → Project → Python Interpreter
  → Add Interpreter → Add Local Interpreter
  → Select existing environment or create new

# 3. Mark source root
Right-click src/ → Mark Directory as → Sources Root

# 4. Enable pytest
PyCharm → Preferences → Tools → Python Integrated Tools
  → Default test runner: pytest
```

**Both IDEs:**
- `Cmd+Shift+T` or `Ctrl+Shift+T`: Run tests
- Click "Run" icon next to test name to run single test
- Use IDE debugger: Set breakpoints, step through code
- View coverage: After running tests, IDE shows coverage

### 6. Verify Git Configuration

```bash
# Check git configuration
git config user.email
git config user.name

# If not set, configure it:
git config user.email "your.email@company.com"
git config user.name "Your Name"

# Verify it worked
git config --list | grep user
# Expected:
# user.email=your.email@company.com
# user.name=Your Name
```

---

## Quick Test Development Cycle

### Step 1: Understand Your Assignment
```bash
# Open your work package
cat WORK_PACKAGES_AGENTS.md | grep "WP-X.Y" -A 30

# Understand what service you're testing
# Look at: src/tracertm/services/[YOUR_SERVICE].py
```

### Step 2: Create Test File From Template
```bash
# Copy template
cp tests/integration/TEMPLATE.py tests/integration/test_YOUR_SERVICE.py

# Edit the class name and description
vi tests/integration/test_YOUR_SERVICE.py
```

### Step 3: Write Tests
```python
# Pattern 1: Basic Test
def test_basic_operation(self):
    """Test basic operation description"""
    # Setup
    data = create_sample_data()

    # Execute
    result = service.operation(data)

    # Verify
    assert result is not None
    assert result.status == "SUCCESS"

# Pattern 2: Error Test
def test_error_condition(self):
    """Test error handling"""
    with pytest.raises(ValueError):
        service.operation(invalid_data)

# Pattern 3: Parametrized Test
@pytest.mark.parametrize("input,expected", [
    (input1, expected1),
    (input2, expected2),
])
def test_multiple_inputs(self, input, expected):
    result = service.operation(input)
    assert result == expected
```

### Step 4: Run Tests Incrementally
```bash
# Run one test
pytest tests/integration/test_YOUR_SERVICE.py::TestClass::test_one -v

# Run class
pytest tests/integration/test_YOUR_SERVICE.py::TestClass -v

# Run all with coverage
pytest tests/integration/test_YOUR_SERVICE.py -v --cov=src/tracertm/services/YOUR_SERVICE
```

### Step 5: Check Coverage
```bash
# Simple report
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=term-with-missing

# HTML report (open in browser)
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=html
open htmlcov/index.html
```

### Step 6: Identify Gaps
```bash
# Lines NOT covered will show "0" in term-with-missing report
# Add tests for those lines

# Example output:
# Name                          Stmts   Miss  Cover   Missing
# services/query_service.py       156     31    80%    42,45,48,52-60,63
#                                              ^__ Add tests for these lines!
```

### Step 7: Repeat Until Target
- Get to 80%+ coverage (for most services)
- All tests passing
- No mocks for the service layer

---

## Key Rules

### DO ✅
- ✅ Use real database (SQLite in-memory)
- ✅ Test the actual service code
- ✅ Test error paths
- ✅ Test edge cases
- ✅ Clean up after tests (teardown)
- ✅ Use descriptive test names
- ✅ Document test intent in docstrings
- ✅ Make tests independent (no inter-test dependencies)
- ✅ Verify results with assertions

### DON'T ❌
- ❌ Mock the service you're testing
- ❌ Mock database/repository for integration tests
- ❌ Use patch() on internal methods
- ❌ Skip error cases
- ❌ Leave tests hanging (use timeouts)
- ❌ Use generic test names (test_something)
- ❌ Create tests that interfere with each other
- ❌ Test implementation details, test behavior

---

## Common Patterns

### Pattern 1: Setup/Teardown Per Test
```python
@pytest.fixture(autouse=True)
def setup(self):
    """Setup: Create fresh database for test"""
    self.db = get_test_db()  # Fresh SQLite DB
    self.service = MyService(self.db)

    yield  # Test runs here

    # Cleanup
    self.db.close()
```

### Pattern 2: Create Test Data
```python
@pytest.fixture
def sample_items(self):
    """Create 10 sample items in database"""
    items = []
    for i in range(10):
        item = Item(
            title=f"Item {i}",
            status="ACTIVE",
            priority=i % 5
        )
        self.db.add(item)
        items.append(item)
    self.db.commit()
    return items
```

### Pattern 3: Test Happy Path
```python
def test_successful_operation(self, sample_items):
    """Happy path: operation succeeds"""
    result = self.service.process_items(sample_items)

    assert result is not None
    assert len(result) == 10
    assert all(r.processed for r in result)
```

### Pattern 4: Test Error Path
```python
def test_error_handling(self):
    """Error path: invalid input raises exception"""
    with pytest.raises(ValueError) as exc_info:
        self.service.process_items(invalid_data)

    assert "invalid" in str(exc_info.value).lower()
```

### Pattern 5: Parametrized for Multiple Cases
```python
@pytest.mark.parametrize("status,expected_count", [
    ("ACTIVE", 7),
    ("INACTIVE", 2),
    ("DELETED", 1),
])
def test_filter_by_status(self, status, expected_count):
    """Test filtering by different statuses"""
    results = self.service.filter_by_status(status)
    assert len(results) == expected_count
```

### Pattern 6: Async/Await Integration Test
```python
@pytest.mark.asyncio
async def test_async_database_operation(self):
    """Test asynchronous database operation with real async code"""
    # Setup: Async database connection
    db = await get_test_db_async()
    service = ItemService(db)

    # Execute: Async operation (real code, not mocked)
    item = await service.create_async(
        name="Test Item",
        status="ACTIVE"
    )

    # Verify: Results from async operation
    assert item.id is not None
    assert item.created_at is not None
    assert item.status == "ACTIVE"

    # Cleanup: Close async connection
    await db.close()
```

**Key points for Pattern 6:**
- Mark with `@pytest.mark.asyncio` decorator
- Add `async` to function name: `async def test_...`
- Use `await` for all async operations
- Pytest-asyncio handles event loop automatically
- Still use real database (not mocked)
- Still test error paths and edge cases
- Cleanup with `await db.close()`

**When to use Pattern 6:**
- Testing service methods that are async
- Phase 1-2 work has database operations
- Storage layer has async I/O
- API handlers are async

---

## Troubleshooting

### Problem: ModuleNotFoundError - "No module named 'src'" (80% of import errors)

**This is the #1 blocker for new Python testers. You're not alone.**

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
  or
ImportError: cannot import name 'QueryService' from 'src.tracertm.services'
```

**Solutions (try in order):**

1. **Verify you're in the right directory**
   ```bash
   pwd
   # Expected: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   # If not: cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   ```

2. **Run pytest from project root**
   ```bash
   # WRONG (running from subdirectory):
   cd tests/integration
   pytest test_YOUR_SERVICE.py -v  # Will fail with import error

   # RIGHT (run from project root):
   cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
   pytest tests/integration/test_YOUR_SERVICE.py -v  # Works!
   ```

3. **Verify pip install completed successfully**
   ```bash
   python3 -m pip install -e ".[dev,test]"
   # Watch for errors at the end
   # Expected last line: "Successfully installed tracertm..."
   ```

4. **Test the import directly**
   ```bash
   python3 -c "from src.tracertm.services.query_service import QueryService; print('OK')"
   # Expected output: OK
   # If error: tracertm not installed correctly
   ```

5. **Check conftest.py exists**
   ```bash
   ls tests/conftest.py
   # Expected: File should exist
   # If not: Something's wrong with repo, contact lead
   ```

6. **Clear Python cache and reinstall**
   ```bash
   python3 -m pip uninstall tracertm -y
   rm -rf build/ dist/ *.egg-info
   python3 -m pip install -e ".[dev,test]"
   ```

**If still broken after step 6:**
- Post error message in Slack #coverage-work
- Include: Full error, your `pwd`, your Python version
- Lead will help diagnose

### Problem: Tests Hang
```bash
# Use timeout to catch hangs
pytest tests/integration/test_YOUR_SERVICE.py -v --timeout=10
# If tests hang >10 seconds, fail and show where

# Fix: Add fixture cleanup
@pytest.fixture(autouse=True)
def setup(self):
    self.db = get_test_db()
    yield
    self.db.close()  # IMPORTANT!
```

### Problem: Coverage Doesn't Increase
```bash
# See what's NOT covered
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=term-with-missing

# Lines with "0" need tests
# Example: "Missing: 42,45,48,52-60"
# Add tests that exercise those line numbers
```

### Problem: Tests Pass But Coverage Doesn't Change
**Cause:** You're mocking the code instead of testing it

```python
# ❌ WRONG (mocking)
@patch('service.repository.find')
def test_something(self, mock_repo):
    mock_repo.return_value = {}  # Mocked!
    # Real code never runs

# ✅ RIGHT (no mocking)
def test_something(self):
    self.db.add(Item(...))
    self.db.commit()
    result = self.service.find(...)  # Real code runs!
    assert result is not None
```

### Problem: Database Already Exists Error
```bash
# Use fresh database for each test
@pytest.fixture(autouse=True)
def setup(self):
    self.db = get_test_db()  # Creates fresh DB
    # Clear any existing data
    self.db.query(Item).delete()
    self.db.commit()
    yield
    self.db.close()
```

### Problem: Can't Import Service
```python
# Check import path
from src.tracertm.services.query_service import QueryService

# If not working, add to conftest.py:
import sys
sys.path.insert(0, '/path/to/src')
```

---

## Tools You'll Use

### pytest - Test Runner
```bash
# Run single file
pytest tests/integration/test_file.py -v

# Run single test
pytest tests/integration/test_file.py::ClassName::test_name -v

# Run with output
pytest tests/integration/test_file.py -v -s

# Run in parallel
pytest tests/integration/test_file.py -v -n auto
```

### coverage - Coverage Measurement
```bash
# Generate report
pytest --cov=src/tracertm/services/X --cov-report=term-with-missing

# HTML report
pytest --cov=src/tracertm/services/X --cov-report=html

# JSON report
pytest --cov=src/tracertm/services/X --cov-report=json
```

### git - Version Control
```bash
# Create branch for your work
git checkout -b coverage/WP-X-Y-description

# Commit your work
git add tests/integration/test_YOUR_SERVICE.py
git commit -m "WP-X.Y: Add test coverage for service"

# Push to remote
git push origin coverage/WP-X-Y-description
```

---

## Daily Workflow

### Morning
```bash
# Update from main
git fetch origin
git rebase origin/main

# Check your work package
cat WORK_PACKAGES_AGENTS.md | grep "WP-YOUR" -A 20
```

### During Day
```bash
# Develop tests
# Run tests frequently
pytest tests/integration/test_YOUR_SERVICE.py -v

# Check coverage
pytest tests/integration/test_YOUR_SERVICE.py \
    --cov=src/tracertm/services/YOUR_SERVICE \
    --cov-report=term-with-missing
```

### Before Standup
```bash
# Commit progress
git add .
git commit -m "WP-X.Y: [Status] Tests: [count], Coverage: [%]"
git push origin coverage/WP-X-Y-description
```

### Standup Report
```
- Completed: [X] tests, [Y]% coverage
- Working on: [What]
- Blocked by: [If any]
- Next: [What's next today]
```

---

## When You're Done

### Checklist
- [ ] All tests passing: `pytest tests/integration/test_YOUR_SERVICE.py -v`
- [ ] Coverage >80%: Verified with coverage report
- [ ] File documented: Docstrings on all classes/methods
- [ ] No mocks: Service layer not mocked
- [ ] Git branch: Pushed to origin
- [ ] PR created: With coverage report

### Create Pull Request
```bash
# Create PR (after pushing branch)
git push origin coverage/WP-X-Y-description
# Or: Use GitHub UI to create PR

# Title: WP-X.Y: [Brief description]
# Description:
# - Tests added: [count]
# - Coverage: [before]% → [after]%
# - Service: [service name]
```

---

## Resources

**Files to Read:**
- `WORK_PACKAGES_AGENTS.md` - Your specific work packages
- `WORK_TICKET_TEMPLATE.md` - Detailed ticket info
- `TEST_COVERAGE_AUDIT_2025.md` - Context on coverage gaps
- `CODE_COVERAGE_EVALUATION_85-100.md` - Why coverage is low

**Example Test:**
- `tests/integration/TEMPLATE.py` - Use this as template

**Fixtures Available:**
- `tests/integration/conftest.py` - Database/service fixtures
- `tests/fixtures.py` - Shared fixtures

**Service Documentation:**
- Check docstrings in service files
- Look at existing unit tests for patterns

---

## Questions?

### Common Questions

**Q: Should I mock services?**
A: NO! Use real database and real services. That's the whole point.

**Q: How many tests per service?**
A: 50-100+ depending on complexity. Check your work package for target.

**Q: What if a service calls another service?**
A: That's OK! Both services should be real (not mocked) for integration tests.

**Q: Can I use @pytest.mark.skip for complex tests?**
A: NO! Write the test. If it's truly impossible, ask the team.

**Q: How long should each test take?**
A: <1 second ideally. If >5 seconds, investigate why.

**Q: Can I modify the service code to make it testable?**
A: Only if the service is broken. Don't add test-only code paths.

---

## Let's Go!

You now have everything needed to execute coverage work.

**Next steps:**
1. Read your assigned work package (WP-X.Y)
2. Review the test template
3. Create your test file
4. Write 50-100 tests
5. Get >80% coverage
6. Submit PR

**Questions during execution?** Ask in standup or check resources above.

**Let's get to 85%+ coverage!** 🚀

---

*Last Updated: December 8, 2025*
*For: Test Implementation Agents*
