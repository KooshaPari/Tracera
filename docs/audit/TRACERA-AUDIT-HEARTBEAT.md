# Tracera audit heartbeat

Scope: read-only management checks for PR #1132 only. No product fixes, merges,
focused-pane prompts, screenshots, or global harness configuration changes.

Skill consulted: `/Users/kooshapari/.agents/skills/loop-support/SKILL.md`.
The installed generic loop daemon lacks bounded sunset and runs unrestricted CLI
prompts. This audit instead uses a project-specific macOS LaunchAgent.

- Label: `gui/501/studio.pheno.tracera.audit1132`
- Interval: 600 seconds; RunAtLoad starts the first tick immediately.
- Runtime: `/tmp/tracera-audit-heartbeat-1132/`
- Executable: `/usr/bin/python3 /tmp/tracera-audit-heartbeat-1132/tick.py`
- Definition: runtime `heartbeat.plist`; no global plist or policy edits.
- Records: append-only `ledger.jsonl`, current `state.json`, final `handoff.json`.
- Checks: bounded read-only GitHub PR head/state request, local inventory counts,
  named owner, recorded blocker, next action, Pacific timestamp and next fire.
- First verified tick: 2026-10-15 18:29:23 Pacific; PR OPEN.
- First scheduled next fire: 2026-10-15 18:39:23 Pacific.

Terminal criteria: runtime `STOP` marker means user stop; `VERIFIED_COMPLETE`
means coordinator has confirmed every required verification complete. Three
unchanged PR-head/evidence-count/concrete-blocker ticks produce SUNSET_BLOCKED
and a handoff. A PR push by itself is not completion. Sunset writes the ledger
and handoff before unloading only this label; files remain preserved.

The blocker is the coordinator's recorded verification deficit, not a fresh
public Access test at each tick. The heartbeat performs no authentication or
product-side mutation. Review `state.json` for latest actual execution; a
registered interval is not proof that future ticks have run. `/tmp` runtime
survives parent chat exit but is not a reboot-persistent installation.

Verification: `launchctl print gui/501/studio.pheno.tracera.audit1132` confirmed
one registered label, the 600-second interval, first PID 69338, and first tick
receipt. Stop by creating runtime `STOP` (processed at next tick), or unload
exactly this label with `launchctl bootout gui/501/studio.pheno.tracera.audit1132`.
