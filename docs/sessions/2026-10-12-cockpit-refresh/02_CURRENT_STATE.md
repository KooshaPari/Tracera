# Current State — what exists today (revision 3)

## `dash.kooshapari.com` = `koosha-phenotype` (revision 2 source-of-truth)

| Aspect                            | Value                                                                                                                                    | Notes                                                   |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Repo path                         | `/Users/kooshapari/CodeProjects/Phenotype/repos/koosha-phenotype`                                                                        | Local clone                                             |
| Git remote                        | `git@github.com:KooshaPari/KooshaPari.git`                                                                                               | Public `KooshaPari` org repo                            |
| Vercel project                    | `kooshapari-site`                                                                                                                        | projectId `prj_wVRCWLBwtZUg5DbPqfLpe9IbeaXt`            |
| Vercel team/org                   | `team_uMfxKsua6PPiWqtcD93kzO5r`                                                                                                          | Owned by operator                                       |
| Custom domain                     | `dash.kooshapari.com` (and `kooshapari.com` apex)                                                                                        | Configured in Vercel dashboard, NOT in repo             |
| Cloudflare Access                 | 302 → `floral-moon-c604.cloudflareaccess.com` (login)                                                                                    | App is behind CF Access                                 |
| Current branch                    | `feat/dimensional-layering` (1 commit ahead of `main`)                                                                                   | Working tree clean                                      |
| Build command                     | `npm run stage:publication`                                                                                                              | Stage + bundle via esbuild                              |
| Output                            | `dist/`                                                                                                                                  | Vercel `outputDirectory: "dist"`                        |
| Stack                             | Vanilla JS + esbuild + Playwright (e2e + a11y)                                                                                           | NOT React; NOT a SPA framework                          |
| Pages                             | `index.html`, `work.html`, `engineering.html`, `product.html`, `blog.html`, `contact.html`, `resume.html`, `archive.html`, `work/*.html` | Multi-page static, SPA on `index.html`                  |
| Test framework                    | Playwright + `node --test` (unit)                                                                                                        | `tests/*.test.js` + `tests/e2e/`                        |
| Design system                     | `assets/styles/`, `styles/tokens.css`, governed by `.claude/skills/phenotype-design-constitution/SKILL.md`                               |                                                         |
| Brand                             | "Technical Atelier" — Koosha Paridehpour, evidence-led, museum-quiet, designer-engineer                                                  |                                                         |
| 15 projects in `data/projects.js` | Tracera is row 9 (developer-tools, violet `#7C3AED`, JetBrains Mono + IBM Plex Sans)                                                     | Full case studies per project                           |
| Legal identity                    | `data/phenotype.js` — Phenotype is a USPTO-registered trademark held by MP Advance Solutions LLC, California                             | High-stakes: any change to the brand is a legal concern |
| Public record                     | `data/phenotype-public-record.js` — citation-backed Resume vs Public-Record contrast table                                               |                                                         |

## SPA architecture (the cockpit refresh lands here)

| File                                      |       Lines | Role                                                                                                                                                                     |
| ----------------------------------------- | ----------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `index.html`                              |          69 | SPA root: `<div id="shell-root"></div>` + `<main id="view-root"></main>` + Three.js importmap                                                                            |
| `scripts/app.js`                          |         210 | SPA entry: imports `parseRoute`, `routeFromLocation`, `renderShell`, per-view renderers; sets page metadata; init scroll-reveal, transitions, magnetic, parallax, etc.   |
| `scripts/router.js`                       |          37 | DOM-bound orchestrator: `routeFromLocation`, `navigateTo`, listens for `hashchange`/`popstate`/`routechange`                                                             |
| `scripts/router-helpers.js`               |         165 | PURE route parser: `VIEW_ROUTES = Set('home','engineering','product','work','resume','contact','blog')`, `parseRoute`, `routeToPath`, `routeToHash`, `applyLens`         |
| `scripts/components/shell.js`             |         136 | Per-view top-nav + lens control + reader toggle. Current `ROUTES` = `[ ['/work','Work'], ['/resume','Resume'], ['/contact','Contact'] ]` (blog commented out 2026-10-11) |
| `scripts/views/home.js`                   |         242 | Home view: per-lens project priority, lens-specific identity profile                                                                                                     |
| `scripts/views/work.js` + `work-index.js` |      varies | Work index + project catalog                                                                                                                                             |
| `scripts/views/project-detail.js`         |      varies | Individual project case study (per slug)                                                                                                                                 |
| `scripts/views/resume.js`                 |      varies | Resume view                                                                                                                                                              |
| `scripts/views/contact.js`                |      varies | Contact view                                                                                                                                                             |
| `scripts/views/blog-index.js`             |      varies | Blog index                                                                                                                                                               |
| `scripts/views/blog-post.js`              |      varies | Blog post detail                                                                                                                                                         |
| `scripts/views/not-found.js`              |      varies | 404 view + canvas init                                                                                                                                                   |
| `scripts/lens-state.js`                   |      varies | Engineering/product lens state (localStorage-persisted)                                                                                                                  |
| `scripts/reader-state.js`                 |      varies | Reader mode toggle                                                                                                                                                       |
| `scripts/construction-shell.js`           |          29 | "Under construction" interstitial gate (NOT the AppShell; one-time modal)                                                                                                |
| `scripts/views/parent.js`                 | **missing** | **The /parent/ view to be built in Phase 1**                                                                                                                             |

