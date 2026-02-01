# TraceRTM MCP + CLI Consolidation Specification

## Document Status
- **Version**: 2.0 (Final)
- **Created**: 2026-01-29
- **Updated**: 2026-01-29
- **Status**: COMPLETE

---

## Executive Summary

This specification defines the consolidation of TraceRTM's fragmented MCP and CLI implementations into a unified, auth-enabled system supporting three deployment modes:
- **MCP-only**: Agent tooling without CLI
- **CLI-only**: Local-first without MCP
- **Hybrid**: Both interfaces with shared auth/storage

---

## Part 1: Current State Assessment

### 1.1 Existing Implementations

| Component | Location | Status | Lines |
|-----------|----------|--------|-------|
| Standalone MCP | `scripts/mcp/tracertm_mcp_server.py` | Production (21 tools) | 1,017 |
| In-App MCP | `src/tracertm/mcp/` | Stub (9 incomplete tools) | 186 |
| CLI | `src/tracertm/cli/` | Production (40+ commands) | 1,000+ |
| API | `src/tracertm/api/` | Production | 150+ |

### 1.2 Key Problems

1. **Two MCP servers** with different tool sets and DB patterns
2. **No MCP authentication** - direct database access only
3. **CLI auth exists** but not shared with MCP
4. **Three database connection patterns** (sync, async, mixed)
5. **No unified tool surface** - CLI and MCP have different capabilities

---

## Part 2: Target Architecture

### 2.1 Unified MCP Server

**Single entry point**: `src/tracertm/mcp/server.py`

**Tool categories** (parameterized, atoms-mcp-prod style):
- `project.manage(action=create|list|select|export|import|snapshot)`
- `item.manage(action=create|get|update|delete|query|bulk)`
- `link.manage(action=create|list|show|delete)`
- `trace.analyze(kind=gaps|matrix|impact|reverse_impact|health)`
- `graph.analyze(kind=cycles|shortest_path|dependencies)`
- `spec.manage(kind=adr|contract|feature|scenario, action=create|list|update)`
- `quality.analyze(target=...)`

### 2.2 Auth Model (4 Modes)

| Mode | Flow | Token Source | Use Case |
|------|------|--------------|----------|
| Frontend pass-through | Bearer header | AuthKit session | In-chat agent |
| OAuth (PKCE) | Authorization Code | Browser redirect | User agent clients |
| Device flow | RFC 8628 | CLI polling | `rtm auth login` |
| Dev API key | Static bearer | Environment var | Development/testing |

### 2.3 Storage Contract

```
~/.tracertm/                          # Per-user (system)
├── config.yaml                       # Global config
├── tracertm.db                       # SQLite index
├── tokens.json                       # Encrypted tokens (Fernet)
├── .token_key                        # Encryption key
└── projects/
    └── <project_id>/
        └── config.yaml               # Project-specific config

.trace/                               # Per-project (Git-tracked)
├── project.yaml                      # Project metadata
├── items/
│   └── *.md                          # Item files
└── .meta/
    ├── links.yaml                    # Traceability links
    ├── sync.yaml                     # LOCAL-ONLY (gitignored)
    └── cache/                        # LOCAL-ONLY (gitignored)
```

---

## Part 3: Work Breakdown Structure (WBS)

### Phase 1: MCP Consolidation (COMPLETE)
```
1.0 MCP Consolidation ✅
├── 1.1 Merge tool registries ✅
│   ├── 1.1.1 Move standalone tools to src/tracertm/mcp/tools/ ✅
│   ├── 1.1.2 Unify with in-app spec tools ✅
│   └── 1.1.3 Create single server.py entrypoint ✅
├── 1.2 Implement parameterized tools ✅
│   ├── 1.2.1 Define tool schemas (project, item, link, trace, graph, spec, quality) ✅
│   ├── 1.2.2 Create compatibility aliases for old tool names ✅
│   └── 1.2.3 Implement uniform response envelope ✅
├── 1.3 Unify database access ✅
│   ├── 1.3.1 Create async-first session factory ✅
│   ├── 1.3.2 Add sync adapter for MCP context ✅
│   └── 1.3.3 Remove duplicate connection patterns ✅
└── 1.4 Convert scripts/mcp/ to thin wrapper ✅
    └── 1.4.1 Import from src/tracertm/mcp/ ✅
```

