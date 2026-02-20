# Embedded CLIProxy in Go Backend + Claude Setup Reference + Agent SDK vs Claude Code CLI (Subagents)

Design and research for: (1) embedding CLIProxyAPI as a package in the Go backend, (2) referencing the clean/deploy Claude setup (atoms-tech, atomsAgent), and (3) validating Claude Agent SDK vs Claude Code CLI, especially regarding subagents.

---

## 1. Embedded CLIProxy service in Go backend

CLIProxyAPI exposes a **Go SDK** for embedding the proxy (routing, auth, translation) inside your own service without running the CLI binary.

### 1.1 Install and import

```bash
go get github.com/router-for-me/CLIProxyAPI/v6/sdk/cliproxy
```

```go
import (
    "context"
    "errors"
    "time"

    "github.com/router-for-me/CLIProxyAPI/v6/internal/config"
    "github.com/router-for-me/CLIProxyAPI/v6/sdk/cliproxy"
)
```

Use the **`/v6`** module path.

### 1.2 Minimal embed

```go
cfg, err := config.LoadConfig("config.yaml")
if err != nil { panic(err) }

svc, err := cliproxy.NewBuilder().
    WithConfig(cfg).
    WithConfigPath("config.yaml").  // absolute or working-dir relative
    Build()
if err != nil { panic(err) }

ctx, cancel := context.WithCancel(context.Background())
defer cancel()

if err := svc.Run(ctx); err != nil && !errors.Is(err, context.Canceled) {
    panic(err)
}
```

The service handles config hot-reload, auth/token refresh, and graceful shutdown. Cancel the context to stop it.

### 1.3 Server options (middleware, routes, logs)

- **WithMiddleware** – global Gin middleware.
- **WithEngineConfigurator** – tweak Gin engine (CORS, trusted proxies).
- **WithRouterConfigurator** – add your own routes after defaults (e.g. `/healthz`).
- **WithRequestLoggerFactory** – override request log writer/dir.

### 1.4 Custom auth and token sources

- **WithCoreAuthManager** – supply your own `auth.Manager` (e.g. custom RoundTripper per auth, programmatic `Execute` / `ExecuteStream`).
- **WithTokenClientProvider** / **WithAPIKeyClientProvider** – load tokens from memory or remote store instead of the default filesystem.

### 1.5 Hooks

- **OnBeforeStart**, **OnAfterStart** – lifecycle hooks without patching internals.

### 1.6 Shutdown

- `Run` defers `Shutdown`; cancelling the parent context is enough. Or call `svc.Shutdown(ctx)` with a timeout.

