#!/usr/bin/env bash
# Initialize Vault with development secrets
# This script migrates secrets from .env to Vault KV v2 store

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-dev-root-token}"
ENV_FILE="${1:-.env}"

export VAULT_ADDR
export VAULT_TOKEN

echo "[VAULT-SETUP] Initializing secrets in Vault from $ENV_FILE..."

# Wait for Vault to be ready
echo "[VAULT-SETUP] Waiting for Vault to be ready..."
for i in {1..30}; do
    if vault status >/dev/null 2>&1; then
        echo "[VAULT-SETUP] Vault is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "[VAULT-SETUP] ERROR: Vault not ready after 30s"
        exit 1
    fi
    sleep 1
done

# Enable KV v2 secrets engine (if not already enabled in dev mode)
if ! vault secrets list | grep -q "^secret/"; then
    echo "[VAULT-SETUP] Enabling KV v2 secrets engine at secret/..."
    vault secrets enable -version=2 -path=secret kv
fi

# Function to safely extract env var from file
get_env_var() {
    local var_name=$1
    local env_file=$2
    grep "^${var_name}=" "$env_file" 2>/dev/null | cut -d'=' -f2- | sed 's/^["'\'']\(.*\)["'\'']$/\1/'
}

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "[VAULT-SETUP] WARNING: $ENV_FILE not found, using placeholder values"
    echo "[VAULT-SETUP] You should update these secrets in Vault after initial setup"

    # Set minimal required secrets
    vault kv put secret/tracertm/jwt \
        secret="$(openssl rand -hex 32)" \
        expiry="24h"

    vault kv put secret/tracertm/database \
        url="postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm" \
        host="localhost" \
        port="5432" \
        user="tracertm" \
        password="tracertm_password" \
        name="tracertm"

    vault kv put secret/tracertm/redis \
        url="redis://localhost:6379" \
        host="localhost" \
        port="6379"

    vault kv put secret/tracertm/neo4j \
        uri="bolt://localhost:7687" \
        user="neo4j" \
        password="neo4j_password" \
        auth="neo4j/neo4j_password"

    vault kv put secret/tracertm/s3 \
        endpoint="http://127.0.0.1:9000" \
        access_key_id="minioadmin" \
        secret_access_key="minioadmin" \
        bucket="tracertm" \
        region="us-east-1"

    echo "[VAULT-SETUP] ✅ Initialized with placeholder secrets"
    exit 0
fi

# Migrate secrets from .env
echo "[VAULT-SETUP] Migrating secrets from $ENV_FILE..."

# JWT Secrets
JWT_SECRET=$(get_env_var "JWT_SECRET" "$ENV_FILE")
if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "YOUR_RANDOM_32_BYTE_HEX_STRING" ]; then
    echo "[VAULT-SETUP] WARNING: JWT_SECRET not set or is placeholder, generating new secret..."
    JWT_SECRET=$(openssl rand -hex 32)
    echo "[VAULT-SETUP] ⚠️  New JWT_SECRET generated. All existing tokens will be invalidated."
fi

vault kv put secret/tracertm/jwt \
    secret="$JWT_SECRET" \
    expiry="$(get_env_var 'JWT_EXPIRY' "$ENV_FILE" || echo '24h')"

echo "[VAULT-SETUP] ✅ JWT secrets stored"

# Database Credentials
vault kv put secret/tracertm/database \
    url="$(get_env_var 'DATABASE_URL' "$ENV_FILE")" \
    host="$(get_env_var 'DB_HOST' "$ENV_FILE")" \
    port="$(get_env_var 'DB_PORT' "$ENV_FILE")" \
    user="$(get_env_var 'DB_USER' "$ENV_FILE")" \
    password="$(get_env_var 'DB_PASSWORD' "$ENV_FILE")" \
    name="$(get_env_var 'DB_NAME' "$ENV_FILE")"

echo "[VAULT-SETUP] ✅ Database credentials stored"

# Redis Credentials
vault kv put secret/tracertm/redis \
    url="$(get_env_var 'REDIS_URL' "$ENV_FILE")" \
    host="$(get_env_var 'REDIS_HOST' "$ENV_FILE")" \
    port="$(get_env_var 'REDIS_PORT' "$ENV_FILE")"

echo "[VAULT-SETUP] ✅ Redis credentials stored"

# Neo4j Credentials
vault kv put secret/tracertm/neo4j \
    uri="$(get_env_var 'NEO4J_URI' "$ENV_FILE")" \
    user="$(get_env_var 'NEO4J_USER' "$ENV_FILE")" \
    password="$(get_env_var 'NEO4J_PASSWORD' "$ENV_FILE")" \
    auth="$(get_env_var 'NEO4J_AUTH' "$ENV_FILE")"

