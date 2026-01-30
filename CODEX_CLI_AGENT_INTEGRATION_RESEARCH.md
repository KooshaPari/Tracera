# OpenAI Codex CLI: Comprehensive Agent Integration Research

**Date**: January 28, 2026
**Research Focus**: Authentication, CLI Commands, Agent Capabilities, Integration Patterns, Security, and Configuration

---

## Executive Summary

OpenAI Codex CLI is a lightweight, open-source coding agent that runs in the terminal, offering powerful capabilities for automated code generation, file manipulation, and shell command execution. This research provides comprehensive guidance on integrating Codex CLI as an agent within Python systems, with focus on authentication mechanisms, MCP server integration, sandbox security modes, and practical programmatic invocation patterns.

**Key Findings**:
- Codex supports three authentication flows: OAuth (browser-based), Device Code (headless), and API key (direct)
- MCP (Model Context Protocol) server mode enables seamless integration with other agents and systems
- Sandbox modes (read-only, workspace-write, danger-full-access) provide fine-grained permission control
- CLI supports non-interactive mode (`--full-auto`, `codex exec`) for CI/CD automation
- Multimodal capabilities include vision-based image understanding and file manipulation

---

## 1. Authentication Mechanisms

### 1.1 OAuth Flow (Browser-based Authentication)

**Default Method**: Interactive login with ChatGPT account

```bash
# Standard OAuth login
codex login

# Prompts user to open browser and authenticate with OpenAI account
# Token automatically stored in ~/.codex/credentials
```

**How It Works**:
- User runs `codex login` in terminal
- CLI spawns local HTTP server on localhost:8080 (callback endpoint)
- Browser opens OpenAI OAuth endpoint
- User authenticates with ChatGPT credentials
- OAuth token returns to localhost callback
- CLI stores token in `~/.codex/credentials` (encrypted)

**Limitations**:
- Requires graphical browser access
- Fails on headless/SSH environments
- Localhost callback blocked by corporate firewalls

**Token Storage**:
```
~/.codex/
├── credentials          # Encrypted OAuth token
├── config.toml         # Configuration
└── sessions/           # Session logs (JSONL)
```

### 1.2 Device Code Authentication (Headless Environments)

**For SSH, containers, remote development machines**

```bash
# Device code login (headless)
codex login --device-auth

# Output:
# Visit: https://device.openai.com/auth?code=XXXX-YYYY
# Paste code: XXXX-YYYY
# [waiting for authorization...]
```

**Process**:
1. Generate unique device code and user code
2. User visits device.openai.com and enters user code
3. CLI polls OpenAI for token confirmation
4. Token returned and stored in credentials

**Requirements**:
- Workspace admin must enable "Device Code Authentication" in ChatGPT settings
- User or admin must approve at workspace level
- No interactive browser required

**Known Issues (2026)**:
- Some workspace admins block device code auth for security
- Fallback to API key required if disabled

### 1.3 API Key Authentication (Direct)

**Programmatic/CI/CD authentication**

```bash
# Method 1: Environment variable
export OPENAI_API_KEY="sk-..."
codex exec --task "write python script"

# Method 2: Pipe API key to login
echo "sk-..." | codex login --api-key

# Method 3: Configuration file
# ~/.codex/config.toml
[auth]
api_key = "sk-..."
```

**Advantages**:
- No interactive login required
- Works in CI/CD pipelines
- No browser or device approval needed
- Direct API access

**Security Considerations**:
- Store in environment variables, not in code
- Rotate keys regularly
- Use restricted API keys with minimal permissions
- Never commit to git repositories

### 1.4 Token Refresh and Expiration

```bash
# Check current authentication status
codex auth status

# Refresh token if expired
codex auth refresh

# Logout
codex logout
```

**Token Lifecycle**:
- OAuth tokens typically valid for 30 days
- Automatic refresh on expiration
- Device code tokens valid for 1 session
- API keys don't expire unless revoked

---

## 2. CLI Commands and Options Reference

### 2.1 Core Command Structure

```bash
# Basic syntax
codex [OPTIONS] [COMMAND] [ARGS]

# Common options
codex --help              # Show help
codex --version          # Show version
codex --debug            # Enable debug logging
codex -c/--config PATH   # Override config file
codex -p/--profile NAME  # Use config profile
```

