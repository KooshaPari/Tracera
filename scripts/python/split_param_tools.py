#!/usr/bin/env python3
"""Script to extract tool function ranges from param.py for splitting.

Outputs line ranges for each tool to help with manual extraction.
"""

import re
from pathlib import Path

# Read param.py
param_file = Path(__file__).parent.parent / "src/tracertm/mcp/tools/param.py"
content = param_file.read_text()
lines = content.split("\n")

# Find all @mcp.tool decorators and their line numbers
tool_starts = []
for i, line in enumerate(lines, 1):
    if line.strip().startswith("@mcp.tool"):
        # Get function name from next line
        func_line = lines[i] if i < len(lines) else ""
        match = re.search(r"async def (\w+)\(", func_line)
        if match:
            tool_starts.append((i, match.group(1)))

# Create line ranges
tools_info = []
for idx, (line_no, name) in enumerate(tool_starts):
    if idx + 1 < len(tool_starts):
        next_line = tool_starts[idx + 1][0]
        end_line = next_line - 1
    else:
        end_line = len(lines)

    tools_info.append({"name": name, "start": line_no, "end": end_line, "lines": end_line - line_no + 1})

# Print report

for _tool in tools_info:
    pass


# Group tools by domain for output modules
domain_groups = {
    "storage": ["sync_manage", "backup_manage", "watch_manage"],
    "io_operations": ["export_manage", "import_manage", "ingest_manage"],
    "database": ["db_manage"],
    "agent": ["agents_manage", "progress_manage"],
    "query_test": ["saved_query_manage", "test_manage"],
    "ui": ["tui_manage", "design_manage"],
    "system": ["benchmark_manage", "chaos_manage"],
}

for tool_names in domain_groups.values():
    total_lines = sum(t["lines"] for t in tools_info if t["name"] in tool_names)
    for name in tool_names:
        tool = next((t for t in tools_info if t["name"] == name), None)
        if tool:
            pass
