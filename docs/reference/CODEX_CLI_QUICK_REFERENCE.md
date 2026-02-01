# OpenAI Codex CLI: Quick Reference Guide

## Authentication Quick Start

### OAuth Login (Recommended)
```bash
codex login
# Opens browser for ChatGPT login
# Token stored: ~/.codex/credentials
```

### Device Code (Headless/SSH)
```bash
codex login --device-auth
# Visit: https://device.openai.com/auth?code=XXXX
# Enter code, then approve
```

### API Key (CI/CD)
```bash
export OPENAI_API_KEY="sk-..."
codex exec --task "your task here"
```

---

## Essential Commands

### Interactive Mode
```bash
codex              # Start interactive session
codex --cwd /path  # Set working directory
codex --file app.py --task "add logging"  # Pre-load file
```

### Non-Interactive (CI/CD)
```bash
codex exec --task "write python function"
codex e "fix the bug"          # Short form
codex exec --full-auto --task "..."  # No approval prompts
```

### File & Code Operations
```bash
codex --file src/api.py --task "add error handling"
codex --image screenshot.png --task "build this UI"
codex review                   # Review staged changes
codex review --file app.py     # Review specific file
```

---

## Security Cheat Sheet

### Sandbox Modes
```bash
# Read-only (safest for analysis)
codex exec --task "analyze code" --sandbox read-only

# Workspace-write (default safe option)
codex exec --task "refactor" --sandbox workspace-write

# Danger-full-access (ONLY in isolated containers!)
codex exec --task "..." --sandbox danger-full-access
```

### Safe Practices
- Never use `--dangerously-bypass-approvals-and-sandbox` in production
- Always require approvals for write operations
- Restrict working directory with `--cwd`
- Use read-only mode for analysis tasks
- Validate input before passing to Codex

---

## Common Patterns

### Generate Code
```python
import subprocess

def codex_generate(task: str) -> str:
    result = subprocess.run(
        ["codex", "exec", "--task", task, "--full-auto"],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise Exception(f"Failed: {result.stderr}")
    return result.stdout
```

### Structured Output
```python
import subprocess
import json

def codex_with_schema(task: str, schema_path: str) -> dict:
    result = subprocess.run(
        ["codex", "exec", "--task", task,
         "--output-schema", schema_path, "--full-auto"],
        capture_output=True, text=True, timeout=300
    )
    return json.loads(result.stdout)
```

### Error Handling
```python
def codex_safe(task: str) -> str:
    try:
        result = subprocess.run(
            ["codex", "exec", "--task", task],
            capture_output=True, text=True, timeout=300
        )
        if "rate limit" in result.stderr.lower():
            raise RuntimeError("Rate limited")
        if result.returncode != 0:
            raise RuntimeError(f"Failed: {result.stderr}")
        return result.stdout
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timeout (5 min exceeded)")
```

---

## Configuration Files

### ~/.codex/config.toml
```toml
[auth]
method = "oauth"

[model]
default = "o3"

[execution]
sandbox = "workspace-write"
require_approval = true
timeout = 300

[shell.environment]
inherit = "core"
exclude = ["PRIVATE_KEY", "SECRET_TOKEN"]
```

### ~/.codex/credentials
- Auto-created by Codex
- Contains encrypted OAuth token
- Never commit to git

---

## Troubleshooting

### Not Authenticated
```bash
$ codex login
# Check status:
$ codex auth status
```

### Rate Limited
```bash
$ codex status
# Shows messages used/limit
# Wait 5 hours for window reset
```

### Timeout
```bash
# Increase timeout
codex exec --task "..." --timeout 600
```

### Sandbox Violation
```bash
# Read error message:
# "Permission denied: can't write outside workspace"
# Solution: Use correct --sandbox mode
```

### MCP Server Won't Start
```bash
# Check Node.js installed
node --version

# Check npm/npx works
npx --version

# Reinstall Codex
npm install -g codex
```

---

## MCP Integration (Agents SDK)

### Basic Setup
```python
from openai.agents import Agent
from openai.agents.mcp import MCPServerStdio

codex = MCPServerStdio(
    command="npx",
    args=["-y", "codex", "mcp-server"]
)

agent = Agent(
    model="gpt-4o",
    tools=[codex]
)
```

### Use in Agent
```python
response = agent.run(
    task="Generate FastAPI REST API"
)
```

---

## Performance Tips

1. **Use `--full-auto` for CI/CD** - Removes approval delays
2. **Set appropriate `--timeout`** - Default 300s (5 min)
3. **Use `--sandbox read-only` for analysis** - Faster responses
4. **Batch tasks when possible** - Fewer invocations
5. **Cache schema files** - Reuse output schemas
6. **Monitor rate limits** - Check with `codex status`

---

## Environment Variables

```bash
CODEX_HOME="~/.codex"              # Config directory
OPENAI_API_KEY="sk-..."            # For API key auth
CODEX_SANDBOX="workspace-write"    # Sandbox mode
CODEX_MODEL="o3"                   # Model selection
CODEX_TIMEOUT="600"                # Timeout seconds
CODEX_FULL_AUTO="true"             # Auto-approve
```

---

## Model Selection

```bash
# Available models
codex exec --task "..." --model o3          # Latest/most capable
codex exec --task "..." --model o4-mini     # Faster, cheaper
codex exec --task "..." --model gpt-4       # Stable, reliable

# Check available
codex config show --json | grep model
```

---

## File Operations Examples

### Edit Python File
```bash
codex --file main.py \
  --task "Add comprehensive docstrings to all functions"
```

### Create New File
```bash
codex exec \
  --task "Write a Python decorator for retry logic with exponential backoff"
```

### Multiple Files
```bash
codex --file app.py,config.py \
  --task "Refactor to use environment variables for config"
```

### From Screenshot
```bash
codex --image ui-mockup.png \
  --task "Implement this UI in React with TypeScript"
```

---

## Testing Generated Code

```bash
# Generate code with tests
codex exec --task "Write Python function to validate email with unit tests"

# Run the generated code
codex exec --task "Write a test suite for the sorting algorithm"

# Review test coverage
codex review --file tests/test_main.py
```

---

## Rate Limit Strategy

1. Check limits: `codex status`
2. Plan batch work
3. Use appropriate sandbox (read-only = faster)
4. Monitor usage over time
5. Request quota increase if needed

---

## Integration Checklist

- [ ] Codex installed: `npm install -g codex`
- [ ] Authenticated: `codex login` or `OPENAI_API_KEY` set
- [ ] Configuration file exists: `~/.codex/config.toml`
- [ ] Sandbox mode appropriate for use case
- [ ] Error handling in place
- [ ] Rate limiting monitored
- [ ] MCP server tested (if using agents)
- [ ] Timeout values appropriate
- [ ] Environment variables secure
- [ ] Approvals configured correctly

---

## Resources

- Official Docs: https://developers.openai.com/codex/
- GitHub: https://github.com/openai/codex
- Agents SDK: https://developers.openai.com/codex/guides/agents-sdk/
- MCP Protocol: https://developers.openai.com/codex/mcp/
- Security: https://developers.openai.com/codex/security/

---

*Quick reference current as of January 28, 2026*
