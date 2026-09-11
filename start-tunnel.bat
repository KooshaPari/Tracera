@echo off
REM start-tunnel.bat — Windows wrapper for the Cloudflare Tunnel
REM (uses cloudflared.exe which is already on PATH if you ran the
REM installer in user-mode).
REM
REM Run from repo root: start-tunnel.bat

if not exist .cloudflared\cert.pem (
  echo [tunnel] cert.pem not found - run: cloudflared tunnel login
  cloudflared tunnel login
)

if not exist .cloudflared\*.json (
  echo [tunnel] No credentials JSON found - creating tunnel "tracera"
  cloudflared tunnel create tracera
)

echo [tunnel] Starting tunnel "tracera" (Ctrl-C to stop)...
cloudflared --config .cloudflared\config.yml --no-autoupdate tunnel run tracera
