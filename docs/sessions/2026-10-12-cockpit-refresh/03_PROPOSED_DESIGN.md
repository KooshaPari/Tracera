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

| Repo | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| `koosha-phenotype` | `/parent/` view + AppShell + 15-min refresh + 9-agent state | (read-only) | `/parent/personal` subroute |
| `Tracera` | (none) | MCP/CLI/skill surface for `/parent/` data sources | (none) |
| `paperclip` | (none) | (none) | `kind: "personal"` schema + routing |

The two are wired together: `koosha-phenotype` reads paperclip issues
(via `tracera.pheno.studio/api`) and calls Tracera's MCP/CLI for
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

| File | Change | Lines (est.) |
|------|--------|-------------:|
| `scripts/router-helpers.js` | Add `'parent'` to `VIEW_ROUTES`; add 2 if-branches in `parseRoute` and `routeToPath` | +6 |
| `scripts/router.js` | No change | 0 |
| `scripts/app.js` | Add `import { renderParent } from './views/parent.js'`; wire `route.view === 'parent'` in the render dispatch; (optionally) change default landing to `/parent` | +5 |
| `scripts/components/shell.js` | Add `['/parent', 'Parent']` to `ROUTES` (the top nav) | +1 |
| `vercel.json` | Add `{ "source": "/parent", "destination": "/parent.html" }` rewrite | +3 |
| `styles/bundled/pages.css` (or new `parent.css`) | Per-view styles, ASCII status widget, 9-agent grid, 15-min refresh indicator | +150 |
| `data/phenotype.js` | (optionally) extend `IDENTITY` with a 9-agent roster sourced from paperclip's `/api/agents` | +20 (or none, if data is fetched at runtime) |

**Files to create:**

| File | Role | Lines (est.) |
|------|------|-------------:|
| `scripts/views/parent.js` | The `/parent/` view: orchestrator (mounts the 9-agent strip, the 15-min snapshot, the feed) | 300-500 |
| `scripts/views/parent-helpers.js` | Per-agent card renderer, snapshot fetcher, ASCII widget helpers | 200-400 |
| `tests/parent.test.js` | Unit tests for the route parser and parent view helpers | 100-200 |
| `tests/e2e/parent.spec.js` | E2E test: navigate to `/parent/`, verify 9 cards render, verify 15-min timer exists | 50-100 |

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
- Bundle: keep the total under the 230 KB convention. **Corrected 2026-10-15:** lazy-loading `parent.js` was originally specified as a *requirement*, on the premise that the bundle sat at 228.7 KB and the new view would push it over. Measured, the bundle is 212.3 KB and the new view adds ~2.5 KB, so lazy-loading is **not required for budget reasons**. It remains a reasonable code-splitting/first-paint choice, but the design no longer depends on it.

### `/parent/` view structure (proposed)

The `/parent/` view is a **consolidated dashboard for a single human
operator (Koosha)**. It is the *parent of all context* in the platform.

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
- agentcom-inbox health → CF Worker health probe or paperclip issue count
- herdr focused pane → herdr state API (operator's local TUI multiplexer)
- paperclip open issues → `GET /api/issues?assigneeAgentId=...` (or all open)
- opencode-go quota → `GET https://opencode.ai/zen/go/v1/usage` with the operator's API key (server-side only; never expose the key to the browser)
- CF Workers health → cloudflare API or paperclip-reported worker status

**Feed content:**
- Recent commits across all `KooshaPari/*` repos (last 7 days, public only)
- Recent paperclip activity (issues filed, status changes)
- Recent portfolio blog posts (already rendered in `/blog`)

### Acceptance criteria (Phase 1, `koosha-phenotype`)

- [ ] `dash.kooshapari.com/` renders the `/parent/` view (either as default route or via redirect from `/`).
- [ ] `/parent/` shows the 9-agent strip with live state per agent.
- [ ] `/parent/` shows the 15-min snapshot with last-refreshed timestamp.
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
