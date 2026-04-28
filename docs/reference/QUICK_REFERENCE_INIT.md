# TraceRTM Init Commands - Quick Reference

## Commands Overview

| Command | Purpose | Common Usage |
|---------|---------|--------------|
| `rtm init` | Create new .trace/ structure | `rtm init --name myproject` |
| `rtm register` | Register existing .trace/ | `rtm register` |
| `rtm index` | Re-index .trace/ into DB | `rtm index` |
| `rtm project list` | List all projects | `rtm project list` |

## Quick Start

### New Project
```bash
# 1. Create and initialize
mkdir myproject && cd myproject
rtm init --name myproject

# 2. Create first epic
rtm create epic "User Authentication"

# 3. List items
rtm list
```

### Clone Existing
```bash
# 1. Clone repo
git clone https://github.com/user/project.git
cd project

# 2. Register
rtm register

# 3. List items
rtm list
```

## Command Details

### `rtm init`
```bash
rtm init [--name NAME] [--path PATH] [--description DESC]
```

**Examples:**
```bash
rtm init                                          # Use directory name
rtm init --name myproject                         # Custom name
rtm init --path /path/to/project                  # Custom path
rtm init --name myproject --description "My app"  # With description
```

**Creates:**
- `.trace/project.yaml` - Project metadata
- `.trace/epics/` - Epic markdown files
- `.trace/stories/` - Story markdown files
- `.trace/tests/` - Test markdown files
- `.trace/tasks/` - Task markdown files
- `.trace/docs/` - Documentation
- `.trace/.meta/links.yaml` - Traceability links
- `.trace/.meta/agents.yaml` - Agent config
- `.trace/.meta/sync.yaml` - Sync state (gitignored)

### `rtm register`
```bash
rtm register [--path PATH]
```

**Examples:**
```bash
rtm register                    # Current directory
rtm register --path /path/to/project
```

**Does:**
- Reads `project.yaml`
- Registers in global DB
- Indexes all markdown files
- Sets as current project

### `rtm index`
```bash
rtm index [--path PATH] [--full]
```

**Examples:**
```bash
rtm index              # Incremental (default)
rtm index --full       # Full re-index
rtm index --path /path/to/project
```

**Modes:**
- **Incremental**: Only changed files
- **Full**: All files

### `rtm project list`
```bash
rtm project list [--sync-status] [--paths/--no-paths]
```

**Examples:**
```bash
rtm project list                # All projects with paths
rtm project list --no-paths     # Hide paths
rtm project list --sync-status  # Show sync status
```

**Shows:**
- Project ID
- Name
- Description
- Local .trace/ path
- Item count
- Last indexed time

## Directory Structure

```
.trace/
├── project.yaml              # name, counters, settings
├── epics/
│   └── EPIC-001.md
├── stories/
│   └── STORY-001.md
├── tests/
│   └── TEST-001.md
├── tasks/
│   └── TASK-001.md
├── docs/
│   └── architecture.md
└── .meta/
    ├── links.yaml            # Traceability matrix
    ├── agents.yaml           # Agent config
    └── sync.yaml             # Sync state (gitignored)
```

## Workflow Patterns

### Daily Development
```bash
# Morning: Pull changes
git pull
rtm index

# Work: Create/edit items
rtm create story "New feature"
# Edit .trace/stories/STORY-001.md

# Evening: Commit
rtm index
git add .trace/
git commit -m "Updated requirements"
git push
```

### Team Collaboration
```bash
# Team member A
rtm create epic "Payment System"
git commit -am "Add payment epic"
git push

# Team member B
git pull
rtm index  # Auto-indexes new epic
rtm list   # See new epic
```

### LLM Agent Integration
```python
# Agent reads requirements
with open(".trace/epics/EPIC-001.md") as f:
    requirements = f.read()

# Agent creates task
with open(".trace/tasks/TASK-001.md", "w") as f:
    f.write(task_markdown)

# Re-index to pick up changes
subprocess.run(["rtm", "index"])
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "No .trace/ directory found" | Run `rtm init` first |
| ".trace/ already exists" | Use `rtm register` instead |
| "Project not found" | Run `rtm register` before `rtm index` |
| Items not showing | Check frontmatter, run `rtm index --full` |

## Tips

1. **Always commit .trace/ to git**
   ```bash
   git add .trace/
   git commit -m "Requirements update"
   ```

2. **Use pre-commit hooks**
   ```bash
   echo "rtm index" > .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

3. **Gitignore sync.yaml only**
   ```gitignore
   .trace/.meta/sync.yaml
   ```

4. **Re-index after manual edits**
   ```bash
   vim .trace/epics/EPIC-001.md
   rtm index
   ```

5. **Full re-index if issues**
   ```bash
   rtm index --full
   ```

## See Also

- [CLI_INIT_COMMANDS.md](CLI_INIT_COMMANDS.md) - Complete documentation
- [PROJECT_LOCAL_STORAGE.md](PROJECT_LOCAL_STORAGE.md) - Architecture
- [CLI_REFERENCE.md](CLI_REFERENCE.md) - All CLI commands
