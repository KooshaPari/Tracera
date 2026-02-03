#!/usr/bin/env python3
"""
Dev start with preflight: run preflight, auto-start infra if needed, then process-compose.

- Runs dev-start preflight (database, redis, nats, neo4j).
- If any check fails, tries to start that service via scripts/shell/start-services.sh, then re-runs preflight.
- If still failing, prints detailed failures (no need for 'rtm dev check') and exits 1.
- If all pass, execs process-compose with remaining args (e.g. up --logs-truncate or up -d --logs-truncate).

Usage:
  python scripts/python/dev-start-with-preflight.py up --logs-truncate
  python scripts/python/dev-start-with-preflight.py up -d --logs-truncate
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    # Script lives in scripts/python/ so parent.parent = scripts/, parent.parent.parent = repo root
    repo_root = Path(__file__).resolve().parent.parent.parent
    os.chdir(repo_root)
    sys.path.insert(0, str(repo_root / "src"))
    pc_config_path = repo_root / "config" / "process-compose.yaml"
    if not pc_config_path.exists():
        print("config/process-compose.yaml not found", file=sys.stderr)
        return 1

    # Load .env into process so preflight sees DATABASE_URL etc.
    env = os.environ.copy()
    env_file = repo_root / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k:
                    env[k] = v

    from tracertm.preflight import (
        build_dev_start_checks,
        format_preflight_failures,
        run_preflight_with_results,
    )

    checks = build_dev_start_checks()
    passed, results = run_preflight_with_results("dev", checks, strict=False)

    if not passed:
        # Map check names to start-services.sh service names
        failed_names = {r.name for r in results if not r.ok}
        service_map = {
            "database": "postgres",
            "redis": "redis",
            "nats": "nats",
            "neo4j": "neo4j",
        }
        start_script = repo_root / "scripts" / "shell" / "start-services.sh"
        if start_script.exists():
            for check_name, svc in service_map.items():
                if check_name in failed_names:
                    subprocess.run(
                        [str(start_script), svc],
                        cwd=repo_root,
                        env=env,
                        capture_output=True,
                        timeout=60,
                    )
            time.sleep(5)
            passed, results = run_preflight_with_results("dev", checks, strict=False)

    if not passed:
        print(format_preflight_failures(results), file=sys.stderr)
        return 1

    # Run process-compose with config. Use absolute path so it is found regardless of cwd (e.g. when invoked via "rtm dev start").
    pc_config_raw = os.environ.get("PC_CONFIG", "").strip().split()
    pc_config = []
    i = 0
    while i < len(pc_config_raw):
        part = pc_config_raw[i]
        if part == "-f" and i + 1 < len(pc_config_raw):
            path = Path(pc_config_raw[i + 1])
            if not path.is_absolute():
                path = (repo_root / path).resolve()
            pc_config.extend(["-f", str(path)])
            i += 2
            continue
        pc_config.append(part)
        i += 1
    if not pc_config:
        pc_config = ["-f", str(pc_config_path)]
    pc_args = pc_config + (sys.argv[1:] if len(sys.argv) > 1 else ["up", "--logs-truncate"])
    pc_bin = "process-compose"
    try:
        os.execvp(pc_bin, [pc_bin, *pc_args])
    except FileNotFoundError:
        print(f"{pc_bin} not found; install it (e.g. brew install process-compose)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