### 2.2 Main Commands

#### Interactive Mode (Default)

```bash
# Start interactive session
codex                     # Open interactive composer
codex --cwd /path        # Set working directory
codex --file app.py      # Pre-load file in editor

# Within interactive session:
/help                    # Show help topics
/status                  # Show rate limits and usage
/undo                    # Undo last action
/clear                   # Clear conversation
/exit                    # Exit session
```

#### Non-Interactive Execution

```bash
# Non-interactive execution mode (recommended for CI/CD)
codex exec --task "write a Python function to calculate prime numbers"

codex e --task "fix the bug in main.py"  # Short form

# Full-auto mode (all approvals granted)
codex exec --task "refactor code" --full-auto

# With specific sandbox permissions
codex exec --task "install dependencies" \
  --sandbox workspace-write \
  --full-auto
```

#### File-Specific Operations

```bash
# Edit specific file
codex --file src/main.py --task "add error handling"

# Multiple files
codex --file app.py,config.py --task "refactor to use new config"

# Include images in prompt
codex --file screenshot.png --task "implement this UI design"
```

#### Code Review

```bash
# Review staged changes
codex review

# Review specific commit
codex review --commit abc123def

# Generate review report
codex review --output-schema review-schema.json
```

### 2.3 Advanced Flags

```bash
# --full-auto: No approvals required (use carefully!)
codex exec --task "..." --full-auto

# --sandbox: Permission level
codex exec --task "..." --sandbox read-only              # No write access
codex exec --task "..." --sandbox workspace-write        # Write in project
codex exec --task "..." --sandbox danger-full-access     # Full access (DANGER!)

# --dangerously-bypass-approvals-and-sandbox
# NEVER use in production - only in isolated CI runners!

# --output-schema: Structured output
codex exec --task "..." --output-schema schema.json

# --model: Specify model
codex exec --task "..." --model o3              # o3, o4-mini, etc.
codex exec --task "..." --model gpt-4

# --timeout: Execution timeout
codex exec --task "..." --timeout 300           # 5 minutes

# --cwd: Working directory
codex exec --task "..." --cwd /project/src

# --image: Multimodal input
codex exec --task "implement from screenshot" --image screenshot.png
```

---

## 3. MCP Server Mode for Agent Integration

### 3.1 Running Codex as MCP Server

**Enables integration with Claude, other agents, and orchestration tools**

```bash
# Start Codex as MCP server (stdio mode)
codex mcp-server

# For use with Agents SDK:
npx codex mcp-server

# Configure in agent's stdio config:
# {
#   "command": "npx",
#   "args": ["-y", "codex", "mcp-server"]
# }
```

### 3.2 MCP Tools Exposed

When running as MCP server, Codex exposes two primary tools:

```
1. codex()
   - Input: Initial task/prompt
   - Output: Streaming agent response
   - Events: Task progress, file changes, command execution

2. codex-reply(session_id, user_message)
   - Input: Session ID + continuation message
   - Output: Agent response
   - Maintains conversation context across turns
```

### 3.3 MCP Server Configuration

**In Agents SDK configuration**:

```python
from openai.agents import Agent
from openai.agents.mcp import MCPServerStdio

# Define Codex as MCP tool
codex_mcp = MCPServerStdio(
    command="npx",
    args=["-y", "codex", "mcp-server"]
)

# Create agent with Codex tool
agent = Agent(
    model="gpt-4o",
    tools=[codex_mcp],
    instructions="You can use Codex to write and review code"
)

# Use in agent
response = agent.run(
    task="Generate a Python API using FastAPI"
)
```

### 3.4 Event Streaming from MCP

```python
# MCP server streams events back as notifications:
# {
#   "type": "notification",
#   "method": "progress",
#   "params": {
#     "request_id": "...",
#     "stage": "analyzing",
#     "description": "Analyzing code structure..."
#   }
# }

# Codex events include:
# - codex.analyzing        (analyzing code/requirements)
# - codex.generating       (generating solution)
# - codex.reviewing        (reviewing generated code)
# - codex.file_edit        (file modification event)
# - codex.shell_execute    (shell command execution)
# - codex.approval_needed  (waiting for approval)
```

