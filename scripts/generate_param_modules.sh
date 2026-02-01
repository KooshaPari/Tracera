#!/bin/bash
# Generate param modules from param.py

PARAM_FILE="src/tracertm/mcp/tools/param.py"
OUT_DIR="src/tracertm/mcp/tools/params"

# Function to extract and wrap tool function
extract_tool() {
    local name=$1
    local start=$2
    local end=$3
    local output=$4
    local imports=$5

    # Extract function
    sed -n "${start},${end}p" "$PARAM_FILE" > "/tmp/tool_${name}.txt"

    # Create module with imports and extracted code
    cat > "$output" << 'HEADER'
"""Auto-generated MCP tool module."""

from __future__ import annotations

import gzip
import json
import yaml
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover
    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn
            return decorator
    mcp = _StubMCP()  # type: ignore[assignment]

HEADER

    # Add domain-specific imports
    echo "$imports" >> "$output"
    echo "" >> "$output"
    echo "from .common import _wrap, _maybe_select_project, _get_async_session" >> "$output"
    echo "" >> "$output"
    echo "" >> "$output"

    # Append extracted code
    cat "/tmp/tool_${name}.txt" >> "$output"

    echo "Generated: $output"
}

echo "Generating remaining param modules..."

# The modules we already created manually:
# - project.py (223-258)
# - item.py (259-343)
# - link.py (344-382)
# - trace.py (383-529)
# - graph.py (430-454)
# - specification.py (455-519)
# - config.py (530-586)
# - storage.py (587-947)

# Generate remaining modules:
# Note: Some are already created, script for future reference
