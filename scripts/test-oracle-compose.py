#!/usr/bin/env python3
"""Regression checks for the disposable oracle's host-boundary overlay.

This test is intentionally dependency-free and does not contact Docker.  The
overlay is the security boundary: every published dependency port must be
loopback-only, while the backend network remains internal in Compose.
"""

from pathlib import Path
import importlib.util
import re
import sys
import tempfile


VALIDATOR_PATH = Path(__file__).resolve().with_name("validate-oracle-compose.py")
VALIDATOR_SPEC = importlib.util.spec_from_file_location("oracle_compose_validator", VALIDATOR_PATH)
if VALIDATOR_SPEC is None or VALIDATOR_SPEC.loader is None:
    raise RuntimeError(f"could not load validator module: {VALIDATOR_PATH}")
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = VALIDATOR_MODULE
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)
validate_checkout = VALIDATOR_MODULE.validate_checkout


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "deploy" / "oracle-isolated" / "docker-compose.override.yml"
EXPECTED = {
    "127.0.0.1:18000:80",
    "127.0.0.1:18081:8080",
    "127.0.0.1:18080:8000",
    "127.0.0.1:15432:5432",
    "127.0.0.1:16379:6379",
    "127.0.0.1:14222:4222",
}


def main() -> int:
    text = OVERLAY.read_text(encoding="utf-8")
    published = set(re.findall(r'"([^"\n]+:[^"\n]+:[^"\n]+)"', text))
    if published != EXPECTED:
        missing = sorted(EXPECTED - published)
        unexpected = sorted(published - EXPECTED)
        print(f"FAIL: missing={missing} unexpected={unexpected}", file=sys.stderr)
        return 1
    if any(not binding.startswith("127.0.0.1:") for binding in published):
        print("FAIL: non-loopback host publication detected", file=sys.stderr)
        return 1

    # The gateway includes conf.d at runtime.  Its upstream hostnames must be
    # resolvable through the rendered Compose service namespace, not merely
    # through a main nginx.conf that happens to be valid in isolation.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        conf_d = root / "conf.d"
        conf_d.mkdir()
        nginx = root / "nginx.conf"
        nginx.write_text("http { include /etc/nginx/conf.d/*.conf; }\n", encoding="utf-8")
        (conf_d / "routes.conf").write_text(
            "upstream api {\n    server unresolved-oracle-backend:8000;\n}\n",
            encoding="utf-8",
        )
        compose = root / "compose.yml"
        compose.write_text("services:\n  python-backend:\n", encoding="utf-8")
        errors, _ = validate_checkout(root, compose, nginx_config=nginx)
        if not any("unresolved-oracle-backend" in error for error in errors):
            print(
                "FAIL: included conf.d upstream host was not validated against Compose services",
                file=sys.stderr,
            )
            return 1
    print(f"OK: {len(published)} oracle publications are loopback-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
