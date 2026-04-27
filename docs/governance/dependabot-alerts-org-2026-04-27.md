# Dependabot Alerts — Org Inventory 2026-04-27

**Scope:** All non-archived, non-fork KooshaPari repos (91 surveyed via `gh repo list --no-archived --source`).
**Method:** API-only, read-only. Per repo: `gh api repos/KooshaPari/<r>/dependabot/alerts?state=open --paginate`. Repos with alerts API disabled or 403/404 silently skipped.

## Aggregate

- **Total open alerts:** 316
- **Repos with alerts:** 19 / 91 (~21%)
- **Severity split (org-wide):**
  - CRITICAL: 4 (1.3%)
  - HIGH: 102 (32.3%)
  - MEDIUM: 160 (50.6%)
  - LOW: 50 (15.8%)

## Top-10 Repos by Open Alert Count

| # | Repo | Total | Critical | High | Medium | Low |
|---|------|-------|----------|------|--------|-----|
| 1 | thegent | 57 | 0 | 24 | 27 | 6 |
| 2 | heliosCLI | 51 | 1 | 22 | 18 | 10 |
| 3 | HexaKit | 48 | 0 | 16 | 28 | 4 |
| 4 | PhenoLang | 36 | 2 | 8 | 19 | 7 |
| 5 | PhenoProject | 31 | 0 | 15 | 15 | 1 |
| 6 | pheno | 28 | 1 | 6 | 13 | 8 |
| 7 | BytePort | 16 | 0 | 0 | 11 | 5 |
| 8 | Tracera | 15 | 0 | 5 | 9 | 1 |
| 9 | hwLedger | 7 | 0 | 3 | 2 | 2 |
| 10 | PhenoRuntime | 6 | 0 | 1 | 1 | 4 |

**Top-10 sum:** 295 (93.4% of org total) — concentration is high.

## Tail (11–19)

| Repo | Total |
|------|-------|
| Dino | 5 |
| phenotype-auth-ts | 3 |
| DevHex | 3 |
| PolicyStack | 2 |
| PlatformKit | 2 |
| phenoDesign | 2 |
| AgilePlus | 2 |
| PhenoObservability | 1 |
| argis-extensions | 1 |

## Critical Alerts (4 total)

- **PhenoLang:** 2
- **heliosCLI:** 1
- **pheno:** 1

These are the highest-priority targets — drill down per repo with:
`gh api repos/KooshaPari/<r>/dependabot/alerts?state=open --jq '.[] | select(.security_advisory.severity=="critical") | {pkg: .dependency.package.name, ghsa: .security_advisory.ghsa_id, manifest: .dependency.manifest_path}'`

## Lockfile- vs Manifest-Actionable (Recommendation Framework)

Without per-alert ecosystem inspection, classification heuristic by repo language:

- **Lockfile-actionable (Cargo.lock / package-lock / pnpm-lock regen typically clears):**
  - thegent (Rust+TS), heliosCLI (Rust), HexaKit (Rust), pheno (Rust), PhenoRuntime (Rust), hwLedger (Rust), AgilePlus (Rust)
  - Estimated reach: ~200/316 alerts (~63%)
- **Manifest-actionable (require Cargo.toml/package.json bump, possibly breaking):**
  - PhenoLang, PhenoProject, BytePort, Tracera, Dino — typically transitive pinned deps
  - Estimated reach: ~80/316 alerts (~25%)
- **Already-tracked / suppressed (cargo-deny W-78/W-93 audits):**
  - heliosCLI, HexaKit, PhenoLang — overlap with cargo-deny snapshot from 2026-04-26
  - Estimated reach: ~36/316 (~12%)

## Recommended Next Actions (no code in this doc)

1. **Lockfile regen wave** (top Rust repos): regenerate Cargo.lock in thegent, heliosCLI, HexaKit, pheno, PhenoRuntime, hwLedger, AgilePlus. Single PR per repo.
2. **Critical-only sweep** (4 alerts): inspect PhenoLang ×2, heliosCLI ×1, pheno ×1 — manifest fix or justified suppression.
3. **Cross-check with cargo-deny W-93 snapshot:** confirm overlap before re-bumping deps already audited.
4. **Defer LOW-severity** (50 alerts) until HIGH/CRITICAL cleared.

## Provenance

- Survey command: `gh repo list KooshaPari --limit 300 --no-archived --source --json name,isFork`
- Fetch command: `gh api repos/KooshaPari/<r>/dependabot/alerts?state=open --paginate --jq 'length'`
- Severity command: `gh api ... --jq '.[] | .security_advisory.severity'`
- Date: 2026-04-27 (UTC); inventory snapshot, not live.