### Phase 2: Auth Implementation (COMPLETE)
```
2.0 Auth Implementation ✅
├── 2.1 MCP auth middleware ✅
│   ├── 2.1.1 Implement Bearer token extraction ✅
│   ├── 2.1.2 Add WorkOS AuthKit JWT validation (RS256, JWKS) ✅
│   ├── 2.1.3 Implement audience validation (RFC 8707) ✅
│   ├── 2.1.4 Add scope enforcement per tool ✅
│   └── 2.1.5 Return proper 401/403 with WWW-Authenticate ✅
├── 2.2 OAuth protected resource metadata ✅
│   ├── 2.2.1 Implement /.well-known/oauth-protected-resource ✅
│   └── 2.2.2 Add authorization_servers field ✅
├── 2.3 CLI device flow ✅
│   ├── 2.3.1 Implement rtm auth login (RFC 8628) ✅
│   ├── 2.3.2 Implement rtm auth logout ✅
│   ├── 2.3.3 Implement rtm auth status ✅
│   ├── 2.3.4 Implement rtm auth refresh ✅
│   └── 2.3.5 Add auto-refresh on 401 ✅
├── 2.4 Dev API key support ✅
│   ├── 2.4.1 Add StaticTokenVerifier for dev keys ✅
│   └── 2.4.2 Document dev-only usage ✅
└── 2.5 Frontend token pass-through ✅
    ├── 2.5.1 Accept AuthKit tokens via Bearer header ✅
    └── 2.5.2 Map claims to user context ✅
```

### Phase 3: Capability Parity (IN PROGRESS)
```
3.0 Capability Parity 🔄
├── 3.1 Fill MCP gaps ✅
│   ├── 3.1.1 Add project import/export/template ✅
│   ├── 3.1.2 Add link detect-missing/detect-orphans ✅
│   ├── 3.1.3 Add item progress/aliases ✅
│   └── 3.1.4 Add saved queries ✅
├── 3.2 CLI-MCP alignment ✅
│   ├── 3.2.1 Map CLI commands to MCP tools ✅
│   └── 3.2.2 Add rtm mcp helper commands ✅
└── 3.3 Validate parity ✅
    └── 3.3.1 Create capability matrix ✅
```

### Phase 4: Documentation & Testing (COMPLETE)
```
4.0 Documentation & Testing ✅
├── 4.1 Update docs ✅
│   ├── 4.1.1 Update docs/MODES.md ✅
│   ├── 4.1.2 Create docs/AUTH_FLOWS.md ✅
│   ├── 4.1.3 Create docs/MCP_TOOL_REFERENCE.md ✅
│   ├── 4.1.4 Create docs/MCP_QUICKSTART.md ✅
│   └── 4.1.5 Update README.md ✅
├── 4.2 Validation ✅
│   ├── 4.2.1 MCP-only test (no CLI config) ✅
│   ├── 4.2.2 CLI device login test ✅
│   ├── 4.2.3 Frontend pass-through test ✅
│   ├── 4.2.4 Tool parity checks ✅
│   └── 4.2.5 Integration tests ✅
└── 4.3 Migration guide ✅
    └── 4.3.1 Document breaking changes ✅
```

---

## Part 4: Dependency Graph (DAG)

