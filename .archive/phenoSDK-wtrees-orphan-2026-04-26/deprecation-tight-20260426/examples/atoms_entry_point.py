#!/usr/bin/env python3
"""
Atoms MCP Server Entry Point Example
====================================

Example of how to create a simplified entry point for the Atoms MCP server
using the universal project framework.
"""

import sys
from pathlib import Path

# Add pheno-sdk to path
pheno_sdk_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(pheno_sdk_path))

from pheno.shared.project_framework import create_mcp_server


def create_atoms_entry_point():
    """
    Create the Atoms MCP server entry point.
    """

    # Create the project builder
    builder = (
        create_mcp_server("atoms-mcp", port=50002)
        .description("Atoms MCP - Unified CLI for all operations")
        .version("1.0.0")
        .domain("atomcp.kooshapari.com")
        .command("python -m atoms_mcp_old.atoms-mcp start")
        .working_directory(".")
        .environment(
            ATOMS_VERBOSE="1",
            PYTHONPATH=":".join(
                [
                    str(Path(__file__).parent.parent / "KInfra" / "libraries" / "python"),
                    str(Path(__file__).parent.parent / "mcp-QA"),
                ],
            ),
        )
        .health_check("/health")
        .timeouts(30, 10)
        .custom("default_port", 50002)
        .custom("project_type", "atoms")
    )

    # Add custom command handlers if needed
    def custom_start_handler(args):
        """
        Custom start handler for Atoms.
        """
        print(f"🚀 Starting Atoms MCP Server on port {args.port or 50002}")
        # Call the original start logic
        return builder.build_cli()._start_server(args)

    # Apply custom handlers
    builder.cli_handler("start", custom_start_handler)

    # Build and return the entry point
    return builder.build_entry_point()


# Create the entry point function
main = create_atoms_entry_point()

if __name__ == "__main__":
    sys.exit(main())
