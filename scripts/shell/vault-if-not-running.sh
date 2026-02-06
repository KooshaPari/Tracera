#!/usr/bin/env bash
# Start HashiCorp Vault in dev mode if not already running
# Dev mode: in-memory storage, auto-unsealed, root token logged

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN_FILE=".vault-root-token"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "Vault" "8200" "vault"

# Check if vault is already running; hold process so process-compose shows "running" not "completed"
if curl -sf "$VAULT_ADDR/v1/sys/health" >/dev/null 2>&1; then
    echo "[VAULT] Already running at $VAULT_ADDR; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
fi

# Check if vault command exists
if ! command -v vault &>/dev/null; then
    echo "[VAULT] ERROR: 'vault' not found in PATH"
    echo "[VAULT] Install via: brew install vault"
    exit 1
fi

echo "[VAULT] Starting Vault dev server at $VAULT_ADDR..."

# Start vault in dev mode
# Dev mode automatically:
# - Uses in-memory storage (no disk persistence)
# - Initializes and unseals the vault
# - Creates a root token
# - Enables KV v2 secrets engine at secret/
exec vault server -dev -dev-listen-address=127.0.0.1:8200 \
    -dev-root-token-id=dev-root-token 2>&1 | while IFS= read -r line; do
    echo "[VAULT] $line"

    # Extract and save root token
    if [[ "$line" =~ Root\ Token:\ ([a-zA-Z0-9\.\-]+) ]]; then
        echo "${BASH_REMATCH[1]}" > "$VAULT_TOKEN_FILE"
        echo "[VAULT] Root token saved to $VAULT_TOKEN_FILE"
    fi
done
