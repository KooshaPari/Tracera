# Rust Toolchain Pin Audit — 2026-04-27

**Method**: API-only via `gh api repos/KooshaPari/<r>/contents/rust-toolchain.toml`. Surveyed all 30 active (non-archived) Rust-language repos under `KooshaPari/*`.

## Coverage

- **30** active Rust repos surveyed
- **8** have `rust-toolchain.toml` (26.7%)
- **22** have NO toolchain pin (73.3%)
- **0** use legacy `rust-toolchain` (no `.toml`)

## Channel Distribution

| Channel | Count | Repos |
|---------|-------|-------|
| `nightly` | 7 | AgilePlus, Apisync, HexaKit, pheno, PhenoLang, Stashly, Tasken |
| `1.82` (pinned) | 1 | FocalPoint |
| (unpinned) | 22 | Agentora, AuthKit, Benchora, GDK, helios-cli, heliosCLI, hwLedger, Metron, ObservabilityKit, PhenoAgent, phenoAI, phenoData, PhenoMCP, PhenoObservability, PhenoRuntime, phenoShared, phenotype-infra, phenotype-tooling, phenoUtils, PhenoVCS, PlayCua, Tokn |

## Drift / Misalignment Findings

1. **FocalPoint stuck on Rust 1.82** while the rest of the pinned fleet runs `nightly`. Latest stable is 1.84.x; 1.82 is ~3 releases behind. Either bump to current stable or align with nightly group.
2. **73% of Rust repos have NO pin** — toolchain version drifts with whatever rustup default is on the build host. This is the single largest alignment gap.
3. **Nightly-7 cluster** uses identical `[toolchain] channel="nightly"` + `components=["rustfmt","clippy","rust-docs"]`. Good internal consistency; candidate for a shared template.

## Top Recommendations

1. **Adopt org-wide `rust-toolchain.toml` standard.** Apply the nightly-7 template (or pinned-stable variant) to the 22 unpinned repos for reproducible builds.
2. **Resolve FocalPoint drift.** Either bump `1.82` → current stable (`1.84+`) or move it onto nightly to match the rest of the pinned fleet.
3. **Decide nightly vs stable policy.** 7/8 pinned repos chose nightly — formalize this as policy or migrate to a stable pin (nightly is fragile for downstream consumers like Dependabot lock regen).
4. **Pin critical infra first.** PhenoRuntime, hwLedger, phenoShared, AgilePlus consumers (PhenoMCP, PhenoVCS, Metron) should pin before lower-priority repos.
