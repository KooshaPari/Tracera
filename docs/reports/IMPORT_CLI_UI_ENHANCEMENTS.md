# Import CLI UI Enhancements

**Date**: 2026-01-31
**Component**: CLI Import Commands
**Epic**: FR78-FR82 (Import/Export Functionality)

## Overview

Enhanced the import commands (`rtm import json`, `rtm import yaml`, `rtm import jira`, `rtm import github`) with Rich UI components, interactive data previews, and improved validation feedback.

## Changes Made

### 1. UI Component Integration

Added comprehensive Rich UI imports:

```python
from tracertm.cli.ui import (
    console,
    success_panel,
    error_panel,
    warning_panel,
    info_panel,
    spinner,
    progress_bar,
    confirm_operation,
    create_item_table,
)
from rich.panel import Panel
from rich.table import Table
```

### 2. Enhanced Command Signatures

All import commands now support:

- `--preview/--no-preview` - Toggle data preview display (default: enabled)
- `--yes/-y` - Skip confirmation prompts for automation

**Example:**
```bash
# With preview and confirmation (default)
rtm import json data.json

# No preview, auto-confirm
rtm import json data.json --no-preview --yes

# Validate only (no import)
rtm import json data.json --validate-only
```

### 3. Validation Enhancements

#### Updated Validation Functions

Changed validation functions to return both errors and warnings:

```python
def _validate_import_data(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate import data structure (FR82).

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    # ... validation logic
    return errors, warnings
```

**Improvements:**
- Distinguishes between critical errors (block import) and warnings (proceed with caution)
- Validates optional fields and provides helpful warnings
- Checks link structure for referential integrity
- Provides context-specific validation for each import format

#### Validation Display

Created `_create_validation_table()` to display validation results in a colored table:

| Type | Message |
|------|---------|
| 🔴 ERROR | Data must be a dictionary |
| 🟡 WARNING | Item 5 has no description |

### 4. Data Preview Tables

#### Generic Import Preview (JSON/YAML)

Function: `_create_import_preview(data, source_type)`

Displays:
- Total items and links count
- Preview table with first 20 items:
  - Source ID
  - Title (truncated to 50 chars)
  - Type
  - Status

**Example Output:**
```
╭─ JSON Import Preview ─────────────────────────────╮
│ JSON Import Preview                               │
│                                                   │
│ Total Items: 150                                  │
│ Total Links: 42                                   │
│                                                   │
│ (Showing first 20 of 150 items)                   │
│                                                   │
│ ┌─Source ID──┬─Title────────┬─Type──┬─Status─┐  │
│ │ PROJ-123   │ Add login... │ story │ todo   │  │
│ │ PROJ-124   │ Fix bug...   │ bug   │ done   │  │
│ └────────────┴──────────────┴───────┴────────┘  │
╰───────────────────────────────────────────────────╯
```

#### Jira Import Preview

Function: `_create_jira_preview(data)`

Displays:
- Total issues count
- Preview table with:
  - Jira Key (e.g., PROJ-123)
  - Summary
  - Issue Type
  - Status

#### GitHub Import Preview

Function: `_create_github_preview(data)`

Displays:
- Total items count
- Preview table with:
  - GitHub ID/Number
  - Title
  - Type (Issue/PR)
  - State

### 5. Progress Indicators

#### File Reading

Uses spinner during file read and parse operations:

```python
with spinner("Reading JSON file"):
    content = input_path.read_text(encoding="utf-8")
    data = json.loads(content)
```

#### Validation

Shows spinner during validation:

```python
with spinner("Validating data structure"):
    errors, warnings = _validate_import_data(data)
```

#### Import Progress

Uses progress bars with item counts during import:

```python
with progress_bar(len(items_data), f"Importing {len(items_data)} items") as (prog, task):
    for item_data in items_data:
        # ... create item
        prog.update(task, advance=1)
```

**Progress Bar Features:**
- Shows spinner animation
- Displays percentage complete
- Shows time remaining
- Real-time item count

### 6. Interactive Confirmations

Before importing, users are prompted to confirm:

```python
items_count = len(data.get("items", []))
links_count = len(data.get("links", []))
operation = f"import {items_count} item(s) and {links_count} link(s) from JSON"
if not confirm_operation(operation):
    console.print(info_panel("Import cancelled", "No changes were made"))
    return
```

