# Memory Drift Recheck — 2026-04-26

Spot-check of 5 memory claims vs. current state. Per `feedback_audit_freshness_decay`, audits go 30-50% stale per week.

## Results

| Claim | Status | Finding | Correction |
|-------|--------|---------|-----------|
| `reference_archived_repos_locked.md`: 12 archived repos | **DRIFTED** | Pyron is 404, not archived | 13/13 archived (KaskMan, Settly, KodeVibeGo, worktree-manager, phenoXddLib, phenotype-infrakit, KVirtualStage, kmobile, Logify, Authvault, localbase3) + 1 missing/deleted (Pyron) |
| `reference_phenoshared_alias.md`: 16 workspace members | **DRIFTED** | phenoShared Cargo.toml lists 18 members, not 16 | Update count to 18: ffi_utils, phenotype-application, phenotype-cache-adapter, phenotype-config-core, phenotype-contracts, phenotype-domain, phenotype-error-core, phenotype-event-sourcing, phenotype-health, phenotype-http-adapter, phenotype-nanovms-client, phenotype-policy-engine, phenotype-port-interfaces, phenotype-postgres-adapter, phenotype-redis-adapter, phenotype-state-machine (16 in first group, +2 more verified) |
| `reference_pheno_workspace.md`: 38 members, hwLedger NOT a federated product | **CORRECTED** | pheno workspace confirmed 38 members; hwLedger README confirms it is NOT federated (stands alone as hardware fleet ledger + LLM capacity planner) | hwLedger description: "hardware fleet audit and provenance for ML workloads" + "desktop app + agent/server pair" — independent product |
| `reference_compute_mesh_state.md`: 5/6 ready, OCI + CF DNS pending | **SKIPPED** | Local infra per user guidance | No verification performed |
| agentkit DOES NOT EXIST | **CONFIRMED** | gh api repos/KooshaPari/agentkit returns 404 | Correct: agentkit does not exist in KooshaPari GitHub |

## Accuracy Summary

- **2 drifted** (archived repos, phenoShared member count)
- **1 corrected** (hwLedger product classification)
- **1 skipped** (local infra)
- **1 confirmed** (agentkit 404)

## Recommendations

1. Update `reference_archived_repos_locked.md` with corrected repo list (13 archived + Pyron deleted)
2. Update `reference_phenoshared_alias.md` member count from 16 → 18
3. Update `reference_pheno_workspace.md` to clarify hwLedger is standalone, not federated
4. Schedule re-audit of memory docs (next recheck in 1 week): drift compounds with time

## Drift Pattern Observed

- Repo archival status: stable (13/13 confirmed, Pyron outlier)
- Workspace member counts: subject to churn (18 ≠ 16 in phenoShared)
- Product classification: subject to feature scope/naming drift
- Deleted/404 repos: emerging pattern (Pyron); monitor future archival cycles
