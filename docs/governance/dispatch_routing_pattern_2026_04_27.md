# Dispatch-Worker Routing Pattern R&D

**Date:** 2026-04-27
**Status:** Proposed
**Author:** Forge

## Recommendation

**Rule-based routing with explicit per-task tier override is the optimal pattern.**

Smart routing wastes a cheap-LLM call per dispatch (defeats cost-saving purpose). Round-robin ignores task fit, reducing quality. Hybrid combines the best of both.

---

## Routing Config (`routing.toml`)

```toml
# Default tier mapping by task type
[rules]
investigate = "minimax"
mechanical_edit = "minimax"
code_refactor = "codex-mini"
architecture = "opus"
test_gen = "kimi"
memory_codify = "minimax"
file_edit = "minimax"
read_research = "minimax"
simple_rewrite = "minimax"
complex_reasoning = "opus"
security_review = "opus"
api_design = "codex-mini"
migration = "codex-mini"

# Override for specific patterns (regex → tier)
[overrides]
"auth.*security" = "opus"
"design.*system" = "opus"
"refactor.*core" = "codex-mini"
"test.*critical" = "kimi"
```

---

## Trade-offs

| Pattern | Cost | Quality | Latency | Complexity |
|---------|------|---------|---------|------------|
| Rule-based | Low | High | Fast | Low |
| Smart (LLM) | High* | Variable | Slow | Medium |
| Round-robin | Low | Low | Fast | Low |
| Hybrid | Low | High | Fast | Medium |

**Smart routing** requires a cheap-LLM call per dispatch to classify the task—wasting the cost savings of using cheap workers in the first place. Self-defeating.

**Round-robin** spreads load but ignores task complexity, causing under-powered workers to struggle with architecture tasks or over-powered workers to waste resources on mechanical edits.

**Rule-based** achieves fast dispatch, high quality via task-tier matching, and low complexity. Override table handles edge cases without polluting defaults.

**Hybrid** (rule-based default + LLM override for unknown patterns) is viable if the LLM call is cached or infrequent. Default to rules; escalate to smart only for unrecognized task types.

---

## Implementation Notes

- Shell script reads `routing.toml` at startup, caches in memory
- Task type extracted from agent prompt metadata (`--task-type=investigate`)
- Override table checked before default rules (allows fast-path for known patterns)
- Metrics: track task-type distribution to refine rules over time
