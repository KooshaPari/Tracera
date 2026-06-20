# Item CLI UI Components - Quick Start Guide

**Enhanced UI for Item Management Commands**

---

## Overview

The item management CLI (`rtm item`) now features beautiful, consistent UI components for better user experience. This guide shows you how to use the enhanced commands.

---

## What's New

### Visual Improvements
- ✅ **Success Panels** - Structured display of successful operations
- ✅ **Error Panels** - Clear error messages with helpful details
- ✅ **Warning Panels** - Organized warnings
- ✅ **Info Panels** - Information summaries
- ✅ **Spinners** - Loading indicators for operations
- ✅ **Progress Bars** - Visual feedback for bulk operations
- ✅ **Preview Tables** - See changes before applying
- ✅ **Interactive Wizard** - Step-by-step item creation

---

## Quick Examples

### 1. Create Item (Standard)

```bash
rtm item create "User Authentication" --view FEATURE --type epic --status todo --priority high
```

**Output:**
```
⠋ Creating epic EPIC-001...
╭─────────────────────────────────────────────────╮
│ ✓ Item Created: EPIC-001                       │
├─────────────────────────────────────────────────┤
│ ID:       EPIC-001                              │
│ Title:    User Authentication                   │
│ Type:     epic                                  │
│ View:     FEATURE                               │
│ Status:   todo                                  │
│ Priority: high                                  │
│ File:     .trace/epics/EPIC-001.md              │
│ Project:  MyProject                             │
╰─────────────────────────────────────────────────╯
```

### 2. Create Item (Interactive Wizard) 🆕

```bash
rtm item create-interactive
```

**Output:**
```
╭─────────────────────────────────────────────────╮
│ Create New Item - Step 1: Basic Information    │
╰─────────────────────────────────────────────────╯

Item title: User Login API
Description (optional): REST API endpoint for user authentication

╭─────────────────────────────────────────────────╮
│ Create New Item - Step 2: Classification       │
╰─────────────────────────────────────────────────╯

Select view:
  1. FEATURE
  2. CODE
  3. API
  4. TEST
  ...

Select item type:
  1. endpoint
  2. schema
  3. webhook

... (continues through all steps)

╭─────────────────────────────────────────────────╮
│ Create New Item - Step 5: Review & Create      │
├─────────────────────────────────────────────────┤
│ Title:       User Login API                     │
│ Description: REST API endpoint for...           │
│ View:        API                                 │
│ Type:        endpoint                            │
│ Status:      todo                                │
│ Priority:    medium                              │
│ Owner:       (unassigned)                        │
│ Parent ID:   (none)                              │
╰─────────────────────────────────────────────────╯

✓ Create this item? [y/N]: y
```

### 3. List Items

```bash
rtm item list --view FEATURE --status todo
```

**Output:**
```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ External  ┃ Title                ┃ Type    ┃ Status ┃ Priority ┃ Owner   ┃
┃ ID        ┃                      ┃         ┃        ┃          ┃         ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ EPIC-001  │ User Authentication  │ epic    │ todo   │ high     │ alice   │
│ EPIC-002  │ Dashboard UI         │ epic    │ todo   │ medium   │         │
│ STORY-042 │ Login Form           │ story   │ todo   │ medium   │ bob     │
└───────────┴──────────────────────┴─────────┴────────┴──────────┴─────────┘
```

**No Results:**
```
╭─────────────────────────────────────────────────╮
│ ⚠ No Items Found                                │
├─────────────────────────────────────────────────┤
│ Query:   Project: MyProject                     │
│ Filters: Type: all, Status: archived            │
╰─────────────────────────────────────────────────╯
```

### 4. Update Item

```bash
rtm item update EPIC-001 --status in_progress
```

**Output:**
```
⠋ Updating item EPIC-001...
╭─────────────────────────────────────────────────╮
│ ✓ Item Updated                                  │
├─────────────────────────────────────────────────┤
│ ID:      EPIC-001                               │
│ Title:   User Authentication                    │
│ Version: 2                                      │
│ File:    .trace/epics/EPIC-001.md               │
╰─────────────────────────────────────────────────╯
```

