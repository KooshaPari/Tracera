#!/usr/bin/env bash
set -u
INPUT="$1"
OUT="$2"
: > "$OUT"
while IFS=$'\t' read -r name branch pushed stars; do
  [ -z "$name" ] && continue
  if gh api "repos/KooshaPari/$name/branches/$branch/protection" --silent 2>/dev/null; then
    prot=$(gh api "repos/KooshaPari/$name/branches/$branch/protection" 2>/dev/null)
    enforce=$(printf '%s' "$prot" | jq -r '.enforce_admins.enabled // "n/a"')
    reviews=$(printf '%s' "$prot" | jq -r '.required_pull_request_reviews.required_approving_review_count // "none"')
    restr=$(printf '%s' "$prot" | jq -r 'if .restrictions then "limited" else "none" end')
    printf '%s\t%s\tCLASSIC\t-\t%s\t%s\t%s\t%s\n' "$name" "$branch" "$enforce" "$reviews" "$restr" "$stars" >> "$OUT"
  else
    rs=$(gh api "repos/KooshaPari/$name/rulesets" --jq 'length' 2>/dev/null || echo 0)
    if [ "${rs:-0}" -gt 0 ]; then
      printf '%s\t%s\tRULESET\t%s\t-\t-\t-\t%s\n' "$name" "$branch" "$rs" "$stars" >> "$OUT"
    else
      printf '%s\t%s\tUNPROTECTED\t-\t-\t-\t-\t%s\n' "$name" "$branch" "$stars" >> "$OUT"
    fi
  fi
done < "$INPUT"
echo "DONE rows=$(wc -l < "$OUT")"
