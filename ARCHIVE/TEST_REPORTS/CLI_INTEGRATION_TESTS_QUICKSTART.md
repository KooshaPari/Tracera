# CLI Integration Tests - Quick Start Guide

## Quick Commands

```bash
# Run all CLI integration tests
pytest tests/integration/cli/test_cli_integration.py -v

# Run with coverage report
pytest tests/integration/cli/test_cli_integration.py \
  --cov=src/tracertm/cli/commands/item \
  --cov=src/tracertm/cli/commands/link \
  --cov=src/tracertm/cli/commands/project \
  --cov-report=term-missing \
  --cov-report=html

# View HTML coverage report
open htmlcov/index.html

# Run specific test class
pytest tests/integration/cli/test_cli_integration.py::TestItemCreateIntegration -v

# Run single test
pytest tests/integration/cli/test_cli_integration.py::TestItemCreateIntegration::test_item_create_basic -v -s

# Run with verbose output
pytest tests/integration/cli/test_cli_integration.py -vv -s

# Run tests matching pattern
pytest tests/integration/cli/test_cli_integration.py -k "create" -v

# Run in parallel (faster)
pytest tests/integration/cli/test_cli_integration.py -n auto
```

## Test Structure at a Glance

```
tests/integration/cli/test_cli_integration.py
├── TestItemCreateIntegration (7 tests)
│   ├── test_item_create_basic
│   ├── test_item_create_with_all_options
│   ├── test_item_create_invalid_view
│   ├── test_item_create_invalid_type_for_view
│   ├── test_item_create_invalid_json_metadata
│   ├── test_item_create_increments_counter
│   └── test_item_create_with_parent_id
├── TestItemListIntegration (6 tests)
├── TestItemShowIntegration (3 tests)
├── TestItemUpdateIntegration (6 tests)
├── TestItemDeleteIntegration (2 tests)
├── TestLinkCreateIntegration (5 tests)
├── TestLinkListIntegration (4 tests)
├── TestLinkShowIntegration (1 test)
├── TestLinkDeleteIntegration (1 test)
├── TestProjectInitIntegration (2 tests)
├── TestProjectListIntegration (3 tests)
├── TestProjectSwitchIntegration (2 tests)
├── TestProjectExportIntegration (2 tests)
├── TestErrorHandlingIntegration (2 tests)
└── TestCompleteWorkflowIntegration (3 tests)

Total: 60+ integration tests
```

## Adding New Tests

### Template for Item Command Test
```python
def test_my_new_feature(self, runner, temp_env):
    """Test description."""
    # 1. Execute CLI command
    result = runner.invoke(
        item_app,
        ["command", "args", "--flag", "value"],
    )

    # 2. Assert command succeeded
    assert result.exit_code == 0
    assert "expected text" in result.stdout

    # 3. Verify database state
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            item = session.query(Item).filter(...).first()
            assert item.field == "expected_value"
```

### Template for Link Command Test
```python
def test_link_feature(self, runner, temp_env):
    """Test link functionality."""
    # 1. Create items first
    runner.invoke(item_app, ["create", "Item A", ...])
    runner.invoke(item_app, ["create", "Item B", ...])

    # 2. Get item IDs
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            item_a = session.query(Item).filter(...).first()
            item_b = session.query(Item).filter(...).first()

    # 3. Create link
    result = runner.invoke(
        link_app,
        ["create", item_a.id, item_b.id, "--type", "implements"],
    )

    assert result.exit_code == 0

    # 4. Verify link
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            link = session.query(Link).filter(...).first()
            assert link is not None
```

### Template for Workflow Test
```python
def test_complete_workflow(self, runner, temp_env):
    """Test multi-step workflow."""
    # Step 1: Create parent
    result1 = runner.invoke(item_app, ["create", "Parent", ...])
    assert result1.exit_code == 0

    # Step 2: Get parent ID
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            parent = session.query(Item).filter(...).first()
            parent_id = parent.id

    # Step 3: Create children
    for i in range(3):
        result = runner.invoke(
            item_app,
            ["create", f"Child {i}", "--parent", parent_id, ...],
        )
        assert result.exit_code == 0

    # Step 4: Verify hierarchy
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            children = session.query(Item).filter(
                Item.parent_id == parent_id
            ).all()
            assert len(children) == 3
```

## Debugging Failed Tests

### View Full CLI Output
```python
def test_debug_example(self, runner, temp_env):
    result = runner.invoke(item_app, ["create", ...])

    # Print full output for debugging
    print(f"Exit code: {result.exit_code}")
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")

    assert result.exit_code == 0
```

### Inspect Database State
```python
def test_inspect_database(self, runner, temp_env):
    runner.invoke(item_app, ["create", "Test Item", ...])

    # Inspect what's actually in the database
    with DatabaseConnection(temp_env["db_url"]) as db:
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            all_items = session.query(Item).all()
            for item in all_items:
                print(f"Item: {item.id} - {item.title} - {item.view}")

    # Now write assertions
```