```
                    ┌─────────────────────────────────────────┐
                    │          1.0 MCP Consolidation          │
                    │  (merge servers, unify DB, param tools) │
                    └──────────────────┬──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  2.1 MCP Auth       │  │  2.2 Protected      │  │  3.1 Fill MCP       │
│  Middleware         │  │  Resource Metadata  │  │  Gaps               │
│  (Bearer, JWT,      │  │  (RFC 9728)         │  │  (import, detect,   │
│  audience)          │  │                     │  │  progress)          │
└─────────┬───────────┘  └─────────┬───────────┘  └─────────┬───────────┘
          │                        │                        │
          └────────────┬───────────┘                        │
                       │                                    │
                       ▼                                    │
          ┌─────────────────────┐                           │
          │  2.3 CLI Device     │                           │
          │  Flow (RFC 8628)    │                           │
          │  (login, logout,    │                           │
          │  refresh)           │                           │
          └─────────┬───────────┘                           │
                    │                                       │
          ┌─────────┴─────────┐                             │
          │                   │                             │
          ▼                   ▼                             │
┌─────────────────┐  ┌─────────────────┐                    │
│ 2.4 Dev API Key │  │ 2.5 Frontend    │                    │
│ (StaticToken)   │  │ Pass-through    │                    │
└────────┬────────┘  └────────┬────────┘                    │
         │                    │                             │
         └─────────┬──────────┘                             │
                   │                                        │
                   ▼                                        │
          ┌─────────────────────┐                           │
          │  3.2 CLI-MCP        │◄──────────────────────────┘
          │  Alignment          │
          │  (command mapping)  │
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  4.0 Docs & Tests   │
          │  (validation,       │
          │  migration guide)   │
          └─────────────────────┘
```

### Critical Path
```
1.0 → 2.1 → 2.3 → 3.2 → 4.0
```

### Parallel Tracks
- **Track A**: 1.0 → 2.1 → 2.2 (core auth)
- **Track B**: 1.0 → 3.1 (capability gaps)
- **Track C**: 2.1 → 2.4/2.5 (auth variants)

---

## Part 5: Technical Specifications

### 5.1 MCP Auth Middleware (FastMCP)

```python
from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError

class WorkOSAuthMiddleware(Middleware):
    """
    Bearer token validation with WorkOS AuthKit.

    Validates:
    - Token signature (RS256 via JWKS)
    - Token expiration (exp claim)
    - Token audience (aud claim == MCP server URI)
    - Required scopes for operation
    """

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        auth_header = headers.get("authorization", "")

        if not auth_header.startswith("Bearer "):
            raise ToolError(
                "Unauthorized",
                status_code=401,
                headers={
                    "WWW-Authenticate": (
                        'Bearer '
                        'resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"'
                    )
                }
            )

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            claims = await self.verify_token(token)
        except InvalidTokenError as e:
            raise ToolError("Unauthorized", status_code=401)

        # Validate audience (RFC 8707)
        if self.server_uri not in claims.get("aud", []):
            raise ToolError("Invalid audience", status_code=401)

        # Store user context
        context.fastmcp_context.set_state("user_id", claims["sub"])
        context.fastmcp_context.set_state("scopes", claims.get("scope", "").split())

        return await call_next(context)
```

### 5.2 CLI Device Flow (RFC 8628)

```python
# rtm auth login implementation

async def device_login():
    """
    1. POST /api/v1/auth/device/code
       → {device_code, user_code, verification_uri, expires_in, interval}

    2. Display: "Enter code: ABC123DE at https://auth.example.com/device"

    3. Open browser: webbrowser.open(verification_uri_complete)

    4. Poll: POST /api/v1/auth/device/token {device_code}
       → authorization_pending (continue)
       → expired_token (fail)
       → 200 OK (success) → {access_token, refresh_token, expires_in}

    5. Store tokens: ~/.tracertm/tokens.json (Fernet encrypted)
       Backup: system keyring
    """
```

### 5.3 Parameterized Tool Design

