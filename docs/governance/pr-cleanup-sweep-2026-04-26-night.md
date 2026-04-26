# PR Cleanup Sweep — 2026-04-26 (Night)

**Scope:** API-only sweep across `org:KooshaPari` open PRs. No clones, no fs walks.

## Summary

| Metric | Count |
|---|---|
| Total open PRs (org-wide) | 20 |
| Archived/disabled repos hit | 0 |
| Mergeable=true | 20 |
| Mergeable=CONFLICTING | 0 |
| Stale (>30 days) | 0 |
| Closures executed | 0 |

All 20 open PRs were created **today (2026-04-26)** during the active session sweep. None are stale. No repo in scope is archived or disabled.

## Mergeable Candidates (manual approval)

Mergeable state `unstable` = passing required checks, but non-required checks pending/failing (CI billing-blocked is expected per global policy). Safe to admin-merge per global "CI billing-blocked != blocking" rule.

| PR | Author | Title |
|---|---|---|
| KooshaPari/pheno#84 | KooshaPari | deps(python): bump pytest >=8.0 → >=9.0.3 |
| KooshaPari/pheno#83 | KooshaPari | deps(agileplus-mcp): bump pytest >=8.0 → >=9.0.3 |
| KooshaPari/AuthKit#47 | KooshaPari | deps(dev): bump pytest 8→9.0.3, black 24→26.3.1 |
| KooshaPari/Civis#253 | KooshaPari | round-7a: post-rebase reconcile (READMEs upstream-canonical) |
| KooshaPari/Tracera#362 | KooshaPari | ci: align Python workflows with 3.13 |
| KooshaPari/phenodocs#74 | KooshaPari | deps(go): bump golang.org/x/net 0.20.0 → 0.38.0 |
| KooshaPari/PhenoProject#6 | KooshaPari | deps(python): bump pytest 7.4.0 → 9.0.3 |
| KooshaPari/PhenoProject#5 | KooshaPari | deps(python): security patch bumps base.txt |
| KooshaPari/FocalPoint#5 | KooshaPari | deps(rust): bump jsonwebtoken 9.3 → 10.3.0 |
| KooshaPari/PhenoLang#18 | KooshaPari | tier-2 CVE sweep — agileplus-mcp/pyproject.toml |
| KooshaPari/KDesktopVirt#8 | KooshaPari | tier-2 CVE sweep — Cargo.toml |
| KooshaPari/PhenoLang#17 | KooshaPari | tier-2 CVE sweep — python/pyproject.toml |
| KooshaPari/PhenoLang#16 | KooshaPari | tier-2 CVE sweep — Cargo.toml lru 0.12 → 0.16 |
| KooshaPari/Tracera#361 | dependabot[bot] | bump rollup 0.34.7 → 2.80.0 (npm_and_yarn) |

Suggested merge: `gh pr merge <#> --squash --admin --delete-branch -R <repo>`.

## Blocked Candidates (mergeable_state=blocked)

Branch-protection-blocked, likely required reviews on `phenoShared`. Need branch-protection adjustment or `--admin` override:

| PR | Title |
|---|---|
| KooshaPari/phenoShared#111 | fix(js): align Bun workspace metadata |
| KooshaPari/phenoShared#110 | fix(config): restore config core validation |
| KooshaPari/phenoShared#109 | feat(errors): add dual-interface contracts |
| KooshaPari/phenoShared#108 | chore(gitignore): add .worktrees/ entries |
| KooshaPari/phenoShared#107 | fix(crates): missing description fields |
| KooshaPari/phenoShared#106 | fix(readme): document all 16 workspace members |

These form a dependency stack — should merge bottom-up: 106 → 107 → 108 → 109 → 110 → 111.

## Closures

**None.** No archived-repo PRs, no stale PRs, no superseded duplicates identified. Closure cap (30) not approached.

## Conflicting Candidates (rebase needed)

**None.** All PRs report `mergeable=true`.

## Blockers / Notes

- `mergeable_state=unstable` across the board reflects CI billing constraint (KooshaPari Actions billing exhausted), not real failures. Per `~/.claude/CLAUDE.md`, do not block on this — admin-merge after local quality verification.
- phenoShared stack (#106-#111) needs sequential merge to avoid rebase storms.
- Single bot PR: Tracera#361 (rollup bump in `/ARCHIVE/CONFIG/...` path — verify path is not in active build before merge).