### Debug Temp Environment
```python
def test_inspect_temp_env(self, runner, temp_env):
    # See what's in temp environment
    print(f"Temp dir: {temp_env['tmpdir']}")
    print(f"Trace dir: {temp_env['trace_dir']}")
    print(f"DB path: {temp_env['db_path']}")
    print(f"DB URL: {temp_env['db_url']}")

    # Check files created
    trace_dir = temp_env['trace_dir']
    print(f"Trace dir contents: {list(trace_dir.iterdir())}")
```

## Common Patterns

### Pattern: Create Item and Verify
```python
# Create
result = runner.invoke(item_app, ["create", "Item", "--view", "FEATURE", "--type", "epic"])
assert result.exit_code == 0

# Verify
with DatabaseConnection(temp_env["db_url"]) as db:
    from sqlalchemy.orm import Session
    with Session(db.engine) as session:
        item = session.query(Item).filter(Item.title == "Item").first()
        assert item is not None
```

### Pattern: Create Link Between Items
```python
# Create items
runner.invoke(item_app, ["create", "Source", ...])
runner.invoke(item_app, ["create", "Target", ...])

# Get IDs
with DatabaseConnection(temp_env["db_url"]) as db:
    from sqlalchemy.orm import Session
    with Session(db.engine) as session:
        source = session.query(Item).filter(Item.title == "Source").first()
        target = session.query(Item).filter(Item.title == "Target").first()

# Create link
runner.invoke(link_app, ["create", source.id, target.id, "--type", "implements"])
```

### Pattern: Test Error Handling
```python
# Should fail with invalid input
result = runner.invoke(item_app, ["create", "Item", "--view", "INVALID", ...])

assert result.exit_code != 0
assert "Invalid view" in result.stdout
```

## Expected Output

### Successful Test Run
```
tests/integration/cli/test_cli_integration.py::TestItemCreateIntegration::test_item_create_basic PASSED
tests/integration/cli/test_cli_integration.py::TestItemCreateIntegration::test_item_create_with_all_options PASSED
tests/integration/cli/test_cli_integration.py::TestItemCreateIntegration::test_item_create_invalid_view PASSED
...

====== 60 passed in 45.23s ======
```

### Coverage Report
```
Name                                     Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
src/tracertm/cli/commands/item.py          845     98    88%   42-45, 78-82, ...
src/tracertm/cli/commands/link.py          511     45    91%   123-125, 234-236, ...
src/tracertm/cli/commands/project.py       335     32    90%   89-92, 145-148, ...
----------------------------------------------------------------------
TOTAL                                     1691    175    90%
```

## Troubleshooting

### Issue: Tests fail with "Project not found"
**Solution**: Temp environment fixture not used. Add `temp_env` parameter:
```python
def test_my_test(self, runner, temp_env):  # Add temp_env here
    ...
```

### Issue: Database connection errors
**Solution**: Ensure you're using the temp environment's DB URL:
```python
with DatabaseConnection(temp_env["db_url"]) as db:  # Use temp_env DB
    ...
```

### Issue: Items not found after creation
**Solution**: Check project ID matches:
```python
item = session.query(Item).filter(
    Item.title == "Test",
    Item.project_id == temp_env["project_id"]  # Add project filter
).first()
```

### Issue: Config manager errors
**Solution**: Use temp environment's config manager:
```python
config_manager = temp_env["config_manager"]
```

## Performance Tips

### Run Tests in Parallel
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (much faster)
pytest tests/integration/cli/test_cli_integration.py -n auto
```

### Focus on Failing Tests
```bash
# Run only failed tests from last run
pytest tests/integration/cli/test_cli_integration.py --lf

# Run failed tests first
pytest tests/integration/cli/test_cli_integration.py --ff
```

### Skip Slow Tests During Development
```python
@pytest.mark.slow
def test_slow_operation(self, runner, temp_env):
    ...

# Run without slow tests
pytest tests/integration/cli/test_cli_integration.py -m "not slow"
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run CLI Integration Tests
  run: |
    pytest tests/integration/cli/test_cli_integration.py \
      --cov=src/tracertm/cli/commands \
      --cov-report=xml \
      --cov-report=term \
      -v
```

### Pre-commit Hook
```bash
#!/bin/bash
# Run CLI integration tests before commit
pytest tests/integration/cli/test_cli_integration.py --tb=short -q
```

## Key Files Reference

- **Test File**: `tests/integration/cli/test_cli_integration.py`
- **Item Commands**: `src/tracertm/cli/commands/item.py`
- **Link Commands**: `src/tracertm/cli/commands/link.py`
- **Project Commands**: `src/tracertm/cli/commands/project.py`
- **Config Manager**: `src/tracertm/config/manager.py`
- **Database Models**: `src/tracertm/models/`

## Next Steps

1. Run tests: `pytest tests/integration/cli/test_cli_integration.py -v`
2. Check coverage: Add `--cov` flags
3. Review missing lines in coverage report
4. Add tests for uncovered edge cases
5. Ensure all tests pass before committing

---

**Quick Start Complete!** You now have 60+ integration tests ready to achieve 80%+ coverage for CLI commands.