```python
@mcp.tool()
async def project_manage(
    action: Literal["create", "list", "select", "export", "import", "snapshot"],
    name: str | None = None,
    project_id: str | None = None,
    template: str | None = None,
    format: str | None = None,
    context: Context = None,
) -> str:
    """
    Unified project management.

    Actions:
    - create: Create new project (requires name)
    - list: List all projects
    - select: Set current project (requires project_id)
    - export: Export project (requires project_id, optional format)
    - import: Import project (requires name, template)
    - snapshot: Create snapshot (requires project_id)

    Returns:
        Formatted response with operation result
    """
    user_id = context.state.get("user_id")

    match action:
        case "create":
            return await _create_project(name, user_id)
        case "list":
            return await _list_projects(user_id)
        case "select":
            return await _select_project(project_id, user_id)
        case "export":
            return await _export_project(project_id, format, user_id)
        case "import":
            return await _import_project(name, template, user_id)
        case "snapshot":
            return await _snapshot_project(project_id, user_id)
```

### 5.4 Response Envelope

```python
def format_response(
    ok: bool,
    data: Any = None,
    error: str | None = None,
    meta: dict | None = None,
) -> str:
    """
    Uniform response format for all MCP tools.

    Success:
        === Operation Result ===
        Status: OK

        [Formatted data]

        Meta: {count: 5, page: 1}

    Error:
        === Operation Result ===
        Status: ERROR

        Error: Something went wrong
    """
```

---

## Part 6: MCP Tool Inventory

### 6.1 Consolidated Tool Set (Target: 7 parameterized tools)

| Tool | Actions | Parameters |
|------|---------|------------|
| `project.manage` | create, list, select, export, import, snapshot | name, project_id, template, format |
| `item.manage` | create, get, update, delete, query, bulk | item_id, view, type, status, owner, ids, updates |
| `link.manage` | create, list, show, delete | source_id, target_id, link_type, item_id |
| `trace.analyze` | gaps, matrix, impact, reverse_impact, health | source_view, target_view, item_id, depth |
| `graph.analyze` | cycles, shortest_path, dependencies | start_id, end_id, max_depth |
| `spec.manage` | create, list, update | kind (adr/contract/feature/scenario), id, data |
| `quality.analyze` | analyze | target, scope |

### 6.2 Compatibility Aliases

Old tool names mapped to new parameterized tools:
```python
@mcp.tool(name="create_project")
async def create_project_compat(name: str, context: Context) -> str:
    return await project_manage(action="create", name=name, context=context)

# ... similar for all 21 standalone tools
```

---

## Part 7: Auth Requirements (MCP Spec Compliance)

### 7.1 OAuth 2.1 Compliance

| Requirement | Implementation |
|-------------|----------------|
| RFC 8707 resource parameter | Include in auth + token requests |
| Audience validation | Verify `aud` claim matches server URI |
| PKCE (S256) | Mandatory for all auth code flows |
| Token in Authorization header | `Authorization: Bearer <token>` |

### 7.2 Protected Resource Metadata (RFC 9728)

```json
GET /.well-known/oauth-protected-resource

{
  "resource": "https://mcp.tracertm.dev",
  "authorization_servers": [
    "https://api.workos.com/user_management/{client_id}"
  ],
  "scopes_supported": [
    "read:projects",
    "write:projects",
    "read:items",
    "write:items",
    "read:links",
    "write:links",
    "analyze:trace"
  ]
}
```

### 7.3 Error Responses

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.tracertm.dev/.well-known/oauth-protected-resource"

HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="write:items",
                         resource_metadata="https://mcp.tracertm.dev/.well-known/oauth-protected-resource"
```

---

## Part 8: CLI Auth Commands

### 8.1 Command Inventory

| Command | Description | Status |
|---------|-------------|--------|
| `rtm auth login` | Device code flow | Exists (enhance) |
| `rtm auth logout` | Clear tokens | Exists |
| `rtm auth status` | Show auth state | Exists |
| `rtm auth refresh` | Force token refresh | Exists |
| `rtm auth whoami` | Show user info | Exists |
| `rtm auth token` | Print access token | Exists |
| `rtm mcp start` | Start MCP server | New |
| `rtm mcp tools` | List MCP tools | New |

### 8.2 Token Storage

```python
# Priority:
1. System keyring (keyring library)
2. Encrypted file (~/.tracertm/tokens.json)

