# API Reference

> **Recovered June 2026.** Restored from git history (`9e78f48dd^`) and repointed to the current thin-service
> contract. The legacy `api-documentation.md` / `workflows.md` siblings from the pre-consolidation tree are
> not restored; use the maintained references below instead.

Complete API documentation for the Tracera HTTP service.

## Current contract (June 2026)

The audit-facing API slice is **24 business routes + 2 operational probes**. As of June 2026:

| Status | Count | Notes |
|--------|------:|-------|
| Mounted | **17** | Exposed via `src/tracertm/api/main.py` |
| Unmounted | **8** | Router code present; not yet included in main mounts |
| Probes | **2** | `GET /health`, `GET /ready` (no auth) |

Authoritative lists:

- **[`../API_REFERENCE.md`](../API_REFERENCE.md)** — endpoint paths grouped by domain
- **[`../governance/policy/endpoint_traceability_map.md`](../governance/policy/endpoint_traceability_map.md)** — FR→route→test matrix

## Quick navigation

| Resource | Content |
|----------|---------|
| [API endpoint list](../API_REFERENCE.md) | All `/api/v1` paths |
| [Endpoint traceability](../governance/policy/endpoint_traceability_map.md) | Mounted vs unmounted + test linkage |
| [Quickstart](../quickstart.md) | Bootstrap, JWT env, smoke curls |
| [MCP/CLI/API matrix](../04-guides/mcp-cli-api-matrix.md) | How clients map to HTTP |
| [Feature inventory](../FEATURE_INVENTORY.md) | FR catalog backing the endpoint map |

## Authentication

All `/api/v1/*` routes require a bearer JWT unless noted otherwise in the quickstart. Set:

```bash
export TRACERA_JWT_SECRET=<production-secret>
export TRACERA_JWT_AUDIENCE=tracera-api
export TRACERA_JWT_ISSUER=tracera
```

## Related documentation

- **Architecture**: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Developer workflow**: [`../04-guides/DEVELOPER_GUIDE.md`](../04-guides/DEVELOPER_GUIDE.md)
- **Deployment**: [`../04-guides/DEPLOYMENT_GUIDE.md`](../04-guides/DEPLOYMENT_GUIDE.md)

---

**Last updated**: 2026-06-26 (recovery pass)  
**Scope**: HTTP API specifications for the thin Tracera service
