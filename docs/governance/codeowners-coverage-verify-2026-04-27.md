# CODEOWNERS Coverage Audit — Post-Wave-17

**Date:** 2026-04-27
**Scope:** All non-archived, non-fork repos owned by `KooshaPari` (n=71)
**Method:** GitHub Contents API probe of `CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`
**Categorization:**
- **MISSING** = no file at any of the three locations
- **STUB** = file exists but `<50` bytes OR 0 ownership rules (`<pattern> @owner` lines)
- **OK** = file exists with `>=50` bytes AND `>=1` valid ownership rule

## Summary

| Category | Count | Pct |
|---|---|---|
| MISSING | 24 | 33.8% |
| STUB | 12 | 16.9% |
| OK | 35 | 49.3% |
| **Total** | **71** | **100%** |

Coverage gap: **50.7%** of repos are either missing CODEOWNERS or have stub-quality files.

## MISSING (24)

No CODEOWNERS at any path. Priority repos in **bold** (active product/code repos):

- **AgentMCP**
- **Agentora**
- **Benchora**
- **DevHex**
- **PhenoMCP**
- **PhenoHandbook**
- **PlatformKit**
- **PlayCua**
- **ResilienceKit**
- **phenotype-auth-ts**
- **phenotype-hub**
- **phenotype-registry**
- **dinoforge-packs**
- **heliosBench**
- **eyetracker**
- **nanovms**
- **vibeproxy-monitoring-unified**
- agent-devops-setups
- agileplus-landing
- byteport-landing
- hwledger-landing
- phenokits-landing
- projects-landing
- thegent-landing

Landing/marketing sites (8) are lower priority; the 16 in bold are active code repos and should get CODEOWNERS in the next wave.

## STUB (12)

File exists but is a 1-rule, ~30–50 byte stub (likely `* @KooshaPari` only, no path-scoped ownership):

| Repo | Path | Size | Rules |
|---|---|---|---|
| AgilePlus | .github/CODEOWNERS | 47 | 1 |
| heliosCLI | .github/CODEOWNERS | 47 | 1 |
| phenodocs | .github/CODEOWNERS | 42 | 1 |
| phenoXdd | .github/CODEOWNERS | 44 | 1 |
| phenotype-infra | CODEOWNERS | 44 | 1 |
| phenotype-tooling | CODEOWNERS | 44 | 1 |
| Apisync | CODEOWNERS | 34 | 1 |
| argis-extensions | CODEOWNERS | 34 | 1 |
| Httpora | CODEOWNERS | 34 | 1 |
| PolicyStack | CODEOWNERS | 34 | 1 |
| Stashly | CODEOWNERS | 34 | 1 |
| Tasken | CODEOWNERS | 34 | 1 |

**Top stubs to expand** (highest leverage — active multi-crate or multi-area repos):
1. **AgilePlus** — multi-crate workspace; needs path-scoped rules per crate.
2. **heliosCLI** — framework with subprojects; needs scoped owners.
3. **phenotype-infra** — IaC + scripts; needs `/iac`, `/scripts`, `/.github` rules.
4. **phenotype-tooling** — multi-tool repo.
5. **PolicyStack** — policy domains warrant path scoping.
6. **phenoXdd** — XDD framework with multiple modules.

## OK (35)

35 repos have substantive CODEOWNERS (>=50 bytes, >=1 rule). Standouts:
- **FocalPoint** (.github/CODEOWNERS, 2150 bytes, 37 rules) — gold standard.
- **thegent** (CODEOWNERS, 1460 bytes, 27 rules).
- **PhenoCompose**, **Tracera** (581 bytes, 12 rules each).
- **PhenoObservability** (436 bytes, 16 rules).

## Recommended Next Actions

1. **Expand 6 stubs** (AgilePlus, heliosCLI, phenotype-infra, phenotype-tooling, PolicyStack, phenoXdd) with path-scoped rules — model on FocalPoint/thegent.
2. **Add CODEOWNERS** to 16 active MISSING code repos (bolded above).
3. **Defer landing sites** (8 `*-landing` + projects-landing) until product CODEOWNERS waves stabilize.

## Raw Data

Raw probe output: `/tmp/codeowners-audit/results.txt` (regenerable via `probe.sh`).