**Source:** [CLIProxyAPI docs/sdk-usage.md](https://github.com/router-for-me/CLIProxyAPI/blob/main/docs/sdk-usage.md). Repo layout: `sdk/cliproxy`, `internal/config`, `cmd/server`.

---

## 2. Reference: Claude setup in clean/deploy (atoms-tech, atomsAgent)

The **clean/deploy** tree contains two projects used as a reference for a “similarly complex” Claude setup:

- **atoms-tech** – frontend (React).
- **atomsAgent** – the Claude/sandbox system (Python services + optional tRPC/FastMCP).

**Path:** From repo root (`kush/trace`), go up two levels to `485`: **`../../clean/deploy`** → i.e. **`485/clean/deploy`** (sibling of `kush`, not under `kush`). So `clean` lives at `485/clean`, and deploy at `485/clean/deploy`.

### 2.1 Layout (summary)

| Path | Role |
|------|------|
| `clean/deploy/atoms.tech/` | Frontend (React) |
| `clean/deploy/atomsbot/` | Bot / automation |
| `clean/deploy/src/atomsAgent/` | Python: API routes, sandbox, services |
| `clean/deploy/mcp-atomsagent-integration/` | FastMCP + Claude SDK integration specs |

### 2.2 atomsAgent (Python)

- **api/routes/** – monitoring, sandbox, streaming.
- **sandbox/** – auth, manager, types (sandbox lifecycle).
- **services/** – e.g. `sandbox_agent.py`, `sandbox_claude_wrapper.py`, streaming, monitoring, tracing.

`SandboxClaudeWrapper` wraps a Claude client for sandbox execution (create_agent, query / query_stream with tools and options). Execution is delegated to **Vercel Sandbox** (SandboxManager → Vercel Sandbox API), not Claude Code CLI.

### 2.3 MCP–atomsAgent integration

- **FastMCP server** – middleware (auth, logging, response transform), tools: `execute_in_sandbox`, `get_execution_metrics`, `get_trace`.
- **Claude SDK integration** – `06_claude_sdk_integration.ts`: `ClaudeAtomAgentIntegration` uses **Anthropic Messages API** with tools (`execute_in_sandbox`, `get_execution_metrics`, `get_trace`), agentic loop (Claude decides tool use → execute → feed result back).
- **Flow:** Frontend (React) → tRPC → DB → FastMCP (tools) → Claude SDK integration (tool execution) → atomsAgent services (SandboxAgent) → SandboxManager → Vercel Sandbox API.

So Claude is used via **Messages API + tool use** (and optionally MCP), not via Claude Code CLI. The “complex” part is the chain: frontend → backend API → MCP/tools → Claude agent loop → sandbox execution.

**Reference files:**

- `clean/deploy/mcp-atomsagent-integration/ARCHITECTURE.md` – system and data flow.
- `clean/deploy/mcp-atomsagent-integration/06_claude_sdk_integration.ts` – Claude + atomsAgent tools.
- `clean/deploy/src/atomsAgent/services/sandbox_claude_wrapper.py` – wrapper around Claude client for sandbox runs.

---

## 3. Agent SDK vs Claude Code CLI – robustness and subagents (validated)

### 3.1 Official positioning

- **Agent SDK overview:** “The Agent SDK gives you the **same tools, agent loop, and context management** that power Claude Code, programmable in Python and TypeScript.”
- **Runtime:** The SDK uses **Claude Code as its runtime** (same executable); you install Claude Code and then use the SDK to drive it programmatically (e.g. `query()`, options, tools).

So the SDK is not a reimplementation; it reuses Claude Code under the hood and exposes the same capabilities in code.

### 3.2 Subagents – SDK support (validated)

**Programmatic subagents**

- **Options.agents** – `Record<string, AgentDefinition>`.
- **AgentDefinition** – `description`, `tools?`, `prompt`, `model?` ('sonnet' | 'opus' | 'haiku' | 'inherit').
- Use: define specialized subagents; the main agent can delegate to them.

**Task tool (invoke subagent)**

- **Tool name:** `Task` (documented as “Agent” in some contexts).
- **Input (AgentInput):** `description`, `prompt`, `subagent_type`.
- **Behavior:** “Launches a new agent to handle complex, multi-step tasks autonomously.”
- **Output (TaskOutput):** `result`, `usage?`, `total_cost_usd?`, `duration_ms?`.

So the SDK has a **first-class Task tool** that launches a subagent by `subagent_type` (matching a key in `agents`).

**Hooks**

- **SubagentStart** – `SubagentStartHookInput`: `hook_event_name: 'SubagentStart'`, `agent_id`, `agent_type`.
- **SubagentStop** – `SubagentStopHookInput`: `hook_event_name: 'SubagentStop'`, `stop_hook_active`.

So subagent lifecycle is observable and hookable in the SDK.

### 3.3 Comparison with Claude Code CLI

| Aspect | Claude Code CLI | Agent SDK |
|--------|------------------|-----------|
| **Subagent definition** | Via .claude config / UX | Programmatic: `options.agents` (AgentDefinition) |
| **Invoking a subagent** | Same Task tool (Claude Code built-in) | Same Task tool, driven via SDK (same runtime) |
| **Subagent lifecycle** | Internal to CLI | Exposed via hooks: SubagentStart, SubagentStop |
| **Control** | Interactive / config files | Full programmatic control (options, hooks, tools) |

Because the SDK **uses Claude Code as the runtime**, the Task/subagent behavior is the same as in the CLI; the SDK adds a programmatic API (agents map, hooks) and the same tool set. For **subagents specifically**, the Agent SDK provides **equal robustness** to the CLI, with the added benefit of defining and observing subagents in code (agents option + SubagentStart/SubagentStop hooks).

### 3.4 Caveats

- **Install:** The SDK still requires Claude Code to be installed; it drives the same executable.
- **Auth:** Same as Claude Code (e.g. `ANTHROPIC_API_KEY` or third-party providers via env).
- **Skills / slash commands / CLAUDE.md:** Available when using `settingSources: ['project']` (and optionally `systemPrompt: { type: 'preset', preset: 'claude_code' }`) so filesystem-based config is loaded.

**Sources:** [Agent SDK overview](https://docs.anthropic.com/en/docs/agent-sdk/overview), [Agent SDK TypeScript reference](https://docs.anthropic.com/en/docs/agent-sdk/typescript) (Options.agents, AgentDefinition, Task tool, SubagentStart/SubagentStop hooks).

---

## 4. Summary and recommendations

| Goal | Approach |
|------|----------|
| **Embedded CLIProxy in Go** | Add `github.com/router-for-me/CLIProxyAPI/v6/sdk/cliproxy` and optionally `internal/config`; build with `NewBuilder().WithConfig(cfg).WithConfigPath(...).Build()`; run with `svc.Run(ctx)`. Add middleware/routes/auth/hooks as needed. |
| **Claude setup reference** | Use `clean/deploy`: atoms-tech (frontend), atomsAgent (Python sandbox + Claude wrapper), mcp-atomsagent-integration (FastMCP + Claude SDK integration). Claude is used via Messages API + tools and Vercel Sandbox, not Claude Code CLI. |
| **Agent SDK vs Claude Code CLI (subagents)** | SDK uses Claude Code as runtime; subagents are supported the same way (Task tool). SDK adds programmatic subagent definitions (`agents`) and lifecycle hooks (SubagentStart, SubagentStop). **Validated:** Agent SDK provides equal robustness for subagents, with better programmatic control. |

---

## 5. References

| Topic | Link |
|--------|------|
| CLIProxyAPI SDK usage | https://github.com/router-for-me/CLIProxyAPI/blob/main/docs/sdk-usage.md |
| CLIProxyAPI repo | https://github.com/router-for-me/CLIProxyAPI |
| Agent SDK overview | https://docs.anthropic.com/en/docs/agent-sdk/overview |
| Agent SDK TypeScript (Options, Task, hooks) | https://docs.anthropic.com/en/docs/agent-sdk/typescript |
| Agent Skills (SDK + Claude Code) | https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview |
| clean/deploy atomsAgent | `485/clean/deploy` (from trace: `../../clean/deploy`) — atoms.tech, atomsAgent, mcp-atomsagent-integration |
