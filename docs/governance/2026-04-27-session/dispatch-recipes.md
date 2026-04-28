# dispatch-worker Recipe Book

## Pattern 1: Fire-and-forget research wave (most common)
```bash
mkdir -p /tmp/wave_NNN
for i in $(seq 1 8); do
  dispatch-worker --tier minimax-direct \
    --prompt "5 patterns for X. ≤120 words." \
    > /tmp/wave_NNN/iter_$i.out 2>&1 &
done
```
Don't wait for output unless you need it for the next decision.

## Pattern 2: Backgrounded inline parent work
```bash
(
  set +e
  # ... heavy bash sequence ...
) > /tmp/job_log.log 2>&1 &
echo "PID $!"
# Continue parent work; log inspectable later.
```

## Pattern 3: Until-loop drain
```bash
until [ -z "$(gh search prs --owner X --state open --json url --jq '.[].url' | head -1)" ]; do
  for url in $(gh search prs --owner X --state open --json url --jq '.[].url'); do
    gh pr merge "$url" --squash --admin --delete-branch
  done
  sleep 4
done
```

## Pattern 4: Process backpressure
```bash
until [ "$(ps aux | grep dispatch-worker | grep -v grep | wc -l | tr -d ' ')" -lt 30 ]; do
  sleep 4
done
```
Run before firing >30 new dispatches.

## Pattern 5: Reusable script via real .sh file
**Don't:** `bash -c "$(declare -f fn); fn arg"` (heredoc escape hell)
**Do:** Write to `/tmp/job.sh`, chmod +x, then `bash /tmp/job.sh arg1 arg2`

## Pattern 6: Cleanup discipline
```bash
ls -dt /tmp/wave* 2>/dev/null | tail -n +30 | xargs rm -rf
```
Periodic prune avoids /tmp bloat across long sessions.

## Pattern 7: Pre-flight
```bash
df -h / | tail -1                    # disk
curl -sf http://localhost:20128/v1/models -o /dev/null && echo UP  # omniroute
gh api rate_limit --jq '.resources.core.remaining'  # GH
```
Always before mass dispatch.

## Pattern 8: Tier diversity (avoid single point of failure)
Spread waves across `minimax-direct`, `kimi-direct`, `freetier`. If one rate-limits, others continue.

## Pattern 9: Rate-limit cooldown burn
When GH = 0, switch to:
- dispatch-worker waves (no GH calls)
- Authoring governance docs
- Memory updates
- Cleanup scripts that use only local data

## Pattern 10: Self-pacing wakeup
```bash
ScheduleWakeup delaySeconds=270 prompt="/loop ..."
```
But ALSO: dispatch fresh waves before ending the turn — wakeup is a safety net.
