#!/usr/bin/env python3
"""Pre-commit hook to quickly check cross-link integrity.

Performs fast validation without full extraction.

State: STABLE
Since: 0.3.0
"""

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent


def quick_check():
    """Quick check of cross-link database."""
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"

    if not db_path.exists():
        print("⚠️  Cross-link database not found")
        print("   Run: python scripts/extract_cross_links.py")
        return 1

    try:
        with open(db_path) as f:
            db = json.load(f)

        # Quick validation
        total_modules = len(db.get("modules", {}))
        total_tests = len(db.get("tests", {}))
        total_docs = len(db.get("docs", {}))

        print(f"✅ Cross-link database exists:")
        print(f"   - {total_modules} modules")
        print(f"   - {total_tests} tests")
        print(f"   - {total_docs} docs")

        # Check if database is recent
        import os
        import time
        mtime = os.path.getmtime(db_path)
        age_hours = (time.time() - mtime) / 3600

        if age_hours > 24:
            print(f"⚠️  Database is {age_hours:.1f} hours old")
            print("   Consider regenerating: python scripts/extract_cross_links.py")
            return 1

        return 0

    except Exception as e:
        print(f"❌ Error reading cross-link database: {e}")
        return 1


def main():
    """Run quick cross-link check."""
    return quick_check()


if __name__ == "__main__":
    sys.exit(main())
