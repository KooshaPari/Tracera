"""
Environment Management for Pheno SDK
====================================

Provides environment management utilities for MCP servers.
"""

import os
import subprocess
from pathlib import Path


class EnvironmentManager:
    """
    Manages environment configuration for MCP servers.
    """

    def __init__(self):
        self.project_root = self._find_project_root()

    def _find_project_root(self) -> Path:
        """
        Find the project root directory.
        """
        current = Path(__file__).parent

        # Look for common project indicators
        indicators = [".git", "pyproject.toml", "setup.py", "requirements.txt"]

        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent

        # Fallback to current directory
        return Path.cwd()

    def set_mcp_endpoint_for_target(self, target: str) -> None:
        """Set/unset MCP_ENDPOINT for non-test runtime based on target.

        Rules:
        - production => set to production endpoint
        - local      => set to local endpoint
        - dev/preview=> unset (NONE)
        """
        target = target.lower()

        try:
            # Try to use centralized endpoint registry if available
            from pheno.mcp.qa.config.endpoints import (
                EndpointRegistry,
                Environment,
                MCPProject,
            )

            if target == "production":
                ep = EndpointRegistry.get_endpoint(MCPProject.ATOMS, Environment.PRODUCTION)
                os.environ["MCP_ENDPOINT"] = ep
                os.environ["ATOMS_MCP_ENDPOINT"] = ep
            elif target == "local":
                ep = EndpointRegistry.get_endpoint(MCPProject.ATOMS, Environment.LOCAL)
                os.environ["MCP_ENDPOINT"] = ep
                os.environ["ATOMS_MCP_ENDPOINT"] = ep
            else:
                os.environ.pop("MCP_ENDPOINT", None)
                os.environ.pop("ATOMS_MCP_ENDPOINT", None)
        except ImportError:
            # Fallback to simple environment variable setting
            if target == "production":
                os.environ["MCP_ENDPOINT"] = "https://mcp.atoms.tech"
                os.environ["ATOMS_MCP_ENDPOINT"] = "https://mcp.atoms.tech"
            elif target == "local":
                os.environ["MCP_ENDPOINT"] = "http://localhost:50002"
                os.environ["ATOMS_MCP_ENDPOINT"] = "http://localhost:50002"
            else:
                os.environ.pop("MCP_ENDPOINT", None)
                os.environ.pop("ATOMS_MCP_ENDPOINT", None)

    def ensure_git_state_and_push(self) -> int:
        """Ensure git working tree is committed and pushed to origin current branch.

        Returns 0 on success, non-zero on failure.
        """

        def run(cmd: str) -> tuple[int, str, str]:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True, check=False)
                return result.returncode, result.stdout.strip(), result.stderr.strip()
            except Exception as e:
                return 1, "", str(e)

        # Verify we are in a git repo
        code, _, _ = run("git rev-parse --is-inside-work-tree")
        if code != 0:
            print("⚠️  Not a git repository; skipping auto-commit/push.")
            return 0

        # Determine current branch
        code, branch, err = run("git rev-parse --abbrev-ref HEAD")
        if code != 0 or not branch:
            print(f"❌ Failed to determine current branch: {err}")
            return 1

        # Check for changes
        code, status, _ = run("git status --porcelain")
        if code != 0:
            print(f"❌ Failed to check git status: {status}")
            return 1

        if not status.strip():
            print("✅ Working tree is clean")
        else:
            print("📝 Working tree has changes, committing...")

            # Add all changes
            code, _, err = run("git add -A")
            if code != 0:
                print(f"❌ Failed to add changes: {err}")
                return 1

            # Commit changes
            commit_msg = f"Auto-commit before deployment ({target})"
            code, _, err = run(f'git commit -m "{commit_msg}"')
            if code != 0:
                print(f"❌ Failed to commit changes: {err}")
                return 1

            print("✅ Changes committed")

        # Push to origin
        print(f"📤 Pushing to origin/{branch}...")
        code, _, err = run(f"git push origin {branch}")
        if code != 0:
            print(f"❌ Failed to push to origin: {err}")
            return 1

        print("✅ Pushed to origin")
        return 0

    def get_environment_variables(self) -> dict:
        """
        Get current environment variables relevant to MCP servers.
        """
        return {
            "MCP_ENDPOINT": os.environ.get("MCP_ENDPOINT"),
            "ATOMS_MCP_ENDPOINT": os.environ.get("ATOMS_MCP_ENDPOINT"),
            "ZEN_MCP_ENDPOINT": os.environ.get("ZEN_MCP_ENDPOINT"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
            "PHENO_SDK_ROOT": os.environ.get("PHENO_SDK_ROOT"),
        }

    def setup_development_environment(self, dev_mode: bool = False) -> None:
        """
        Set up development environment variables.
        """
        if dev_mode:
            os.environ.setdefault("FASTMCP_LOG_LEVEL", "DEBUG")
            os.environ.setdefault("ZEN_DEV_MODE", "1")
            os.environ.setdefault("ATOMS_VERBOSE", "1")

        # Set common defaults
        os.environ.setdefault("ZEN_PROVIDER_PRIORITY", "OPENROUTER")
        os.environ.setdefault("EMBEDDINGS_PROVIDER", "ollama")
        os.environ.setdefault("OLLAMA_EMBED_MODEL", "nomic-embed-text")
