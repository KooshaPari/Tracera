#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
report_file="${2:-.claude/verification/governance-health-report.json}"
history_file="${3:-.claude/verification/governance-health-history.jsonl}"

cd "$root"
mkdir -p "$(dirname "$report_file")"
mkdir -p "$(dirname "$history_file")"

score=100
issues=()

required_files=(
  ".claude/quality.json"
  ".claude/governance-toolchain.lock.json"
  "scripts/governance-drift-detector.sh"
)

for path in "${required_files[@]}"; do
  if [[ ! -e "$path" ]]; then
    issues+=("missing:${path}")
    score=$((score - 20))
  fi
done

if [[ -f ".claude/quality.json" ]]; then
  min_score="$(jq -r '.governance.health.min_score // 80' .claude/quality.json)"
else
  min_score="${HEALTH_MIN_SCORE:-80}"
fi

if [[ "$score" -lt 0 ]]; then
  score=0
fi

{
  printf '{\n'
  printf '  "schema_version": 1,\n'
  printf '  "score": %s,\n' "$score"
  printf '  "min_score": %s,\n' "$min_score"
  printf '  "issues": ['
  for i in "${!issues[@]}"; do
    [[ "$i" -gt 0 ]] && printf ', '
    jq -Rn --arg value "${issues[$i]}" '$value'
  done
  printf ']\n'
  printf '}\n'
} > "$report_file"

jq -c . "$report_file" >> "$history_file"
