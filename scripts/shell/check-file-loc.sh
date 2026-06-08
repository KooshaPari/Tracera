#!/usr/bin/env bash

set -euo pipefail

python3 scripts/quality/check_file_loc.py "$@"
