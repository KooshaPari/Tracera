# Cockpit Refresh — Session Overview

**Date opened:** 2026-10-12T22:33Z
**Operator signal:** "USER DESIGN DIRECTIVES for cockpit overhaul (fold into the refresh PR work)"
**Mode:** plan-first → PRs
**Revision:** 3 (revised 2026-10-12T23:00Z — full SPA architecture understood, reframed as "portfolio → cockpit evolution"; Phase 1 + 4 merged; B6 resolved)

## Goal — portfolio → cockpit evolution

The deployed `dash.kooshapari.com` is a multi-page static site whose index.html hosts a vanilla-JS (no framework) client-routed shell; `/parent` is added as a new view in that shell plus a static `parent.html` entry
("Technical Atelier" — evidence-led, museum-quiet, designer-engineer
voice) that the operator is evolving into a unified cockpit. The
cockpit lands at `/parent/` first, replacing the "naive 4-tab default"
that the operator is preempting in the directive. The portfolio's
existing routes (`/`, `/work`, `/resume`, `/contact`, `/blog`, project
pages) continue to work as secondary nav.

## Hard constraints (operator directives, verbatim)

1. **`dash.kooshapari.com` must land on `/parent/` view FIRST**, not the basic
   tab system.
2. **Replace the naive tabs with a richer unified platform design.**
3. **Agent-facing interfaces:** MCP server, CLI, skill/plugin surface so
   agents can trivially work with it.
4. **Long-term shape:** Tracera/Paperclip for personal — spec+work
   management and agent orchestration for his whole life, not just jobs.
5. **Keep 15-min refresh + per-agent state.**
6. **Plan first, then PRs.**
7. **PR title policy (binding, 2026-10-12T23:48Z amendment — title-scoped ONLY; supersedes the original 22:33Z wording on the title clause only. The other 8 directives remain binding, including the "Authored by Instinct" PR-body first line, which applies to ALL PRs):** Heavy/architecture PRs (multi-file, design-defining, Phase 1/2/3 cockpit work, >800-line guideline) MUST use plain titles without the `[Instinct]` prefix. Light/small PRs (single-file bugfix, copy edit, typo fix) MAY use the `[Instinct]` prefix.
8. **No force-push.**
9. **Everything stays behind Cloudflare Access.**

## Reframed scope (revision 3)

The "naive tab system" does not exist in the current codebase. The
current top-nav is `Work | Resume | Contact` (with the blog link
commented out 2026-10-11) — no tabs. The operator's directive is
**preemptive**: don't build a 4-tab default; build `/parent/` first.

The cockpit refresh lands in **four repos** (the fourth, `harness-ops`, is out of refresh scope and carries no directive):

| Repo               | Owns                                                                                        | Operator's directive |
| ------------------ | ------------------------------------------------------------------------------------------- | -------------------- |
| `koosha-phenotype` | Web app at `dash.kooshapari.com` — `/parent/` view, AppShell, 15-min refresh, 9-agent state | (1), (2), (5)        |
| `Tracera`          | Agent-facing surface (MCP/CLI/skill)                                                        | (3)                  |
| `paperclip`        | Issue model (kind=personal schema)                                                          | (4)                  |
| `harness-ops`      | CF Workers (out of refresh scope; in-flight)                                                | n/a                  |

## Phase model (revision 3, merged)

- **Phase 0** — _plan + state audit_ (this document, revision 3)
- **Phase 1** — _`/parent/` view + AppShell + 15-min refresh + per-agent state_ (in `koosha-phenotype`)
  — directives (1), (2), (5); single phase, not split
- **Phase 2** — _MCP + CLI + skill/plugin agent surface_ (in `Tracera`)
  — directive (3)
- **Phase 3** — _personal-mode extensions_ (`paperclip kind=personal` schema + `/parent/personal` subroute)
  — directive (4)

## Visual foundation (binding, from `phenotype-design-constitution` skill)

- Voice: third-person, past/present tense, evidence-led ("approximately", "user-stated", "canonical user fact")
- Palette: Obsidian `#0F1012` / Slate `#353A40` / Ceramic `#F6F5F5` / Teal `#7EBAB5` + per-project accent (Tracera = violet `#7C3AED`)
- Fonts: Inter (body) + Space Grotesk (display) + JetBrains Mono (meta, evidence chips)
- WCAG 2.2 AA: contrast >= 4.5:1, focus rings, 24px touch targets, reduced-motion, skip-link
- Bundle <= 230 KB minified (measured 212.3 KB on 2026-10-14, ~17.7 KB headroom; 70.7 KB gzipped); 60fps parallax (transform + opacity only)
- Status pills: `o` historical, `D` current, `O` research
- ASCII widgets allowed (status widget, project spine, evidence chip)

The `/parent/` view must use this palette and font system, not invent new ones. The 9 per-agent cards and 15-min snapshot fit the "evidence-led, museum-quiet" voice — no promotional copy, no "passionate" / "rockstar" / "driven" / "results-oriented" adjectives. ASCII status widgets encouraged.

## Cross-references

- `01_OPERATOR_DIRECTIVES.md` — verbatim operator input (revision 2)
- `02_CURRENT_STATE.md` — what exists today (revision 3: full SPA architecture, design constitution, build pipeline)
- `03_PROPOSED_DESIGN.md` — what to build, per phase (revision 3: file-level implementation plan, Phase 1+4 merged)
- `04_PR_PIPELINE.md` — branch / commit / PR conventions (revision 2: per-repo)
- `05_BLOCKERS.md` — what's blocking (revision 3: B6 resolved, B5 reframed)
- `06_DECISION_LOG.md` — decisions made (revision 3: D10–D13; D14 added 2026-10-14: 23:48Z title-policy amendment)
- `MANIFEST.md` — canonical-vs-backup map + binding-policy recap (2026-10-14)
