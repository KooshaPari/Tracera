#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

script = Path("scripts/install-local-runtime.sh").read_text(encoding="utf-8")

assert 'bun --cwd "$repo_root/frontend/apps/desktop" run build' not in script, (
    "installer must not use Bun's invalid global --cwd invocation"
)
assert '(\n  cd "$repo_root/frontend/apps/desktop"\n  bun run build\n)' in script, (
    "installer must build the desktop bundle from its package directory"
)
assert 'app_src="$repo_root/frontend/apps/desktop/build/dev-macos-arm64/Tracera.app"' in script, (
    "installer must consume the postbundle-normalized Tracera.app artifact"
)
assert 'Tracera-dev.app' not in script, "installer must not reference the pre-postbundle artifact"
postbundle = Path("frontend/apps/desktop/scripts/postbundle.ts").read_text(encoding="utf-8")
assert 'const FRONTEND_DIST = join(REPO_ROOT, "frontend", "dist");' in postbundle, (
    "postbundle must locate the canonical frontend dist output"
)
assert 'cpSync(FRONTEND_DIST, resources, { recursive: true, force: true });' in postbundle, (
    "postbundle must stage frontend/dist into app Resources"
)
print("local runtime installer command/artifact contract: PASS")
PY
