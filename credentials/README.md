# Credentials

Authentication configurations and credential patterns.

## Purpose
Standardize authentication and credential management.

## Mutability
Locked - Credential configs reference secrets, never hardcode.

## Structure
```
credentials/
├── auth/               # Authentication configs
│   ├── oauth2/
│   │   └── provider.yaml
│   ├── oidc/
│   │   └── idp.yaml
│   └── jwt/
│       └── jwt.yaml
├── patterns/          # Credential patterns
│   └── sdk-auth.go   # Example SDK auth
└── mfa/               # MFA configurations
    ├── totp.yaml
    └── hardware-key.yaml
```

## Auth Patterns
| Type | Use Case |
|------|----------|
| OAuth2 | Third-party auth (Google, GitHub) |
| OIDC | Identity federation |
| JWT | Stateless API auth |
| API Keys | Service-to-service |
| mTLS | Secure service communication |

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Load auth configs for SDK initialization |
| Write | Generate SDK auth code |
| Enforce | Validate credential rotation |

## SDK Auth Example
```go
// credentials/patterns/sdk-auth.go
package auth

// AuthConfig holds authentication configuration
type Config struct {
    Method     string // "oauth2", "jwt", "apikey"
    ClientID   string
    ClientSecret string // Reference: ${env:CLIENT_SECRET}
    Scopes     []string
}

// NewAuth creates authenticated client
func NewAuth(cfg Config) (*Client, error) {
    secret, err := secretmanager.Get(cfg.ClientSecret)
    if err != nil {
        return nil, err
    }
    // Initialize based on method
}
```

## Related
- [secrets/](../secrets/) - Secret storage
- [security/](../security/) - Security scanning
- [libs/](../libs/) - Auth libraries
