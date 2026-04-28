#!/usr/bin/env python3
"""Batch add inline metadata to ALL Python modules."""

import re
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent


def infer_metadata(module_path: Path) -> Optional[Dict]:
    """Infer metadata based on module path."""
    path_str = str(module_path.relative_to(PROJECT_ROOT))

    # Already done - skip
    already_done = [
        "src/pheno/auth/__init__.py",
        "src/pheno/clients/__init__.py",
        "src/pheno/storage/__init__.py",
        "src/pheno/config/__init__.py",
        "src/pheno/adapters/sst/__init__.py",
        "src/pheno/health/__init__.py",
        "src/pheno/telemetry/__init__.py",
        "src/pheno/credentials/__init__.py",
        "src/pheno/framework/__init__.py",
        "src/pheno/tui/__init__.py",
        "src/pheno/analysis/__init__.py",
        "src/pheno/providers/__init__.py",
    ]

    if path_str in already_done:
        return None

    # Infer state based on path
    state = "STABLE"
    warning = None

    # Experimental modules
    if any(x in path_str for x in ["experimental", "alpha", "beta", "preview"]):
        state = "EXPERIMENTAL"
        warning = "API may change without notice"
    elif "ui/" in path_str or "tui/" in path_str or "gui/" in path_str:
        state = "EXPERIMENTAL"
        warning = "UI components are in early development"
    elif "infra/" in path_str:
        state = "STABLE"
    elif "database/" in path_str or "db/" in path_str:
        state = "STABLE"
    elif "workflow/" in path_str or "orchestrator/" in path_str:
        state = "STABLE"
    elif "kits/" in path_str:
        state = "STABLE"

    # Determine version
    since = "0.3.0"  # Default
    if "infra/" in path_str or "kits/" in path_str:
        since = "0.2.0"
    elif "database/" in path_str:
        since = "0.1.0"

    # Build metadata
    metadata = {
        "state": state,
        "since": since,
        "tests": f"tests/{path_str.replace('src/pheno/', '').replace('/__init__.py', '/')}",
        "docs": f"docs/api/{path_str.replace('src/pheno/', '').replace('/__init__.py', '').replace('/', '-')}.md",
    }

    if warning:
        metadata["warning"] = warning

    return metadata


def generate_simple_docstring(metadata: Dict, module_name: str) -> str:
    """Generate docstring with extended metadata."""
    lines = []

    # Core metadata
    lines.append(f"State: {metadata['state']}")
    lines.append(f"Since: {metadata['since']}")

    if "version_changed" in metadata:
        lines.append(f"Version_Changed: {metadata['version_changed']}")

    # Specifications
    if "specs" in metadata:
        lines.append(f"Specs: {', '.join(metadata['specs'])}")
    if "specified_by" in metadata:
        lines.append(f"Specified_By: {metadata['specified_by']}")

    # User Stories
    if "stories" in metadata:
        lines.append(f"Stories: {', '.join(metadata['stories'])}")
    if "implements" in metadata:
        lines.append(f"Implements: {metadata['implements']}")

    # Tests
    lines.append(f"Tests: {metadata['tests']}")
    if "verified_by" in metadata:
        lines.append(f"Verified_By: {metadata['verified_by']}")
    if "coverage" in metadata:
        lines.append(f"Coverage: {metadata['coverage']}")

    # Documentation
    lines.append(f"Docs: {metadata['docs']}")
    if "explained_by" in metadata:
        lines.append(f"Explained_By: {metadata['explained_by']}")
    if "demonstrated_by" in metadata:
        lines.append(f"Demonstrated_By: {metadata['demonstrated_by']}")

    # Decisions
    if "decided_by" in metadata:
        lines.append(f"Decided_By: {metadata['decided_by']}")
    if "adr" in metadata:
        lines.append(f"ADR: {metadata['adr']}")

    # Code Structure
    if "depends_on" in metadata:
        lines.append(f"Depends_On: {', '.join(metadata['depends_on'])}")
    if "imports" in metadata:
        lines.append(f"Imports: {', '.join(metadata['imports'])}")
    if "exports" in metadata:
        lines.append(f"Exports: {', '.join(metadata['exports'])}")
    if "extends" in metadata:
        lines.append(f"Extends: {metadata['extends']}")
    if "inherits_from" in metadata:
        lines.append(f"Inherits_From: {metadata['inherits_from']}")
    if "composed_of" in metadata:
        lines.append(f"Composed_Of: {', '.join(metadata['composed_of'])}")
    if "implements_interface" in metadata:
        lines.append(f"Implements_Interface: {metadata['implements_interface']}")

    # Relationships
    if "supersedes" in metadata:
        lines.append(f"Supersedes: {metadata['supersedes']}")
    if "conflicts_with" in metadata:
        lines.append(f"Conflicts_With: {metadata['conflicts_with']}")
    if "migrates_from" in metadata:
        lines.append(f"Migrates_From: {metadata['migrates_from']}")
    if "prerequisite_of" in metadata:
        lines.append(f"Prerequisite_Of: {metadata['prerequisite_of']}")
    if "alternative_to" in metadata:
        lines.append(f"Alternative_To: {metadata['alternative_to']}")

    # Events & Exceptions
    if "raises" in metadata:
        lines.append(f"Raises: {', '.join(metadata['raises'])}")
    if "handles" in metadata:
        lines.append(f"Handles: {', '.join(metadata['handles'])}")
    if "emits" in metadata:
        lines.append(f"Emits: {', '.join(metadata['emits'])}")
    if "listens_to" in metadata:
        lines.append(f"Listens_To: {', '.join(metadata['listens_to'])}")

    # Issues & Planning
    if "requested_by" in metadata:
        lines.append(f"Requested_By: {metadata['requested_by']}")
    if "approved_by" in metadata:
        lines.append(f"Approved_By: {metadata['approved_by']}")
    if "roadmap" in metadata:
        lines.append(f"Roadmap: {metadata['roadmap']}")

    # Metadata
    if "tags" in metadata:
        lines.append(f"Tags: {', '.join(metadata['tags'])}")
    if "keywords" in metadata:
        lines.append(f"Keywords: {', '.join(metadata['keywords'])}")

    # Performance
    if "performance" in metadata:
        lines.append(f"Performance: {metadata['performance']}")
    if "benchmarks" in metadata:
        lines.append(f"Benchmarks: {metadata['benchmarks']}")

    # Security
    if "security" in metadata:
        lines.append(f"Security: {metadata['security']}")
    if "vulnerability_id" in metadata:
        lines.append(f"Vulnerability_ID: {metadata['vulnerability_id']}")

    # External
    if "pypi" in metadata:
        lines.append(f"PyPI: {metadata['pypi']}")
    if "github" in metadata:
        lines.append(f"GitHub: {metadata['github']}")
    if "stackoverflow" in metadata:
        lines.append(f"StackOverflow: {metadata['stackoverflow']}")

    # Warning
    if "warning" in metadata:
        lines.append("")
        lines.append("Warning:")
        lines.append(f"    {metadata['warning']}")

    return "\n".join(lines)


