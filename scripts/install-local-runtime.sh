#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:${PATH}"

# Install the supported native macOS runtime without Docker.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
server_bin="$repo_root/target/release/tracera-server"
app_src="$repo_root/frontend/apps/desktop/build/dev-macos-arm64/Tracera-dev.app"
app_dst="${HOME}/Applications/Tracera-dev-0.1.0.app"
agent_dir="${HOME}/Library/LaunchAgents"
agent="${agent_dir}/com.phenotype.tracera-server.plist"

mkdir -p "$agent_dir" "${HOME}/Applications"
build_log="$(mktemp -t tracera-build.XXXXXX)"
if ! cargo build --release -p tracera-server 2>"$build_log"; then
  if grep -q "mis-aligned LINKEDIT" "$build_log"; then
    mv "$repo_root/target/release" "$repo_root/target/release-corrupt-$(date +%s)"
    cargo build --release -p tracera-server
  else
    cat "$build_log" >&2
    exit 1
  fi
fi
rm -f "$build_log"
bun --cwd "$repo_root/frontend/apps/desktop" run build
[[ -x "$server_bin" ]] || { echo "release server missing: $server_bin" >&2; exit 1; }
[[ -d "$app_src" ]] || { echo "desktop bundle missing: $app_src" >&2; exit 1; }
ditto "$app_src" "$app_dst"

cat > "$agent" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.phenotype.tracera-server</string>
  <key>ProgramArguments</key><array><string>${server_bin}</string></array>
  <key>WorkingDirectory</key><string>${repo_root}</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>${HOME}/Library/Logs/tracera-server.log</string>
  <key>StandardErrorPath</key><string>${HOME}/Library/Logs/tracera-server.error.log</string>
</dict></plist>
PLIST

launchctl bootout "gui/$(id -u)" "$agent" >/dev/null 2>&1 || true
if command -v lsof >/dev/null 2>&1; then
  listener="$(lsof -nP -tiTCP:8080 -sTCP:LISTEN 2>/dev/null | head -1 || true)"
  if [[ -n "$listener" ]]; then
    owner="$(ps -p "$listener" -o comm= 2>/dev/null | sed 's/^ *//' || true)"
    echo "port 8080 is already owned by PID ${listener}${owner:+ (${owner})}; refusing duplicate launchd startup" >&2
    exit 1
  fi
fi
launchctl bootstrap "gui/$(id -u)" "$agent"
TRACERA_URL="http://127.0.0.1:8080" open "$app_dst"
echo "installed desktop: $app_dst"
echo "installed backend agent: $agent"