---

## 4. Agent Capabilities

### 4.1 Code Generation

**Python Example - Factorial Function**

```bash
codex exec --task "Write a Python function that calculates factorial with memoization"
```

**Output**:
```python
def factorial(n, memo={}):
    """Calculate factorial with memoization."""
    if n in memo:
        return memo[n]
    if n <= 1:
        return 1
    memo[n] = n * factorial(n - 1, memo)
    return memo[n]

# Tests included:
# assert factorial(5) == 120
# assert factorial(10) == 3628800
```

### 4.2 File Manipulation

**Patch-based Changes**:

```bash
codex exec --file app.py --task "Add comprehensive error handling"
```

Codex returns patches that show exact changes:

```diff
--- app.py
+++ app.py
@@ -10,7 +10,12 @@
 def process_data(file_path):
-    data = open(file_path).read()
+    try:
+        with open(file_path, 'r') as f:
+            data = f.read()
+    except FileNotFoundError:
+        logging.error(f"File {file_path} not found")
+        return None
+    except IOError as e:
+        logging.error(f"IO error: {e}")
+        return None
```

### 4.3 Shell Command Execution

**Interactive execution with output capture**:

```bash
codex exec --task "Set up Python virtual environment and install dependencies"
```

Codex executes (with approval):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

**Inline Command Execution** (in interactive mode):

```
User: Install and test the code
Codex: I'll install dependencies and run tests
> !pip install -e .
> !pytest tests/
```

### 4.4 Code Review Capabilities

```bash
codex review --output-schema review.json
```

**Output Structure**:
```json
{
  "summary": "Code quality is good with minor improvements",
  "files_reviewed": 5,
  "issues": [
    {
      "file": "src/api.py",
      "line": 42,
      "severity": "warning",
      "message": "Consider adding type hints",
      "suggestion": "def process(data: dict) -> dict:"
    }
  ],
  "improvements": [
    {
      "category": "performance",
      "description": "N+1 query detected in loop"
    }
  ]
}
```

### 4.5 Multimodal Understanding

**Vision and Image Analysis**:

```bash
# Analyze screenshot and generate code
codex exec --image screenshot.png \
  --task "Implement this UI design in React"

# Multiple images for context
codex exec --image wireframe.png,mock.png \
  --task "Build the component shown in these mockups"

# Error screenshot analysis
codex exec --image error-screenshot.png \
  --task "Debug this error"
```

Supported formats: PNG, JPEG, WebP, GIF

### 4.6 Multi-turn Conversations

```bash
# Start session
codex

# Turn 1
User: Write a user authentication system in FastAPI
Codex: [generates auth system with JWT]

# Turn 2 (context retained)
User: Add password reset functionality
Codex: [updates existing system to include reset flow]

# Turn 3
User: Add email verification
Codex: [continues building on context]
```

---

## 5. Integration Patterns for Python

### 5.1 Subprocess Invocation (Simple)

```python
import subprocess
import json
import tempfile
from pathlib import Path

def invoke_codex_simple(task: str, cwd: str = None) -> str:
    """Simple wrapper for codex exec command."""
    cmd = [
        "codex", "exec",
        "--task", task,
        "--full-auto"
    ]

    if cwd:
        cmd.extend(["--cwd", cwd])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        raise RuntimeError(f"Codex failed: {result.stderr}")

    return result.stdout

# Usage
try:
    output = invoke_codex_simple(
        "Write a Python decorator for caching function results",
        cwd="/project"
    )
    print(output)
except Exception as e:
    print(f"Error: {e}")
```

### 5.2 Structured Output with JSON Schema

```python
import subprocess
import json
import tempfile

def invoke_codex_structured(
    task: str,
    output_schema: dict,
    cwd: str = None
) -> dict:
    """Invoke Codex with structured JSON output."""

    # Write schema to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False
    ) as f:
        json.dump(output_schema, f)
        schema_path = f.name

    try:
        cmd = [
            "codex", "exec",
            "--task", task,
            "--output-schema", schema_path,
            "--full-auto"
        ]

        if cwd:
            cmd.extend(["--cwd", cwd])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise RuntimeError(f"Codex failed: {result.stderr}")

        # Parse JSON output
        return json.loads(result.stdout)
    finally:
        Path(schema_path).unlink()

# Example schema for code review
review_schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "severity": {"enum": ["error", "warning", "info"]},
                    "message": {"type": "string"}
                }
            }
        }
    }
}

# Usage
review = invoke_codex_structured(
    "Review the code in app.py for quality issues",
    review_schema,
    cwd="/project"
)
print(f"Found {len(review['issues'])} issues")
```

