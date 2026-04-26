# Dependabot Alert Snapshot — Tier-1 Repos (2026-04-26)

Generated snapshot of all open Dependabot security vulnerability alerts across tier-1 active repositories. Used to identify next-highest-impact targets for vulnerability resolution sweeps (following Tracera 2026-04-25, 28 alerts).

## Summary

| Rank | Repository | Critical | High | Moderate | Low | **Total** |
|------|-----------|----------|------|----------|-----|----------|
| 1 | **heliosCLI** | 1 | 22 | 18 | 12 | **53** |
| 2 | **thegent** | 0 | 25 | 29 | 6 | **60** |
| 3 | **agentapi-plusplus** | 0 | 6 | 13 | 2 | **21** |
| 4 | **BytePort** | 0 | 0 | 11 | 5 | **16** |
| 5 | AgilePlus | 0 | 0 | 6 | 2 | 8 |
| 6 | hwLedger | 0 | 3 | 2 | 2 | 7 |
| 7 | helios-router | 0 | 0 | 3 | 1 | 4 |
| 8 | AuthKit | 0 | 1 | 1 | 0 | 2 |
| 9 | phenoShared | 0 | 0 | 1 | 0 | 1 |
| — | TestingKit, ResilienceKit, PhenoKits, ObservabilityKit, McpKit, HeliosLab, heliosBench, heliosApp | 0 | 0 | 0 | 0 | **0** |

**Total workspace open alerts:** 231 (CRITICAL: 1, HIGH: 57, MODERATE: 85, LOW: 29)

## Top 3 Priority Targets (Next Sweep)

### 1. thegent (60 total, 0 CRITICAL, 25 HIGH)
**Impact:** Highest overall count; 25 high-severity vulnerabilities indicate transitive dependency issues in a widely-used dotfiles framework.
**Action:** Dependency audit, lock-file review, and coordinated updates across ecosystem (phenotype-infrakit, heliosApp, et al.).

### 2. heliosCLI (53 total, 1 CRITICAL, 22 HIGH)
**Impact:** Highest critical count (1); highest high-severity count (22). HeliosCLI has direct production exposure.
**Action:** Immediate critical CVE remediation, then systematic high-severity resolution across CLI/framework dependencies.

### 3. agentapi-plusplus (21 total, 0 CRITICAL, 6 HIGH)
**Impact:** Agent API platform; 21 alerts with 6 high-severity dependencies. API surface exposure is significant.
**Action:** API-layer dependency hardening; transitive audits on async/tokio/opentelemetry stacks.

## Secondary Targets
- **BytePort** (16 total) — platform/codec library; moderate exposure
- **AgilePlus** (8 total) — tooling; low risk
- **hwLedger** (7 total) — hardware integration; low risk

## Ecosystem Impact Notes

- **Tracera 2026-04-25:** 28 alerts closed across workspace; this snapshot captures remaining and newly-detected alerts
- **thegent + heliosCLI overlap:** Both likely share Rust/Python transitive dependencies (GitPython, certifi, urllib3); coordinated updates may resolve cross-repo issues
- **heliosApp clean:** No open alerts (0/0/0/0) — heliosCLI's high count does not propagate downstream
- **phenotype-infrakit coupling:** thegent+heliosCLI updates may unlock phenotype-infrakit and broader HeliosFamily remediation

## Query Method

GraphQL `vulnerabilityAlerts(states: OPEN)` query across all repos, aggregated by severity level.

```graphql
query {
  repository(owner: "KooshaPari", name: "<repo>") {
    vulnerabilityAlerts(first: 100, states: OPEN) {
      edges {
        node {
          securityVulnerability {
            severity
          }
        }
      }
      totalCount
    }
  }
}
```

---

**Next Action:** Dispatch dedicated sweep agents to thegent and heliosCLI to triage and resolve top-severity alerts.
