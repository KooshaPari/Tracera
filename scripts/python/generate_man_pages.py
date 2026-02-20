#!/usr/bin/env python3
"""Generate man pages for TraceRTM commands (Story 3.5, FR29, FR30).

Usage:
    python scripts/generate_man_pages.py [output_dir]
"""

import sys
from pathlib import Path

from tracertm.cli.help_system import HELP_TOPICS, generate_man_page


def main() -> None:
    """Generate man pages for all commands."""
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("man/man1")
    output_dir.mkdir(parents=True, exist_ok=True)

    for topic in HELP_TOPICS:
        man_page = generate_man_page(topic)
        output_file = output_dir / f"rtm-{topic}.1"
        output_file.write_text(man_page)

    # Generate main rtm.1 man page
    main_man = """
.TH RTM 1 "TraceRTM" "User Commands"
.SH NAME
rtm \\- Agent-native, multi-view requirements traceability system
.SH SYNOPSIS
.B rtm
[OPTIONS] COMMAND [ARGS]...
.SH DESCRIPTION
TraceRTM is an agent-native, multi-view requirements traceability system
designed for managing complex software projects with AI agent coordination.
.SH COMMANDS
See individual man pages for detailed command documentation:
.IP rtm-item(1)
Item management commands
.IP rtm-project(1)
Project management commands
.IP rtm-link(1)
Link management commands
.IP rtm-config(1)
Configuration management commands
.IP rtm-agents(1)
Agent management commands
.SH OPTIONS
.TP
.B --version, -v
Show version and exit
.TP
.B --help, -h
Show help message
.TP
.B --debug
Enable debug mode with full stack traces
.SH EXAMPLES
.TP
Create an item:
rtm item create "User Authentication" --view FEATURE --type feature
.TP
Switch projects:
rtm project switch my-project
.TP
Visualize links:
rtm link graph item-1 --depth 2
.TP
Bulk create from CSV:
rtm item bulk-create --input items.csv
.SH SEE ALSO
rtm-item(1), rtm-project(1), rtm-link(1), rtm-config(1), rtm-agents(1)
.SH AUTHOR
TraceRTM Development Team
"""
    (output_dir / "rtm.1").write_text(main_man)


if __name__ == "__main__":
    main()
