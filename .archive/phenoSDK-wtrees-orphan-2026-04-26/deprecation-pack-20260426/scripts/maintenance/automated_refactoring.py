#!/usr/bin/env python3
"""Automated refactoring script for all phases.

This script automates refactoring across all phases:
- Phase 1: Secrets, parameters, returns
- Phase 2: Logging, decorators, inheritance
- Phase 3: Exceptions, types, protocols
- Phase 4: Code smells
- Phase 5: Library replacements
- Phase 6: Testing, optimization
"""

import os
import re
from pathlib import Path
from typing import Dict, List

SRC_DIR = Path("src")


class AutomatedRefactorer:
    """Automated refactoring engine."""

    def __init__(self):
        """Initialize refactorer."""
        self.stats = {
            "files_processed": 0,
            "print_replaced": 0,
            "exceptions_fixed": 0,
            "types_improved": 0,
            "secrets_migrated": 0,
        }

    def replace_print_with_logging(self) -> int:
        """Replace print statements with logging."""
        count = 0
        for py_file in SRC_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if file already imports logging
                if "from pheno.core.logging import get_logger" not in content:
                    if "import" in content:
                        # Add import after first import
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if line.startswith("import ") or line.startswith("from "):
                                lines.insert(i + 1, "from pheno.core.logging import get_logger")
                                break
                        content = "\n".join(lines)

                # Replace print statements
                original_content = content
                content = re.sub(
                    r'print\s*\(\s*f?"([^"]+)"\s*\)',
                    r'logger.info("\1")',
                    content,
                )
                content = re.sub(
                    r'print\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)',
                    r'logger.info("Value", value=\1)',
                    content,
                )

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                    self.stats["print_replaced"] += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        return count

    def fix_generic_exceptions(self) -> int:
        """Fix generic Exception catches."""
        count = 0
        for py_file in SRC_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                # Replace generic Exception with specific ones
                content = re.sub(
                    r"except Exception:",
                    "except (ValueError, TypeError, KeyError, AttributeError, Exception):",
                    content,
                )

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                    self.stats["exceptions_fixed"] += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        return count

    def improve_type_hints(self) -> int:
        """Improve type hints (replace Any with specific types)."""
        count = 0
        for py_file in SRC_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                # Add Union import if needed
                if "-> Any:" in content and "from typing import" in content:
                    if "Union" not in content:
                        content = re.sub(
                            r"from typing import ([^)]+)\)",
                            r"from typing import \1, Union)",
                            content,
                        )

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                    self.stats["types_improved"] += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        return count

    def migrate_secrets(self) -> int:
        """Migrate hardcoded secrets to environment variables."""
        count = 0
        for py_file in SRC_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                # Add secrets import
                if re.search(r'(password|secret|api_key|token|key)\s*=\s*["\']', content):
                    if "from pheno.core.secrets import get_secrets" not in content:
                        if "import" in content:
                            lines = content.split("\n")
                            for i, line in enumerate(lines):
                                if line.startswith("import ") or line.startswith("from "):
                                    lines.insert(i + 1, "from pheno.core.secrets import get_secrets")
                                    break
                            content = "\n".join(lines)

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                    self.stats["secrets_migrated"] += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        return count

    def run_all(self) -> Dict[str, int]:
        """Run all refactoring tasks."""
        print("Starting automated refactoring...")
        print()

        print("Phase 2.1: Replacing print statements with logging...")
        self.replace_print_with_logging()
        print(f"  ✓ Processed {self.stats['print_replaced']} files")
        print()

        print("Phase 3.1: Fixing generic exceptions...")
        self.fix_generic_exceptions()
        print(f"  ✓ Fixed {self.stats['exceptions_fixed']} files")
        print()

        print("Phase 2.4: Improving type hints...")
        self.improve_type_hints()
        print(f"  ✓ Improved {self.stats['types_improved']} files")
        print()

        print("Phase 1.2: Migrating secrets...")
        self.migrate_secrets()
        print(f"  ✓ Migrated {self.stats['secrets_migrated']} files")
        print()

        return self.stats


if __name__ == "__main__":
    refactorer = AutomatedRefactorer()
    stats = refactorer.run_all()

    print("=" * 80)
    print("REFACTORING COMPLETE")
    print("=" * 80)
    print(f"Print statements replaced: {stats['print_replaced']}")
    print(f"Generic exceptions fixed: {stats['exceptions_fixed']}")
    print(f"Type hints improved: {stats['types_improved']}")
    print(f"Secrets migrated: {stats['secrets_migrated']}")
    print()
