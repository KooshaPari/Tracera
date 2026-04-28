#!/usr/bin/env python3
"""
Complete Application Example
============================

Demonstrates integration of enhanced pheno-sdk kits:
- tui_kit - Beautiful terminal interfaces
- cli-builder-kit - TUI-enhanced CLIs
- config-kit - Interactive configuration
- deploy-kit - TUI deployment orchestration

This example shows how to build a complete CLI application with
configuration, deployment, and beautiful terminal output.
"""

import asyncio

# CLI Builder Kit - for TUI-enhanced CLIs
from cli_builder.tui_integration import create_tui_cli

# Deploy Kit - for TUI deployment
from pheno.deployment.tui_orchestrator import (
    DeploymentStage,
    create_deployment_orchestrator,
)

# TUI Kit - for beautiful terminal output
from pheno_sdk.tui_kit import (
    get_theme,
    render_progress,
    render_status,
)

# Config - interactive configuration (removed from pheno.config; use manual prompts or CLI builder)


class AtomsFastMCPApp:
    """
    Example application: Atoms FastMCP Server CLI

    Demonstrates complete integration of enhanced SDK components.
    """

    def __init__(self):
        """
        Initialize the application.
        """
        self.context = "atoms"
        self.theme = get_theme(self.context)
        self.config = {}

        # Create CLI with TUI support
        self.cli = create_tui_cli(
            name="atoms",
            context=self.context,
            description="Atoms FastMCP Server - Production Ready",
            version="1.0.0",
        )

        # Register commands
        self._register_commands()

    def _register_commands(self):
        """
        Register CLI commands.
        """
        # Setup command
        self.cli.add_command(
            "setup", self.cmd_setup, description="Interactive setup wizard", use_monitor=None,
        )

        # Deploy command
        self.cli.add_command(
            "deploy", self.cmd_deploy, description="Deploy to production", use_monitor="deployment",
        )

        # Status command
        self.cli.add_command(
            "status", self.cmd_status, description="Check application status", use_monitor="status",
        )

        # Test command
        self.cli.add_command(
            "test", self.cmd_test, description="Run test suite", use_monitor="test",
        )

    def cmd_setup(self) -> None:
        """Setup command - interactive configuration."""
        render_status("info", "Starting Atoms setup wizard...", context=self.context)

        # Create configuration wizard
        wizard = create_config_wizard(
            name="Atoms FastMCP",
            context=self.context,
            fields=[
                {
                    "name": "environment",
                    "description": "Deployment environment",
                    "default": "production",
                    "choices": ["development", "staging", "production"],
                },
                {
                    "name": "vercel_project",
                    "description": "Vercel project name",
                    "default": "atoms-fastmcp",
                },
                {"name": "port", "description": "Server port", "default": 8000},
                {"name": "api_key", "description": "API key for external services", "secret": True},
                {
                    "name": "enable_monitoring",
                    "description": "Enable monitoring",
                    "default": "yes",
                    "choices": ["yes", "no"],
                },
            ],
        )

        # Run wizard
        self.config = wizard.run_wizard()

        # Validate and save
        if wizard.validate_config():
            wizard.save_config()
            render_status("success", "Configuration complete!", context=self.context)
        else:
            render_status("error", "Configuration validation failed", context=self.context)

    def cmd_deploy(self, monitor=None, target: str = "vercel") -> None:
        """Deploy command - orchestrated deployment with TUI."""
        render_status("info", f"Deploying Atoms to {target}...", context=self.context)

        # Create deployment orchestrator
        orchestrator = create_deployment_orchestrator(
            context=self.context,
            targets=[
                {
                    "name": "vercel",
                    "type": "vercel",
                    "config": {
                        "project": self.config.get("vercel_project", "atoms-fastmcp"),
                        "environment": self.config.get("environment", "production"),
                    },
                },
            ],
        )

        # Register stage handlers
        orchestrator.register_stage_handler(DeploymentStage.VALIDATE, self._validate_stage)
        orchestrator.register_stage_handler(DeploymentStage.BUILD, self._build_stage)
        orchestrator.register_stage_handler(DeploymentStage.TEST, self._test_stage)
        orchestrator.register_stage_handler(DeploymentStage.DEPLOY, self._deploy_stage)
        orchestrator.register_stage_handler(DeploymentStage.VERIFY, self._verify_stage)

        # Execute deployment
        result = asyncio.run(orchestrator.deploy(target))

        if result:
            render_status("success", "Deployment successful!", context=self.context)
        else:
            render_status("error", "Deployment failed!", context=self.context)

    def cmd_status(self, monitor=None) -> None:
        """Status command - check application status."""
        if monitor:
            monitor.update(status="running", message="Checking status...")

        render_progress(30, 100, "Checking API...", context=self.context)
        # Simulate checking API
        api_status = "healthy"

        render_progress(60, 100, "Checking database...", context=self.context)
        # Simulate checking database
        db_status = "connected"

        render_progress(100, 100, "Status check complete", context=self.context)

        # Display results
        print(f"\n{self.theme.icon} Atoms Status:")
        print(f"  API: {api_status}")
        print(f"  Database: {db_status}")
        print(f"  Environment: {self.config.get('environment', 'unknown')}")

        if monitor:
            monitor.state.metrics = {"api_status": api_status, "db_status": db_status}
            monitor.print()

    def cmd_test(self, monitor=None) -> None:
        """Test command - run test suite."""
        if monitor:
            monitor.tests_total = 50

        # Simulate running tests
        for i in range(50):
            # Simulate test execution
            if i % 10 == 7:
                # Failed test
                if monitor:
                    monitor.update_tests(failed=1)
            # Passed test
            elif monitor:
                monitor.update_tests(passed=1)

        if monitor:
            monitor.print()

        render_status("success", "Test suite completed", context=self.context)

    # Deployment stage handlers

    def _validate_stage(self, config: dict) -> dict:
        """
        Validate deployment.
        """
        # Validate configuration, check credentials, etc.
        return {"success": True, "message": "Validation passed"}

    def _build_stage(self, config: dict) -> dict:
        """
        Build application.
        """
        # Build Docker image, compile assets, etc.
        return {"success": True, "message": "Build complete"}

    def _test_stage(self, config: dict) -> dict:
        """
        Run tests.
        """
        # Execute test suite
        return {"success": True, "message": "All tests passed"}

    def _deploy_stage(self, config: dict) -> dict:
        """
        Deploy application.
        """
        # Deploy to target platform
        return {"success": True, "message": "Deployed successfully"}

    def _verify_stage(self, config: dict) -> dict:
        """
        Verify deployment.
        """
        # Check endpoints, run smoke tests
        return {"success": True, "message": "Verification passed"}

    def run(self):
        """
        Run the CLI application.
        """
        self.cli.run()


def main():
    """
    Main entry point.
    """
    # Show banner
    theme = get_theme("atoms")
    print(f"\n{theme.icon} {theme.display_name} FastMCP Server")
    print("=" * 60)
    print("Complete SDK Integration Example")
    print("=" * 60 + "\n")

    # Create and run application
    app = AtomsFastMCPApp()
    app.run()


if __name__ == "__main__":
    main()
