#!/usr/bin/env bash
set -euo pipefail

# Contract test for the read-only capability probe. This deliberately does not
# require a Kubernetes cluster, Docker daemon, or deployment credentials.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
report="$("$ROOT_DIR"/deploy/kubernetes/capability-report.sh --json)"

REPORT="$report" python3 - <<'PY'
import json
import os
import sys

try:
    payload = json.loads(os.environ["REPORT"])
except (KeyError, json.JSONDecodeError) as exc:
    raise SystemExit(f"capability report is not valid JSON: {exc}")

required = {
    "helm": {"installed", "lint"},
    "kubectl": {"installed", "cluster_reachable"},
    "docker": {"installed", "compose"},
}
if set(payload) != set(required):
    raise SystemExit(f"unexpected capability sections: {sorted(payload)}")
for section, keys in required.items():
    if set(payload[section]) != keys:
        raise SystemExit(f"unexpected keys in {section}: {sorted(payload[section])}")
    if not all(isinstance(payload[section][key], bool) for key in keys):
        raise SystemExit(f"non-boolean capability value in {section}")

# A reachable cluster may only be reported when kubectl is installed. This
# catches malformed probes while remaining valid on cluster-free CI runners.
if payload["kubectl"]["cluster_reachable"] and not payload["kubectl"]["installed"]:
    raise SystemExit("cluster_reachable cannot be true when kubectl is absent")
print("deployment capability report contract passed")
PY
