# BMM Workflow Automation

Comprehensive automation script for running BMad Method workflows using `auggie` or `claude` CLI tools.

## Features

- ✅ **Auto-initialization**: Detects and runs workflow-init if needed
- 🔄 **Parallel execution**: Run compatible workflows simultaneously
- 💬 **Live interaction**: Handles user prompts and approvals in real-time
- 📊 **Progress tracking**: Updates workflow status automatically
- 🎯 **Selective execution**: Run specific workflows or entire phases
- 🔌 **Multi-CLI support**: Works with both auggie and claude CLI
- 📦 **Cross-project**: Portable script for any BMM project

## Prerequisites

Install at least one of these CLI tools:

```bash
# Auggie CLI (recommended)
bun add -g @augmentcode/cli

# OR Claude CLI
pip install claude-cli
```

## Installation

```bash
# Make script executable
chmod +x scripts/python/bmm-auto.py

# Optional: Add to PATH
ln -s $(pwd)/scripts/python/bmm-auto.py /usr/local/bin/bmm-auto
```

## Usage

### Initialize Project

```bash
# Run workflow initialization
./scripts/python/bmm-auto.py init

# Or if added to PATH
bmm-auto init
```

### Check Status

```bash
# View current workflow status
bmm-auto status
```

### Run Workflows

```bash
# Run next pending workflow interactively
bmm-auto next

# Run all pending workflows
bmm-auto run

# Run specific workflows
bmm-auto run brainstorm-project research product-brief

# Run entire phase (e.g., Phase 0: Discovery)
bmm-auto run --phase 0

# Run workflows in parallel (where possible)
bmm-auto run --phase 0 --parallel

# Run automatically without user interaction (experimental)
bmm-auto run --auto
```

### Advanced Options

```bash
# Use specific CLI tool
bmm-auto run --cli auggie
bmm-auto run --cli claude

# Run from different project directory
bmm-auto --project-root /path/to/project status

# Enable verbose output
bmm-auto run --verbose
```

## How It Works

### 1. Workflow Detection

The script reads `docs/bmm-workflow-status.yaml` to determine:
- Which workflows are pending
- Which agent to use for each workflow
- Dependencies between workflows

### 2. CLI Integration

**Auggie CLI Mode:**
- Uses `--workspace-root` for context
- Supports `--output-format json` for structured output
- Interactive mode for user prompts

**Claude CLI Mode:**
- Uses `--output-format stream-json` for real-time streaming
- Processes JSON messages as they arrive
- Handles checkpoints and user input dynamically

### 3. Structured Output Protocol

The script instructs agents to output JSON for automation:

```json
{
  "type": "user_input",
  "question": "What's your project called?",
  "options": ["Option A", "Option B"]
}
```

```json
{
  "type": "checkpoint",
  "section": "Requirements",
  "content": "Generated PRD content...",
  "next": "Architecture design"
}
```

```json
{
  "type": "complete",
  "output_file": "docs/PRD.md",
  "summary": "Created comprehensive PRD with 15 FRs and 8 NFRs"
}
```

### 4. Parallel Execution

Workflows are grouped by agent to avoid conflicts:
- Same agent workflows run sequentially
- Different agent workflows run in parallel
- Example: `brainstorm` (analyst) + `research` (analyst) run sequentially,
  but can run parallel to `prd` (pm) if dependencies allow

## Configuration

The script automatically detects:
- Project root (from `.bmad` folder)
- BMM configuration (`.bmad/bmm/config.yaml`)
- Workflow status file (`docs/bmm-workflow-status.yaml`)
- Available CLI tools (auggie/claude)

## Integration with OpenSpec

For projects using OpenSpec, the script can be enhanced:

```python
# Add to bmm-auto.py for OpenSpec integration
def _check_openspec(self):
    """Check if project uses OpenSpec"""
    return (self.project_root / "openspec").exists()

def _sync_with_openspec(self, workflow_id: str, output_file: str):
    """Sync workflow output with OpenSpec"""
    if not self._check_openspec():
        return

    # Copy relevant artifacts to openspec/specs/
    # Update AGENTS.md with workflow context
    # Create change proposals for implementation
```

### OpenSpec Workflow

```bash
# 1. Run BMM planning workflows
bmm-auto run --phase 0 --phase 1 --phase 2

# 2. Sync to OpenSpec
# (Manual or automated via script enhancement)
cp docs/PRD.md openspec/specs/requirements.md
cp docs/architecture.md openspec/specs/architecture.md

# 3. Create implementation proposals
# Use OpenSpec commands: /openspec:proposal, /openspec:apply
```

## Troubleshooting

### "Neither auggie nor claude CLI found"

Install one of the CLI tools:
```bash
bun add -g @augmentcode/cli
# OR
pip install claude-cli
```

### "No workflow status found"

Run initialization first:
```bash
bmm-auto init
```

### Workflows not updating status

Check file permissions:
```bash
ls -la docs/bmm-workflow-status.yaml
chmod 644 docs/bmm-workflow-status.yaml
```

### Agent not found

Ensure BMad is properly installed:
```bash
ls -la .bmad/bmm/agents/
```

## Advanced: Custom Agents

The script supports custom agents defined in `.bmad/custom/agents/`:

```yaml
# .bmad/custom/agents/my-agent.agent.yaml
agent:
  metadata:
    id: my-agent
    name: "My Custom Agent"
    type: expert

  menu:
    - trigger: my-workflow
      workflow: "{project-root}/.bmad/custom/workflows/my-workflow.yaml"
```

Run with:
```bash
bmm-auto run my-workflow
```

## Contributing

To extend the script:

1. **Add new CLI support**: Implement `_run_<cli>_workflow()` method
2. **Add new message types**: Extend `_process_streaming_message()`
3. **Add phase filtering**: Enhance `_parse_workflow_tasks()`
4. **Add OpenSpec integration**: Implement sync methods

## License

Part of the BMad Method framework. See project LICENSE.

## Support

For issues or questions:
- Check BMad documentation: `.bmad/bmm/docs/`
- Review workflow definitions: `.bmad/bmm/workflows/`
- Consult agent configurations: `.bmad/bmm/agents/`
