# Overall Audit Snapshot - 2026-04-26

## Scope

- Workspace: `/Users/kooshapari/CodeProjects/Phenotype/repos`
- GitHub owner scope: `KooshaPari/*`
- Commands used: `gh search prs`, `gh search issues`, `gh issue view`, local `git status`

## Executive State

- Open PRs across `KooshaPari/*`: 0
- Open issues across `KooshaPari/*`: 1,999
- Critical security issues: 2
- Highest-risk active blocker: private sibling dependency routing for `PhenoObservability` cargo-deny.

## Priority Backlog

### P0 - Security Alerts

1. `KooshaPari/pheno#25`
   - URL: https://github.com/KooshaPari/pheno/issues/25
   - Source: Trivy / CodeQL sync
   - Severity: critical
   - CVE: `CVE-2026-32871`
   - Next action: inspect security alert details and dependency tree, patch or route duplicate with `pheno#18`.

2. `KooshaPari/agentapi-plusplus#437`
   - URL: https://github.com/KooshaPari/agentapi-plusplus/issues/437
   - Source: Trivy / CodeQL sync
   - Severity: critical
   - CVE: `CVE-2025-55182`
   - Next action: inspect security alert details and dependency tree, patch dependency, then open a narrow PR.

### P1 - CI Governance Blocker

1. `KooshaPari/PhenoObservability#27`
   - URL: https://github.com/KooshaPari/PhenoObservability/issues/27
   - Problem: `cargo-deny` cannot resolve private sibling path dependency `KooshaPari/phenotype-bus` with default Actions token.
   - Required decision: read-only cross-repo token, dependency routing change, or CI context with full workspace checkout.
   - Prior PR: `#26`, closed as non-landable after blocker was ported.

### P2 - Main-Branch CI Backlog

Largest generated CI issue clusters from the first 1,000 open issues:

| Repo | Open Issues | CI Issues | CodeQL Issues | Critical | High |
| --- | ---: | ---: | ---: | ---: | ---: |
| `helios-cli` | 239 | 18 | 0 | 0 | 0 |
| `portage` | 219 | 8 | 0 | 0 | 0 |
| `heliosBench` | 120 | 0 | 0 | 0 | 0 |
| `helios-router` | 95 | 0 | 0 | 0 | 0 |
| `Tracera` | 67 | 24 | 0 | 0 | 0 |
| `cliproxyapi-plusplus` | 44 | 0 | 0 | 0 | 0 |
| `heliosCLI` | 37 | 17 | 0 | 0 | 0 |
| `agentapi-plusplus` | 35 | 7 | 8 | 1 | 3 |
| `QuadSGM` | 28 | 8 | 0 | 0 | 0 |
| `HexaKit` | 26 | 14 | 12 | 0 | 1 |
| `phenoRouterMonitor` | 25 | 25 | 0 | 0 | 0 |
| `pheno` | 20 | 13 | 7 | 1 | 6 |

### P3 - Local Dirty Worktrees

Top dirty local repos by tracked file count:

| Repo | Count | Notes |
| --- | ---: | --- |
| `phenodocs` | 45 | Deleted VitePress `.vitepress/.temp/*` generated files. |
| `PhenoProc` | 16 | Mostly modified nested crate/worktree pointers. |
| `Tracely` | 9 | Docs/spec/Cargo/worklog drift. |
| `FocalPoint` | 8 | iOS generated FFI artifacts plus docs-site guide. |
| `bare-cua` | 6 | Needs local classification. |
| `Civis` | 5 | Needs local classification. |
| `kwality` | 5 | Needs local classification. |
| `PhenoDevOps/agent-devops-setups` | 5 | Needs local classification. |

## Recommended Execution Order

1. Patch or close/duplicate-route the two critical Trivy issues.
2. Resolve `PhenoObservability#27` by choosing a dependency-access model before recreating cargo-deny PR.
3. Clean local dirty generated-file drift starting with `phenodocs`, then classify `PhenoProc` nested repo pointer drift.
4. Reduce auto-alert issue noise by picking one CI cluster family at a time: `pheno`, `HexaKit`, then `heliosCLI`/`helios-cli`.
5. Refresh this dashboard after each batch; do not treat issue count reduction as success unless main checks or security alert states actually change.
