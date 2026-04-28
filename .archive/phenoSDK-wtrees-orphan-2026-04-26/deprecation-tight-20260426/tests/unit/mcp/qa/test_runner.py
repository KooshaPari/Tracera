"""
Test Runner - Redirect to Base Test Runner

DEPRECATED: This module is deprecated and will be removed in a future version.
Please import from pheno.mcp.qa.core.base.test_runner instead.

The TestRunner class has been refactored into BaseTestRunner with better
extensibility for project-specific implementations.

Migration Guide:
    OLD: from pheno.mcp.qa.core.test_runner import TestRunner
    NEW: from pheno.mcp.qa.core.base.test_runner import BaseTestRunner

    Or use the main package export:
    from pheno.mcp.qa import BaseTestRunner  # Recommended
    from pheno.mcp.qa import TestRunner      # Legacy alias (still works)

For new code, extend BaseTestRunner:
    class MyTestRunner(BaseTestRunner):
        def _get_metadata(self):
            return {"project": "my-project"}

        def _get_category_order(self):
            return ["core", "integration"]
"""

import warnings

from pheno.mcp.qa.core.base.test_runner import BaseTestRunner

# Provide legacy alias
TestRunner = BaseTestRunner

# Issue deprecation warning
warnings.warn(
    "mcp_qa.core.test_runner is deprecated. "
    "Please import BaseTestRunner from pheno.mcp.qa.core.base.test_runner instead. "
    "Example: from pheno.mcp.qa import BaseTestRunner",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["BaseTestRunner", "TestRunner"]
