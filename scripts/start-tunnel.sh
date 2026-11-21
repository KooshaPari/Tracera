#!/usr/bin/env bash
# start-tunnel.sh — report Tracera private/public ingress paths.
#
# The live Cloudflare tunnel is shared infrastructure ("tracera-local") and
# carries routes for multiple Phenotype products. Tracera no longer owns the
# complete cloudflared configuration, so this repo MUST NOT create, replace, or
# start that shared tunnel from a Tracera-only route file.
#
# This helper is intentionally non-mutating for Cloudflare. It reports Tailnet
# reachability and the Tracera-owned public hostnames. Shared tunnel lifecycle
# belongs in shared infrastructure IaC.

set -euo pipefail

echo "[tunnel] Tracera ingress status"

if command -v tailscale >/dev/null 2>&1; then
  TS_STATUS="$(tailscale status --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("BackendState","unknown"))' 2>/dev/null || echo unknown)"
  TS_IP="$(tailscale ip -4 2>/dev/null | head -n1 || true)"
  if [[ "$TS_STATUS" == "Running" && -n "$TS_IP" ]]; then
    echo "[tunnel] Tailnet ACTIVE:"
    echo "[tunnel]   tracera:8080/api (HTTP carried inside encrypted Tailnet)"
    echo "[tunnel]   $TS_IP:8080/api (HTTP carried inside encrypted Tailnet)"
  else
    echo "[tunnel] Tailnet not confirmed active (state=$TS_STATUS)"
  fi
else
  echo "[tunnel] tailscale not installed"
fi

echo "[tunnel] Public Tracera routes on shared Cloudflare tunnel:"
echo "[tunnel]   https://tracera.pheno.studio"
echo "[tunnel]   https://t.tracera.pheno.studio"
echo
echo "[tunnel] REFUSING to create/start/replace cloudflared from this repository."
echo "[tunnel] Reason: the live tunnel is shared infrastructure and includes non-Tracera routes."
echo "[tunnel] Use the shared infrastructure owner/IaC for tunnel lifecycle changes."
