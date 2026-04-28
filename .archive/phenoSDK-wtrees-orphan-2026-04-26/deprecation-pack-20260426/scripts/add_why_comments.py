#!/usr/bin/env python3
"""Add strategic WHY comments to complex business logic."""

from pathlib import Path

REPO_ROOT = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk")

# Strategic WHY comments to add
WHY_COMMENTS = [
    # Credential rotation - security rationale
    {
        "file": "src/pheno/credentials/rotate.py",
        "after": "# Why: Security best practice - credentials must be rotated on a schedule",
        "line": "def add_policy"
    },
    # Auth RBAC - business logic
    {
        "file": "src/pheno/auth/rbac.py",
        "after": "# Why: RBAC enforces principle of least privilege at runtime",
        "line": "def validate_access"
    },
    # Database migrations - data integrity
    {
        "file": "src/pheno/database/migrations.py",
        "after": "# Why: Forward-only migrations prevent data loss and ensure reproducibility",
        "line": "def create_alembic"
    },
    # Enterprise security - compliance
    {
        "file": "src/pheno/enterprise/security.py",
        "after": "# Why: Compliance frameworks (SOC2, HIPAA) require audit trails",
        "line": "def log_event"
    },
    # Credential broker - isolation
    {
        "file": "src/pheno/credentials/broker.py",
        "after": "# Why: Credential broker isolates secrets management from business logic",
        "line": "class Broker"
    },
    # Observability - debugging
    {
        "file": "src/pheno/observability/bootstrap.py",
        "after": "# Why: OpenTelemetry enables distributed tracing for debugging microservices",
        "line": "def create_otel"
    },
    # Health checks - reliability
    {
        "file": "src/pheno/health/checks.py",
        "after": "# Why: Health checks enable automated recovery and load balancer integration",
        "line": "def validate_all"
    },
    # MFA - security defense-in-depth
    {
        "file": "src/pheno/auth/mfa_handler.py",
        "after": "# Why: MFA provides defense-in-depth against credential compromise",
        "line": "def validate_code"
    },
    # Schema validation - data quality
    {
        "file": "src/pheno/lib/schema_manager.py",
        "after": "# Why: Schema validation prevents corrupt data from entering the system",
        "line": "def validate_schema"
    },
    # Deployment checks - production safety
    {
        "file": "src/pheno/lib/deployment/checks.py",
        "after": "# Why: Pre-deployment checks prevent broken deployments from reaching production",
        "line": "def validate_code_quality"
    },
]

def main():
    """Add WHY comments to complex business logic."""
    print("Adding strategic WHY comments...")

    comments_added = 0

    for comment_spec in WHY_COMMENTS:
        file_path = REPO_ROOT / comment_spec["file"]

        if not file_path.exists():
            print(f"  ⚠ File not found: {file_path}")
            continue

        try:
            content = file_path.read_text()
            search_line = comment_spec["line"]
            why_comment = comment_spec["after"]

            # Find the line and add comment before it
            lines = content.split('\n')
            modified = False

            for i, line in enumerate(lines):
                if search_line in line and "# Why:" not in lines[max(0, i-1)]:
                    # Add WHY comment before this line
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, " " * indent + why_comment)
                    modified = True
                    comments_added += 1
                    print(f"  ✓ {file_path.relative_to(REPO_ROOT)}")
                    break

            if modified:
                file_path.write_text('\n'.join(lines))

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")

    print(f"\n{comments_added} WHY comments added")
    return 0

if __name__ == "__main__":
    exit(main())
