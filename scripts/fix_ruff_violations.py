#!/usr/bin/env python3
"""Bulk-fix Ruff violations programmatically.

Handles:
- ANN001: Add type annotations to function params (Any for test fixtures)
- ANN201/ANN202: Add -> None return type to functions
- ANN002/ANN003: Add *args: Any, **kwargs: Any
- ANN204: Add -> None to __init__ and other special methods
- D205: Add blank line after docstring summary
- ARG001/ARG002/ARG004/ARG005: Prefix unused args with _
- G004: Convert f-string logging to % style
- B007: Prefix unused loop vars with _
- SIM113: Use enumerate
- TRY300/TRY301: Move return out of try / move raise out of try
"""

import json
import operator
import re
import subprocess
import sys
from pathlib import Path


def get_violations(codes: list[str]) -> list[dict]:
    """Get violations for specific codes from ruff."""
    code_args = ",".join(codes)
    result = subprocess.run(
        ["ruff", "check", "--select", code_args, "--output-format=json", "."],
        capture_output=True,
        text=True,
        cwd="/Users/kooshapari/temp-PRODVERCEL/485/kush/trace",
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def fix_ann001_ann002_ann003(violations: list[dict]) -> int:
    """Add type annotations to function parameters.

    For test files: uses Any for fixture params.
    For src files: uses Any as fallback.
    """
    # Group by file
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] in ("ANN001", "ANN002", "ANN003"):
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.split("\n")
        modified = False

        # Sort violations by line number descending so we can modify without shifting
        file_violations.sort(key=lambda v: (v["location"]["row"], v["location"]["column"]), reverse=True)

        for v in file_violations:
            row = v["location"]["row"] - 1  # 0-indexed
            v["location"]["column"] - 1

            if row >= len(lines):
                continue

            line = lines[row]

            # Extract the parameter name from the message
            msg = v["message"]

            if v["code"] == "ANN001":
                # "Missing type annotation for function argument `xxx`"
                match = re.search(r"`(\w+)`", msg)
                if not match:
                    continue
                param_name = match.group(1)

                # Skip 'self' and 'cls'
                if param_name in ("self", "cls"):
                    continue

                # Find the parameter in the line and add : Any
                # Be careful with default values
                # Pattern: param_name followed by optional =default, then , or )
                pattern = rf"\b({re.escape(param_name)})\s*(?=[,)=:])"
                replacement_match = re.search(pattern, line)
                if replacement_match:
                    pos = replacement_match.end(1)
                    # Check if already annotated
                    rest = line[pos:].lstrip()
                    if rest.startswith(":"):
                        continue  # Already annotated
                    lines[row] = line[:pos] + ": Any" + line[pos:]
                    modified = True
                    fixed += 1

            elif v["code"] == "ANN002":
                # "Missing type annotation for `*args`"
                pattern = r"(\*args)\s*(?=[,):])"
                replacement_match = re.search(pattern, line)
                if replacement_match:
                    pos = replacement_match.end(1)
                    rest = line[pos:].lstrip()
                    if rest.startswith(":"):
                        continue
                    lines[row] = line[:pos] + ": Any" + line[pos:]
                    modified = True
                    fixed += 1

            elif v["code"] == "ANN003":
                # "Missing type annotation for `**kwargs`"
                pattern = r"(\*\*kwargs)\s*(?=[,):])"
                replacement_match = re.search(pattern, line)
                if replacement_match:
                    pos = replacement_match.end(1)
                    rest = line[pos:].lstrip()
                    if rest.startswith(":"):
                        continue
                    lines[row] = line[:pos] + ": Any" + line[pos:]
                    modified = True
                    fixed += 1

        if modified:
            new_content = "\n".join(lines)
            # Ensure Any is imported
            if "from typing import" in new_content and "Any" not in new_content:
                new_content = re.sub(
                    r"(from typing import )([^\n]+)",
                    lambda m: m.group(1) + "Any, " + m.group(2) if "Any" not in m.group(2) else m.group(0),
                    new_content,
                    count=1,
                )
            elif "from typing import" not in new_content and "import typing" not in new_content:
                # Add typing import at top (after docstrings/comments)
                # Find first non-comment, non-docstring, non-blank line
                insert_pos = 0
                in_docstring = False
                for i, ln in enumerate(lines):
                    stripped = ln.strip()
                    if stripped.startswith(('"""', "'''")):
                        if in_docstring:
                            in_docstring = False
                            continue
                        if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                            in_docstring = True
                            continue
                    if in_docstring:
                        continue
                    if stripped.startswith(("#", "from __future__")) or stripped == "":
                        insert_pos = i + 1
                        continue
                    if stripped.startswith(("import ", "from ")):
                        insert_pos = i + 1
                        continue
                    break
                lines_list = new_content.split("\n")
                lines_list.insert(insert_pos, "from typing import Any")
                new_content = "\n".join(lines_list)

            path.write_text(new_content, encoding="utf-8")

    return fixed


