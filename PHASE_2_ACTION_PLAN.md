# PHASE 2 ACTION PLAN: Command Structure Refactoring

**Objective**: Fix 22 integration tests by refactoring command structure
**Estimated Time**: 4-6 hours
**Impact**: Improves pass rate from 86.1% → 92.2%
**Priority**: CRITICAL

---

## PROBLEM STATEMENT

### Current Issue
Commands are registered as Typer subapps, requiring awkward double invocation:

```bash
# Current (BAD UX):
rtm query query --filter status=todo
rtm export export --format yaml
rtm progress progress stats

# Expected (GOOD UX):
rtm query --filter status=todo
rtm export --format yaml
rtm progress stats
```

### Tests Failing
- 7 tests in `test_epic3_query_command.py`
- 3 tests in `test_epic3_yaml_export.py`
- 1 test in `test_epic3_json_output.py`
- 6 tests in `test_epic7_progress_tracking.py`
- 3 tests in `test_epic7_search_filters.py`
- 3 tests in `test_epic6_multi_project.py`

**Total**: 22+ tests blocked

---

## ROOT CAUSE ANALYSIS

### Current Architecture (Problematic)

**File**: `src/tracertm/cli/app.py`
```python
from tracertm.cli.commands import query, export, progress

# This creates nested command structure:
app.add_typer(query.app, name="query", help="Query items...")
app.add_typer(export.app, name="export", help="Export data...")
app.add_typer(progress.app, name="progress", help="Progress tracking...")
```

**File**: `src/tracertm/cli/commands/query.py`
```python
app = typer.Typer(help="Query commands")

@app.command()  # This becomes 'query query' in main app!
def query(...):
    # Implementation
```

### Result
- Main app sees `query` as a subapp
- Subapp has `query` command
- Full path: `rtm query query`
- Tests expect: `rtm query`

---

## SOLUTION APPROACH

### Option A: Flatten Command Structure (RECOMMENDED)

**Pros**:
- Better user experience
- Matches test expectations
- Simpler command hierarchy
- Easier to maintain

**Cons**:
- Requires refactoring command files
- Need to handle subcommands differently

### Option B: Update Tests

**Pros**:
- No code changes needed
- Quick fix

**Cons**:
- Bad UX persists
- User confusion
- Not scalable

**DECISION**: Choose Option A (flatten structure)

---

## IMPLEMENTATION PLAN

### Step 1: Refactor Query Command (1 hour)

**File**: `src/tracertm/cli/commands/query.py`

**Current**:
```python
import typer

app = typer.Typer(help="Query commands")

@app.command()
def query(...):
    # Implementation
```

**New**:
```python
import typer

def create_query_command():
    """Create the query command for the main app."""
    @typer.command("query")
    def query(...):
        # Same implementation
        pass
    return query
```

**File**: `src/tracertm/cli/app.py`

**Current**:
```python
from tracertm.cli.commands import query
app.add_typer(query.app, name="query")
```

**New**:
```python
from tracertm.cli.commands.query import create_query_command
app.command()(create_query_command())
```

---

### Step 2: Refactor Export Command (1 hour)

**File**: `src/tracertm/cli/commands/export.py`

Same pattern as query:
1. Remove `app = typer.Typer()`
2. Create factory function `create_export_command()`
3. Return command function
4. Update `app.py` registration

---

### Step 3: Refactor Progress Command (1 hour)

**Challenge**: Progress might have subcommands (stats, report, etc.)

**Solution**: Use command groups

**File**: `src/tracertm/cli/commands/progress.py`

**If multiple subcommands**:
```python
def create_progress_group():
    """Create progress command group."""
    group = typer.Typer(help="Progress tracking")

    @group.command("stats")
    def stats(...):
        pass

    @group.command("report")
    def report(...):
        pass

    return group
```

**File**: `src/tracertm/cli/app.py`
```python
from tracertm.cli.commands.progress import create_progress_group
app.add_typer(create_progress_group(), name="progress")
```

**Result**: `rtm progress stats` (not `rtm progress progress stats`)

---

### Step 4: Verify Search & Dashboard (30 min)

Check if these also need refactoring:
- `src/tracertm/cli/commands/search.py`
- `src/tracertm/cli/commands/dashboard.py`

**Test**:
```bash
rtm search --help
rtm dashboard --help
```

If they show nested structure, apply same fix.

---

### Step 5: Update Command Imports (30 min)

**File**: `src/tracertm/cli/app.py`

**Current**:
```python
from tracertm.cli.commands import (
    backup,
    config,
    db,
    export,
    item,
    link,
    project,
    query,
    sync,
    view,
    # ... etc
)

app.add_typer(query.app, name="query")
app.add_typer(export.app, name="export")
# ... etc
```

