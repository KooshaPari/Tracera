#!/usr/bin/env bash
set -euo pipefail

# Static policy gate for the Helm chart. It is intentionally secret-free and
# does not contact a cluster; run it before rendering/applying manifests.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHART="$ROOT_DIR/deploy/kubernetes"
fail() { printf 'kubernetes security check failed: %s\n' "$1" >&2; exit 1; }

[[ -f "$CHART/templates/tracera.yaml" ]] || fail "deployment template missing"
[[ -f "$CHART/values.yaml" ]] || fail "values file missing"

grep -q 'runAsNonRoot: true' "$CHART/templates/tracera.yaml" || fail "workload must run as non-root"
grep -q 'readOnlyRootFilesystem: true' "$CHART/templates/tracera.yaml" || fail "root filesystem must be read-only"
grep -q 'allowPrivilegeEscalation: false' "$CHART/templates/tracera.yaml" || fail "privilege escalation must be disabled"
grep -q 'seccompProfile:' "$CHART/templates/tracera.yaml" || fail "seccomp profile must be explicit"
grep -q 'secretRef:' "$CHART/templates/tracera.yaml" || fail "runtime secrets must come from a Secret reference"
grep -q 'path: /ready' "$CHART/templates/tracera.yaml" || fail "readiness must use /ready"
grep -q 'path: /health' "$CHART/templates/tracera.yaml" || fail "liveness must use /health"
grep -q 'type: ClusterIP' "$CHART/values.yaml" || fail "service must default to internal ClusterIP"
! grep -RIn 'REPLACE_ME\|password:.*tracera' "$CHART" >/dev/null || fail "chart contains placeholder/concrete credentials"
! grep -q 'hostNetwork: true' "$CHART/values.yaml" || fail "host networking must remain disabled"

printf 'kubernetes security policy checks passed\n'
