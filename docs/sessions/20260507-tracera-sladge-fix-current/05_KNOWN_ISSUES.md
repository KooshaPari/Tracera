# Known Issues

- The old `docs/tracera-sladge-current` worktree remains stale relative to
  active `fix/add-metadata` history.
- The repository contains large archived dependency artifacts that can trigger
  Git LFS pointer warnings when creating new worktrees.
- Network-reliant validation may fall back to committed snapshots in this
  sandbox.
