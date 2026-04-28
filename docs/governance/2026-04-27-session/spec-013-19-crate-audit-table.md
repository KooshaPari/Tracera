# Spec 013 — 19-Crate Audit Table (codex-extracted, 2026-04-27)

Source: `AgilePlus/kitty-specs/013-phenotype-infrakit-stabilization/spec.md`

## Full table

| name | language | task | priority |
|---|---|---|---|
| phenotype-go-kit | Go | Consolidate into infrakit | High |
| phenotype-config | Rust | Stabilize API, publish | High |
| phenotype-shared | Rust | Merge with phenotype-contracts | High |
| phenotype-gauge | Rust | Stabilize metrics API | Medium |
| phenotype-nexus | Rust | Stabilize service discovery | Medium |
| phenotype-forge | Rust | Stabilize build utilities | Medium |
| phenotype-cipher | Rust | Stabilize crypto primitives | High |
| phenotype-xdd-lib | Rust | Stabilize data structures | Medium |
| Authvault | Rust | Stabilize auth primitives | High |
| Tokn | Rust | Stabilize token management | High |
| Zerokit | Rust | Stabilize zero-trust utilities | Medium |
| PolicyStack | Rust | Merge with phenotype-policy-engine | High |
| Quillr | Rust | Stabilize document generation | Low |
| Httpora | Rust | Stabilize HTTP utilities | High |
| Apisync | Rust | Stabilize API sync utilities | Medium |
| phenotype-cli-core | Rust | Stabilize CLI framework | High |
| phenotype-middleware-py | Python | Stabilize, publish to PyPI | Medium |
| phenotype-logging-zig | Zig | Stabilize, evaluate language fit | Low |
| phenotype-auth-ts | TypeScript | Stabilize, publish to npm | Medium |

## Priority buckets
- **HIGH (9):** phenotype-go-kit, phenotype-config, phenotype-shared, phenotype-cipher, Authvault, Tokn, PolicyStack, Httpora, phenotype-cli-core
- **MEDIUM (8):** phenotype-gauge, phenotype-nexus, phenotype-forge, phenotype-xdd-lib, Zerokit, Apisync, phenotype-middleware-py, phenotype-auth-ts
- **LOW (2):** Quillr, phenotype-logging-zig

## Merge mappings (per WP-003)
- phenotype-shared → phenotype-contracts (with deprecation re-exports until WP-009)
- PolicyStack → phenotype-policy-engine
- Collapse: phenotype-error-{core,errors,macros}
- Collapse: phenotype-{ports-canonical,port-traits,async-traits}

## WP-007 publish targets
- crates.io (workspace topo order, no inter-crate cycle)
- PyPI (phenotype-middleware-py)
- npm (phenotype-auth-ts)
- TBD on phenotype-logging-zig (publish-vs-deprecate decision pending)

## WP-000 status (2026-04-27 verification)
- T000-2 PRs #544-#563: 13 MERGED + 3 CLOSED + 3 not-found = effectively done
- T000-4 phenotype-crypto-complete-v2 branch: doesn't exist anywhere = done
- T000-3 cache-adapter-impl: actual branch is `feat/cache-adapter-impl-v2`, NOT in AgilePlus/phenoShared/phenotype-tooling/DataKit (4-hit org-wide grep was for different repos — needs re-targeting)
- T000-6 disk: 12Gi free (above ≥10Gi gate); 2 inactive target/ dirs pruned this turn

## WP-001 reality check (2026-04-27)

Of the 19 crates spec 013 plans to consolidate:

**EXIST as standalone GH repos (8):**
Authvault, Tokn, Zerokit, Quillr, Httpora, Apisync, PolicyStack, phenotype-auth-ts

**EXIST under renamed/embedded paths (6):**
- `phenotype-config` → `Configra` (renamed standalone repo) + embedded `PhenoProc-wtrees/.../crates/phenotype-config-{loader,core}/`
- `phenotype-cipher` → `Configra/pheno-crypto/Cargo.toml` (sub-crate)
- `phenotype-forge` → `phenoForge` + `forge` standalone repos + `PhenoDevOps/rust/forge/Cargo.toml`
- `phenotype-xdd-lib` → `phenoXdd` + `phenoXddLib` standalone repos
- `phenotype-cli-core` → may be embedded in HexaKit/PhenoProc workspaces (TBC)
- `phenotype-config-core` → embedded in PhenoProc-wtrees

**TRULY MISSING (2):** phenotype-go-kit, phenotype-logging-zig (no GH home found via grep+description search)

