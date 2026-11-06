# Hosted gate triage after Q1 and benchmark bridge

Observed 2026-10-17 against bridge commit `097015d0d9d10d7c8721b67a57a40856942d8e5b`.
These are actual hosted failures, not an accepted release. No Actions rerun or paid service upgrade was requested.

| Failed check                      | Actual cause                                                                    | Classification and action                                                                               |
| --------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Lint & Format                     | Prettier rejected four new JSON/Markdown files                                  | Candidate defect; fixed with pinned Prettier 3.6.2 and all changed JSON/Markdown checked                |
| osv (two runs)                    | Go sidecar requires Go >=1.25.13; scanner runs Go 1.24.2 with GOTOOLCHAIN=local | Existing scanner/toolchain mismatch; both actual job logs inspected                                     |
| Rust dependency policy (two runs) | Rustls 0.23.45 affected by RUSTSEC-2026-0346, -0347, -0348, -0349               | Existing locked dependency present at base and candidate; narrowly patched to 0.23.46                   |
| ci-agents / lint-rust             | Same cargo-deny rustls advisories                                               | Same dependency issue; no deny-policy weakening                                                         |
| ci-agents / required              | Upstream required-job failure                                                   | Aggregate consequence, not a separate source defect                                                     |
| deploy                            | Vercel `api-deployments-free-per-day`, more than 100/day                        | Free quota exhausted; no paid upgrade or deploy retry                                                   |
| Vercel                            | External build-rate-limit status                                                | Service quota; no production acceptance                                                                 |
| SonarCloud Code Analysis          | New duplication 3.2%, required <=3%                                             | Unresolved gate: intentional identical backend migration DDL; each migration reports 88.89% duplication |

The patched Rustls lock entry changes only version and checksum, 0.23.45 -> 0.23.46.
Actual local cargo-deny advisory check passes after the patch. Existing yanked-package
warnings for chacha20 0.10.1 and spin 0.9.8 remain visible; they were not suppressed.
The patched server suite passes 96 library, 123 binary, four existing database and
seven SQLite tests; the explicitly isolated PostgreSQL test is ignored in that invocation
and retains its earlier separately executed Q1 evidence.

The Sonar gate was traced through the service's actual component-measures API to:

- `migrations-postgres/0012_product_observations.sql`
- `migrations-sqlite/0012_product_observations.sql`

Paths are relative to `crates/tracera-server`. The duplicate schema definitions are
intentional backend migration artifacts. No exclusion was added, no applied migration
checksum was changed, and no cosmetic SQL rewrite was used to evade the metric.
The failed gate remains unaccepted pending a proper policy/design disposition.

Main independently advanced from `ae68aea7febd772282606bf1e142d507316cfea0` to
`9be711bb9fe83417046590a1d2d21019273bce37`. The actual GitHub comparison contains
only `docs/operations/w9-unresolved.md` and `docs/operations/w9-verification.md`.
Neither overlaps candidate paths. This is source-overlap evidence, not merged integration
or default-branch acceptance. No merge, rebase, reset or force push was performed.

Runtime receipts remain frozen evidence for their original Q1/bridge binary subjects.
The security-lock follow-on has separately executed local compilation/test and advisory
checks; it does not retroactively change the old runtime binary identity.
