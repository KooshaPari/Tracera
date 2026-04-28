#!/usr/bin/env python3
"""dispatch-mcp — MCP server wrapping OmniRoute single-endpoint dispatch.

Primary delegation tool. Falls back to Skill({skill: "dispatch"}) or the
`dispatch-worker` CLI if this server is unavailable.

Tools exposed:
  - dispatch_worker(prompt, cwd?, max_tokens?)        → "Worker" profile
  - dispatch_main(prompt, cwd?, max_tokens?)          → "Main" profile
  - dispatch_codeman(prompt, cwd?, max_tokens?)       → "Codeman" profile
  - dispatch_freetier(prompt, cwd?, max_tokens?)      → "FreeTier" profile
  - dispatch_kimi(prompt, cwd?, max_tokens?)          → kmc/kimi-k2.5
  - dispatch_kimi_thinking(prompt, cwd?, max_tokens?) → kmc/kimi-k2.5-thinking
  - dispatch_minimax(prompt, cwd?, max_tokens?)       → minimax/minimax-m2.7-highspeed
  - dispatch_opus(prompt, cwd?, max_tokens?)          → cc/claude-opus-4-6  (synthesis-critical only)
  - dispatch_haiku(prompt, cwd?, max_tokens?)         → cc/claude-haiku-4-5-20251001
  - dispatch_gemini(prompt, cwd?, max_tokens?)        → gemini/gemini-3.1-pro-high
  - dispatch_custom(prompt, model, cwd?, max_tokens?) → any OmniRoute model ID
  - dispatch_health()                                 → check OmniRoute reachability
"""
import json
import os
import sys
import urllib.request
import urllib.error

OMNIROUTE_URL = os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1")

# Try to import FastMCP. If unavailable, fall back to printing usage.
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("dispatch-mcp: install fastmcp first: pip install mcp", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("dispatch")


def _call_omniroute(model: str, prompt: str, cwd: str | None = None, max_tokens: int = 4096) -> str:
    """POST to OmniRoute /v1/chat/completions and return assistant content."""
    system = "You are a Phenotype-org headless worker."
    if cwd:
        system += f" Project working directory (context only): {cwd}."

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }

    req = urllib.request.Request(
        f"{OMNIROUTE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OmniRoute HTTP {e.code}: {body[:500]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"OmniRoute unreachable: {e.reason}. Is omniroute up on {OMNIROUTE_URL}?")

    if "error" in data:
        raise RuntimeError(f"OmniRoute error: {json.dumps(data['error'])}")

    try:
        content = data["choices"][0]["message"]["content"]
        routed_model = data.get("model", "?")
        return f"{content}\n\n--- routed to: {routed_model} ---"
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"unexpected response shape: {json.dumps(data)[:500]}")


def _make_dispatch(model_id: str):
    """Factory: build a dispatch_<tier> tool for a given backing model ID."""
    def _tool(prompt: str, cwd: str | None = None, max_tokens: int = 4096) -> str:
        return _call_omniroute(model_id, prompt, cwd=cwd, max_tokens=max_tokens)
    return _tool


# Profile tiers
mcp.tool(name="dispatch_worker", description="Cheap volume worker tier (OmniRoute Worker profile).")(_make_dispatch("Worker"))
mcp.tool(name="dispatch_main", description="Balanced tier (OmniRoute Main profile).")(_make_dispatch("Main"))
mcp.tool(name="dispatch_codeman", description="Code-execution tier (OmniRoute Codeman profile).")(_make_dispatch("Codeman"))
mcp.tool(name="dispatch_freetier", description="Free models only (OmniRoute FreeTier profile).")(_make_dispatch("FreeTier"))

# Direct-model tiers
mcp.tool(name="dispatch_kimi", description="Kimi K2.5 direct.")(_make_dispatch("kmc/kimi-k2.5"))
mcp.tool(name="dispatch_kimi_thinking", description="Kimi K2.5 with reasoning.")(_make_dispatch("kmc/kimi-k2.5-thinking"))
mcp.tool(name="dispatch_minimax", description="MiniMax M2.7 highspeed direct.")(_make_dispatch("minimax/minimax-m2.7-highspeed"))
mcp.tool(name="dispatch_opus", description="Claude Opus 4.6 — SYNTHESIS-CRITICAL ONLY.")(_make_dispatch("cc/claude-opus-4-6"))
mcp.tool(name="dispatch_haiku", description="Claude Haiku 4.5.")(_make_dispatch("cc/claude-haiku-4-5-20251001"))
mcp.tool(name="dispatch_gemini", description="Gemini 3.1 Pro high.")(_make_dispatch("gemini/gemini-3.1-pro-high"))


@mcp.tool(name="dispatch_custom", description="Dispatch to any OmniRoute model ID directly.")
def dispatch_custom(prompt: str, model: str, cwd: str | None = None, max_tokens: int = 4096) -> str:
    return _call_omniroute(model, prompt, cwd=cwd, max_tokens=max_tokens)


@mcp.tool(name="dispatch_health", description="Check OmniRoute reachability.")
def dispatch_health() -> str:
    try:
        with urllib.request.urlopen(f"{OMNIROUTE_URL}/models", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            count = len(data.get("data", []))
            return f"OK: OmniRoute reachable at {OMNIROUTE_URL}, {count} models exposed."
    except Exception as e:
        return f"DOWN: {OMNIROUTE_URL} unreachable ({e}). Try: nohup omniroute --no-open > /tmp/omniroute.log 2>&1 &"


if __name__ == "__main__":
    mcp.run()
