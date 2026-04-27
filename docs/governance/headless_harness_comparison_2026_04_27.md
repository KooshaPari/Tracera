# Headless Agent Harness Comparison

**Date:** 2026-04-27
**Scope:** Phenotype org — worker harness for autonomous pipeline tasks

---

## Harness Inventory

| Harness | Version | Provider | Status |
|---------|---------|----------|--------|
| Forge | 2.12.9 | MiniMax | Available |
| Codex | 0.125.0 | OpenAI | Available |
| Claude Code | 2.1.119 | Anthropic | Available |
| Droid | — | thegent | **Not installed** (launcher wrapper present; target binary absent) |
| Aider | — | — | Not installed |
| Continue | — | — | Not installed |

---

## Comparison Matrix

| Criterion | Forge | Codex | Claude Code |
|-----------|-------|-------|-------------|
| **Idle memory** | ~40–80 MB (Rust binary) | ~80–150 MB (Node/Electron) | ~60–120 MB |
| **Memory @ 5+ concurrent** | Low (stateless per invoke) | Medium (session-per-invoke overhead) | Medium (session overhead) |
| **JSONL / structured output** | `forge data` (batch JSONL processor, `--input` + `--schema`) — not per-invocation stdout | `--json` streams events as JSONL; `--output-schema FILE` validates final response | `--output-format json\|stream-json` + `--json-schema SCHEMA` for validation |
| **Subagent spawning** | None (MCP tool-only; no native spawn) | None (but `codex mcp-server` exposes as MCP tool — can compose) | `--agents <json>` defines named agents; `claude agents` manages background agents; teammate mode via `teammateMode: auto` in settings |
| **Background / bash-friendly** | Yes — `forge -p '...'` works with `&`, `|`, redirections | Yes — `codex exec ... &`; also `codex exec-server --listen ws://` for persistent WS background (see `codex-responses-ws-check.out`) | Yes — `claude -p ... &`; `claude agents` for managed background sessions |
| **Per-invocation model override** | No `--model` flag; selects agent at invoke time via `--agent forge\|muse\|sage` | Yes: `-m, --model MODEL` | Yes: `--model MODEL` |
| **Cost per call** | Minimax (~$0.001–0.01/1K tok via MiniMax-M2.7-highspeed) | OpenAI (o3: ~$3–15/1M output tok; gpt-4o: ~$2.5/1M output) | Anthropic (opus: ~$15/1M output; sonnet: ~$3/1M output) |
| **Feature parity vs Claude Code** | ~40% (no structured output, no subagents, no model override) | ~75% (JSONL, model override, WS background, MCP server) | **100% baseline** |

---

## Droid Status

`droid` is a thegent launcher wrapper (`~/.local/bin/droid`) that attempts to exec a uv-installed `thegent` binary. The target at `~/.local/share/uv/tools/thegent/bin/droid` does not exist — uv tool is not installed on this machine. **Droid is non-functional** in the current environment.

---

## Recommendation

### Primary Worker Harness: Claude Code
- Richest structured output (`--output-format json`, `--json-schema`, `--input-format stream-json`) for pipeline integration
- Subagent support via `--agents` and background agent management
- `--model` per-invocation override works reliably
- `--bare` mode minimizes overhead for headless pipelines
- Teammate mode available for orchestrated multi-agent workloads
- **Gap vs Claude Code baseline:** none — Claude Code is the baseline

### Fallback / Specialty Harness: Codex
- `--json` for per-event JSONL streaming
- `--output-schema` for final-response validation
- `codex exec-server --listen ws://127.0.0.1:0` provides a persistent WebSocket endpoint — background-friendly for long-running orchestration (user note: check `codex-responses-ws-check.out` for WS status)
- `--model` per-invocation works
- `--oss` flag available for open-source model routing
- **Use when:** OpenAI cost model preferred, or when Codex-specific tooling (sandbox policies, plugin system) is needed

### Forge: Specialty Only
- `forge data` is purpose-built for batch JSONL processing with schema-constrained LLM tool calls
- Use for bulk structured transformation pipelines, not as a general agent harness
- No `--model` override, no structured stdout — unsuitable as primary worker

---

## Gaps vs Claude Code Feature Parity

| Gap | Severity | Forge | Codex |
|-----|----------|-------|-------|
| No `--model` override | P1 | Yes | No |
| No structured JSON output | P1 | Yes | No |
| No subagent/agent composition | P2 | Yes | Partial (via MCP) |
| No `--json-schema` validation | P2 | Yes | Yes (via `--output-schema`) |
| No `--output-format stream-json` | P2 | Yes | Partial (via `--json`) |
| No `--bare` minimal mode | P3 | Yes | Partial (via `--ignore-user-config --ignore-rules`) |
| No background session management | P3 | Yes | Partial (via `exec-server` WS) |
| No teammate mode | P3 | Yes | No |

**Bottom line:** Claude Code is the clear primary choice for Phenotype's headless pipeline harness. Codex is the recommended fallback where OpenAI routing or sandbox isolation is required. Forge covers only the batch-JSONL niche.
