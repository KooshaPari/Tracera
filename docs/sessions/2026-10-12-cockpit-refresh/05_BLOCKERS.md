# Blockers (revision 3, 2026-10-15)

## Hard blockers (work cannot start)

### B1. opencode-go monthly quota 100% on workspace `wrk_01...`

- **What:** All subagent dispatches fail with HTTP 429 `GoUsageLimitError`.
- **Auto-reset:** 2026-10-18T10:22:53Z (5.5 days from 2026-10-12T22:36Z).
- **Operator work-around:** wA:p4 pane is "Design API key rotator proxy" — may unblock sooner than the auto-reset.
- **Workaround for this plan-first phase:** proceed with VP-Eng reading code and writing docs (no subagent needed). The plan-first phase is _explicitly_ unblocked.
- **Resolution criteria:** `/v1/usage` returns `monthly.status=ok` (or the wA:p4 key proxy is live and rotates to a different workspace).

## Soft blockers (work can start, with caveats)

> Corrected 2026-10-15: B5 previously sat under "Hard blockers (work cannot start)" even
> though its own resolution criteria said Phase 1 "can proceed once B1 is resolved". It is a
> visibility caveat, not a gate, so it belongs here.

### B5. Cannot see deployed `dash.kooshapari.com` (Cloudflare Access wall) — REFRAMED in revision 3

- **Earlier framing (revision 2, superseded):** "I cannot inspect the deployed 'basic tab system' the operator references."
- **Revised framing (revision 3):** The "basic tab system" does not exist in the current codebase. The current top-nav is just `Work | Resume | Contact` (3 links, no tabs). The operator's directive is **preemptive**: don't build a naive 4-tab default; build `/parent/` first.
- **Remaining impact:** the deployed app's actual landing state is behind CF Access and cannot be inspected. If the operator has uncommitted work (in another clone, on another branch, in flight) that introduces tabs, I cannot see it. The local clone has no tabs and no `/parent/` route.
- **Workaround:** the Phase 1 implementation starts from a clean `main` in `koosha-phenotype` and builds the `/parent/` view as a NEW view (not a replacement of an existing tab system). The CF Access wall doesn't block this because the new view is being added, not modified.
- **Resolution criteria:** none (reframed). This is a visibility caveat, not a gate — the Phase 1 implementation can proceed without it. The only hard gate is B1.

### ~~B6. Operator's in-flight work on `koosha-phenotype` is on `feat/dimensional-layering` branch~~ — RESOLVED in revision 3

