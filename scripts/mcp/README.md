# BMM MCP Server & CLI

Modern BMad Method workflow automation using **FastMCP 3.0.0b1** with beautiful Typer + Rich CLI.

## 🌟 Features

### MCP Server (`bmm_server.py`)
- ✅ **Tools**: init_project, run_workflow, run_phase, get_status
- ✅ **Resources**: workflow-status, project-config, next-workflow, progress-summary
- ✅ **Prompts**: workflow_execution_prompt, phase_planning_prompt, project_overview_prompt
- ✅ **Elicitation**: Built-in user prompting (no custom JSON protocol needed)
- ✅ **Sampling**: Server can invoke LLMs for workflow execution
- ✅ **Progress Reporting**: Real-time progress updates
- ✅ **Middleware**: Logging and monitoring
- ✅ **Icons**: Beautiful tool icons (NEW in 2.13, supported in 3.0.0b1)
- ✅ **Storage Backends**: Pluggable storage (file-based by default)

### CLI (`bmm_cli.py`)
- ✅ **Beautiful UI**: Rich tables, panels, progress bars
- ✅ **Interactive**: Typer-powered commands
- ✅ **MCP Client**: Connects to BMM MCP server
- ✅ **Commands**: init, status, run, next, resources, read, prompts, tools, config, server

## 📦 Installation

```bash
# Install dependencies
pip install fastmcp==3.0.0b1 mcp==1.25.0 typer rich pyyaml

# Make scripts executable
chmod +x scripts/mcp/bmm_server.py
chmod +x scripts/mcp/bmm_cli.py

# Optional: Add to PATH
ln -s $(pwd)/scripts/mcp/bmm_cli.py /usr/local/bin/bmm
```

## 🚀 Quick Start

### Installation

```bash
# One-command install
./scripts/mcp/quick_install.sh
```

### Usage

```bash
# Check status (TESTED ✅)
python scripts/mcp/bmm_cli.py status

# Or use wrapper
./scripts/mcp/run_bmm.sh status

# Initialize project
python scripts/mcp/bmm_cli.py init

# Run next workflow
python scripts/mcp/bmm_cli.py next

# Run specific workflow
python scripts/mcp/bmm_cli.py run prd

# Run entire phase
python scripts/mcp/bmm_cli.py run --phase 0

# Run phase in parallel
python scripts/mcp/bmm_cli.py run --phase 0 --parallel
```

## 🔧 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize BMM project | `bmm init` |
| `status` | Show workflow status | `bmm status` |
| `run` | Run workflows | `bmm run prd` |
| `next` | Run next workflow | `bmm next` |
| `resources` | List MCP resources | `bmm resources` |
| `read` | Read MCP resource | `bmm read bmm://workflow-status` |
| `prompts` | List MCP prompts | `bmm prompts` |
| `tools` | List MCP tools | `bmm tools` |
| `config` | Show configuration | `bmm config` |
| `server` | Start MCP server | `bmm server` |

## 🎯 MCP Server Usage

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bmm-workflows": {
      "command": "python3",
      "args": ["/path/to/trace/scripts/mcp/bmm_server.py"]
    }
  }
}
```

### With Custom MCP Client

```python
from fastmcp.client import FastMCPClient

client = FastMCPClient(
    server_script="scripts/mcp/bmm_server.py",
    transport="stdio"
)

# Call tools
result = await client.call_tool("init_project", {})

# Read resources
status = await client.read_resource("bmm://workflow-status")

# Get prompts
prompt = await client.get_prompt("workflow_execution_prompt", {"workflow_id": "prd"})
```

### With SSE Transport (Remote Access)

```bash
# Start server with SSE
python scripts/mcp/bmm_server.py --transport sse --host 0.0.0.0 --port 8000

# Connect from client
client = FastMCPClient(
    server_url="http://localhost:8000",
    transport="sse"
)
```

## 📚 MCP Resources

| URI | Description |
|-----|-------------|
| `bmm://workflow-status` | Current workflow status (YAML) |
| `bmm://project-config` | BMM configuration |
| `bmm://next-workflow` | Next pending workflow |
| `bmm://progress-summary` | Human-readable progress |

