#!/usr/bin/env bash
set +e
repo=$1
deleted=0
for branch in $(gh api "repos/KooshaPari/$repo/branches?per_page=100" --paginate --jq '.[] | select(.name != "main" and .name != "master" and .name != "develop") | .name' 2>/dev/null); do
  [[ "$branch" =~ ^(release|hotfix|prod|dev$|main|master) ]] && continue
  open_pr=$(gh pr list --repo "KooshaPari/$repo" --head "$branch" --state open --json number --jq '.[0].number' 2>/dev/null)
  [ -n "$open_pr" ] && continue
  # closed or merged — both safe to delete
  any_pr=$(gh pr list --repo "KooshaPari/$repo" --head "$branch" --state all --json number,state --jq '.[0]' 2>/dev/null)
  if [ -n "$any_pr" ] && [ "$any_pr" != "null" ]; then
    gh api -X DELETE "repos/KooshaPari/$repo/git/refs/heads/$branch" 2>/dev/null && {
      deleted=$((deleted+1))
      echo "deleted: $repo/$branch ($any_pr)"
    }
  fi
done
echo "[$repo] deleted $deleted stale branches"
