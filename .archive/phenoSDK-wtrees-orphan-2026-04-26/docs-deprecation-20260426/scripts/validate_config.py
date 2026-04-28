#!/usr/bin/env python3
"""
Environment Configuration Validator
===================================

Validates environment configurations for different deployment scenarios.
Ensures required variables are set and values are within acceptable ranges.

Usage:
    python scripts/validate_config.py
    python scripts/validate_config.py --env preview
    python scripts/validate_config.py --env production
"""

import argparse
import sys
from pathlib import Path


class ConfigValidator:
    """
    Validates environment configurations.
    """

    def __init__(self, env_type: str = "development"):
        self.env_type = env_type
        self.required_vars = self._get_required_vars()

    def _get_required_vars(self) -> dict[str, str]:
        """
        Get required environment variables for each environment type.
        """
        base_required = [
            "PORT",
            "PUBLIC_URL",
        ]

        if self.env_type != "development":
            base_required.extend(
                [
                    "SUPABASE_URL",
                    "SUPABASE_PROJECT_ID",
                    "SUPABASE_ANON_KEY",
                    "SUPABASE_SERVICE_ROLE_KEY",
                    "SUPABASE_DB_PASSWORD",
                    "DB_URL",
                ],
            )

        return dict.fromkeys(base_required, f"Required for {self.env_type} environment")

    def load_environment(self) -> dict[str, str]:
        """
        Load environment variables from appropriate .env file.
        """
        env_file_map = {
            "development": ".env",
            "preview": ".env.preview",
            "production": ".env.production",
        }

        env_file = env_file_map.get(self.env_type, ".env")
        env_path = Path(env_file)

        if not env_path.exists():
            print(f"Environment file {env_file} not found")
            return {}

        env_vars = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

        return env_vars

    def validate(self) -> bool:
        """
        Validate environment configuration.
        """
        print(f"Validating {self.env_type} environment configuration...")

        env_vars = self.load_environment()
        if not env_vars:
            print("❌ No environment variables loaded")
            return False

        missing_vars = []
        invalid_vars = []

        # Check required variables
        for var, description in self.required_vars.items():
            if var not in env_vars or not env_vars[var]:
                missing_vars.append(var)
            elif not self._validate_var_format(var, env_vars[var]):
                invalid_vars.append(var)

        # Report results
        if missing_vars:
            print(f"❌ Missing required variables: {', '.join(missing_vars)}")
            return False

        if invalid_vars:
            print(f"❌ Invalid variable formats: {', '.join(invalid_vars)}")
            return False

        # Additional validations
        validations = [
            self._validate_port(env_vars),
            self._validate_url(env_vars),
        ]

        if all(validations):
            print("✅ Environment configuration is valid")
            return True
        print("❌ Environment configuration validation failed")
        return False

    def _validate_var_format(self, var_name: str, var_value: str) -> bool:
        """
        Validate format of specific environment variables.
        """
        # Port validation
        if var_name == "PORT":
            try:
                port = int(var_value)
                return 1 <= port <= 65535
            except ValueError:
                return False

        # URL validation
        if var_name.endswith("_URL") or var_name == "PUBLIC_URL":
            return var_value.startswith(("http://", "https://")) or var_value == ""

        return True

    def _validate_port(self, env_vars: dict[str, str]) -> bool:
        """
        Validate port configuration.
        """
        port_str = env_vars.get("PORT", "")
        if not port_str:
            print("❌ PORT is not set")
            return False

        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                print(f"❌ PORT {port} is outside valid range (1-65535)")
                return False
            return True
        except ValueError:
            print(f"❌ PORT '{port_str}' is not a valid integer")
            return False

    def _validate_url(self, env_vars: dict[str, str]) -> bool:
        """
        Validate URL configuration.
        """
        url = env_vars.get("PUBLIC_URL", "")
        if not url:
            print("❌ PUBLIC_URL is not set")
            return False

        if not url.startswith(("http://", "https://")):
            print(f"❌ PUBLIC_URL '{url}' must start with http:// or https://")
            return False

        return True


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Pheno SDK Environment Configuration Validator")

    parser.add_argument(
        "--env",
        choices=["development", "preview", "production"],
        default="development",
        help="Environment type to validate",
    )

    args = parser.parse_args()

    validator = ConfigValidator(args.env)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
