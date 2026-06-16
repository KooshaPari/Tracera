#!/bin/bash
branches=$(git branch --no-color --no-merged integration/consolidate | grep -v '^\*' | grep -v '^  QUARANTINE' | awk '{print $1}')
merged=0
skipped=0
skipped_list=""
for branch in $branches; do
  count=$(git diff --name-status integration/consolidate...$branch | grep -c '^D')
  if [ "$count" -eq 0 ]; then
    echo "Merging $branch ..."
    if git merge --no-ff "$branch" -m "Merge branch $branch into integration/consolidate (consolidation pipeline)"; then
      merged=$((merged + 1))
    else
      echo "CONFLICT/FAIL on $branch, aborting..."
      git merge --abort 2>/dev/null || true
      skipped=$((skipped + 1))
      skipped_list="$skipped_list $branch"
    fi
  else
    echo "SKIP $branch ($count deletions)"
    skipped=$((skipped + 1))
    skipped_list="$skipped_list $branch"
  fi
done
echo "MERGED: $merged"
echo "SKIPPED: $skipped"
echo "SKIPPED_LIST:$skipped_list"
