"""Test environment manager for auto-targeting different deployment targets.

Handles environment setup for:
- local: Local development (localhost, local database)
- dev: Development deployment
- prod: Production deployment

Inspired by atoms-mcp-prod/test_env_manager.py
"""

import os
from enum import Enum
from typing import Any, Dict, cast


class TestEnvironment(Enum):
    """Supported test environments."""

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

    @classmethod
    def from_string(cls, value: str) -> "TestEnvironment":
        """Parse environment string.
        
        Args:
            value: Environment string (local, dev, prod)
            
        Returns:
            TestEnvironment enum value
            
        Raises:
            ValueError: If environment is invalid
        """
        value_lower = value.lower().strip()
        
        try:
            return cls(value_lower)
        except ValueError:
            raise ValueError(f"Invalid environment: {value}. Use: local, dev, or prod")


class TestEnvManager:
    """Manages test environment configuration."""

    # Environment configurations
    CONFIGS = {
        TestEnvironment.LOCAL: {
            "name": "Local Development",
            "api_url": "http://localhost:8000",
            "db_url": os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
            "timeout": 10,
            "retry_attempts": 3,
            "description": "Local development with local services",
        },
        TestEnvironment.DEV: {
            "name": "Development",
            "api_url": os.getenv("DEV_API_URL", "https://dev.tracertm.example.com"),
            "db_url": os.getenv("DEV_DATABASE_URL"),
            "timeout": 30,
            "retry_attempts": 5,
            "description": "Development deployment",
        },
        TestEnvironment.PROD: {
            "name": "Production",
            "api_url": os.getenv("PROD_API_URL", "https://tracertm.example.com"),
            "db_url": os.getenv("PROD_DATABASE_URL"),
            "timeout": 60,
            "retry_attempts": 5,
            "description": "Production deployment",
        },
    }

    @classmethod
    def get_environment_for_scope(cls, scope: str) -> TestEnvironment:
        """Determine which environment to use based on test scope.

        Args:
            scope: Test scope - 'unit', 'integration', 'e2e'

        Returns:
            TestEnvironment to use
        """
        # Unit tests always use local (they don't need deployment)
        if scope == "unit":
            return TestEnvironment.LOCAL

        # Check if explicitly set via environment variable
        explicit_env = os.getenv("TEST_ENV")
        if explicit_env:
            try:
                return TestEnvironment.from_string(explicit_env)
            except ValueError:
                pass

        # Default to dev for integration/e2e
        if scope in ["integration", "e2e"]:
            return TestEnvironment.DEV

        return TestEnvironment.LOCAL

    @classmethod
    def get_config(cls, environment: TestEnvironment) -> dict[str, Any]:
        """Get configuration for an environment.

        Args:
            environment: TestEnvironment to get config for

        Returns:
            Configuration dictionary
        """
        config = cls.CONFIGS[environment]
        if isinstance(config, dict[str, Any]):
            return dict(config)
        return cast(dict[str, Any], {})

    @classmethod
    def setup_environment(cls, environment: TestEnvironment) -> None:
        """Set up environment variables for testing.

        Args:
            environment: TestEnvironment to set up
        """
        config = cls.get_config(environment)

        # Set TraceRTM-specific variables
        os.environ["TRACERTM_API_URL"] = config["api_url"]
        os.environ["TRACERTM_DB_URL"] = config["db_url"]
        os.environ["TRACERTM_TIMEOUT"] = str(config["timeout"])
        os.environ["TRACERTM_RETRY_ATTEMPTS"] = str(config["retry_attempts"])

        # Set database URL for SQLAlchemy
        if config["db_url"]:
            os.environ["DATABASE_URL"] = config["db_url"]

        # Set environment-specific URLs for different test types
        if environment == TestEnvironment.LOCAL:
            os.environ["TRACERTM_INTEGRATION_BASE_URL"] = "http://localhost:8000"
            os.environ["TRACERTM_E2E_BASE_URL"] = "http://localhost:8000"
        elif environment == TestEnvironment.DEV:
            os.environ["TRACERTM_INTEGRATION_BASE_URL"] = config["api_url"]
            os.environ["TRACERTM_E2E_BASE_URL"] = config["api_url"]
        elif environment == TestEnvironment.PROD:
            os.environ["TRACERTM_INTEGRATION_BASE_URL"] = config["api_url"]
            os.environ["TRACERTM_E2E_BASE_URL"] = config["api_url"]

    @classmethod
    def print_environment_info(cls, environment: TestEnvironment) -> None:
        """Print environment information.

        Args:
            environment: TestEnvironment to print info for
        """
        config = cls.get_config(environment)
        print(f"🎯 Test Environment: {config['name']}")
        print(f"📝 Description: {config['description']}")
        print(f"🔗 API URL: {config['api_url']}")
        print(f"⏱️  Timeout: {config['timeout']}s")
        print(f"🔄 Retries: {config['retry_attempts']}")
