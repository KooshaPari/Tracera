# Migration Guide: From GitHub Projects to TraceRTM

**Source:** GitHub Projects  
**Target:** TraceRTM  
**Difficulty:** Medium

---

## Overview

This guide explains how to migrate your project data from GitHub Projects to TraceRTM, preserving issues, pull requests, and relationships.

---

## Prerequisites

1. GitHub export file (JSON format)
2. TraceRTM installed and configured
3. Database initialized

---

## Step 1: Export from GitHub

### Option 1: GitHub API

```bash
# Get GitHub issues
curl -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/repos/owner/repo/issues?state=all" \
  > github-export.json
```

### Option 2: GitHub Projects Export

1. Go to GitHub → Projects
2. Export project data
3. Save as JSON

---

## Step 2: Validate Export

```bash
# Validate GitHub export format
rtm import github github-export.json --validate-only
```

**Expected Output:**
```
✓ Validation passed. GitHub export is valid.
```

---

## Step 3: Import to TraceRTM

```bash
# Import to new project
rtm import github github-export.json --project "Imported from GitHub"

# Or import to existing project
rtm import github github-export.json --project "My Project"
```

---

## Mapping

### Issue Types

| GitHub Type | TraceRTM Type | View |
|-------------|---------------|------|
| Issue | task | FEATURE |
| Pull Request | feature | FEATURE |

### Status Mapping

| GitHub Status | TraceRTM Status |
|---------------|-----------------|
| open | todo |
| in_progress | in_progress |
| in_review | in_progress |
| closed | complete |
| done | complete |

### Link Types

| GitHub Relationship | TraceRTM Link |
|---------------------|---------------|
| PR implements issue | implements |
| PR fixes issue | fixes |
| Issue relates to issue | relates_to |

---

## Post-Import Steps

### 1. Verify Import

```bash
# Switch to imported project
rtm project switch "Imported from GitHub"

# List items
rtm item list

# Check links
rtm link list
```

### 2. Organize by Views

```bash
# Move code-related items to CODE view
rtm item update <item-id> --view CODE

# Move test items to TEST view
rtm item update <item-id> --view TEST
```

### 3. Create Additional Links

```bash
# Link PRs to issues
rtm link create --source <pr-id> --target <issue-id> --type implements
```

---

## Troubleshooting

### Issue: "Missing 'items' or 'issues' field"

**Solution:** Ensure export includes items or issues:
```json
{
  "items": [...]
}
```

### Issue: "Invalid JSON"

**Solution:** Validate JSON format:
```bash
python -m json.tool github-export.json > validated.json
```

---

## Example

```bash
# 1. Export from GitHub
curl -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/owner/repo/issues" > github-export.json

# 2. Validate
rtm import github github-export.json --validate-only

# 3. Import
rtm import github github-export.json --project "GitHub Import"

# 4. Verify
rtm project switch "GitHub Import"
rtm item list
rtm dashboard
```

---

## Summary

✅ **Exported from GitHub**  
✅ **Validated export format**  
✅ **Imported to TraceRTM**  
✅ **Verified and organized**

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
