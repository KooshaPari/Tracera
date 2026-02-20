# Agent System Implementation Plan

In-depth plan for the Trace agent system: per-session chat persistence, filesystem sandboxing, and AI execution (Claude / Codex via CLIProxy). Adapted from atomsAgent where applicable; integrated with Trace’s existing Python backend and AIService.

---

## 1. Goals and Constraints

| Goal | Constraint |
|------|-------------|
| Per-session chat persistence | Chat/session ID ties to a sandbox path; store persists with chat (DB or in-memory initially). |
| Per-session filesystem sandboxing | One sandbox root per session; tools (read_file, write_file, run_command) run under that root. |
| AI execution | Primary: existing AIService (Anthropic Messages API + tools). Future: Claude Code → Codex via CLIProxy OAuth. |
| Reuse atomsAgent patterns | Copy/adapt sandbox types, execution request/result, agent orchestration; swap Vercel Sandbox for local FS or keep Vercel as optional backend. |

---

## 2. Reference: atomsAgent (clean/deploy)

**What we reuse (conceptually or by copy):**

| Component | Location (atomsAgent) | Use in Trace |
|-----------|------------------------|--------------|
| **SandboxConfig** | `sandbox/types.py` | Copy and adapt: add `sandbox_root` for local FS; keep vcpus/memory/timeout for future Vercel. |
| **SandboxMetadata**, **SandboxStatus** | `sandbox/types.py` | Copy; status lifecycle applies to both Vercel and local sandboxes. |
| **ExecutionRequest** / **ExecutionResult** | `sandbox/types.py` | Copy; prompt, tools, config, result status/output. |
| **SandboxManager** (abstract) | `sandbox/manager.py` | **Replace** with a **SandboxProvider** interface: `create_sandbox`, `execute_command`, `write_file`, `cleanup_sandbox`. Implement **LocalFilesystemSandbox** first. |
| **SandboxClaudeWrapper** | `services/sandbox_claude_wrapper.py` | **Do not copy** as-is (uses Claude Code `create_agent`). In Trace we use **AIService** with `working_directory` = session sandbox path. |
| **SandboxAgent** | `services/sandbox_agent.py` | **Adapt**: orchestration only — get/create session sandbox, call AIService (or future Codex path) with `working_directory`; optionally install deps in sandbox. |
| **OIDCAuthManager** | `sandbox/auth.py` | Use only when adding **Vercel Sandbox** as a second provider; not required for local FS. |

**What we do not copy:**

- Vercel Sandbox API calls (manager.py HTTP calls): replaced by local FS or optional later Vercel provider.
- Claude Code CLI / `create_agent` (SandboxClaudeWrapper): Trace uses Messages API via AIService; Codex path later via CLIProxy + Claude Code or Gateway.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Frontend (React)                                                            │
│  Chat UI → POST /api/v1/chat/stream (messages, provider, session_id?)       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  API (FastAPI)                                                              │
│  stream_chat: resolve session_id → sandbox path; pass to AgentService       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AgentService (new)                                                          │
│  • get_or_create_session_sandbox(session_id) → working_directory            │
│  • stream_chat_with_sandbox(messages, session_id, provider, …)               │
│    → AIService.stream_chat(..., working_directory=session_sandbox_path)     │
│  • Optional: future codex path via CLIProxy / Claude Code                    │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────────────────────────┐
│  SessionSandboxStore │            │  AIService (existing)                   │
│  session_id → path   │            │  stream_chat_with_tools_streaming(      │
│  (in-memory or DB)   │            │    working_directory=session_path      │
└─────────────────────┘            │  )                                      │
         │                          └─────────────────────────────────────────┘
         ▼
