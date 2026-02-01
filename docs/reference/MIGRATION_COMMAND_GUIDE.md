# TraceRTM Migration Command Guide

## Overview

The `rtm migrate` command helps you transition from the old global storage structure (`~/.tracertm/projects/{name}/`) to the new project-local `.trace/` pattern.

## Installation

The migrate command is automatically registered in the TraceRTM CLI. No additional setup required.

## Command Syntax

```bash
rtm migrate migrate --project NAME --to PATH [--dry-run]
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `--project NAME` | Name of the project in ~/.tracertm/projects/ to migrate | Yes |
| `--to PATH` | Target directory path for .trace/ (project root) | Yes |
| `--dry-run` | Preview migration without making changes | No |

## Migration Scenarios

### Scenario 1: Old Global → New Project-Local

**From:** `~/.tracertm/projects/{name}/` (markdown files)
**To:** `{target_path}/.trace/` (project-local)

This is the primary use case for migrating existing TraceRTM projects to the new architecture.

### Scenario 2: Database-Only → Project-Local

Export items from SQLite and generate markdown files with proper structure.

## Migration Process

The migration command performs the following steps:

1. **Validation**
   - Checks if source project exists in ~/.tracertm/projects/
   - Validates target directory exists
   - Scans source directory for items

2. **Backup**
   - If .trace/ already exists in target, creates timestamped backup
   - Format: `.trace.backup.YYYYMMDD_HHMMSS`

3. **Structure Creation**
   - Creates .trace/ directory
   - Creates subdirectories: epics/, stories/, tests/, tasks/, docs/, .meta/

4. **File Migration**
   - Copies all markdown files to corresponding directories
   - Preserves file timestamps and content

5. **Metadata Generation**
   - Generates project.yaml with:
     - Auto-detected counters from existing items
     - Project metadata
     - Default settings
   - Creates/updates .meta/links.yaml

6. **Global Index Registration**
   - Registers project in ~/.tracertm/tracertm.db
   - Sets as current active project
   - Creates index entries for all items

7. **Git Integration**
   - Updates .gitignore to exclude .trace/.meta/sync.yaml
   - Preserves existing .gitignore entries

## Examples

### Example 1: Basic Migration

```bash
# Migrate a project to its source code repository
rtm migrate migrate --project my-app --to /path/to/my-app/
```

### Example 2: Dry Run Preview

```bash
# Preview what will be migrated without making changes
rtm migrate migrate --project my-app --to ./ --dry-run
```

Output:
```
╭─────────────────────────────────────────────────────────╮
│                  TraceRTM Migration                     │
│                                                          │
│ Source: /Users/you/.tracertm/projects/my-app/          │
│ Target: /path/to/my-app/.trace/                        │
│ Mode: DRY RUN                                           │
╰─────────────────────────────────────────────────────────╯

Items to Migrate
┏━━━━━━━━━┳━━━━━━━┓
┃ Type    ┃ Count ┃
┡━━━━━━━━━╇━━━━━━━┩
│ Epics   │     3 │
│ Stories │    12 │
│ Tests   │     8 │
│ Tasks   │    25 │
│ Docs    │     2 │
│ Total   │    50 │
└─────────┴───────┘

DRY RUN MODE - No changes will be made
Run without --dry-run to execute the migration
```

### Example 3: Migrate to Current Directory

```bash
# Navigate to your project root
cd /path/to/my-app

# Migrate to current directory
rtm migrate migrate --project my-app --to ./
```

## Migration Output

### Success Output

```
╭─────────────────────────────────────────────────────────╮
│                  TraceRTM Migration                     │
│                                                          │
│ Source: /Users/you/.tracertm/projects/my-app/          │
│ Target: /path/to/my-app/.trace/                        │
│ Mode: EXECUTE                                           │
╰─────────────────────────────────────────────────────────╯

Items to Migrate
[table showing counts]

Proceed with migration? [y/N]: y

✓ Backed up existing .trace/ to: .trace.backup.20250130_143022

Creating .trace/ structure...
✓ Created .trace/ directory structure

Copying markdown files...
✓ Copied 3 epics
✓ Copied 12 stories
✓ Copied 8 tests
✓ Copied 25 tasks
✓ Copied 2 docs

Generating project.yaml...
✓ Generated project.yaml
  Counters: {'epic': 4, 'story': 13, 'test': 9, 'task': 26}

Migrating links...
✓ Migrated links.yaml

Registering project in global index...
✓ Registered project in global index
  Project ID: 550e8400-e29b-41d4-a716-446655440000

✓ Migration completed successfully!

╭─────────────────────────────────────────────────────────╮
│                   Migration Summary                     │
│                                                          │
│ Location: /path/to/my-app/.trace/                      │
│                                                          │
│ Items migrated:                                         │
│   - Epics: 3                                            │
│   - Stories: 12                                         │
│   - Tests: 8                                            │
│   - Tasks: 25                                           │
│   - Docs: 2                                             │
│   Total: 50                                             │
│                                                          │
│ Next steps:                                             │
│   1. Review .trace/ directory structure                 │
│   2. Commit .trace/ to version control                  │
│   3. Use 'rtm sync' to sync with remote API             │
╰─────────────────────────────────────────────────────────╯