### 5.3 Session-based Agent Class

```python
import subprocess
import json
import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class CodexEvent:
    """Represents event from Codex."""
    type: str          # analyzing, generating, reviewing, file_edit, shell_execute
    description: str
    data: Optional[dict] = None

class CodexAgent:
    """Wrapper for Codex CLI agent."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load Codex configuration."""
        result = subprocess.run(
            ["codex", "config", "show", "--json"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}

    def generate_code(
        self,
        task: str,
        file: Optional[str] = None,
        model: str = "o3"
    ) -> str:
        """Generate code using Codex."""
        cmd = ["codex", "exec", "--task", task, "--model", model, "--full-auto"]

        if file:
            cmd.extend(["--file", file])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise RuntimeError(f"Code generation failed: {result.stderr}")

        return result.stdout

    def review_code(self, file: str) -> dict:
        """Review code with Codex."""
        result = subprocess.run(
            ["codex", "review", "--file", file, "--json"],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise RuntimeError(f"Code review failed: {result.stderr}")

        return json.loads(result.stdout)

    def execute_shell(self, command: str, cwd: Optional[str] = None) -> str:
        """Execute shell command within Codex context."""
        task = f"Execute this shell command: {command}"
        cmd = ["codex", "exec", "--task", task, "--full-auto"]

        if cwd:
            cmd.extend(["--cwd", cwd])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"Shell execution failed: {result.stderr}")

        return result.stdout

    def get_status(self) -> dict:
        """Get Codex status and rate limits."""
        result = subprocess.run(
            ["codex", "status", "--json"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return json.loads(result.stdout)

        return {"authenticated": False, "error": result.stderr}

# Usage Example
if __name__ == "__main__":
    agent = CodexAgent()

    # Generate code
    code = agent.generate_code(
        "Write a Python class for managing database connections with connection pooling"
    )
    print("Generated Code:")
    print(code)

    # Check status
    status = agent.get_status()
    print(f"\nRate Limit Status: {status}")
```

### 5.4 MCP Client Integration (Advanced)

```python
import asyncio
import json
from typing import Optional, AsyncGenerator

class CodexMCPClient:
    """Client for Codex MCP server."""

    def __init__(self, codex_mcp_command: list):
        self.codex_mcp_command = codex_mcp_command  # e.g., ["npx", "codex", "mcp-server"]
        self.process = None
        self.request_id = 0

    async def start(self):
        """Start Codex MCP server process."""
        import asyncio
        self.process = await asyncio.create_subprocess_exec(
            *self.codex_mcp_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def send_request(self, method: str, params: dict) -> dict:
        """Send JSON-RPC request to Codex MCP server."""
        self.request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }

        # Send to stdin
        self.process.stdin.write((json.dumps(request) + "\n").encode())
        await self.process.stdin.drain()

        # Read response from stdout
        line = await self.process.stdout.readline()
        if not line:
            raise RuntimeError("Codex MCP server closed connection")

        return json.loads(line.decode())

    async def generate_code(self, task: str) -> AsyncGenerator[str, None]:
        """Generate code with streaming response."""
        response = await self.send_request("codex", {"task": task})

        # Stream content
        for chunk in response.get("content", []):
            if chunk.get("type") == "text":
                yield chunk.get("text", "")

    async def close(self):
        """Close MCP connection."""
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Async usage example
async def main():
    client = CodexMCPClient(["npx", "codex", "mcp-server"])
    await client.start()

    try:
        async for chunk in client.generate_code("Write a REST API in FastAPI"):
            print(chunk, end="", flush=True)
    finally:
        await client.close()

# Run: asyncio.run(main())
```

---

## 6. Security Considerations

### 6.1 Sandbox Modes Explained

