# TraceRTM CLI Examples

**Version**: 1.0  
**Last Updated**: 2025-01-27

---

## 📖 Common Use Cases

This guide provides practical examples for common TraceRTM CLI workflows.

---

## Example 1: Starting a New Project

### Scenario
You're starting a new web application project and want to track features, code, and tests.

### Steps

```bash
# 1. Initialize configuration
rtm config init --database-url sqlite:///myproject.db

# 2. Create project
rtm project init "Web App" --description "My web application"

# 3. Create database tables
rtm db migrate

# 4. Verify setup
rtm db status
rtm project list
```

---

## Example 2: Feature Planning

### Scenario
Plan features for a user authentication system.

### Steps

```bash
# Create epic
rtm item create "User Authentication System" \
  --view FEATURE \
  --type epic \
  --description "Complete authentication and authorization system"

# Create features under epic
rtm item create "User Login" \
  --view FEATURE \
  --type feature \
  --parent <epic-id> \
  --description "Email/password login"

rtm item create "User Registration" \
  --view FEATURE \
  --type feature \
  --parent <epic-id> \
  --description "New user signup"

# Create stories
rtm item create "User can login with email" \
  --view FEATURE \
  --type story \
  --parent <login-feature-id> \
  --status todo

rtm item create "User can reset password" \
  --view FEATURE \
  --type story \
  --parent <login-feature-id> \
  --status todo

# View feature hierarchy
rtm item list --view FEATURE
```

---

## Example 3: Code Implementation Tracking

### Scenario
Track code files that implement features.

### Steps

```bash
# Create code items
rtm item create "auth/login.py" \
  --view CODE \
  --type file \
  --description "Login endpoint implementation"

rtm item create "auth/models.py" \
  --view CODE \
  --type file \
  --description "User model"

# Create links from feature to code
rtm link create \
  --source <login-feature-id> \
  --target <login-py-id> \
  --type implements

# View code items
rtm view switch CODE
rtm item list
```

---

## Example 4: Test Coverage Tracking

### Scenario
Link test cases to features and code.

### Steps

```bash
# Create test items
rtm item create "tests/test_login.py" \
  --view TEST \
  --type test_suite \
  --description "Login functionality tests"

rtm item create "test_login_success" \
  --view TEST \
  --type test_case \
  --parent <test-suite-id>

# Link tests to feature
rtm link create \
  --source <login-feature-id> \
  --target <test-suite-id> \
  --type tested_by

# Link tests to code
rtm link create \
  --source <login-py-id> \
  --target <test-suite-id> \
  --type tested_by

# View test coverage
rtm view switch TEST
rtm item list
```

---

## Example 5: Multi-View Navigation

### Scenario
Explore a feature across all views.

### Steps

```bash
# Start in feature view
rtm view switch FEATURE
rtm item show <feature-id>

# Switch to code view to see implementation
rtm view switch CODE
rtm item list --filter <feature-id>

# Switch to test view to see tests
rtm view switch TEST
rtm item list --filter <feature-id>

# View all links
rtm link list --source <feature-id>
```

---

## Example 6: Bulk Operations

### Scenario
Update multiple items at once.

### Steps

```bash
# Update all todo items in FEATURE view to in_progress
rtm item bulk-update \
  --view FEATURE \
  --status todo \
  --new-status in_progress \
  --force

# Update all in_progress items to done
rtm item bulk-update \
  --view FEATURE \
  --status in_progress \
  --new-status done \
  --force
```

---

## Example 7: Project Backup

### Scenario
Backup project before major changes.

### Steps

```bash
# Create backup
rtm backup backup \
  --output backup_$(date +%Y%m%d).json.gz \
  --compress

# Verify backup exists
ls -lh backup_*.json.gz

# Restore if needed (destructive!)
rtm backup restore backup_20250127.json.gz --force
```

---

## Example 8: Project Switching

### Scenario
Work with multiple projects.

