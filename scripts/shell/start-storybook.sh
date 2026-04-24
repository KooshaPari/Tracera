#!/usr/bin/env bash
set -euo pipefail

scripts/shell/print-runtime-info.sh storybook
scripts/shell/require-port-free.sh storybook 6006
cd frontend
exec bun run dev:storybook
