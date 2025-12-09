# Phase 8 Next Steps: Quick Action Plan

## Current Status
- **Pass Rate**: 92.6% (2,086/2,270 passing)
- **Remaining Failures**: 166 tests
- **Code Coverage**: 53.24%

## Quick Wins (1-2 hours to 95%+ pass rate)

### Step 1: Fix ConfigManager Patches (Est. 30 min, ~100 tests)

Run bulk replacements across CLI test files:

```bash
# Fix all ConfigManager patches
find tests/unit/cli -name "*.py" -type f -exec sed -i '' \
  's/@patch("tracertm\.cli\.commands\.[a-z_]*\.ConfigManager")/@patch("tracertm.config.manager.ConfigManager")/g' {} \;

# Verify changes
pytest tests/unit/cli/ -q --tb=no | tail -5
```

### Step 2: Fix storage_helper Decorator Issues (Est. 30 min, ~40 tests)

**Files to Fix**:
- `tests/unit/cli/test_example_with_helper.py`
- `tests/unit/cli/test_mvp_shortcuts.py`
- `tests/unit/cli/test_storage_helper.py`

**Pattern**:
```python
# Change this:
@patch("tracertm.cli.commands.example_with_helper.get_current_project")

# To this:
@patch("tracertm.cli.storage_helper.get_current_project")
```

**Commands**:
```bash
sed -i '' 's/@patch("tracertm\.cli\.commands\.example_with_helper\.get_current_project")/@patch("tracertm.cli.storage_helper.get_current_project")/g' tests/unit/cli/test_example_with_helper.py

sed -i '' 's/@patch("tracertm\.cli\.commands\.example_with_helper\.get_storage_manager")/@patch("tracertm.cli.storage_helper.get_storage_manager")/g' tests/unit/cli/test_example_with_helper.py

# Similar for other helper functions
```

### Step 3: Fix Remaining E2E Tests (Est. 20 min, 8 tests)

**test_cli_state_progress_flow.py**:
```python
# Need proper ConfigManager mock
@patch("tracertm.cli.storage_helper.get_current_project")
@patch("tracertm.storage.LocalStorageManager")
```

**test_cli_sync_flow.py & test_cli_watch_flow.py**:
- Add proper fixture setup
- Mock file system operations
- Update assertion expectations

### Step 4: Fix Last API Test (Est. 10 min, 1 test)

**Option A** (Recommended): Add error handling to API
```python
# In src/tracertm/api/main.py
@app.get("/api/v1/items")
async def list_items(...):
    try:
        repo = ItemRepository(db)
        items = await repo.get_by_project(project_id)
        return {...}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Option B**: Update test expectation
```python
# In test, catch the exception instead of expecting 500
with pytest.raises(Exception):
    response = client.get("/api/v1/items?project_id=test")
```

## Detailed Fix Commands

### Complete CLI Test Fix Script

```bash
#!/bin/bash
# Save as: fix_cli_tests.sh

echo "Fixing ConfigManager patches..."
find tests/unit/cli -name "*.py" -type f -exec sed -i '' \
  's/@patch("tracertm\.cli\.commands\.[a-z_]*\.ConfigManager")/@patch("tracertm.config.manager.ConfigManager")/g' {} \;

echo "Fixing storage_helper patches..."
sed -i '' 's/patch("tracertm\.cli\.commands\.example_with_helper\.\([a-z_]*\)")/patch("tracertm.cli.storage_helper.\1")/g' \
  tests/unit/cli/test_example_with_helper.py

sed -i '' 's/patch("tracertm\.cli\.commands\.mvp_shortcuts\.\([a-z_]*\)")/patch("tracertm.cli.storage_helper.\1")/g' \
  tests/unit/cli/test_mvp_shortcuts.py

echo "Running tests..."
pytest tests/unit/cli/ -q --tb=no
```

### Verify Script

```bash
#!/bin/bash
# Save as: verify_fixes.sh

echo "=== CLI Tests ==="
pytest tests/unit/cli/ -q --tb=no | tail -3

echo -e "\n=== API Tests ==="
pytest tests/unit/api/ -q --tb=no | tail -3

echo -e "\n=== E2E Tests ==="
pytest tests/e2e/ -q --tb=no | tail -3

