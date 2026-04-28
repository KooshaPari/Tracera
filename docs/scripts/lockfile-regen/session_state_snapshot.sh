#!/usr/bin/env bash
# session_state_snapshot.sh — capture state at session boundary
# Usage: session_state_snapshot.sh > /tmp/state-$(date +%s).json
set +e

cat <<JSON
{
  "timestamp_unix": $(date +%s),
  "timestamp_iso": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "disk_free_gi": "$(df -h / | tail -1 | awk '{print $4}' | tr -d 'Gi')",
  "active_dispatch_workers": $(ps aux | grep dispatch-worker | grep -v grep | wc -l | tr -d ' '),
  "gh_rate_remaining": $(gh api rate_limit --jq '.resources.core.remaining' 2>/dev/null || echo 0),
  "gh_rate_reset": $(gh api rate_limit --jq '.resources.core.reset' 2>/dev/null || echo 0),
  "open_org_prs": $(gh search prs --owner KooshaPari --state open --limit 100 --json url,isDraft,author --jq '[.[] | select(.isDraft==false and (.author.login | startswith("app/dependabot") | not))] | length' 2>/dev/null || echo "?"),
  "tmp_wave_dirs": $(ls -d /tmp/wave* 2>/dev/null | wc -l | tr -d ' '),
  "tmp_clones": $(ls -d /tmp/*-lockfile-* /tmp/*-r[0-9]* 2>/dev/null | wc -l | tr -d ' ')
}
JSON