**Confirmation Features:**
- Displays data preview
- Shows clear operation description
- Allows cancellation without side effects
- Can be skipped with `--yes` flag

### 7. Enhanced Error Handling

All error messages now use styled panels:

```python
# Before
console.print(f"[red]✗[/red] File not found: {input_file}")

# After
console.print(error_panel(f"File not found: {input_file}"))
```

**Error Panel Features:**
- Red border and error icon
- Main error message
- Optional details/help text
- Consistent styling

### 8. Success Feedback

Import success now displays rich summary panels:

```python
summary = f"Project: {project.name}\nItems: {items_created}\nLinks: {links_created}"
console.print(success_panel(f"Successfully imported from {source}", summary))
```

**Success Panel Features:**
- Green border and success icon
- Operation summary
- Detailed metrics (items, links, project name)
- Consistent styling

## Import Flow

### Complete Import Flow (Example: JSON)

1. **File Reading**
   - Spinner: "Reading JSON file"
   - Error handling for missing/invalid files

2. **Validation**
   - Spinner: "Validating data structure"
   - Display validation table if errors/warnings exist
   - Block import on errors
   - Warn but allow import on warnings

3. **Preview** (if `--preview` enabled, default)
   - Display preview table with first 20 items
   - Show total counts

4. **Confirmation** (if `--yes` not set)
   - Prompt: "Proceed with import N item(s) and M link(s) from JSON?"
   - Allow cancellation

5. **Import Execution**
   - Spinner: "Setting up project"
   - Progress bar: "Importing N items"
   - Progress bar: "Importing M links"

6. **Success Summary**
   - Green panel with project name, items, and links count

## Validation Coverage

### JSON/YAML Imports

**Errors:**
- Data is not a dictionary
- Missing required 'items' or 'project' field
- 'items' is not a list
- 'links' is not a list
- Item missing 'title' field
- Link missing 'source_id' or 'target_id'

**Warnings:**
- Item missing 'view' field (defaults to FEATURE)
- Item missing 'type' field (defaults to feature)
- Item missing 'description' field

### Jira Imports

**Errors:**
- Data is not a dictionary
- Missing 'issues' field
- 'issues' is not a list
- Issue missing 'key' field
- Issue missing 'fields' field

**Warnings:**
- Issue missing 'summary' field
- Issue missing 'issuetype' field
- Issue missing 'status' field

### GitHub Imports

**Errors:**
- Data is not a dictionary
- Missing 'items' or 'issues' field
- Items/issues is not a list

**Warnings:**
- Item missing 'title' field
- Item missing 'state' field

## Command Examples

### JSON Import with Preview

```bash
# Full interactive mode
rtm import json backup.json

# Output:
# ⠋ Reading JSON file...
# ⠋ Validating data structure...
# ╭─ JSON Import Preview ───────────────────╮
# │ Total Items: 25                         │
# │ Total Links: 10                         │
# │ [Preview table with 20 items]           │
# ╰─────────────────────────────────────────╯
# Proceed with import 25 item(s) and 10 link(s) from JSON? [y/N]: y
# ⠋ Setting up project...
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
# ╭─ Success ────────────────────────────────╮
# │ ✓ Successfully imported from JSON       │
# │ Project: My Project                     │
# │ Items: 25                               │
# │ Links: 10                               │
# ╰─────────────────────────────────────────╯
```

### Automated Import (CI/CD)

```bash
# No preview, auto-confirm
rtm import yaml data.yaml --no-preview --yes

# Output:
# ⠋ Reading YAML file...
# ⠋ Validating data structure...
# ⠋ Setting up project...
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02
# ╭─ Success ────────────────────────────────╮
# │ ✓ Successfully imported from YAML       │
# │ Project: CI Project                     │
# │ Items: 100                              │
# │ Links: 50                               │
# ╰─────────────────────────────────────────╯
```

### Validation Only

```bash
# Validate without importing
rtm import jira export.json --validate-only

# Output:
# ⠋ Reading Jira export file...
# ⠋ Validating Jira format...
# ┌─Type────┬─Message──────────────────────┐
# │ WARNING │ Issue PROJ-5 missing summary │
# └─────────┴──────────────────────────────┘
# ╭─ Success ──────────────────────────────╮
# │ ✓ Validation passed                   │
# │ Jira export format is valid           │
# ╰───────────────────────────────────────╯
```

### Validation Errors