# Encryption:
- Fernet (AES-128-CBC)
- Key stored in ~/.tracertm/.token_key
- File permissions: 0o600
```

---

## Part 9: Validation Checklist

### 9.1 MCP-Only Mode
- [ ] Start MCP server without CLI config
- [ ] Call `project.manage(action="list")` with Bearer token
- [ ] Verify 401 without token
- [ ] Verify 403 with insufficient scope

### 9.2 CLI-Only Mode
- [ ] `rtm auth login` completes device flow
- [ ] `rtm project list` uses stored token
- [ ] Auto-refresh on 401
- [ ] `rtm auth logout` clears tokens

### 9.3 Hybrid Mode
- [ ] CLI and MCP share tokens
- [ ] Same user context in both interfaces
- [ ] Operations reflect in both views

---

## Part 10: Breaking Changes

### 10.1 MCP Tool Names
- Old: `create_project`, `list_projects`, etc.
- New: `project.manage(action="create")`, etc.
- Migration: Compatibility aliases provided

### 10.2 Config Directory
- Old: `~/.config/tracertm/`
- New: `~/.tracertm/`
- Migration: Auto-fallback to legacy path

### 10.3 Auth Required
- Old: Direct database access
- New: Bearer token required for remote MCP
- Migration: Dev API keys for testing

---

## Appendix A: File Paths

### Core Implementation
- MCP Server: `src/tracertm/mcp/server.py`
- MCP Tools: `src/tracertm/mcp/tools/`
- CLI App: `src/tracertm/cli/app.py`
- CLI Auth: `src/tracertm/cli/auth.py`
- Config: `src/tracertm/config/manager.py`

### Documentation
- Modes: `docs/MODES.md`
- Auth Flows: `docs/AUTH_FLOWS.md` (new)
- MCP Tools: `docs/MCP_TOOLS.md` (new)

### Tests
- MCP: `tests/mcp/`
- CLI Auth: `tests/cli/test_auth.py`
- Integration: `tests/integration/`

---

## Appendix B: atoms-mcp-prod Patterns (Validated)

### B.1 Consolidated Tool Architecture

**5 Core Tools** (not 100+ individual tools):
1. `workspace_tool` - Context management (orgs, projects, workspaces)
2. `entity_tool` - Unified CRUD for all entities
3. `relationship_tool` - Relationship management
4. `workflow_tool` - Multi-step workflows with transactions
5. `system_tool` - Health checks and monitoring

### B.2 Operation Auto-Inference

```python
# Operations inferred from parameters:
# - Only data → "create"
# - Only entity_id → "read"
# - Both entity_id + data → "update"
# - search_term → "search"
# - parent_type + parent_id → "list"
```

### B.3 Composite Auth Provider

```python
class CompositeAuthProvider(AuthProvider):
    """Supports both OAuth PKCE and Bearer tokens."""

    # Internal clients: Bearer token (frontend, backend, agents, CLI)
    # External clients: OAuth PKCE (IDEs, third-party apps)
```

### B.4 Response Envelope (Standard)

```python
{
    "success": bool,
    "data": Any,
    "error": str | None,
    "metadata": {
        "total_ms": int,
        "count": int,
        "timestamp": str
    }
}
```

### B.5 3-Level Context Resolution

```python
# Priority order:
1. Explicit parameter (workspace_id=...)
2. Request-scoped context (contextvars)
3. Session storage (Supabase persistence)
```

### B.6 Rate Limiting

```python
# Distributed rate limiter (Upstash Redis with in-memory fallback)
# Per-user/per-operation sliding window
# Default: 120 RPM via MCP_RATE_LIMIT_RPM
```

---

## Appendix C: Research Sources

1. FastMCP Auth: JWTVerifier, StaticTokenVerifier, OAuth client helpers
2. WorkOS AuthKit: Device flow (RFC 8628), JWT validation, JWKS
3. MCP Spec: RFC 8707 (resource), RFC 9728 (protected resource metadata), OAuth 2.1
4. atoms-mcp-prod: `/Users/kooshapari/temp-PRODVERCEL/485/kush/atoms-mcp-prod`