### Steps

```bash
# List all projects
rtm project list

# Switch to different project
rtm project switch "Project A"

# Work on Project A
rtm item list

# Switch to another project
rtm project switch "Project B"

# Work on Project B
rtm item list
```

---

## Example 9: Status Tracking

### Scenario
Track item status across views.

### Steps

```bash
# Create items with different statuses
rtm item create "Feature A" --view FEATURE --type feature --status todo
rtm item create "Feature B" --view FEATURE --type feature --status in_progress
rtm item create "Feature C" --view FEATURE --type feature --status done

# Filter by status
rtm item list --view FEATURE --status todo
rtm item list --view FEATURE --status in_progress
rtm item list --view FEATURE --status done

# Update status
rtm item update <item-id> --status done
```

---

## Example 10: Complete Workflow

### Scenario
Complete workflow from project init to feature completion.

### Steps

```bash
# 1. Setup
rtm config init --database-url sqlite:///project.db
rtm project init "My Project"
rtm db migrate

# 2. Create feature
FEATURE_ID=$(rtm item create "User Login" \
  --view FEATURE --type feature | grep "ID:" | awk '{print $2}')

# 3. Create code
CODE_ID=$(rtm item create "auth/login.py" \
  --view CODE --type file | grep "ID:" | awk '{print $2}')

# 4. Create test
TEST_ID=$(rtm item create "test_login.py" \
  --view TEST --type test_suite | grep "ID:" | awk '{print $2}')

# 5. Link everything
rtm link create --source $FEATURE_ID --target $CODE_ID --type implements
rtm link create --source $FEATURE_ID --target $TEST_ID --type tested_by
rtm link create --source $CODE_ID --target $TEST_ID --type tested_by

# 6. Update status as work progresses
rtm item update $FEATURE_ID --status in_progress
rtm item update $CODE_ID --status in_progress
rtm item update $TEST_ID --status in_progress

# 7. Mark complete
rtm item update $FEATURE_ID --status done
rtm item update $CODE_ID --status done
rtm item update $TEST_ID --status done

# 8. View results
rtm item list --view FEATURE --status done
rtm link list --source $FEATURE_ID
```

---

## Advanced Examples

### Example 11: Hierarchical Item Creation

```bash
# Create epic
EPIC_ID=$(rtm item create "Epic" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')

# Create features
FEATURE1_ID=$(rtm item create "Feature 1" --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')
FEATURE2_ID=$(rtm item create "Feature 2" --view FEATURE --type feature --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Create stories
rtm item create "Story 1" --view FEATURE --type story --parent $FEATURE1_ID
rtm item create "Story 2" --view FEATURE --type story --parent $FEATURE1_ID
rtm item create "Story 3" --view FEATURE --type story --parent $FEATURE2_ID
```

### Example 12: Cross-View Traceability

```bash
# Feature → Code → Test traceability
rtm link create --source <feature-id> --target <code-id> --type implements
rtm link create --source <code-id> --target <test-id> --type tested_by

# View traceability chain
rtm link list --source <feature-id>
rtm link list --source <code-id>
```

### Example 13: View Statistics

```bash
# Get overview of all views
rtm view stats

# Get specific view stats
rtm view stats --view FEATURE
rtm view stats --view CODE
rtm view stats --view TEST
```

---

## Tips & Tricks

### Use Partial IDs
```bash
# You don't need full UUID, just first 8 characters
rtm item show abc12345
```

### Combine Filters
```bash
# Multiple filters
rtm item list --view FEATURE --status todo --limit 10
```

### Use Force Flags
```bash
# Skip confirmations in scripts
rtm item delete <id> --force
rtm item bulk-update --force
rtm backup restore <file> --force
```

### Chain Commands
```bash
# Create and immediately show
rtm item create "Item" --view FEATURE --type feature && \
rtm item list --view FEATURE | tail -1
```

---

## Common Patterns

