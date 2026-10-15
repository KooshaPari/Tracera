# Proposed Design (revision 3 — portfolio → cockpit evolution, file-level plan)

> **Status:** DRAFT (Phase 0 / plan-first). Operator must approve before any
> code is written.

## Framing (revision 3)

`dash.kooshapari.com` is a shipped, production-grade portfolio SPA
(vanilla JS + esbuild, design constitution enforced, 15 projects with
case studies, USPTO-registered brand identity). The operator's directive
is to **evolve** it into a unified cockpit by adding a new `/parent/`
view as the default landing — and to prevent a "naive 4-tab default"
from creeping in.

The "naive tab system" the operator references does not exist in the
current code (the top nav is just `Work | Resume | Contact`). The
directive is **preemptive**: don't build a basic tab nav as the cockpit
shell; build `/parent/` as a richer, content-first consolidated view
that honors the portfolio's design constitution.

## Three-repo scope (reconfirmed)

| Repo               | Phase 1                                                     | Phase 2                                           | Phase 3                             |
| ------------------ | ----------------------------------------------------------- | ------------------------------------------------- | ----------------------------------- |
| `koosha-phenotype` | `/parent/` view + AppShell + 15-min refresh + 9-agent state | (read-only)                                       | `/parent/personal` subroute         |
| `Tracera`          | (none)                                                      | MCP/CLI/skill surface for `/parent/` data sources | (none)                              |
| `paperclip`        | (none)                                                      | (none)                                            | `kind: "personal"` schema + routing |

The two are wired together: `koosha-phenotype` reads Paperclip data via the
Paperclip API (see **Data path**) and calls Tracera's MCP/CLI for
agent-facing actions.

---

## Phase 1 — `/parent/` view + AppShell + 15-min refresh + 9-agent state (in `koosha-phenotype`)

This is a single phase. The 15-min refresh and the per-agent state are
inseparable from the AppShell — they live INSIDE the view, not in a
separate phase.

### Goals

- `dash.kooshapari.com` lands on `/parent/` first (either default route or a `/` → `/parent` redirect).
- The new `/parent/` view is a consolidated, content-first cockpit — not a tab system.
- The portfolio's existing routes (`/`, `/work`, `/resume`, `/contact`, project pages) continue to work as secondary nav.
- 9 per-agent cards (one per paperclip agent) show live state.
- 15-min refresh ticks visibly (last-refreshed timestamp updates).
- The design constitution (monochrome ink + per-project accent, Inter + Space Grotesk + JetBrains Mono, evidence-led voice, WCAG 2.2 AA) is honored.

### File-level implementation plan (Phase 1)

**Files to modify:**

| File                                             | Change                                                                                                                                                          | Lines (est.) |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -----------: |
| `scripts/router-helpers.js`                      | Add `'parent'` to `VIEW_ROUTES`; add 2 if-branches in `parseRoute` and `routeToPath`                                                                            |           +6 |
| `scripts/router.js`                              | No change                                                                                                                                                       |            0 |
| `scripts/app.js`                                 | Add `import { renderParent } from './views/parent.js'`; wire `route.view === 'parent'` in the render dispatch; (optionally) change default landing to `/parent` |           +5 |
| `scripts/components/shell.js`                    | Add `['/parent', 'Parent']` to `ROUTES` (the top nav)                                                                                                           |           +1 |
| `vercel.json`                                    | Add `{ "source": "/parent", "destination": "/parent.html" }` rewrite                                                                                            |           +3 |
| `styles/bundled/pages.css` (or new `parent.css`) | Per-view styles, ASCII status widget, 9-agent grid, 15-min refresh indicator                                                                                    |         +150 |
| `data/phenotype.js`                              | extend `IDENTITY` with a static 9-agent roster (refreshed at build time from the snapshot below)                                                                |          +20 |

**Files to create:**