### Adding `/parent/` (Phase 1 file-level plan)

- `scripts/router-helpers.js`: add `'parent'` to `VIEW_ROUTES` (1 line) + 2 if-branches in `parseRoute` (for `/parent`) and `routeToPath` (for `view: 'parent'`) — about 6 lines total
- `scripts/router.js`: no change (already path-based + pushState)
- `scripts/app.js`: add `import { renderParent } from './views/parent.js'` and wire `if (route.view === 'parent') renderParent(viewRoot, { ... })` in the renderer dispatch — about 4 lines
- `scripts/views/parent.js` (new, ~300-500 lines): the parent view — 9-agent strip, 15-min snapshot, feed; ASCII status widgets; design constitution palette
- `scripts/views/parent-helpers.js` (new, ~200-400 lines): per-agent card renderer, snapshot fetcher, ASCII widget helpers
- `scripts/components/shell.js`: add `['/parent', 'Parent']` to the `ROUTES` list — 1 line
- `vercel.json`: add a rewrite rule for `/parent` → `/parent.html` (consistent with `/work` → `/work.html`). **This only works if `parent.html` is actually created and staged** — the SPA catch-all serves `index.html` for unknown routes, so a rewrite to a file that was never generated leaves `/parent` broken. See the file list and registration table in `03_PROPOSED_DESIGN.md`.
- `scripts/app.js` (optional): change default landing to `/parent` (vs `/`) — 1 line if a redirect is preferred over a default-route swap

### Bundle + perf budget

- Current bundle: 212.3 KB minified, measured directly from `bundled/app.bundle.*.js` on 2026-10-14 (0 source files changed since that build, so the figure is current). The earlier 228.7 KB figure, previously attributed here to the `phenotype-design-constitution` § 6, does not match the build output and was stale.
- Budget: <= 230 KB minified, leaving ~17.7 KB of headroom (70.7 KB gzipped on the wire)
- New `/parent/` view must NOT push the bundle over budget
- Strategy: lazy-loading `parent.js` is an **optional** code-splitting choice, not a budget requirement — see the corrected measurement above

### Design constitution (`.claude/skills/phenotype-design-constitution/SKILL.md`)

- Voice: third person, past/present tense, evidence-led ("approximately", "user-stated", "canonical user fact")
- Palette: Obsidian `#0F1012` / Slate `#353A40` / Ceramic `#F6F5F5` / Teal `#7EBAB5` + per-project accent (Tracera = violet `#7C3AED`)
- Fonts: Inter (body) + Space Grotesk (display) + JetBrains Mono (meta, evidence chips)
- WCAG 2.2 AA: contrast >= 4.5:1, focus rings, 24px touch targets, reduced-motion, skip-link
- Bundle <= 230 KB minified
- 60fps on parallax/reveals (transform + opacity only, never `width`/`height`/`top`/`left`)
- Status pills: `o` historical, `D` current, `O` research
- ASCII widgets allowed (status widget, project spine, evidence chip)
- **The `/parent/` view must conform to this constitution.** No "passionate"/"rockstar"/"driven" copy. Evidence-led labels. Glyph-prefixed status.

## Build + deploy pipeline

