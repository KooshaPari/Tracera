# Decision Log (revision 3)

## D1. Plan-first, no code yet

- **Date:** 2026-10-12T22:36Z
- **Decision:** Phase 0 = plan + state audit only. Do not write any code
  in `Tracera` (or any other repo) until operator approves the design.
- **Rationale:** Operator's directive is "plan first, then PRs".

## D2. ~~Tracera is the canonical source~~ REVERSED in revision 2

- **Date (original):** 2026-10-12T22:36Z
- **Reversed:** 2026-10-12T22:49Z
- **Original (WRONG) decision:** Treat `Tracera` as the canonical source
  for the cockpit-refresh work.
- **Reversed because:** the deployed `dash.kooshapari.com` is the
  Vercel project `kooshapari-site` (projectId
  `prj_wVRCWLBwtZUg5DbPqfLpe9IbeaXt`), which is built from
  `koosha-phenotype`, not from `Tracera`. Tracera is the agent-facing
  surface (MCP/CLI/skill), not the web app.
- **New decision:** see D9.

## D3. `cockpit-source` 4 M-files are out of scope

- **Date:** 2026-10-12T22:36Z
- **Decision:** Do not touch the 4 M-files in `cockpit-source` from the
  August 2026 sanitization pass.
- **Rationale:** They are 2 months old, not part of this directive, and
  no operator signal mentions them. They are operator's in-flight work.

## D4. Plan docs live in Tracera, not in cockpit-source or koosha-phenotype

- **Date:** 2026-10-12T22:36Z
- **Decision:** Session docs go in
  `Tracera/docs/sessions/2026-10-12-cockpit-refresh/`.
- **Rationale:** Tracera has the `docs/sessions/` convention; the
  plan spans multiple repos; one canonical home is cleaner. The session
  dir is untracked (no commit), but the path is correct.

## D5. Phase 0 work can proceed without opencode-go quota

- **Date:** 2026-10-12T22:36Z
- **Decision:** Plan-first phase is VP-Eng-only (read code, write
  docs). No subagent dispatch until quota clears.
- **Rationale:** Plan-first is explicitly unblocked. Subagent dispatch
  is the only thing that needs the opencode-go quota.

## D6. ~~AppShell pattern in Tracera~~ MOVED to koosha-phenotype in revision 2

- **Date (original):** 2026-10-12T22:36Z
- **Revised:** 2026-10-12T22:49Z
- **Original decision:** Phase 1 introduces a top-level `AppShell` in
  Tracera.
- **Revised decision:** AppShell lives in `koosha-phenotype` (the web
  app at `dash.kooshapari.com`). Tracera does NOT get an AppShell.
- **Rationale:** the "shell" is a web UI concept; the agent-facing
  surface in Tracera uses CLI + MCP, not a shell.

## D7. Branching model (per repo)

- **Date:** 2026-10-12T22:36Z
- **Decision:** One branch per Phase deliverable (see
  `04_PR_PIPELINE.md`). All PRs against `main`.
- **Rationale:** Operator's "no force-push" rule. Merge commits, not
  rebases. One Phase per branch keeps each PR reviewable.

## D8. ~~Tracera's design tokens (Phase 1) are the visual foundation~~ REVISED in revision 2

- **Date (original):** 2026-10-12T22:36Z
- **Revised:** 2026-10-12T22:49Z
- **Original decision:** AppShell + /parent/ use Tracera's design tokens
  (per `docs/specs/014-design-tokens-wcag.md`).
- **Revised decision:** AppShell + /parent/ use `koosha-phenotype`'s
  design system (`assets/styles/`, `tokens.css`, governed by the
  `phenotype-design-constitution` skill). Tracera's design tokens are
  only relevant if Phase 2 work needs to match Tracera's CLI/MCP
  console output.
- **Rationale:** `dash.kooshapari.com` is `koosha-phenotype`; its design
  system is already there and well-maintained.

## D9. Two-repo design (new in revision 2, expanded to three-repo in revision 3)

- **Date (original):** 2026-10-12T22:49Z
- **Revised:** 2026-10-12T23:00Z
- **Original decision:** The cockpit refresh spans two repos:
  `koosha-phenotype` (web) + `Tracera` (agent surface).
- **Revised decision:** Three repos:
  - `koosha-phenotype` (web app, Phase 1 + 3 UI)
  - `Tracera` (agent-facing surface, Phase 2)
  - `paperclip` (issue model, Phase 3 schema)
- **Rationale:** Phase 3 (personal mode) requires a schema change to
  paperclip (the `kind=personal` flag). paperclip is a separate product
  with its own deployment; treating it as a third repo in the design is
  cleaner than treating it as a sub-component of Tracera.

## D10. The `/parent/` view is a NEW view, not a refactor of an existing tab system (new in revision 3)