**Resolved this turn:**
- `phenotype-gauge` → **`Metron`** ✓ verified: "Metrics collection and reporting with Prometheus support" + topics (metrics/observability/phenotype-org/prometheus/rust)
- `phenotype-nexus` → **`Servion`** ✓ verified: "Service registry and discovery for microservices"
- `phenotype-middleware-py` → likely **`portage`** (Harbor framework for agent evals) or one of: PolicyStack/thegent/PhenoKits/PhenoProc (all Python-primary)
- **PhenoProc workspace already contains 28 phenotype-* sub-crates** including phenotype-config-core, phenotype-contracts, phenotype-policy-engine, phenotype-state-machine, phenotype-cache-adapter, phenotype-async-traits, phenotype-error-macros, phenotype-health, phenotype-telemetry — i.e. **PhenoProc is essentially the de-facto consolidation target** that spec 013 plans for phenoShared

## CRITICAL: Spec 013 needs scope rewrite
The spec assumes phenoShared as consolidation target, but PhenoProc has already done parallel consolidation.

**Reality (2026-04-27):**

| | PhenoProc | phenoShared |
|---|---|---|
| lib.rs LOC | 4,539 | 1,557 |
| Sub-crates | 28 | ~9 |
| Strength | Breadth (state-machine, cli-core, config-loader, project-registry, retry, telemetry, validation, time, string, mock) | Depth (config-core 428 LOC, nanovms-client 386 LOC) |
| phenotype-config-core | NO (has config-loader 204 LOC) | YES (428 LOC) |
| phenotype-state-machine | YES (296 LOC) | NO |

→ **Real next-session decision:** the two workspaces contain DIFFERENT phenotype-* crates with overlap-by-name (e.g. both have phenotype-contracts and phenotype-policy-engine but different sizes). Spec 013 work is **3-way merge** into one canonical workspace:
1. Keep larger LOC implementation per crate
2. Reconcile API surfaces (likely some renames)
3. Update consumers (8 standalone repos depend on whichever they currently link)

This is multi-week work, not a single PR.

## 2026-04-27 final reconciliation

**Canonical consolidation home:** `phenoShared` (verified — explicit "shared Rust/library infrastructure" topics, monorepo+library+rust). PhenoProc is app-flavored.

**8 standalone repos audit (live `gh api`):**
- **ARCHIVED (deprecate path):** Authvault, Zerokit, Quillr — `archived: true`. Spec 013 should mark these as "deprecate, list successor."
- **ACTIVE (real migration work):** Tokn (1MB), Httpora (70KB), Apisync (71KB), **PolicyStack (11.7MB — biggest)**, phenotype-auth-ts (224KB).

**Maturity of named-canonical homes:**
- **Metron** (= phenotype-gauge): real Rust crate, 13KB code, topics: metrics+observability+prometheus+rust. Viable migration target.
- **Servion** (= phenotype-nexus): STUB repo, diskUsage 2KB, no languages, no topics. Needs content scaffolded.

**Final spec 013 actual scope:**
1. 5 active-repo migrations: Tokn, Httpora, Apisync, PolicyStack, phenotype-auth-ts → phenoShared
2. 2-way merge: phenoShared + PhenoProc → unified workspace (different crates, ~6K LOC combined)
3. 3 archived crates: just mark "deprecated, see X" in spec
4. 2 stub-or-unbuilt: Servion content scaffolding (phenotype-nexus), phenotype-go-kit + phenotype-logging-zig (no homes found)
5. Naming reconciliation: forge → builder, cipher → crypto (decided), config → Configra/pheno-core, xdd-lib → phenoXdd

Substantially smaller than the 56-checkbox count suggested. ~2-3 weeks focused work, not multi-month.

**EXISTS** (1): phenotype-shared = phenoShared (verified)

→ **Scope correction:** spec 013 is **mostly rename-reconciliation + finding canonical homes**, not greenfield building. Real WP-003 work split:
- 8 crates: migrate from standalone GH repo
- 6 crates: rename + canonicalize from existing renamed/embedded location
- ~4-5 crates: scaffold-or-deprecate decision (gauge/nexus/go-kit/middleware-py/logging-zig)

## WP-002a/b decisions (2026-04-27)
- **MSRV:** `rust-version = "1.75"` (8 manifests pinned, well below local 1.95)
- **Workspace metadata template** (proposed):
  ```toml
  [workspace.package]
  version = "0.1.0"
  edition = "2021"
  rust-version = "1.75"
  license = "MIT"
  repository = "https://github.com/KooshaPari/phenoShared"
  authors = ["Phenotype Team"]
  keywords = ["phenotype", "shared"]
  categories = ["development-tools"]
  ```
- **Fallback names (T002b-2):**
  - `phenotype-forge` → **`phenotype-builder`** (crates.io 404)
  - `phenotype-cipher` → **`phenotype-crypto`** (crates.io 404)
- **crates.io-available**: phenotype-config, phenotype-gauge, phenotype-nexus, phenotype-cli-core, phenotype-contracts, phenotype-policy-engine
