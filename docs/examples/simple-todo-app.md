# Example Project: Simple TODO App

**Project Type:** Simple (10 features, 1 view)  
**Complexity:** Low  
**Estimated Time:** 1-2 hours

---

## Overview

This example demonstrates using TraceRTM for a simple TODO application with 10 features in a single FEATURE view. Perfect for learning the basics.

---

## Project Setup

```bash
# Initialize project
rtm config init --database-url sqlite:///todo-app.db
rtm project init "Simple TODO App" --description "A basic todo application"
rtm db migrate
```

---

## Creating Features

### Step 1: Create Epic

```bash
EPIC_ID=$(rtm item create "TODO App Features" \
  --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
```

### Step 2: Create Features

```bash
# Feature 1: Add Task
FEATURE1=$(rtm item create "Add Task" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 2: List Tasks
FEATURE2=$(rtm item create "List Tasks" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 3: Mark Complete
FEATURE3=$(rtm item create "Mark Complete" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 4: Delete Task
FEATURE4=$(rtm item create "Delete Task" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 5: Edit Task
FEATURE5=$(rtm item create "Edit Task" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 6: Filter Tasks
FEATURE6=$(rtm item create "Filter Tasks" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 7: Search Tasks
FEATURE7=$(rtm item create "Search Tasks" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 8: Sort Tasks
FEATURE8=$(rtm item create "Sort Tasks" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 9: Persist Data
FEATURE9=$(rtm item create "Persist Data" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Feature 10: Export Tasks
FEATURE10=$(rtm item create "Export Tasks" \
  --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')
```

---

## Viewing the Project

```bash
# List all features
rtm item list --view FEATURE

# Show progress
rtm progress show --view FEATURE

# View hierarchy
rtm item show $EPIC_ID
```

---

## Tracking Progress

```bash
# Update feature status
rtm item update $FEATURE1 --status in_progress
rtm item update $FEATURE1 --status complete

# View progress
rtm progress show

# Generate report
rtm progress report --days 7
```

---

## Exporting the Project

```bash
# Export to JSON
rtm export --format json --output todo-app.json

# Export to YAML
rtm export --format yaml --output todo-app.yaml
```

---

## Summary

This simple project demonstrates:
- ✅ Project initialization
- ✅ Creating items in FEATURE view
- ✅ Hierarchical organization (Epic → Features)
- ✅ Status tracking
- ✅ Progress monitoring
- ✅ Data export

**Total Items:** 11 (1 epic + 10 features)  
**Views Used:** 1 (FEATURE)  
**Complexity:** Low

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