- **Date:** 2026-10-12T23:00Z
- **Decision:** Phase 1 adds a new `view: 'parent'` entry to the router, plus a new `scripts/views/parent.js` and `parent-helpers.js`. It does NOT refactor any existing tab system because none exists.
- **Rationale:** The current top-nav is `Work | Resume | Contact` (3 links, no tabs). The operator's directive "replace the naive tabs" is preemptive: don't build a 4-tab default; build `/parent/` first. The implementation strategy is "add, don't replace."
- **File impact:** `scripts/router-helpers.js` (1 line in VIEW_ROUTES, 2 if-branches in parseRoute/routeToPath); `scripts/router.js` (no change); `scripts/app.js` (+5 lines to wire the new view); `scripts/components/shell.js` (+1 line to add `/parent` to ROUTES); `vercel.json` (+3 lines for the rewrite rule); `scripts/views/parent.js` (new, 300-500 lines); `scripts/views/parent-helpers.js` (new, 200-400 lines).

## D11. Phase 1 + Phase 4 are one phase (new in revision 3)

- **Date:** 2026-10-12T23:00Z
- **Decision:** Merge "Phase 1: /parent/ view as default landing, replace naive tabs" and "Phase 4: keep 15-min refresh + per-agent state wired through" into a single Phase 1.
- **Rationale:** The 15-min refresh and the 9 per-agent state are inseparable from the AppShell and the `/parent/` view. Splitting them into two phases was a planning artifact, not a real implementation boundary. The subagent work for both is "build the `/parent/` view with the 15-min refresh and 9-agent cards."

## D12. B6 (operator's in-flight work blocks branching) is RESOLVED (new in revision 3)

- **Date:** 2026-10-12T23:00Z
- **Decision:** The 3 in-flight branches in `koosha-phenotype`
  (`feat/dimensional-layering`, `feat/e-ink-paper`,
  `feat/editorial-grid-case-study`) are operator's design-novelty PRs,
  not the cockpit refresh. The cockpit refresh can branch from a clean
  `main`.
- **Rationale:** All three branches are small visual-novelty PRs
  (verified for `feat/dimensional-layering`: 3-line tokens.css + 24-line
  case-studies.css). None introduce a "basic tab system" or otherwise
  conflict with the cockpit refresh.

## D13. Design constitution is binding (new in revision 3)

- **Date:** 2026-10-12T23:00Z
- **Decision:** The Phase 1 design must conform to the
  `phenotype-design-constitution` skill in
  `.claude/skills/phenotype-design-constitution/SKILL.md`. The constitution
  enforces:
  - Voice (third person, past/present, evidence-led, no promotional copy)
  - Palette (monochrome ink + per-project accent)
  - Fonts (Inter / Space Grotesk / JetBrains Mono)
  - WCAG 2.2 AA (contrast, focus, touch targets, reduced-motion, skip-link)
  - Bundle budget (<= 230 KB minified; measured 212.3 KB on 2026-10-14, so ~17.7 KB headroom — the earlier 228.7 KB figure was stale)
  - Animation (transform + opacity only, 60fps)
  - Status pills (glyph-prefixed)
  - ASCII widgets (status widget, project spine, evidence chip recipes)
- **Rationale:** The portfolio is a shipped, production-grade product
  with a registered trademark. The `/parent/` view is an evolution of
  that product, not a new product. The design constitution is the
  brand contract and must be honored.

## D14. PR title policy amended (operator directive, 2026-10-12T23:48Z)

- **Decision (operator, verbatim amendment):** the "PRs titled `[Instinct]`"
  sub-clause of the 22:33Z directive block is **title-scoped only** —
  heavy/architecture PRs use plain titles; the `[Instinct]` prefix MAY be
  used for light/legibility PRs. The other directives in that block
  (including the "Authored by Instinct" PR-body first line, which remains
  binding for ALL PRs) are unchanged.
- **Rationale:** NOT stated by the operator in the amendment — the verbatim
  text is preserved in 01_OPERATOR_DIRECTIVES.md. (Agent inference only:
  plain titles likely review better on design-defining work; treat as
  inference, not operator intent.)
- **Propagation (2026-10-14, validated R1–R7):** applied to
  00_SESSION_OVERVIEW.md (directive #7), 01_OPERATOR_DIRECTIVES.md
  (verbatim + summary-table row 9), 03_PROPOSED_DESIGN.md (Phase 1/2
  acceptance checklists), 04_PR_PIPELINE.md (title convention +
  PR-body template). See MANIFEST.md for the canonical-vs-backup map.

## Pending decisions (need operator signal)

- P1. Visual mockup of `/parent/` (or design from scratch using the constitution).
- P2. Personal-mode issue model fields.
- P3. MCP server deployment target.
- P4. Exact 15-min refresh source of truth.
- P5. `/parent/` as default landing (redirect from `/` vs separate route with `/` as fallback).
- P6. 9-agent data source (paperclip `/api/agents` live vs static config).
- P7. Bundle budget decision (increase vs lazy-load).
