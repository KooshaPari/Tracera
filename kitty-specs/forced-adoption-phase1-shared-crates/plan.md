---
title: Plan — Forced Adoption Phase 1 Shared Crates
spec: spec.md
date: 2026-04-25
status: Draft
---

## Phasing

Five phases, agent-led. No human checkpoints, no scheduled reviews.
Wall-clock estimates use the agent-time mapping from `~/.claude/CLAUDE.md`
"Timescales: Agent-Led, Aggressive Estimates".

### Phase 1 — Discovery (3–6 tool calls, ~3 min)

Pick the 5 high-value consumer repos and disambiguate the dual home for
`phenotype-health`. Output: a short `discovery.md` (sibling to this
plan) capturing selections + rationale.

**Recommended candidates (from spec.md):**
AgilePlus, thegent, hwLedger, BytePort, PhenoKits.

**Selection rationale signals to capture:**

- **Activity:** recent commit cadence (last 30 days). Top-active repos
  produce the highest signal-to-noise on canonical-type fit.
- **Bespoke type density:** repos with the largest count of local
  error/config/health types are the highest-value migrations.
- **Build green on `main`:** consumer must currently build green so
  that a regression after the migration PR is unambiguous signal.

**Tasks:**

| Task ID | Description |
|---------|-------------|
| D-01 | Confirm AgilePlus, thegent, hwLedger, BytePort, PhenoKits all build on `main`. |
| D-02 | Inventory each repo's local error enums (count + file paths). |
| D-03 | Inventory each repo's local config loaders + health checks. |
| D-04 | **Disambiguate `phenotype-health` canonical home** (FR-11). Compare `phenotype-infrakit/crates/phenotype-health` vs. `phenoShared/crates/phenotype-health`: API surface, last-touched date, downstream coupling. Record ADR-style decision in `discovery.md`. |
| D-05 | Record selection in `discovery.md` with one-line rationale per repo. |

### Phase 2 — Design (3–5 tool calls, ~3 min)

For each (consumer × crate) pair retained from Phase 1, produce a
side-by-side `design/<consumer>-<crate>.md` with:

1. Local type signature(s) being replaced (file path + line range).
2. Canonical type signature.
3. Migration delta: imports to add, types to drop, call-site rewrites.
4. Test impact: which existing tests must keep passing; new tests if
   the canonical type unlocks coverage that wasn't there.
5. **Descope check:** if the local type uses fields not present in
   canonical, mark the pair `descoped: yes` and write a one-line
   "canonical API gap" finding (per spec NG-02).

| Task ID | Description |
|---------|-------------|
| DS-01 | AgilePlus × `phenotype-error-core` design doc. |
| DS-02 | AgilePlus × `phenotype-config-core` design doc. |
| DS-03 | thegent × `phenotype-health` design doc. |
| DS-04 | hwLedger × `phenotype-error-core` design doc. |
| DS-05 | BytePort × `phenotype-config-core` design doc. |
| DS-06 | PhenoKits × `phenotype-health` design doc. |

### Phase 3 — Build (per-consumer migration PRs, parallel-mergeable)

One PR per (consumer × crate) pair, opened against the consumer repo's
default branch. PRs are independent across repos and can be dispatched
as a parallel subagent batch (per `~/.claude/CLAUDE.md` Subagent Swarm
guidance). Within a single consumer repo, sequence PRs so the second
does not collide with the first (small repos may bundle if both deltas
are <50 LOC and orthogonal).

| Task ID | PR scope |
|---------|----------|
| B-01 | AgilePlus → adopt `phenotype-error-core` (FR-03). |
| B-02 | AgilePlus → adopt `phenotype-config-core` (FR-04). |
| B-03 | thegent → adopt `phenotype-health` (FR-05). |
| B-04 | hwLedger → adopt `phenotype-error-core` (FR-06). |
| B-05 | BytePort → adopt `phenotype-config-core` (FR-07). |
| B-06 | PhenoKits → adopt `phenotype-health` (FR-08). |

Each PR's commit body cites this spec + the source PR (phenotype-infrakit
#87) + the audit doc.

### Phase 4 — Test/Validate (per-PR; runs as part of B-0X)

For each PR opened in Phase 3:

