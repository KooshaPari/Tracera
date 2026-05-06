# Research

## Current Checkout

- Canonical path: `Tracera`
- Active branch: `chore/trufflehog-20260502`
- Canonical state: dirty with unrelated workflow, package, Docker, report, and
  test-file edits.

## Stale Evidence

- Recorded path: `Tracera-recovered-wtrees/sladge-badge`
- State: path exists, but Git operations fail because it points at missing
  `Tracera-recovered/.git/worktrees/sladge-badge` metadata.

## Decision

Do not reuse the stale recovered worktree. Use a fresh current-head worktree
inside the live `Tracera` repo to preserve canonical local changes and produce
current evidence.