echo "[VAULT-SETUP] ✅ Neo4j credentials stored"

# S3 Credentials
vault kv put secret/tracertm/s3 \
    endpoint="$(get_env_var 'S3_ENDPOINT' "$ENV_FILE")" \
    access_key_id="$(get_env_var 'S3_ACCESS_KEY_ID' "$ENV_FILE")" \
    secret_access_key="$(get_env_var 'S3_SECRET_ACCESS_KEY' "$ENV_FILE")" \
    bucket="$(get_env_var 'S3_BUCKET' "$ENV_FILE")" \
    region="$(get_env_var 'S3_REGION' "$ENV_FILE")"

echo "[VAULT-SETUP] ✅ S3 credentials stored"

# WorkOS Credentials (if present)
WORKOS_API_KEY=$(get_env_var 'WORKOS_API_KEY' "$ENV_FILE")
WORKOS_CLIENT_ID=$(get_env_var 'WORKOS_CLIENT_ID' "$ENV_FILE")

if [ -n "$WORKOS_API_KEY" ] && [ -n "$WORKOS_CLIENT_ID" ]; then
    vault kv put secret/tracertm/workos \
        api_key="$WORKOS_API_KEY" \
        client_id="$WORKOS_CLIENT_ID" \
        redirect_uri="$(get_env_var 'WORKOS_REDIRECT_URI' "$ENV_FILE")"
    echo "[VAULT-SETUP] ✅ WorkOS credentials stored"
fi

# GitHub App Credentials (if present)
GITHUB_APP_ID=$(get_env_var 'GITHUB_APP_ID' "$ENV_FILE")
GITHUB_APP_CLIENT_SECRET=$(get_env_var 'GITHUB_APP_CLIENT_SECRET' "$ENV_FILE")

if [ -n "$GITHUB_APP_ID" ] && [ "$GITHUB_APP_ID" != "YOUR_APP_ID" ]; then
    vault kv put secret/tracertm/github \
        app_id="$GITHUB_APP_ID" \
        client_id="$(get_env_var 'GITHUB_APP_CLIENT_ID' "$ENV_FILE")" \
        client_secret="$GITHUB_APP_CLIENT_SECRET" \
        webhook_secret="$(get_env_var 'GITHUB_WEBHOOK_SECRET' "$ENV_FILE")" \
        private_key_path="$(get_env_var 'GITHUB_PRIVATE_KEY_PATH' "$ENV_FILE")"
    echo "[VAULT-SETUP] ✅ GitHub App credentials stored"
fi

# AI Provider API Keys (if present)
VOYAGE_API_KEY=$(get_env_var 'VOYAGE_API_KEY' "$ENV_FILE")
OPENAI_API_KEY=$(get_env_var 'OPENAI_API_KEY' "$ENV_FILE")
ANTHROPIC_API_KEY=$(get_env_var 'ANTHROPIC_API_KEY' "$ENV_FILE")

if [ -n "$VOYAGE_API_KEY" ]; then
    vault kv put secret/tracertm/ai/voyage \
        api_key="$VOYAGE_API_KEY" \
        model="$(get_env_var 'VOYAGE_MODEL' "$ENV_FILE")" \
        dimensions="$(get_env_var 'VOYAGE_DIMENSIONS' "$ENV_FILE")"
    echo "[VAULT-SETUP] ✅ VoyageAI credentials stored"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    vault kv put secret/tracertm/ai/openai \
        api_key="$OPENAI_API_KEY"
    echo "[VAULT-SETUP] ✅ OpenAI credentials stored"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    vault kv put secret/tracertm/ai/anthropic \
        api_key="$ANTHROPIC_API_KEY"
    echo "[VAULT-SETUP] ✅ Anthropic credentials stored"
fi

echo ""
echo "[VAULT-SETUP] ============================================"
echo "[VAULT-SETUP] ✅ All secrets migrated to Vault successfully"
echo "[VAULT-SETUP] ============================================"
echo ""
echo "[VAULT-SETUP] Vault Address: $VAULT_ADDR"
echo "[VAULT-SETUP] Root Token: $VAULT_TOKEN"
echo ""
echo "[VAULT-SETUP] List secrets with:"
echo "  export VAULT_ADDR=$VAULT_ADDR"
echo "  export VAULT_TOKEN=$VAULT_TOKEN"
echo "  vault kv list secret/tracertm"
echo ""
echo "[VAULT-SETUP] Read a secret with:"
echo "  vault kv get secret/tracertm/jwt"
echo ""
echo "[VAULT-SETUP] ⚠️  SECURITY NOTICE:"
echo "  - Dev mode uses in-memory storage (secrets lost on restart)"
echo "  - For production, use Vault with proper storage backend"
echo "  - Consider rotating the JWT secret to invalidate old tokens"
echo ""
