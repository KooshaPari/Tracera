"""FastMCP server wrapping dispatch-worker for agent tier-based delegation.

Exposes tools for routing prompts to cheap-tier agents (Kimi, Minimax, Codex-5, Codex-Mini, Opus).
Each tool shells out to dispatch-worker to invoke the corresponding tier.

Usage in Claude Code:
  Use via MCP tool `dispatch` with `tier` parameter.
  Example: dispatch(prompt="...", tier="kimi", cwd="/path/to/work")
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP

log = logging.getLogger("dispatch-mcp")

mcp = FastMCP("dispatch")


async def _run_dispatch_worker(
    tier: str, prompt: str, cwd: str | None = None
) -> dict:
    """Shell out to dispatch-worker with specified tier.

    Args:
        tier: Agent tier (kimi, minimax, codex_5, codex_mini, opus)
        prompt: The prompt to send to the agent
        cwd: Optional working directory for the dispatch

    Returns:
        Dict with response text, token usage, and metadata
    """
    cmd = ["dispatch-worker", "--tier", tier]

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            input=prompt.encode("utf-8"),
            capture_output=True,
            text=False,
            cwd=cwd or Path.home(),
            timeout=300,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            log.error(f"dispatch-worker failed: {stderr}")
            return {
                "error": f"dispatch-worker exited with code {result.returncode}",
                "stderr": stderr,
            }

        output = result.stdout.decode("utf-8", errors="replace")

        # Try to parse structured output (JSON if available)
        try:
            parsed = json.loads(output)
            return parsed
        except json.JSONDecodeError:
            # Fall back to raw text
            return {"text": output, "raw": True}

    except subprocess.TimeoutExpired:
        return {"error": "dispatch-worker timed out (300s)"}
    except FileNotFoundError:
        return {
            "error": "dispatch-worker not found in PATH. Install from repos/thegent/bin or ensure it is in your shell PATH."
        }
    except Exception as e:
        return {"error": f"dispatch-worker execution failed: {str(e)}"}


@mcp.tool(
    description=(
        "Dispatch a prompt to a cheap-tier agent (Kimi, Minimax, Codex-5, Codex-Mini) "
        "for bulk reasoning tasks: summarization, extraction, test generation, doc polishing. "
        "Shells out to dispatch-worker binary."
    )
)
async def dispatch(
    prompt: str,
    tier: Literal["kimi", "minimax", "codex_5", "codex_mini"] = "kimi",
    cwd: str | None = None,
) -> dict:
    """Dispatch a prompt to a cheap-tier agent.

    Args:
        prompt: The prompt text
        tier: Agent tier (kimi, minimax, codex_5, codex_mini). Default: kimi
        cwd: Optional working directory for the dispatch

    Returns:
        Response dict with text, tokens, or error details
    """
    log.info(f"dispatch.start", extra={"tier": tier, "prompt_len": len(prompt)})
    result = await _run_dispatch_worker(tier, prompt, cwd)
    log.info(f"dispatch.done", extra={"tier": tier})
    return result


@mcp.tool(
    description=(
        "Dispatch a prompt to Opus (high-tier reasoning agent). "
        "Use for complex analysis, design, architecture decisions where quality > cost."
    )
)
async def dispatch_opus(
    prompt: str,
    cwd: str | None = None,
) -> dict:
    """Dispatch to Opus tier."""
    log.info(f"dispatch.opus.start", extra={"prompt_len": len(prompt)})
    result = await _run_dispatch_worker("opus", prompt, cwd)
    log.info(f"dispatch.opus.done")
    return result


@mcp.tool(description="Health check: verify dispatch-worker is available and functional.")
async def dispatch_health() -> dict:
    """Check if dispatch-worker is available."""
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            ["dispatch-worker", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        available = result.returncode == 0
        return {
            "available": available,
            "message": "dispatch-worker is available" if available else "dispatch-worker failed health check",
        }
    except FileNotFoundError:
        return {
            "available": False,
            "message": "dispatch-worker not found in PATH",
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"dispatch-worker health check failed: {str(e)}",
        }


def main() -> None:
    """Entry point for dispatch-mcp server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    mcp.run()


if __name__ == "__main__":
    main()
