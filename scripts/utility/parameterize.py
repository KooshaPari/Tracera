#!/usr/bin/env python3
"""
PhenoKits Config Parameterizer

Applies parameterized configurations to projects with validation.
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_schema() -> dict[str, Any]:
    """Load the parameter schema."""
    schema_path = Path(__file__).parent.parent / "schemas" / "config-params.schema.json"
    with open(schema_path) as f:
        return json.load(f)


def validate_project(params: dict[str, Any]) -> list[str]:
    """Validate project parameters."""
    errors = []
    project = params.get("project", {})

    # Required fields
    for field in ["name", "org", "github_repo"]:
        if field not in project:
            errors.append(f"project.{field} is required")

    # Pattern validations
    if "name" in project:
        name = project["name"]
        if not name.replace("-", "").isalnum() or not name[0].islower():
            errors.append("project.name must be kebab-case (e.g., 'my-project')")

    if "org" in project:
        org = project["org"]
        if not org[0].isupper() if org else False:
            errors.append("project.org must be PascalCase (e.g., 'MyOrg')")

    return errors


def validate_secrets(params: dict[str, Any]) -> list[str]:
    """Validate secret references."""
    errors = []
    for secret in params.get("secrets", []):
        if not secret.startswith("SECRET:"):
            errors.append(f"Invalid secret format: {secret} (use SECRET:NAME)")
    return errors


def validate(params: dict[str, Any]) -> bool:
    """Validate all parameters."""
    errors = validate_project(params)
    errors.extend(validate_secrets(params))

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("✓ All parameters valid")
    return True


def apply_config(template_path: Path, params: dict[str, Any]) -> str:
    """Apply parameters to a config template."""
    content = template_path.read_text()

    # Replace placeholders
    replacements = {
        "{{project.name}}": params["project"]["name"],
        "{{project.org}}": params["project"]["org"],
        "{{github.repo}}": params["project"]["github_repo"],
        "{{runtime.rust}}": params.get("runtime", {}).get("rust", "1.75"),
        "{{runtime.node}}": params.get("runtime", {}).get("node", "20"),
        "{{runtime.go}}": params.get("runtime", {}).get("go", "1.22"),
        "{{runtime.python}}": params.get("runtime", {}).get("python", "3.12"),
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, str(value))

    return content


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: parameterize.py <params.json> [template_file]")
        sys.exit(1)

    params_file = Path(sys.argv[1])
    with open(params_file) as f:
        params = json.load(f)

    if not validate(params):
        sys.exit(1)

    if len(sys.argv) >= 3:
        template = Path(sys.argv[2])
        result = apply_config(template, params)
        print(result)

    print(f"✓ Parameters validated for {params['project']['name']}")


if __name__ == "__main__":
    main()