| File                              | Role                                                                                                                                                                                                                                                                                                                                                                                                                                      | Lines (est.) |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -----------: |
| `scripts/views/parent.js`         | The `/parent/` view: orchestrator (mounts the 9-agent strip, the 15-min snapshot, the feed)                                                                                                                                                                                                                                                                                                                                               |      300-500 |
| `scripts/views/parent-helpers.js` | Per-agent card renderer, snapshot fetcher, ASCII widget helpers                                                                                                                                                                                                                                                                                                                                                                           |      200-400 |
| `tests/parent.test.js`            | Unit tests for the route parser and parent view helpers                                                                                                                                                                                                                                                                                                                                                                                   |      100-200 |
| `tests/e2e/parent.spec.js`        | E2E test: navigate to `/parent/`, verify 9 cards render, verify 15-min timer exists                                                                                                                                                                                                                                                                                                                                                       |       50-100 |
| `parent.html`                     | Static entry for the route, required by the `vercel.json` rewrite. **Omitted from this list originally** (caught in review 2026-10-15): without it the rewrite points at a file that does not exist and `/parent` bypasses the `index.html` catch-all. `parent.html` must bootstrap the same shell as `index.html` (it is registered in `prerender.js` `TOP_LEVEL_ROUTES` below) so the client route and the static entry cannot diverge. |          ~66 |
| `workers/parent-proxy/`           | Same-origin `/api/parent/*` proxy handler (`wrangler.toml` + `src/index.ts`); hosting route + Access secrets binding assigned here - **proposal**, gated on B-REPO and the operator's service-token step (see "Data path (proposal; gated on B-REPO)"). If B-REPO resolves to job-cockpit, this becomes a route in that app's server instead. |          ~150 |

**Registration points the route needs beyond the two files above** (all three were missing from
this plan originally and were caught in review — a new top-level page has to be enumerated in
_every_ one of them, not just the obvious one):

| Where                          | What to add                                                                   |
| ------------------------------ | ----------------------------------------------------------------------------- |
| `scripts/stage-publication.js` | `'parent.html'` in `topLevelFiles`                                            |
| `scripts/bundle-css.js`        | `'parent.css'` in the `pages.css` bundle list                                 |
| `scripts/prerender.js`         | `{ file: 'parent.html', route: { view: 'parent' }, … }` in `TOP_LEVEL_ROUTES` |
| `tests/internal-nav.test.js`   | `parent.html` in **both** `STATIC_PAGES` and `expectedTopLevel`               |

**Test additions:**

- `tests/router.test.js`: add a `parseRoute('/parent')` test that returns `{ view: 'parent' }`
- `tests/router.test.js`: add a `routeToPath({ view: 'parent' })` test that returns `/parent`

### Design constitution constraints (binding)

- Palette: Obsidian / Slate / Ceramic / Teal + per-project accent. The 9 per-agent cards each use the agent's own accent (jcode=teal, codex=violet, etc.) if available, or fall back to Teal.
- Fonts: Inter (body), Space Grotesk (display), JetBrains Mono (snapshot JSON, status pills, evidence chips)
- Voice: third-person, past/present, evidence-led. NO "passionate" / "rockstar" / "driven" / "results-oriented" adjectives anywhere.
- Status pills: `o` historical, `D` current, `O` research. The per-agent state pills use these glyphs.
- ASCII status widgets: the 15-min snapshot frame uses the status widget recipe from `phenotype-design-constitution` § 8.1 (ramp blocks + status labels).
- WCAG 2.2 AA: contrast, focus rings, 24px touch targets, reduced-motion respected for the 15-min refresh indicator.
- Bundle: keep the total under the 230 KB convention. **Corrected 2026-10-15:** lazy-loading `parent.js` was originally specified as a _requirement_, on the premise that the bundle sat at 228.7 KB and the new view would push it over. Measured, the bundle is 212.3 KB and the new view adds ~2.5 KB, so lazy-loading is **not required for budget reasons**. It remains a reasonable code-splitting/first-paint choice, but the design no longer depends on it.

### `/parent/` view structure (proposed)

The `/parent/` view is a **consolidated dashboard for a single human
operator (Koosha)**. It is the _parent of all context_ in the platform.

