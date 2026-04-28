#!/usr/bin/env python3
"""Batch add frontmatter to ALL MDX files."""

import re
from pathlib import Path
from typing import Dict, Optional
import yaml

PROJECT_ROOT = Path(__file__).parent.parent


def infer_mdx_metadata(mdx_path: Path) -> Optional[Dict]:
    """Infer metadata based on MDX file path."""
    path_str = str(mdx_path.relative_to(PROJECT_ROOT))

    # Base metadata
    metadata = {
        "state": "STABLE",
        "tags": [],
    }

    # Infer from path
    if "/specs/" in path_str:
        metadata["tags"].extend(["specification", "technical"])
    elif "/api/" in path_str:
        metadata["tags"].extend(["api", "reference"])
    elif "/guides/" in path_str:
        metadata["tags"].extend(["guide", "tutorial"])
    elif "/getting-started/" in path_str:
        metadata["tags"].extend(["getting-started", "beginner"])
        metadata["state"] = "STABLE"
    elif "/kits/" in path_str:
        metadata["tags"].extend(["kit", "module"])
        metadata["state"] = "STABLE"
    elif "/architecture/" in path_str:
        metadata["tags"].extend(["architecture", "design"])
    elif "/examples/" in path_str:
        metadata["tags"].extend(["example", "tutorial"])
    elif "/contributing/" in path_str:
        metadata["tags"].extend(["contributing", "development"])
    elif "/deployment/" in path_str:
        metadata["tags"].extend(["deployment", "operations"])
    elif "/development/" in path_str:
        metadata["tags"].extend(["development", "internal"])
    elif "/stories/" in path_str:
        metadata["tags"].extend(["user-story", "requirements"])
    elif "/security/" in path_str:
        metadata["tags"].extend(["security"])
    elif "/troubleshooting/" in path_str:
        metadata["tags"].extend(["troubleshooting", "help"])

    return metadata


def add_or_update_frontmatter(file_path: Path):
    """Add or update YAML frontmatter in MDX file."""
    if not file_path.exists():
        return False

    with open(file_path) as f:
        content = f.read()

    # Infer metadata
    new_metadata = infer_mdx_metadata(file_path)
    if not new_metadata:
        return False

    # Check if has frontmatter
    if content.startswith('---'):
        # Find end of frontmatter
        end_idx = content.find('\n---\n', 3)
        if end_idx == -1:
            end_idx = content.find('\n---', 3)
            if end_idx == -1:
                return False

        # Parse existing frontmatter
        try:
            existing_fm = yaml.safe_load(content[3:end_idx])
            if existing_fm is None:
                existing_fm = {}
        except yaml.YAMLError:
            return False

        body = content[end_idx + 4:]

        # Only add missing keys (don't override existing)
        for key, value in new_metadata.items():
            if key not in existing_fm:
                existing_fm[key] = value
            elif key == "tags" and isinstance(value, list):
                # Merge tags
                existing_tags = existing_fm.get("tags", [])
                if isinstance(existing_tags, list):
                    existing_fm["tags"] = list(set(existing_tags + value))

        # Write back
        new_fm = yaml.dump(existing_fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_fm}---{body}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        return True
    else:
        # Add new frontmatter
        new_fm = yaml.dump(new_metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_fm}---\n\n{content}"

        with open(file_path, 'w') as f:
            f.write(new_content)

        return True


def main():
    """Run batch MDX frontmatter addition."""
    print("=" * 70)
    print("Batch Adding Frontmatter to ALL MDX Files")
    print("=" * 70)
    print()

    # Find all MDX files
    mdx_files = list(PROJECT_ROOT.glob("apps/docs/content/docs/**/*.mdx"))

    print(f"Found {len(mdx_files)} MDX files")
    print()

    updated = 0
    skipped = 0
    errors = 0

    for file_path in sorted(mdx_files):
        try:
            if add_or_update_frontmatter(file_path):
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
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(mdx_files)}")
    print()

    if updated > 0:
        print("✅ Batch MDX frontmatter update complete!")
        print()
        print("Next steps:")
        print("  1. Run: ./scripts/verify_inline_metadata.sh")
        print("  2. Review: git diff apps/docs/")
        print("  3. Build docs: cd apps/docs && npm run build")


if __name__ == "__main__":
    main()
