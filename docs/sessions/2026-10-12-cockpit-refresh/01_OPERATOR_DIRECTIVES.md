# Operator Directives — verbatim

**Channel:** chat (typed operator signal, 2026-10-12T22:33:41.794Z)
**Author:** Koosha Pari (operator)
**Mode:** captured verbatim for trace-link

> USER DESIGN DIRECTIVES for cockpit overhaul (fold into the refresh PR
> work):
> (1) dash.kooshapari.com must land on the /parent/ view FIRST, not the
> basic tab system; replace the naive tabs with a richer unified platform
> design.
> (2) Agent-facing interfaces: MCP server, CLI, skill/plugin surface so
> agents can trivially work with it.
> (3) Long-term shape: Tracera/Paperclip for personal - spec+work
> management and agent orchestration for his whole life, not just jobs.
> Keep 15-min refresh + per-agent state.
> Plan first, then PRs titled [Instinct], Authored by Instinct first
> line, no force-push; everything stays behind Cloudflare Access.

**Amendment (2026-10-12T23:48Z, by the operator):** The "PRs titled `[Instinct]`" sub-clause above is title-scoped — heavy/architecture PRs use plain titles; the `[Instinct]` prefix MAY be used for light/legibility PRs. The other directives in this block (including "Authored by Instinct" first line) remain binding.

## Decomposition (operator signal → 9 directives)

| #   | Directive                                                                                                                                                                                             | Phase              | Repo                                                                                                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1   | `/parent/` view is the FIRST landing page                                                                                                                                                             | Phase 1            | `koosha-phenotype`                                                                                                  |
| 2   | NOT the basic tab system                                                                                                                                                                              | Phase 1 (replaced) | `koosha-phenotype`                                                                                                  |
| 3   | Replace naive tabs with unified platform design                                                                                                                                                       | Phase 1            | `koosha-phenotype`                                                                                                  |
| 4   | MCP server agent surface                                                                                                                                                                              | Phase 2            | `Tracera` (`crates/tracera-mcp`)                                                                                    |
| 5   | CLI agent surface                                                                                                                                                                                     | Phase 2            | `Tracera` (`crates/tracera-cli` / `tracera-go-cli`)                                                                 |
| 6   | Skill/plugin agent surface                                                                                                                                                                            | Phase 2            | `Tracera` (skill catalog)                                                                                           |
| 7   | Tracera/Paperclip for personal (whole life, not jobs)                                                                                                                                                 | Phase 3            | `paperclip` issue model + `koosha-phenotype` UI                                                                     |
| 8   | Keep 15-min refresh + per-agent state                                                                                                                                                                 | Phase 1 (merged)   | `koosha-phenotype` AppShell — revision 3 folded the old Phase 4 into Phase 1 (D11), so there is no separate Phase 4 |
| 9   | Plan first, PR titles per 2026-10-12T23:48Z amendment (plain for heavy/architecture, `[Instinct]` optional for light/legibility), "Authored by Instinct" first line, no force-push, Cloudflare Access | Meta (Phase 0)     | all repos                                                                                                           |

## What the operator did NOT say (do not invent)

- The visual / layout of `/parent/` — left to design phase
- Which Tracera pages to consolidate under `/parent/` — left to design
- The exact MCP tool surface — must match the CLI / skill surface
- The refresh interval exact source (15-min tick? cron? job queue?)
- Where Paperclip fits into the personal-mode extension
