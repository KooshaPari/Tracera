# PR Pipeline — branch / commit / PR conventions (revision 2 — per-repo)

## Source repos (in scope)

| Repo                                                            | Domain                                      | Branch base                                                     | Vercel/CF deploy                                                                   |
| --------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `koosha-phenotype` (remote `KooshaPari/KooshaPari.git`)         | Web app at `dash.kooshapari.com`            | `main` (operator's in-flight is on `feat/dimensional-layering`) | Vercel `kooshapari-site`                                                           |
| `Tracera` (remote `KooshaPari/Tracera.git`)                     | Agent-facing surface (MCP/CLI/skill)        | `main`                                                          | Vercel + CF Worker `tracera-edge`                                                  |
| `paperclip` (separate, in `~/CodeProjects/Phenotype/repos/...`) | Issue model + orchestration                 | `main` (TBD)                                                    | Local:3180 (dev) + `paperclip.phenotype.space/api` (prod, behind Cloudflare Access; hostname corrected 2026-10-15 - see 02/05) |
| `harness-ops`                                                   | CF Workers (inbox receiver, Discord bridge) | `main`                                                          | CF Workers (`agentcom-inbox`, `agentcom-discord`)                                  |

**Out of scope:** `cockpit-source` (local Python dashboard, separate project).

## Branch naming (per repo)

### `koosha-phenotype` (Phase 1 + 3 + 4)

- `feature/cockpit-parent-view` — Phase 1 (SINGLE phase since revision 3 / D11: `/parent/` view + AppShell + 15-min refresh + per-agent state; one branch, not split)
- `feature/cockpit-personal-mode` — Phase 3: `/parent/personal` route
- `fix/cockpit-*` — small fixes

### `Tracera` (Phase 2)

- `feature/cockpit-agent-mcp` — Phase 2: MCP server tools
- `feature/cockpit-agent-cli` — Phase 2: CLI subcommands
- `feature/cockpit-agent-skill` — Phase 2: skill/plugin surface
- `fix/cockpit-*` — small fixes

### `paperclip` (Phase 3 issue model)

- `feature/cockpit-personal-kind` — Phase 3: add `kind: "personal"` to issues

### `harness-ops` (when ready)

- `fix/agentcom-*` — small fixes to existing Workers
- `feat/agentcom-discord-inbound` — when operator approves the design

## Commit format

Follow each repo's existing convention. **Required trailers (operator's standing rule):**

```
tx-agent:     jcode
tx-task:      PHE-N (or GitHub issue #N)
tx-scope:     <affected components>
tx-intent:    <one-line what this achieves>
tx-validated: lint|test|build|cargo-check|manual|none
```

## PR title convention

Per the 2026-10-12T23:48Z amendment: heavy/architecture PRs are titled
with a plain title and do **NOT** include the `[Instinct]` tag.
Light/marketing/legibility PRs **MAY** use `[Instinct]` in the title.
The other 8 directives from 2026-10-12T22:33Z remain binding (including
"Authored by Instinct" as the first line of the PR body — see below).

Examples (heavy/architecture; plain titles per 2026-10-12T23:48Z amendment):

- koosha-phenotype: add /parent/ view as default landing
- koosha-phenotype: AppShell with 15-min refresh + per-agent state
- Tracera-mcp: add agent list / get / issue file tools
- Tracera-cli: add agent list, issue create, view parent, quota subcommands
- paperclip: add kind=personal for whole-life issue model

Light/legibility PRs MAY use the `[Instinct]` prefix instead of a plain
title (e.g. `[Instinct] docs: fix cockpit onboarding typos`).

## PR body — first line

Every PR body starts with:

> Authored by Instinct

then the rest of the description.

## Force-push

- **No force-push** to any published branch.
- No `git push --force`, no `--force-with-lease`, no `git reset --hard`.
- If a branch needs cleanup, open a follow-up PR that rebases via merge
  commit (`git pull --rebase=false` from `main`), or close + reopen.

## Cloudflare Access

- All deploys to `dash.kooshapari.com` (and any preview URL) stay behind
  Cloudflare Access. The auth boundary is the edge.
- Do not change the CF Access policy in code; that's an operator-side
  setting in the CF dashboard.

## Deploy mechanics (per repo)

### `koosha-phenotype` deploy

- Vercel project `kooshapari-site` is owned by the operator.
- `vercel deploy` or `vercel --prod` from the operator's auth context.
- **Subagent cannot deploy** without Vercel auth; the subagent produces the
  PR; the operator runs the deploy.

### `Tracera` web deploy

- Vercel project (TBD — same as `tracera-edge`?). Currently
  `tracera-edge.pheno.studio` is the edge worker; the main app
  is at `tracera.pheno.studio`. _(Corrected 2026-10-15: `tracera.pheno.studio` is **Tracera's**
  API, not paperclip's. Paperclip's public endpoint is `paperclip.phenotype.space` (corrected 2026-10-15 from `paperclip.kooshapari.com`; route-level evidence in `05_BLOCKERS.md` P6), behind
  Cloudflare Access — see `02_CURRENT_STATE.md`.)_
- Subagent produces the PR; operator deploys.

### `harness-ops` CF Workers deploy

- `wrangler deploy` after `wrangler secret put` for each secret.
- Subagent cannot deploy (no CF API token); operator deploys.

## Subagent dispatch (when quota is unblocked)

When the opencode-go quota resets (or wA:p4 key proxy lands) and a
subagent can be dispatched:

- **One agent per repo.** For Phase 1, the subagent works in
  `koosha-phenotype`. For Phase 2, in `Tracera`. Never both.
- Branch the work from `main` and open the PR against `main`.
- Title the PR per the 2026-10-12T23:48Z amendment: plain title for
  heavy/architecture work, `[Instinct]` optional for light/legibility work.
- Use mimo-v2.6-flash (or whatever the current standing default is at
  dispatch time) per the routing policy.
- Provide a self-contained prompt that includes:
  - The Phase scope (1 / 2 / 3 / 4) and the target repo
  - The acceptance criteria from `03_PROPOSED_DESIGN.md`
  - The PR pipeline rules (this file)
  - The branch name from the table above
  - The tx-agent trailer template
  - **CRITICAL: read 00_SESSION_OVERVIEW.md "Reframed scope" first — the
    "naive tab system" the directive preemptively forbids does NOT exist in
    the codebase (current top-nav is `Work | Resume | Contact`). Design
    `/parent/` as the richer consolidated view. Do NOT hunt for a tab system
    to replace. Inspecting the deployed top-nav through CF Access is
    **optional, not a prerequisite\*\* — the wall is authenticated, so if access
    is unavailable, fall back to operator-provided evidence or the documented
    local state (the nav list in 02_CURRENT_STATE.md) and say which you used.

## PR review

- Self-review before requesting review (no `gh pr ready` until self-review
  is done).
- Wait for operator review; do not auto-merge.
- The merge itself is the operator's call.

## Local origin safety (revision 2)

- `koosha-phenotype` remote = `git@github.com:KooshaPari/KooshaPari.git` (the public `KooshaPari` org repo). Verify before `git push` — this is a public repo.
- `Tracera` remote = `git@github.com:KooshaPari/Tracera.git`. Public.
- `harness-ops` remote = local-only (no public push).
- No local-origin collisions (the rename to `job-cockpit` for `cockpit-source` is documented in a prior session; that fix is still in effect for the cockpit-source side).