**New**:
```python
from tracertm.cli.commands.query import create_query_command
from tracertm.cli.commands.export import create_export_command
from tracertm.cli.commands.progress import create_progress_group
# Keep existing imports for commands that work correctly

# Register refactored commands
app.command()(create_query_command())
app.command()(create_export_command())
app.add_typer(create_progress_group(), name="progress")

# Keep existing registrations
app.add_typer(item.app, name="item")  # This one is fine (has subcommands)
app.add_typer(link.app, name="link")  # This one is fine (has subcommands)
# ... etc
```

---

### Step 6: Run Tests (30 min)

After each refactoring step:

```bash
# After query refactor:
pytest tests/integration/test_epic3_query_command.py -xvs

# After export refactor:
pytest tests/integration/test_epic3_yaml_export.py -xvs
pytest tests/integration/test_epic3_json_output.py::test_query_json_output -xvs

# After progress refactor:
pytest tests/integration/test_epic7_progress_tracking.py -xvs

# After search refactor:
pytest tests/integration/test_epic7_search_filters.py -xvs

# After dashboard refactor:
pytest tests/integration/test_epic6_multi_project.py -xvs

# Full integration suite:
pytest tests/integration/ -q
```

---

## VERIFICATION CHECKLIST

### Manual Testing
```bash
# Query command
rtm query --help
rtm query --filter status=todo

# Export command
rtm export --help
rtm export --format yaml

# Progress command
rtm progress --help
rtm progress stats

# Search command
rtm search --help
rtm search "test"

# Dashboard command
rtm dashboard --help
rtm dashboard show
```

### Expected Results
- No double invocation needed
- Commands work with single name
- Help text displays correctly
- All 22 tests pass

---

## ROLLBACK PLAN

If refactoring causes issues:

1. **Git stash changes**:
   ```bash
   git stash
   ```

2. **Revert to Option B** (update tests):
   ```python
   # In test files, change:
   result = runner.invoke(app, ["query", "--filter", "status=todo"])
   # To:
   result = runner.invoke(app, ["query", "query", "--filter", "status=todo"])
   ```

3. **Create issue** for Phase 3 to revisit architecture

---

## SUCCESS CRITERIA

- ✅ All 22 integration tests pass
- ✅ Commands work with single invocation (no double names)
- ✅ Help text displays correctly
- ✅ No regression in other tests
- ✅ User experience improved
- ✅ Pass rate improved from 86.1% → 92.2%

---

## RISK ASSESSMENT

### Low Risk
- Query command (single command, no subcommands)
- Export command (single command, no subcommands)

### Medium Risk
- Progress command (might have subcommands)
- Search command (unknown structure)
- Dashboard command (unknown structure)

### Mitigation
- Test each command individually before proceeding
- Keep rollback plan ready
- Document any architectural decisions

---

## TIMELINE

| Task | Estimated Time | Cumulative |
|------|----------------|------------|
| Step 1: Query refactor | 1 hour | 1 hour |
| Step 2: Export refactor | 1 hour | 2 hours |
| Step 3: Progress refactor | 1 hour | 3 hours |
| Step 4: Search/Dashboard check | 30 min | 3.5 hours |
| Step 5: Update imports | 30 min | 4 hours |
| Step 6: Testing | 1 hour | 5 hours |
| Documentation | 30 min | 5.5 hours |
| Buffer | 30 min | 6 hours |

**Total**: 6 hours maximum

---

## DEPENDENCIES

### Before Starting
- ✅ Phase 1 complete (database fixtures working)
- ✅ Tests running successfully
- ✅ Git repository clean

### After Completion
- Ready for Phase 3 (TUI test infrastructure)
- Can proceed to database fixture enhancements
- Foundation for Phase 4 fine-tuning

---

## NOTES

### Command Structure Best Practices

**Use `add_typer()` when**:
- Command has multiple subcommands (e.g., `item create`, `item list`, `item show`)
- Grouping related commands
- Need namespace organization

**Use `@app.command()` when**:
- Single command with no subcommands
- Direct action command
- Better UX with flat structure

### Current Correct Examples
```python
# Good: item has subcommands
app.add_typer(item.app, name="item")
# Usage: rtm item create, rtm item list, rtm item show

# Good: link has subcommands
app.add_typer(link.app, name="link")
# Usage: rtm link create, rtm link list

# Bad: query should be direct command
app.add_typer(query.app, name="query")
# Current: rtm query query
# Should be: rtm query
```

---

## NEXT STEPS AFTER PHASE 2

1. **Phase 3A**: TUI Test Infrastructure (2-3 hours)
   - Add Textual app fixtures
   - Fix 146 widget tests

2. **Phase 3B**: Database Fixture Enhancement (1-2 hours)
   - Add Link, History model imports
   - Fix 4 database tests

3. **Phase 3C**: Mock Expectation Updates (3-4 hours)
   - Update 35 unit tests
   - Match actual implementation

4. **Phase 4**: Fine-tuning & Optimization
   - Target: 95%+ pass rate
   - Performance optimization
   - Coverage analysis

---

**Document Created**: December 2, 2025
**For**: Phase 2 Command Structure Refactoring
**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace`
