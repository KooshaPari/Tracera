"""auto_update_loc module."""

import sys
from pathlib import Path

# Paths to the quality tools
quality_script = Path("scripts/quality/check_file_loc.py")
allowlist_file = Path("config/loc-allowlist.txt")


def update_allowlist() -> None:
    """Update allowlist."""
    import subprocess

    # Run the quality check script and capture its output
    try:
        result = subprocess.run(
            [sys.executable, str(quality_script)],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return

    output = result.stdout

    # Parse violations from the output
    # or "  - 1661:frontend/apps/web/src/hooks/useSpecifications.api.ts"
    violations = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("- "):
            parts = line[2:].split(":")
            if len(parts) >= 2:
                loc = int(parts[0].replace("\033[1;33m", "").replace("\033[0m", ""))
                path = parts[1].split(" ")[0].strip()
                violations[path] = loc

    if not violations:
        return

    # Read existing allowlist
    current_allowlist = {}
    if allowlist_file.exists():
        for line in allowlist_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                current_allowlist[parts[0]] = int(parts[1])

    # Update allowlist with current values for violations
    current_allowlist.update(dict(violations.items()))

    # Sort and write back
    lines = [f"{path} {current_allowlist[path]}" for path in sorted(current_allowlist.keys())]

    allowlist_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    update_allowlist()
