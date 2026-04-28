#!/usr/bin/env python3
"""Batch add pytest markers to test files."""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# Map test paths to specs/stories
TEST_MAPPINGS = {
    "tests/auth/": {
        "specs": ["SPEC-AUTH-001", "SPEC-AUTH-002", "SPEC-AUTH-003"],
        "stories": ["US-001", "US-002"],
        "feature": "authentication",
    },
    "tests/clients/": {
        "specs": ["SPEC-HTTP-001", "SPEC-HTTP-002", "SPEC-HTTP-003"],
        "stories": ["US-010", "US-011", "US-012"],
        "feature": "http-clients",
    },
    "tests/storage/": {
        "specs": ["SPEC-STOR-001", "SPEC-STOR-002", "SPEC-STOR-003"],
        "stories": ["US-020", "US-021", "US-022"],
        "feature": "storage",
    },
    "tests/config/": {
        "specs": [],
        "stories": [],
        "feature": "configuration",
    },
    "tests/adapters/": {
        "specs": ["SPEC-MCP-001", "SPEC-MCP-002"],
        "stories": ["US-060", "US-061"],
        "feature": "mcp-adapters",
    },
    "tests/health/": {
        "specs": ["SPEC-OBS-003"],
        "stories": ["US-035"],
        "feature": "health-checks",
    },
    "tests/telemetry/": {
        "specs": ["SPEC-OBS-001", "SPEC-OBS-002"],
        "stories": ["US-033", "US-034"],
        "feature": "observability",
    },
}


def infer_test_metadata(test_path: Path) -> Optional[Dict]:
    """Infer metadata based on test file path."""
    path_str = str(test_path.relative_to(PROJECT_ROOT))

    for test_dir, metadata in TEST_MAPPINGS.items():
        if path_str.startswith(test_dir):
            return metadata

    # Default metadata for unmapped tests
    return {"specs": [], "stories": [], "feature": "general"}


def add_module_docstring_metadata(content: str, metadata: Dict) -> str:
    """Add metadata to module docstring."""
    # Find module docstring
    pattern = r'^(""")(.*?)(""")'
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)

    if not match:
        return content

    existing_doc = match.group(2).strip()

    # Check if already has metadata
    if "Specs:" in existing_doc or "State:" in existing_doc:
        return content

    # Build metadata lines
    meta_lines = []
    if metadata["specs"]:
        meta_lines.append(f"Specs: {', '.join(metadata['specs'])}")
    if metadata["stories"]:
        meta_lines.append(f"Stories: {', '.join(metadata['stories'])}")
    if metadata["feature"]:
        meta_lines.append(f"Feature: {metadata['feature']}")

    if not meta_lines:
        return content

    # Insert metadata at start of docstring
    new_doc = "\n".join(meta_lines) + "\n\n" + existing_doc
    new_content = content.replace(match.group(0), f'{match.group(1)}{new_doc}{match.group(3)}')

    return new_content


def add_test_markers_to_function(content: str, func_match: re.Match, metadata: Dict) -> str:
    """Add pytest markers to a test function."""
    func_def = func_match.group(0)

    # Check if already has markers
    if "@pytest.mark.spec" in func_def or "@pytest.mark.story" in func_def:
        return content

    # Find the function definition line
    func_line_match = re.search(r'(async )?def (test_\w+)', func_def)
    if not func_line_match:
        return content

    # Build markers
    markers = []
    if metadata["specs"]:
        # Use first spec as primary
        markers.append(f'    @pytest.mark.spec("{metadata["specs"][0]}")')
    if metadata["stories"]:
        # Use first story as primary
        markers.append(f'    @pytest.mark.story("{metadata["stories"][0]}")')
    if metadata["feature"]:
        markers.append(f'    @pytest.mark.feature("{metadata["feature"]}")')

    if not markers:
        return content

    # Find where to insert markers (before the def line)
    insert_pos = func_match.start()

    # Insert markers
    markers_text = "\n".join(markers) + "\n"
    new_content = content[:insert_pos] + markers_text + content[insert_pos:]

    return new_content


def update_test_file(file_path: Path):
    """Update a test file with markers."""
    if not file_path.exists():
        return 0

    with open(file_path) as f:
        content = f.read()

    # Infer metadata
    metadata = infer_test_metadata(file_path)
    if not metadata:
        return 0

    original_content = content

    # Add module docstring metadata
    content = add_module_docstring_metadata(content, metadata)

    # Find all test functions (both class methods and standalone)
    # Pattern: def test_xxx or async def test_xxx
    # Look for decorators before function
    test_pattern = r'((?:    @\w+.*\n)*)(    (?:async )?def test_\w+.*?\n(?:.*?\n)*?(?=\n    (?:def |async def |@|class )|$))'

    functions_found = 0
    for match in re.finditer(test_pattern, content, re.MULTILINE):
        # Only add markers if function doesn't have them already
        if "@pytest.mark.spec" not in match.group(0):
            content = add_test_markers_to_function(content, match, metadata)
            functions_found += 1

    # If no changes, return 0
    if content == original_content:
        return 0

    # Write back
    with open(file_path, 'w') as f:
        f.write(content)

    return functions_found


def main():
    """Run batch test marker addition."""
    print("=" * 70)
    print("Batch Adding Pytest Markers to Test Files")
    print("=" * 70)
    print()

    # Find all test files
    test_files = list(PROJECT_ROOT.glob("tests/**/test_*.py"))

    print(f"Found {len(test_files)} test files")
    print()

    updated_files = 0
    total_functions = 0
    skipped = 0

    for file_path in sorted(test_files):
        try:
            functions = update_test_file(file_path)
            if functions > 0:
                print(f"✓ {file_path.relative_to(PROJECT_ROOT)} (+{functions} markers)")
                updated_files += 1
                total_functions += functions
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ {file_path.relative_to(PROJECT_ROOT)}: {e}")

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Files updated: {updated_files}")
    print(f"  Total markers added: {total_functions}")
    print(f"  Files skipped: {skipped} (already have markers)")
    print(f"  Total files: {len(test_files)}")
    print()

    if updated_files > 0:
        print("✅ Batch test marker addition complete!")
        print()
        print("Next steps:")
        print("  1. Run: ./scripts/verify_inline_metadata.sh")
        print("  2. Review: git diff tests/")
        print("  3. Run tests: pytest -v")


if __name__ == "__main__":
    main()
