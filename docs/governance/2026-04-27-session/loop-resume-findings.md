# Loop resume findings (2026-04-27 post-compact)

## Spec 021 ground truth

`AgilePlus/kitty-specs/021-polyrepo-ecosystem-stabilization/tasks.md` is **186 checkboxes across Phase 1-5** (worker initially saw a truncated 16-line snippet — fabricated). Real phase content:

| Phase | Theme | Status (per memory) |
|-------|-------|---------------------|
| P1.1 | Merge PRs #544-563 | DONE (13 merged + 3 closed + 3 not-found) — stale checkboxes |
| P1.2 | Delete 8 typo/test repos | Most archived this session; verify Tokn (active, not truncated name) |
| P1.3 | 22 GB local cleanup | Done multiple times (target-pruner) |
| P1.4 | .gitignore on 9 repos | DONE (worktree-gitignore wave 17 repos task #526) |
| P1.5 | Org `.github` repo + 9 reusable workflows | UNCERTAIN — reusables exist in phenoShared, not org `.github` |
| P1.6 | Audit + enrich 35 specs | Partial; specs 013/014/016 enriched |
| P1.7 | Worktree discipline | DONE (canonical CLAUDE.md updates, repo-wtrees pattern) |
| P1.8 | cargo fmt + clippy on phenotype-infrakit | Likely done; phenotype-infrakit ≈ phenoShared today |
| P1.9 | Commit dirty across 9 repos | DONE (every-turn commit policy) |
| P1.10 | Canonical repos→main | DONE (most), heliosCLI now archived |
| P2.1 | 15 duplicate-repo merges → 8 targets | Partial: error-core/contracts done; FixitGo/FixitRs/forgecode-fork still open |
| P2.2 | Archive 4 odin-* | Verify via `gh api` |

**Net real outstanding:** ~30-40 checkboxes (mostly P3-P5 + remaining P2 dedup), not 186.

## agileplus-landing build delta

`astro.config.mjs` differs from siblings by ONE line: missing `base: process.env.GITHUB_PAGES === 'true' ? '/agileplus-landing' : '/'`. This is cosmetic (GH Pages base path) — not a build blocker.

Other 4 sibling configs are otherwise identical. Real build error requires capturing `bun run build` output (in flight). Hypothesis from worker: missing `@astrojs/node` adapter is implausible since 4 siblings build with same minimal config.

## Dependabot residuals plan (worker output, gpt-5-mini)

| Repo | Action class | Target |
|------|--------------|--------|
| heliosCLI (18) | bump root | reqwest latest stable |
| pheno (9) | replace transitive | switch to rustls-tls |
| HexaKit (8) | bump root | time/chrono latest |
| hwLedger (7) | deeper audit | crypto/ring/rsa review |
| PhenoRuntime (6) | bump root | hyper + tokio |
| KDesktopVirt (5) | replace transitive | rustls-tls swap |

Note: live `gh api dependabot/alerts` returned 0 for all 6 above — either limit reset closed them automatically (per user message "limit reset resume") or the per-repo counts are now stale. Re-snapshot in flight.

## Worker outcomes

- W1 agileplus-build (gemini-3-flash): hypothesis (adapter missing) implausible — discard
- W2 spec-021 (oswe-vscode-prime): saw truncated snippet, fabricated 16-line view — discard
- W3 spec-018 (kimi-k2.5/oss-120b): refused to read files — kimi cwd injection only adds to system prompt, doesn't grant file access
- W4 spec-020: kimi-coding rate-limit cooldown ("No credentials")
- W5 tracera#385 (gpt-5.5): correct diagnosis — needs `git fetch origin '+refs/pull/*:refs/remotes/origin/pr/*'` first
- W6 dependabot-residuals (gpt-5-mini): solid generic plan, in-flight verification needed

## Pattern: kimi `--cwd` adds context, NOT file access

Kimi worker explicitly said "I'm unable to read the contents of the repository files you referenced" — `--cwd` only injects path string into system prompt; does not give the worker shell/Read access. For file-grounded tasks, must use `worker` tier (gpt-5.5 / oswe-vscode-prime) which has tool-use, OR paste content into the prompt.
