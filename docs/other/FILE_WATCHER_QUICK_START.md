# File Watcher Quick Start Guide

## What is the File Watcher?

The TraceRTM file watcher automatically monitors your `.trace/` directory for changes and immediately indexes them into the SQLite database. No more manual `rtm index` commands - changes are detected in real-time!

## Quick Start

### 1. Install Dependencies

```bash
pip install watchdog
# or if using the project
pip install -e .
```

### 2. Basic Usage

Navigate to your project directory and run:

```bash
rtm watch
```

That's it! The watcher is now monitoring `.trace/` for changes.

### 3. Create/Edit Files

Edit any file in `.trace/`:

```bash
# Edit an epic
vim .trace/epics/EPIC-001.md

# Create a new story
echo "..." > .trace/stories/STORY-042.md

# Update links
vim .trace/.meta/links.yaml
```

Changes are automatically indexed within 500ms!

### 4. Stop Watching

Press `Ctrl+C` to gracefully stop the watcher.

## Common Use Cases

### Development Workflow

Run the watcher while editing requirements:

```bash
# Terminal 1: Start watcher
rtm watch

# Terminal 2: Edit files
vim .trace/epics/EPIC-001.md
vim .trace/stories/STORY-001.md

# Terminal 3: Query database (sees changes immediately)
rtm list --type epic
rtm search "authentication"
```

### TUI with Auto-Indexing

Launch the TUI with background file watcher:

```bash
rtm tui dashboard --watch
```

Edit `.trace/` files in another terminal, and the TUI will show updated data on refresh!

### Multiple Projects

Watch different projects in separate terminals:

```bash
# Terminal 1
cd ~/projects/project-a
rtm watch

# Terminal 2
cd ~/projects/project-b
rtm watch

# Terminal 3
cd ~/projects/project-c
rtm watch
```

### With Remote Sync

Enable automatic sync queue population:

```bash
rtm watch --auto-sync
```

Changes are automatically queued for remote sync. Push them later with:

```bash
rtm sync push
```

## Command Reference

### Standalone Watcher

```bash
# Basic
rtm watch

# Specific project
rtm watch --path /path/to/project

# Custom debounce (in milliseconds)
rtm watch --debounce 1000

# Enable auto-sync
rtm watch --auto-sync

# Custom refresh rate (in seconds)
rtm watch --refresh 2.0
```

### TUI Integration

```bash
# Basic TUI with watcher
rtm tui dashboard --watch

# Specific project
rtm tui dashboard --watch --path /path/to/project
```

## Statistics Display

The watcher shows live statistics:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File Watcher Statistics     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status            │ 🟢 Running                │
│ Events Processed  │ 42                        │
│ Events Pending    │ 0                         │
│ Last Event        │ 2024-11-30 10:23:45       │
│                   │                           │
│ Changes by Type   │                           │
│   Created         │ 12                        │
│   Modified        │ 28                        │
│   Deleted         │ 2                         │
└───────────────────┴───────────────────────────┘
```

## What Gets Watched?

### ✅ Watched Files

- `.trace/epics/*.md` - Epic markdown files
- `.trace/stories/*.md` - Story markdown files
- `.trace/tests/*.md` - Test markdown files
- `.trace/tasks/*.md` - Task markdown files
- `.trace/.meta/links.yaml` - Traceability links
- `.trace/project.yaml` - Project metadata

### ❌ Ignored Files

- `.trace/.meta/sync.yaml` - Local-only sync state (gitignored)
- Hidden files (except `.trace` and `.meta`)
- Non-markdown/YAML files
- Files outside `.trace/`

## Troubleshooting

### "No .trace/ directory found"

**Solution**: Initialize the project first:

```bash
rtm init
```

### Changes not detected

**Check**:
1. Is the file in `.trace/`? ✓
2. Is it a `.md` or `.yaml` file? ✓
3. Is it `sync.yaml`? (ignored)
4. Is watchdog installed? `pip list | grep watchdog`

### High CPU usage

**Solution**: Increase debounce delay:

```bash
rtm watch --debounce 2000
```

### Database locked errors

**Solution**: Only one process should write to the database at a time. The watcher handles this automatically via SQLite WAL mode.

## Tips & Tricks

### 1. Faster Response

For immediate indexing (at the cost of more CPU):

```bash
rtm watch --debounce 100
```

### 2. Slower, Conservative

For large projects with many rapid changes:

```bash
rtm watch --debounce 2000
```

### 3. Monitor Multiple Projects

Use `tmux` or screen to run multiple watchers:

```bash
tmux new -s project-a
rtm watch --path ~/projects/project-a

# Ctrl+B, C (new window)
rtm watch --path ~/projects/project-b

# Ctrl+B, C (new window)
rtm watch --path ~/projects/project-c
```

### 4. Background Service

Run as a systemd service (Linux):

```bash
sudo systemctl enable tracertm-watcher
sudo systemctl start tracertm-watcher
```

See [FILE_WATCHER_README.md](./src/tracertm/storage/FILE_WATCHER_README.md) for systemd configuration.

### 5. Git Hook Integration

Auto-index after pulling changes:

```bash
# .git/hooks/post-merge
#!/bin/bash
rtm index
```

Or run the watcher continuously during development:

```bash
# Start watcher in background
rtm watch &

# Do your work
git pull
git checkout feature-branch
vim .trace/epics/EPIC-001.md
git commit -am "Update epic"

# Stop watcher when done
fg  # Brings watcher to foreground
Ctrl+C
```

## Next Steps

- **Full Documentation**: See [FILE_WATCHER_README.md](./src/tracertm/storage/FILE_WATCHER_README.md)
- **Architecture Details**: See [FILE_WATCHER_IMPLEMENTATION.md](./FILE_WATCHER_IMPLEMENTATION.md)
- **API Reference**: See Python API in [file_watcher.py](./src/tracertm/storage/file_watcher.py)

## Getting Help

```bash
# Command help
rtm watch --help

# TUI help
rtm tui dashboard --help

# General help
rtm help
```

## Examples

### Example 1: Real-time Development

```bash
# Terminal 1: Watch for changes
cd ~/my-project
rtm watch

# Terminal 2: Edit files
vim .trace/epics/EPIC-001.md
# Save changes → automatically indexed!

# Terminal 3: Query immediately
rtm search "authentication"
# Shows the latest changes from EPIC-001
```

### Example 2: Team Collaboration

```bash
# Alice's machine
cd ~/shared-project
rtm watch --auto-sync

# Alice edits .trace/epics/EPIC-042.md
# → Automatically indexed
# → Queued for sync

# Alice pushes
rtm sync push

# Bob's machine
cd ~/shared-project
rtm sync pull
# → Bob's .trace/ updated
# → Bob's watcher detects changes
# → Bob's database updated
```

### Example 3: Automated Testing

```bash
# Run watcher in background
rtm watch &
WATCHER_PID=$!

# Run tests that modify .trace/
pytest tests/integration/

# Verify indexing
rtm list --type test

# Stop watcher
kill $WATCHER_PID
```

---

**Happy watching! 🎉**

For more advanced usage, see the full documentation in [FILE_WATCHER_README.md](./src/tracertm/storage/FILE_WATCHER_README.md).
