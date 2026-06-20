# Interactive Wizard Examples

## Quick Start

### Create Your First Project

The easiest way to get started with TraceRTM is using the interactive wizard:

```bash
rtm project init-interactive
```

This will guide you through:
1. Choosing a project name
2. Writing a description
3. Enabling integrations (GitHub, Jira)
4. Selecting views (FEATURE, CODE, TEST, etc.)

**Example Session**:
```
🚀 Create New TraceRTM Project

Step 1/5: name
Project name: my-first-project

Step 2/5: description
Project description: Learning TraceRTM basics

Step 3/5: enable_github
Enable GitHub integration? [y/n]: n

Step 4/5: enable_jira
Enable Jira integration? [y/n]: n

Step 5/5: views
Views to enable (comma-separated) [FEATURE,CODE,TEST]:

┌─ Configuration Summary ────────────────────────────┐
│ Project Configuration                              │
│                                                    │
│ Name: my-first-project                            │
│ Description: Learning TraceRTM basics             │
│ GitHub: Disabled                                  │
│ Jira: Disabled                                    │
│ Views: FEATURE, CODE, TEST                        │
└────────────────────────────────────────────────────┘

Proceed with project creation? [Y/n]: y

Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 5/5

┌─ Success ───────────────────────────────────────────┐
│ ✓ Project 'my-first-project' created successfully! │
│                                                     │
│ Project ID: abc12345                               │
│ Database: ~/.tracertm/tracertm.db                  │
│ Project Directory: ~/.tracertm/projects/my-first...│
│                                                     │
│ Enabled Views:                                     │
│   • FEATURE                                        │
│   • CODE                                           │
│   • TEST                                           │
└─────────────────────────────────────────────────────┘
```

---

## Common Workflows

### 1. Create Project with GitHub Integration

```bash
rtm project init-interactive
```

**Answers**:
- Project name: `web-app-tracker`
- Description: `Requirements for web application`
- Enable GitHub? `y`
- Enable Jira? `n`
- Views: `FEATURE,CODE,TEST,DESIGN,DOCUMENTATION`

**After creation**:
```bash
rtm github setup
# Follow GitHub setup wizard
```

---

### 2. Import Existing Project

If you have a backup file or exported project:

```bash
rtm project import-interactive
```

**Steps**:
1. Provide file path: `backups/project-2026-01-31.json`
2. Review preview (items/links count)
3. Choose project name (or keep existing)
4. Decide on markdown files (recommended: yes)

**Example**:
```
📥 Import TraceRTM Project

Step 1/3: import_file
Import file path: backups/production-backup.json
✓ Valid project file found
  Project: production-app
  Items: 256, Links: 145

Step 2/3: project_name
Project name [production-app]:

Step 3/3: create_markdown
Create markdown files for imported items? [Y/n]: y

Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 5/5

✓ Project 'production-app' imported successfully!
  Items Imported: 256
  Links Imported: 145
```

---

### 3. Clone Project for Staging

When you need a copy of a project (e.g., production → staging):

```bash
rtm project clone-interactive
```

**Steps**:
1. Select source from list (by number or name)
2. Choose target name
3. Include items (yes for full copy)
4. Include links (yes to preserve relationships)
5. Clone markdown (yes to get local files)

**Example**:
```
📋 Clone TraceRTM Project

Available projects:
  1. production-app (256 items)
  2. demo-app (42 items)

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

Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 5/5

✓ Project cloned successfully!
  Source: production-app
  Target: staging-app
```

---

## Advanced Examples

### Create Project with Multiple Views

For comprehensive tracking across development lifecycle:

```bash
rtm project init-interactive
```

**Configuration**:
- Name: `full-stack-app`
- Description: `Full stack application with UX and architecture tracking`
- GitHub: `y`
- Jira: `y`
- Views: `FEATURE,CODE,TEST,DESIGN,PERSONA,USER_JOURNEY,ARCHITECTURE,API_SPEC`

This creates a project ready for:
- Product features
- Source code tracking
- Test management
- Design specifications
- User personas
- User journey mapping
- Architecture decisions
- API documentation

---

### Import with Custom Project Name

Restore a backup with a new name:

```bash
rtm project import-interactive
```

**Settings**:
- File: `production-2026-01-31.json`
- Name: `production-restored-2026-01-31` (different from file)
- Markdown: `y`

**Use case**: Keep historical backups separate from active project.

---

### Clone Structure Only

