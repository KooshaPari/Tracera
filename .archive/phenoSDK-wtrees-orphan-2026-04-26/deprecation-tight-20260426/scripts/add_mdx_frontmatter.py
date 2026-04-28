#!/usr/bin/env python3
"""Add frontmatter to Fumadocs MDX files."""

import re
from pathlib import Path
from typing import Dict
import yaml

# MDX frontmatter mappings
MDX_METADATA = {
    "apps/docs/content/docs/specs/auth.mdx": {
        "title": "Authentication Specifications",
        "description": "Technical specifications for authentication features",
        "state": "STABLE",
        "since": "0.3.0",
        "specs": [
            "SPEC-AUTH-001: OAuth2 PKCE",
            "SPEC-AUTH-002: JWT Validation",
            "SPEC-AUTH-003: Token Refresh",
        ],
        "stories": [
            "US-001: Authenticate via OAuth2",
            "US-002: Auto-refresh tokens",
        ],
        "implementations": [
            "src/pheno/auth/oauth2_pkce.py",
            "src/pheno/auth/jwt_handler.py",
        ],
        "tests": [
            "tests/auth/test_oauth2_pkce.py",
        ],
        "tags": ["authentication", "oauth2", "jwt", "security"],
    },
    "apps/docs/content/docs/specs/http.mdx": {
        "title": "HTTP Client Specifications",
        "description": "Technical specifications for HTTP client features",
        "state": "STABLE",
        "since": "0.3.0",
        "specs": [
            "SPEC-HTTP-001: Retry Logic",
            "SPEC-HTTP-002: SSE Streaming",
            "SPEC-HTTP-003: Response Transformers",
            "SPEC-HTTP-004: Rate Limiting",
        ],
        "stories": [
            "US-010: Retry failed requests",
            "US-011: Stream real-time events",
            "US-012: Transform responses",
            "US-032: Configure rate limits",
        ],
        "implementations": [
            "src/pheno/clients/retry.py",
            "src/pheno/clients/sse_handler.py",
            "src/pheno/clients/transformers.py",
            "src/pheno/clients/rate_limit.py",
        ],
        "tests": [
            "tests/clients/test_retry.py",
            "tests/clients/test_sse_handler.py",
            "tests/clients/test_transformers.py",
        ],
        "tags": ["http", "streaming", "sse", "retry", "rate-limiting"],
    },
    "apps/docs/content/docs/specs/storage.mdx": {
        "title": "Storage Specifications",
        "description": "Technical specifications for storage features",
        "state": "STABLE",
        "since": "0.2.0",
        "specs": [
            "SPEC-STOR-001: Multi-Backend Storage",
            "SPEC-STOR-002: ETag Caching",
            "SPEC-STOR-003: Streaming Upload",
        ],
        "stories": [
            "US-020: Unified storage API",
            "US-021: Cache with ETags",
            "US-022: Upload large files",
        ],
        "implementations": [
            "src/pheno/storage/providers.py",
            "src/pheno/storage/etag_cache.py",
        ],
        "tests": [
            "tests/storage/test_providers.py",
            "tests/storage/test_etag_cache.py",
        ],
        "tags": ["storage", "s3", "caching", "streaming"],
    },
    "apps/docs/content/docs/specs/mcp.mdx": {
        "title": "MCP Protocol Specifications",
        "description": "Technical specifications for MCP features",
        "state": "STABLE",
        "since": "0.3.0",
        "specs": [
            "SPEC-MCP-001: Tool Discovery",
            "SPEC-MCP-002: Resource Access",
            "SPEC-MCP-003: Prompt Templates",
        ],
        "stories": [
            "US-060: Discover MCP tools",
            "US-061: Access MCP resources",
            "US-062: Use prompt templates",
        ],
        "implementations": [
            "src/pheno/adapters/sst/sdk_adapter.py",
        ],
        "tests": [
            "tests/test_sst_sdk_adapter.py",
        ],
        "tags": ["mcp", "sst", "tools", "resources"],
    },
    "apps/docs/content/docs/specs/observability.mdx": {
        "title": "Observability Specifications",
        "description": "Technical specifications for observability features",
        "state": "STABLE",
        "since": "0.3.0",
        "specs": [
            "SPEC-OBS-001: OpenTelemetry",
            "SPEC-OBS-002: Structured Logging",
            "SPEC-OBS-003: Health Checks",
        ],
        "stories": [
            "US-033: Instrument with OTel",
            "US-034: Structured logging",
            "US-035: Deploy health checks",
        ],
        "implementations": [
            "src/pheno/telemetry/opentelemetry.py",
            "src/pheno/telemetry/structured_logging.py",
            "src/pheno/health/checks.py",
        ],
        "tests": [
            "tests/telemetry/",
            "tests/health/",
        ],
        "tags": ["observability", "opentelemetry", "logging", "health"],
    },
    "apps/docs/content/docs/api/pheno-auth.mdx": {
        "title": "pheno.auth API Reference",
        "description": "Authentication module API documentation",
        "state": "STABLE",
        "since": "0.3.0",
        "module": "pheno.auth",
        "specs": ["SPEC-AUTH-001", "SPEC-AUTH-002", "SPEC-AUTH-003"],
        "tags": ["api", "authentication", "oauth2", "jwt"],
    },
    "apps/docs/content/docs/api/pheno-clients.mdx": {
        "title": "pheno.clients API Reference",
        "description": "HTTP clients module API documentation",
        "state": "STABLE",
        "since": "0.3.0",
        "module": "pheno.clients",
        "specs": ["SPEC-HTTP-001", "SPEC-HTTP-002", "SPEC-HTTP-003", "SPEC-HTTP-004"],
        "tags": ["api", "http", "streaming", "retry"],
    },
    "apps/docs/content/docs/api/pheno-storage.mdx": {
        "title": "pheno.storage API Reference",
        "description": "Storage module API documentation",
        "state": "STABLE",
        "since": "0.2.0",
        "module": "pheno.storage",
        "specs": ["SPEC-STOR-001", "SPEC-STOR-002", "SPEC-STOR-003"],
        "tags": ["api", "storage", "caching"],
    },
}


