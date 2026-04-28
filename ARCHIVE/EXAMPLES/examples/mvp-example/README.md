# MVP Example Project

Example TraceRTM project demonstrating MVP features.

## Setup

```bash
# Initialize project
rtm project init mvp-example

# Or use the existing project
rtm project switch <project-id>
```

## Example Workflow

### 1. Create Requirements

```bash
# Create epic
rtm create epic "User Authentication System"

# Create stories
rtm create story "As a user, I want to login with email and password"
rtm create story "As a user, I want to reset my password"
rtm create story "As a user, I want to logout"

# Create tests
rtm create test "Test login with valid credentials"
rtm create test "Test login with invalid credentials"
rtm create test "Test password reset flow"
```

### 2. Link Requirements

```bash
# Get item IDs from rtm list output, then:

# Link epic to stories
rtm link create <epic-id> <story-1-id> --type decomposes_to
rtm link create <epic-id> <story-2-id> --type decomposes_to
rtm link create <epic-id> <story-3-id> --type decomposes_to

# Link stories to tests
rtm link create <story-1-id> <test-1-id> --type tests
rtm link create <story-1-id> <test-2-id> --type tests
rtm link create <story-2-id> <test-3-id> --type tests
```

### 3. Set Priorities and Owners

```bash
# Update priorities
rtm item update <story-1-id> --priority high
rtm item update <story-2-id> --priority medium
rtm item update <story-3-id> --priority low

# Assign owners
rtm item update <story-1-id> --owner alice
rtm item update <story-2-id> --owner bob
rtm item update <story-3-id> --owner alice
```

### 4. Update Status

```bash
# Mark as in progress
rtm item update <story-1-id> --status in_progress

# Mark as done
rtm item update <test-1-id> --status done
```

### 5. View Requirements

```bash
# List all
rtm list

# Filter by owner
rtm list --owner alice

# Filter by priority
rtm list --priority high

# Show details
rtm show <story-1-id>

# Drill down
rtm drill <epic-id> --depth 3
```

### 6. Search

```bash
# Search for "login"
rtm search "login"

# Search in specific view
rtm search "password" --view FEATURE
```

### 7. View History

```bash
# Show history
rtm history <story-1-id>

# Show specific version
rtm show <story-1-id> --version 2
```

### 8. Export

```bash
# Export to JSON
rtm export --format json --output mvp-example.json

# Export to CSV
rtm export --format csv --output mvp-example.csv

# Export to Markdown
rtm export --format markdown --output mvp-example.md
```

## Expected Output

After running the example, you should have:

- 1 epic
- 3 stories
- 3 tests
- 6 links (3 epic→story, 3 story→test)
- Priority assignments
- Owner assignments
- Status updates
- Complete traceability chain

## Verify Traceability

```bash
# Show links for epic
rtm link show <epic-id>

# Show links for story
rtm link show <story-1-id>

# Show project state
rtm state
```

---

**Last Updated**: 2025-01-27
