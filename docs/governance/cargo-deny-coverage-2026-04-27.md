# cargo-deny / cargo-audit Coverage — 2026-04-27

API-only inventory across 30 active Rust repos in KooshaPari org.

## Summary Counts

| Metric | Count | % |
|---|---|---|
| Active Rust repos | 30 | 100% |
| `deny.toml` present (root) | 30 | 100% |
| `deny.toml` missing | 0 | 0% |
| CI runs `cargo-deny` | 8 | 26.7% |
| CI runs `cargo-audit` | 9 | 30.0% |
| CI runs **neither** | 19 | 63.3% |
| CI runs **both** | 7 | 23.3% |

## CI Coverage Detail

**deny + audit (7):** AgilePlus, helios-cli, heliosCLI, HexaKit, pheno, PhenoLang, Tokn
**deny only (1):** FocalPoint
**audit only (2):** Stashly, Tasken
**neither (19):** Agentora, Apisync, AuthKit, Benchora, GDK, hwLedger, Metron, ObservabilityKit, PhenoAgent, phenoAI, phenoData, PhenoMCP, PhenoObservability, PhenoRuntime, phenoShared, phenotype-infra, phenotype-tooling, phenoUtils, PhenoVCS, PlayCua

## Top-5 Repos Missing `deny.toml`

None — `deny.toml` coverage is 100%.

## Top-5 High-Priority "Neither" (CI Gap)

Ranked by criticality / surface area:
1. **hwLedger** — 273+ tests, financial domain, no audit/deny CI
2. **PhenoRuntime** — runtime crate, broad downstream blast radius
3. **PhenoObservability** — security-sensitive (telemetry, logs)
4. **AuthKit** — auth/identity, must have supply-chain gates
5. **PhenoMCP** — external protocol surface (MCP server)

## Recommendations

1. **Wire cargo-deny + cargo-audit into CI for the 19 "neither" repos** via shared reusable workflow (`phenotype-infra/.github/workflows/rust-supply-chain.yml`).
2. **Promote `deny only` / `audit only` repos to both** — FocalPoint needs audit; Stashly + Tasken need deny.
3. **Pin reusable workflow version** to avoid drift; centralize `deny.toml` policy via inheritance/include.
4. **Backfill priority order:** hwLedger → AuthKit → PhenoRuntime → PhenoObservability → PhenoMCP → remaining 14.
5. **Track in AgilePlus** as governance work package under existing supply-chain/SBOM spec.

Source: GitHub Contents API + Workflows API, 2026-04-27.
