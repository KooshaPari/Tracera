# Secrets

Sensitive configuration requiring secure storage and management.

## Purpose
Manage secrets, rotation policies, and scanning configurations.

## Mutability
Locked - Never commit secrets. Use reference patterns.

## Structure
```
secrets/
├── patterns/          # Secret handling patterns
│   ├── env-var.yml    # Environment variable secrets
│   ├── vault.yml      # HashiCorp Vault patterns
│   └── aws-secrets.yml # AWS Secrets Manager patterns
├── rotation/          # Rotation policies
│   └── rotation-policy.yml
├── scanning/          # Secret scanning configs
│   ├── gitleaks.toml
│   └── trufflehog.yml
└── templates/         # Secret templates (placeholders only)
    └── secret-template.yml
```

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Reference via secret manager (never hardcode) |
| Write | Store in Vault/AWS Secrets Manager |
| Rotate | Automated via rotation policies |
| Scan | Run gitleaks/trufflehog in CI |

## Do's and Don'ts
### DO
```yaml
# ✅ Reference secrets
database:
  password: ${env:DATABASE_PASSWORD}
```

### DON'T
```yaml
# ❌ Never hardcode
database:
  password: "my-secret-password"
```

## Related
- [credentials/](../credentials/) - Authentication configs
- [configs/](../configs/) - Configs that reference secrets
