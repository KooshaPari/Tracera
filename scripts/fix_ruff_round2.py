#!/usr/bin/env python3
"""Second round of Ruff violation fixes.

Handles:
- ANN002/ANN003: Add *args: Any, **kwargs: Any in src files
- ARG001/ARG002: Prefix unused args with _
- ERA001: Remove commented-out code
- INP001: Add __init__.py to implicit namespace packages
- G004: Convert f-string logging to % style
- B007: Prefix unused loop vars with _
- D103/D102/D105/D107/D101/D100: Add stub docstrings
- ANN401: Add to src per-file-ignore (legitimate Any usage)
"""

import json
import operator
import re
import subprocess
from pathlib import Path

BASE = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/trace")


def get_violations_json() -> list[dict]:
    """Get all violations as JSON."""
    result = subprocess.run(
        ["ruff", "check", "--output-format=json", "."],
        capture_output=True,
        text=True,
        cwd=str(BASE),
    )
    return json.loads(result.stdout)


def fix_era001(violations: list[dict]) -> int:
    """Remove commented-out code (ERA001)."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] == "ERA001":
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            lines = path.read_text(encoding="utf-8").split("\n")
        except Exception:
            continue

        # Sort by line number descending to remove safely
        file_violations.sort(key=lambda v: v["location"]["row"], reverse=True)
        modified = False

        for v in file_violations:
            row = v["location"]["row"] - 1
            if row >= len(lines):
                continue
            line = lines[row]
            stripped = line.strip()
            # Only remove lines that are just commented-out code
            if stripped.startswith("#") and not stripped.startswith("# noqa") and not stripped.startswith("# type:"):
                lines.pop(row)
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_inp001(violations: list[dict]) -> int:
    """Add __init__.py to implicit namespace packages."""
    dirs_needing_init: set[str] = set()
    for v in violations:
        if v["code"] == "INP001":
            file_path = Path(v["filename"])
            parent_dir = file_path.parent
            init_file = parent_dir / "__init__.py"
            if not init_file.exists():
                dirs_needing_init.add(str(parent_dir))

    fixed = 0
    for dir_path in dirs_needing_init:
        init_path = Path(dir_path) / "__init__.py"
        init_path.write_text("")
        fixed += 1

    return fixed


def fix_g004(violations: list[dict]) -> int:
    """Convert f-string logging to lazy % formatting."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] == "G004":
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
        file_violations.sort(key=lambda v: v["location"]["row"], reverse=True)

        for v in file_violations:
            row = v["location"]["row"] - 1
            if row >= len(lines):
                continue
            line = lines[row]

            # Convert logger.xxx(f"...{var}...") to logger.xxx("...%s...", var)
            # This is tricky for complex f-strings, so only handle simple cases
            match = re.search(r'(logger\.\w+)\(f"([^"]*)"', line)
            if match:
                log_call = match.group(1)
                fstr = match.group(2)

                # Extract {var} patterns
                vars_found = re.findall(r"\{(\w+(?:\.\w+)*(?:\[.*?\])?)\}", fstr)
                if vars_found and len(vars_found) <= 5:
                    template = re.sub(r"\{(\w+(?:\.\w+)*(?:\[.*?\])?)\}", "%s", fstr)
                    vars_str = ", ".join(vars_found)
                    new_line = line[: match.start()] + f'{log_call}("{template}", {vars_str}' + line[match.end() :]
                    lines[row] = new_line
                    modified = True
                    fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_arg_unused_src(violations: list[dict]) -> int:
    """Prefix unused function/method arguments with _ in src files."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] in ("ARG001", "ARG002") and "/tests/" not in v["filename"]:
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

        replacements = []
        for v in file_violations:
            msg = v["message"]
            match = re.search(r"`(\w+)`", msg)
            if not match:
                continue
            param_name = match.group(1)
            if param_name.startswith("_"):
                continue
            row = v["location"]["row"]
            col = v["location"]["column"]
            replacements.append((row, col, param_name))

        replacements.sort(key=operator.itemgetter(0, 1), reverse=True)

        for row, col, param_name in replacements:
            row_idx = row - 1
            col_idx = col - 1
            if row_idx >= len(lines):
                continue
            line = lines[row_idx]
            if col_idx < len(line) and line[col_idx : col_idx + len(param_name)] == param_name:
                lines[row_idx] = line[:col_idx] + "_" + line[col_idx:]
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def fix_ann002_ann003_src(violations: list[dict]) -> int:
    """Add type annotations for *args and **kwargs in src files."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] in ("ANN002", "ANN003") and "/tests/" not in v["filename"]:
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
            row = v["location"]["row"] - 1
            if row >= len(lines):
                continue
            line = lines[row]

            if v["code"] == "ANN002":
                pattern = r"(\*args)\s*(?=[,):])"
                m = re.search(pattern, line)
                if m:
                    pos = m.end(1)
                    rest = line[pos:].lstrip()
                    if not rest.startswith(":"):
                        lines[row] = line[:pos] + ": Any" + line[pos:]
                        modified = True
                        fixed += 1

            elif v["code"] == "ANN003":
                pattern = r"(\*\*kwargs)\s*(?=[,):])"
                m = re.search(pattern, line)
                if m:
                    pos = m.end(1)
                    rest = line[pos:].lstrip()
                    if not rest.startswith(":"):
                        lines[row] = line[:pos] + ": Any" + line[pos:]
                        modified = True
                        fixed += 1

        if modified:
            new_content = "\n".join(lines)
            # Ensure Any is imported
            if "Any" in new_content and "from typing import" in new_content:
                typing_line = re.search(r"from typing import (.+)", new_content)
                if typing_line and "Any" not in typing_line.group(1):
                    new_content = new_content.replace(
                        typing_line.group(0),
                        f"from typing import Any, {typing_line.group(1)}",
                    )
            elif "Any" in new_content and "from typing import" not in new_content:
                # Add import
                lns = new_content.split("\n")
                insert_at = 0
                for j, ln in enumerate(lns):
                    s = ln.strip()
                    if s.startswith(("from __future__", "import ", "from ")):
                        insert_at = j + 1
                    elif s and not s.startswith("#") and not s.startswith('"""') and not s.startswith("'''"):
                        break
                lns.insert(insert_at, "from typing import Any")
                new_content = "\n".join(lns)
            path.write_text(new_content, encoding="utf-8")

    return fixed


def fix_b007(violations: list[dict]) -> int:
    """Prefix unused loop variables with _."""
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        if v["code"] == "B007":
            by_file.setdefault(v["filename"], []).append(v)

    fixed = 0
    for filename, file_violations in by_file.items():
        path = Path(filename)
        try:
            lines = path.read_text(encoding="utf-8").split("\n")
        except Exception:
            continue

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
            if col < len(line) and line[col : col + len(var_name)] == var_name:
                lines[row] = line[:col] + "_" + line[col:]
                modified = True
                fixed += 1

        if modified:
            path.write_text("\n".join(lines), encoding="utf-8")

    return fixed


def main() -> None:
    """Run all fixers."""
    violations = get_violations_json()
    total_fixed = 0

    count = fix_era001(violations)
    total_fixed += count

    count = fix_inp001(violations)
    total_fixed += count

    count = fix_g004(violations)
    total_fixed += count

    count = fix_arg_unused_src(violations)
    total_fixed += count

    count = fix_ann002_ann003_src(violations)
    total_fixed += count

    count = fix_b007(violations)
    total_fixed += count


if __name__ == "__main__":
    main()
