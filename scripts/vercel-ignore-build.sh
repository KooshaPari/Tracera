#!/usr/bin/env bash
# Vercel Ignored Build Step. Exit 0 = skip the build, exit 1 = build.
# Saves Hobby-plan deployment quota (100/day): skip Dependabot branches and
# pushes that only touch docs/markdown.
# Any uncertainty (missing base commit, git error, shallow clone) builds.
if [[ "${VERCEL_GIT_COMMIT_REF:-}" == dependabot/* ]]; then
  echo "skip: dependabot branch"; exit 0
fi

# Prefer the last successfully deployed commit as the diff base. Vercel exports
# this for the branch. Falling back to HEAD^ compares only the final commit, so
# a multi-commit push whose last commit is docs-only would skip a build even
# though earlier commits changed code.
base="${VERCEL_GIT_PREVIOUS_SHA:-HEAD^}"

# Vercel does not guarantee a deep clone, so the base may be absent. Build
# rather than risk skipping a real change.
if ! git cat-file -e "${base}^{commit}" 2>/dev/null; then
  echo "build: base commit ${base} unavailable"; exit 1
fi

# A redeployment reuses the last successful commit, so base == HEAD and the diff
# is empty. Building in that case lets changed environment variables take effect
# and avoids cancelling a deliberate redeploy.
base_sha=$(git rev-parse "$base" 2>/dev/null || printf '%s' "$base")
head_sha=$(git rev-parse HEAD 2>/dev/null || printf '%s' HEAD)
if [[ "$base_sha" == "$head_sha" ]]; then
  echo "build: redeploying the same commit ($base)"; exit 1
fi

# ignoreCommand runs from the repository root (vercel.json lives there), so the
# pathspec "." covers the whole tree.
git diff --quiet "$base" HEAD -- . ':(exclude)docs' ':(exclude)*.md' 2>/dev/null
status=$?

# Only an exact 0 means "no differences"; 1 means differences, anything else is
# an error. Anything other than 0 builds, which is the safe direction.
if [[ $status -eq 0 ]]; then
  echo "skip: docs/markdown-only changes from ${base}"; exit 0
fi
echo "build: non-docs changes (or diff error, status=${status}) from ${base}"
exit 1
