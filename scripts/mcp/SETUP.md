# BMM MCP Server - Setup Guide

Complete setup guide for the BMM MCP server and CLI.

## Prerequisites

### 1. Python 3.8+

```bash
python3 --version  # Should be 3.8 or higher
```

### 2. Install Dependencies

```bash
# Core dependencies (already installed)
pip install fastmcp==3.0.0b1 mcp==1.25.0  # ✅ Already installed
pip install typer rich pyyaml

# Optional: For Redis storage backend
pip install redis

# Optional: For authentication
pip install python-jose[cryptography]
```

### 3. Verify FastMCP Installation

```bash
python3 -c "import fastmcp; print(fastmcp.__version__)"
# Should output: 3.0.0b1 or higher
```

## Installation

### Quick Install (Recommended)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Run installation script
./scripts/mcp/install.sh
```

This will:
- ✅ Check Python version
- ✅ Install all dependencies from requirements.txt
- ✅ Make scripts executable
- ✅ Test installation
- ✅ Optionally create `bmm` alias

### Manual Install

If you prefer manual installation:

#### Step 1: Install Dependencies

```bash
pip3 install -r scripts/mcp/requirements.txt
```

#### Step 2: Make Scripts Executable

```bash
chmod +x scripts/mcp/bmm_server.py
chmod +x scripts/mcp/bmm_cli.py
```

### Step 2: Test MCP Server

```bash
# Test server starts without errors
python3 scripts/mcp/bmm_server.py &
SERVER_PID=$!

# Wait a moment
sleep 2

# Kill test server
kill $SERVER_PID

echo "✅ Server test passed"
```

### Step 3: Test CLI

```bash
# Test CLI help
python3 scripts/mcp/bmm_cli.py --help

# Should show beautiful Typer help with all commands
```

### Step 4: Create Alias (Optional)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias bmm='python3 /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/mcp/bmm_cli.py'
```

Then:

```bash
source ~/.zshrc  # or ~/.bashrc
bmm --help
```

## Configuration

### For Claude Desktop

1. **Locate config file:**
   ```bash
   # macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json
   
   # Linux
   ~/.config/Claude/claude_desktop_config.json
   
   # Windows
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add BMM server:**
   ```json
   {
     "mcpServers": {
       "bmm-workflows": {
         "command": "python3",
         "args": [
           "/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/mcp/bmm_server.py"
         ],
         "env": {
           "PYTHONPATH": "/Users/kooshapari/temp-PRODVERCEL/485/kush/trace"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify in Claude:**
   - Look for 🔌 icon in chat
   - Should see "bmm-workflows" server
   - Should see tools: init_project, run_workflow, run_phase, get_status

### For Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "bmm-workflows": {
      "command": "python3",
      "args": [
        "/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/mcp/bmm_server.py"
      ]
    }
  }
}
```

### For Custom MCP Client

```python
from fastmcp.client import FastMCPClient

client = FastMCPClient(
    server_script="/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/mcp/bmm_server.py",
    transport="stdio"
)

# Use client
result = await client.call_tool("get_status", {})
```

## Testing

### Test 1: Server Starts

```bash
python3 scripts/mcp/bmm_server.py
# Should start without errors
# Press Ctrl+C to stop
```

### Test 2: CLI Status

```bash
python3 scripts/mcp/bmm_cli.py status
# Should show current project status
```

### Test 3: List Tools

```bash
python3 scripts/mcp/bmm_cli.py tools
# Should show beautiful table of tools
```

### Test 4: List Resources

```bash
python3 scripts/mcp/bmm_cli.py resources
# Should show tree of resources
```

### Test 5: Read Resource

```bash
python3 scripts/mcp/bmm_cli.py read bmm://workflow-status
# Should show workflow status YAML
```

### Test 6: Run Workflow (Dry Run)

```bash
# This will test the full workflow execution
python3 scripts/mcp/bmm_cli.py run --help
# Should show run command help
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastmcp'"

**Solution:**
```bash
pip install fastmcp==3.0.0b1
```

### Issue: "ModuleNotFoundError: No module named 'typer'"

**Solution:**
```bash
pip install typer rich
```

### Issue: "Permission denied"

**Solution:**
```bash
chmod +x scripts/mcp/bmm_server.py
chmod +x scripts/mcp/bmm_cli.py
```

### Issue: Claude Desktop doesn't show server

**Solution:**
1. Check config file path is correct
2. Verify JSON syntax (use jsonlint.com)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs:
   ```bash
   # macOS
   ~/Library/Logs/Claude/mcp*.log
   ```

### Issue: "Project not initialized"

**Solution:**
```bash
python3 scripts/mcp/bmm_cli.py init
```

### Issue: Server crashes on startup

**Solution:**
1. Check Python version: `python3 --version`
2. Check FastMCP version: `pip show fastmcp`
3. Run with verbose logging:
   ```bash
   python3 scripts/mcp/bmm_server.py --verbose
   ```

## Advanced Configuration

### Enable Redis Storage

```python
# In bmm_server.py, add:
from fastmcp.storage import RedisStorage

mcp.set_storage(RedisStorage(url="redis://localhost:6379"))
```

### Enable Authentication

```python
# In bmm_server.py, add:
from fastmcp.auth import BearerAuth

mcp = FastMCP(
    "bmm-workflows",
    auth=BearerAuth(token="your-secret-token")
)
```

### Enable SSE Transport (Remote Access)

```bash
# Start server with SSE
python3 scripts/mcp/bmm_server.py --transport sse --host 0.0.0.0 --port 8000

# Connect from remote client
client = FastMCPClient(
    server_url="http://your-server:8000",
    transport="sse"
)
```

## Next Steps

1. ✅ Complete setup
2. ✅ Test with CLI
3. ✅ Test with Claude Desktop
4. ✅ Run first workflow
5. ✅ Explore resources and prompts
6. ✅ Customize for your needs

## Support

- **Documentation**: scripts/mcp/README.md
- **Design**: scripts/mcp/DESIGN.md
- **FastMCP Docs**: https://gofastmcp.com/
- **Issues**: Check main project repository

## Quick Reference

```bash
# Initialize project
bmm init

# Check status
bmm status

# Run next workflow
bmm next

# Run specific workflow
bmm run prd

# Run phase
bmm run --phase 0

# Run phase in parallel
bmm run --phase 0 --parallel

# List resources
bmm resources

# Read resource
bmm read bmm://workflow-status

# List tools
bmm tools

# List prompts
bmm prompts

# Show config
bmm config

# Start server (debug)
bmm server
```
