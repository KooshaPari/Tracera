# Worker-Task Routing Matrix (parent-only-Claude regime)

## Decision matrix: which tier for which task

| Task class | Best tier | Why | Backup |
|---|---|---|---|
| One-liner research (5-list, 1-line each) | freetier | Free, sub-second | minimax-direct |
| Structured analysis (≤200 words) | minimax-direct | M2.7-highspeed reasoning + low cost | kimi-direct |
| Code reasoning (cargo deps, semver pin) | kimi-direct | gpt-oss-120b stronger on tool-talk | minimax-direct |
| Summarize log file (<2000 lines) | freetier | Free, fast | kimi-direct |
| Generate test data | minimax-direct | Structured output | kimi-direct |
| Multi-file code generation | NONE (parent inline) | dispatch-worker is single-shot text-only | codex exec via Bash |
| File editing / git ops | NONE (parent inline) | dispatch-worker can't write files | codex exec via Bash |
| Long-form synthesis (>500 words) | minimax-direct or kimi-direct | better depth | parent inline |
| Critical decisions / architecture | parent inline | high judgment requires Claude | NONE |

## Anti-patterns
- ❌ Use dispatch-worker for "regenerate Cargo.lock" — fabricates output.
- ❌ Route tier `worker` or `main` (claude-routed) — FORBIDDEN per regime.
- ❌ Use Agent tool with subagent_type=general-purpose — defaults to Claude.
- ❌ Wait for dispatch-worker output before parent does next step (latency adds up).
- ❌ Dispatch >50 in parallel — saturates omniroute.

## Patterns
- ✅ Fire 5-15 dispatch workers, don't wait, do parent work in parallel.
- ✅ Use freetier for cheap volume; minimax for cheaper-but-better.
- ✅ Cap concurrent dispatch-worker at 30 (sustainable).
- ✅ Read worker output ONLY if you need it (most are research = decay-fast).
- ✅ Pre-flight check: `curl -sf http://localhost:20128/v1/models -o /dev/null` before mass dispatch.

## Dispatch-worker output reliability
- Plain text → 99% reliable
- Code blocks → 90% reliable (sometimes garbles)
- File paths / shell commands → 80% reliable (verify before executing)
- Hallucination rate → low for short outputs, rises with prompt length

## Cost (this session)
- ~1500 invocations
- Estimated <$1 total (most free)
- Sub-second median latency
