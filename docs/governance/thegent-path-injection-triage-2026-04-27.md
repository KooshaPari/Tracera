# thegent Path-Injection Alert Triage — 2026-04-27

**Repo:** KooshaPari/thegent (archived=false)
**Source:** GitHub code-scanning, `state=open`, rules `rust/path-injection` + `py/path-injection`
**Method:** API-only inventory; no dismissals performed.

## Totals

| Category | Count | Rust | Python |
|----------|-------|------|--------|
| **Total open** | 242 | 182 | 60 |
| **False-positive (test/bench/archive)** | 69 | 66 | 3 |
| **Real product code (human triage)** | 173 | 116 | 57 |

False-positive classification rule: path matches `tests/`, `test_*`, `*_test.{rs,py}`, `benches/`, `examples/`, `benchmark/`, `.archive/`, `vendor/`, `node_modules/`, or `target/`.

## False-Positive Clusters (auto-dismiss candidates)

| Count | File |
|------:|------|
| 41 | `crates/thegent-hooks/tests/changed_files_enhancement.rs` |
| 14 | `crates/thegent-hooks/tests/phase1_5_git_enhancement.rs` |
| 11 | `crates/thegent-hooks/tests/phase1_cli.rs` |
|  2 | `benchmark/tbench_validate.py` |
|  1 | `heliosHarness/benchmark/src/helios_bench/local_runner.py` |

## Top-10 Real-Code Hot Files (human triage)

| Count | File | Lang |
|------:|------|------|
| 64 | `crates/thegent-hooks/src/main.rs` | rust |
| 20 | `templates/shared/scripts/quality/quality_runner.py` | py |
| 13 | `hooks/hook-dispatcher/src/governance_fs.rs` | rust |
| 10 | `crates/harness-native/src/dispatcher.rs` | rust |
|  9 | `scripts/worktree_governance_inventory.py` | py |
|  7 | `hooks/hook-dispatcher/src/main.rs` | rust |
|  7 | `.kittify/scripts/tasks/tasks_cli.py` | py |
|  5 | `scripts/worktree_legacy_remediation_report.py` | py |
|  5 | `crates/thegent-runtime/src/main.rs` | rust |
|  5 | `crates/thegent-hooks/src/report.rs` | rust |

Top-1 file (`thegent-hooks/src/main.rs`, 64 alerts = 26% of all open alerts) is the highest-leverage fix target — single-file remediation would close ~26% of backlog and ~37% of real-code alerts.

## Notes

- 25 distinct real-code files account for 173 alerts; long-tail (16 files with ≤4 alerts each) totals 29 alerts.
- Hook-dispatcher and thegent-hooks subsystems dominate (sums to ~104 real alerts) — strong signal these crates need a shared path-validation helper.
- No dismissals performed. Manual review required before any `gh api ... -X PATCH` dismissal.