1. `cargo build --workspace` green.
2. `cargo test --workspace` green.
3. `cargo clippy --workspace -- -D warnings` green.
4. Local LOC delta recorded in PR description (lines removed from local
   error enum / config loader / health check).
5. Adoption matrix in `tasks.md` updated with PR URL on merge.

### Phase 5 — Deploy (admin-merge per repo)

| Task ID | Description |
|---------|-------------|
| V-01 | Admin-merge each Phase 3 PR (`gh pr merge --admin`) per the GitHub Actions billing constraint in global CLAUDE.md. |
| V-02 | Re-run audit grep methodology (audit §2). |
| V-03 | Update `docs/governance/cross-project-reuse-audit-2026-04-25.md`: replace §2 zero counts with new counts; remove §5 "Phase 1 supply/demand gap" finding once ≥3 consumers per crate are confirmed. |
| V-04 | Update memory entry "Phase 1 LOC Reduction Execution Complete" with adoption confirmation. |

## DAG

| Phase | Task ID | Description | Depends On |
|-------|---------|-------------|------------|
| 1 | D-01 | Confirm 5 candidates build on `main`. | — |
| 1 | D-02 | Inventory local error enums. | D-01 |
| 1 | D-03 | Inventory local config loaders + health checks. | D-01 |
| 1 | D-04 | Disambiguate `phenotype-health` canonical home. | — |
| 1 | D-05 | Record selections in `discovery.md`. | D-02, D-03, D-04 |
| 2 | DS-01 | Design: AgilePlus × error-core. | D-05 |
| 2 | DS-02 | Design: AgilePlus × config-core. | D-05 |
| 2 | DS-03 | Design: thegent × health. | D-05 |
| 2 | DS-04 | Design: hwLedger × error-core. | D-05 |
| 2 | DS-05 | Design: BytePort × config-core. | D-05 |
| 2 | DS-06 | Design: PhenoKits × health. | D-05 |
| 3 | B-01 | Build PR: AgilePlus error-core. | DS-01 |
| 3 | B-02 | Build PR: AgilePlus config-core. | DS-02, B-01 (sequence within repo) |
| 3 | B-03 | Build PR: thegent health. | DS-03 |
| 3 | B-04 | Build PR: hwLedger error-core. | DS-04 |
| 3 | B-05 | Build PR: BytePort config-core. | DS-05 |
| 3 | B-06 | Build PR: PhenoKits health. | DS-06 |
| 4 | (embedded in each B-0X) | cargo build/test/clippy + LOC delta. | corresponding B-0X |
| 5 | V-01 | Admin-merge each PR. | all of Phase 3 (per-PR independent). |
| 5 | V-02 | Re-run audit methodology. | V-01 (all merged). |
| 5 | V-03 | Update audit doc. | V-02. |
| 5 | V-04 | Update memory entry. | V-02. |

## Parallelism Map

- **Phase 1:** D-02, D-03, D-04 are independent — dispatch as 3 parallel
  subagents.
- **Phase 2:** all 6 design tasks are independent — dispatch as 6
  parallel subagents.
- **Phase 3:** all 6 build PRs are independent across repos — dispatch
  as 6 parallel subagents. Within AgilePlus, B-02 should sequence after
  B-01 to avoid conflict on the same workspace `Cargo.toml`.
- **Phase 5:** V-01 admin-merges run as a single batch; V-02/V-03/V-04
  are sequential after.

## Out-of-Scope (mirrors spec.md NG-01..NG-06)

- Pre-adoption deprecation of local types.
- Canonical API edits.
- Re-homing Phase 1 crates from `phenotype-infrakit` to `phenoShared`
  (apart from FR-11's `phenotype-health` disambiguation).
- Go-shared crates.
- OTel-bootstrap consolidation.
- `phenotype-cloud-acquire`.

## Estimated Effort

Per the timescale rubric:

- Phase 1 Discovery: ~3 min, 1 parallel subagent batch.
- Phase 2 Design: ~5 min, 1 parallel subagent batch (6 tasks).
- Phase 3 Build: ~15 min, 1 parallel subagent batch (6 PRs across
  6 repos; AgilePlus serializes 2 PRs).
- Phase 4 Test/Validate: embedded.
- Phase 5 Deploy: ~3 min sequential.

Total: **~25 min wall-clock**, ~3 parallel subagent batches.
