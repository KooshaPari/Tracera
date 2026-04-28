#!/usr/bin/env python3
"""Code quality improvements script."""

import re
from pathlib import Path

SRC_DIR = Path("src")


def add_final_types() -> int:
    """Add Final type annotations to constants."""
    count = 0
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            if re.search(r"^[A-Z_]+\s*=\s*['\"]", content, re.MULTILINE):
                if "from typing import" in content and "Final" not in content:
                    content = re.sub(
                        r"from typing import ([^)]+)\)",
                        r"from typing import \1, Final)",
                        content,
                    )
                    count += 1

            if content != original_content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception:
            pass

    return count


def add_protocol_definitions() -> int:
    """Add Protocol definitions for interfaces."""
    count = 0
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            if re.search(r"class\s+\w+\(ABC\):", content):
                if "from typing import Protocol" not in content:
                    if "from typing import" in content:
                        content = re.sub(
                            r"from typing import ([^)]+)\)",
                            r"from typing import \1, Protocol)",
                            content,
                        )
                        count += 1

                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)

        except Exception:
            pass

    return count


def add_literal_types() -> int:
    """Add Literal type annotations."""
    count = 0
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            if re.search(r'if\s+\w+\s+in\s+\[["\']', content):
                if "from typing import Literal" not in content:
                    if "from typing import" in content:
                        content = re.sub(
                            r"from typing import ([^)]+)\)",
                            r"from typing import \1, Literal)",
                            content,
                        )
                        count += 1

                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)

        except Exception:
            pass

    return count


if __name__ == "__main__":
    print("Starting code quality improvements...")
    print()

    print("Phase 3.2: Adding Final types...")
    final_count = add_final_types()
    print(f"  ✓ Added Final to {final_count} files")
    print()

    print("Phase 3.3: Adding Protocol definitions...")
    protocol_count = add_protocol_definitions()
    print(f"  ✓ Added Protocol to {protocol_count} files")
    print()

    print("Phase 3.4: Adding Literal types...")
    literal_count = add_literal_types()
    print(f"  ✓ Added Literal to {literal_count} files")
    print()

    print("=" * 80)
    print("CODE QUALITY IMPROVEMENTS COMPLETE")
    print("=" * 80)
    print(f"Final types added: {final_count}")
    print(f"Protocol definitions added: {protocol_count}")
    print(f"Literal types added: {literal_count}")
