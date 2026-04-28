# Phase 2 WP-2.1: Critical Issues & Fix Plan

## Issue #1: Async/Await Mocking (10 Test Failures)

### Affected Tests
- test_sync_status_basic
- test_sync_status_with_pending_changes
- test_sync_push_basic
- test_sync_push_nothing_to_push
- test_sync_pull_basic
- test_sync_pull_nothing_new
- test_sync_full_sync
- test_sync_dry_run
- test_sync_shows_progress
- test_sync_reports_summary
- test_sync_force_overwrite

### Error Pattern
```
TraceRTMError("Push failed: a coroutine was expected, got <MagicMock...>")
TraceRTMError("Failed to get sync status: '>' not supported between instances of 'MagicMock' and 'int'")
```

### Root Cause
The sync engine methods are async but tests are mocking them with MagicMock instead of AsyncMock.

### Fix Required
In `tests/integration/cli/test_cli_medium_full_coverage.py`, change sync mock setup:

```python
# WRONG - current code
from unittest.mock import MagicMock
mock_sync_engine = MagicMock()
mock_sync_engine.process_queue.return_value = None

# CORRECT - required fix
from unittest.mock import AsyncMock
mock_sync_engine = AsyncMock()
mock_sync_engine.process_queue = AsyncMock(return_value=None)
mock_sync_engine.pull_changes = AsyncMock(return_value={})
mock_sync_engine.sync = AsyncMock(return_value={})
```

### Verification
After fix, run:
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestSyncBasicOperations -v
```

---

## Issue #2: Design Command Not Implemented (6 Test Failures)

### Affected Tests
- test_design_init_minimal
- test_design_init_with_figma
- test_design_init_overwrites_existing
- test_design_init_creates_directories
- test_design_init_creates_metadata_files
- test_design_init_sets_timestamps

### Error
```
SystemExit(2)
```

### Root Cause
The design command is not registered in the CLI. Tests expect a `design init` subcommand that doesn't exist.

### Check Current State
```bash
grep -r "design" src/tracertm/cli/commands/__init__.py
grep -r "add_command" src/tracertm/cli/commands/design.py
```

### Fix Required
1. Check if `design.py` command exists
2. Ensure it's imported and registered in CLI
3. Example registration (in main CLI init):
```python
from tracertm.cli.commands import design
# Then register:
@cli.group()
def design():
    """Design management commands"""
    pass

@design.command()
def init(storybook_path, figma_url, output_dir):
    """Initialize design tracking"""
    pass
```

### Verification
```bash
tracertm design init --help
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestDesignCommandInit::test_design_init_minimal -v
```

---

## Issue #3: Empty Name Validation (2 Test Failures)

### Affected Tests
- test_project_init_empty_name
- test_project_switch_empty_name

### Error
Test expects exit code != 0 but gets 0 (success).

### Root Cause
Empty string validation is missing in project init/switch commands.

### Files to Check
- `src/tracertm/cli/commands/project.py`

### Fix Required
Add validation in project init:
```python
def init_project(name, description, database_url):
    if not name or not name.strip():
        raise ValueError("Project name cannot be empty")
    
    name = name.strip()
    if len(name) == 0:
        raise ValueError("Project name cannot be empty or whitespace only")
```

### Verification
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectInit::test_project_init_empty_name -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectSwitch::test_project_switch_empty_name -v
```

---

## Issue #4: Storage Error Handling (1 Test Failure)

### Affected Test
- test_project_list_storage_error

### Error
Test expects error but command succeeds (exit_code == 0, expected != 0).

### Root Cause
Mock error is not being properly raised or caught by command handler.

### Fix Required
Check `src/tracertm/cli/commands/project.py` list command:
```python
def list_projects():
    try:
        projects = storage.get_all_projects()
    except StorageError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)  # Need explicit error exit
```

### Verification
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectList::test_project_list_storage_error -v
```

---

## Issue #5: Project Switch Context Issues (2 Test Failures)

### Affected Tests
- test_project_switch_to_current
- test_project_switch_preserves_settings

### Error
SystemExit(1)

### Root Cause
Project switch command has issues with:
1. Switching to already-current project
2. Preserving settings during switch

### Fix Required
Check `src/tracertm/cli/commands/project.py` switch logic:
```python
def switch_project(project_name):
    current = storage.get_current_project()
    if current == project_name:
        click.echo("Already on project: " + project_name)
        # Don't exit with error - this is not an error condition
        return
    
    # Preserve settings
    old_settings = storage.get_project_settings(current)
    storage.set_current_project(project_name)
    storage.preserve_settings(old_settings)
```

### Verification
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectSwitch::test_project_switch_to_current -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectSwitch::test_project_switch_preserves_settings -v
```

---

## Issue #6: Relative Path Handling (1 Test Failure)

### Affected Test
- test_trace_relative_path

### Error
```
FileNotFoundError: [Errno 2] No such file or directory: '...subdir/.trace'
```

### Root Cause
Test tries to create nested directory without creating parent first.

### Fix Required
In `src/tracertm/cli/commands/init.py`:
```python
def create_trace_structure(path, project_name):
    trace_dir = path / ".trace"
    # WRONG:
    # trace_dir.mkdir(exist_ok=True)
    
    # CORRECT:
    trace_dir.mkdir(parents=True, exist_ok=True)  # Create parents too!
```

### Verification
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestInitTraceStructure::test_trace_relative_path -v
```

---

## Issue #7: Test Command Infrastructure (1 Test Failure)

### Affected Test
- test_test_run_all

### Error
SystemExit(2)

### Root Cause
Test command not finding test files or configuration.

### Check
```bash
which pytest
tracertm test --help
```

### Fix Required
Verify test command implementation in `src/tracertm/cli/commands/test_command.py`.

### Verification
```bash
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestTestCommand::test_test_run_all -v
```

---

## Fix Execution Priority

### Tier 1 (Critical - Fixes ~11 tests)
1. Fix async/await mocking in sync tests
2. Implement/register design command

### Tier 2 (High - Fixes ~5 tests)
3. Add empty name validation
4. Fix storage error handling
5. Fix project switch logic

### Tier 3 (Medium - Fixes ~2 tests)
6. Fix relative path handling
7. Verify test command setup

---

## Test Regression Prevention

After applying fixes, run complete validation:

```bash
# Full test suite
pytest tests/integration/cli/test_cli_medium_full_coverage.py -v --tb=short

# Just the fixed tests
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestSyncBasicOperations -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestDesignCommandInit -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectInit::test_project_init_empty_name -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectList::test_project_list_storage_error -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestProjectSwitch -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestInitTraceStructure::test_trace_relative_path -v
pytest tests/integration/cli/test_cli_medium_full_coverage.py::TestTestCommand::test_test_run_all -v
```

---

## Summary Table

| Issue | Tests Failed | Severity | Fix Complexity | Est. Time |
|-------|-------------|----------|-----------------|-----------|
| Async Mocking | 10 | CRITICAL | Medium | 30 min |
| Design Command | 6 | CRITICAL | Medium | 45 min |
| Empty Validation | 2 | HIGH | Low | 15 min |
| Error Handling | 1 | HIGH | Low | 15 min |
| Project Switch | 2 | HIGH | Medium | 20 min |
| Path Handling | 1 | MEDIUM | Low | 10 min |
| Test Command | 1 | MEDIUM | Medium | 20 min |
| **TOTAL** | **24** | | **Medium** | **2.5 hours** |

