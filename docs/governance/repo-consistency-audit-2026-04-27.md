# Repo Consistency Audit — 2026-04-27

API-only audit of KooshaPari org for repo-state vs metadata inconsistencies.
Scope: ~85 non-archived repos. Sampling depth: 10 repos full-probe, all repos branch+desc.
Method: `gh api` only, no clones. Search-API rate-limited mid-run (sub-crate go.mod/Cargo.toml grep partially limited).

## Inconsistencies by Category

### A. Default-branch anomalies (non-fork)

| Repo | default_branch | Issue |
|------|----------------|-------|
| `nanovms` | `docs` | README/CI/badges assume `main`; default branch is `docs`. High-confidence misconfig. |
| `DINOForge-UnityDoorstop` | `master` | Upstream fork, expected. No action. |
| `Planify` | `master` | Deprecated fork of Plane.so, expected. No action. |
| `PlayCua` | `master` | Marked deprecated fork, expected. No action. |

### B. Description vs README contradictions

| Repo | Description | README reality | Severity |
|------|-------------|----------------|----------|
| `phenoData` | "Pheno phenoData workspace" | Detailed: 3 crates (surreal-bridge, pg-bridge, pheno-query), Rust 1.84+, maintenance status | low — desc is lazy stub |
| `phenoUtils` | "Pheno phenoUtils workspace" | Detailed: CLI shell, fs, crypto, net, testing crates | low — desc is lazy stub |
| `phenoAI` | "Phenotype AI agent workspace and tooling" | Matches README | OK |
| `dinoforge-packs` | "Resource packs for DINOForge platform" | README self-flags prior README claimed archived (now corrected) | OK — already self-healed |
| `AgentMCP`, `phenotype-hub`, `vibeproxy-monitoring-unified` | Honest "placeholder/scaffold" | Match README | OK |

### C. Multiple module/package paths in same repo

- `PlatformKit`: 2 go.mod (`go/devhex/go.mod`, `go/devenv/go.mod`) — multi-module monorepo, README documents this. Consistent.
- Search API rate-limited before exhaustive Rust/Go scan; recommend follow-up audit with token rotation.

### D. Pattern signal (cross-cutting)

- "Lazy stub" descriptions (literally `Pheno X workspace`) on: `phenoData`, `phenoUtils`, `phenoDesign`, `Conft`, `PhenoProject`, `PhenoDevOps`. Suggest auto-sync from first README paragraph during release-cut.
- Stub-rewrite wave already healed: `AgentMCP`, `dinoforge-packs`, `phenotype-hub`, `vibeproxy-monitoring-unified` (each carries a "previous README was fictional/stale, now corrected" notice).

## Top-5 To Fix (Prioritized)

1. **`nanovms` default branch** — flip from `docs` to `main` (or rename `main`→`prod` if `docs` is intentional GitHub Pages root). README/badges/CI assume `main`. Highest confidence inconsistency.
2. **`phenoData` description** — replace stub "Pheno phenoData workspace" with: "Rust workspace for SurrealDB, PostgreSQL/pgvector, and unified query planner crates (Phenotype data layer)."
3. **`phenoUtils` description** — replace stub with: "Rust workspace for CLI shells, async filesystem, cryptography, networking, and testing helpers (Phenotype foundational utilities)."
4. **Org-wide lint** — add a CI/release-cut check: GitHub `description` must not equal `Pheno <name> workspace` (auto-derive from `<H1> README` first paragraph).
5. **Re-run search-API audit** post rate-limit reset — exhaustive Rust `[package].name` collision and Go `module` path checks across all 85 repos (deferred this run; ~2 min once unblocked).

## Sources verified

- `gh api users/KooshaPari/repos --paginate` (full list)
- `gh api repos/<r>` per repo (default_branch, description)
- `gh api repos/<r>/readme` (decoded base64, first 30 lines)
- `gh api search/code` (partial; rate-limited at ~repo 5/10)
