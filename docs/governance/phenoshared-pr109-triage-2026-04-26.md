# phenoShared PR #109 Triage — feat(errors): add dual-interface contracts

## Status

**Author:** KooshaPari (user) | **Created:** 2026-04-26T04:44:44Z | **Mergeable:** YES | **Review Decision:** PENDING

## Scope Summary

PR #109 introduces a shared error contract layer (`contracts/errors/`) with standardized error codes and envelopes across Rust and TypeScript. Key changes:

- **Contracts** (new): `error-codes.json`, `error-envelope.schema.json`, and JSON fixtures under `contracts/errors/`
- **Rust** (`phenotype-error-core`): refactored into focused modules (`code.rs`, `context.rs`, `envelope.rs`, `layered.rs`); switches wire model from ad-hoc `ERR_<status>` strings to typed `ErrorCode` + structured `ErrorEnvelope` (with `details`, `fatal`, `retryable`)
- **TypeScript** (`packages/errors`): exports `ERROR_CODES`, `PhenotypeErrorEnvelope`; adds parity tests; tightens `packages/types` response `error.code` to shared union
- **Docs** (updated): `FUNCTIONAL_REQUIREMENTS.md`, `PRD.md`; new session docs under `docs/sessions/20260426-errors-dual-interface-contracts/`
- **Total files:** 18 changed (7 added files in contracts + modules + tests)

## Risk Assessment

**Medium Risk:** Wire contract change affects serialization/deserialization of error payloads. All consumers (clients, gateways) must align with the new envelope shape and error-code union. Pre-existing formatting drift in `phenotype-config-core` blocks workspace-wide `cargo fmt --check` (acknowledged in PR body).

## Recommendation

**✅ MERGE** — User-authored, well-scoped, includes parity tests, and specifies validation steps (cargo test, clippy, bun typecheck). Codex co-authored-by tag indicates code-gen assistance was applied. Validation commands in PR body must run before merge to confirm no regressions.

**Pre-merge checklist:**
- Run: `cargo test -p phenotype-error-core` + `cargo clippy -p phenotype-error-core -- -D warnings`
- Run: `cd packages/errors && bun run typecheck && bun test`
- Run: `cd packages/types && bun test`
- Verify mergeable status + review decision (currently empty, may need approval)
- Note: `cargo fmt --check` workspace-wide will fail due to pre-existing drift in `phenotype-config-core`; localized format OK

**Post-merge:**
- Tag downstream consumers (gateways, clients) for contract alignment
- Defer `phenotype-config-core` formatting to separate refactor (not blocking this PR)
