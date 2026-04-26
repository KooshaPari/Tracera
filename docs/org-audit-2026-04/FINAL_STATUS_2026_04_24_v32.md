# Wave-76 Final Status (v32) — 2026-04-24

## Deltas vs v31

### Async Instrumentation Expansion
- **async_instrumented macro** broadened (commit 03c999b) to accept `anyhow::Result` + custom Result aliases
- FocalPoint Observably now covers ~39 instrumented async functions across 7 crates

### Focus-Rituals Wave-2
- 2 macros: `generate_weekly_review`, `generate_monthly_retro` (commit 1688a34)
- Clean verification pass (commit 5333d02)

### Connector-Canvas Wave-2
- 6 macros: `refresh_client_token`, `try_token_refresh`, `drain_paginated`, `list_courses`, `list_assignments`, `list_submissions`
- Clean verification pass (commit 5333d02)

### Connector-Strava + Focus-Always-On Wave-3
- 7 macros total (commit 00b1561)
- Path fixes applied; `drain_paginated()` FnMut generic removed (incompatibility with macro)

### Documentation & Release
- **phenotype-observably-macros** README + USAGE.md cookbook published — FocalPoint adoption lessons codified
- **KDesktopVirt v0.2.1** SHIPPED (commit 942a24e, tag pushed, GitHub release live)
  - 12→4 advisory cleanup included

### Known Gaps
- **AgentMCP**: pack corruption RESOLVED but branches now divergent — manual rebase/merge required
- **AgilePlus**: bare-git approval pending
- **OpenAI key**: UNREVOKED (security action needed)

## Top-3 Gains
1. FocalPoint Observably: ~39 instrumented async functions across 7 crates
2. Macro cookbook: adoption pattern codified for wave-77+ roll-outs
3. KDesktopVirt v0.2.1: public release with advisory cleanup

## Wave-77+ Roadmap
- Tracera v0.1.1 release in flight
- Focus-eval + connector-gcal continued instrumentation
- AgilePlus + HexaKit submodule cleanup

---
**Status:** Shipped · 39 async instrumented · 2 docs published · 1 release live