### 5. Delete Item

```bash
rtm item delete EPIC-001
```

**Output:**
```
╭─────────────────────────────────────────────────╮
│ Confirm: Delete Item                            │
├─────────────────────────────────────────────────┤
│ Are you sure you want to delete item           │
│ 'EPIC-001'?                                     │
│                                                 │
│ This action cannot be undone.                   │
╰─────────────────────────────────────────────────╯

✓ Confirm? [y/N]: y

⠋ Deleting item EPIC-001...
╭─────────────────────────────────────────────────╮
│ ✓ Item Deleted                                  │
├─────────────────────────────────────────────────┤
│ ID:           EPIC-001                          │
│ File Removed: .trace/epics/EPIC-001.md          │
│ SQLite:       Index updated                     │
╰─────────────────────────────────────────────────╯
```

### 6. Bulk Update

```bash
rtm item bulk-update --view FEATURE --status todo --new-status in_progress
```

**Output:**
```
⠋ Loading preview...
╭─────────────────────────────────────────────────╮
│ ℹ Bulk Update Preview                           │
├─────────────────────────────────────────────────┤
│ Total Items: 15                                 │
│ Updates:     status=in_progress                 │
╰─────────────────────────────────────────────────╯

Sample items (first 5):
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Title              ┃ Current       ┃ New               ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ E-01 │ User Auth          │ status=todo   │ status=in_progress│
│ E-02 │ Dashboard          │ status=todo   │ status=in_progress│
│ S-42 │ Login Form         │ status=todo   │ status=in_progress│
└──────┴────────────────────┴───────────────┴───────────────────┘

Estimated duration: 0.45s

╭─────────────────────────────────────────────────╮
│ Confirm: Bulk Update                            │
├─────────────────────────────────────────────────┤
│ Update 15 items?                                │
│                                                 │
│ This will change: status=in_progress            │
╰─────────────────────────────────────────────────╯

✓ Confirm? [y/N]: y

⠋ Updating items...
╭─────────────────────────────────────────────────╮
│ ✓ Bulk Update Complete                          │
├─────────────────────────────────────────────────┤
│ Items Updated: 15                               │
╰─────────────────────────────────────────────────╯
```

### 7. Bulk Create from CSV

```bash
rtm item bulk-create --input items.csv
```

**Output:**
```
⠋ Loading CSV preview...
╭─────────────────────────────────────────────────╮
│ ℹ Bulk Create Preview                           │
├─────────────────────────────────────────────────┤
│ CSV File:     items.csv                         │
│ Total Items:  50                                │
│ Valid Rows:   50                                │
│ Invalid Rows: 0                                 │
╰─────────────────────────────────────────────────╯

Sample items (first 5):
┏━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━┓
┃ Row ┃ Title         ┃ View   ┃ Type    ┃ Status ┃ Priority┃ Owner┃
┡━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━┩
│ 2   │ Login API     │ API    │ endpoint│ todo   │ high    │ alice│
│ 3   │ User Schema   │ API    │ schema  │ todo   │ medium  │ -    │
└─────┴───────────────┴────────┴─────────┴────────┴─────────┴──────┘

Estimated duration: 1.25s

✓ Create 50 items from CSV? [y/N]: y

⠋ Creating items from CSV...
╭─────────────────────────────────────────────────╮
│ ✓ Bulk Create Complete                          │
├─────────────────────────────────────────────────┤
│ Items Created: 50                               │
│ CSV File:      items.csv                        │
╰─────────────────────────────────────────────────╯
```

### 8. Bulk Delete

```bash
rtm item bulk-delete --status archived --permanent
```

