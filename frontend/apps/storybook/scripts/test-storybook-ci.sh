#!/usr/bin/env bash
set -euo pipefail

bun run test:vitest --run

storybook build --quiet
