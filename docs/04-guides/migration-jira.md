# Migration Guide: From Jira to TraceRTM

**Source:** Jira  
**Target:** TraceRTM  
**Difficulty:** Medium

---

## Overview

This guide explains how to migrate your project data from Jira to TraceRTM, preserving issues, links, and metadata.

---

## Prerequisites

1. Jira export file (JSON format)
2. TraceRTM installed and configured
3. Database initialized

---

## Step 1: Export from Jira

### Option 1: Jira REST API

```bash
# Get Jira issues via API
curl -u username:password \
  "https://your-jira.atlassian.net/rest/api/3/search?jql=project=PROJ" \
  > jira-export.json
```

### Option 2: Jira UI Export

1. Go to Jira → Issues → Search
2. Apply filters
3. Export → JSON

---

## Step 2: Validate Export

```bash
# Validate Jira export format
rtm import jira jira-export.json --validate-only
```

**Expected Output:**
```
✓ Validation passed. Jira export is valid.
```

---

## Step 3: Import to TraceRTM

```bash
# Import to new project
rtm import jira jira-export.json --project "Imported from Jira"

# Or import to existing project
rtm import jira jira-export.json --project "My Project"
```

---

## Mapping

### Issue Types

| Jira Type | TraceRTM Type | View |
|-----------|---------------|------|
| Epic | epic | FEATURE |
| Story | story | FEATURE |
| Task | task | FEATURE |
| Bug | bug | FEATURE |
| Sub-task | subtask | FEATURE |

### Status Mapping

| Jira Status | TraceRTM Status |
|-------------|-----------------|
| To Do | todo |
| In Progress | in_progress |
| In Review | in_progress |
| Done | complete |
| Closed | complete |

### Link Types

| Jira Link | TraceRTM Link |
|-----------|---------------|
| relates to | relates_to |
| blocks | blocks |
| is blocked by | blocked_by |
| duplicates | duplicates |
| is duplicated by | duplicated_by |

---

## Post-Import Steps

### 1. Verify Import

```bash
# Switch to imported project
rtm project switch "Imported from Jira"

# List items
rtm item list

# Check links
rtm link list
```

### 2. Review and Clean Up

```bash
# Find items without links
rtm query --filter status=todo

# Update statuses if needed
rtm item update <item-id> --status in_progress
```

### 3. Organize by Views

```bash
# Move items to appropriate views
rtm item update <item-id> --view CODE  # For code-related items
rtm item update <item-id> --view TEST  # For test items
```

---

## Troubleshooting

### Issue: "Missing 'issues' field"

**Solution:** Ensure export includes issues array:
```json
{
  "issues": [...]
}
```

### Issue: "Invalid JSON"

**Solution:** Validate JSON format:
```bash
python -m json.tool jira-export.json > validated.json
```

### Issue: "Project not found"

**Solution:** Create project first:
```bash
rtm project init "My Project"
rtm import jira jira-export.json --project "My Project"
```

---

## Example

```bash
# 1. Export from Jira (via API or UI)
# 2. Validate
rtm import jira jira-export.json --validate-only

# 3. Import
rtm import jira jira-export.json --project "Jira Import"

# 4. Verify
rtm project switch "Jira Import"
rtm item list
rtm dashboard
```

---

## Summary

✅ **Exported from Jira**  
✅ **Validated export format**  
✅ **Imported to TraceRTM**  
✅ **Verified and organized**

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
