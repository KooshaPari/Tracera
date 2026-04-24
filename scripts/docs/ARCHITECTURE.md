# BMM Automation Architecture

Technical architecture and design decisions for the BMM workflow automation script.

## Overview

The `bmm-auto.py` script provides a comprehensive automation layer for BMad Method workflows, supporting both interactive and automated execution modes with real-time user interaction.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     bmm-auto.py CLI                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ init command │  │ run command  │  │status command│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │ BMMAutomation   │                        │
│                   │   Orchestrator  │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│    ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼──────┐      │
│    │ Workflow │     │   Agent    │    │  Status    │      │
│    │  Parser  │     │  Executor  │    │  Tracker   │      │
│    └──────────┘     └─────┬──────┘    └────────────┘      │
│                            │                                 │
│              ┌─────────────┴─────────────┐                  │
│              │                           │                  │
│       ┌──────▼──────┐           ┌───────▼────────┐         │
│       │   Auggie    │           │     Claude     │         │
│       │  CLI Runner │           │   CLI Runner   │         │
│       └──────┬──────┘           └───────┬────────┘         │
└──────────────┼──────────────────────────┼──────────────────┘
               │                          │
        ┌──────▼──────┐            ┌──────▼──────┐
        │   Auggie    │            │   Claude    │
        │     CLI     │            │     CLI     │
        └──────┬──────┘            └──────┬──────┘
               │                          │
        ┌──────▼──────────────────────────▼──────┐
        │         BMad Agent System               │
        │  (analyst, pm, architect, tea, etc.)    │
        └──────┬──────────────────────────────────┘
               │
        ┌──────▼──────┐
        │  Workflow   │
        │  Execution  │
        │  (XML/YAML) │
        └─────────────┘
```

## Core Components

### 1. BMMAutomation Class

**Responsibilities:**
- Project initialization detection
- Workflow status management
- CLI tool detection and selection
- Orchestration of workflow execution

**Key Methods:**
- `check_initialization()`: Verify BMM setup
- `run_init()`: Execute workflow-init if needed
- `_parse_workflow_tasks()`: Convert YAML to executable tasks
- `run_workflow_sequence()`: Orchestrate multiple workflows
- `_run_parallel_workflows()`: Execute compatible workflows concurrently

### 2. WorkflowTask Dataclass

**Purpose:** Represents a single executable workflow

**Fields:**
- `id`: Workflow identifier (e.g., "brainstorm-project")
- `agent`: Agent to use (e.g., "analyst", "pm")
- `command`: Full workflow command path
- `status_type`: required/optional/recommended
- `output_path`: Expected output file
- `dependencies`: List of prerequisite workflows
- `status`: Current execution status

### 3. CLI Runners

#### Auggie CLI Runner (`_run_auggie_workflow`)

**Features:**
- Uses `--workspace-root` for context
- Supports `--output-format json` for structured output
- Interactive mode for direct user interaction
- Print mode for automated execution

**Command Structure:**
```bash
auggie --workspace-root /path/to/project \
       --instruction "/bmad:bmm:workflows:prd" \
       --print \
       --output-format json
```

#### Claude CLI Runner (`_run_claude_workflow`)

**Features:**
- Uses `--output-format stream-json` for real-time streaming
- Processes JSON messages as they arrive
- Handles partial messages with `--include-partial-messages`
- Supports structured output validation

**Command Structure:**
```bash
claude --print \
       --output-format stream-json \
       "Execute workflow: /bmad:bmm:workflows:prd"
```

## Structured Output Protocol

The script uses a JSON-based protocol for agent communication:

### Message Types

#### 1. User Input Request
```json
{
  "type": "user_input",
  "question": "What's your project called?",
  "options": ["Option A", "Option B", "Option C"]
}
```

#### 2. Checkpoint/Approval
```json
{
  "type": "checkpoint",
  "section": "Functional Requirements",
  "content": "Generated content here...",
  "next": "Non-Functional Requirements"
}
```

#### 3. Progress Update
```json
{
  "type": "progress",
  "step": "Analyzing architecture",
  "message": "Reviewing system components..."
}
```

#### 4. Completion
```json
{
  "type": "complete",
  "output_file": "docs/PRD.md",
  "summary": "Created PRD with 15 FRs and 8 NFRs"
}
```

## Parallel Execution Strategy

### Agent Grouping

Workflows are grouped by agent to prevent conflicts:

```python
agent_groups = {
    "analyst": [brainstorm, research, product-brief],
    "pm": [prd, validate-prd],
    "architect": [create-architecture, validate-architecture]
}
```

### Execution Model

1. **Same Agent**: Sequential execution (prevents context conflicts)
2. **Different Agents**: Parallel execution (via `asyncio.gather`)
3. **Dependencies**: Respected across all execution modes

### Example Timeline

```
Time →
0s    analyst:brainstorm ────────────────────┐
                                              ├→ Complete
