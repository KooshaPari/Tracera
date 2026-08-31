#!/usr/bin/env bash
# scripts/provision-workers-kv.sh
# Provision the TRACERA_KV namespace and patch wrangler.toml.
#
# Usage: bash scripts/provision-workers-kv.sh
# Requires: wrangler CLI authenticated (`wrangler login`)
# Justification: <5 lines of wrangler invocations + sed patch; no logic warrants
#   a compiled binary. Per Phenotype scripting policy: Bash only as <=5-line glue.
set -euo pipefail

TOML="$(dirname "$0")/../wrangler.toml"

echo "Provisioning production KV namespace..."
PROD_ID=$(wrangler kv namespace create tracera_cache 2>&1 | grep '"id"' | sed 's/.*"id": *"\([^"]*\)".*/\1/')
echo "Production id: $PROD_ID"
sed -i.bak "s/^id = \"PROVISION_REQUIRED\"/id = \"$PROD_ID\"/" "$TOML"

echo "Provisioning preview KV namespace..."
PREVIEW_ID=$(wrangler kv namespace create tracera_cache --preview 2>&1 | grep '"id"' | sed 's/.*"id": *"\([^"]*\)".*/\1/')
echo "Preview id: $PREVIEW_ID"
sed -i.bak "s/^# preview_id = \"PROVISION_REQUIRED\"/preview_id = \"$PREVIEW_ID\"/" "$TOML"

rm -f "$TOML.bak"
echo "wrangler.toml patched. Commit the updated file."