**Read-Only Mode**:
```bash
codex exec --task "analyze code" --sandbox read-only
# Codex can:
#   - Read files in project
#   - Analyze code structure
# Codex CANNOT:
#   - Write files
#   - Run commands
#   - Access network
```

**Workspace-Write Mode** (default safe option):
```bash
codex exec --task "refactor code" --sandbox workspace-write
# Codex can:
#   - Read all files in project
#   - Write within project directory
#   - Run commands in project context
#   - Access project dependencies
# Codex CANNOT:
#   - Write outside project directory
#   - Access parent directories
#   - Use network (by default)
```

**Danger-Full-Access Mode** (DANGEROUS):
```bash
codex exec --task "..." --sandbox danger-full-access
# Codex can:
#   - Read/write ANYWHERE on system
#   - Execute any shell command
#   - Access network
#   - Modify system files
# ONLY USE in:
#   - Isolated CI/CD runners
#   - Temporary Docker containers
#   - Dedicated sandbox VMs
```

### 6.2 Approval Policies

```bash
# Default: asks for approval before risky actions
codex exec --task "..."

# Auto-approve within sandbox boundaries
codex exec --task "..." --full-auto

# Never ask (DANGEROUS!)
codex exec --task "..." --dangerously-bypass-approvals-and-sandbox
# Only safe in:
#   - Dedicated isolated VM
#   - Temporary container
#   - Trusted CI/CD runner
```

### 6.3 Secure Python Integration

```python
import subprocess
import os
from typing import Optional
from enum import Enum

class SandboxMode(str, Enum):
    READ_ONLY = "read-only"
    WORKSPACE_WRITE = "workspace-write"
    DANGER_FULL_ACCESS = "danger-full-access"

class SecureCodexInvoker:
    """Secure wrapper for Codex CLI invocation."""

    def __init__(self,
                 sandbox: SandboxMode = SandboxMode.WORKSPACE_WRITE,
                 require_approval: bool = True,
                 timeout: int = 300,
                 allowed_cwd: Optional[str] = None):
        self.sandbox = sandbox
        self.require_approval = require_approval
        self.timeout = timeout
        self.allowed_cwd = allowed_cwd

    def invoke(self, task: str, cwd: Optional[str] = None) -> str:
        """Safely invoke Codex with security controls."""

        # Security check: validate cwd if restricted
        if self.allowed_cwd:
            resolved_cwd = os.path.realpath(cwd or os.getcwd())
            allowed = os.path.realpath(self.allowed_cwd)

            if not resolved_cwd.startswith(allowed):
                raise ValueError(f"CWD {cwd} outside allowed {self.allowed_cwd}")

        # Security check: never use full access with auto-approve together
        if (self.sandbox == SandboxMode.DANGER_FULL_ACCESS
            and not self.require_approval):
            raise ValueError(
                "SECURITY: Cannot use danger-full-access without approvals. "
                "This prevents accidental malicious execution."
            )

        # Build safe command
        cmd = [
            "codex", "exec",
            "--task", task,
            "--sandbox", self.sandbox.value
        ]

        if not self.require_approval:
            cmd.append("--full-auto")

        if cwd:
            cmd.extend(["--cwd", cwd])

        # Execute with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )

        if result.returncode != 0:
            # Don't expose full stderr for security
            raise RuntimeError(f"Codex execution failed with code {result.returncode}")

        return result.stdout

# Safe usage examples
def safe_code_review():
    """Review code (read-only, safe)."""
    invoker = SecureCodexInvoker(
        sandbox=SandboxMode.READ_ONLY,
        require_approval=True
    )
    return invoker.invoke("Review code for security issues")

def safe_refactoring():
    """Refactor code (workspace-write, approvals required)."""
    invoker = SecureCodexInvoker(
        sandbox=SandboxMode.WORKSPACE_WRITE,
        require_approval=True,
        allowed_cwd="/project/src"
    )
    return invoker.invoke("Refactor for better performance", cwd="/project/src")
```

### 6.4 Environment Variable Management

