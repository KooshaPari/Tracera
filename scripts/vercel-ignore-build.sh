#!/usr/bin/env bash
# Vercel Ignored Build Step. Exit 0 = skip the build, exit 1 = build.
# Saves Hobby-plan deployment quota (100/day): skip Dependabot branches and commits that only touch docs/markdown.
# Any uncertainty (no parent commit, git error) builds.
if [[ "${VERCEL_GIT_COMMIT_REF:-}" == dependabot/* ]]; then
  echo "skip: dependabot branch"; exit 0
fi
if git diff --quiet HEAD^ HEAD -- . ':(exclude)docs' ':(exclude)*.md' 2>/dev/null; then
  echo "skip: docs/markdown-only commit"; exit 0
fi
exit 1