def update_module_docstring(file_path: Path):
    """Update a single module's docstring."""
    if not file_path.exists():
        return False

    # Read content
    with open(file_path) as f:
        content = f.read()

    # Check if already has State metadata
    if re.search(r'^State:', content, re.MULTILINE):
        return False

    # Infer metadata
    metadata = infer_metadata(file_path)
    if not metadata:
        return False

    # Find docstring pattern
    pattern = r'(# Standards:.*?\n""")(.*?)(""")'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        # Try alternate pattern (no Standards comment)
        pattern = r'^(""")(.*?)(""")'
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)

    if not match:
        print(f"⚠️  {file_path}: No docstring pattern found")
        return False

    # Generate metadata
    module_name = file_path.parent.name
    docstring_metadata = generate_simple_docstring(metadata, module_name)

    # Insert after opening """ and before existing content
    existing_content = match.group(2).strip()

    # If existing content is just a placeholder, replace it
    if existing_content in ["__init__ module.", "Module implementation.", ""]:
        new_docstring = docstring_metadata
    else:
        # Prepend metadata before existing content
        new_docstring = f"{docstring_metadata}\n\n{existing_content}"

    # Replace
    new_content = content.replace(
        match.group(0),
        f'{match.group(1)}{new_docstring}{match.group(3)}'
    )

    # Write back
    with open(file_path, 'w') as f:
        f.write(new_content)

    return True


def main():
    """Run batch metadata addition."""
    print("=" * 70)
    print("Batch Adding Inline Metadata to ALL Modules")
    print("=" * 70)
    print()

    # Find all __init__.py files
    init_files = list(PROJECT_ROOT.glob("src/pheno/**/__init__.py"))

    print(f"Found {len(init_files)} Python modules")
    print()

    updated = 0
    skipped = 0
    errors = 0

    for file_path in sorted(init_files):
        try:
            if update_module_docstring(file_path):
                print(f"✓ {file_path.relative_to(PROJECT_ROOT)}")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ {file_path.relative_to(PROJECT_ROOT)}: {e}")
            errors += 1

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped} (already have metadata)")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(init_files)}")
    print()

    if updated > 0:
        print("✅ Batch update complete!")
        print()
        print("Next steps:")
        print("  1. Run: ./scripts/verify_inline_metadata.sh")
        print("  2. Review: git diff src/pheno/")
        print("  3. Commit changes")


if __name__ == "__main__":
    main()
