# MVP Getting Started Guide

**TraceRTM MVP** - Quick start guide for the Minimum Viable Product.

---

## 🚀 Quick Start

### 1. Initialize a Project

```bash
rtm project init my-project
```

This creates a new project and sets up the database.

### 2. Create Requirements

Use the MVP shortcuts for simple syntax:

```bash
# Create an epic
rtm create epic "User Authentication System"

# Create a story
rtm create story "As a user, I want to login"

# Create a test
rtm create test "Test login with valid credentials"
```

Or use the full syntax:

```bash
rtm item create "User Authentication" --view FEATURE --type epic
```

### 3. Link Requirements

```bash
# Link epic to story
rtm link create <epic-id> <story-id> --type decomposes_to

# Link story to test
rtm link create <story-id> <test-id> --type tests
```

### 4. List Requirements

```bash
# List all
rtm list

# Filter by type
rtm list --type story

# Filter by status
rtm list --status active

# Filter by priority
rtm list --priority high

# Filter by owner
rtm list --owner alice
```

### 5. Show Requirement Details

```bash
# Show current version
rtm show <item-id>

# Show specific version
rtm show <item-id> --version 2

# Show with metadata
rtm show <item-id> --metadata
```

### 6. Search Requirements

```bash
rtm search "login"
rtm search "authentication" --view FEATURE
```

### 7. View History

```bash
# Show change history
rtm history <item-id>

# Show version info
rtm history version <item-id>

# Show specific version
rtm history version <item-id> --version 3
```

### 8. Export Data

```bash
# Export to JSON
rtm export --format json

# Export to CSV
rtm export --format csv --output data.csv

# Export to Markdown
rtm export --format markdown --output docs.md
```

---

## 📋 MVP Command Reference

### Project Management

| Command | Description |
|---------|-------------|
| `rtm project init <name>` | Initialize new project |
| `rtm project list` | List all projects |
| `rtm project switch <id>` | Switch to a project |

### Requirement CRUD (MVP Shortcuts)

| Command | Description |
|---------|-------------|
| `rtm create <type> <title>` | Create requirement (epic, story, test, etc.) |
| `rtm list [--type] [--status] [--priority] [--owner]` | List requirements |
| `rtm show <id> [--version]` | Show requirement details |

### Requirement CRUD (Full Syntax)

| Command | Description |
|---------|-------------|
| `rtm item create <title> --view <view> --type <type>` | Create item |
| `rtm item list [filters]` | List items |
| `rtm item show <id>` | Show item details |
| `rtm item update <id> [options]` | Update item |
| `rtm item delete <id>` | Delete item |

### Linking

| Command | Description |
|---------|-------------|
| `rtm link create <source> <target> --type <type>` | Create link |
| `rtm link list [--item <id>] [--type <type>]` | List links |
| `rtm link show <item-id>` | Show links for item |

### Search & Navigation

| Command | Description |
|---------|-------------|
| `rtm search <query>` | Search items |
| `rtm drill <id> [--depth N]` | Drill down hierarchy |
| `rtm state` | Show project state |

### History & Versioning

| Command | Description |
|---------|-------------|
| `rtm history <id>` | Show item history |
| `rtm history version <id> [--version N]` | Show version info |

### Export

| Command | Description |
|---------|-------------|
| `rtm export --format json [--output file.json]` | Export to JSON |
| `rtm export --format csv [--output file.csv]` | Export to CSV |
| `rtm export --format markdown [--output file.md]` | Export to Markdown |

---

## 📊 Requirement Types

MVP supports these types via shortcuts:

- **epic** → FEATURE view, epic type
- **feature** → FEATURE view, feature type
- **story** → FEATURE view, story type
- **task** → FEATURE view, task type
- **test** → TEST view, test_case type
- **spec** → FEATURE view, spec type

---

## 🔗 Link Types

Common link types:

- `decomposes_to` - Parent-child relationship
- `implements` - Implementation relationship
- `tests` - Test relationship
- `depends_on` - Dependency relationship
- `related_to` - General relationship

---

## 📝 Status Values

Default status values:

- `todo` - Not started
- `in_progress` - In progress
- `done` - Completed
- `blocked` - Blocked

---

## 🎯 Priority Values

Priority levels:

- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority

---

## 💡 Tips

1. **Use MVP shortcuts** for simpler syntax: `rtm create story "..."` instead of `rtm item create ...`
2. **Filter by priority/owner** to organize work: `rtm list --priority high --owner alice`
3. **Use history** to track changes: `rtm history <id>`
4. **Export regularly** for backups: `rtm export --format json --output backup.json`
5. **Link requirements** to build traceability: `rtm link create <source> <target> --type implements`

---

## 🆘 Troubleshooting

### "No database configured"
```bash
rtm config init
```

### "Project not found"
```bash
rtm project list
rtm project switch <project-id>
```

### "Item not found"
Check the item ID with `rtm list` or `rtm search`

---

**Last Updated**: 2025-01-27  
**MVP Version**: 1.0
