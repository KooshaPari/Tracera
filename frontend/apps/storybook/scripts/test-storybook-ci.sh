#!/usr/bin/env bash
set -euo pipefail

# TASK #177: Fix bmad storybook bootstrap asset path resolution
# Use bunx to resolve storybook binary from node_modules, not system PATH
bun run test:vitest --run

bunx storybook build --quiet
