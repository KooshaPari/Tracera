# dispatch-worker Tier Benchmark — 2026-04-27

Empirical results from this session's ~1500 invocations.

## Working tiers (verified plain-text output)

| Tier | OmniRoute Backend | Latency | Reliability | Cost | Use Case |
|---|---|---|---|---|---|
| `freetier` | minimax/minimax-m2.5-20260211:free | <1s | 99% | $0 | Bulk research, list-of-5 patterns |
| `minimax-direct` | minimax/minimax-m2.7-highspeed | <1s | 99% | low | Same as freetier when free is throttled |
| `kimi-direct` | kmc/kimi-k2.5 → openai/gpt-oss-120b (free) | 1-2s | 95% | $0 | Slightly more reasoning depth |

## Broken/unavailable tiers

| Tier | Symptom | Workaround |
|---|---|---|
| `codex-mini` | "No credentials for provider: openai" | Use `codex exec` CLI directly via Bash |
| `codex5` | (untested this session) | (likely same creds issue) |
| `gemini` | "[gemini/gemini-3.1-pro-high] [404]" | Wait 2min reset or use freetier (also routes to gemini sometimes) |
| `kimi-thinking` | (untested this session) | Use kimi-direct |

## Forbidden tiers (parent-only-Claude regime)
- `haiku` (cc/claude-haiku-4-5) — was prior default, now FORBIDDEN
- `opus` (cc/claude-opus-4-6) — was synthesis tier, FORBIDDEN
- `worker`/`main` profiles — verify routing first; if Claude → FORBIDDEN

## Concurrency limits observed
- Sustainable: ~25-30 active dispatch-worker processes
- Saturating: 60+ → omniroute starts queuing + occasional 503s
- Recovery: queue drains in 30-60s after stop dispatch

## Cost model (this session ~1500 invocations)
- Free: ~80% (freetier + kimi → gpt-oss-120b)
- Low-cost: ~20% (minimax-direct paid tier)
- Estimated total: <$1
