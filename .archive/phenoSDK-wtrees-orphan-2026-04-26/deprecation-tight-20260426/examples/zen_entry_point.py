#!/usr/bin/env python3
"""
Zen MCP Server Entry Point Example
==================================

Example of how to create a simplified entry point for the Zen MCP server
using the universal project framework.
"""

import sys
from pathlib import Path

# Add pheno-sdk to path
pheno_sdk_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(pheno_sdk_path))

from pheno.shared.project_framework import create_mcp_server


def create_zen_entry_point():
    """
    Create the Zen MCP server entry point.
    """

    # Create the project builder
    builder = (
        create_mcp_server("zen-mcp", port=8000)
        .description("Zen MCP Server - Unified CLI")
        .version("1.0.0")
        .domain("zen.kooshapari.com")
        .command("python -m zen_mcp_server.server")
        .working_directory(".")
        .environment(
            ZEN_PROVIDER_PRIORITY="OPENROUTER",
            EMBEDDINGS_PROVIDER="ollama",
            OLLAMA_EMBED_MODEL="nomic-embed-text",
        )
        .health_check("/health")
        .timeouts(60, 15)
        .custom("default_port", 8000)
        .custom("project_type", "zen")
    )

    # Add custom command handlers if needed
    def custom_start_handler(args):
        """
        Custom start handler for Zen.
        """
        print(f"🚀 Starting Zen MCP Server on port {args.port or 8000}")
        # Call the original start logic
        return builder.build_cli()._start_server(args)

    def custom_validate_handler(args):
        """
        Custom validation handler for Zen.
        """
        print("🔍 Validating Zen MCP Server configuration...")
        # Add Zen-specific validation logic here
        try:
            import fastmcp

            print("✅ FastMCP is available")
        except ImportError as e:
            print(f"❌ FastMCP is not available: {e}")
            return 1

        print("✅ Configuration validation passed")
        return 0

    # Apply custom handlers
    builder.cli_handler("start", custom_start_handler)
    builder.cli_handler("validate", custom_validate_handler)

    # Build and return the entry point
    return builder.build_entry_point()


# Create the entry point function
main = create_zen_entry_point()

if __name__ == "__main__":
    sys.exit(main())
