"""Fix dict[str, object] -> dict[str, Any] across api/ files and ensure Any is imported."""

import re
import sys
from pathlib import Path

# Files to fix (excluding client.py and main.py which is already done)
FILES = [
    "src/tracertm/api/routers/specifications.py",
    "src/tracertm/api/routers/integrations.py",
    "src/tracertm/api/handlers/items.py",
    "src/tracertm/api/sync_client.py",
    "src/tracertm/api/routers/execution.py",
    "src/tracertm/api/handlers/github.py",
    "src/tracertm/api/routers/blockchain.py",
    "src/tracertm/api/handlers/chat.py",
    "src/tracertm/api/routers/health.py",
    "src/tracertm/api/routers/health_canary.py",
    "src/tracertm/api/routers/agent.py",
    "src/tracertm/api/routers/features.py",
    "src/tracertm/api/routers/contracts.py",
    "src/tracertm/api/routers/adrs.py",
    "src/tracertm/api/middleware/auth.py",
    "src/tracertm/api/handlers/oauth.py",
    "src/tracertm/api/routers/quality.py",
    "src/tracertm/api/deps.py",
    "src/tracertm/api/config/startup.py",
    "src/tracertm/api/routers/auth.py",
    "src/tracertm/api/http_client.py",
    "src/tracertm/api/handlers/links.py",
    "src/tracertm/api/handlers/integrations.py",
    "src/tracertm/api/config/rate_limiting.py",
]


def ensure_any_import(content: str) -> str:
    """Ensure Any is imported from typing."""
    # Check if Any is already imported
    if re.search(r'\bAny\b', content[:2000]):  # Check in first 2000 chars (imports area)
        # Check if it's actually imported (not just used)
        if re.search(r'from typing import.*\bAny\b', content) or re.search(r'import Any', content):
            return content

    # Try to add Any to existing typing import
    # Pattern: from typing import X, Y, Z
    pattern = r'(from typing import\s+)((?:\w+(?:\s*,\s*)?)+)'
    match = re.search(pattern, content)
    if match:
        existing = match.group(2).strip()
        imports = [x.strip() for x in existing.split(",")]
        if "Any" not in imports:
            imports.append("Any")
            imports.sort()
            new_import = match.group(1) + ", ".join(imports)
            content = content[:match.start()] + new_import + content[match.end():]
            return content

    # No existing typing import, add one after other imports
    # Find last import line
    lines = content.split("\n")
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_idx = i
        elif stripped and not stripped.startswith("#") and not stripped.startswith('"""') and last_import_idx > 0:
            break

    lines.insert(last_import_idx + 1, "from typing import Any")
    return "\n".join(lines)


total_replacements = 0
for filepath in FILES:
    path = Path(filepath)
    if not path.exists():
        print(f"SKIP (not found): {filepath}")
        continue

    content = path.read_text(encoding="utf-8")
    original = content

    # Count replacements
    count = content.count("dict[str, object]")
    if count > 0:
        content = content.replace("dict[str, object]", "dict[str, Any]")
        content = ensure_any_import(content)
        total_replacements += count

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"FIXED: {filepath} ({count} replacements)")
    else:
        print(f"SKIP (no changes): {filepath}")

print(f"\nTotal: {total_replacements} replacements across {len(FILES)} files")
