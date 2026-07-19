#!/usr/bin/env bash
set -euo pipefail

# Read-only probe: no namespaces, kubeconfig, images, or secrets are mutated.
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
chart_dir="$repo_dir/deploy/kubernetes"
json=false
[[ "${1:-}" == "--json" ]] && json=true
has() { command -v "$1" >/dev/null 2>&1; }
helm_installed=false; helm_lint=false; cluster=false; compose=false
has helm && helm_installed=true && helm lint "$chart_dir" >/dev/null 2>&1 && helm_lint=true
has kubectl && kubectl cluster-info >/dev/null 2>&1 && cluster=true
has docker && docker compose version >/dev/null 2>&1 && compose=true
if "$json"; then
  printf '{"helm":{"installed":%s,"lint":%s},"kubectl":{"installed":%s,"cluster_reachable":%s},"docker":{"installed":%s,"compose":%s}}\n' \
    "$helm_installed" "$helm_lint" "$(has kubectl && echo true || echo false)" "$cluster" \
    "$(has docker && echo true || echo false)" "$compose"
  exit 0
fi
printf 'Tracera deployment capability (read-only)\n'
for tool in helm kubectl docker kind k3d minikube; do
  if has "$tool"; then printf '  %-8s available\n' "$tool"; else printf '  %-8s unavailable\n' "$tool"; fi
done
printf '  helm lint: %s\n' "$([[ "$helm_lint" == true ]] && echo pass || echo unavailable/failed)"
printf '  kubernetes cluster: %s\n' "$([[ "$cluster" == true ]] && echo reachable || echo not-reachable)"
printf '  docker compose: %s\n' "$([[ "$compose" == true ]] && echo available || echo unavailable)"
printf '\nNo mutation performed.\n'
