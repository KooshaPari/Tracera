#!/bin/bash
# Quick script to deploy to production
# Usage: ./prod-deploy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/deploy.sh" production
