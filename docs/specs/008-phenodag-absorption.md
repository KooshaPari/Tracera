# Spec 008: phenodag absorption (DAG/queue/atomic-claim/lease/dedup)

> Absorbs: phenodag v0.3.0 (https://github.com/KooshaPari/phenodag)
> Sponsor decision: D3 = YES (thin redirector for 1 release, then archive phenodag).
> Date: 2026-07-05
> Source: `docs/sessions/2026-07-05-polyrepo-portfolio-strategy/03-audits/03-phenodag-absorption-spec.md`

## Scope (this spec)

This spec absorbs the **trace-spine** concerns from phenodag into Tracera:
the DAG/queue/atomic-claim/lease/dedup machinery. The PM/cockpit concerns
go to AgilePlus spec 008.

## FR table

| FR | Title | Source (phenodag) | Target (Tracera) | Notes |
|---|---|---|---|---|
| TRC-PHENO-001 | Atomic SQLite claim | `phenodag.go` claim/pick | `crates/tracera-server/src/queue/claim.rs` | port + extend |
| TRC-PHENO-002 | Heartbeat / reclaim | `phenodag.go` heartbeat/reclaim | `crates/tracera-server/src/queue/heartbeat.rs` | new |
| TRC-PHENO-003 | Release / done / fail | `phenodag.go` release/done/fail | `crates/tracera-server/src/queue/lifecycle.rs` | port |
| TRC-PHENO-004 | Fuzzy duplicate detection | `phenodag.go` dupes | `crates/tracera-server/src/dedup/` | new module |
| TRC-PHENO-005 | WAL SQLite (modernc.org/sqlite) | `phenodag.go` + `go.sum` | `crates/tracera-server/src/db/sqlite.rs` | pure-Go -> pure-Rust (sqlx or rusqlite) |
| TRC-PHENO-006 | Mangled-git + no-git tolerant scanner | `phenodag.go` cmdScan | `crates/tracera-edge/src/scan/` | new |
| TRC-PHENO-007 | Trace export (JSON/YAML) | `phenodag.go` export | `crates/tracera-server/src/export/` | port |
| TRC-PHENO-008 | Beads (bd) compatibility | `phenodag.go` bd wrapper | `crates/tracera-server/src/beads_compat/` | new |
| TRC-PHENO-009 | Status / validate | `phenodag.go` status/validate | `crates/tracera-server/src/queue/health.rs` | port |
| TRC-PHENO-010 | Init / seed | `phenodag.go` init/seed | `crates/tracera-server/src/queue/init.rs` | port |

## Phased migration

| Phase | What | Effort | Risk |
|---|---|---|---|
| P1 | Port TRC-PHENO-001 to TRC-PHENO-003 (atomic claim, heartbeat, lifecycle) | 1 PR | low |
| P2 | Port TRC-PHENO-004, TRC-PHENO-005 (dedup, SQLite) | 1-2 PRs | medium |
| P3 | Port TRC-PHENO-006, TRC-PHENO-007 (scanner, export) | 1-2 PRs | low |
| P4 | Port TRC-PHENO-008 (beads compat) | 1 PR | low |
| P5 | Port TRC-PHENO-009, TRC-PHENO-010 (status, init) | 1 PR | low |
| P6 | Archive `phenodag` repo | 1 commit | low |

Total: ~6-8 PRs over 2-3 weeks.

## Why these go to Tracera (not AgilePlus)

Tracera is the **trace spine**. The DAG/queue/atomic-claim/lease/dedup
machinery is the substrate that tracks *what work is happening* across
the polyrepo fleet. This is a trace concern, not a PM concern. PM
concerns (cockpit, portfolio, conventional commits) are in AgilePlus
spec 008.

## Cross-references

- AgilePlus spec 008: phenodag absorption (PM/cockpit/portfolio concerns)
- phenodag repo: https://github.com/KooshaPari/phenodag (will be archived)
- phenodag ADR-dag-superset-merge: https://github.com/KooshaPari/phenodag/blob/main/docs/adr/ADR-dag-superset-merge.md
  (dagctl was already absorbed into phenodag; Tracera is the next absorption)
- polyrepo portfolio strategy session: `docs/sessions/2026-07-05-polyrepo-portfolio-strategy/`

## Sign-off

- Spec author: root manager (polyrepo portfolio strategy 2026-07-05)
- Tracera team: TBD (this is a spec-level request, not yet a coding PR)
- Phenodag consumers: see the 1-release redirector PR for migration timing
