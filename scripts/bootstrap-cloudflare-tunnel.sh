#!/usr/bin/env bash
# bootstrap-cloudflare-tunnel.sh — one-time DNS + credentials for the tracera tunnel
#
# Prereq: `cloudflared tunnel login` (writes cert.pem into CRED_DIR).
#
# Creates the remotely-managed tunnel, writes credentials JSON into .cloudflared/,
# and publishes DNS for:
#   tracera.pheno.studio
#   api.tracera.pheno.studio
#   mcp.tracera.pheno.studio
#
# Usage (from repo root):
#   bash scripts/bootstrap-cloudflare-tunnel.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRED_DIR="${CRED_DIR:-$REPO_ROOT/.cloudflared}"
TUNNEL_NAME="${TUNNEL_NAME:-tracera}"

mkdir -p "$CRED_DIR"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "error: cloudflared not installed" >&2
  exit 1
fi

if [ ! -f "$CRED_DIR/cert.pem" ]; then
  echo "error: missing $CRED_DIR/cert.pem — run 'cloudflared tunnel login' first" >&2
  exit 1
fi

cd "$CRED_DIR"

if ! compgen -G "*.json" >/dev/null 2>&1; then
  echo "[tunnel] creating tunnel '${TUNNEL_NAME}'"
  cloudflared tunnel create "$TUNNEL_NAME"
fi

cred_file=$(compgen -G "*.json" | head -n1)
tunnel_id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["TunnelID"])' "$cred_file")

echo "[tunnel] tunnel id=${tunnel_id}, credentials=${cred_file}"

for host in tracera.pheno.studio api.tracera.pheno.studio mcp.tracera.pheno.studio; do
  echo "[tunnel] routing DNS ${host}"
  cloudflared tunnel route dns "$TUNNEL_NAME" "$host" || true
done

# Keep config.yml in sync with the credentials file name.
if grep -q '<UUID>' "$REPO_ROOT/.cloudflared/config.yml"; then
  python3 - "$REPO_ROOT/.cloudflared/config.yml" "${cred_file%.json}" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
tunnel_id = sys.argv[2]
path.write_text(path.read_text().replace("<UUID>", tunnel_id))
PY
  echo "[tunnel] updated .cloudflared/config.yml credentials-file"
fi

echo
echo "=== Tunnel bootstrap complete ==="
echo "Start with: bash scripts/start-tunnel.sh"
echo "Or fetch a connector token for docker compose:"
echo "  cloudflared tunnel token ${tunnel_id}"
