# ADR-0002: FastMCP 2.14+ Integration

**Status:** Accepted
**Date:** 2026-01-28
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM requires AI-native tooling to enable conversational interaction with the traceability system. The system needs:

1. **Structured tool interface** for AI assistants (Claude, ChatGPT)
2. **Resource access** to traceability data (requirements, tests, links)
3. **Prompt templates** for common workflows
4. **Type-safe** parameter validation
5. **Multiple transport options** (stdio for desktop, HTTP for web)

AI assistants need standardized protocols to interact with domain-specific tools. The Model Context Protocol (MCP) is Anthropic's open standard for this purpose.

## Decision

We will use **FastMCP 2.14+** as the primary MCP server implementation for TraceRTM.

## Rationale

### FastMCP Advantages

- **Production-ready**: FastMCP 2.14+ is production-stable, actively maintained by Anthropic
- **Pythonic API**: Decorator-based tool/resource/prompt registration matches TraceRTM's Python stack
- **Type validation**: Pydantic-based parameter schemas with automatic validation
- **Transport flexibility**: Supports stdio (Claude Desktop), HTTP (web clients), SSE (streaming)
- **Auto-documentation**: Tool schemas auto-generate from type hints
- **Async-first**: Native async/await support for database operations

### Technology Stack Alignment

```python
# pyproject.toml dependencies
dependencies = [
    "fastmcp>=3.0.0b1",  # Latest FastMCP version
    "mcp>=1.26.0",       # Core MCP protocol
    "pydantic>=2.12.5",  # Type validation
    "fastapi>=0.115.0",  # HTTP transport (when needed)
]
```

### Integration Pattern

```python
# src/tracertm/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP("TraceRTM", version="2.0.0")

@mcp.tool
async def create_requirement(
    title: str,
    description: str,
    priority: Literal["low", "medium", "high", "critical"] = "medium",
) -> dict:
    """Create a new requirement with traceability metadata."""
    # Service layer call
    result = await requirement_service.create(...)
    return result.model_dump()

@mcp.resource("tracertm://projects/{project_id}/coverage")
async def get_coverage_report(project_id: str) -> str:
    """Get test coverage report for a project."""
    coverage = await coverage_service.calculate(project_id)
    return coverage.to_markdown()
```

## Alternatives Rejected

### Alternative 1: Vanilla MCP (anthropic/mcp)

- **Description:** Use the low-level MCP SDK directly
- **Pros:** Maximum flexibility, no framework abstraction
- **Cons:** Requires manual transport handling, parameter validation, tool registration boilerplate
- **Why Rejected:** FastMCP provides all needed features with less code. No advantage to low-level control.

### Alternative 2: LangChain Tools

- **Description:** Expose TraceRTM as LangChain tools via LCEL
- **Pros:** LangChain ecosystem integration, agent orchestration
- **Cons:** Heavy dependency (600+ transitive deps), vendor lock-in, not Claude-native
- **Why Rejected:** MCP is protocol-level (works with any MCP client), LangChain is framework-level. MCP is lighter weight and interoperable.

### Alternative 3: Custom REST API + OpenAPI

- **Description:** Build REST API with OpenAPI schema for AI tool use
- **Pros:** Standard HTTP, OpenAPI tooling, language-agnostic
- **Cons:** No streaming, no stateful conversations, AI must construct HTTP calls manually
- **Why Rejected:** MCP provides conversation context, streaming, and better AI integration than REST. REST API remains for traditional clients.

### Alternative 4: Function Calling via API (no MCP)

- **Description:** AI calls TraceRTM REST API directly with function calling
- **Pros:** No new protocol, reuses existing API
- **Cons:** No resource access pattern, no prompt templates, no conversation context
- **Why Rejected:** MCP resources/prompts are critical for complex workflows. Function calling alone is insufficient.

## Consequences

### Positive

- **AI-native workflows:** Claude can directly manipulate traceability data via conversation
- **Type safety:** Pydantic validation prevents invalid tool calls
- **Discoverability:** AI sees tool descriptions, parameters, and examples automatically
- **Transport flexibility:** stdio for desktop, HTTP for web, SSE for real-time
- **Reduced integration effort:** FastMCP handles protocol details, server can focus on domain logic
- **Streaming support:** Server-Sent Events (SSE) for progress updates on long-running operations

### Negative

- **New protocol:** Teams unfamiliar with MCP have learning curve
- **Dependency:** Tied to FastMCP library (though MCP protocol is open standard)
- **Dual API surface:** Must maintain both REST API (traditional clients) and MCP server (AI clients)
- **Transport limitations:** stdio requires desktop app (Claude Desktop), HTTP requires CORS/auth handling

### Neutral

- **Authentication:** MCP server uses same auth as REST API (JWT/WorkOS)
- **Deployment:** MCP server runs alongside FastAPI backend (shared process or separate service)
- **Monitoring:** MCP tool calls logged via structured logging (same as REST endpoints)

## Implementation

### Affected Components

- `src/tracertm/mcp/server.py` - Main FastMCP server
- `src/tracertm/mcp/tools/` - Tool implementations (requirements, tests, coverage, etc.)
- `src/tracertm/mcp/resources/` - Resource providers (projects, graphs, reports)
- `src/tracertm/mcp/prompts/` - Prompt templates (BDD scenarios, ADR creation, etc.)
- `src/tracertm/services/` - Service layer (shared with REST API)

### Migration Strategy

**Phase 1: Core Tools (Week 1-2)**
- Implement CRUD tools for requirements, test cases, links
- Resource providers for projects, coverage reports
- stdio transport for Claude Desktop

**Phase 2: Advanced Tools (Week 3-4)**
- Impact analysis, graph queries, scenario execution
- Prompt templates for common workflows
- HTTP transport for web clients

**Phase 3: Integration (Week 5-6)**
- TUI integration (Claude Code + TraceRTM MCP)
- Web UI integration (MCP-over-HTTP)
- Documentation and examples

### Rollout Plan

- **Phase 1:** Beta release with stdio transport, core tools only
- **Phase 2:** HTTP transport, web client integration
- **Phase 3:** General availability, all tools/resources/prompts

### Success Criteria

- [x] 20+ tools covering all major TraceRTM operations
- [x] 10+ resources for data access (projects, coverage, graphs)
- [x] 5+ prompt templates for workflows (BDD, ADR, coverage analysis)
- [x] stdio transport working with Claude Desktop
- [ ] HTTP transport working with web clients (pending Phase 2)
- [ ] <100ms latency for simple tools (get_requirement)
- [ ] <5s latency for complex tools (analyze_impact)

## References

- [FastMCP Documentation](https://github.com/anthropics/fastmcp)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [ADR-0001: TraceRTM v2 Architecture](ADR-0001-tracertm-v2-architecture.md)
- [Implementation: src/tracertm/mcp/](../../src/tracertm/mcp/)

---

**Notes:**
- Transport choice (stdio vs HTTP) determined by client environment
- stdio: Claude Desktop, local CLI tools
- HTTP: Web clients, remote integrations, multi-user deployments
- All tools must be idempotent (safe to retry) due to network/transport failures
