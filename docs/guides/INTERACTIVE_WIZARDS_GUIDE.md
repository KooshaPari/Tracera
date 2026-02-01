# Interactive Wizards User Guide

## Overview

TraceRTM CLI provides interactive wizards for complex project operations. These wizards guide you step-by-step through configuration and setup, making it easier to perform complex tasks without memorizing command-line options.

## Available Wizards

### 1. Project Initialization Wizard

**Command**: `rtm project init-interactive`

**What it does**: Creates a new TraceRTM project with guided configuration.

**When to use**:
- First time creating a project
- Want to enable GitHub/Jira integrations
- Need to select specific views
- Prefer guided setup over command-line flags

**Example**:
```bash
$ rtm project init-interactive

🚀 Create New TraceRTM Project

Step 1/5: name
Project name: my-app

Step 2/5: description
Project description: Mobile app requirements tracking

Step 3/5: enable_github
Enable GitHub integration? [y/n]: y

Step 4/5: enable_jira
Enable Jira integration? [y/n]: n

Step 5/5: views
Views to enable (comma-separated) [FEATURE,CODE,TEST]:
```

**Tips**:
- Press Enter to accept defaults (shown in brackets)
- Use Ctrl+C at any time to cancel
- Integration config files are created but require setup
- View directories are created automatically

---

### 2. Project Import Wizard

**Command**: `rtm project import-interactive`

**What it does**: Imports a project from a backup file (JSON or YAML).

**When to use**:
- Restoring from backup
- Migrating projects between environments
- Unsure about import file format
- Want to preview before importing

**Example**:
```bash
$ rtm project import-interactive

📥 Import TraceRTM Project

Step 1/3: import_file
Import file path: backups/project-backup.json
✓ Valid project file found
  Project: production-app
  Items: 156, Links: 89

Step 2/3: project_name
Project name [production-app]: staging-app

Step 3/3: create_markdown
Create markdown files for imported items? [Y/n]: y
```

**Tips**:
- File path can be absolute or relative
- Preview shows item/link counts before import
- Can rename project during import
- Markdown creation is recommended for local storage

---

### 3. Project Clone Wizard

**Command**: `rtm project clone-interactive`

**What it does**: Creates a copy of an existing project.

**When to use**:
- Creating project templates
- Setting up staging/test environments
- Duplicating project structure
- Want to selectively copy items/links

**Example**:
```bash
$ rtm project clone-interactive

📋 Clone TraceRTM Project

Available projects:
  1. production-app (156 items)
  2. template-project (0 items)
  3. demo-project (42 items)

Step 1/5: source_project
Select source project (name or number): 1

Step 2/5: target_name
Target project name [production-app-copy]: staging-app

Step 3/5: include_items
Include items? [Y/n]: y

Step 4/5: include_links
Include links? [Y/n]: y

Step 5/5: clone_markdown
Clone markdown files? [Y/n]: y
```

**Tips**:
- Select by number (1, 2, 3) or name
- Item count helps identify the right project
- Can clone structure without items
- Markdown files preserve local history

---

## Common Patterns

### Creating a New Project

**Recommended approach**:
```bash
rtm project init-interactive
```

Then follow the prompts. For GitHub integration:
```bash
rtm github setup
```

For Jira integration:
```bash
rtm jira setup
```

### Backing Up and Restoring

**Backup**:
```bash
rtm project export my-project --output backup.json --include-markdown
```

**Restore**:
```bash
rtm project import-interactive
# When prompted, provide backup.json path
```

### Creating Environment Copies

**From production to staging**:
```bash
rtm project clone-interactive
# Select production project
# Name it staging-app
# Include items and links
```

### Creating Templates

**Create template**:
```bash
rtm project init-interactive
# Set up structure, no items

rtm project template create my-template --template empty-project
```

**Use template**:
```bash
rtm project template use empty-project --name new-project
```

---

## Wizard Features

### Input Validation

All wizards validate inputs:
- **Project names**: Checked for uniqueness
- **File paths**: Verified for existence and format
- **Views**: Validated against available options
- **Selections**: Range-checked for lists

### Progress Tracking

Complex operations show progress:
```
Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 3/5
```

### Confirmation Summaries

Before executing, wizards show what will happen:
```
┌─ Configuration Summary ─────────────────────┐
│ Project Configuration                       │
│                                             │
│ Name: my-project                           │
│ Description: My awesome project            │
│ GitHub: Enabled                            │
│ Jira: Disabled                             │
│ Views: FEATURE, CODE, TEST                 │
└─────────────────────────────────────────────┘

Proceed with project creation? [Y/n]:
```

### Error Handling

Clear error messages with recovery:
```
[red]Project 'my-project' already exists[/red]
Project name: my-project-v2
```

---

## Keyboard Shortcuts

- **Enter** - Accept default value
- **Ctrl+C** - Cancel wizard (graceful exit)
- **Ctrl+D** - EOF (treated as cancel)

