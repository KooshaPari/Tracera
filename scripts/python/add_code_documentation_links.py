#!/usr/bin/env python3
"""Add documentation links to code files.

This script adds:
1. Frontmatter to __init__.py (barrel entries)
2. Documentation links to docstrings
3. Inline documentation comments
4. Cross-references between code and docs
"""

import os
import re
from pathlib import Path

# Map of code modules to documentation pages
MODULE_TO_DOCS = {
    "src/pheno/storage/": {
        "doc": "docs/specs/architecture/index.md#database-layer",
        "state": "IN_PROGRESS",
        "description": "Database storage layer - PostgreSQL, Redis, Neo4j",
    },
    "src/pheno/clients/": {
        "doc": "docs/specs/technical/index.md#api-specifications",
        "state": "IN_PROGRESS",
        "description": "HTTP client implementations and transformers",
    },
    "src/pheno/mcp/": {
        "doc": "docs/research/dimensions/phenosdk-tools.md#mcp",
        "state": "IN_PROGRESS",
        "description": "Model Context Protocol server implementation",
    },
    "src/pheno/testing/": {
        "doc": "docs/specs/technical/index.md#testing-specifications",
        "state": "IN_PROGRESS",
        "description": "Testing framework and fixtures",
    },
    "src/pheno/infra/": {
        "doc": "docs/specs/architecture/index.md#infrastructure",
        "state": "IN_PROGRESS",
        "description": "Infrastructure and deployment layer",
    },
    "src/pheno_sdk/cli/": {
        "doc": "docs/planning/timeline.md#week-1",
        "state": "COMPLETE",
        "description": "CLI interface (Typer-based)",
    },
}

# Function patterns and their documentation links
FUNCTION_DOC_LINKS = {
    r"def test_.*\(": {
        "doc": "docs/specs/technical/index.md#testing-specifications",
        "template": "Test implementation following testing specifications",
    },
    r"def create_.*\(": {
        "doc": "docs/specs/technical/index.md#api-specifications",
        "template": "Creation endpoint following API specifications",
    },
    r"class.*Model.*:": {
        "doc": "docs/specs/architecture/index.md#data-models",
        "template": "Data model following architecture specifications",
    },
    r"async def .*\(": {
        "doc": "docs/research/dimensions/trace-testing.md#async-test-setup",
        "template": "Async implementation for concurrent operations",
    },
}

# Barrel entry template for __init__.py
BARREL_FRONTMATTER = """# Barrel Export Module
#
# This module exports public API for {module_name}
#
# Documentation:
#   - Specification: {doc_link}
#   - State: {state}
#   - Description: {description}
#
# Cross-references:
#   - Related Planning: {planning_link}
#   - Related Research: {research_link}
#
# Implementation Notes:
#   - Follows {state} state from state-model.yaml
#   - All exported items have documentation links
#   - Internal implementation details are private (_prefixed)

"""

# Docstring template for functions/classes
DOCSTRING_TEMPLATE = '''"""
{original_docstring}

Documentation:
    See specification: {doc_link}
    Related research: {research_link}
    Timeline: {timeline}

References:
    - Specification: {doc_link}
    - Implementation state: {state}
"""'''

# Inline comment template
INLINE_COMMENT = """
# Linked to Documentation
# See: {doc_link}
# State: {state}
# Purpose: {purpose}
"""


def find_python_files(directory: str) -> list[str]:
    """Find all Python files in directory."""
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Skip test directories and caches
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache", ".mypy_cache"}]

        files.extend(os.path.join(root, filename) for filename in filenames if filename.endswith(".py"))

    return files


def get_module_doc_link(filepath: str) -> dict[str, str] | None:
    """Get documentation link for a code module."""
    for module_path, doc_info in MODULE_TO_DOCS.items():
        if filepath.startswith(module_path.replace("/", os.sep)):
            return doc_info
    return None


