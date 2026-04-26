# phenoShared cargo-deny advisories — 2026-04-27 (W-96 cohort expansion)

**Status**: NOT clean — 2 advisories, both fixable by single dep bump.
**Cohort**: W-96 measurable cohort grows 10/11 → 11/12 once resolved.
**Scope**: phenotype-shared (alias phenoShared), 12 workspace members.

## Advisory inventory

| ID | Severity | Crate | Path | Category |
|----|----------|-------|------|----------|
| RUSTSEC-2024-0421 | vulnerability | `idna 0.5.0` | `validator 0.18.1` → `phenotype-application` | CLUSTER-FIX |
| RUSTSEC-2024-0370 | unmaintained | `proc-macro-error 1.0.4` | `validator_derive 0.18.2` → `validator 0.18.1` → `phenotype-application` | CLUSTER-FIX |

Both advisories share a **single root cause**: `validator = "0.18"` pinned in:

- `Cargo.toml:47` (workspace)
- `crates/phenotype-application/Cargo.toml:38`

`validator 0.20.0` (latest, per `cargo search`) drops `proc-macro-error` (uses proc-macro-error2/manyhow) and uses `url 2.5.4+` / `idna 1.x`, resolving both.

## Stale ignores in deny.toml (cleanup candidates)

Three `[advisories.ignore]` entries no longer match any crate in the dep tree:

- RUSTSEC-2025-0134 (rustls-pemfile)
- RUSTSEC-2025-0140 (gix)
- RUSTSEC-2026-0049 (async-nats / rustls-webpki)

Likely cleared by a prior `async-nats` / `gix` upgrade. Recommend dropping these from `deny.toml` in the same PR as the validator bump.

## Recommendation: CLUSTER-FIX

Single PR:

1. Bump `validator` 0.18 → 0.20 (workspace + phenotype-application).
2. Adjust `validator` API call sites if any (0.18 → 0.20 had attribute changes; sweep `#[validate(...)]` usages in `phenotype-application`).
3. Run `cargo update -p idna` to confirm idna 1.x resolution.
4. Drop 3 stale `deny.toml` ignores.
5. `cargo deny check advisories` must pass.

**Effort**: small feature, ~3-6 tool calls. Forward-only; no breaking changes outside `phenotype-application` validator usage.

## Cohort accounting

- Pre-check: phenoShared not yet in W-96 measurable cohort (10/11 clean).
- Post-fix: cohort grows to 11/12 clean.
- Tracking dashboard: `ORG_DASHBOARD_v53` cargo-deny row.
