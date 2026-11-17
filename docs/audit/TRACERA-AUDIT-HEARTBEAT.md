# Persistent ownership heartbeat, 2026-10-15

The former /tmp runtime and launchd label were absent at 19:42 PDT; historical
18:29/18:39 receipts do not establish continuing execution or a prior sunset.
The monitor was restored with durable project-only state and a login LaunchAgent.

- Label: `gui/501/studio.pheno.tracera.audit1132`
- State directory: `~/.local/state/tracera-audit-1132/`
- Definition: `~/Library/LaunchAgents/studio.pheno.tracera.audit1132.plist`
- Executable: `/usr/bin/python3 ~/.local/state/tracera-audit-1132/tick.py`
- Schedule: `StartInterval=600`, `RunAtLoad=true`; survives chat exit and login/reboot.
- First real receipt: **2026-10-15 19:54:59 PDT**, ACTIVE, exit 0.
- First nominal next due: **2026-10-15 20:04:59 PDT**. Sleep may delay execution.
- Snapshot: PR OPEN at `1289421542adfd2356de05b72b16fe54e8b44bd7`; 25 gaps,
  44 view rows, 69 total rows, 25 issue headings, 37 Unknown rows across the
  whole inventory. The earlier 33 Unknown denominator concerned view rows only.
- Public unauthenticated project-list request returned 302, an Access redirect;
  this is not authenticated acceptance and does not alter Access policy.

Each tick records Pacific time, owner, PR head/state, bounded inventory and issue
counts, public HTTP status, concrete blocker and next authorized action in
append-only `ledger.jsonl` and current `state.json`. Reads are limited to GitHub
and an unauthenticated HTTP status probe. The monitor does not run coding agents,
repair products, prompt panes, navigate authenticated sessions or merge PRs.

Three consecutive unchanged external-blocker snapshots produce SUNSET_BLOCKED.
A changed PR head, count or public status resets that counter. Read failures are
MONITOR_ERROR and do not advance the blocker counter. PR closure/merge alone is
never proof that the audit is complete. `STOP` produces SUNSET_CANCELLED;
`VERIFIED_COMPLETE.json` requires `all_required_verification_complete: true`
and nonempty `evidence`, supplied only after coordinator verification of every
required audit check. That marker produces SUNSET_COMPLETE.

Every sunset writes permanent `handoff.json`, preserves the ledger and archives
only the owned plist under state-directory `sunset/` before unloading only its
own label. Archiving prevents reboot restart. Inspect actual state/ledger for
execution evidence; the nominal next due is not proof that a tick ran.

Stop at next tick: `touch ~/.local/state/tracera-audit-1132/STOP`.
Immediate stop: `launchctl bootout gui/501/studio.pheno.tracera.audit1132`, then
move the owned plist into the state directory so it cannot reload at login.
The runtime `README.md` retains the same operating instructions.

Validation passed: real first-tick receipt and launchctl exit 0; loaded service
reports runatload and a 600-second interval. Offline isolated tests exercised
three identical blocker ticks with three ledger records and final handoff,
changed-head reset, cancellation and explicit completion. Service controls were
disabled for those tests, leaving the live schedule untouched.
