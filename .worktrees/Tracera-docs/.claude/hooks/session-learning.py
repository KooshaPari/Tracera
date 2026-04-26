#!/usr/bin/env python3
"""Session Learning Hook - Captures learnings for future sessions.

Trigger: SessionEnd event
Pattern: Evolver-style retrospective with ACE compression.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def extract_learnings(session_data: Any) -> None:
    """Extract structured learnings from session."""
    # Parse session data
    messages = session_data.get("messages", [])
    tools_used = session_data.get("tools_used", [])
    errors = session_data.get("errors", [])

    # Detect patterns
    phase_completions = [m for m in messages if "phase" in m.lower() and "complete" in m.lower()]
    blockers_resolved = [
        m for m in messages if "blocker" in m.lower() and ("resolved" in m.lower() or "fixed" in m.lower())
    ]
    patterns_found = [m for m in messages if "pattern" in m.lower() or "anti-pattern" in m.lower()]

    return {
        "phases": phase_completions,
        "blockers": blockers_resolved,
        "patterns": patterns_found,
        "tools": tools_used,
        "errors": errors,
    }


def format_retrospective(learnings: Any, topic: Any) -> None:
    """Format as structured retrospective."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

    retro = f"""# Session Learning: {topic}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## ✅ What Worked
"""

    for phase in learnings["phases"]:
        retro += f"- Phase completion: {phase}\n"

    retro += "\n## ❌ What Failed\n"
    for error in learnings["errors"]:
        retro += f"- Error: {error}\n"

    retro += "\n## 📝 Key Patterns Discovered\n"
    for pattern in learnings["patterns"]:
        retro += f"- {pattern}\n"

    retro += "\n## 🔧 Tools Used Effectively\n"
    for tool in learnings["tools"]:
        retro += f"- {tool}\n"

    return retro, timestamp


def update_memory_files(retro: Any, timestamp: Any, topic: Any) -> None:
    """Update memory files with learnings."""
    memory_dir = Path.home() / ".claude" / "projects" / "-Users-kooshapari-temp-PRODVERCEL-485-kush-trace" / "memory"

    # Save full retrospective
    retro_file = memory_dir / f"retrospectives/{topic}-{timestamp}.md"
    retro_file.parent.mkdir(parents=True, exist_ok=True)
    retro_file.write_text(retro)

    # Update failures.md with anti-patterns
    failures_file = memory_dir / "failures.md"
    content = failures_file.read_text() if failures_file.exists() else "# Failures & Anti-Patterns\n\n"

    # Extract failures section from retro
    if "## ❌ What Failed" in retro:
        failures = retro.split("## ❌ What Failed")[1].split("##")[0]
        content += f"\n## {timestamp} - {topic}\n{failures}"
        failures_file.write_text(content)


def main() -> None:
    """SessionEnd hook entry point."""
    try:
        # Read session data from stdin
        session_data = json.load(sys.stdin)

        # Detect topic from session
        topic = session_data.get("topic", "general")

        # Extract learnings
        learnings = extract_learnings(session_data)

        # Format retrospective
        retro, timestamp = format_retrospective(learnings, topic)

        # Update memory files
        update_memory_files(retro, timestamp, topic)

        # Output summary to user

        sys.exit(0)

    except Exception:
        sys.exit(0)  # Don't block session end on error


if __name__ == "__main__":
    main()
