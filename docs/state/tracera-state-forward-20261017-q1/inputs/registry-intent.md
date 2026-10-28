---
repo: "Tracera"
aliases: ["tracera-server", "tracera-edge", "tracera-events"]
role: trace-and-observability-ledger
status: active
last_verified: 2026-09-20
bound_prompts: 2
bound_plans: 0
bound_responses: 1
device: homelab-koosh + macbook
---

# Intent — Tracera

## Intent Statement

Tracera exists to give the user (or another agent) the ability to look
across past agentic and LLM workflow runs and reason about what depends on
what. Concretely:

- If the user changes a spec, Tracera answers "which past sessions assumed
  this spec was in force?"
- If the user wants to learn from prior runs, Tracera distills a stable
  long-term memory entry the next session can load as context.
- If the user needs to audit who ran what and when, Tracera's ledger gives
  a per-workspace answer without needing a multi-tenant billing system.

Tracera is local-first. The CVP runs on the user's own machine (or one
homelab node). Cloud surfaces exist only for cross-device sync, fleet
discovery, and public sharing — not as the primary execution tier.

See [`docs/cvp/Tracera.md`](../cvp/Tracera.md) for the CVP definition
(this doc scopes Tracera; the CVP defines what to ship first).

## Bound Prompts

| Date       | Source | File                                                     | Tag                                                         |
| ---------- | ------ | -------------------------------------------------------- | ----------------------------------------------------------- |
| 2026-04-23 | codex  | `docs/curated-prompts/codex/2026-04/bb782500e06bf5d3.md` | bugfix                                                      |
| 2026-09-19 | user   | this session                                             | infra-cutover (Render → Vercel + Cloudflare Tunnel + fleet) |

## Bound Plans

| Date | Source | File | Status |
| ---- | ------ | ---- | ------ |

## Bound Responses (specs, ideas, plans from agents)

| Date | Source | File                                     | Kind |
| ---- | ------ | ---------------------------------------- | ---- |
| ?    | ?      | `e4047b4c9e4816f6.md` (not materialized) | ?    |

## Boundary

See: [`docs/boundary/Tracera.md`](../boundary/Tracera.md)

## Ecosystem Role

Tracera sits in the **observability layer** of the Phenotype stack:

```text
   agents / runtimes  (AgentMCP, agentapi, thegent, Jcode)
        │
        ▼
   trace + session ingest  (Tracera)           ← this repo
        │
        ▼
   memory + audit replay   (Tracera; phenodag queue is post-CVP / gated)
        │
        ▼
   cross-product dashboards (HeliosLab, PhenoObservability)
```

Tracera owns the _trace-link graph_ and _memory distillation_. It does
not own agent execution, code search, sprint planning, or product
analytics — those live in their respective repos.

See `ECOSYSTEM_MAP.md` for the canonical ecosystem role and the
`docs/cvp/Tracera.md` Anti-CVPs section for things that look like
Tracera but aren't.

## Open Questions

- Memory distillation canonical strategy (pattern-based vs graph-input).
- Cloudflare Tunnel Access policy for the public URL.
- Whether the Electrobun desktop's first CVP release ships with packaging
  polish (auto-update, code signing for distribution) or just the bare
  desktop binary.

## Change Log

| Date       | Change                                                                         | Worklog                                                    |
| ---------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| 2026-06-17 | Initial binding (L7-001 sweep)                                                 | `worklogs/L7-001-intent-boundary-curation-2026-06-17.json` |
| 2026-09-20 | Filled intent statement + ecosystem role; added Render → Vercel cutover prompt | this doc                                                   |