```python
import os
from typing import Dict, Optional

class CodexEnvironment:
    """Manage Codex-safe environment variables."""

    # Variables Codex SHOULD inherit
    SAFE_INHERIT = {
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "LANG",
        "LC_ALL",
        "TERM"
    }

    # Never pass to Codex
    DANGEROUS = {
        "AWS_SECRET_ACCESS_KEY",
        "GITHUB_TOKEN",
        "OPENAI_API_KEY",
        "DATABASE_PASSWORD",
        "PRIVATE_KEY"
    }

    @staticmethod
    def get_safe_env() -> Dict[str, str]:
        """Get only safe environment variables for Codex."""
        env = {}
        for key, value in os.environ.items():
            if key in CodexEnvironment.SAFE_INHERIT:
                env[key] = value
        return env

    @staticmethod
    def validate_env(env_vars: Dict[str, str]) -> bool:
        """Check if env vars contain secrets."""
        for key in env_vars.keys():
            if key in CodexEnvironment.DANGEROUS:
                return False
        return True

# Usage
safe_env = CodexEnvironment.get_safe_env()
# Pass only safe environment to Codex
```

---

## 7. Configuration Reference

### 7.1 Config File Structure (~/.codex/config.toml)

```toml
[auth]
# Authentication method: oauth, device, or api_key
method = "oauth"
api_key = ""  # For API key auth

[model]
# Default model for generation
default = "o3"
# Available: o3, o4-mini, gpt-4, etc.

[execution]
# Default sandbox mode
sandbox = "workspace-write"
# Ask for approval before actions
require_approval = true
# Default timeout in seconds
timeout = 300

[cli]
# Verbose output
verbose = false
# Color output
colored = true
# Output format: text, json, structured
output = "text"

[mcp]
# Enable MCP server mode
enabled = true
# MCP server settings
[mcp.server]
port = 3000
host = "127.0.0.1"

[logging]
# Log level: debug, info, warning, error
level = "info"
# Log file location
file = "~/.codex/logs/codex.log"

[shell]
# Environment variables policy
[shell.environment]
# inherit: "none", "core", or "all"
inherit = "core"
# Variables to always include
include = ["PATH", "HOME"]
# Variables to exclude
exclude = ["PRIVATE_KEY", "SECRET_TOKEN"]
# Variable overrides
overrides = { CUSTOM_VAR = "value" }
```

### 7.2 Environment Variables

```bash
# Core configuration
export CODEX_HOME="~/.codex"                    # Config directory
export OPENAI_API_KEY="sk-..."                  # API key auth

# Behavior overrides
export CODEX_SANDBOX="workspace-write"          # Sandbox mode
export CODEX_MODEL="o3"                         # Model selection
export CODEX_TIMEOUT="600"                      # Timeout in seconds
export CODEX_FULL_AUTO="true"                   # Auto-approve

# Advanced configuration
export CODEX_DEBUG="true"                       # Enable debug logging
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Custom endpoint
export HTTP_PROXY="http://proxy:8080"           # Proxy settings
```

### 7.3 Profile-based Configuration

```bash
# Use named profile
codex exec --task "..." --profile ci-cd

# ~/.codex/config.toml profiles
[profile.ci-cd]
sandbox = "workspace-write"
require_approval = false
timeout = 600

[profile.safe]
sandbox = "read-only"
require_approval = true

[profile.interactive]
sandbox = "workspace-write"
require_approval = true
verbose = true
```

---

## 8. Error Handling and Recovery

### 8.1 Common Error Patterns

