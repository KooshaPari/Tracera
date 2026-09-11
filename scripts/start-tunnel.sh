#!/usr/bin/env bash
# start-tunnel.sh — start the Cloudflare Tunnel that exposes the local
# Tracera backend to the public internet at `tracera.pheno.studio/api/*`
# (and `api.tracera.pheno.studio`, `mcp.tracera.pheno.studio`).
#
# Prereqs (one-time):
#   1. cloudflared installed: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#   2. Login:                  `cloudflared tunnel login`
#   3. Create tunnel:          `cloudflared tunnel create tracera`
#   4. Route DNS:              `cloudflared tunnel route dns tracera tracera.pheno.studio`
#                              `cloudflared tunnel route dns tracera api.tracera.pheno.studio`
#                              `cloudflared tunnel route dns tracera mcp.tracera.pheno.studio`
#   5. Set env vars:           see crates/tracera-server/.env.local
#
# Run from the repo root: `bash scripts/start-tunnel.sh`
# Or as a service:        `cloudflared service install && sc start cloudflared`

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRED_DIR="$REPO_ROOT/.cloudflared"
TUNNEL_NAME="${TUNNEL_NAME:-tracera}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "[tunnel] ERROR: cloudflared is not installed or not in PATH." >&2
  echo "[tunnel] Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" >&2
  exit 1
fi

if [ ! -f "$CRED_DIR/cert.pem" ]; then
  echo "[tunnel] No cert.pem found in $CRED_DIR — running 'cloudflared tunnel login' (follow the URL in your browser)." >&2
  (cd "$CRED_DIR" && cloudflared tunnel login)
fi

if ! compgen -G "$CRED_DIR/*.json" >/dev/null 2>&1; then
  echo "[tunnel] No tunnel credentials JSON found in $CRED_DIR — running 'cloudflared tunnel create $TUNNEL_NAME'." >&2
  (cd "$CRED_DIR" && cloudflared tunnel create "$TUNNEL_NAME")
fi

echo "[tunnel] Starting '$TUNNEL_NAME' (Ctrl-C to stop)..."
exec cloudflared --config "$CRED_DIR/config.yml" --no-autoupdate tunnel run "$TUNNEL_NAME"