### Pattern 1: Feature → Code → Test
```bash
# Create feature
FEATURE=$(rtm item create "Feature" --view FEATURE --type feature | grep "ID:" | awk '{print $2}')

# Create code
CODE=$(rtm item create "code.py" --view CODE --type file | grep "ID:" | awk '{print $2}')

# Create test
TEST=$(rtm item create "test_code.py" --view TEST --type test_suite | grep "ID:" | awk '{print $2}')

# Link chain
rtm link create --source $FEATURE --target $CODE --type implements
rtm link create --source $CODE --target $TEST --type tested_by
```

### Pattern 2: Status Workflow
```bash
# Create as todo
rtm item create "Item" --view FEATURE --type feature --status todo

# Move to in_progress
rtm item update <id> --status in_progress

# Complete
rtm item update <id> --status done
```

### Pattern 3: Bulk Status Updates
```bash
# Move all todos to in_progress
rtm item bulk-update --status todo --new-status in_progress --force

# Complete all in_progress
rtm item bulk-update --status in_progress --new-status done --force
```

---

## Example 11: Querying Items

### Scenario
Find items matching specific criteria.

### Steps

```bash
# Query by status
rtm query --filter status=todo

# Query with multiple filters
rtm query --filter status=todo,view=FEATURE

# Query by relationship
rtm query --related-to ITEM-001 --link-type tests

# Cross-project query
rtm query --all-projects --status todo
```

---

## Example 12: Saved Queries

### Scenario
Save and reuse frequently-used queries.

### Steps

```bash
# Save a query
rtm saved-queries save "my-todos" --filter status=todo

# List saved queries
rtm saved-queries list

# Run saved query
rtm saved-queries run "my-todos"

# Delete saved query
rtm saved-queries delete "my-todos"
```

---

## Example 13: Progress Tracking

### Scenario
Track project progress and identify issues.

### Steps

```bash
# Show overall progress
rtm progress show

# Show progress for view
rtm progress show --view FEATURE

# Find blocked items
rtm progress blocked

# Find stalled items
rtm progress stalled --days 14

# Show velocity
rtm progress velocity --days 30

# Generate report
rtm progress report --days 30 --json
```

---

## Example 14: History & Rollback

### Scenario
View item history and rollback changes.

### Steps

```bash
# Show item history
rtm history ITEM-001

# Query state at specific date
rtm history ITEM-001 --at "2025-01-15"

# Show version info
rtm history version ITEM-001 --version 3

# Rollback to previous version
rtm history rollback ITEM-001 --version 3
```

---

## Example 15: Importing Data

### Scenario
Import data from external sources.

### Steps

```bash
# Import from JSON
rtm import json backup.json --project my-project

# Import from YAML
rtm import yaml backup.yaml --project my-project

# Import from Jira
rtm import jira jira-export.json --project imported-project

# Import from GitHub
rtm import github github-export.json --project imported-project

# Validate before importing
rtm import json backup.json --validate-only
```

---

## Example 16: Multi-Project Dashboard

### Scenario
View status of all projects at once.

### Steps

```bash
# Show dashboard
rtm dashboard

# Query across all projects
rtm query --all-projects --status todo
```

---

## Example 17: Enhanced Search

### Scenario
Find items using advanced search filters.

### Steps

```bash
# Basic search
rtm search "authentication"

# Search with filters
rtm search "login" --view FEATURE --status todo

# Search with date filters
rtm search "test" --created-after "2025-01-01"

# Fuzzy matching
rtm search "auth" --fuzzy

# Combine filters
rtm search "feature" --status blocked --owner agent-12
```

---

## Example 18: Link Management

### Scenario
Detect cycles and auto-link from commits.

### Steps

```bash
# Detect dependency cycles
rtm link detect-cycles

# Auto-link from commit message
rtm link auto-link --commit-message "Implements STORY-123"

# Auto-link from file
rtm link auto-link --file commits.txt
```

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