┌─────────────────────┐
│  SandboxProvider     │
│  (interface)         │
│  • LocalFSProvider   │  ← first implementation: mkdir per session under base
│  • (VercelProvider)  │  ← optional later: delegate to atomsAgent-style manager
└─────────────────────┘
```

---

## 4. Component Design

### 4.1 Sandbox types (`tracertm.agent.types`)

- **SandboxStatus**: `creating | ready | executing | completed | failed | cleaning_up | cleaned` (same as atomsAgent).
- **SandboxConfig**: `vcpus`, `memory_mb`, `timeout_seconds`, `max_turns`, `environment`, `dependencies`; add `sandbox_root: Optional[str]` for local FS (assigned by provider when null).
- **SandboxMetadata**: `sandbox_id`, `status`, `created_at`, `started_at`, `completed_at`, `sandbox_root` (path for local FS), optional `vcpus`/`memory_mb`/`timeout_seconds` for Vercel.
- **ExecutionRequest**: `prompt`, `tools`, `config: SandboxConfig`, `context`, `max_retries` (same idea as atomsAgent).
- **ExecutionResult**: `sandbox_id`, `status`, `output`, `metadata`, `error`, `execution_time_ms`, `tokens_used`.

### 4.2 SandboxProvider interface (`tracertm.agent.sandbox.base`)

```python
class SandboxProvider(Protocol):
    async def create_sandbox(self, config: SandboxConfig, session_id: str) -> SandboxMetadata: ...
    async def execute_command(self, sandbox_id: str, command: str) -> dict: ...
    async def write_file(self, sandbox_id: str, path: str, content: str) -> dict: ...
    async def cleanup_sandbox(self, sandbox_id: str) -> bool: ...