```
+----------------------------------------------------------+
| HEADER (atelier-header, same chrome as other views)      |
|  Work  Resume  Contact  Parent            Reader  Lens  |
+----------------------------------------------------------+
| MAIN (view-root)                                         |
|                                                          |
|  ## Parent View                                          |
|  Last refreshed: 14m23s ago  [Refresh now]               |
|                                                          |
|  ### 9-Agent Strip                                       |
|  [jcode] [hermes] [vp] [instinct] [codex] [kcode]        |
|  [winremote] [engineer-general] [engineer-specialist]    |
|                                                          |
|  ### 15-min Snapshot                                      |
|  o  agentcom-inbox: nominal                             |
|  D  herdr focused pane: jcode                            |
|  o  paperclip open issues: 6                            |
|  O  opencode-go quota: 100% (resets 2026-10-18)         |
|  D  CF Workers: agentcom-inbox, agentcom-discord ready   |
|                                                          |
|  ### Feed (recent activity, in chronological order)     |
|  [embedded portfolio cards from existing case studies]  |
|                                                          |
+----------------------------------------------------------+
```

**Agent card content (per the 9 paperclip agents):**

- Agent name (Inter, h3, with glyph-prefixed status pill)
- Last activity timestamp (JetBrains Mono, mono caption)
- Current task / focus (Inter, body)
- Open issues count (JetBrains Mono, evidence chip)
- ASCII status indicator (4-character ramp: `....` / `:::.` / `###.` / `###`)

**Snapshot content (data sources):**

**Data path (proposal):** browser -> same-origin `/api/parent/*` (behind Cloudflare Access) -> server-side proxy -> sources. The proxy holds any Access service token and the operator's API keys server-side; the static client bundle never sees credentials. Full design: "Data path (proposal; gated on B-REPO)" below.

All sources below execute **server-side** (see **Data path**); the browser only ever fetches the rendered snapshot JSON.

