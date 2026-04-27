# ORG_DASHBOARD v58 - Post-Protobuf-Suppress Actual State (2026-04-27)

**Predecessor:** [v57 zero-advisory](./ORG_DASHBOARD_v57_2026_04_27_zero_advisory.md)  
**Scope:** Protobuf suppress landed (commit 6921973); actual advisory count now 3 (from 4).  
**Status:** Org cargo-deny 50 → 3 (-94%) confirmed. PhenoMCP 3× rustls-webpki alpha decision pending.

---

## HEADLINE

**Org cargo-deny: 50 → 3 (-94%) on 2026-04-27 22:XX post-protobuf-suppress.**  
Protobuf-rs uncontrolled-recursion now suppressed in PhenoObservability. PhenoMCP 3 rustls-webpki LOW remain (alpha bump OR suppress decision pending).

---

## Trajectory: W-92 → Post-Protobuf (Final)

| Snapshot | Advisory Count | Delta | Driver |
|---|---:|---:|---|
| W-92 (baseline) | 50 | — | 2026-04-21 initial |
| W-93 | 27 | -23 | FocalPoint / Metron passthrough |
| W-94 | 13 | -14 | KDesktopVirt bollard cluster |
| W-95 | 8 | -5 | eyetracker uniffi cluster |
| W-96 | 8 | ±0 | audit + validation |
| W-97 | 1 | -7 | AgilePlus PR #431 (utoipa-axum dead-dep) |
| W-98 | 4 | -(-3) | 4 LOW transitives surfaced |
| **Post-Protobuf** | **3** | **-1** | PhenoObservability suppress (6921973) |

---

## Residual Advisories (3 LOW — Active Decision Path)

| Repo | Advisory | Crate | Severity | Status |
|---|---|---|---|---|
| PhenoMCP | name-constraint-bypass | rustls-webpki | LOW | **OPEN**: alpha bump (rustls-pbkdf2 v0.7) OR suppress |
| PhenoMCP | wildcard-overflow | rustls-webpki | LOW | **OPEN**: same patch as above |
| PhenoMCP | crl-panic | rustls-webpki | LOW | **OPEN**: same patch as above |
| ~~PhenoObservability~~ | ~~uncontrolled-recursion~~ | ~~protobuf~~ | ~~LOW~~ | **SUPPRESSED** (6921973) |

All three PhenoMCP advisories are pre-existing transitives; waiting on rustls-webpki upstream patch or suppression approval.

---

## Org Audit Status: NEWLY CLEAN (Pheno Full)

Per pheno full audit (commit c56fcd9): **0 advisories in phenotype-shared crate + pheno workspace + all consumers.**

**SBOMs Generated:** 154 total across org.  
**Merge Rate:** 6/6 PRs merged (100%).

---

## Open Decision

**PhenoMCP rustls-webpki: Bump or Suppress?**

- **Option A:** Bump rustls (dep rustls-pbpdf2 v0.6 → v0.7); requires coordinate with proto downstream.
- **Option B:** Suppress (commit allow-list); unblock CI; revisit on next quarterly audit.

Decision pending user guidance or upstream patch ETA.

---

## Memory Consolidated (18 Entries)

All feedback entries codified in session-memory. Key codification: `feedback_dashboard_actuals_only.md` — dashboard numbers from actual snapshots only, not projections.

---

**Status:** Ready to commit (no push until user decision on PhenoMCP option).  
**Next:** [W-99 Governance Phase 2 Kickoff](./ORG_DASHBOARD_v59_governance_phase2.md) (TBD post-decision).
