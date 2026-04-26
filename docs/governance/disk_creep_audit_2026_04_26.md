# Disk Creep Audit — 2026-04-26

## Pre-flight vs Current Delta

| Time | Free | Notes |
|------|------|-------|
| Wave start (~morning) | ~23 Gi | Baseline, post-prune |
| Mid-wave | 14 Gi | cargo storms, recovered to 23 Gi by target prunes |
| Recent decline | 23 → 20 → 19 → 18 Gi | **Steady creep, ~5 Gi lost** |
| **Now** | **23 Gi (24 Gi avail)** | df -h reports 23Gi used / 24Gi avail on /dev/disk3s1s1 |

Note: `df` currently reads 23 Gi free — slight recovery vs the reported 18 Gi low. Investigation focuses on what consumed 5+ Gi during the wave that did NOT come from `target/` (those were pruned).

## Top 10 Disk Consumers (Repo + System)

| Rank | Path | Size | Class | Recent? |
|------|------|------|-------|---------|
| 1 | `/Users/kooshapari/Library/Caches` (aggregate) | **32 G** | OS / app caches | mixed |
| 2 | **`/private/tmp`** | **17 G** | **Agent scratch clones** | **YES (108 dirs mtime <24h)** |
| 3 | `repos/hwLedger/target` | 8.7 G | Rust target | yes (post-prune rebuild) |
| 4 | `repos/AgilePlus/target` | 8.4 G | Rust target | yes |
| 5 | `repos/FocalPoint/target` | 6.4 G | Rust target | yes |
| 6 | `~/Library/Caches/org.swift.swiftpm` | 4.2 G | SwiftPM | likely |
| 7 | `~/.cargo/registry` | 4.2 G | Cargo registry | grew with cargo storms |
| 8 | `/private/var/folders` | 4.2 G | macOS per-user temp | active |
| 9 | `~/Library/Caches/go-build` | 3.5 G | Go build cache | likely (Tracera/Tokn/heliosCLI) |
| 10 | `repos/cloud/node_modules` | 2.5 G | Node deps | static |

## Primary Creep Source: `/private/tmp` (17 G)

**108 directories with mtime within last 24h.** 695 total entries. Agent-spawned scratch clones for audits, PR prep, fix branches, fresh-compares.

### Top /private/tmp consumers

| Path | Size | Purpose |
|------|------|---------|
| `tracera-fresh-compare.5jNnUP` | 2.5 G | Tracera scratch |
| `tracera-gitpython-hotfix` | 2.3 G | Tracera hotfix branch |
| `tracera-recovery-pr.2d6quZ` | 1.6 G | Tracera recovery |
| `phenokits-fresh.TDBzua` | 1.0 G | Phenokits scratch |
| `audit_AuthKit` | 874 M | Audit clone |
| `phenokits-clean-20260426-193911` | 738 M | Phenokits clean |
| `phenokits-next-plan.iVJQ4z` | 716 M | Phenokits plan |
| `thegent-readme-fix` / `thegent_fix` / `thegent_check` | 573 M × 3 | TheGent triplicate clones |
| `PhenoProc` | 571 M | PhenoProc clone |
| `phenokits-ledger.4xmmBn` | 565 M | Phenokits ledger |
| `audit_BytePort` | 556 M | Audit clone |
| `audit_Benchora` | 465 M | Audit clone |
| `audit_Dino` | 342 M | Audit clone |

**Group totals:**
- `tracera*` aggregate: **6.3 G**
- `phenokits*` aggregate: **3.2 G**
- `audit_*` aggregate: **2.3 G**
- `thegent*` aggregate: **1.7 G**

## Recommended Prunes (safest first)

| Order | Target | Size | Command | Risk |
|-------|--------|------|---------|------|
| 1 | `/private/tmp/audit_*` (completed audits) | ~2.3 G | `rm -rf /private/tmp/audit_*` | **LOW** — audits done, already committed to repo |
| 2 | `/private/tmp/tracera-fresh-compare.*` + `tracera-recovery-pr.*` (mktemp suffix dirs) | ~4.1 G | `rm -rf /private/tmp/tracera-fresh-compare.* /private/tmp/tracera-recovery-pr.*` | **LOW** — temp suffix indicates mktemp scratch |
| 3 | `/private/tmp/phenokits-*` (suffix `.XXXXXX` mktemp) | ~3 G | `rm -rf /private/tmp/phenokits-*.??????` | **LOW** — mktemp scratch, sessions complete |
| 4 | `/private/tmp/thegent_check`, `/private/tmp/thegent_fix`, `/private/tmp/thegent-readme-fix` | ~1.7 G | individual `rm -rf` after verifying no uncommitted work | **MEDIUM** — verify each is clean first |
| 5 | `/private/tmp/tracera-gitpython-hotfix` | 2.3 G | `cd && git status` first; rm if clean | **MEDIUM** — non-mktemp name, confirm hotfix landed |
| 6 | `/private/tmp/PhenoProc`, `/private/tmp/AgentMCP-fix`, `/private/tmp/agentapi_fix` etc. | ~2 G | per-dir verify-then-rm | **MEDIUM** |
| 7 | `~/.cargo/registry` cache trim | save ~1-2 G | `cargo cache --autoclean` | **LOW** — refetched on demand |
| 8 | `~/Library/Caches/go-build` | 3.5 G | `go clean -cache` | **LOW** — rebuilds on next compile |
| 9 | `~/Library/Caches/org.swift.swiftpm` | 4.2 G | manual purge | **LOW-MED** — refetched |

**Recoverable in safe-zone (orders 1-3 + 7-8):** ~13-14 G. Brings free from 23 → 36+ Gi.

## Root Cause

Agent-driven `mktemp -d` and ad-hoc `/private/tmp/<name>` clones are not being cleaned up after task completion. Today's autonomous wave produced **108 fresh /tmp dirs**, many full-tree clones (300 MB – 2.5 GB each). No agent self-reported large consumption because each individual clone is moderate; the cumulative effect is 17 G.

## Recommended Policy (out of scope for this dispatch)

- Agents using `mktemp -d` MUST `trap 'rm -rf "$DIR"' EXIT`.
- Long-lived `/private/tmp/<name>` clones (non-mktemp) need a session-end sweep.
- Add nightly cron: `find /private/tmp -maxdepth 1 -type d -mtime +1 -name 'audit_*' -exec rm -rf {} +`.

## Out-of-Scope

This audit is read-only. Each prune is a separate dispatch.
