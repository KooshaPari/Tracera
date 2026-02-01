#!/bin/bash
# Quick script to deploy a preview version
# Usage: ./preview-deploy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/deploy.sh" preview