```

- **LocalFilesystemSandboxProvider**: base_dir (e.g. env `AGENT_SANDBOX_BASE_DIR` or default under temp). `create_sandbox`: mkdir `base_dir / session_id`, return metadata with `sandbox_root` = that path. `execute_command`: subprocess in `sandbox_root`. `write_file`: write under `sandbox_root`. `cleanup_sandbox`: optional delete or leave for persistence.

### 4.3 SessionSandboxStore (`tracertm.agent.session_store`)

- **Purpose**: Map `session_id` → sandbox path (and optional SandboxMetadata) so that chat stream and tools use the same root for the lifetime of the session.
- **Implementation**: In-memory dict first: `session_id -> { "sandbox_id", "sandbox_root", "created_at" }`. Later: persist in DB (e.g. chat or agent_session table) and/or TTL cleanup.
- **API**: `get_or_create(session_id, config?) → sandbox_root`, `get(session_id) → metadata | None`, `delete(session_id)`.

### 4.4 AgentService (`tracertm.agent.agent_service`)

- **get_or_create_session_sandbox(session_id, config?)**: Uses SessionSandboxStore + SandboxProvider to return `working_directory` (path) for the session. If no session_id, return None (current behavior: no per-session sandbox).
- **stream_chat_with_sandbox(messages, session_id, provider, model, system_prompt, max_tokens, db_session)**:
  - Resolve `working_directory` via `get_or_create_session_sandbox(session_id)`.
  - Call `get_ai_service().stream_chat(..., working_directory=working_directory, ...)` and yield SSE chunks.
- **simple_chat_with_sandbox(...)**: Same resolution, then `ai_service.simple_chat(...)`.
- **Future**: Optional `stream_chat_via_codex(session_id, ...)` that uses CLIProxy + Claude Code with session sandbox path; not in initial scope.

### 4.5 API wiring

- **Request**: Add optional `session_id` (or `chat_id`) to `ChatRequest` in `tracertm.schemas.chat`. If present, `stream_chat` and `simple_chat` pass it to AgentService.
- **Flow**: `stream_chat` → AgentService.stream_chat_with_sandbox(messages, session_id=request_body.session_id, ...) → AIService with `working_directory` set when session_id is present.
- **Tools**: Existing ai_tools (read_file, write_file, run_command) already respect `working_directory`; no change except that it is now the session sandbox path when session_id is provided.

---

## 5. What to Copy from atomsAgent (file-level)

| Copy | From | To |
|------|------|----|
| Types (adapt) | `atomsAgent/sandbox/types.py` | `tracertm/agent/types.py` — add `sandbox_root` to SandboxMetadata/SandboxConfig where needed. |
| Execution request/result | Same | Same file. |
| Manager logic | `atomsAgent/sandbox/manager.py` | **Do not copy**; implement SandboxProvider + LocalFilesystemSandboxProvider from scratch. |
| Auth | `atomsAgent/sandbox/auth.py` | Omit until Vercel Sandbox is added. |
| SandboxAgent orchestration pattern | `atomsAgent/services/sandbox_agent.py` | `tracertm/agent/agent_service.py` — orchestration only, no Claude wrapper; call AIService. |
| SandboxClaudeWrapper | atomsAgent | **Do not copy**; Trace uses AIService. |

---

## 6. Per-Session Persistence and Sandbox Lifetime

- **Persistence**: Session → sandbox path is stored in SessionSandboxStore (in-memory first). Optionally persist `session_id` ↔ `sandbox_root` in DB with chat/conversation so it survives restarts.
- **Sandbox lifetime**: For local FS, sandbox dir can persist with the chat (long-lived). Cleanup can be TTL-based or on explicit “end session” action. For Vercel Sandbox (future), keep atomsAgent-style create → execute → cleanup per request or per session depending on product choice.
- **Chat persistence**: Existing chat/message storage (if any) unchanged; only addition is linking chat/session to a sandbox path for tool execution.

---

## 7. Codex / CLIProxy (future)

- **Routing to Codex**: Claude Code (or Agent SDK) can be pointed at CLIProxy (or embedded CLIProxy in Go) via `ANTHROPIC_BASE_URL` + auth; CLIProxy translates to OpenAI/Codex. User signs in with OpenAI/Anthropic OAuth; backend passes user token per request (BYOK).
- **Trace backend**: Either (1) keep Python AIService and add a “codex” provider that calls an internal or external CLIProxy URL with user token, or (2) run Claude Code as a subprocess with env pointing at CLIProxy and `working_directory` = session sandbox path (similar to ai-sdk-provider-codex-cli). Plan does not implement this in Phase 1.

---

## 8. Implementation Phases

| Phase | Deliverable |
|-------|-------------|
| **1** | Types in `tracertm.agent.types`; SandboxProvider interface + LocalFilesystemSandboxProvider; SessionSandboxStore (in-memory); AgentService (get_or_create_session_sandbox, stream_chat_with_sandbox delegating to AIService). |
| **2** | ChatRequest.session_id; wire stream_chat/simple_chat to AgentService when session_id present; ensure ai_tools use working_directory. |
| **3** | (Optional) Persist session → sandbox in DB; TTL or explicit cleanup. |
| **4** | (Optional) Vercel Sandbox as second SandboxProvider; OIDC auth. |
| **5** | (Optional) Codex path: CLIProxy + Claude Code or Gateway with OAuth. |

---

## 9. File Layout (Trace)

```
src/tracertm/
  agent/
    __init__.py
    types.py           # SandboxConfig, SandboxMetadata, ExecutionRequest, ExecutionResult, SandboxStatus
    sandbox/
      __init__.py
      base.py          # SandboxProvider protocol
      local_fs.py      # LocalFilesystemSandboxProvider
    session_store.py   # SessionSandboxStore
    agent_service.py   # AgentService
  services/
    ai_service.py      # unchanged; used with working_directory from AgentService
  api/
    main.py            # stream_chat uses AgentService when session_id present
  schemas/
    chat.py            # add session_id to ChatRequest
