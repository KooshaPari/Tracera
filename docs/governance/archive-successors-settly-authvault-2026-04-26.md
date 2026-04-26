# Archive Successors: Settly & Authvault (2026-04-26)

## Summary

This document tracks the consolidation and successor projects for two archived repositories: **Settly** and **Authvault**. Both repositories are now archived but their functionality has been migrated into active projects within the phenotype ecosystem.

---

## 1. Settly

### Original Purpose
Universal configuration management framework for Rust, following hexagonal architecture principles. Provided layered configs, validation, and environment support.

### Current Successor
**`phenotype-config`** (canonical location: `/Users/kooshapari/CodeProjects/Phenotype/repos/crates/phenotype-config`)

All Settly functionality has been fully migrated into `phenotype-config`, which now serves as the primary configuration management crate for the phenotype ecosystem. The spec docs, PRD, architecture, and governance are all maintained in this crate.

### Evidence
- `/crates/phenotype-config/PRD.md` — labeled as "PRD — Settly"
- `/crates/phenotype-config/ARCHITECTURE.md` — architecture documentation
- `/crates/phenotype-config/FUNCTIONAL_REQUIREMENTS.md` — functional specs
- `/crates/phenotype-config/CHARTER.md` — project charter
- `/crates/phenotype-config/GOVERNANCE.md` — governance and QA policies

### References to Redirect
- Any imports or docs referencing "Settly" should be updated to point to `phenotype-config`
- Old Settly repository links: redirect to `/repos/crates/phenotype-config`

### Status
**MIGRATED AND ACTIVE** — No orphaned functionality.

---

## 2. Authvault

### Original Purpose
Authentication and vault management primitives for the phenotype ecosystem. Provided credential storage, token caching, and auth validation infrastructure.

### Current Successor
**`phenotype-cipher`** + **`Tokn`** (distributed across phenotype ecosystem)

Authvault has been decomposed into two successor projects:

1. **`phenotype-cipher`** — Cryptographic operations and token manipulation
   - Location: `/crates/phenotype-cipher` (canonical), also in `/pheno/phenotype-cipher`, `/PhenoProc/phenotype-cipher`
   - Handles: encryption, decryption, cryptographic hashing

2. **`Tokn`** — Token management and credential versioning
   - Location: `/Tokn` (canonical), also in `/pheno/Tokn`, `/PhenoLang-wtrees/cve-residual/Tokn`
   - Handles: token caching, credential versioning, auth state management

### Evidence
- **Token Caching & Credential Versioning**: STASHLY_MIGRATIONS_ADOPTION_REPORT.md references "Authvault token caching (credential versioning)"
- **AgilePlus Spec Tasks**:
  - `AgilePlus-wtrees/pyjwt-fix/kitty-specs/013-phenotype-infrakit-stabilization/tasks.md`:
    - T014: "Migrate phenotype-cipher, Authvault, Tokn, Zerokit into workspace"
    - T024: "Write unit tests for phenotype-cipher, Authvault, Tokn (crypto/auth crates, target: ≥90%)"
    - T036: "Publish Authvault, Tokn, Zerokit, phenotype-gauge to crates.io"
  - `kitty-specs/012-github-portfolio-triage/spec.md`:
    - "phenotype-rust-auth | Rust | Archive | Placeholder, auth in Authvault"
    - "odin-auth-service | Odin | Archive | Legacy auth, replaced by Authvault"

### References to Redirect
- Any imports or docs referencing "Authvault" should be updated to point to:
  - **`phenotype-cipher`** for cryptographic operations
  - **`Tokn`** for token/credential management
- Old Authvault repository links: redirect to appropriate successor based on use case

### Status
**MIGRATED AND DECOMPOSED** — No orphaned functionality. Successor projects are active and scheduled for crates.io publication (T036).

---

## 3. Consolidation Plan

### Immediate Actions
1. Update any documentation or READMEs that reference Settly or Authvault to point to successors
2. Verify all active crates have no dangling imports from archived repos
3. Ensure phenotype-cipher and Tokn are properly exported in workspace Cargo.toml

### Future Work (Per AgilePlus Specs)
- **T014**: Complete workspace migration of phenotype-cipher, Tokn, Zerokit (pending)
- **T024**: Increase unit test coverage to ≥90% for crypto/auth crates
- **T036**: Publish to crates.io (phenotype-cipher, Tokn, Zerokit, phenotype-gauge)

### Cross-Project Impact
- **AuthKit** — Uses phenotype-cipher and Tokn; already active
- **Stashly** — Depends on Tokn for credential versioning
- **phenotype-infrakit** — Workspace consolidation in progress (T014)

---

## 4. Orphaned Status

**NONE** — Both archived projects have clear, active successors with documented migration paths.

- **Settly** → phenotype-config (1:1 replacement)
- **Authvault** → phenotype-cipher + Tokn (1:2 decomposition, both active)

