---
repo: "Tracera"
aliases: ["tracera-server", "tracera-edge", "tracera-events"]
role: trace-and-observability-ledger
status: active
last_boundary_review: 2026-09-20
review_cadence: 30d
in_scope:
  - "Trace-link capture (session → spec → tool → output graph)"
  - "Cross-run reasoning (impact / blast-radius / confidence queries)"
  - "Memory distillation (short-term → long-term memory entries)"
  - "Local-first persistence (SQLite + WAL for one-user workspace)"
  - "Fleet enrollment + reporting for homelab nodes (one-node CVP)"
  - "Cloudflare Edge Worker for fleet discovery + Tunnel proxy"
  - "Electrobun desktop viewer (single-user, no multi-tenant billing)"
  - "Web UI (Vite + React) talking to local or same-origin backend"
out_of_scope:
  - capability: "Multi-tenant WorkOS auth (CVP is single-user local)"
    lives_in: "post-CVP; deferred until shared workspaces ship"
  - capability: "Cloud D1/R2 persistence (SQLite is enough for CVP)"
    lives_in: "post-CVP"
  - capability: "ML inference pipelines (Neo4j, RAG, ML adapters)"
    lives_in: "crates/tracera-ml, crates/tracera-rag, crates/tracera-neo4j — gated"
  - capability: "Multi-node fleet orchestration"
    lives_in: "crates/tracera-cli, crates/tracera-go-cli — post-CVP"
  - capability: "GitHub/Jira/AgilePlus ingestion"
    lives_in: "crates/tracera-server/src/ingest/ — post-CVP"
  - capability: "phenodag queue absorption surface"
    lives_in: "crates/tracera-server — gated behind phenodag-queue feature flag"
  - capability: "Branded multi-tenant hosting on pheno.studio"
    lives_in: "deploy/selfhost + cloudflared config — post-CVP"
---

# Boundary — Tracera

## In Scope

The Tracera boundary is the **trace-link graph** and the **memory
distillation pipeline** that feeds the next session. Everything in the
in-scope list is part of the CVP or directly supports it. Everything else
in the repository either feeds one of these or is post-CVP.

For the canonical CVP definition, see [`docs/cvp/Tracera.md`](../cvp/Tracera.md).

## Out of Scope

| Not here                                                      | Lives in                                                          | Reason                                                                                  |
| ------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Multi-tenant WorkOS auth (WorkOS integration code is present) | `crates/tracera-workos` (gated)                                   | CVP is single-user local; shared workspaces are post-CVP                                |
| ML inference / Neo4j / RAG                                    | `crates/tracera-ml`, `crates/tracera-neo4j`, `crates/tracera-rag` | CVP runs on SQLite + heuristic distillation only                                        |
| Multi-node fleet orchestration                                | `crates/tracera-cli`, `crates/tracera-go-cli`                     | CVP enrolls one node; fleet-of-fleets is post-CVP                                       |
| GitHub/Jira/AgilePlus ingest                                  | `crates/tracera-server/src/ingest/`                               | CVP captures sessions manually or from local agents; remote-platform ingest is post-CVP |
| phenodag queue absorption                                     | `crates/tracera-server` (feature flag)                            | Opt-in until HTTP/service wiring is complete                                            |
| Custom-domain Tracera hosting                                 | `deploy/selfhost/`, `cloudflared config`                          | CVP runs locally; CF Tunnel publish exists but isn't branded                            |
| Agent execution                                               | `AgentMCP`, `agentapi`, `thegent`, `Jcode`                        | Tracera observes, doesn't execute                                                       |
| Code search                                                   | `HeliosLab`                                                       | Different indexing domain (source vs traces)                                            |
| Sprint planning                                               | `AgilePlus`                                                       | Tracera captures _what happened_, not _what to do_                                      |
| Cross-product analytics dashboards                            | `HeliosLab`, `PhenoObservability`                                 | Tracera's audit is per-workspace, not cross-org                                         |

## Boundary Crossings

| Crossing                   | Direction                                  | Surface                                              | Status                                                                  |
| -------------------------- | ------------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------------- |
| Trace-link capture ingest  | agent → Tracera                            | HTTP POST `/api/v1/trace`                            | green (Rust server)                                                     |
| Cross-run queries          | UI → Tracera                               | HTTP POST `/api/v1/{impact,confidence,blast-radius}` | green (Rust server)                                                     |
| Memory distillation        | in-process                                 | internal API                                         | green (Rust server, pattern strategy)                                   |
| Fleet enrollment           | local node → edge                          | HTTP POST `/fleet/enroll`                            | green (Cloudflare Worker + sidecar)                                     |
| Fleet status report        | local node → edge                          | HTTP POST `/fleet/heartbeat`                         | green                                                                   |
| Live API path (production) | Vercel frontend → CF Tunnel → local server | HTTP `https://tracera.pheno.studio/api/*`            | red (proxy mode lands once Rust server is reachable through the tunnel) |
| Edge cache reads           | CF Worker → KV                             | internal                                             | amber (KV not yet populated)                                            |
| WebSocket realtime sync    | UI → server                                | `ws(s)://.../ws`                                     | amber (server impl exists; UI wiring TBD)                               |
| MCP server interface       | external → Tracera                         | MCP stdio/HTTP                                       | red (post-CVP; `crates/tracera-mcp/` scaffolded)                        |

## Last Boundary Review

**Date:** 2026-09-20
**Reviewer:** jcode (this session)
**Decisions:**

- Drew the boundary around the trace-link graph + memory distillation
  pipeline. These are the two things that distinguish Tracera from
  generic observability.
- Multi-node fleet orchestration, ML inference, and remote-platform
  ingest are explicitly post-CVP. Their code exists in the repo but
  stays ungated or feature-flagged until the CVP ships.
- The Vercel catch-all (`api/[...path].ts`) is a stub-or-proxy boundary
  crossing. It's the Vercel-hosted frontend's path to either stubs (now)
  or the live Rust server (once the proxy target is reachable).
- The Cloudflare Edge Worker is the federation boundary. Fleet discovery,
  enrollment, and (eventually) Tunnel-origin proxy all live there.

**Next review:** 2026-10-20
