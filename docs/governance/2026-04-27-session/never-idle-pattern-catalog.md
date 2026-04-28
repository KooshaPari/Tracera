# Never-Idle Pattern Catalog
**Source:** Empirically observed during 7+ hour 2026-04-27 evening session.

## Defining "idle"
- ❌ "Holding for next /loop fire"
- ❌ "Waiting for wakeup"
- ❌ "Stopping here for this iteration"
- ❌ "Will continue when GH rate-limit resets"

## What's NOT idle
- ✓ Tool call still in flight (background bash, dispatched workers)
- ✓ Authoring governance docs (parent inline)
- ✓ Updating memory entries
- ✓ Cleaning up /tmp scratch dirs
- ✓ Running until-loops that wait on rate-limit reset (then drain immediately)
- ✓ State snapshot scripts
- ✓ Process-load monitoring

## Parent-inline work that fills cooldown windows
1. **Governance authoring** — turn dispatch-worker outputs into structured docs
2. **Memory cycling** — date-stamp transient memories, deprecate old ones
3. **Script writing** — codify patterns (lockfile_regen_v2, branch_cleanup_wide)
4. **/tmp hygiene** — periodic prune
5. **MEMORY.md curation** — keep ≤200 lines, push older to dated subdirs
6. **JSON state snapshots** — emit machine-readable state for next agent

## Dispatch-burning patterns
1. **Wave-of-5-patterns prompts** — each wave generates ≤120-word lists
2. **Tier rotation** — minimax → kimi → freetier each wave (avoid single point)
3. **Concurrency cap** — 30-40 active workers max (saturation at 80+)
4. **Backpressure via until-loop** — `until [ count -lt 30 ]` before next wave
5. **Cleanup after every 30 waves** — `ls -dt /tmp/wave*` keep latest

## Until-loop patterns that count as "active"
```bash
# Wait-for-rate-limit (active even though sleeping)
until [ "$(gh api rate_limit --jq .remaining)" -gt 100 ]; do sleep 30; done
```
This counts as active because the LOOP is committed; when condition hits, immediate action follows.

## What ends a turn correctly
1. Tool call still in flight
2. Fresh dispatch (≥10 workers fired in last bash command)
3. Inline output produced (file written, memory updated, commit made)
4. ScheduleWakeup armed AND step 1-3 also done

## What ends a turn incorrectly
1. "Holding" + nothing dispatched
2. ScheduleWakeup with no other action
3. End-of-turn summary with no tool calls

## Boundary cases
- **GH API exhausted**: switch to dispatch + governance authoring; until-loop awaits reset.
- **Disk pressure**: target-pruner inline; do NOT idle; cleanup is work.
- **Process saturation**: wait for queue to drop, then resume; use the wait time to author.
- **Worker tier exhausted**: switch tier; if all exhausted, parent inline only.

## Operator override
The operator can say "stop" to end a session, but the agent NEVER ends voluntarily.
