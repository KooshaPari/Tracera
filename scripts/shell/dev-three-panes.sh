#!/usr/bin/env bash
# Start TraceRTM with a single tmux session showing 3 panes: go | python | frontend.
# Infra (temporal, caddy, temporal_worker) must already be running via overmind -D.
# Usage: scripts/dev-three-panes.sh [project_root]
# Called by: rtm dev start --three

set -e
ROOT="${1:-.}"
cd "$ROOT"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

# Kill existing tracertm tmux session so we start fresh
tmux kill-session -t tracertm 2>/dev/null || true

# Strict deps order: go -> py -> frontend so preflights pass
# Create session with first pane (Go backend)
tmux new-session -d -s tracertm -n dev "cd '$ROOT/backend' && air -c .air.toml"
sleep 2
# Split: second pane (Python API; use .venv so conda/miniforge does not override)
tmux split-window -h -t tracertm "cd '$ROOT' && PYTHONWARNINGS='ignore:remove second argument of ws_handler:DeprecationWarning' .venv/bin/python -m uvicorn src.tracertm.api.main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude ARCHIVE --reload-exclude CONFIG"
sleep 2
# Split: third pane (Frontend)
tmux split-window -h -t tracertm "cd '$ROOT/frontend/apps/web' && bun run dev --host 0.0.0.0"
# Arrange as 3 equal columns
tmux select-layout -t tracertm tiled
# Attach so user sees the 3 panes
exec tmux attach -t tracertm
