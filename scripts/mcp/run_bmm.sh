#!/bin/bash
# BMM CLI Wrapper - Uses current Python environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Use current Python (respects conda/venv activation)
PYTHON_CMD="python"

# Run CLI with all arguments
exec $PYTHON_CMD "$SCRIPT_DIR/bmm_cli.py" "$@"