echo -e "\n=== Total ==="
pytest tests/ -q --tb=no | tail -3

echo -e "\n=== Coverage ==="
coverage run -m pytest tests/ -q --tb=no > /dev/null 2>&1
coverage report --include="src/*" | tail -5
```

## Testing Strategy

### Before Making Changes
```bash
# Save current test results
pytest tests/ -q --tb=no > test_results_before.txt

# Note the failure count
grep "failed" test_results_before.txt
```

### After Each Fix
```bash
# Run affected tests only
pytest tests/unit/cli/test_example_with_helper.py -q --tb=no

# If passing, run full suite
pytest tests/ -q --tb=no | tail -5
```

### Track Progress
```bash
# Create progress tracker
echo "Pass Rate Progress:" > phase8_progress.log
date >> phase8_progress.log
pytest tests/ -q --tb=no | grep -E "failed|passed" >> phase8_progress.log
```

## Expected Outcomes

### After Quick Wins (2 hours)
- **Pass Rate**: 95-98% (2,150-2,220 passing tests)
- **Remaining Failures**: 5-15 tests
- **Coverage**: ~53% (unchanged, requires new tests)

### After Coverage Push (Additional 8-10 hours)
- **Pass Rate**: 98-99% (2,220-2,245 passing tests)
- **Coverage**: 80%+ (target achieved)
- **New Tests**: ~500 new test statements

## Priority Order

1. **ConfigManager patches** (Highest ROI: 100 tests, 30 min)
2. **storage_helper patches** (High ROI: 40 tests, 30 min)
3. **E2E integration** (Medium ROI: 8 tests, 20 min)
4. **API error handling** (Low ROI: 1 test, 10 min)
5. **Coverage additions** (Long-term: requires new tests)

## Troubleshooting Guide

### If Bulk sed Fails
```bash
# Check if running on macOS (needs -i '' for in-place)
sed --version  # If GNU sed, use: sed -i

# If error "invalid command code", escape differently
# Use Python instead:
python3 << EOF
import re, glob
for f in glob.glob('tests/unit/cli/*.py'):
    content = open(f).read()
    content = re.sub(
        r'@patch\("tracertm\.cli\.commands\.[a-z_]*\.ConfigManager"\)',
        '@patch("tracertm.config.manager.ConfigManager")',
        content
    )
    open(f, 'w').write(content)
EOF
```

### If Tests Still Fail After Patch
1. Check patch location: `grep -n "@patch" test_file.py`
2. Check actual import: `grep -n "import\|from" source_file.py`
3. Verify mock setup: Run test with `-xvs` to see traceback
4. Check fixture order: Fixtures execute bottom-to-top in decorator stack

### Common Issues

**Issue**: Test passes locally but fails in CI
- **Cause**: Different Python version or missing dependencies
- **Fix**: Check CI environment, pin versions

**Issue**: Mock not being called
- **Cause**: Patch location incorrect or import happens before patch
- **Fix**: Patch at source, or use `patch.object()`

**Issue**: Assertion error on mock call
- **Cause**: Function signature changed
- **Fix**: Update mock call assertions to match new signature

## Documentation Updates Needed

After fixes complete:

1. Update main README with test running instructions
2. Add TESTING.md with patterns and best practices
3. Update CONTRIBUTING.md with test requirements
4. Add GitHub Actions workflow
5. Document coverage thresholds

## Next Session Checklist

- [ ] Run bulk ConfigManager fix
- [ ] Fix storage_helper patches
- [ ] Complete E2E test fixes
- [ ] Fix last API test
- [ ] Verify 95%+ pass rate
- [ ] Update PHASE_8_COMPLETION_REPORT.md
- [ ] Commit and push all fixes
- [ ] Create PR with summary

## Success Criteria

✅ **Phase 8 Complete When**:
- Pass rate ≥ 95% (2,150+ tests passing)
- Failures ≤ 15 tests
- All remaining failures documented
- Fix patterns documented
- Clear path to 100% defined

🎯 **Stretch Goals**:
- Pass rate ≥ 98% (2,220+ tests passing)
- Coverage ≥ 60%
- All API tests passing
- All E2E tests passing
- CI/CD integrated
