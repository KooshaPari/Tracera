# cargo-deny Scheduled Scan — Maintain Zero-Advisory Floor

**Date:** 2026-04-27  
**Context:** Achieved zero cargo-deny advisories (0/0) in core Rust projects after comprehensive sweep. This document formalizes automated monitoring to catch regressions.

---

## Executive Summary

Three Rust projects have CI cargo-deny coverage; ten major Rust repos lack it. Recommendation: deploy a standard reusable workflow across all 13 target repos, running weekly + on Cargo.toml changes, to maintain zero-advisory floor programmatically.

---

## Per-Repo CI Status

| Repo | cargo-deny CI | Audit CI | Status |
|------|---------------|----------|--------|
| **FocalPoint** | NO | No | Highest-traffic target |
| **hwLedger** | NO | No | Swift + Rust; Rust portion missing scan |
| **BytePort** | NO | No | High-priority Rust lib |
| **KDesktopVirt** | NO | No | Active dev; Rust foundations |
| **HeliosLab** | NO | security-guard-hook-audit.yml | Partial coverage |
| **Configra** | NO | No | Rust workspace |
| **AgilePlus** | NO | audit.yml + security-guard-hook-audit.yml | Partial coverage |
| **PhenoObservability** | NO | No | Rust workspace |
| **eyetracker** | NO | No | Newer project |
| **heliosCLI** | YES | security-guard-hook-audit.yml | GOLD STANDARD |
| **PhenoProc** | NO | No | Rust workspace |
| **PhenoMCP** | NO | No | MCP server; dependency risk high |

**Summary:** 1/12 have cargo-deny; 2/12 have partial audit coverage; 9/12 unmonitored.

---

## Recommended Deployment

### Standard Reusable Workflow

Create `.github/workflows/cargo-deny.yml` in each repo with pattern modeled on **heliosCLI** (proven gold standard). Triggers:
- **On schedule:** Weekly (e.g., Monday 09:00 UTC)
- **On code change:** Any Cargo.toml, Cargo.lock, or src/ push to main
- **On PR:** Lint only (fail if new advisories detected)

### Workflow YAML Template

```yaml
name: cargo-deny

on:
  schedule:
    # Weekly scan: Monday 09:00 UTC
    - cron: '0 9 * * 1'
  push:
    branches:
      - main
    paths:
      - 'Cargo.toml'
      - 'Cargo.lock'
      - 'src/**'
      - 'crates/*/Cargo.toml'
  pull_request:
    paths:
      - 'Cargo.toml'
      - 'Cargo.lock'

jobs:
  cargo-deny:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        checks:
          - advisories
          - bans
          - licenses
          - sources
    steps:
      - uses: actions/checkout@v6

      - uses: EmbarkStudios/cargo-deny-action@v2
        with:
          rust-version: stable
          log-level: warn
          command: check ${{ matrix.checks }}
          arguments: --all-features

      - name: Report summary
        if: failure()
        run: |
          echo "❌ cargo-deny detected issues. Review output above."
          exit 1
```

### Workspace Root Workflow (Optional)

For monorepos with multiple crates, add a **workspace-level** trigger in the root `.github/workflows/cargo-deny.yml`:

```yaml
name: cargo-deny-workspace

on:
  schedule:
    - cron: '0 9 * * 1'
  push:
    branches:
      - main
    paths:
      - '*/Cargo.toml'
      - 'Cargo.lock'

jobs:
  deny-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: EmbarkStudios/cargo-deny-action@v2
        with:
          rust-version: stable
```

---

## Implementation Order (Phased)

### Phase 1: High-Traffic Targets (Week 1)
Deploy to top 3 repos by activity/downloads:
1. **FocalPoint** — highest-traffic, released v0.0.12+ this session
2. **PhenoObservability** — core observability layer
3. **PhenoMCP** — MCP server; dependency risk

**Effort:** 3 × 2 min = 6 min wall-clock

### Phase 2: Core Platforms (Week 2)
4. **hwLedger** — Swift + Rust hybrid; Rust deps high risk
5. **AgilePlus** — event-sourcing-heavy; transitive deps
6. **heliosCLI** — verify template + sync with latest

**Effort:** 3 × 2 min = 6 min wall-clock

### Phase 3: Supporting Layers (Week 3)
7–13: BytePort, KDesktopVirt, Configra, HeliosLab, PhenoProc, eyetracker, PhenoMCP

---

## Maintenance & Escalation

### Weekly Scan Cadence
- **Monday 09:00 UTC:** All repos scan
- **Failure:** Workflow fails PR; blocks merge until resolved
- **Escalation:** If 2+ repos flag new advisory, trigger emergency dependency audit

### Suppress Only with Justification
Per governance: zero bare suppressions. Format in `deny.toml`:
```toml
[advisories]
ignore = [
    { id = "RUSTSEC-YYYY-XXXX", reason = "no upgrade path; vendored; expires 2026-12-31" }
]
```

### Rollout Checkpoint (1 Week Post-Deploy)
- All 13 repos green for 7 consecutive days = floor maintained
- Escalate any red to dependency triage team within 48 hours

---

## References

- **heliosCLI Workflow** (proven): `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI/.github/workflows/cargo-deny.yml`
- **Cargo-deny Docs**: https://embarkstudios.github.io/cargo-deny/
- **RUSTSEC Advisory DB**: https://rustsec.org/
- **Governance**: `/repos/docs/governance/` (suppression policy, CI completeness)
