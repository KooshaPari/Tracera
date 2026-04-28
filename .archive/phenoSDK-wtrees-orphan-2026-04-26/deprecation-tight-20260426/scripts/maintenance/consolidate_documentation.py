#!/usr/bin/env python3
"""
Documentation Consolidation Script

Moves fragmented root-level documentation files to organized subdirectories.
Preserves git history by not deleting files, but moving them to archive.

Run: python consolidate_documentation.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import re

def get_file_date(filepath):
    """Get file modification date for archiving."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime("%Y%m%d")
    except:
        return datetime.now().strftime("%Y%m%d")

def consolidate_docs():
    """Main consolidation function."""
    root = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk")
    docs = root / "docs"

    # Ensure directories exist
    dirs = [docs / "phases", docs / "sessions", docs / "audits",
            docs / "summaries", docs / "guides", docs / "blueprints",
            docs / "archive"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Files to keep in root (core repo files)
    keep_root = {"README.md", "CONTRIBUTING.md", "DEVELOPMENT.md",
                 "CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "LICENSE"}

    # Track moves
    moves = {}

    print("🔄 Starting Documentation Consolidation...\n")

    # 1. Phase files → docs/phases/ (keep only consolidated PHASE_N_* files)
    print("📦 Processing Phase files...")
    phase_files = sorted(root.glob("PHASE*.md"))

    consolidated_phases = set()

    # Mark consolidated phases to keep
    for f in phase_files:
        if re.match(r"PHASE_\d+_[A-Z_]+\.md$", f.name):
            consolidated_phases.add(f.name)
            print(f"  ✓ Keep consolidated: {f.name}")

    # Archive others
    for f in phase_files:
        if f.name not in consolidated_phases:
            date = get_file_date(f)
            new_name = f"ARCHIVE_{date}_{f.name}"
            dest = docs / "archive" / new_name
            shutil.copy2(f, dest)
            moves[str(f)] = str(dest)
            print(f"  → Archive: {f.name} → {new_name}")

    # 2. Docstring files → docs/guides/GUIDE_DOCSTRINGS.md
    print("\n📦 Processing Docstring files...")
    docstring_files = list(root.glob("DOCSTRING_*.md"))
    if docstring_files:
        print(f"  Found {len(docstring_files)} docstring files to consolidate")
        for f in docstring_files:
            date = get_file_date(f)
            new_name = f"ARCHIVE_{date}_{f.name}"
            dest = docs / "archive" / new_name
            shutil.copy2(f, dest)
            moves[str(f)] = str(dest)
            print(f"  → Archive: {f.name}")

    # 3. Session files → docs/sessions/
    print("\n📦 Processing Session files...")
    session_files = list(root.glob("*SESSION*.md"))
    for f in session_files:
        # Extract date if present
        new_name = f.name
        dest = docs / "sessions" / new_name
        if not dest.exists():
            shutil.copy2(f, dest)
            moves[str(f)] = str(dest)
            print(f"  → Move: {f.name} → sessions/")

    # 4. Audit files → docs/audits/
    print("\n📦 Processing Audit files...")
    audit_files = list(root.glob("*AUDIT*.md"))
    for f in audit_files:
        new_name = f.name
        dest = docs / "audits" / new_name
        if not dest.exists():
            shutil.copy2(f, dest)
            moves[str(f)] = str(dest)
            print(f"  → Move: {f.name} → audits/")

    # 5. Summary/Final/Status files
    print("\n📦 Processing Summary, Final, and Status files...")

    summary_patterns = [
        ("*SUMMARY*.md", "summaries"),
        ("FINAL_*.md", "summaries"),
        ("BUILD_*.md", "summaries"),
        ("*COMPLETE*.md", "blueprints"),
        ("*STATUS*.md", "blueprints"),
        ("*COMPLETION*.md", "blueprints"),
        ("*READY*.md", "blueprints"),
    ]

    for pattern, target_dir in summary_patterns:
        files = list(root.glob(pattern))
        for f in files:
            if f.name in keep_root:
                continue
            new_name = f.name
            dest = docs / target_dir / new_name
            if not dest.exists():
                shutil.copy2(f, dest)
                moves[str(f)] = str(dest)
                print(f"  → Move: {f.name} → {target_dir}/")

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Documentation Consolidation Complete!")
    print(f"{'='*60}")
    print(f"\nCopied {len(moves)} files:")
    print(f"  • Phase files → docs/phases/")
    print(f"  • Session files → docs/sessions/")
    print(f"  • Audit files → docs/audits/")
    print(f"  • Summary files → docs/summaries/")
    print(f"  • Blueprint files → docs/blueprints/")
    print(f"  • Old files → docs/archive/ (with ARCHIVE_ prefix)")

    print(f"\n📌 Next Steps:")
    print(f"  1. Review moved files: git status")
    print(f"  2. Update links in docs/INDEX.md")
    print(f"  3. Update README.md with new structure")
    print(f"  4. Test site: uv run python -m pheno_sdk.cli docs")
    print(f"  5. Commit: git add docs/ && git commit -m 'docs: consolidate fragmented docs to organized structure'")

    return moves

if __name__ == "__main__":
    import sys

    try:
        moves = consolidate_docs()
        print("\n✨ Script completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