✓ Updated .gitignore
```

## Generated project.yaml Structure

```yaml
name: my-app
description: Migrated TraceRTM project: my-app
version: 1.0.0
migrated_at: 2025-01-30T14:30:22.123456Z

# Auto-generated counters from existing items
counters:
  epic: 4      # Next: EPIC-004
  story: 13    # Next: STORY-013
  test: 9      # Next: TEST-009
  task: 26     # Next: TASK-026

# Project-level settings
settings:
  default_priority: medium
  default_status: todo
  auto_link_commits: true

# Team/ownership
team: []

# Integration hooks
hooks:
  on_item_create: []
  on_item_update: []
  on_link_create: []
```

## Post-Migration Steps

### 1. Verify Migration

```bash
# Check .trace/ structure
ls -la .trace/

# Verify items were copied
ls .trace/epics/
ls .trace/stories/
ls .trace/tests/
ls .trace/tasks/

# Check project.yaml
cat .trace/project.yaml

# Verify links
cat .trace/.meta/links.yaml
```

### 2. Commit to Git

```bash
# Add .trace/ to version control
git add .trace/

# Commit
git commit -m "Add TraceRTM project-local storage"

# Note: .trace/.meta/sync.yaml is already in .gitignore
```

### 3. Sync with Remote

```bash
# Push local changes to remote API
rtm sync push

# Or full bidirectional sync
rtm sync
```

### 4. Re-index (if needed)

```bash
# Force full re-index of .trace/ into SQLite
rtm index --full
```

## Counter Generation

The migration command automatically detects the highest counter for each item type:

```
EPIC-001.md   → Counter: 1
EPIC-002.md   → Counter: 2
EPIC-003.md   → Counter: 3
              → Next counter: 4
```

This ensures that newly created items won't conflict with existing IDs.

## Backup Strategy

If `.trace/` already exists in the target directory:

1. Automatic backup is created: `.trace.backup.{timestamp}`
2. Backup contains complete copy of existing .trace/
3. Original .trace/ is then replaced with migrated content

To restore from backup:

```bash
# Remove migrated .trace/
rm -rf .trace/

# Restore from backup
mv .trace.backup.20250130_143022 .trace
```

## Troubleshooting

### Error: Project not found

```
Error: Project not found in ~/.tracertm/projects/: my-app
Tip: Use 'rtm project list' to see available projects
```

**Solution:** Verify the project name is correct and exists in `~/.tracertm/projects/`

### Error: Target path does not exist

```
Error: Target path does not exist: /path/to/my-app
```

**Solution:** Create the target directory first:
```bash
mkdir -p /path/to/my-app
```

### Migration fails partway through

**Solution:** Check the backup:
```bash
ls -la .trace.backup.*
```

Restore from backup and try again with `--dry-run` first.

## Safety Features

1. **Dry Run Mode**: Preview changes without modifying files
2. **Automatic Backup**: Existing .trace/ is always backed up
3. **Validation**: Checks source and target before starting
4. **Confirmation**: Prompts for confirmation before executing
5. **Atomic Operations**: Files are copied completely or not at all

## Integration with Other Commands

### After Migration

```bash
# List items from migrated project
rtm list --type epic

# Create new items (uses counters from project.yaml)
rtm create story "New feature"

# View traceability
rtm link graph EPIC-001

# Watch for changes
rtm watch

# Sync with remote
rtm sync
```

## Architecture Notes

The migration preserves the hybrid storage model:

- **SQLite** (`~/.tracertm/tracertm.db`): Fast queries, relationships, sync state
- **Markdown** (`.trace/`): Version-controlled, LLM-readable, human-editable

Both are kept in sync automatically via the storage layer.

## Migration Checklist

- [ ] Verify source project exists: `ls ~/.tracertm/projects/`
- [ ] Navigate to target directory: `cd /path/to/project`
- [ ] Preview migration: `rtm migrate migrate --project NAME --to ./ --dry-run`
- [ ] Execute migration: `rtm migrate migrate --project NAME --to ./`
- [ ] Verify .trace/ structure: `ls -la .trace/`
- [ ] Check project.yaml counters: `cat .trace/project.yaml`
- [ ] Verify links: `cat .trace/.meta/links.yaml`
- [ ] Test queries: `rtm list --type epic`
- [ ] Commit to git: `git add .trace/ && git commit`
- [ ] Sync with remote: `rtm sync`

## Related Commands

- `rtm init` - Initialize new .trace/ directory
- `rtm register` - Register existing .trace/ after git clone
- `rtm index` - Re-index .trace/ into SQLite
- `rtm sync` - Sync with remote API
- `rtm project list` - List all projects

## Further Reading

- [PROJECT_LOCAL_STORAGE.md](/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/PROJECT_LOCAL_STORAGE.md) - Project-local architecture
- [UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md](/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md) - Storage layer design
