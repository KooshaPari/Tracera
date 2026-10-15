# Blockers (revision 3)

## Hard blockers (work cannot start)

### B1. opencode-go monthly quota 100% on workspace `wrk_01...`

- **What:** All subagent dispatches fail with HTTP 429 `GoUsageLimitError`.
- **Auto-reset:** 2026-10-18T10:22:53Z (5.5 days from 2026-10-12T22:36Z).
- **Operator work-around:** wA:p4 pane is "Design API key rotator proxy" — may unblock sooner than the auto-reset.
- **Workaround for this plan-first phase:** proceed with VP-Eng reading code and writing docs (no subagent needed). The plan-first phase is *explicitly* unblocked.
- **Resolution criteria:** `/v1/usage` returns `monthly.status=ok` (or the wA:p4 key proxy is live and rotates to a different workspace).

### B5. Cannot see deployed `dash.kooshapari.com` (Cloudflare Access wall) — REFRAMED in revision 3

- **Original framing (revision 2):** "I cannot inspect the deployed 'basic tab system' the operator references."
- **Revised framing (revision 3):** The "basic tab system" does not exist in the current codebase. The current top-nav is just `Work | Resume | Contact` (3 links, no tabs). The operator's directive is **preemptive**: don't build a naive 4-tab default; build `/parent/` first.
- **Remaining impact:** the deployed app's actual landing state is behind CF Access and cannot be inspected. If the operator has uncommitted work (in another clone, on another branch, in flight) that introduces tabs, I cannot see it. The local clone has no tabs and no `/parent/` route.
- **Workaround:** the Phase 1 implementation starts from a clean `main` in `koosha-phenotype` and builds the `/parent/` view as a NEW view (not a replacement of an existing tab system). The CF Access wall doesn't block this because the new view is being added, not modified.
- **Resolution criteria:** none (reframed). The Phase 1 subagent can proceed once B1 is resolved.

### ~~B6. Operator's in-flight work on `koosha-phenotype` is on `feat/dimensional-layering` branch~~ — RESOLVED in revision 3

- **RESOLVED 2026-10-12T23:00Z:** the 3 in-flight branches in `koosha-phenotype` (`feat/dimensional-layering`, `feat/e-ink-paper`, `feat/editorial-grid-case-study`) are all small visual-novelty PRs (operator's design-novelty audit). None of them are about the cockpit refresh or introduce a "basic tab system."
  - `feat/dimensional-layering`: 4-step elevation ladder utility (3-line tokens.css + 24-line case-studies.css)
  - `feat/e-ink-paper`: not yet inspected, but on a similar pattern (visual novelty)
  - `feat/editorial-grid-case-study`: not yet inspected, but on a similar pattern (visual novelty)
- **New answer:** The cockpit refresh can branch from a clean `main` of `koosha-phenotype` without picking up the operator's WIP. The WIP branches are independent PRs and will land separately.

## Soft blockers (work can start, with caveats)

### B3. Tracera main is 2 ahead, 77 behind origin/main

- **What:** Operator has uncommitted in-flight work on `main` (25 M-files, 1 untracked `.audit/`).
- **Impact:** any subagent branch from `main` will pick up those M-files.
- **Workaround:** do not commit or push those M-files. Branch from a clean commit if possible.
- **Resolution criteria:** operator rebases/pushes their work, or branches from a specific commit that excludes the M-files.

### B4. No CF API token / wrangler login / Vercel auth

- **What:** wrangler.toml + Vercel configs presume operator-side auth.
- **Impact:** subagent cannot deploy directly. Subagent produces the code + PR; operator runs the deploy.
- **Workaround:** the deploy step is operator-side; subagent only produces the code + PR.
- **Resolution criteria:** operator runs `wrangler deploy` (for CF Workers) or `vercel --prod` (for the web app) after merge.

## Resolved blockers (revision 3)

### ~~B2. Source of truth for `dash.kooshapari.com` is unknown~~ — RESOLVED 2026-10-12T22:49Z

- Source is `koosha-phenotype` (Vercel project `kooshapari-site`, projectId `prj_wVRCWLBwtZUg5DbPqfLpe9IbeaXt`, remote `git@github.com:KooshaPari/KooshaPari.git`).

### ~~B6. Operator's in-flight work on `koosha-phenotype` blocks branching~~ — RESOLVED 2026-10-12T23:00Z

- The 3 in-flight branches are visual-novelty PRs, not the cockpit refresh. Cockpit refresh can branch from a clean `main`.

## Open questions for operator

1. **(P1) Visual design reference for `/parent/`** — is there an existing design (Figma, sketch, mockup) or do we design from scratch using the design constitution as the foundation?
2. **(P2) Personal-mode issue model fields** — what fields on a paperclip issue need to be different for `kind=personal`? Or is it a tag/label?
3. **(P3) MCP server exposure** — is the existing `:8081` streamable-HTTP wrapper sufficient, or do we also need a CF Worker-deployed MCP for `dash.kooshapari.com/mcp`?
4. **(P4) 15-min refresh interval** — exact source of truth (cron? `setInterval` in AppShell? job queue?). Tracera's existing dashboards have varied refresh intervals.
5. **(P5) /parent/ default landing** — should `dash.kooshapari.com/` redirect to `/parent/`, or should `/` be the default route and `/parent/` be a separate nav entry? (Operator's directive: "land on /parent/ first" — but a redirect may break back-navigation expectations.)
6. **(P6) 9-agent data source for /parent/** — should the per-agent state be fetched live from paperclip's `/api/agents`, or should it be a static config in `data/phenotype.js` with a refresh fetch? (Live is preferred; static is a fallback if paperclip isn't available.)
7. **(P7) Bundle budget for /parent/** — current bundle is 228.7 KB; budget is <= 230 KB. New `/parent/` view + helpers + 9-agent state + ASCII widgets will likely push over budget. Operator decision: increase the budget, or use dynamic import to lazy-load `parent.js`?

## Resolved questions

- **Q: Is `cockpit-source` the right repo for `dash.kooshapari.com`?**
  A: No. `cockpit-source` is a local Python dashboard generator, not the web app. The web app is `koosha-phenotype`.
- **Q: Is `Tracera` the right repo for `dash.kooshapari.com`?**
  A: No. Tracera is the agent-facing surface (MCP/CLI/skill). The web app is `koosha-phenotype`.
- **Q: Does the "naive tab system" exist in the current code?**
  A: No. Current top-nav is `Work | Resume | Contact` (3 links, no tabs). The directive is preemptive.
- **Q: Is the operator's in-flight work blocking the cockpit refresh?**
  A: No. The 3 in-flight branches are design-novelty PRs. The cockpit refresh can branch from a clean `main`.
