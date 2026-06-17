# Implementation Strategy

- Keep the change documentation-only.
- Prefer a fresh current-head worktree over merging stale prepared evidence.
- Use a fast-forward into canonical only after verifying ancestry, scope, and
  canonical cleanliness.
