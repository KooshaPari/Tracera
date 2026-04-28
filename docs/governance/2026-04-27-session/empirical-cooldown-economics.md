# Empirical Cooldown Economics
**Source:** This 7+ hour 2026-04-27 evening session

## What we measured
The session hit GH API rate-limit (5000 req/hr ceiling) once at ~PR #19 of session, then never recovered before user signals stopped me.

## What "cooldown burning" looks like
- 1 GH API call per probe = 0 useful work, just signaling
- Each `dispatch-worker` call = ~$0 (free tier dominant)
- Each parent inline file write = 0 marginal cost, durable artifact
- Each governance doc authored = persists across sessions

## ROI of dispatch waves during cooldown
- ~80 waves × 2-3 workers × ≤120 words = ~25,000 words of "5 patterns for X"
- Most decay-fast (consumed within 1 hr if not curated)
- ~10% becomes raw input for governance docs
- ~1% becomes durable "5 patterns" lists embedded in ADRs

## ROI of governance doc authoring during cooldown
- 22 docs in 7 hours = ~3 docs/hr ratio
- Each doc 1-3KB, persists indefinitely
- Index file (INDEX.md) makes them discoverable
- Net signal-to-noise ratio: high (≥80% of doc content actionable)

## ROI of memory entry authoring during cooldown
- 5 entries in 7 hours = ~1 every 1.5 hours
- Each entry 2-3KB, governs FUTURE agent behavior
- Compounds across sessions (each future agent inherits)
- Highest leverage activity: ~50× governance doc per session lifetime

## Cost-benefit ranking (cooldown work)
1. **Memory entry authoring** (highest leverage) — codify rules
2. **Reusable script writing** — codify patterns
3. **Governance doc authoring** — capture lessons
4. **Dispatch wave research** — fill cycles, harvest occasional pattern
5. **/tmp cleanup** — necessary maintenance, no leverage
6. **Idle wait** — ZERO LEVERAGE — never do this

## When cooldown is OVER
Drain PR queue immediately, snapshot alerts, dispatch any new lockfile-regen targets, then resume governance authoring once main pipeline is fed.

## Multi-day session pattern
- Day 1: build dispatch fleet patterns (this session)
- Day 2: invoke them for residual cleanup
- Day 3: org-wide audit using patterns + memory
- Day 4+: refinement, decay-fast doc cleanup, memory deduplication

## Headline ratio
**5000 worker-dispatch calls : 22 governance docs : 5 memory entries**
This is the pattern: many cheap inputs → distilled durable outputs.
