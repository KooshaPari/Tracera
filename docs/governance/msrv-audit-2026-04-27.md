# MSRV Audit — KooshaPari Rust Repos (2026-04-27)

**Method:** API-only — `gh api repos/<r>/contents/Cargo.toml` + base64 decode + grep `rust-version`. Active (non-archived) Rust repos only.

## Distribution (30 repos)

| MSRV | Count | Repos | Released | Age (mo) |
|------|-------|-------|----------|----------|
| 1.85 | 2 | AgilePlus, PhenoRuntime | 2025-02 | 14 |
| 1.82 | 2 | FocalPoint, hwLedger | 2024-10 | 18 |
| 1.81 | 1 | phenoShared | 2024-09 | 19 |
| 1.75 | 10 | GDK, HexaKit, pheno, phenoAI, PhenoLang, phenotype-tooling, PhenoVCS, Stashly, Tasken, Tokn | 2023-12 | 28 |
| 1.70 | 1 | PhenoObservability | 2023-06 | 34 |
| UNSET | 10 | Agentora, Apisync, Benchora, helios-cli, heliosCLI, Metron, phenoData, PhenoMCP, phenoUtils, PlayCua | n/a | n/a |
| NO_CARGO_TOML | 4 | AuthKit, ObservabilityKit, PhenoAgent, phenotype-infra | n/a | n/a |

## Stale MSRVs (>18 months old)

12 repos pin MSRVs older than 2024-10:

- **PhenoObservability (1.70, 34mo)** — most stale; predates async fn in traits, let-else stabilization gap.
- **1.75 cohort (10 repos, 28mo)** — GDK, HexaKit, pheno, phenoAI, PhenoLang, phenotype-tooling, PhenoVCS, Stashly, Tasken, Tokn.
- **phenoShared (1.81, 19mo)** — borderline.

10 repos UNSET (no `rust-version` field) — implicitly track toolchain, no floor enforced.

## Recommendation

**Org-wide MSRV bump to 1.82** (Oct 2024, 18mo — current upper-bound of "stable enough for libs"):

1. Bump 12 stale repos to `rust-version = "1.82"` in workspace root Cargo.toml.
2. Set `1.82` as floor on the 10 UNSET repos; pin explicitly to fail-loud on toolchain drift (per optionality/loud-failure policy).
3. Leave AgilePlus / PhenoRuntime at 1.85 (binaries can lead).
4. Add 4 NO_CARGO_TOML repos to language-stack audit — verify they are truly non-Rust or polyglot with nested crates.
5. Re-audit at 2026-Q3; target rolling floor of `latest_stable - 4 minors`.

**Risk:** 1.82 unlocks `&raw const`, precise capturing in RPIT, async closure stabilization (1.85) deferred — safe for libs.
