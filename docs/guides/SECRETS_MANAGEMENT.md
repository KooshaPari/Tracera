# Secrets Management with HashiCorp Vault

## Overview

TraceRTM uses [HashiCorp Vault](https://www.vaultproject.io/) for secure secrets management in production environments. For local development, secrets can be loaded from `.env` files or Vault dev mode.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TraceRTM Application                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Config Loader (internal/config/vault_config.go)     │  │
│  │                                                       │  │
│  │  • Checks USE_VAULT=true/false                       │  │
│  │  • Falls back to .env if Vault disabled              │  │
│  │  • Validates required secrets                        │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │                                         │
│                    ▼                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Vault Client (internal/vault/client.go)             │  │
│  │                                                       │  │
│  │  • Health checks                                     │  │
│  │  • Reads secrets from KV v2                          │  │
│  │  • Type-safe credential structs                      │  │
│  └─────────────────┬─────────────────────────────────────┘  │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     ▼
       ┌─────────────────────────────┐
       │   HashiCorp Vault Server    │
       │                             │
       │  KV v2 Secrets Engine:     │
       │  secret/tracertm/           │
       │    ├── jwt                  │
       │    ├── database             │
       │    ├── redis                │
       │    ├── neo4j                │
       │    ├── s3                   │
       │    ├── workos               │
       │    ├── github               │
       │    └── ai/                  │
       │         ├── voyage          │
       │         ├── openai          │
       │         └── anthropic       │
       └─────────────────────────────┘
```

## Quick Start

### Local Development (with .env)

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set required values:**
   ```bash
   # Generate JWT secret
   openssl rand -hex 32

   # Update .env with your values
   vi .env
   ```

3. **Ensure Vault is disabled:**
   ```bash
   # In .env
   USE_VAULT=false
   ```

4. **Start the application:**
   ```bash
   make dev
   ```

### Local Development (with Vault dev mode)

1. **Install Vault:**
   ```bash
   brew install vault
   ```

2. **Start Vault dev server (automatic via process-compose):**
   ```bash
   make dev
   # Vault starts automatically on port 8200
   ```

3. **Initialize secrets from `.env`:**
   ```bash
   ./scripts/vault-setup-secrets.sh .env
   ```

4. **Enable Vault in configuration:**
   ```bash
   # In .env
   USE_VAULT=true
   VAULT_ADDR=http://127.0.0.1:8200
   VAULT_TOKEN=dev-root-token
   ```

5. **Restart application:**
   ```bash
   # In process-compose TUI: Ctrl+R on go-backend
   # Or restart with: make dev
   ```

### Production Setup

**⚠️ WARNING: Dev mode is NOT secure for production!**

For production:
1. Deploy Vault with proper storage backend (Consul, etcd, or cloud KMS)
2. Use proper authentication (AppRole, Kubernetes, Cloud IAM)
3. Enable TLS/HTTPS
4. Implement secret rotation
5. Configure audit logging

See [Vault Production Hardening](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening) for details.

## Secrets Structure

### JWT Secrets (`secret/tracertm/jwt`)
```yaml
secret: <32-byte hex string>     # Generated with: openssl rand -hex 32
expiry: 24h                       # Token expiration time
```

### Database Credentials (`secret/tracertm/database`)
```yaml
url: postgresql+asyncpg://tracertm:password@localhost:5432/tracertm
host: localhost
port: 5432
user: tracertm
password: <secure-password>
name: tracertm
```

### Redis (`secret/tracertm/redis`)
```yaml
url: redis://localhost:6379
host: localhost
port: 6379
```

### Neo4j (`secret/tracertm/neo4j`)
```yaml
uri: bolt://localhost:7687
user: neo4j
password: <secure-password>
auth: neo4j/<secure-password>
```

### S3/MinIO (`secret/tracertm/s3`)
```yaml
endpoint: http://127.0.0.1:9000
access_key_id: <access-key>
secret_access_key: <secret-key>
bucket: tracertm
region: us-east-1
```

### WorkOS (Optional) (`secret/tracertm/workos`)
```yaml
api_key: sk_live_...
client_id: client_...
redirect_uri: http://localhost:4000/auth/callback
```

### GitHub App (Optional) (`secret/tracertm/github`)
```yaml
app_id: 123456
client_id: Iv_XXXXXXXXXX
client_secret: <secret>
webhook_secret: <secret>
private_key_path: /path/to/key.pem
```

### AI Providers (Optional) (`secret/tracertm/ai/*`)

**VoyageAI** (`secret/tracertm/ai/voyage`):
```yaml
api_key: pa_XXXXXXXXXX
model: voyage-3.5
dimensions: 1024
```

**OpenAI** (`secret/tracertm/ai/openai`):
```yaml
api_key: sk-...
```

**Anthropic** (`secret/tracertm/ai/anthropic`):
```yaml
api_key: sk-ant-...
```

## Vault Operations

### View All Secrets
```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=dev-root-token

# List all secret paths
vault kv list secret/tracertm

# Read a specific secret
vault kv get secret/tracertm/jwt
vault kv get secret/tracertm/database
```

### Update a Secret
```bash
# Update JWT secret
vault kv put secret/tracertm/jwt \
  secret="$(openssl rand -hex 32)" \
  expiry="24h"

# Update database password
vault kv patch secret/tracertm/database \
  password="new-secure-password"
```

### Delete a Secret
```bash
vault kv delete secret/tracertm/workos
```

### Secret Rotation
```bash
# 1. Generate new secret
NEW_JWT_SECRET=$(openssl rand -hex 32)

# 2. Update Vault
vault kv put secret/tracertm/jwt secret="$NEW_JWT_SECRET" expiry="24h"

# 3. Restart application to pick up new secret
# In process-compose TUI: Ctrl+R on go-backend
```

## Code Integration

### Loading Config with Vault

```go
package main

import (
    "github.com/kooshapari/tracertm-backend/internal/config"
)

func main() {
    // Automatically uses Vault if USE_VAULT=true
    cfg, err := config.LoadConfigFromVault()
    if err != nil {
        log.Fatalf("Failed to load config: %v", err)
    }

    // Use config
    fmt.Printf("Database: %s\n", cfg.DatabaseURL)
    fmt.Printf("JWT Secret length: %d\n", len(cfg.JWTSecret))
}
```

### Direct Vault Client Usage

```go
package main

import (
    "context"
    "github.com/kooshapari/tracertm-backend/internal/vault"
)

func main() {
    ctx := context.Background()

    // Create client
    client, err := vault.NewClient()
    if err != nil {
        log.Fatal(err)
    }

    // Health check
    if err := client.HealthCheck(ctx); err != nil {
        log.Fatal("Vault not healthy:", err)
    }

    // Get JWT secret
    jwtSecret, err := client.GetJWTSecret(ctx)
    if err != nil {
        log.Fatal(err)
    }

    // Get database credentials
    dbCreds, err := client.GetDatabaseCredentials(ctx)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("DB URL: %s\n", dbCreds.URL)
}
```

## Environment Variables

### Required for Vault
```bash
USE_VAULT=true                     # Enable Vault integration
VAULT_ADDR=http://127.0.0.1:8200  # Vault server address
VAULT_TOKEN=dev-root-token         # Authentication token
```

### Fallback (when USE_VAULT=false)
All secrets must be set in `.env` or environment variables:
- `JWT_SECRET`
- `DATABASE_URL`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `REDIS_URL`, `REDIS_HOST`, `REDIS_PORT`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET`, `S3_REGION`
- Optional: `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `GITHUB_APP_*`, AI provider keys

## Security Best Practices

### Development
✅ **Do:**
- Use Vault dev mode for local testing
- Keep `.env` out of version control (already in `.gitignore`)
- Use `vault-setup-secrets.sh` to migrate from `.env` to Vault
- Generate strong JWT secrets: `openssl rand -hex 32`

❌ **Don't:**
- Commit `.env` files to Git
- Use placeholder passwords in production
- Share `VAULT_TOKEN` in public channels
- Use dev mode Vault in production

### Production
✅ **Do:**
- Use proper Vault storage backend (Consul, etcd, cloud KMS)
- Enable TLS/HTTPS for Vault
- Use AppRole or cloud IAM authentication (not root tokens)
- Implement secret rotation policies
- Enable Vault audit logging
- Use separate Vault namespaces per environment
- Monitor Vault health and seal status

❌ **Don't:**
- Use in-memory storage (dev mode)
- Use root tokens for application authentication
- Disable audit logging
- Store secrets in application code
- Use weak passwords or default credentials

## Troubleshooting

### Vault Not Starting
```bash
# Check if port 8200 is in use
lsof -i :8200

# Kill existing Vault process
pkill vault

# Restart with process-compose
make dev
```

### Connection Refused
```bash
# Check Vault status
vault status

# Verify VAULT_ADDR
echo $VAULT_ADDR

# Test connectivity
curl http://127.0.0.1:8200/v1/sys/health
```

### Authentication Errors
```bash
# Verify token
vault token lookup

# In dev mode, use default token
export VAULT_TOKEN=dev-root-token

# Test authentication
vault kv list secret/tracertm
```

### Missing Secrets
```bash
# List all secrets
vault kv list secret/tracertm

# Check if secret exists
vault kv get secret/tracertm/jwt

# If missing, run setup script
./scripts/vault-setup-secrets.sh .env
```

### Config Loading Fails
```go
// Error: "failed to get JWT secret"
// Solution: Ensure secret exists in Vault

vault kv put secret/tracertm/jwt \
  secret="$(openssl rand -hex 32)" \
  expiry="24h"
```

## Migration Guide

### From .env to Vault

1. **Ensure `.env` has all required secrets:**
   ```bash
   # Check for placeholders
   grep PLACEHOLDER .env

   # Replace with real values
   vi .env
   ```

2. **Run migration script:**
   ```bash
   ./scripts/vault-setup-secrets.sh .env
   ```

3. **Verify migration:**
   ```bash
   vault kv list secret/tracertm
   vault kv get secret/tracertm/jwt
   vault kv get secret/tracertm/database
   ```

4. **Enable Vault in config:**
   ```bash
   # In .env
   USE_VAULT=true
   ```

5. **Restart application and verify:**
   ```bash
   make dev
   # Check logs for "Loading config from Vault..."
   ```

### From Vault back to .env (Emergency)

1. **Export secrets from Vault:**
   ```bash
   vault kv get -format=json secret/tracertm/jwt | \
     jq -r '.data.data.secret' > /tmp/jwt_secret
   ```

2. **Update `.env`:**
   ```bash
   JWT_SECRET=$(cat /tmp/jwt_secret)
   # ... update other secrets
   ```

3. **Disable Vault:**
   ```bash
   USE_VAULT=false
   ```

4. **Restart application:**
   ```bash
   make dev
   ```

## Files Reference

- **Backend Code:**
  - `/backend/internal/vault/client.go` - Vault client implementation
  - `/backend/internal/config/vault_config.go` - Config loader with Vault integration

- **Scripts:**
  - `/scripts/vault-if-not-running.sh` - Starts Vault dev server
  - `/scripts/vault-setup-secrets.sh` - Migrates secrets from .env to Vault

- **Configuration:**
  - `/.env.example` - Template with all required secrets
  - `/process-compose.yaml` - Vault service definition

- **Documentation:**
  - This file: `/docs/guides/SECRETS_MANAGEMENT.md`

## Related Resources

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- [Vault KV Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2)
- [Vault Production Hardening](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening)
- [Vault Best Practices](https://developer.hashicorp.com/vault/tutorials/best-practices)
