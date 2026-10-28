#!/usr/bin/env python3
"""Extract a structured digest from Codex rollout JSONL files.

Usage: extract_codex_digest.py <file.jsonl> [...]

Outputs, per file:
  - timeline of user messages (timestamp + text, truncated)
  - assistant final/reasoning text (truncated)
  - tool call inventory (name -> count)
  - shell commands (truncated)
  - file writes / patches (paths only)
"""

import json
import sys
from collections import Counter, defaultdict


def iter_records(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def text_of_content(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if not isinstance(item, dict):
            continue
        t = item.get("type")
        if (
            t == "input_text"
            or t == "output_text"
            or t == "text"
            or t == "summary_text"
        ):
            parts.append(item.get("text", ""))
    return "\n".join(p for p in parts if p)


def payload_text(payload):
    """Extract human-readable text from a rollout payload of any shape."""
    if not isinstance(payload, dict):
        return ""
    # event_msg style
    if payload.get("type") == "user_message":
        return payload.get("message", "") or ""
    if payload.get("type") == "agent_message":
        return payload.get("message", "") or ""
    if payload.get("type") == "agent_reasoning":
        return payload.get("text", "") or ""
    # response_item style
    if payload.get("type") == "message":
        role = payload.get("role", "")
        return f"[{role}] " + text_of_content(payload.get("content"))
    if payload.get("type") == "reasoning":
        return (
            "[reasoning] "
            + text_of_content(payload.get("content"))
            + text_of_content(payload.get("summary"))
        )
    return ""


def summarize(path, max_chars):
    users = []
    assistants = []
    tool_counts = Counter()
    tool_args = defaultdict(list)
    calls = []
    events = Counter()
    cwd = None
    model = None
    n = 0

    for rec in iter_records(path):
        n += 1
        rtype = rec.get("type")
        events[rtype] += 1
        payload = rec.get("payload") or {}
        if isinstance(payload, dict):
            if cwd is None:
                cwd = payload.get("cwd")
            model = payload.get("model") or model

        if rtype == "session_meta":
            cwd = payload.get("cwd", cwd)
            model = payload.get("model") or model

        # Function/tool calls
        if rtype == "response_item":
            ptype = payload.get("type")
            if ptype == "function_call":
                name = payload.get("name", "?")
                tool_counts[name] += 1
                try:
                    args = json.loads(payload.get("arguments") or "{}")
                except Exception:
                    args = {}
                tool_args[name].append(args)
                calls.append((rec.get("timestamp"), name, args))
            elif ptype == "local_shell_call" or ptype == "custom_tool_call":
                name = payload.get("name") or ptype
                tool_counts[ptype] += 1
        elif rtype == "event_msg":
            pt = payload.get("type")
            if pt == "exec_command_begin" or pt == "exec_command_end":
                tool_counts["shell"] += 1
            elif pt in ("task_started", "task_complete"):
                tool_counts[pt] += 1

        txt = payload_text(payload)
        if not txt:
            continue
        ts = rec.get("timestamp", "")
        if payload.get("type") == "user_message" or (
            rtype == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "user"
        ):
            users.append((ts, txt))
        elif payload.get("type") in ("agent_message", "agent_reasoning") or (
            rtype == "response_item"
            and payload.get("type") in ("message", "reasoning")
            and payload.get("role") != "user"
        ):
            assistants.append((ts, txt))

    out = []
    out.append("=" * 100)
    out.append(f"FILE: {path}")
    out.append(f"records={n} cwd={cwd} model={model}")
    out.append(f"event types: {dict(events)}")
    out.append(f"tool counts: {dict(tool_counts.most_common())}")
    out.append("=" * 100)

    out.append("\n\n########## USER MESSAGES ##########")
    for ts, t in users:
        t = t.strip()
        if not t:
            continue
        out.append(f"\n--- USER @ {ts} ---")
        out.append(t[:max_chars])

    out.append("\n\n########## ASSISTANT MESSAGES (non-reasoning first) ##########")
    for ts, t in assistants:
        t = t.strip()
        if not t or t.startswith("[reasoning]"):
            continue
        out.append(f"\n--- AGENT @ {ts} ---")
        out.append(t[:max_chars])

    out.append("\n\n########## SHELL COMMANDS ##########")
    for ts, name, args in calls:
        if name in ("shell", "local_shell", "exec_command") or "command" in args:
            cmd = args.get("command") or args.get("cmd") or ""
            if cmd:
                out.append(f"\n$ [{ts}] {cmd[:1200]}")

    out.append("\n\n########## FILE WRITES / PATCHES ##########")
    seen = set()
    for _ts, name, args in calls:
        path = args.get("path") or args.get("file") or args.get("file_path")
        if path and path not in seen:
            seen.add(path)
            out.append(f"  [{name}] {path}")

    return "\n".join(out)


if __name__ == "__main__":
    max_chars = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    for p in sys.argv[2:]:
        print(summarize(p, max_chars))