**Output:**
```
╭─────────────────────────────────────────────────╮
│ ℹ Bulk Delete Preview                           │
├─────────────────────────────────────────────────┤
│ Total Items: 10                                 │
│ Delete Type: PERMANENT                          │
│ Filters:     status=archived, view=None, ...    │
╰─────────────────────────────────────────────────╯

Items to Delete (showing 10 of 10):
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ External  ┃ Title          ┃ Type   ┃ Status   ┃ Priority┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ OLD-001   │ Legacy Feature │ feature│ archived │ low     │
└───────────┴────────────────┴────────┴──────────┴─────────┘

╭─────────────────────────────────────────────────╮
│ Confirm: Bulk Delete                            │
├─────────────────────────────────────────────────┤
│ Are you sure you want to permanently delete    │
│ 10 items?                                       │
│                                                 │
│ This action cannot be undone!                   │
╰─────────────────────────────────────────────────╯

✓ Confirm? [y/N]: y

Deleting 10 items... ━━━━━━━━━━━━━━━━━━ 100% 0:00:00

╭─────────────────────────────────────────────────╮
│ ✓ Bulk Delete Complete                          │
├─────────────────────────────────────────────────┤
│ Items Deleted: 10                               │
╰─────────────────────────────────────────────────╯
```

---

## Error Handling

### Invalid View
```bash
rtm item create "Test" --view INVALID --type epic
```

**Output:**
```
╭─────────────────────────────────────────────────╮
│ ✗ Failed to Create Item                         │
├─────────────────────────────────────────────────┤
│ Error:   Invalid view: INVALID                  │
│ Details: Valid views: FEATURE, CODE, WIREFRAME, │
│          API, TEST, DATABASE, ROADMAP, PROGRESS │
╰─────────────────────────────────────────────────╯
```

### Item Not Found
```bash
rtm item show NONEXISTENT-001
```

**Output:**
```
╭─────────────────────────────────────────────────╮
│ ✗ Failed to Show Item                           │
├─────────────────────────────────────────────────┤
│ Error: Item not found: NONEXISTENT-001          │
╰─────────────────────────────────────────────────╯
```

---

## Command Reference

### All Enhanced Commands

| Command | UI Components Used |
|---------|-------------------|
| `create` | `spinner`, `success_panel`, `error_panel` |
| `create-interactive` 🆕 | `Wizard`, `confirm_operation`, `spinner`, `success_panel` |
| `list` | `create_item_table`, `warning_panel`, `error_panel` |
| `show` | (unchanged - future enhancement) |
| `update` | `spinner`, `success_panel`, `error_panel` |
| `delete` | `confirm_operation`, `spinner`, `success_panel`, `error_panel` |
| `bulk-update` | `spinner`, `info_panel`, `confirm_operation`, `success_panel` |
| `bulk-create` | `spinner`, `info_panel`, `confirm_operation`, `success_panel` |
| `bulk-delete` | `info_panel`, `create_item_table`, `confirm_operation`, `progress_bar` |

---

## Tips & Best Practices

### 1. Use Interactive Mode for Complex Items
```bash
# Instead of long command lines:
rtm item create "Complex Feature" --view FEATURE --type epic \
  --description "..." --status todo --priority high --owner alice

# Use the wizard:
rtm item create-interactive
```

### 2. Preview Before Bulk Operations
```bash
# Always preview before confirming (default behavior):
rtm item bulk-update --status todo --new-status in_progress

# Only skip preview in automation:
rtm item bulk-update --status todo --new-status in_progress --skip-preview
```

### 3. Use Filters Effectively
```bash
# Narrow down before bulk operations:
rtm item list --view FEATURE --status todo --priority high
rtm item bulk-update --view FEATURE --status todo --new-status in_progress
```

### 4. Check Tables Before Deletion
```bash
# Soft delete first (default):
rtm item delete EPIC-001

# Only use permanent delete when sure:
rtm item delete EPIC-001 --force --permanent
```

---

## Next Steps

1. **Try Interactive Creation:** `rtm item create-interactive`
2. **List Your Items:** `rtm item list`
3. **Preview Bulk Operations:** `rtm item bulk-update --status todo --new-status in_progress`
4. **Export to CSV:** `rtm item list --json > items.json`

---

## Need Help?

- Run `rtm item --help` for command list
- Run `rtm item <command> --help` for command-specific help
- Check `/docs/guides/` for more detailed guides
- Review `/docs/reports/ITEM_CLI_UI_ENHANCEMENTS.md` for technical details
