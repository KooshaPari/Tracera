# Droid Exec Setup for BMM Workflows

## Overview

BMM CLI uses **droid exec** (Factory's headless CLI) as the main agent provider for workflow execution. Droid exec provides secure-by-default execution with autonomy levels and structured output.

## Installation

1. **Install Droid CLI**:
   ```bash
   curl -fsSL https://app.factory.ai/cli | sh
   ```

2. **Get Factory API Key**:
   - Generate from [Factory Settings Page](https://app.factory.ai/settings)
   - Export as environment variable:
     ```bash
     export FACTORY_API_KEY=fk-...
     ```

3. **Verify Installation**:
   ```bash
   droid exec --help
   ```

## MCP Server Configuration

Droid exec needs the BMM MCP server to be configured. There are a few ways to do this:

### Option 1: Environment Variable (Current Implementation)

The CLI sets `BMM_MCP_SERVER` and `MCP_SERVER_PATH` environment variables:
```bash
export BMM_MCP_SERVER=/path/to/scripts/mcp/bmm_server.py
export MCP_SERVER_PATH=/path/to/scripts/mcp/bmm_server.py
```

### Option 2: Factory Config File

Droid may support MCP servers via config file (check Factory documentation):
```json
{
  "mcpServers": {
    "bmm-workflows": {
      "command": "python",
      "args": ["/path/to/scripts/mcp/bmm_server.py"]
    }
  }
}
```

### Option 3: Instruction-Based (Fallback)

If MCP server isn't auto-discovered, the instruction explicitly references it:
```
Use the run_workflow tool from the BMM MCP server (located at /path/to/bmm_server.py)
```

## Usage Examples

### Basic Workflow Execution

```bash
# Run next workflow (low autonomy - safe file operations)
bmm run

# Run specific workflow with medium autonomy
bmm run prd --auto medium

# Run phase with JSON output
bmm run --phase 0 -o json

# Run with high autonomy (for CI/CD)
bmm run --auto high -o json
```

### Autonomy Levels

- **`--auto low`** (default): File operations, documentation updates
- **`--auto medium`**: Development tasks, package installs, git commits (local)
- **`--auto high`**: Full automation, git push, deployments

### Output Formats

- **`text`** (default): Human-readable output
- **`json`**: Structured JSON for parsing
- **`debug`**: Streaming debug messages

## Architecture with Droid

```
User → bmm CLI → droid exec → MCP Server (bmm_server.py) 
  → FastMCP Client → Sub-agent Server → Workflow Execution
```

### Key Features

1. **Secure by Default**: Droid runs read-only unless `--auto` is specified
2. **Structured Output**: JSON format for automation pipelines
3. **Fail-Fast**: Non-zero exit codes on permission violations
4. **Composable**: Works in shell scripts and CI/CD pipelines

## Integration with Nested Agent Architecture

The nested agent architecture works seamlessly with droid:

1. **Main Agent (droid exec)**: Orchestrates workflow execution
2. **MCP Server**: Provides tools, resources, prompts
3. **FastMCP Client (2nd layer)**: Wraps sub-agent execution with elicitation/sampling
4. **Sub-agent Server**: Executes workflows with full FastMCP features

This provides:
- ✅ Elicitation for user input (via FastMCP Client)
- ✅ Sampling for LLM execution (via FastMCP Client)
- ✅ Middleware for logging (via FastMCP Client)
- ✅ Progress reporting (via FastMCP Client)

All while droid exec handles the main orchestration with its security model.

## Best Practices

1. **Start with `--auto low`**: Safest for initial testing
2. **Use JSON output for automation**: `-o json` for parsing results
3. **Check exit codes**: Non-zero means failure
4. **Use `--cwd` for monorepos**: Scope execution to specific directories
5. **Avoid `--skip-permissions-unsafe`**: Only in isolated environments

## Troubleshooting

### Droid not found
```bash
# Install droid
curl -fsSL https://app.factory.ai/cli | sh

# Verify installation
which droid
```

### MCP tools not available
- Check that `BMM_MCP_SERVER` environment variable is set
- Verify MCP server path is correct
- Check droid config file for MCP server configuration

### Permission errors
- Increase autonomy level: `--auto medium` or `--auto high`
- Check that requested operations match autonomy level
- Review droid's fail-fast error messages
