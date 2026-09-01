#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:${PATH}"

# Xcode beta linkers can emit malformed Mach-O LINKEDIT layouts rejected by
# dyld when Cargo loads proc-macro dylibs. Prefer the installed stable Xcode
# for native macOS builds while leaving an explicit DEVELOPER_DIR override
# authoritative for CI/remote builders.
if [[ -z "${DEVELOPER_DIR:-}" ]]; then
  selected_developer_dir="$(xcode-select -p 2>/dev/null || true)"
  if [[ "$selected_developer_dir" == *"Xcode-beta"* && -d "/Applications/Xcode.app/Contents/Developer" ]]; then
    export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
  fi
fi

# Install the supported native macOS runtime without Docker.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
server_bin="$repo_root/target/release/tracera-server"
# The postbundle step normalizes the Electrobun artifact name and patches its
# CFBundleName to Tracera.app. Keep the installer aligned with that shipped
# artifact rather than the pre-postbundle Electrobun directory name.
app_src="$repo_root/frontend/apps/desktop/build/dev-macos-arm64/Tracera.app"
app_dst="${HOME}/Applications/Tracera-dev-0.1.0.app"
agent_dir="${HOME}/Library/LaunchAgents"
agent="${agent_dir}/com.phenotype.tracera-server.plist"
runtime_port="${TRACERA_PORT:-8080}"
database_path="${TRACERA_DB_PATH:-$repo_root/data/tracera.db}"

# Allow CI/remote builders to isolate linker artifacts without changing the
# source checkout. Cargo uses this same variable for the release output path.
target_dir="${CARGO_TARGET_DIR:-$repo_root/target}"
server_bin="$target_dir/release/tracera-server"

# Stop only this installer-owned job before checking for duplicate listeners.
launchctl bootout "gui/$(id -u)" "$agent" >/dev/null 2>&1 || true

if ! command -v lsof >/dev/null 2>&1; then
  echo "cannot verify TCP port ownership: lsof is required" >&2
  exit 1
fi
listener="$(lsof -nP -tiTCP:"$runtime_port" -sTCP:LISTEN 2>/dev/null | head -1 || true)"
if [[ -n "$listener" ]]; then
  owner="$(ps -p "$listener" -o comm= 2>/dev/null | sed 's/^ *//' || true)"
  echo "port $runtime_port is already owned by PID ${listener}${owner:+ (${owner})}; refusing duplicate launchd startup" >&2
  ps -p "$listener" -o pid=,command= >&2 2>/dev/null || true
  echo "stop the owning service or set TRACERA_PORT before retrying" >&2
  exit 1
fi

mkdir -p "$agent_dir" "${HOME}/Applications"
mkdir -p "$(dirname "$database_path")"
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
(
  cd "$repo_root/frontend/apps/desktop"
  bun run build
)
[[ -x "$server_bin" ]] || { echo "release server missing: $server_bin" >&2; exit 1; }
[[ -d "$app_src" ]] || { echo "desktop bundle missing: $app_src" >&2; exit 1; }
ditto "$app_src" "$app_dst"

cat > "$agent" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.phenotype.tracera-server</string>
  <key>ProgramArguments</key><array><string>${server_bin}</string></array>
  <key>EnvironmentVariables</key><dict>
    <key>TRACERA_BIND_ADDR</key><string>127.0.0.1:${runtime_port}</string>
    <key>DATABASE_URL</key><string>${DATABASE_URL:-sqlite://${database_path}?mode=rwc}</string>
  </dict>
  <key>WorkingDirectory</key><string>${repo_root}</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>${HOME}/Library/Logs/tracera-server.log</string>
  <key>StandardErrorPath</key><string>${HOME}/Library/Logs/tracera-server.error.log</string>
</dict></plist>
PLIST

launchctl bootstrap "gui/$(id -u)" "$agent"
TRACERA_URL="http://127.0.0.1:${runtime_port}" open "$app_dst"
echo "installed desktop: $app_dst"
echo "installed backend agent: $agent"
