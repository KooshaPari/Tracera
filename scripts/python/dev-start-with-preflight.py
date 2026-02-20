#!/usr/bin/env python3
"""Dev start with preflight: run preflight, auto-start infra if needed, then process-compose.

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


def load_env_file(repo_root: Path) -> dict[str, str]:
    """Load environment variables from .env file."""
    env = os.environ.copy()
    env_file = repo_root / ".env"

    if not env_file.exists():
        return env

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                env[k] = v

    return env


def start_failed_services(failed_names: set[str], repo_root: Path, env: dict[str, str]) -> None:
    """Start services that failed preflight checks."""
    service_map = {
        "database": "postgres",
        "redis": "redis",
        "nats": "nats",
        "neo4j": "neo4j",
    }
    start_script = repo_root / "scripts" / "shell" / "start-services.sh"

    if not start_script.exists():
        return

    for check_name, svc in service_map.items():
        if check_name in failed_names:
            subprocess.run(
                [str(start_script), svc],
                cwd=repo_root,
                env=env,
                capture_output=True,
                timeout=60,
            )


def run_preflight_checks(repo_root: Path, env: dict[str, str]) -> tuple[bool, list]:
    """Run preflight checks and retry if failed services can be started."""
    from tracertm.preflight import build_dev_start_checks, run_preflight_with_results

    checks = build_dev_start_checks()
    passed, results = run_preflight_with_results("dev", checks, strict=False)

    if not passed:
        failed_names = {r.name for r in results if not r.ok}
        start_failed_services(failed_names, repo_root, env)
        time.sleep(5)
        passed, results = run_preflight_with_results("dev", checks, strict=False)

    return passed, results


def build_process_compose_config(repo_root: Path, pc_config_path: Path) -> list[str]:
    """Build process-compose configuration from environment or default."""
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

    return pc_config


def main() -> int:
    """Main entry point: run preflight, start services if needed, exec process-compose."""
    # Setup paths
    repo_root = Path(__file__).resolve().parent.parent.parent
    os.chdir(repo_root)
    sys.path.insert(0, str(repo_root / "src"))

    pc_config_path = repo_root / "config" / "process-compose.yaml"
    if not pc_config_path.exists():
        return 1

    # Load environment
    env = load_env_file(repo_root)
    env.setdefault("PC_PORT_NUM", "18080")
    os.environ.update(env)

    # Run preflight checks
    passed, _results = run_preflight_checks(repo_root, env)

    if not passed:
        return 1

    # Build and execute process-compose
    pc_config = build_process_compose_config(repo_root, pc_config_path)
    pc_port = env.get("PC_PORT_NUM", "18080")
    pc_args = pc_config + ["--port", pc_port] + (sys.argv[1:] if len(sys.argv) > 1 else ["up", "--logs-truncate"])
    pc_bin = "process-compose"

    try:
        os.execvp(pc_bin, [pc_bin, *pc_args])
    except FileNotFoundError:
        return 1


if __name__ == "__main__":
    sys.exit(main())
