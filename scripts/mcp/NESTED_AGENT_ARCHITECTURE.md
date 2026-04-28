# Nested Agent Architecture with FastMCP Client Wrapper

## Overview

This architecture implements a **2-layer MCP client system** to provide FastMCP features (elicitation, sampling, middleware) that root clients (auggie/droid) don't support natively.

## Architecture Flow

```
User/CLI
  ↓
Main Agent (droid exec) 
  ↓ [MCP Server configured/attached]
MCP Server (bmm_server.py)
  ↓ [Tool: run_workflow]
FastMCP Client (2nd layer) ← Provides elicitation/sampling/middleware
  ↓ [Connects to]
Sub-agent MCP Server (workflow_executor.py generates temporary server)
  ↓ [Tool: execute_workflow]
Sub-agent Execution (with full FastMCP features)
  ↓
Results flow back through the chain
```

## Key Components

### 1. Main Agent Layer (droid exec)
- **Role**: Root client that orchestrates workflow execution (Factory headless CLI)
- **MCP Server**: `bmm_server.py` configured via environment or config
- **Command**: `droid exec --auto <level> --cwd <path> <instruction>`
- **Capabilities**: Basic MCP protocol, tool calling, resource reading
- **Limitations**: No native support for elicitation, sampling, middleware
- **Autonomy Levels**: `low` (default), `medium`, `high` control what operations are allowed

### 2. MCP Server Layer (bmm_server.py)
- **Role**: Provides tools, resources, and prompts to main agent
- **Key Tool**: `run_workflow(workflow_id, auto)`
- **Function**: When called, triggers sub-agent execution via FastMCP Client

### 3. FastMCP Client Wrapper (workflow_executor.py)
- **Role**: 2nd layer MCP client that provides FastMCP features
- **Features**:
  - ✅ Elicitation for user input
  - ✅ Sampling for LLM execution
  - ✅ Middleware for logging/monitoring
  - ✅ Progress reporting
- **Implementation**: Uses `fastmcp.client.Client` to connect to sub-agent servers

### 4. Sub-agent MCP Server (dynamically generated)
- **Role**: Temporary server for each workflow execution
- **Location**: `.bmad/tmp/workflow_{workflow_id}_server.py`
- **Features**: Full FastMCP capabilities for workflow execution
- **Lifecycle**: Created on-demand, cleaned up after execution

## Data Flow

### Workflow Execution Flow

1. **User invokes CLI**: `bmm run workflow-id`
2. **CLI calls agent**: `auggie --mcp-server python:bmm_server.py --instruction "Use run_workflow tool"`
3. **Main agent calls tool**: `run_workflow(workflow_id="workflow-id", auto=False)`
4. **MCP server tool**:
   - Imports `workflow_executor.run_workflow_with_sub_agent()`
   - Creates `WorkflowExecutor` instance
   - Calls `execute_workflow()`
5. **WorkflowExecutor**:
   - Generates temporary MCP server script
   - Creates FastMCP Client connection to temporary server
   - Invokes `execute_workflow` tool on temporary server
6. **Temporary server**:
   - Uses `ctx.elicit()` for user confirmation (if not auto)
   - Uses `ctx.sample()` for LLM execution with full FastMCP features
   - Uses middleware for logging
   - Reports progress via `ctx.report_progress()`
7. **Results flow back**: Temporary server → FastMCP Client → MCP Server → Main Agent → CLI → User

## Why This Architecture?

### Problem
Root clients (auggie/droid) don't natively support:
- Elicitation (interactive user input)
- Sampling (LLM execution with FastMCP features)
- Middleware (logging, monitoring, intercepting)
- Advanced progress reporting

### Solution
Wrap workflow execution in a **2nd MCP client layer**:
- Main agent uses standard MCP protocol
- Sub-agent execution uses FastMCP Client with full features
- I/O flows through both layers seamlessly

## I/O Handling

### User Input Flow
```
User → CLI → Main Agent → MCP Server Tool → FastMCP Client → Sub-agent Server → ctx.elicit() → User
```

### Progress Reporting Flow
```
Sub-agent Server → ctx.report_progress() → FastMCP Client → MCP Server → Main Agent → CLI → User
```

### Results Flow
```
Sub-agent Server → execute_workflow result → FastMCP Client → MCP Server Tool → Main Agent → CLI → User
```

## Example: Running a Workflow

```bash
# User command
bmm run prd

# 1. CLI detects droid and builds command
droid exec \
    --output-format text \
    --auto low \
    --cwd /path/to/project \
    "Use the run_workflow tool from the BMM MCP server with workflow_id='prd', auto=True"

# 2. Droid calls MCP tool (if MCP server is configured)
run_workflow(workflow_id="prd", auto=True)

# 3. MCP server tool creates sub-agent executor
executor = WorkflowExecutor(project_root, agent_name="bmad-master")
result = await executor.execute_workflow(
    workflow_command="/bmad:bmm:workflows:prd",
    workflow_id="prd",
    auto=True
)

# 4. Executor generates temporary server
# Creates: .bmad/tmp/workflow_prd_server.py

# 5. FastMCP Client connects to temporary server
client = Client(Path(".bmad/tmp/workflow_prd_server.py"))
async with client:
    result = await client.call_tool("execute_workflow", {...})

# 6. Temporary server executes with FastMCP features
# - Uses ctx.elicit() for confirmation (unless auto=True)
# - Uses ctx.sample() for LLM execution
# - Uses middleware for logging
# - Reports progress

# 7. Results flow back through all layers
```

## Benefits

1. **Feature Parity**: Sub-agents get full FastMCP features even when root client doesn't support them
2. **Separation of Concerns**: Main agent orchestrates, sub-agents execute
3. **Flexibility**: Each workflow can have its own execution context
4. **I/O Management**: Proper handling of user input and progress across layers
5. **Middleware Support**: Logging and monitoring at sub-agent level

## Files

- `bmm_server.py`: Main MCP server with tools/resources/prompts
- `workflow_executor.py`: FastMCP Client wrapper for sub-agent execution
- `bmm_cli.py`: CLI that invokes main agent with MCP server attached
- Generated: `.bmad/tmp/workflow_{id}_server.py`: Temporary sub-agent servers

## Future Enhancements

- Cleanup temporary server files after execution
- Reuse server instances for same workflow type
- Add caching layer for workflow results
- Support for parallel sub-agent execution
- Enhanced middleware for distributed tracing
