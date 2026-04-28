#!/usr/bin/env python3
"""Security validation script for PhenoSDK.

Validates all security improvements are properly configured:
- GitHub security features
- Secret detection
- Security headers
- Configuration hardening
"""

import json
import subprocess
import sys
from pathlib import Path


def check_github_workflows() -> bool:
    """Check that security workflows exist."""
    print("🔍 Checking GitHub security workflows...")

    required_workflows = [
        ".github/dependabot.yml",
        ".github/workflows/codeql-analysis.yml",
        ".github/workflows/security-snyk.yml",
        ".github/workflows/secret-scanning.yml",
        ".github/codeql-config.yml",
    ]

    all_exist = True
    for workflow in required_workflows:
        path = Path(workflow)
        if path.exists():
            print(f"  ✓ {workflow}")
        else:
            print(f"  ✗ {workflow} - MISSING")
            all_exist = False

    return all_exist


def check_secrets_baseline() -> bool:
    """Check that secrets baseline exists."""
    print("\n🔍 Checking secrets baseline...")

    baseline = Path(".secrets.baseline")
    if baseline.exists():
        size = baseline.stat().st_size
        print(f"  ✓ .secrets.baseline exists ({size} bytes)")
        return True
    else:
        print("  ✗ .secrets.baseline - MISSING")
        return False


def check_security_headers() -> bool:
    """Check security headers module."""
    print("\n🔍 Checking security headers module...")

    try:
        from pheno_sdk.middleware.security_headers import (
            SecurityHeaders,
            get_default_security_headers,
        )

        headers_manager = get_default_security_headers()
        headers = headers_manager.get_headers()

        required_headers = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "Permissions-Policy",
        ]

        all_present = True
        for header in required_headers:
            if header in headers:
                print(f"  ✓ {header}")
            else:
                print(f"  ✗ {header} - MISSING")
                all_present = False

        print(f"\n  Total headers: {len(headers)}")
        return all_present

    except ImportError as e:
        print(f"  ✗ Failed to import security headers module: {e}")
        return False


def check_config_validation() -> bool:
    """Check configuration validation."""
    print("\n🔍 Checking configuration validation...")

    try:
        from pheno_sdk.config import PhenoConfig, check_hardcoded_secrets

        print("  ✓ Configuration module imported")

        # Test hardcoded secret detection
        test_file = Path("src/pheno_sdk/config.py")
        suspicious = check_hardcoded_secrets(test_file)
        print(f"  ✓ Hardcoded secret detection working ({len(suspicious)} suspicious lines in test)")

        return True

    except ImportError as e:
        print(f"  ✗ Failed to import config module: {e}")
        return False


def check_env_example() -> bool:
    """Check .env.example is complete."""
    print("\n🔍 Checking .env.example...")

    env_example = Path(".env.example")
    if not env_example.exists():
        print("  ✗ .env.example - MISSING")
        return False

    content = env_example.read_text()

    required_vars = [
        "PHENO_SECURITY__SECRET_KEY",
        "PHENO_SECURITY__JWT_SECRET",
        "PHENO_ENVIRONMENT",
        "PHENO_DEBUG",
    ]

    all_present = True
    for var in required_vars:
        if var in content:
            print(f"  ✓ {var}")
        else:
            print(f"  ✗ {var} - MISSING")
            all_present = False

    return all_present


def check_pre_commit_hooks() -> bool:
    """Check pre-commit hooks configuration."""
    print("\n🔍 Checking pre-commit hooks...")

    config = Path(".pre-commit-config.yaml")
    if not config.exists():
        print("  ✗ .pre-commit-config.yaml - MISSING")
        return False

    content = config.read_text()

    required_hooks = [
        "detect-secrets",
        "ggshield",
        "bandit",
    ]

    all_present = True
    for hook in required_hooks:
        if hook in content:
            print(f"  ✓ {hook}")
        else:
            print(f"  ✗ {hook} - MISSING")
            all_present = False

    return all_present


def generate_security_report() -> dict:
    """Generate comprehensive security report."""
    results = {
        "github_workflows": check_github_workflows(),
        "secrets_baseline": check_secrets_baseline(),
        "security_headers": check_security_headers(),
        "config_validation": check_config_validation(),
        "env_example": check_env_example(),
        "pre_commit_hooks": check_pre_commit_hooks(),
    }

    return results


def main() -> int:
    """Run security validation."""
    print("=" * 70)
    print("PhenoSDK Security Validation")
    print("=" * 70)

    results = generate_security_report()

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check, status in results.items():
        icon = "✓" if status else "✗"
        print(f"{icon} {check.replace('_', ' ').title()}")

    print("\n" + "=" * 70)
    print(f"Score: {passed}/{total} ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("🎉 All security checks passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} security checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