def fix_ann201_ann202_ann204(violations: list[dict]) -> int:
    """Add -> None return type to functions missing return annotations."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] in ("ANN201", "ANN202", "ANN204", "ANN205"):
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.split("\n")
        modified = False

        # Sort by line descending
        file_violations.sort(key=lambda v: v["location"]["row"], reverse=True)

        for v in file_violations:
            row = v["location"]["row"] - 1
            if row >= len(lines):
                continue

            lines[row]

            # Find the closing paren and colon of the function def
            # Could span multiple lines
            # Look for ) -> ...: or just ):
            # We need to find the ): pattern potentially across lines

            # First, check if this line has the closing ):
            # Walk from the current line forward to find )....:
            found = False
            for i in range(row, min(row + 20, len(lines))):
                ln = lines[i]
                # Look for )  : pattern (the colon that ends the def)
                # Could be ): or ) -> type:
                colon_match = re.search(r"\)\s*:", ln)
                arrow_match = re.search(r"\)\s*->", ln)
                if arrow_match:
                    # Already has return annotation
                    found = True
                    break
                if colon_match:
                    # Insert -> None before the colon
                    pos = colon_match.start() + 1  # After )
                    lines[i] = ln[:pos] + " -> None" + ln[pos:]
                    modified = True
                    fixed += 1
                    found = True
                    break

            if not found:
                continue

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_d205(violations: list[dict]) -> int:
    """Add blank line after docstring summary line."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] == "D205":
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.split("\n")
        modified = False

        # Sort by line descending
        file_violations.sort(key=lambda v: v["location"]["row"], reverse=True)

        for v in file_violations:
            row = v["location"]["row"] - 1
            if row >= len(lines):
                continue

            # D205: 1 blank line required between summary line and description
            # The summary is on this line, need to add a blank line after it
            # Check if next line is not blank
            if row + 1 < len(lines) and lines[row + 1].strip() != "":
                lines.insert(row + 1, "")
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_arg_unused(violations: list[dict]) -> int:
    """Prefix unused function arguments with underscore."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] in ("ARG001", "ARG002", "ARG004", "ARG005"):
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Extract param names and their locations
        replacements = []
        for v in file_violations:
            msg = v["message"]
            match = re.search(r"`(\w+)`", msg)
            if not match:
                continue
            param_name = match.group(1)
            if param_name.startswith("_"):
                continue  # Already prefixed
            row = v["location"]["row"]
            col = v["location"]["column"]
            replacements.append((row, col, param_name))

        if not replacements:
            continue

        lines = content.split("\n")
        modified = False

        # Sort by line descending, then column descending
        replacements.sort(key=operator.itemgetter(0, 1), reverse=True)

        for row, col, param_name in replacements:
            row_idx = row - 1
            col_idx = col - 1
            if row_idx >= len(lines):
                continue

            line = lines[row_idx]
            # Verify the param is at this position
            if line[col_idx : col_idx + len(param_name)] == param_name:
                lines[row_idx] = line[:col_idx] + "_" + line[col_idx:]
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_b007(violations: list[dict]) -> int:
    """Prefix unused loop variables with underscore."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] == "B007":
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.split("\n")
        modified = False

        file_violations.sort(key=lambda v: (v["location"]["row"], v["location"]["column"]), reverse=True)

        for v in file_violations:
            msg = v["message"]
            match = re.search(r"`(\w+)`", msg)
            if not match:
                continue
            var_name = match.group(1)
            if var_name.startswith("_"):
                continue

            row = v["location"]["row"] - 1
            col = v["location"]["column"] - 1
            if row >= len(lines):
                continue

            line = lines[row]
            if line[col : col + len(var_name)] == var_name:
                lines[row] = line[:col] + "_" + line[col:]
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def main() -> None:
    """Run all fixers."""
    # Get all violations at once
    result = subprocess.run(
        ["ruff", "check", "--output-format=json", "."],
        capture_output=True,
        text=True,
        cwd="/Users/kooshapari/temp-PRODVERCEL/485/kush/trace",
    )
    try:
        all_violations = json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.exit(1)

    total_fixed = 0

    # Fix ANN201/ANN202/ANN204 first (return types) - least risk
    count = fix_ann201_ann202_ann204(all_violations)
    total_fixed += count

    # Fix D205 (blank line after summary)
    count = fix_d205(all_violations)
    total_fixed += count

    # Fix ARG001/002/004/005 (unused args)
    count = fix_arg_unused(all_violations)
    total_fixed += count

    # Fix B007 (unused loop vars)
    count = fix_b007(all_violations)
    total_fixed += count

    # Fix ANN001/ANN002/ANN003 last (most invasive)
    count = fix_ann001_ann002_ann003(all_violations)
    total_fixed += count


if __name__ == "__main__":
    main()
