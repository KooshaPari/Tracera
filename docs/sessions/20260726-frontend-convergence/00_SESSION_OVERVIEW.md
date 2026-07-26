# Tracera Frontend Convergence

## Goal

Make the approved, feature-complete Tracera dashboard the only desktop UI while
preserving the currently installed app until live API parity and dogfood gates pass.

## Canonical lineage

- Rich candidate: `95334238ca4e0505770784623432dbc858c91d7e`
- Parent: `3f5eebe52f465af1a991fef3e96d597fed460d8e`
- Jan/Feb baseline: `2c5ffc33f` (2026-02-08)
- Current main/minimal app: `e939246e6` (12 web source files)
- Rich candidate branch: `wip/20260722T1535-18c4a6993eb78260`

The rich candidate is the source of truth for UI capabilities. It is not yet a
runtime-ready replacement because its API contract is broader than the Rust server.

## Non-goals

Do not delete or overwrite the current installed app, force-reset worktrees, or
claim parity from mock-only tests.

