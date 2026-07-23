#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
config="$root/deploy/oracle-isolated/conf.d/tracertm.conf"

[[ -f "$config" ]] || { echo "routing policy config missing" >&2; exit 1; }

python3 - "$config" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
blocked = text.index("location ~ ^/api/v1/(graph|search|traceability)")
go = text.index("location ~ ^/api/v1/(items|links|projects|graph|bulk")
assert blocked < go, "fail-closed location must precede broad Go proxy"
assert "return 503" in text[blocked:go], "unowned domains must fail closed"
assert 'Cache-Control "no-store"' in text[blocked:go]
print("oracle routing policy passed")
PY
