#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
report_file="${2:-.claude/verification/governance-drift-report.json}"

cd "$root"
mkdir -p "$(dirname "$report_file")"

drifts=()

if [[ ! -f ".claude/quality.json" ]]; then
  drifts+=("missing:.claude/quality.json")
fi

if [[ ! -f ".claude/governance-toolchain.lock.json" ]]; then
  drifts+=("missing:.claude/governance-toolchain.lock.json")
fi

if [[ -f ".claude/quality.json" ]]; then
  for key in \
    ".governance.reliability" \
    ".governance.rolling_wave" \
    ".governance.assurance_case" \
    ".governance.privacy_preserving" \
    ".governance.playbooks" \
    ".governance.artifact_quality" \
    ".governance.debt_registry" \
    ".governance.toolchains" \
    ".governance.health"; do
    if ! jq -e "$key" .claude/quality.json >/dev/null; then
      drifts+=("missing:${key}")
    fi
  done
fi

{
  printf '{\n'
  printf '  "schema_version": 1,\n'
  printf '  "drift_count": %s,\n' "${#drifts[@]}"
  printf '  "drifts": ['
  for i in "${!drifts[@]}"; do
    [[ "$i" -gt 0 ]] && printf ', '
    jq -Rn --arg value "${drifts[$i]}" '$value'
  done
  printf ']\n'
  printf '}\n'
} > "$report_file"
