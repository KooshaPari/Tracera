#!/usr/bin/env python3
"""Add inline state/cross-reference metadata to source files.

This script systematically adds metadata to:
- Python module docstrings
- MDX frontmatter
- Markdown frontmatter
- Test files
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# Metadata mapping for each module
MODULE_METADATA = {
    "src/pheno/auth/__init__.py": {
        "state": "STABLE",
        "since": "0.3.0",
        "specs": ["SPEC-AUTH-001", "SPEC-AUTH-002", "SPEC-AUTH-003"],
        "stories": ["US-001", "US-002"],
        "tests": "tests/auth/",
        "docs": "docs/specs/auth.md, docs/tutorials/authentication.md",
        "features": [
            ("OAuth2 with PKCE for CLI applications", "SPEC-AUTH-001"),
            ("JWT validation and processing", "SPEC-AUTH-002"),
            ("Token refresh and lifecycle management", "SPEC-AUTH-003"),
        ],
    },
    "src/pheno/clients/__init__.py": {
        "state": "STABLE",
        "since": "0.3.0",
        "specs": ["SPEC-HTTP-001", "SPEC-HTTP-002", "SPEC-HTTP-003", "SPEC-HTTP-004"],
        "stories": ["US-010", "US-011", "US-012", "US-032"],
        "tests": "tests/clients/",
        "docs": "docs/specs/http.md, docs/api/clients.md",
        "features": [
            ("Retry logic with exponential backoff", "SPEC-HTTP-001"),
            ("SSE streaming support", "SPEC-HTTP-002"),
            ("Response transformers", "SPEC-HTTP-003"),
            ("Rate limiting [IN_PROGRESS]", "SPEC-HTTP-004"),
        ],
    },
    "src/pheno/storage/__init__.py": {
        "state": "STABLE",
        "since": "0.2.0",
        "specs": ["SPEC-STOR-001", "SPEC-STOR-002", "SPEC-STOR-003"],
        "stories": ["US-020", "US-021", "US-022"],
        "tests": "tests/storage/",
        "docs": "docs/specs/storage.md, docs/tutorials/storage.md",
        "features": [
            ("Multi-backend storage (S3, GCS, Azure, MinIO)", "SPEC-STOR-001"),
            ("ETag-based caching", "SPEC-STOR-002"),
            ("Streaming upload for large files", "SPEC-STOR-003"),
        ],
    },
    "src/pheno/config/__init__.py": {
        "state": "STABLE",
        "since": "0.1.0",
        "adr": "ADR-001 (Pydantic validation)",
        "tests": "tests/config/",
        "docs": "docs/api/configuration.md",
        "features": [
            ("Pydantic-based configuration validation", None),
            ("Environment variable support", None),
            ("YAML configuration loading", None),
        ],
    },
    "src/pheno/adapters/sst/__init__.py": {
        "state": "STABLE",
        "since": "0.3.0",
        "specs": ["SPEC-MCP-001", "SPEC-MCP-002", "SPEC-MCP-003"],
        "stories": ["US-060", "US-061", "US-062"],
        "tests": "tests/adapters/, tests/test_sst_sdk_adapter.py",
        "docs": "docs/specs/mcp.md, docs/tutorials/mcp-integration.md",
        "features": [
            ("MCP Tool Discovery", "SPEC-MCP-001"),
            ("MCP Resource Access", "SPEC-MCP-002"),
            ("Prompt Templates [IN_PROGRESS]", "SPEC-MCP-003"),
        ],
        "deprecated": [
            ("SSTAdapter, SSTResource", "Use SSTSDKAdapter instead", "v0.4.0"),
        ],
    },
    "src/pheno/health/__init__.py": {
        "state": "STABLE",
        "since": "0.3.0",
        "specs": ["SPEC-OBS-003"],
        "stories": ["US-035"],
        "tests": "tests/health/",
        "docs": "docs/specs/observability.md, docs/api/health.md",
        "features": [
            ("Custom health checks via ABC base class", None),
            ("Registry pattern for check management", None),
            ("HTTP endpoint utilities", None),
        ],
    },
    "src/pheno/telemetry/__init__.py": {
        "state": "STABLE",
        "since": "0.3.0",
        "specs": ["SPEC-OBS-001", "SPEC-OBS-002"],
        "stories": ["US-033", "US-034"],
        "adr": "ADR-005 (OpenTelemetry), ADR-006 (Structlog)",
        "tests": "tests/telemetry/",
        "docs": "docs/specs/observability.md, docs/api/telemetry.md",
        "features": [
            ("OpenTelemetry integration for distributed tracing", "SPEC-OBS-001"),
            ("Structured JSON logging with context injection", "SPEC-OBS-002"),
            ("Performance metrics collection", None),
        ],
    },
    "src/pheno/credentials/__init__.py": {
        "state": "STABLE",
        "since": "0.2.0",
        "specs": ["SPEC-CRED-001"],
        "stories": ["US-003", "US-031"],
        "tests": "tests/credentials/",
        "docs": "docs/specs/auth.md",
        "features": [
            ("Secure credential storage", "SPEC-CRED-001"),
            ("Keyring integration", "SPEC-CRED-001"),
        ],
    },
    "src/pheno/framework/__init__.py": {
        "state": "EXPERIMENTAL",
        "since": "0.3.0",
        "tests": "tests/framework/",
        "docs": "docs/api/framework.md",
        "warning": "API may change without notice",
    },
    "src/pheno/tui/__init__.py": {
        "state": "EXPERIMENTAL",
        "since": "0.3.0",
        "tests": "tests/tui/",
        "docs": "docs/api/tui.md",
        "warning": "Early development",
    },
    "src/pheno/analysis/__init__.py": {
        "state": "EXPERIMENTAL",
        "since": "0.3.0",
        "tests": "tests/analysis/",
        "docs": "docs/api/analysis.md",
        "warning": "Limited testing",
    },
    "src/pheno/providers/__init__.py": {
        "state": "EXPERIMENTAL",
        "since": "0.3.0",
        "tests": "tests/providers/",
        "docs": "docs/api/providers.md",
        "warning": "Extension point - API may change",
    },
}


def generate_module_docstring(metadata: Dict) -> str:
    """Generate complete module docstring with metadata."""
    lines = []

    # State metadata
    lines.append(f"State: {metadata['state']}")
    lines.append(f"Since: {metadata['since']}")

    if "specs" in metadata:
        lines.append(f"Specs: {', '.join(metadata['specs'])}")
    if "stories" in metadata:
        lines.append(f"Stories: {', '.join(metadata['stories'])}")
    if "adr" in metadata:
        lines.append(f"ADR: {metadata['adr']}")

    lines.append(f"Tests: {metadata['tests']}")
    lines.append(f"Docs: {metadata['docs']}")
    lines.append("")

    # Features
    if "features" in metadata:
        lines.append("Features:")
        for feature, spec in metadata["features"]:
            if spec:
                lines.append(f"- {feature} ({spec})")
            else:
                lines.append(f"- {feature}")
        lines.append("")

    # Warnings
    if "warning" in metadata:
        lines.append("Warning:")
        lines.append(f"    {metadata['warning']}")
        lines.append("")

    # Deprecated
    if "deprecated" in metadata:
        lines.append("Deprecated:")
        for old, replacement, version in metadata["deprecated"]:
            lines.append(f"- {old}: {replacement} ({version} removal)")

    return "\n".join(lines)


def update_python_docstring(file_path: Path, metadata: Dict):
    """Update Python module docstring with metadata."""
    if not file_path.exists():
        print(f"❌ {file_path} not found")
        return

    with open(file_path) as f:
        content = f.read()

    # Find existing module docstring
    # Pattern: """...""" or '''...''' at start after comments
    pattern = r'(# Standards:.*?\n""")(.*?)(""")'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"⚠️  {file_path}: No docstring found")
        return

    # Check if already has metadata
    if "State:" in match.group(2):
        print(f"✓ {file_path}: Already has metadata")
        return

    # Generate new docstring content
    docstring_content = generate_module_docstring(metadata)

    # Replace
    new_content = content.replace(
        match.group(0),
        f'{match.group(1)}{docstring_content}{match.group(3)}'
    )

    with open(file_path, 'w') as f:
        f.write(new_content)

    print(f"✓ {file_path}: Added metadata")


def add_mdx_frontmatter(file_path: Path, metadata: Dict):
    """Add or update MDX frontmatter."""
    if not file_path.exists():
        return

    with open(file_path) as f:
        content = f.read()

    # Check if has frontmatter
    if content.startswith('---'):
        # Parse existing
        end_idx = content.find('---', 3)
        if end_idx == -1:
            return

        existing_fm = yaml.safe_load(content[3:end_idx])
        body = content[end_idx + 3:]

        # Merge metadata
        existing_fm.update(metadata)

        # Write back
        new_fm = yaml.dump(existing_fm, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_fm}---{body}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"✓ {file_path}: Updated frontmatter")
    else:
        # Add new frontmatter
        new_fm = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_fm}---\n\n{content}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"✓ {file_path}: Added frontmatter")


def main():
    """Run metadata addition."""
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("Adding Inline Metadata")
    print("=" * 60)

    # Update Python modules
    print("\n📝 Updating Python modules...")
    for file_path, metadata in MODULE_METADATA.items():
        full_path = project_root / file_path
        update_python_docstring(full_path, metadata)

    print("\n✅ Complete!")
    print("\nNext steps:")
    print("1. Run: scripts/verify_inline_metadata.sh")
    print("2. Review changes: git diff")
    print("3. Add test markers: @pytest.mark.spec('SPEC-XXX-YYY')")
    print("4. Update MDX files with frontmatter")


if __name__ == "__main__":
    main()