- agentcom-inbox health (via `/api/parent` proxy) → CF Worker health probe or paperclip issue count
- herdr focused pane (via `/api/parent` proxy) → herdr state API (operator's local TUI multiplexer; requires a network-reachable bridge - unverified, see 07)
- paperclip open issues (via `/api/parent` proxy) → `GET /api/issues?assigneeAgentId=...` on `paperclip.phenotype.space` (or all open)
- opencode-go quota (via `/api/parent` proxy) → `GET https://opencode.ai/zen/go/v1/usage` with the operator's API key (server-side only; never expose the key to the browser)
- CF Workers health (via `/api/parent` proxy) → cloudflare API or paperclip-reported worker status

**Feed content:**

- Recent commits across all `KooshaPari/*` repos (last 7 days, public only)
- Recent paperclip activity (issues filed, status changes)
- Recent portfolio blog posts (already rendered in `/blog`)


## Data path (proposal; gated on B-REPO)

Status: proposal. Creating the service token and deploying the handler are access/credential changes: **the operator creates the CF Access service token himself (operator step, not delegated to the agent)**; the agent ships only handler code and docs.

| Item | Decision |
|---|---|
| Browser call | `GET https://dash.kooshapari.com/api/parent/{agents,issues,snapshot}` same-origin, carries the operator's existing Access cookie. No third-party origin from the browser. |
| Handler (default) | Cloudflare Worker bound to route `dash.kooshapari.com/api/parent/*`, source in the target repo under `workers/parent-proxy/` (`wrangler.toml` + `src/index.ts`). Runs behind the same Access application as the site, and verifies the `Cf-Access-Jwt-Assertion` header (audience + team domain) before doing anything; reject otherwise. |
| Alternative | Vercel serverless function `api/parent/[...path].js` if the site stays on Vercel. Same checks; the Access JWT must still be verified because Vercel is not itself Access-aware. Choose Worker unless the repo decision (B-REPO) makes Vercel the only host. |
| Upstreams (allowlist, GET only) | Paperclip `/api/agents`, `/api/issues` at `paperclip.phenotype.space` (authoritative hostname, resolved 2026-10-15 - route-level evidence: desk quadlet `PAPERCLIP_PUBLIC_URL` + `PAPERCLIP_ALLOWED_HOSTNAMES`); opencode-go usage; herdr state. Any other path returns 404. |
| Secrets binding | Worker secrets (`wrangler secret put`), never in repo, never in the client bundle: `PAPERCLIP_ACCESS_CLIENT_ID`, `PAPERCLIP_ACCESS_CLIENT_SECRET` (Cloudflare Access service token sent as `CF-Access-Client-Id/Secret` to Paperclip's Access app), `OPENCODE_GO_API_KEY`, plus plain vars `ACCESS_TEAM_DOMAIN`, `ACCESS_AUD`. The service token itself is created by the operator (access change), scoped to the Paperclip Access app with a Service Auth policy only, 1 year expiry, rotation noted in 06_DECISION_LOG. |
| Cache | 60 s edge cache per path so the 15-min refresh cannot hammer upstreams; response carries `fetched_at`. |
| Failure | Upstream error returns `{state:"unavailable", fetched_at}`, never an empty list (matches the Tracera honest-states rule). UI shows the static roster marked "stale". |
| Tests | Unit: rejects missing/invalid JWT; rejects non-allowlisted path; strips upstream auth headers from response. Bundle check: grep shipped assets for `CLIENT_SECRET`/key patterns, must be zero. |

If B-REPO resolves to job-cockpit (Python), replace the Worker row with a route in that app's server (reads secrets from its env), keeping every other row.

---

### Acceptance criteria (Phase 1, `koosha-phenotype`)

- [ ] `dash.kooshapari.com/` renders the `/parent/` view (either as default route or via redirect from `/`).
- [ ] `/parent/` shows the 9-agent strip. **Corrected 2026-10-15:** P6 default: static roster (`data/phenotype.js`) plus a build-time snapshot. Live state is served only through the same-origin `/api/parent/*` proxy described in 03 "Data path", which is a proposal pending operator approval of the Access service token. Direct client-side calls to Paperclip are not viable.
- [ ] `/parent/` shows the 15-min snapshot with last-refreshed timestamp.
- [ ] Shipped bundle contains no secret or Access service token (grep the deployed assets for `CF-Access-Client`).
- [ ] The 15-min refresh ticks visibly (manual refresh button + auto-refresh).
- [ ] ASCII status widgets used in the snapshot frame.
- [ ] All existing portfolio routes still work (`/`, `/engineering`, `/product`, `/work`, `/work/:slug`, `/resume`, `/contact`, `/blog`, `/blog/:slug`, `/archive`).
- [ ] The design constitution is honored: monochrome ink palette, Inter/Space Grotesk/JetBrains Mono, evidence-led voice, WCAG 2.2 AA, glyph-prefixed status pills, ASCII widgets.
- [ ] Total bundle <= 230 KB minified. Lazy-loading of `parent.js` is **optional** (see the corrected bundle note above), not a gate.
- [ ] Unit tests pass (`npm test`); e2e tests pass (`npm run test:e2e`); `npm run verify` is green.
- [ ] Cloudflare Access is intact (no auth regression on `dash.kooshapari.com`).
- [ ] Branch: `feature/cockpit-parent-view` in `koosha-phenotype`.
- [ ] PR title (plain, per 2026-10-12T23:48Z amendment): `koosha-phenotype: add /parent/ view as default landing` — heavy/architecture work MUST NOT include the `[Instinct]` prefix.
- [ ] PR body first line: "Authored by Instinct" (remains binding for ALL PRs — the 2026-10-12T23:48Z amendment is title-scoped only).

---

## Data path (proposal — requires owner approval before any credential is created)

- Browser -> same-origin `/api/parent/*` endpoints on `dash.kooshapari.com` (already behind Cloudflare Access).
- A server-side worker/proxy on dash holds the Access service token (`CF-Access-Client-Id` / `CF-Access-Client-Secret` in server secrets, never shipped to the client) and fans out to the upstreams: Paperclip (`https://paperclip.phenotype.space`, `/api/agents`, `/api/issues`), the herdr state API, and opencode-go usage.
- The static roster in `data/phenotype.js` remains the offline fallback when the proxy or an upstream is unavailable.
- Creating the service token and the proxy is a credential/access change: this section is a **proposal only** and no token is created here.

## Phase 2 — Agent-facing surface (MCP + CLI + skill) in `Tracera`

### MCP server (`crates/tracera-mcp`)

- Already exists as `tracera-mcp` (Rust) + `tracertm-mcp` (Python legacy).
- Augment with: tools that map to `/parent/` view primitives:
  - `list_agents()` — list the 9 paperclip agents with their current state
  - `get_agent_state(agent_id)` — get one agent's live state
  - `list_open_issues(filter)` — list paperclip issues
  - `file_issue(title, body, assignee, priority)` — create a new paperclip issue
  - `get_quota()` — proxy to opencode-go `/v1/usage` (server-side, with operator's API key)
  - `get_cf_worker_health(worker_name)` — check CF Worker status
  - `get_herdr_focused_pane()` — proxy to the herdr state API
- Run mode: stdio by default, streamable-HTTP wrapper on `:8081` (existing `task-mcp-server` Makefile target).

### CLI (`crates/tracera-cli` + `crates/tracera-go-cli`)

- Rust CLI is the canonical (matches the cargo workspace).
- Go CLI is for users who don't want to compile Rust.
- Add subcommands: `tracera agent list`, `tracera agent get <id>`, `tracera issue list`, `tracera issue create`, `tracera view parent` (opens `/parent/` in browser), `tracera refresh`, `tracera quota`.

### Skill / plugin surface

- A `tracera` skill (or `tracera-cli` skill) is registered in the harness's skill catalog so any agent (jcode, codex, kcode, helioslite) can pick it up.
- The skill teaches the agent: how to discover agents, how to file issues, how to read the `/parent/` view, how to set the focused pane.

### Acceptance criteria (Phase 2, `Tracera`)

- [ ] MCP tools listed above are implemented and tested (`cargo test`).
- [ ] CLI subcommands work end-to-end.
- [ ] Skill is registered in the harness's skill catalog.
- [ ] Branch: `feature/cockpit-agent-mcp` (or split into 3 branches per concern).
- [ ] PR titles (plain, per 2026-10-12T23:48Z amendment): `Tracera-mcp: ...`, `Tracera-cli: ...`, `Tracera: register tracera skill` — Phase 2 design-defining work, `[Instinct]` prefix not permitted.

---

## Phase 3 — Personal-mode extensions (in `koosha-phenotype` + `paperclip`)

> "Tracera/Paperclip for personal — spec+work management and agent
> orchestration for his whole life, not just jobs."

The smallest viable cut:

- A new `kind: "personal"` flag on paperclip issues (vs the existing `kind: "job"`). Schema change in `paperclip`.
- A `/parent/personal` subroute in `koosha-phenotype` that filters paperclip issues by `kind=personal`.
- The same 9 agents can be assigned to personal issues; the routing doesn't change.
- A `paperclip` skill that teaches agents the personal-issue model.

### Acceptance criteria (Phase 3)

- [ ] paperclip schema accepts `kind: "personal"`.
- [ ] `/parent/personal` renders filtered issues.
- [ ] Skill is registered.
- [ ] Branch: `feature/cockpit-personal-mode` in `koosha-phenotype`; `feature/cockpit-personal-kind` in `paperclip`.

---

## Out of scope (for this refresh)

- Replacing the portfolio's existing brand identity (Phenotype trademark, voice, palette) — the design constitution is binding.
- Refactoring the SPA to a framework (React, Vue, Svelte) — koosha-phenotype is a vanilla-JS SPA, that paradigm is preserved.
- Migrating `cockpit-source` (the local Python dashboard) — separate project, not the same cockpit.
- Building a new MCP tool from scratch — augment the existing `tracera-mcp`.
- A new product identity (Tracera's branding is fine for the agent surface).