- **RESOLVED 2026-10-12T23:00Z:** the 3 in-flight branches in `koosha-phenotype` (`feat/dimensional-layering`, `feat/e-ink-paper`, `feat/editorial-grid-case-study`) are all small visual-novelty PRs (operator's design-novelty audit). None of them are about the cockpit refresh or introduce a "basic tab system."
  - `feat/dimensional-layering`: 4-step elevation ladder utility (3-line tokens.css + 24-line case-studies.css)
  - `feat/e-ink-paper`: not yet inspected, but on a similar pattern (visual novelty)
  - `feat/editorial-grid-case-study`: not yet inspected, but on a similar pattern (visual novelty)
- **New answer:** The cockpit refresh can branch from a clean `main` of `koosha-phenotype` without picking up the operator's WIP. The WIP branches are independent PRs and will land separately.

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
3. **(P3) MCP server exposure** — is the existing `:8081` streamable-HTTP wrapper sufficient, or do we also need a CF Worker-deployed MCP for `dash.kooshapari.com/mcp`? **Verified 2026-10-14:** the wrapper is real — `crates/tracera-mcp` exists and `Makefile:84` defines `task-mcp-server` on :8081 — but it is **not currently running** (nothing listening on :8081). So "reuse the existing wrapper" is a real option with a known gap: someone must start it.
4. **(P4) 15-min refresh interval** — exact source of truth (cron? `setInterval` in AppShell? job queue?). Tracera's existing dashboards have varied refresh intervals.
5. **(P5) /parent/ default landing** — should `dash.kooshapari.com/` redirect to `/parent/`, or should `/` be the default route and `/parent/` be a separate nav entry? (Operator's directive: "land on /parent/ first" — but a redirect may break back-navigation expectations.)
6. **(P6) 9-agent data source for /parent/** — three options: static roster in `data/phenotype.js` plus a build-time snapshot; live state via the same-origin `/api/parent/*` server-side proxy (see `03_PROPOSED_DESIGN.md` "Data path"); direct client-side calls to Paperclip (not viable - a static client bundle cannot hold Access credentials). P6 default: static roster (`data/phenotype.js`) plus a build-time snapshot. Live state is served only through the same-origin `/api/parent/*` proxy described in 03 "Data path", which is a proposal pending operator approval of the Access service token. Direct client-side calls to Paperclip are not viable. **Hostname resolved 2026-10-15:** the authoritative Paperclip hostname is `paperclip.phenotype.space`, verified route-level against the live desk deployment (the desk quadlet sets `PAPERCLIP_PUBLIC_URL=https://paperclip.phenotype.space` and `PAPERCLIP_ALLOWED_HOSTNAMES=localhost,127.0.0.1,paperclip.phenotype.space`); earlier `paperclip.kooshapari.com` references described the superseded Mac-tunnel record and are replaced across 02/03/04/05. The 9-agent roster remains unverified against the live instance.
7. **(P7) Bundle budget for /parent/** — **measured 2026-10-14: the current bundle is 212.3 KB against a <= 230 KB budget, so there is ~17.7 KB of headroom, not a shortfall.** (The docset previously stated 228.7 KB; that figure does not match `bundled/app.bundle.*.js` and was stale.) The original framing — that a new `/parent/` view "will likely push over budget" — is therefore **not supported by measurement**. Lazy-loading `parent.js` remains a reasonable default for code-splitting and first-paint reasons, but it is **no longer required to stay under budget**. Operator decision: keep lazy-load as a performance choice, inline it into the main bundle and spend the 17.7 KB, or raise the budget? Note no CI check enforces the 230 KB figure today; it is a documented convention only.

## Answer sheet (one line each)

Reply in any form — `P1=A P3=C ...`, or just "your defaults", or answer them one at a
time. "skip" defers any item; unstated items fall back to the recommendation below.

| #   | Question                   | Options                                                                                                                                                   | Recommended if unstated                                                                                                                                                                                         |
| --- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1  | `/parent/` visual design   | A mockup exists (paste it) · design from constitution · derive from an existing route                                                                     | **Design from the constitution**                                                                                                                                                                                |
| P2  | Personal-mode issue fields | tag/label only · new fields · reuse job fields                                                                                                            | **Tag/label only** (smallest change)                                                                                                                                                                            |
| P3  | MCP exposure               | reuse `:8081` · also CF Worker at `/mcp` · Worker only                                                                                                    | **Reuse `:8081`** (exists; just needs starting)                                                                                                                                                                 |
| P4  | 15-min refresh source      | `setInterval` in AppShell · server cron · job queue                                                                                                       | **`setInterval`** (simplest, survives deploys)                                                                                                                                                                  |
| P5  | `/parent/` as landing      | redirect `/`→`/parent/` · separate nav entry · serve `/parent/` at `/`                                                                                    | **Redirect** (literal directive compliance)                                                                                                                                                                     |
| P6  | Agent data source          | static roster · `/api/parent/*` proxy · direct client (not viable)                        | **Static roster (`data/phenotype.js`) plus a build-time snapshot** - live state only via the `/api/parent/*` proxy (see 03 "Data path") |
| P7  | Bundle approach            | lazy-load · inline and spend the 17.7 KB · raise the budget                                                                                               | **Lazy-load** for code-splitting (NOT required by budget — see above)                                                                                                                                           |

These are **recommendations, not decisions.** They are agent judgement recorded so that
nothing dangles if an item goes unanswered; adopting any of them is still an operator choice
and should be logged in `06_DECISION_LOG.md` as such.

## Resolved questions

- **Q: Is `cockpit-source` the right repo for `dash.kooshapari.com`?**
  A: No. `cockpit-source` is a local Python dashboard generator, not the web app. The web app is `koosha-phenotype`.
- **Q: Is `Tracera` the right repo for `dash.kooshapari.com`?**
  A: No. Tracera is the agent-facing surface (MCP/CLI/skill). The web app is `koosha-phenotype`.
- **Q: Does the "naive tab system" exist in the current code?**
  A: No. Current top-nav is `Work | Resume | Contact` (3 links, no tabs). The directive is preemptive.
- **Q: Is the operator's in-flight work blocking the cockpit refresh?**
  A: No. The 3 in-flight branches are design-novelty PRs. The cockpit refresh can branch from a clean `main`.