10s   analyst:research ──────────────────────┘

0s    pm:prd ────────────────────────────────┐
                                              ├→ Complete
15s   pm:validate-prd ───────────────────────┘

Total: 15s (parallel) vs 25s (sequential)
```

## State Management

### Workflow Status File

Location: `docs/bmm-workflow-status.yaml`

**Structure:**
```yaml
generated: "2025-11-20"
project: "TraceRTM"
selected_track: "enterprise"
field_type: "greenfield"

workflow_status:
  phase_0_discovery:
    brainstorm-project:
      status: "optional"  # or "docs/brainstorm.md" when complete
      agent: "analyst"
      command: "/bmad:bmm:workflows:brainstorm-project"
```

**Status Transitions:**
```
pending → running → complete (with file path)
                 → failed
                 → skipped (for optional workflows)
```

## Error Handling

### CLI Tool Detection
```python
def _detect_cli_tool(self) -> str:
    if auggie_available:
        return "auggie"
    elif claude_available:
        return "claude"
    else:
        raise RuntimeError("No CLI tool found")
```

### Workflow Execution
- Captures stdout/stderr
- Returns boolean success/failure
- Updates status file on completion
- Logs errors with context

## Extension Points

### 1. Add New CLI Support

```python
async def _run_<cli>_workflow(self, agent, command, interactive, structured):
    # Implement CLI-specific execution
    pass
```

### 2. Add New Message Types

```python
def _process_streaming_message(self, data):
    msg_type = data.get('type')
    if msg_type == 'new_type':
        self._handle_new_type(data)
```

### 3. Add OpenSpec Integration

```python
def _sync_with_openspec(self, workflow_id, output_file):
    # Copy artifacts to openspec/specs/
    # Update AGENTS.md
    # Create change proposals
```

## Performance Considerations

### Async/Await Usage
- All workflow execution is async
- Enables true parallel execution
- Non-blocking I/O for streaming

### Memory Management
- Streaming JSON prevents large memory buffers
- Workflow status loaded/saved incrementally
- Agent processes isolated

### Optimization Opportunities
1. **Caching**: Cache agent configurations
2. **Batching**: Batch status file updates
3. **Streaming**: Use streaming for large outputs
4. **Concurrency**: Increase parallel workflow limit

## Security Considerations

1. **Path Validation**: All paths validated against project root
2. **Command Injection**: Commands built programmatically, not from user strings
3. **File Permissions**: Status file permissions checked before write
4. **Agent Isolation**: Each agent runs in isolated process

## Testing Strategy

### Unit Tests
- Workflow parsing
- Status file management
- Message processing
- CLI command building

### Integration Tests
- End-to-end workflow execution
- Parallel execution correctness
- Status file updates
- Error handling

### Manual Testing
```bash
# Test initialization
python3 scripts/bmm-auto.py init

# Test status display
python3 scripts/bmm-auto.py status

# Test single workflow
python3 scripts/bmm-auto.py run brainstorm-project

# Test parallel execution
python3 scripts/bmm-auto.py run --phase 0 --parallel
```

## Future Enhancements

1. **Web UI**: Real-time dashboard for workflow progress
2. **Notifications**: Slack/email notifications on completion
3. **Rollback**: Undo completed workflows
4. **Templates**: Workflow templates for common patterns
5. **Analytics**: Track workflow execution times and success rates
6. **CI/CD Integration**: GitHub Actions/GitLab CI support
7. **Multi-Project**: Manage multiple BMM projects
8. **Cloud Execution**: Run workflows on remote agents