```

---

## 10. Backing by DB, Redis, Neo4j, NATS, Temporal, S3/MinIO

The agent system is backed by the same infrastructure as the rest of Trace: **DB (PostgreSQL), Redis, Neo4j, NATS, Temporal, and S3/MinIO** where relevant.

| Resource | Role in agent system |
|----------|----------------------|
| **DB (PostgreSQL)** | Persist `agent_sessions`: `session_id`, `sandbox_root`, optional `project_id`, `created_at`, `updated_at`. SessionSandboxStoreDB uses PostgreSQL so session → sandbox survives restarts and is queryable. |
| **Redis** | Session lookup cache: hot path `session_id` → `sandbox_root` (key `tracertm:agent:session:{session_id}`, TTL e.g. 1h). Optional: rate limiting, ephemeral agent state, message-history cache. Uses existing `CacheService`. |
| **Neo4j** | Optional: link agent sessions to the graph (e.g. session → project, session → items touched). Go backend already uses Neo4j for graph; Python can call Go API or a future small Neo4j client to record session nodes/edges. Not required for Phase 1. |
| **NATS** | Publish agent events for real-time UI and cross-service coordination: `agent.session.created`, optional `agent.chat.progress` / `agent.execution.completed`. EventBus (NATSClient) is initialized in `main.py`; AgentService accepts an optional `event_bus` and publishes when a new session sandbox is created. |
| **Temporal** | **Checkpointing**: long-running agent runs can be executed as a Temporal workflow. Each “turn” (user message + model response + tools) is an activity; workflow state (message history, sandbox ref) is durable so runs survive restarts and can resume. Use for multi-step agent jobs and scheduled/replay flows. |
| **S3 / MinIO** | Object storage for large agent outputs and sandbox snapshots. Preflight already expects `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET` (MinIO-compatible). Execution artifact storage is currently local (`ArtifactStorageService`); agent can use the same pattern and add an S3 backend later (e.g. upload sandbox tarballs or artifact blobs to S3/MinIO). |

### 10.1 Temporal and checkpointing

- **Temporal** is used for durable workflows; it naturally provides **checkpointing** (workflow state is persisted after each step).
- Agent run as a workflow: input = `session_id`, initial `messages` (or pointer to DB/stream). Each turn = one activity (call AIService or tool runner). Workflow state = current message list + sandbox path; if the worker dies, Temporal replays and resumes.
- Optional: store large payloads (e.g. full message history) in DB or S3 and pass only keys in workflow args.

### 10.2 Redis usage

- **Session lookup cache**: `SessionSandboxStoreDB` accepts an optional `CacheService`. On `get_or_create`, check Redis key `tracertm:agent:session:{session_id}` first; on hit return `(sandbox_root, False)`. On miss, resolve from DB/store, then set Redis with TTL (e.g. 3600s). Reduces DB load for hot sessions. Same Redis as `CacheService` (items, graph, impact, etc.).
- **Optional**: Rate limiting (per-session keys), ephemeral agent state, or message-history cache can use the same Redis.

### 10.3 S3 / MinIO usage

- **Yes**, S3 (or MinIO) is in the stack: preflight checks `S3_*`; the codebase has S3-style upload/download in the OpenAPI surface. Execution artifacts are currently on local disk; agent artifacts (sandbox backups, large outputs) can be written to S3/MinIO when that backend is enabled (same env vars).

---

## 11. Database migration

When the database is available, run the agent sessions migration so the API can persist sessions:

```bash
# From project root, with DB URL configured (e.g. in .env or DATABASE_URL)
python -m alembic upgrade head
```

Revision `052_add_agent_sessions` adds the `agent_sessions` table (`session_id`, `sandbox_root`, `project_id`, `created_at`, `updated_at`). If PostgreSQL is not running or the role does not exist, the command will fail; run it once the DB is set up.

---

## 12. References

- Research: `docs/research/EMBEDDED_CLIPROXY_AND_AGENT_SDK_RESEARCH.md`
- Research: `docs/research/VERCEL_AI_SDK_CODEX_OAUTH_RESEARCH.md`
- Reference: `485/clean/deploy` (atomsAgent, mcp-atomsagent-integration)