Create a template from an existing project:

```bash
rtm project clone-interactive
```

**Settings**:
- Source: `template-project`
- Target: `new-client-project`
- Include items: `n` (structure only)
- Include links: `n`
- Clone markdown: `y` (for directory structure)

**Result**: Empty project with same view configuration.

---

## Error Recovery Examples

### Duplicate Project Name

**Scenario**: You try to create a project that already exists.

```
Project name: my-project
[red]Project 'my-project' already exists[/red]
Project name: my-project-v2
```

**Solution**: Choose a different name or delete the existing project first.

---

### Invalid Import File

**Scenario**: File doesn't exist or wrong format.

```
Import file path: backup.txt
[red]File must be .json or .yaml format[/red]
Import file path: backup.json
```

**Solution**: Provide correct file path and format.

---

### Source Project Not Found

**Scenario**: Trying to clone non-existent project.

```
Select source project (name or number): missing-project
[red]Invalid selection: missing-project[/red]
Select source project (name or number): 1
```

**Solution**: Select from the numbered list or use exact project name.

---

## Cancellation Examples

You can cancel any wizard at any step:

### Cancel During Name Entry
```
Project name: ^C
[yellow]Project creation cancelled[/yellow]
```

### Cancel After Preview
```
┌─ Configuration Summary ─────────────────────┐
│ ...                                         │
└─────────────────────────────────────────────┘

Proceed with project creation? [Y/n]: n
[yellow]Project creation cancelled[/yellow]
```

No changes are made until you confirm!

---

## Best Practices

### DO ✅

**Start with interactive wizards**
```bash
# Good for beginners
rtm project init-interactive
```

**Enable markdown files**
```
Create markdown files? [Y/n]: y
```
Enables git tracking and local backups.

**Preview before proceeding**
```
Review the summary
Confirm before creation
```

**Use descriptive names**
```
Project name: customer-portal-requirements
Project name: mobile-app-v2-specs
```

### DON'T ❌

**Don't use in scripts**
```bash
# Bad: wizards are interactive
./deploy.sh
  rtm project init-interactive  # This will hang!
```
Use non-interactive commands for automation.

**Don't skip markdown**
```
Create markdown files? [Y/n]: n  # ❌
```
You lose local storage and git integration.

**Don't use generic names**
```
Project name: project  # ❌ Too generic
Project name: test     # ❌ Conflicts likely
```

---

## Troubleshooting

### Wizard Won't Start

**Check command exists**:
```bash
rtm project --help | grep interactive
```

Should show:
- `init-interactive`
- `import-interactive`
- `clone-interactive`

### Keyboard Issues

**Ctrl+C doesn't work**:
- Try Ctrl+D
- Press Ctrl+C twice quickly
- Check terminal emulator

### Input Not Accepted

**Empty input rejected**:
```
Project name:
[red]Project name cannot be empty[/red]
```
Provide a value.

**Invalid characters**:
```
Project name: my project!
[red]Invalid characters in project name[/red]
```
Use letters, numbers, hyphens, underscores only.

---

## Quick Reference

| Wizard | Command | Use When |
|--------|---------|----------|
| **Init** | `rtm project init-interactive` | Creating new project |
| **Import** | `rtm project import-interactive` | Restoring from backup |
| **Clone** | `rtm project clone-interactive` | Copying existing project |

| Feature | Available |
|---------|-----------|
| Input validation | ✅ All wizards |
| Progress tracking | ✅ All wizards |
| Cancellation | ✅ All wizards |
| Preview | ✅ All wizards |
| Error recovery | ✅ All wizards |

---

## Next Steps

After creating your first project:

1. **Add items**:
   ```bash
   rtm item create --type feature --title "User login"
   ```

2. **List items**:
   ```bash
   rtm item list
   ```

3. **View graph**:
   ```bash
   rtm graph view
   ```

4. **Set up integrations** (if enabled):
   ```bash
   rtm github setup
   rtm jira setup
   ```

5. **Export for backup**:
   ```bash
   rtm project export my-project --output backup.json
   ```

---

## Related Guides

- [Interactive Wizards User Guide](../INTERACTIVE_WIZARDS_GUIDE.md)
- [Project Commands Reference](../../reference/PROJECT_COMMANDS.md)
- [Getting Started](../../01-getting-started/README.md)
- [CLI Guide](../CLI_GUIDE.md)

---

**Last Updated**: 2026-01-31
