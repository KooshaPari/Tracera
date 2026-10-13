#!/usr/bin/env bash
# bootstrap-cloudflare-tunnel.sh — retired mutating bootstrap.
#
# The live Cloudflare tunnel is shared infrastructure and carries multiple
# Phenotype products. Tracera must not create/replace that tunnel, publish DNS,
# or rewrite the shared ingress configuration from this repository.
#
# Shared tunnel lifecycle and DNS belong in shared infrastructure IaC.

set -euo pipefail

echo "error: Tracera-local Cloudflare tunnel bootstrap is disabled." >&2
echo "error: the live tunnel is shared infrastructure; use the shared infra owner/IaC." >&2
echo "error: this script intentionally performs no Cloudflare or DNS mutation." >&2
exit 2