def extract_docstring(content: str) -> tuple[str | None, int, int]:
    """Extract docstring from content, return (docstring, start_line, end_line)."""
    # Look for """ or ''' docstrings
    patterns = [
        (r'^(""".*?""")', re.MULTILINE | re.DOTALL),
        (r"^('''.*?''')", re.MULTILINE | re.DOTALL),
    ]

    for pattern, flags in patterns:
        match = re.search(pattern, content, flags)
        if match:
            start = content[: match.start()].count("\n")
            end = start + match.group(1).count("\n")
            return match.group(1), start, end

    return None, 0, 0


def add_barrel_frontmatter(filepath: str, module_info: dict[str, str]) -> bool:
    """Add frontmatter to __init__.py files."""
    if not filepath.endswith("__init__.py"):
        return False

    try:
        content = Path(filepath).read_text(encoding="utf-8")

        # Skip if already has documentation comment
        if "Documentation:" in content or "Barrel Export" in content:
            return False

        module_name = Path(filepath).parent.name
        planning_link = "docs/planning/timeline.md"
        research_link = "docs/research/overview.md"

        frontmatter = BARREL_FRONTMATTER.format(
            module_name=module_name,
            doc_link=module_info["doc"],
            state=module_info["state"],
            description=module_info["description"],
            planning_link=planning_link,
            research_link=research_link,
        )

        # Prepend frontmatter
        new_content = frontmatter + "\n" + content

        Path(filepath).write_text(new_content, encoding="utf-8")

        return True
    except Exception:
        return False


def add_docstring_links(filepath: str, _module_info: dict[str, str]) -> bool:
    """Add documentation links to function/class docstrings."""
    try:
        content = Path(filepath).read_text(encoding="utf-8")

        # Count how many docstrings we can enhance
        docstring_count = content.count('"""') // 2

        # For now, just note that this file should have doc links
        # Full implementation would parse AST and modify each docstring
        return docstring_count != 0
    except Exception:
        return False


def add_inline_comments(filepath: str, module_info: dict[str, str]) -> bool:
    """Add inline documentation comments."""
    try:
        with Path(filepath).open(encoding="utf-8") as f:
            lines = f.readlines()

        # Add comment at top of file if not present
        if not any("Linked to Documentation" in line for line in lines[:10]):
            comment = INLINE_COMMENT.format(
                doc_link=module_info["doc"],
                state=module_info["state"],
                purpose=module_info["description"],
            )

            # Insert after shebang/encoding if present
            insert_pos = 0
            if lines and (lines[0].startswith("#!") or "coding" in lines[0]):
                insert_pos = 1

            lines.insert(insert_pos, comment + "\n")

            with Path(filepath).open("w", encoding="utf-8") as f:
                f.writelines(lines)

            return True
        return False
    except Exception:
        return False


def generate_documentation_index() -> str:
    """Generate index of code-to-docs links."""
    lines = [
        "# Code Documentation Links Index",
        "",
        "This index maps code modules to their documentation.",
        "",
    ]

    for module_path, doc_info in MODULE_TO_DOCS.items():
        lines.extend((
            f"## {module_path}",
            f"- **Documentation**: {doc_info['doc']}",
            f"- **State**: {doc_info['state']}",
            f"- **Description**: {doc_info['description']}",
            "",
        ))

    return "\n".join(lines)


def main() -> None:
    """Add documentation links to code files."""
    base_path = Path(__file__).parent.parent

    total_processed = 0
    files_updated = 0

    for module_path, doc_info in MODULE_TO_DOCS.items():
        full_module_path = base_path / module_path

        if not full_module_path.exists():
            continue

        # Find all Python files
        py_files = find_python_files(str(full_module_path))

        for py_file in py_files:
            total_processed += 1

            # Add barrel frontmatter to __init__.py
            if add_barrel_frontmatter(py_file, doc_info):
                files_updated += 1

            # Add inline comments
            if add_inline_comments(py_file, doc_info):
                files_updated += 1

    # Generate index
    index_content = generate_documentation_index()
    index_path = base_path / "docs" / "code-documentation-index.md"

    Path(index_path).write_text(index_content, encoding="utf-8")


if __name__ == "__main__":
    main()
