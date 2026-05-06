# Implementation Strategy

Use a fresh current-head worktree under `.worktrees/` because canonical
`Tracera` has broad unrelated local changes and repo-local instructions prefer
feature work in `.worktrees/<topic>/`.

The change is intentionally narrow: README badge plus session documentation.
No stale recovered git metadata, workflow files, package files, Docker files, or
application code are modified.