```python
import subprocess
from enum import Enum

class CodexErrorType(str, Enum):
    AUTH_FAILED = "auth_failed"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    SANDBOX_VIOLATION = "sandbox_violation"
    INVALID_SYNTAX = "invalid_syntax"
    FILE_NOT_FOUND = "file_not_found"
    UNKNOWN = "unknown"

class CodexError(Exception):
    """Structured Codex error."""

    def __init__(self, error_type: CodexErrorType, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(f"[{error_type}] {message}")

def invoke_with_error_handling(task: str) -> str:
    """Invoke Codex with proper error handling."""
    try:
        result = subprocess.run(
            ["codex", "exec", "--task", task, "--full-auto"],
            capture_output=True,
            text=True,
            timeout=300
        )
    except subprocess.TimeoutExpired:
        raise CodexError(
            CodexErrorType.TIMEOUT,
            "Codex execution exceeded 5-minute timeout"
        )
    except FileNotFoundError:
        raise CodexError(
            CodexErrorType.FILE_NOT_FOUND,
            "Codex CLI not installed. Install with: npm install -g codex"
        )

    # Parse error codes
    if result.returncode == 0:
        return result.stdout

    stderr = result.stderr.lower()

    if "unauthorized" in stderr or "invalid token" in stderr:
        raise CodexError(
            CodexErrorType.AUTH_FAILED,
            "Authentication failed. Run: codex login"
        )

    if "rate limit" in stderr or "429" in stderr:
        raise CodexError(
            CodexErrorType.RATE_LIMITED,
            "Rate limited. Check status with: codex status"
        )

    if "sandbox" in stderr or "permission denied" in stderr:
        raise CodexError(
            CodexErrorType.SANDBOX_VIOLATION,
            f"Sandbox violation: {result.stderr}"
        )

    if "syntax" in stderr:
        raise CodexError(
            CodexErrorType.INVALID_SYNTAX,
            f"Invalid task syntax: {result.stderr}"
        )

    raise CodexError(
        CodexErrorType.UNKNOWN,
        f"Unexpected error: {result.stderr}"
    )

# Usage with retry logic
def invoke_with_retry(task: str, max_retries: int = 3) -> str:
    """Invoke with exponential backoff retry."""
    import time

    for attempt in range(max_retries):
        try:
            return invoke_with_error_handling(task)
        except CodexError as e:
            if e.error_type == CodexErrorType.RATE_LIMITED:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            raise  # Re-raise other errors

    raise CodexError(
        CodexErrorType.RATE_LIMITED,
        f"Failed after {max_retries} retries due to rate limiting"
    )
```

### 8.2 Logging and Diagnostics

```python
import logging
import json
from pathlib import Path

# Configure Codex logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_codex_diagnostics() -> dict:
    """Gather diagnostic information for troubleshooting."""
    diagnostics = {}

    # Check installation
    result = subprocess.run(
        ["codex", "--version"],
        capture_output=True,
        text=True
    )
    diagnostics["installed"] = result.returncode == 0
    diagnostics["version"] = result.stdout.strip() if diagnostics["installed"] else None

    # Check authentication
    result = subprocess.run(
        ["codex", "auth", "status", "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        diagnostics["auth"] = json.loads(result.stdout)
    else:
        diagnostics["auth"] = {"authenticated": False}

    # Check rate limits
    result = subprocess.run(
        ["codex", "status", "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        diagnostics["status"] = json.loads(result.stdout)

    # Check configuration
    config_path = Path.home() / ".codex" / "config.toml"
    diagnostics["config_exists"] = config_path.exists()

    return diagnostics

# Usage
diagnostics = check_codex_diagnostics()
print(json.dumps(diagnostics, indent=2))
```

---

## 9. Rate Limiting and Usage

### 9.1 Rate Limit Information

**Message Quota System**:
- Limits based on message interactions (not tokens)
- Measured in 5-hour rolling windows
- Additional weekly quotas apply

**Checking Limits**:

```bash
# Interactive mode
codex
/status
# Shows: Messages used/limit in current window

# Programmatically
codex status --json
```

### 9.2 Output Parsing

**Session Logs** (automatic):

```
~/.codex/sessions/2026/01/28/rollout-20260128-120000.jsonl

Each line is JSON event:
{"type": "message", "role": "user", "content": "..."}
{"type": "message", "role": "assistant", "content": "..."}
{"type": "event", "event": "file_edit", "file": "app.py"}
```

**Structured Output with Schema**:

```bash
codex exec --task "..." --output-schema schema.json
# Returns JSON matching schema
```

---

## Summary of Key Resources

- [OpenAI Codex Authentication](https://developers.openai.com/codex/auth/)
- [CLI Reference](https://developers.openai.com/codex/cli/reference/)
- [Agents SDK Integration](https://developers.openai.com/codex/guides/agents-sdk/)
- [MCP Protocol](https://developers.openai.com/codex/mcp/)
- [Security Documentation](https://developers.openai.com/codex/security/)
- [Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [GitHub Repository](https://github.com/openai/codex)

---

*This research document is current as of January 28, 2026. Codex CLI specifications and features may change. Refer to official documentation for latest updates.*