- `npm run stage:publication` → `dist/`
- `npm test` → `node --test tests/*.test.js` (unit tests)
- `npm run test:e2e` → `npm run stage:publication && npx playwright test` (e2e with a11y + contrast checks)
- `npm run check` → `node --check` on `app.js`, `stage-publication.js`, `data/projects.js`
- `npm run verify` → `npx vercel build && npm test && npm check && npm run test:e2e`
- Vercel: rewrites map clean paths to static HTML files; catch-all rewrite serves `index.html` for client-side routing of unknown paths (excludes `*.html`, `*.js`, etc.)

## In-flight branches (NOT cockpit refresh)

- `feat/dimensional-layering` — 4-step elevation ladder utility (PR 3 of design-novelty audit; 3-line tokens.css + 24-line case-studies.css)
- `feat/e-ink-paper` — operator in-flight (not yet inspected)
- `feat/editorial-grid-case-study` — operator in-flight (not yet inspected)

All three are small visual-novelty PRs. Revision 3 conclusion: the directive is **preemptive** (see `05_BLOCKERS.md` B5 revised framing) — there is no tab system to replace in any known location; build `/parent/` as a NEW view.

## Tracera repo (agent-facing surface, not the web app)

| Aspect               | Current                                                             | Notes                                                                                                                                                                                                                                                                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Path                 | `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera`            | Local clone                                                                                                                                                                                                                                                                                                                                                                                            |
| Default branch       | `main`                                                              | 2 ahead, 77 behind origin/main (operator in-flight work)                                                                                                                                                                                                                                                                                                                                               |
| Remote               | `git@github.com:KooshaPari/Tracera.git`                             | GitHub-public                                                                                                                                                                                                                                                                                                                                                                                          |
| Local mods (M-files) | 25 modified, 1 untracked (`.audit/`)                                | Operator in-flight; not ours to commit                                                                                                                                                                                                                                                                                                                                                                 |
| Backend              | Rust + cargo + sqlx                                                 | `crates/tracera-server`                                                                                                                                                                                                                                                                                                                                                                                |
| Edge Worker          | `crates/tracera-edge` → `tracera-edge.pheno.studio`                 | CF Worker (separate from `dash.kooshapari.com`)                                                                                                                                                                                                                                                                                                                                                        |
| Main API             | `https://tracera.pheno.studio/api`                                  | wrangler.toml `TRACERA_API`                                                                                                                                                                                                                                                                                                                                                                            |
| Web app              | `frontend/apps/web/` (React 19 + TanStack Router + Vite + Tailwind) | 29+ view files; NOT the source of `dash.kooshapari.com`                                                                                                                                                                                                                                                                                                                                                |
| Python SDK           | `crates/tracera-py-sdk`                                             |                                                                                                                                                                                                                                                                                                                                                                                                        |
| Go CLI               | `crates/tracera-go-cli/`                                            |                                                                                                                                                                                                                                                                                                                                                                                                        |
| Rust CLI             | `crates/tracera-cli`                                                |                                                                                                                                                                                                                                                                                                                                                                                                        |
| MCP servers          | `crates/tracera-mcp`                                                | Streamable-HTTP wrapper around stdio (port 8081). **Verified 2026-10-14:** the crate exists on disk and `Makefile:84` defines the `task-mcp-server` target on :8081. The target is **not running** (nothing listening on :8081) — it must be started before use. _(Corrected 2026-10-15: this row also listed a non-existent `crates/tracertm-mcp`; that was a transposed typo and has been removed.)_ |
| Design system        | `docs/specs/014-design-tokens-wcag.md`                              | WCAG-compliant tokens                                                                                                                                                                                                                                                                                                                                                                                  |

## Paperclip (issue model, orchestration)

