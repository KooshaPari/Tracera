#!/bin/bash
BRANCH_BASE="fix/main-ci-greenup"

while IFS= read -r branch; do
  if [ "$branch" = "$BRANCH_BASE" ]; then
    continue
  fi
  
  bu=$(git rev-list --count "${BRANCH_BASE}..${branch}" 2>/dev/null || echo "?")
  ub=$(git rev-list --count "${branch}..${BRANCH_BASE}" 2>/dev/null || echo "?")
  
  echo "${branch}|${bu}|${ub}"
done < branches.txt > branch_counts.txt
