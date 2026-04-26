# Dormant Repo Audit — KooshaPari Org (2026-04-25)

Read-only audit per request to triage dormant/empty repos for archive / re-purpose / delete / investigate decisions. Headline candidate: `phenotype-shared` (canonical-home ADR PhenoKits#31).

**Method:** `gh repo list --no-archived` (99 repos), filter `diskUsage < 200 KB`, sample contents via `gh api repos/.../contents`.

## Headline: `phenotype-shared`

| Field | Value |
|---|---|
| Disk | (not <200KB; full repo) |
| Last push | recent (active) |
| Language | Rust |
| Cargo `members` | **12 entries listed** (not `[]` as user premise stated) |
| `crates/phenotype-event-sourcing/src/` | populated: `memory.rs` 9.9KB, `hash.rs` 5.2KB, `event.rs`, `store.rs`, `snapshot.rs`, `lib.rs` |

**Finding:** Contradicts user premise. The GitHub HEAD of `phenotype-shared` lists 12 workspace members and at least one crate (event-sourcing) ships real code. Either (a) the ADR is stale, (b) the local `repos/phenotype-shared` checkout has drifted from origin, or (c) the dormancy claim refers to crate adoption (downstream consumers), not the repo itself. **Recommendation: Investigate** — reconcile ADR vs. live repo state before acting.

## Dormant Candidates (<200 KB, sampled)

| Repo | Size KB | Lang | Last push | Contents preview | Recommendation |
|---|---|---|---|---|---|
| `phenotype-hub` | 12 | none | 2026-04-25 | docs-only: AGENTS.md, CLAUDE.md, FUNCTIONAL_REQUIREMENTS.md, worklog.md; no `src/` | **Re-purpose** — name reserved for future hub; spec stub exists |
| `phenotype-registry` | 19 | none | 2026-04-25 | SPEC.md, PLAN.md, LIBRARY_RESEARCH_REGISTRY.md (24KB), README.md; no code | **Re-purpose** — research registry doc home, valid as docs-only |
| `vibeproxy-monitoring-unified` | 20 | none | 2026-04-25 | governance scaffolding only (AGENTS, CLAUDE, FRs); no `src/` | **Investigate** — orphaned monitoring stub, unclear owner |
| `phenoData` | 22 | Rust | 2026-04-25 | Cargo workspace, 3 empty crate dirs (pg-bridge, pheno-query, surreal-bridge) | **Re-purpose** — namespace for data crates; empty workspace |
| `phenotype-bus` | 24 | Rust | 2026-04-25 | `src/lib.rs` 4.9KB exists, `Cargo.toml.bak` present | Active stub; **keep, monitor** |
| `dinoforge-packs` | 25 | Go | 2026-04-25 | Has `warfare-starwars/` pack content (buildings, factions, doctrines) | Active content repo; **keep** |
| `DevHex` | 26 | Go | 2026-04-25 | (touched today, unsampled here) | **Investigate** |
| `projects-landing` | 26 | Astro | 2026-04-25 | landing site stub | **Keep** — org pages pattern |
| `phenoUtils` | 27 | Rust | 2026-04-25 | 5 empty crate dirs (pheno-crypto, pheno-fs, pheno-net, pheno-shell, pheno-testing) | **Re-purpose** — namespace reserved for utility crates |
| `Sidekick` | 27 | Rust | 2026-04-25 | 4 crate dirs (cheap-llm, dispatch, messaging, presence); `Cargo.toml.bak` | **Investigate** — likely WIP from cheap-llm session |
| `thegent-workspace` | 30 | Rust | 2026-04-25 | (private, unsampled) | **Investigate** |
| `agileplus-landing` | 33 | Astro | 2026-04-25 | landing site | **Keep** |
| `phenoAI` | 34 | Rust | 2026-04-24 | 3 empty crate dirs (llm-router, mcp-server, pheno-embedding) | **Re-purpose** — AI namespace |
| `Benchora` | 36 | Rust | 2026-04-25 | empty `src/`, `tests/`, `benches/`; SPEC 81B (near-empty) | **Re-purpose** — bench harness name reserved |
| `cheap-llm-mcp` | 40 | Python | 2026-04-25 | (private, recently active session-2026-04-22) | **Keep** — known active per MEMORY |
| `Metron` | 41 | Rust | 2026-04-25 | governance scaffolding only, no `src/` | **Re-purpose** — observability namespace |
| `Httpora` | 42 | none | 2026-04-25 | 10 FR-HTTP-* spec stubs, no code | **Re-purpose** — HTTP crate name reserved |
| `Eidolon` | 47 | Rust | 2026-04-25 | 4 crate dirs (core/desktop/mobile/sandbox); `Cargo.toml.bak` | **Re-purpose** — device automation rebuild name |
| `rich-cli-kit` | 52 | Rust | 2026-04-25 | empty `crates/`, `mcp/`, `shaders/`, `tests/`; CHANGELOG 5.8KB | **Investigate** — known skill, stub state |
| `byteport-landing` / `hwledger-landing` / `phenokits-landing` / `thegent-landing` | 57-61 | Astro | 2026-04-25 | landing sites | **Keep** — org pages pattern |
| `PhenoVCS` | 60 | Rust | 2026-04-25 | governance + Cargo.toml 227B (skeletal) | **Re-purpose** — VCS name reserved |
| `Apisync` | 69 | Rust | 2026-04-25 | hex skeleton (empty adapters/application/domain/infra), `lib.rs` 340B | **Re-purpose** — hex skeleton stub |
| `DataKit` | 72 | Python | 2026-04-25 | (unsampled) | **Investigate** |
| `phenoResearchEngine` | 74 | Python | 2026-04-25 | private, (unsampled) | **Investigate** |
| `heliosBench` | 78 | Python | 2026-04-25 | (unsampled) | **Investigate** |
| `ObservabilityKit` | 79 | Rust | 2026-04-25 | (unsampled) | **Investigate** |
| `PhenoMCP` | 79 | Rust | 2026-04-25 | (unsampled) | **Investigate** |
| `ResilienceKit` | 94 | Python | 2026-04-25 | (unsampled) | **Investigate** |
| `PlatformKit` | 97 | Go | 2026-04-25 | (unsampled) | **Investigate** |
| `Tracely` | 128 | HTML | 2026-04-25 | full PRD/PLAN/ADR/FR scaffold, no code | **Re-purpose** — name reserved, spec-only |
| `phenotype-org-audits` | 130 | Rust | 2026-04-25 | (private, unsampled) | **Keep** — likely active audit tooling |

## Recommendations Summary

### Archive (0)
None outright. All <200KB repos either have specs/scaffolding worth preserving as name reservation, or are landing sites / known active stubs. No abandoned-and-replaced candidates surfaced.

### Re-purpose (13) — name reserved, spec scaffolding present, no current consumers
`phenotype-hub`, `phenotype-registry`, `phenoData`, `phenoUtils`, `phenoAI`, `Benchora`, `Metron`, `Httpora`, `Eidolon`, `PhenoVCS`, `Apisync`, `Tracely`, `dinoforge-packs` (already content-bearing).

### Delete (0)
No truly empty placeholders without naming or doc value found.

### Investigate (12) — needs human review for status
`phenotype-shared` (HEADLINE — ADR contradicts repo state), `vibeproxy-monitoring-unified`, `DevHex`, `Sidekick`, `thegent-workspace`, `rich-cli-kit`, `DataKit`, `phenoResearchEngine`, `heliosBench`, `ObservabilityKit`, `PhenoMCP`, `ResilienceKit`, `PlatformKit`.

### Keep (8)
`phenotype-bus`, `*-landing` (5 sites), `cheap-llm-mcp`, `phenotype-org-audits`.

## Cross-Reference with archived-repo-registry

`docs/governance/archived-repo-registry.md` does NOT exist in the canonical governance dir. Existing docs: `canonical-stub-audit-2026-04.md`, `shared-crates-canonical-home-adr-2026-04.md` (the ADR cited in the prompt), `cross-project-reuse-audit-2026-04-25.md`. Recommend creating `archived-repo-registry.md` from this audit's Investigate column once decisions are made.

## Headline ADR Reconciliation Action

`phenotype-shared` per ADR PhenoKits#31 should ship the 4 canonical shared crates (`phenotype-event-sourcing`, `phenotype-cache-adapter`, `phenotype-policy-engine`, `phenotype-state-machine`). **Live state on origin/main:** all 4 are present in `members` (alongside 8 others), and `phenotype-event-sourcing/src/` contains real implementation files. Either the ADR's "dormant" claim is stale, or local checkouts have drifted. **Action:** clone fresh from origin and re-verify before declaring dormancy; update the ADR or the repo accordingly.