---

## Comparison: Interactive vs Non-Interactive

| Feature | Interactive | Non-Interactive |
|---------|-------------|-----------------|
| **Learning curve** | Low | Medium |
| **Setup time** | Slower | Faster (if you know options) |
| **Error prevention** | High | Medium |
| **Automation** | Not suitable | Excellent |
| **Discovery** | Excellent | Poor |
| **Scripting** | Not possible | Easy |

**Use interactive when**:
- Learning the system
- Configuring complex projects
- Unsure of available options
- Want validation and previews

**Use non-interactive when**:
- Automating workflows
- CI/CD pipelines
- Scripting batch operations
- Know exact options needed

---

## Troubleshooting

### Wizard doesn't start
```bash
# Check if command exists
rtm project --help

# Should show init-interactive, import-interactive, clone-interactive
```

### Ctrl+C doesn't work
- Try Ctrl+D (EOF)
- Press Ctrl+C twice in quick succession
- Terminal emulator issue - try different terminal

### Invalid file format errors
```bash
# Check file extension
file backup.json

# Verify file contents
head -n 10 backup.json
```

### Project already exists
- Use different name
- Delete existing project first: `rtm project delete <name>`
- Or merge during import (wizard will ask)

---

## Examples

### Complete New Project Setup

```bash
# Start wizard
$ rtm project init-interactive

# Follow prompts:
Project name: customer-portal
Project description: Customer facing portal for orders
Enable GitHub integration? [y/n]: y
Enable Jira integration? [y/n]: y
Views to enable: FEATURE,CODE,TEST,DESIGN,DOCUMENTATION

# After creation, configure integrations
$ rtm github setup
$ rtm jira setup

# Start working
$ rtm item create --type feature --title "User login"
```

### Import and Restore

```bash
# Import from backup
$ rtm project import-interactive

Import file path: backups/2026-01-31-production.json
✓ Valid project file found
  Project: production-app
  Items: 256, Links: 145

Project name [production-app]: production-restored
Create markdown files? [Y/n]: y

# Verify import
$ rtm project list
$ rtm item list
```

### Clone to Staging

```bash
# Clone production to staging
$ rtm project clone-interactive

Available projects:
  1. production-app (256 items)
  2. demo-app (42 items)

Select source project: 1
Target project name: staging-app
Include items? [Y/n]: y
Include links? [Y/n]: y
Clone markdown files? [Y/n]: y

# Switch to staging
$ rtm project switch staging-app
```

---

## Advanced Usage

### Custom View Configuration

When creating a project, specify custom views:
```
Views to enable: FEATURE,CODE,TEST,PERSONA,USER_JOURNEY,ARCHITECTURE
```

Available views:
- Core: FEATURE, CODE, TEST, REQUIREMENT, DESIGN, DOCUMENTATION
- UX: PERSONA, USER_JOURNEY, USER_FLOW
- Technical: ARCHITECTURE, SEQUENCE, STATE_MACHINE
- Quality: TEST_RESULTS, COVERAGE_REPORT, SECURITY_SCAN

### Selective Import

Import only specific items by editing the JSON/YAML before import:
```json
{
  "project": {...},
  "items": [
    // Remove items you don't want
  ],
  "links": [...]
}
```

### Template-based Workflow

1. Create template project with structure
2. Export as template
3. Import template for new projects
4. Customize each instance

```bash
# Create template
rtm project init-interactive
# Name: web-app-template
# Add structure, no content

# Export template
rtm project template create web-app-template --template webapp

# Use template
rtm project template use webapp --name new-web-app
```

---

## Best Practices

### DO
- ✅ Use interactive wizards when learning
- ✅ Enable markdown for git tracking
- ✅ Configure integrations after project creation
- ✅ Review configuration summary before proceeding
- ✅ Test in staging before production

### DON'T
- ❌ Use in automated scripts (use non-interactive)
- ❌ Skip markdown creation (lose local history)
- ❌ Ignore validation errors
- ❌ Clone large projects without review
- ❌ Import untrusted backup files

---

## Getting Help

### Command Help
```bash
rtm project init-interactive --help
rtm project import-interactive --help
rtm project clone-interactive --help
```

### List Available Options
```bash
rtm project --help          # See all project commands
rtm --help                  # See all CLI commands
```

### Verbose Output
```bash
# Set log level for debugging
export TRACERTM_LOG_LEVEL=DEBUG
rtm project init-interactive
```

---

## Related Documentation

- [Project Commands Reference](../reference/PROJECT_COMMANDS.md)
- [Non-Interactive CLI Guide](./CLI_GUIDE.md)
- [Integration Setup](./INTEGRATION_SETUP.md)
- [Backup and Restore](./BACKUP_RESTORE.md)

---

**Last Updated**: 2026-01-31
**Version**: 1.0.0
