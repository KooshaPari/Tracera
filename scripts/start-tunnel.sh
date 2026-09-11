#!/usr/bin/env bash
# start-tunnel.sh — hybrid Tailnet (primary) + Cloudflare Tunnel (fallback)
# to expose the local Tracera backend to the public internet at
# `tracera.pheno.studio/api/*` (and `mcp.tracera.pheno.studio`,
# `api.tracera.pheno.studio`).
#
# Routing priority:
#   1. **Tailnet** (preferred): serves `tracera.pheno.studio/api/*` over
#      the user's private Tailscale network (MagicDNS resolves
#      `tracera` → 100.x device IP). Zero public attack surface. No
#      external egress needed.
#   2. **Cloudflare Tunnel** (fallback): used when the public internet
#      needs access (e.g. demo to a third party, GitHub Actions, an
#      external AI agent). Requires `cloudflared` binary + cert.pem
#      (one-time `cloudflared tunnel login`).
#
# Both run together by default; the script verifies Tailnet first and
# only spins up the CF tunnel if `tailscale` is on PATH and active.
#
# Prereqs (one-time):
#   Tailnet (primary):
#     1. Install Tailscale:   https://tailscale.com/download
#     2. `sudo tailscale up` (or via GUI on Windows)
#     3. Enable MagicDNS so `tracera` resolves
#   Cloudflare (fallback):
#     1. `cloudflared` installed (winget: `winget install Cloudflare.cloudflared`)
#     2. `cloudflared tunnel login`   (browser cert flow)
#     3. `cloudflared tunnel create tracera`
#     4. `cloudflared tunnel route dns tracera tracera.pheno.studio` (and api/mcp)
#     5. See `.cloudflared/config.yml` for the ingress rules
#
# Run from the repo root: `bash scripts/start-tunnel.sh`
# Or as Windows service: `cloudflared service install && sc start cloudflared`

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRED_DIR="$REPO_ROOT/.cloudflared"
TUNNEL_NAME="${TUNNEL_NAME:-tracera}"
LOG_DIR="$REPO_ROOT/.cloudflared"

mkdir -p "$LOG_DIR"

# ----------------------------------------------------------------------------
# 1. Tailnet (preferred)
# ----------------------------------------------------------------------------
if command -v tailscale >/dev/null 2>&1; then
  TS_STATUS="$(tailscale status --json 2>/dev/null | grep -o '"BackendState":"[^"]*"' | head -n1 | cut -d'"' -f4 || echo unknown)"
  case "$TS_STATUS" in
    Running)
      TS_DNS="$(tailscale status --json 2>/dev/null | grep -o '"MagicDNS":true' | head -n1 || true)"
      TS_IP="$(tailscale ip -4 2>/dev/null | head -n1 || true)"
      if [ -n "$TS_IP" ]; then
        echo "[tunnel] Tailnet ACTIVE — tracera reachable as:"
        echo "[tunnel]   http://tracera:8080/api  (MagicDNS, Tailnet only)"
        echo "[tunnel]   http://${TS_IP}:8080/api  (raw IP, Tailnet only)"
        echo "[tunnel] Prefer Tailnet when caller is on the same tailnet (zero egress)."
      fi
      ;;
    *)
      echo "[tunnel] tailscale installed but backend state='${TS_STATUS}' — run 'sudo tailscale up'"
      ;;
  esac
else
  echo "[tunnel] tailscale not installed — skipping Tailnet path (public-only via CF tunnel)"
fi

# ----------------------------------------------------------------------------
# 2. Cloudflare Tunnel (fallback / public-internet path)
# ----------------------------------------------------------------------------
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "[tunnel] cloudflared not installed — skipping CF path."
  echo "[tunnel] Install: winget install Cloudflare.cloudflared  (Windows)"
  echo "[tunnel]           brew install cloudflared                           (macOS)"
  echo "[tunnel]           https://github.com/cloudflare/cloudflared/releases  (Linux)"
  exit 0
fi

if [ ! -f "$CRED_DIR/cert.pem" ]; then
  echo "[tunnel] No cert.pem in $CRED_DIR — running 'cloudflared tunnel login' (browser flow)." >&2
  (cd "$CRED_DIR" && cloudflared tunnel login) || {
    echo "[tunnel] Login cancelled or failed. Run 'cloudflared tunnel login' manually." >&2
    exit 1
  }
fi

if ! compgen -G "$CRED_DIR/*.json" >/dev/null 2>&1; then
  echo "[tunnel] No tunnel credentials JSON in $CRED_DIR — running 'cloudflared tunnel create $TUNNEL_NAME'." >&2
  (cd "$CRED_DIR" && cloudflared tunnel create "$TUNNEL_NAME") || {
    echo "[tunnel] Tunnel creation failed. Run 'cloudflared tunnel create $TUNNEL_NAME' manually." >&2
    exit 1
  }
fi

echo "[tunnel] Starting Cloudflare tunnel '$TUNNEL_NAME' (Ctrl-C to stop)..."
echo "[tunnel]   Public ingresses (via CF tunnel):"
echo "[tunnel]     https://tracera.pheno.studio/api/*"
echo "[tunnel]     https://api.tracera.pheno.studio"
echo "[tunnel]     https://mcp.tracera.pheno.studio"
echo "[tunnel]   Local:"
echo "[tunnel]     http://localhost:8080/api"
echo "[tunnel]     http://localhost:8081           (MCP streamable-HTTP)"

exec cloudflared --config "$CRED_DIR/config.yml" --no-autoupdate tunnel run "$TUNNEL_NAME"