## 🔨 MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `init_project` | Initialize BMM project | None (uses elicitation) |
| `run_workflow` | Execute specific workflow | `workflow_id`, `auto` |
| `run_phase` | Execute entire phase | `phase`, `parallel`, `auto` |
| `get_status` | Get workflow status | None |

## 💬 MCP Prompts

| Prompt | Description | Parameters |
|--------|-------------|------------|
| `workflow_execution_prompt` | Prompt for workflow execution | `workflow_id` |
| `phase_planning_prompt` | Prompt for phase planning | `phase` |
| `project_overview_prompt` | Prompt for project overview | None |

## 🎨 Features Showcase

### Elicitation (User Input)

```python
@mcp.tool()
async def init_project(ctx: Context) -> str:
    # Built-in user prompting
    project_name = await ctx.elicit("Project name?")
    track = await ctx.elicit(
        "Select track:",
        options=["quick-flow", "method", "enterprise"]
    )
    return f"Initialized {project_name}"
```

### Sampling (LLM Calls)

```python
@mcp.tool()
async def run_workflow(ctx: Context, workflow_id: str) -> str:
    # Server invokes LLM
    result = await ctx.sample(
        messages=[{"role": "user", "content": f"Execute {workflow_id}"}],
        system_prompt="You are the analyst agent",
        model_preferences={"hints": [{"name": "claude-sonnet-4.5"}]}
    )
    return result.content
```

### Progress Reporting

```python
@mcp.tool()
async def run_phase(ctx: Context, phase: int) -> str:
    await ctx.report_progress(0, 100, "Starting...")
    # ... work ...
    await ctx.report_progress(50, 100, "Halfway...")
    # ... more work ...
    await ctx.report_progress(100, 100, "Complete!")
```

### Middleware

```python
class LoggingMiddleware(Middleware):
    async def on_tool_call(self, ctx: MiddlewareContext, tool_name: str, arguments: Dict):
        print(f"[TOOL] {tool_name} called")
        await ctx.next()

mcp.add_middleware(LoggingMiddleware())
```

## 🔄 Comparison: Old vs New

| Feature | Old (bmm-auto.py) | New (MCP Server) |
|---------|-------------------|------------------|
| User Input | Custom JSON protocol | Built-in elicitation ✅ |
| LLM Calls | Shell out to CLI | Built-in sampling ✅ |
| State Exposure | Manual file reading | MCP resources ✅ |
| Prompt Templates | Hardcoded strings | MCP prompts ✅ |
| Client Support | auggie/claude only | Any MCP client ✅ |
| Standard Protocol | ❌ Custom | ✅ MCP standard |
| CLI Beauty | Basic argparse | ✅ Typer + Rich |
| Progress | Manual print | ✅ ctx.report_progress() |
| Icons | ❌ None | ✅ Tool icons |
| Middleware | ❌ None | ✅ Logging, auth, etc. |

## 🚀 Advanced Usage

### With Factory Models (localhost:8317)

The server can use your factory models for sampling:

```python
result = await ctx.sample(
    messages=[...],
    model_preferences={
        "hints": [{"name": "gpt-5.1-codex"}]  # Use factory model
    }
)
```

### With Authentication (NEW in 2.13, supported in 3.0.0b1)

```python
from fastmcp.auth import BearerAuth

mcp = FastMCP("bmm-workflows", auth=BearerAuth(token="your-token"))
```

### With Storage Backend (NEW in 2.13, supported in 3.0.0b1)

```python
from fastmcp.storage import RedisStorage

mcp.set_storage(RedisStorage(url="redis://localhost:6379"))
```

## 📖 Documentation

- **DESIGN.md**: Architecture and design decisions
- **README.md**: This file
- **FastMCP Docs**: https://gofastmcp.com/

## 🎯 Next Steps

1. ✅ Test MCP server with Claude Desktop
2. ✅ Test CLI commands
3. ✅ Add authentication for remote access
4. ✅ Add Redis storage backend
5. ✅ Create GitHub Action for CI/CD
6. ✅ Add more middleware (rate limiting, caching)
7. ✅ Integrate with factory models

## 🤝 Contributing

See main project CONTRIBUTING.md

## 📄 License

Part of the BMad Method framework. See project LICENSE.
