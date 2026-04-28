# Research

- Root manifests indicate a Python workspace (`pyproject.toml`, `uv.lock`) plus a Bun-managed
  frontend workspace (`package.json`, `bun.lock`).
- The checkout is sparse, so frontend directories are not materialized in the working tree; the
  taskfile should avoid assuming those directories exist before running frontend commands.
