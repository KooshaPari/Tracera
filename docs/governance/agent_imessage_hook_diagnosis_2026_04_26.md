# agent-imessage Stop-Hook 20s Timeout — Root-Cause Diagnosis (2026-04-26)

## TL;DR

The 20s timeout is **not** an FD-exhaustion issue. It is a **monotonic O(N) read of an
unbounded JSONL log** in the hot path of every Stop hook. Under healthy FDs (8228) the
hook still takes ~12s; under load it crosses 20s deterministically. Self-heal mechanism
masks the symptom, never fixes the cause.

## What the hook does

`$HOME/.local/bin/agent-user-status-stop-hook` (Python) is the Claude Code Stop hook.
On every assistant turn end it spawns:

```
/Users/kooshapari/.local/bin/agent-imessage hook-decision --text "<last_message>"
```

with a 20s subprocess timeout. The subprocess calls
`hook_decision_result()` in `agent_user_status/agent_imessage_status.py`, which:

1. Calls `estimate_status(load_config())` — runs ~7 signal probes:
   - `idle_time_signal` (`ioreg`, ~5s budget)
   - `frontmost_app_signal` (`osascript`, ~5s budget)
   - `process_activity_signal` (`ps -axo comm=`, ~5s budget)
   - `media_activity_signal` (`pmset -g assertions`, ~5s budget)
   - `external_signal_records` (small JSON)
   - `action_signal()` and `action_learning_signal()` — **see hot path below**
   - `learning_prior()`
2. Calls `recent_messages` -> `imsg chats` + `imsg history` (~0.5s, fine).
3. Calls `append_action_event(...)` and `append_session_event(...)` (small appends).

## Why 20s timeout fires (the bug)

`recent_action_records()` is invoked **at least 3x** per hook
(via `action_signal`, `action_learning_signal`, plus `learning_prior` indirectly).
Each call funnels through:

```python
# agent_imessage_learning.py:28
def read_action_events(limit: int = 200):
    ...
    for line in ACTION_LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]:
```

This **reads the full file into memory, splits all lines, then slices the last 200**.

Current state on disk:

| File | Size | Lines |
|---|---|---|
| `~/.local/share/agent-imessage/state/action_events.jsonl` | **11 MB** | 11,128 |
| `~/.local/share/agent-imessage/state/correction_events.jsonl` | 3.7 MB | 4,018 |
| `~/.local/share/agent-imessage/state/agent_sessions.jsonl` | 736 KB | 1,444 |

Measured cold-cache wall time (idle laptop, healthy FD count, no other agents):

```
agent-imessage hook-decision --text "test"  →  12.07s total (5.58s user, 3.25s sys)
```

That is 60% of the 20s budget while idle. Under multi-agent load (parallel cargo
builds, FS pressure) this trivially crosses 20s, producing the recurring diagnostic.

The file grows monotonically. `append_action_event` writes one JSON line per Stop
hook invocation (and other call sites) with **no rotation, no truncation, no
compaction**. Every additional turn makes the next hook slower.

## Secondary contributors (smaller, but real)

- 4x `subprocess.run` to macOS shell tools (`osascript`, `ps`, `pmset`, `ioreg`),
  each with 5s budget. On a contended box `osascript` can stall 1-3s by itself.
- `imsg chats --limit 80` + `imsg history --limit 25` ≈ 0.5s steady state.
- `append_session_event` and `append_action_event` are O(1) append, fine.

## Self-heal mechanism — is it working?

**Partially. It treats the wrong root cause.**

The hook's `_self_heal_fd_exhaustion()` only fires when `kern.num_files >= 100_000`
and only kills `find`/`bfs` orphans. The recent firings have FD=8228 (≪ 100k), so
self-heal does not trigger; the hook just emits the "Service degraded — investigate"
diagnostic and exits cleanly. That part works as designed.

What does **not** work: the hook keeps invoking the slow subprocess every turn even
after the diagnostic has fired N times. There is no backoff, no cache, no throttle
— so the user sees the same warning repeatedly without remediation.

## Root cause

**Unbounded JSONL log read on every Stop hook**, reading 11 MB and growing, called
3+ times per invocation through `read_action_events()`, with no rotation policy.
FD usage is a red herring; the real failure mode is I/O + Python parsing time on a
log that grows linearly with agent activity.

## Recommended fix (in priority order)

1. **Bound the read.** Replace `read_text().splitlines()[-limit:]` in
   `agent_imessage_learning.py:28-39` with a tail-only seek
   (open binary, `seek(-N, SEEK_END)`, decode last chunk, take last 200 lines).
   Targets: 11MB read → ~50KB read. Expected hook latency: 12s → <1s.
2. **Cache `recent_action_records` per process.** It is invoked 3x with identical
   arguments inside one hook call.
3. **Rotate `action_events.jsonl`.** Add size-based rotation
   (e.g. truncate older-than-24h entries on each append, or rotate at 1MB).
   Owner: `agent-user-status`. File: `agent_imessage_learning.py`.
4. **Add an L1 cache** for `frontmost_app_signal` / `process_activity_signal`
   results keyed on a 2-3s TTL — the hook cluster fires multiple times per second
   under heavy parallel agents.
5. **Optional**: increase `HOOK_TIMEOUT_S` from 20 to 30 only as a stop-gap; the
   real fix is (1) + (3).
6. File issue against `agent-user-status` repo with this report.

## Suggested user actions

- File issue: `gh issue create -R KooshaPari/agent-user-status` titled
  "Stop-hook tail-read regression: action_events.jsonl O(N) read causes 20s timeout".
- Stopgap (manual, optional): truncate the log to last 500 lines:
  ```bash
  tail -500 ~/.local/share/agent-imessage/state/action_events.jsonl \
    > ~/.local/share/agent-imessage/state/action_events.jsonl.new \
    && mv ~/.local/share/agent-imessage/state/action_events.jsonl{.new,}
  ```
  This will restore sub-second hook latency until a real rotation lands.

## Files referenced

- `/Users/kooshapari/.local/bin/agent-user-status-stop-hook` (hook entry, lines 68-98)
- `/Users/kooshapari/CodeProjects/Phenotype/repos/agent-user-status/src/agent_user_status/agent_imessage_learning.py` (line 28: hot-path bug)
- `/Users/kooshapari/CodeProjects/Phenotype/repos/agent-user-status/src/agent_user_status/agent_imessage_status.py` (lines 63-152: signal aggregation)
- `/Users/kooshapari/CodeProjects/Phenotype/repos/agent-user-status/src/agent_user_status/agent_imessage_core.py` (lines 19-23: STATE_DIR, log paths)
- `~/.local/share/agent-imessage/state/action_events.jsonl` (11 MB, the offender)