def add_or_update_frontmatter(file_path: Path, metadata: Dict):
    """Add or update YAML frontmatter in MDX file."""
    if not file_path.exists():
        print(f"⚠️  {file_path}: File not found")
        return

    with open(file_path) as f:
        content = f.read()

    # Check if has frontmatter
    if content.startswith('---'):
        # Find end of frontmatter
        end_idx = content.find('\n---\n', 3)
        if end_idx == -1:
            end_idx = content.find('\n---', 3)
            if end_idx == -1:
                print(f"⚠️  {file_path}: Malformed frontmatter")
                return

        # Parse existing frontmatter
        try:
            existing_fm = yaml.safe_load(content[3:end_idx])
            if existing_fm is None:
                existing_fm = {}
        except yaml.YAMLError:
            print(f"⚠️  {file_path}: Could not parse frontmatter")
            return

        body = content[end_idx + 4:]

        # Merge metadata (new values override)
        existing_fm.update(metadata)

        # Write back
        new_fm = yaml.dump(existing_fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_fm}---\n{body}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"✓ {file_path}: Updated frontmatter")
    else:
        # Add new frontmatter
        new_fm = yaml.dump(metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_fm}---\n\n{content}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"✓ {file_path}: Added frontmatter")


def main():
    """Run MDX frontmatter addition."""
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("Adding MDX Frontmatter")
    print("=" * 60)
    print()

    count = 0
    for file_path, metadata in MDX_METADATA.items():
        full_path = project_root / file_path
        add_or_update_frontmatter(full_path, metadata)
        count += 1

    print()
    print(f"✅ Processed {count} MDX files")
    print()
    print("Next steps:")
    print("1. Run: ./scripts/verify_inline_metadata.sh")
    print("2. Review changes: git diff apps/docs/")
    print("3. Add more MDX files to MDX_METADATA dict")


if __name__ == "__main__":
    main()
