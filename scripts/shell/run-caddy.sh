#!/usr/bin/env bash
# Run Caddy by full path so Overmind doesn't depend on PATH.
# Export PATH first so child and fallback lookup see Homebrew.
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
set -e
for dir in /opt/homebrew/bin /usr/local/bin; do
  if [[ -x "$dir/caddy" ]]; then
    exec "$dir/caddy" run --config config/Caddyfile --watch
  fi
done
# Fallback: use PATH (e.g. when caddy is in a version manager path)
if command -v caddy &>/dev/null; then
  exec caddy run --config config/Caddyfile --watch
fi
echo "caddy not found; install with: brew install caddy" >&2
exit 127
