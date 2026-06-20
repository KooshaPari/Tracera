#!/usr/bin/env python3
"""Script to fix all database session patterns in integration tests.

Replaces:
    db = temp_env["db"]
    with Session(db.engine) as session:

With:
    with refresh_db_session(temp_env) as session:
"""

from pathlib import Path

# Read the test file
test_file = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/cli/test_cli_integration.py")
content = test_file.read_text(encoding="utf-8")

# Pattern 1: db = temp_env["db"] followed by with Session(db.engine) on next or nearby line
# Replace with: with refresh_db_session(temp_env) as session:

# Find all patterns where we get db then use it in Session
# We need to be careful not to break the helper function itself or fixture
lines = content.split("\n")
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Skip the helper function definition and fixture
    if "def refresh_db_session" in line or "def temp_env" in line:
        new_lines.append(line)
        i += 1
        continue

    # Check if this line has db = temp_env["db"] pattern
    if 'db = temp_env["db"]' in line and "def " not in line:
        # Look ahead for Session(db.engine) pattern within next 3 lines
        found_session = False
        lines_to_skip = 0

        for j in range(i + 1, min(i + 4, len(lines))):
            if "with Session(db.engine) as session:" in lines[j]:
                found_session = True
                lines_to_skip = j - i
                break

        if found_session:
            # Skip the db = temp_env["db"] line
            # Keep any lines in between
            new_lines.extend(
                lines[k]
                for k in range(i + 1, i + lines_to_skip)
                if lines[k].strip() and not lines[k].strip().startswith("#")
            )

            # Replace with refresh_db_session
            indent = len(lines[i + lines_to_skip]) - len(lines[i + lines_to_skip].lstrip())
            new_lines.append(" " * indent + "with refresh_db_session(temp_env) as session:")
            i = i + lines_to_skip + 1
            continue

    new_lines.append(line)
    i += 1

# Write back
new_content = "\n".join(new_lines)
test_file.write_text(new_content, encoding="utf-8")
