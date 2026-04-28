# Agent Stream / Stream-JSON Specification

**Default:** thegent uses stream-json for all agents and droids by default. It sets `THGENT_OUTPUT_FORMAT=stream-json` for each agent runner and passes `--output-format stream-json` to `droid exec`. Wrappers emit JSONL (one JSON object per line); thegent extracts the last assistant message.

Use `--full` to get raw text output instead (no stream-json, no parsing).

## Expected JSONL Format

Each line is a JSON object. Thegent extracts the last line with:

- `type` = `"message"` and `role` = `"assistant"`, or
- `content` present (fallback)

```json
{"type":"message","role":"assistant","content":"Final response text here."}
```

## Per-Agent Output Format Flags

| Agent | Stream-JSON Flag | Fallback (plain text) |
|-------|------------------|------------------------|
| **gemini** | `--output-format stream-json` | `--output-format text` |
| **codex** | `--json` (JSONL) | default |
| **copilot** | `--stream on` | default |
| **cursor** | `--print` (plain stream) | default |
| **claude** | `--output-format stream-json` | `--output-format text` |
| **droid** | `--output-format stream-json` | `--output-format text` (default) |

**Note:** Droids run via `droid exec` (DroidRunner), not a separate agent dispatcher. Thegent passes `--output-format stream-json` by default; `--full` omits it.

## Agent Runner Output Wiring

When `THGENT_OUTPUT_FORMAT=stream-json`, thegent applies per-agent output flags before launching each runner:

```bash
OUTPUT_FMT=""
if [ "${THGENT_OUTPUT_FORMAT}" = "stream-json" ]; then
  case "$AGENT" in
    gemini)  OUTPUT_FMT="--output-format stream-json" ;;
    codex)   OUTPUT_FMT="--json" ;;
    copilot) OUTPUT_FMT="--stream on" ;;
    cursor)  OUTPUT_FMT="--print" ;;
    claude)  OUTPUT_FMT="--output-format stream-json" ;;
    *)       OUTPUT_FMT="" ;;
  esac
fi

# Pass OUTPUT_FMT into the selected runner command.
# The caller chooses the actual command per AGENT; this remains the canonical
# contract thegent enforces internally.
cmd=(thegent run "$AGENT" --cd "$CD" "$PROMPT")
if [ -n "$OUTPUT_FMT" ]; then
  cmd+=("$OUTPUT_FMT")
fi
```

## Droid (DroidRunner)

Droids are invoked directly by thegent via `droid exec -f <file>`. Parity with agents:

- **Output:** Default `--output-format stream-json`; `--full` omits (raw text)
- **Mode:** `--mode read-only` = droid default; `write` → `--auto low`; `full` → `--auto high`
- **stdin:** DEVNULL (non-interactive)
- **No run_agent.sh** — thegent calls droid exec directly

## Wrapper Script Locations

- `~/.factory/skills/agent-orchestra` (agent orchestrator registry and execution policy)
- `~/.factory/skills/gemini-agent/scripts/run_gemini.sh` (if maintained)
- `~/.factory/skills/codex-agent/scripts/run_codex.sh` (or codex-subagent)
- `~/.factory/skills/copilot-agent/scripts/run_copilot.sh`
- `~/.factory/skills/cursor-agent/scripts/run_cursor.sh`
- `~/.factory/skills/claude-agent/scripts/run_claude.sh` (if present)

## Plain-Text Fallback

Only when JSONL parsing fails (e.g. malformed output), thegent falls back to plain-text heuristics: strips trailing noise and extracts the last meaningful block. With well-maintained CLIs this should not occur.

## Cursor Headless Fix

For `cursor agent` to return output in headless mode, add `--trust` (skips workspace approval) and `--workspace <path>` when workspace is set. See `../thegent/factory-seed/cursor-agent/scripts/run_cursor_headless_fix.sh`.