- **Local origin NOT running (2026-10-14):** `curl http://127.0.0.1:3180/` returns no response (HTTP 000); nothing listens on 3180.
- **But the public endpoint IS live, behind Cloudflare Access (corrected 2026-10-14T18:55 PDT):** `https://paperclip.phenotype.space/api/agents` returns HTTP 302 to a `cloudflareaccess.com` login for that app, and the `com.kooshapari.cloudflared-paperclip` launchd job is healthy (three registered Cloudflare edge connections in its log). `agentcom-inbox` is configured against `paperclip=http://127.0.0.1:3180` and ran as recently as 2026-10-12T21:22Z. `~/paperclip-workspace` exists but is empty; paperclip is not a repo, binary, or installed package on this machine.
  - **Hostname corrected 2026-10-15:** the authoritative Paperclip hostname is `paperclip.phenotype.space`, verified route-level against the live desk deployment (the desk quadlet sets `PAPERCLIP_PUBLIC_URL=https://paperclip.phenotype.space` and `PAPERCLIP_ALLOWED_HOSTNAMES=localhost,127.0.0.1,paperclip.phenotype.space`); earlier `paperclip.kooshapari.com` references described the superseded Mac-tunnel record. The 302 verification above was recorded against the Mac-tunnel deployment on 2026-10-14.
  - The infrastructure (tunnel + Access + hostname) is alive; only the local origin process is down. An earlier version of this docset said simply "deployed at localhost:3180", and a first check concluded "DOWN" — both imprecise. What is _not_ proven is whether the origin behind the Access wall currently answers, since the 302 is an auth challenge and no authenticated read was possible.
  - **Consequence for P6:** P6 default: static roster (`data/phenotype.js`) plus a build-time snapshot. Live state is served only through the same-origin `/api/parent/*` proxy described in 03 "Data path", which is a proposal pending operator approval of the Access service token. Direct client-side calls to Paperclip are not viable.
- 9 agents registered: `jcode`, `hermes`, `vp`, `instinct`, `codex`, `kcode`, `winremote`, `engineer-general`, `engineer-specialist`. **Corroborated 2026-10-14, still not live-verified.** Two independent artifacts dated 2026-10-11 — `~/.jcode/scratch/2026-10-12-vp-autonomy/herdr-wiring.md.bak` and `deploy.sh.bak` — each contain exactly this set of 9 names, and a set-diff against this list is empty. That is meaningful independent evidence the roster is real rather than invented, but it is **not** a live `/api/agents` read, so treat it as corroborated rather than confirmed. It also cannot detect agents added or removed since 2026-10-11. Do not hardcode it into per-agent cards without re-reading the live source.
- Issue model: `kind` (job/personal TBD), `assigneeAgentId`, `priority`, `status`, `id` (UUID).
- API endpoints: `/api/issues`, `/api/agents`, `/api/secrets`, `/api/companies/...` (728 paths in `/api/openapi.json`). Path list unverified against a live OpenAPI fetch.

## CF Workers (`harness-ops/agent-comms/workers/`)

| Worker                                           | Status                                                                          | Blocking                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `agentcom-inbox` (Resend → paperclip)            | Code ready (worker.js 255 lines, wrangler.toml configured, deploy.sh 123 lines) | DNS for `inbox.kooshapari.com` + RESEND_WEBHOOK_SECRET (operator) |
| `agentcom-discord` (Discord → paperclip)         | Code ready (worker.js 140 lines, wrangler.toml configured, deploy.sh 75 lines)  | DISCORD_BRIDGE_HMAC_SECRET + DISCORD_WEBHOOK_URL (operator vault) |
| `agentcom-discord-inbound` (paperclip → Discord) | **Not designed** — operator said do NOT invent                                  | Operator design input required                                    |

## `cockpit-source` (NOT the cockpit, separate project)

- `/Users/kooshapari/CodeProjects/Phenotype/repos/cockpit-source`
- Local Python dashboard generator (serves a static HTML file via launchd at `com.kooshapari.cockpit-dashboard`).
- 4 uncommitted M-files dated 2026-08-14/19 (2 months old). Sanitization pass replacing `kooshapari` → `<REDACTED>` in paths. **Not our work; do not touch.**
- This repo is for the local-only Python dashboard, NOT `dash.kooshapari.com`.

## Instinct directive state (blocker)

- 3 prior subagent dispatches failed (2026-10-12 21:32–22:05)
- Root cause: opencode-go workspace `wrk_01...` hit **MONTHLY quota 100%**
  (HTTP 429 `GoUsageLimitError`)
- Reset: **2026-10-18T10:22:53Z** (5.5 days from 2026-10-12T22:36Z)
- Operator is mid-fix at `wA:p4 "OpenCode-Go - key proxy"` (working on
  "Design API key rotator proxy") — likely a workspace rotator to bypass quota
- `/v1/usage` and `/v1/models` endpoints probed. 38-model catalog captured.
- Until quota clears or wA:p4 lands, no subagent can be dispatched for
  implementation work. The plan-first phase is _explicitly_ unblocked.
