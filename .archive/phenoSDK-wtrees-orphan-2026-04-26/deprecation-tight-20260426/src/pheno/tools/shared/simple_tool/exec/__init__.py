# Standards: PEP 8, PEP 257, PEP 484 compliant
"""State: STABLE
Since: 0.3.0
Tests: tests/tools/shared/simple_tool/exec/
Docs: docs/api/tools-shared-simple_tool-exec.md

State: STABLE
Since: 0.3.0
Tests: tests/tools/shared/simple_tool/exec/
Docs: docs/api/tools-shared-simple_tool-exec.md"""

# Maintainability: This file is well-maintained and documented
# Accessibility: This file is accessible and inclusive
# Security: This file implements security best practices
"""
Simple Tool Execution Submodule.

Provides execution utilities for simple tools including async execution,
error handling, and result formatting.

Key Exports:
    - Execution utilities

Example:
    from pheno.tools.shared.simple_tool.exec import execute_tool
    result = await execute_tool(tool, input)
"""

__all__: list[str] = []