```bash
rtm import json invalid.json

# Output:
# ⠋ Reading JSON file...
# ⠋ Validating data structure...
# ┌─Type──┬─Message────────────────────────┐
# │ ERROR │ Data must be a dictionary     │
# │ ERROR │ Missing 'items' field         │
# └───────┴───────────────────────────────┘
# ╭─ Error ────────────────────────────────╮
# │ ✗ Validation failed                   │
# │ Found 2 error(s)                      │
# ╰───────────────────────────────────────╯
```

## Implementation Details

### File Structure

```
src/tracertm/cli/
├── commands/
│   └── import_cmd.py        # Enhanced with Rich UI
└── ui/
    ├── __init__.py          # UI component exports
    ├── components.py        # Panels and basic components
    ├── progress.py          # Spinners and progress bars
    ├── prompts.py           # Confirmations and wizards
    ├── tables.py            # Table builders
    └── themes.py            # Colors and icons
```

### Key Functions

1. **Validation**
   - `_validate_import_data()` - JSON/YAML validation
   - `_validate_jira_format()` - Jira-specific validation
   - `_validate_github_format()` - GitHub-specific validation

2. **Preview Tables**
   - `_create_validation_table()` - Display validation results
   - `_create_import_preview()` - Generic import preview
   - `_create_jira_preview()` - Jira-specific preview
   - `_create_github_preview()` - GitHub-specific preview

3. **Import Functions**
   - `_import_data()` - Generic import with progress
   - `_import_jira_data()` - Jira import with progress
   - `_import_github_data()` - GitHub import with progress

## Benefits

### User Experience

1. **Visibility**: Users see exactly what will be imported before confirming
2. **Safety**: Validation prevents bad data from entering the system
3. **Feedback**: Clear progress indicators for long operations
4. **Error Handling**: Detailed error messages help users fix issues
5. **Consistency**: All import commands use the same UI patterns

### Automation

1. **CI/CD Friendly**: `--no-preview --yes` flags for automated scripts
2. **Validate First**: `--validate-only` for pre-flight checks
3. **Exit Codes**: Proper exit codes for error detection

### Developer Experience

1. **Reusable Components**: All UI components are in `tracertm.cli.ui`
2. **Consistent Patterns**: Same approach can be applied to other commands
3. **Type Safety**: Type hints for all validation functions
4. **Testable**: Validation logic separated from UI logic

## Testing Recommendations

### Unit Tests

1. Test validation functions with various data structures:
   - Valid data
   - Missing required fields
   - Invalid data types
   - Edge cases (empty lists, null values)

2. Test preview table generation:
   - Empty data
   - Single item
   - Many items (>20)
   - Missing optional fields

### Integration Tests

1. Test complete import flow:
   - File reading
   - Validation
   - Preview display
   - User confirmation
   - Progress tracking
   - Success feedback

2. Test error scenarios:
   - Missing file
   - Invalid JSON/YAML
   - Validation errors
   - Database errors

### E2E Tests

1. Test with real data files:
   - Actual Jira exports
   - Actual GitHub exports
   - Large datasets (performance)

## Future Enhancements

1. **Preview Customization**
   - Allow users to specify preview size (`--preview-count 50`)
   - Filter preview by type/status

2. **Advanced Validation**
   - JSON Schema validation
   - Custom validation rules
   - Warnings for data quality issues

3. **Import Statistics**
   - Show import speed (items/sec)
   - Memory usage tracking
   - Duplicate detection

4. **Rollback Support**
   - Create backup before import
   - Rollback on failure
   - Dry-run mode

5. **Parallel Import**
   - Import items in batches
   - Use multiple workers
   - Optimize for large datasets

## Backward Compatibility

All existing functionality is preserved:

- All original command-line options still work
- Default behavior includes preview (can be disabled)
- Exit codes remain consistent
- Data validation is enhanced but not breaking

## Related Files

### Modified

- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/import_cmd.py`

### Dependencies

- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/ui/__init__.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/ui/components.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/ui/progress.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/ui/prompts.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/ui/tables.py`

## Conclusion

The import commands now provide a rich, interactive experience with:

- ✅ Data previews before import
- ✅ Detailed validation with errors and warnings
- ✅ Progress tracking for long operations
- ✅ Interactive confirmations
- ✅ Consistent error handling
- ✅ Beautiful, professional UI

All changes maintain backward compatibility while significantly improving the user experience.
