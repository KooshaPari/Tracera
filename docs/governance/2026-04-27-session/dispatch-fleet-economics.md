# Dispatch-Fleet Economics — empirical from this session

## What we did
Spawned ~1370 waves × 2-4 workers each = ~3500-5000 dispatch-worker invocations across ~7 hours.

## What it cost
- **Free tier (~80%)**: minimax-2.5-free + gpt-oss-120b-free → $0
- **Paid tier (~20%)**: minimax-m2.7-highspeed → estimated <$1
- **Total**: ~$1 for 5000 worker calls

## What we got back
- ~5000 short-form research outputs (5-list patterns, ≤120 words each)
- Aggregate output text: ~600,000 words of "how to ___" content
- Most useful: governance pattern enumeration (when authoring docs), tier benchmark data
- Most wasted: redundant patterns surfaced 5x across waves

## When this scales
- Single-shot text completion at sub-second latency: optimal for 100+ parallel research queries.
- File-write tasks: NOT optimal (workers fabricate output).
- Multi-step reasoning chains: NOT optimal (no tool-use, single-shot).

## Anti-patterns observed
1. Saturation at 80+ concurrent → omniroute queues + 503s. Cap: 30-40.
2. Reading worker output token-by-token wastes parent context. Read only summaries.
3. Repeating prompts close to each other → high redundancy. Vary categories per wave.
4. Cleaning up /tmp/wave* dirs is essential (20MB+ per session if uncleaned).

## Optimal use cases proven this session
- Burning GH-rate-limit cooldown productively (50+ waves between rate-limit checks)
- Authoring governance docs from "5 patterns for X" prompts
- Generating reference cards / cheat-sheets
- Decay-fast research (don't read; just produce, archive)

## Anti-uses
- Dependency analysis (better via cargo tree --invert)
- Code generation (better via codex exec)
- Multi-file refactor (better via parent inline)
- Truth verification (no tool use, no source access)

## Cost-benefit boundary
A wave is worth firing when:
- The output category enriches a governance doc you're writing
- You're rate-limit cooldown burning
- The aggregate text becomes a corpus for later synthesis

A wave is NOT worth firing when:
- You'd just throw away the output
- You need verifiable execution (use Bash inline)
- The same prompt has fired 3+ times this session
