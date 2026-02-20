# Migration Guide: From Spreadsheets to TraceRTM

**Source:** CSV/Excel Spreadsheets  
**Target:** TraceRTM  
**Difficulty:** Easy

---

## Overview

This guide explains how to migrate your project data from spreadsheets (CSV/Excel) to TraceRTM.

---

## Prerequisites

1. Spreadsheet file (CSV format)
2. TraceRTM installed and configured
3. Database initialized

---

## Step 1: Prepare Spreadsheet

### CSV Format

Your CSV should have these columns:

```csv
title,description,view,type,status,priority,owner
"User Login","Login feature",FEATURE,feature,todo,high,alice
"auth.py","Auth module",CODE,file,todo,medium,bob
```

### Required Columns

- `title` (required)
- `view` (required): FEATURE, CODE, TEST, API, etc.
- `type` (required): feature, file, test_suite, endpoint, etc.

### Optional Columns

- `description`
- `status`: todo, in_progress, blocked, complete, cancelled
- `priority`: low, medium, high
- `owner`
- `parent_id`: For hierarchical items

---

## Step 2: Convert to JSON/YAML

### Option 1: Python Script

```python
import csv
import json

# Read CSV
items = []
with open('spreadsheet.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        items.append(row)

# Convert to TraceRTM format
data = {
    "items": items
}

# Save as JSON
with open('import.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Option 2: Manual Conversion

Convert CSV to JSON manually or use online tools.

---

## Step 3: Validate

```bash
# Validate JSON format
rtm import json import.json --validate-only
```

---

## Step 4: Import

```bash
# Import from JSON
rtm import json import.json --project "Imported from Spreadsheet"
```

---

## Example CSV

```csv
title,description,view,type,status,priority,owner
"Epic: User Management","User management epic",FEATURE,epic,todo,high,
"User Registration","Registration feature",FEATURE,feature,todo,high,alice
"User Login","Login feature",FEATURE,feature,todo,high,alice
"auth/register.py","Registration code",CODE,file,todo,medium,bob
"auth/login.py","Login code",CODE,file,todo,medium,bob
"tests/test_register.py","Registration tests",TEST,test_suite,todo,medium,charlie
"tests/test_login.py","Login tests",TEST,test_suite,todo,medium,charlie
```

---

## Post-Import Steps

### 1. Verify Import

```bash
# Switch to imported project
rtm project switch "Imported from Spreadsheet"

# List items
rtm item list

# Check by view
rtm item list --view FEATURE
rtm item list --view CODE
```

### 2. Create Links

```bash
# Link features to code
rtm link create --source <register-feature-id> --target <register.py-id> --type implements

# Link code to tests
rtm link create --source <register.py-id> --target <test_register.py-id> --type tested_by
```

---

## Troubleshooting

### Issue: "Missing 'title' field"

**Solution:** Ensure CSV has `title` column.

### Issue: "Invalid view"

**Solution:** Use valid views: FEATURE, CODE, TEST, API, DATABASE, ROADMAP, PROGRESS

### Issue: "Invalid type"

**Solution:** Use valid types for each view.

---

## Summary

✅ **Prepared CSV spreadsheet**  
✅ **Converted to JSON**  
✅ **Validated format**  
✅ **Imported to TraceRTM**  
✅ **Created links**

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
