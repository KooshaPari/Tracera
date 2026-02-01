# Vault Quick Reference

## TL;DR

```bash
# Local dev without Vault (fastest)
cp .env.example .env
vi .env  # Set USE_VAULT=false
make dev

# Local dev with Vault
make dev  # Vault starts automatically
./scripts/vault-setup-secrets.sh .env
# Edit .env: USE_VAULT=true
# Restart: Ctrl+R on go-backend in TUI

# Production
# Use proper Vault with storage backend + TLS + AppRole auth
# See docs/guides/SECRETS_MANAGEMENT.md
```

## Common Commands

### View Secrets
```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=dev-root-token

vault kv list secret/tracertm           # List all
vault kv get secret/tracertm/jwt         # Get JWT secret
vault kv get secret/tracertm/database    # Get DB credentials
```

### Update Secrets
```bash
# Rotate JWT secret
vault kv put secret/tracertm/jwt \
  secret="$(openssl rand -hex 32)" \
  expiry="24h"

# Update DB password only
vault kv patch secret/tracertm/database \
  password="new-password"
```

### Migrate from .env
```bash
./scripts/vault-setup-secrets.sh .env
```

### Emergency: Disable Vault
```bash
# In .env
USE_VAULT=false

# Restart
make dev
```

## Secret Paths

| Path | Contents |
|------|----------|
| `secret/tracertm/jwt` | JWT signing secret, expiry |
| `secret/tracertm/database` | PostgreSQL credentials |
| `secret/tracertm/redis` | Redis connection URL |
| `secret/tracertm/neo4j` | Neo4j credentials |
| `secret/tracertm/s3` | MinIO/S3 credentials |
| `secret/tracertm/workos` | WorkOS auth (optional) |
| `secret/tracertm/github` | GitHub App (optional) |
| `secret/tracertm/ai/voyage` | VoyageAI API key (optional) |
| `secret/tracertm/ai/openai` | OpenAI API key (optional) |
| `secret/tracertm/ai/anthropic` | Anthropic API key (optional) |

## Environment Variables

```bash
# Vault integration
USE_VAULT=true                      # Enable Vault
VAULT_ADDR=http://127.0.0.1:8200   # Vault address
VAULT_TOKEN=dev-root-token          # Auth token (dev only)

# Fallback when USE_VAULT=false
JWT_SECRET=<hex-string>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
NEO4J_URI=bolt://...
S3_ENDPOINT=http://...
# ... etc (see .env.example)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Vault not starting | `pkill vault && make dev` |
| Connection refused | Check `VAULT_ADDR` and `vault status` |
| Auth errors | Use `VAULT_TOKEN=dev-root-token` (dev mode) |
| Missing secrets | Run `./scripts/vault-setup-secrets.sh .env` |
| Config load fails | Verify secret exists: `vault kv get secret/tracertm/jwt` |

## Code Examples

### Load Config
```go
import "github.com/kooshapari/tracertm-backend/internal/config"

cfg, err := config.LoadConfigFromVault()
// Automatically uses Vault if USE_VAULT=true
```

### Direct Vault Access
```go
import "github.com/kooshapari/tracertm-backend/internal/vault"

client, _ := vault.NewClient()
jwtSecret, _ := client.GetJWTSecret(ctx)
dbCreds, _ := client.GetDatabaseCredentials(ctx)
```

## Files

- 📄 `/backend/internal/vault/client.go` - Vault client
- 📄 `/backend/internal/config/vault_config.go` - Config loader
- 🔧 `/scripts/vault-if-not-running.sh` - Start Vault dev
- 🔧 `/scripts/vault-setup-secrets.sh` - Migrate .env → Vault
- 📋 `/.env.example` - Secret template
- 📖 `/docs/guides/SECRETS_MANAGEMENT.md` - Full docs

## Production Checklist

- [ ] Use proper storage (Consul/etcd/cloud KMS, not in-memory)
- [ ] Enable TLS/HTTPS
- [ ] Use AppRole or cloud IAM auth (not root token)
- [ ] Enable audit logging
- [ ] Implement secret rotation
- [ ] Monitor seal status
- [ ] Separate namespaces per environment
- [ ] Backup Vault data regularly

## Links

- 📚 [Full Guide](../guides/SECRETS_MANAGEMENT.md)
- 🔗 [Vault Docs](https://developer.hashicorp.com/vault/docs)
- 🔗 [Production Hardening](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening)
