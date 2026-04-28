# Auth Adapters

## At a Glance
- **Purpose:** Unified authentication system with OAuth 2.0 flows, token management, and multi-factor authentication.
- **Best For:** Applications needing secure authentication, multi-tenant sessions, and comprehensive auth workflows.
- **Key Building Blocks:** `AuthManager`, `AuthProvider` adapters, `MFAAdapter` implementations, token management.

## Core Capabilities
- Authorization code flow with PKCE support across multiple providers.
- Token refresh and rotation workflows with secure storage.
- Multi-factor authentication (MFA) via email, SMS, TOTP, and push notifications.
- Framework middleware for FastAPI/Starlette and Flask.
- Provider adapters for Auth0, AuthKit, and generic OAuth2 providers.
- TUI widgets for credential management in terminal apps.

## Getting Started

### Installation
```bash
pip install pheno-sdk
# Auth adapters are included in the main package
```

### Minimal Example
```python
from pheno.auth import AuthManager, Credentials
from pheno.adapters.auth.providers import register_provider, AuthKitProvider
from pheno.auth.token_manager import FileTokenManager

# Register provider once at startup
register_provider("authkit", AuthKitProvider)

auth = AuthManager(token_manager=FileTokenManager("~/.config/auth/tokens.json"))

# Exchange an authorization code (obtained via browser redirect)
credentials = Credentials(
    authorization_code="...",
    redirect_uri="http://localhost:3000/callback",
)
result = await auth.authenticate("authkit", credentials)

if result.success and result.tokens:
    print("Access token", result.tokens.access_token)
```

## How It Works
- `AuthManager` coordinates providers, token storage, and MFA flows.
- Provider adapters in `pheno.adapters.auth.providers` handle OAuth endpoints.
- MFA adapters in `pheno.adapters.auth.mfa` provide multi-factor authentication.
- `FileTokenManager` (or custom `TokenManager` implementations) persists tokens securely.
- Optional session helpers in `pheno.auth.session_broker` integrate with web frameworks.

## Usage Recipes
- Protect API routes with FastAPI dependency `get_current_user` provided by middleware.
- Use MFA adapters for secure multi-factor authentication flows.
- Integrate with workflow orchestration for multi-step account provisioning workflows.
- Combine with database adapters to persist user profiles inside tenant-aware schemas.

## Interoperability
- Works with configuration management to load client IDs/secrets per environment.
- Emits login events that can be published via event systems for auditing.
- Coordinates with service orchestration for multi-step account provisioning workflows.

## Operations & Observability
- Log authentication attempts with structured logging by injecting a logger into middleware configuration.
- Track authentication metrics (success/failure, refresh count) via observability systems.
- Configure rate limiting on OAuth routes using proxy gateway to protect against abuse.

## Testing & QA
- Use the in-memory session store for unit tests.
- Mock OAuth providers with provided test utilities or stub HTTP responses.
- Use MCP QA tools for comprehensive authentication testing.

## Troubleshooting
- **Invalid redirect URI:** ensure the redirect matches exactly what is registered with the provider.
- **Token refresh failing:** verify refresh tokens are stored and refresh scopes granted.
- **Session not found:** confirm your session backend is initialized (Redis URL, encryption keys).

## Primary API Surface
- `AuthManager(token_manager, credential_manager=None)`
- `register_provider("authkit", AuthKitProvider)` from `pheno.adapters.auth.providers`
- `auth.authenticate(provider_name, Credentials(...))`
- `FileTokenManager(storage_path)` for persistence
- `SessionOAuthBroker` helpers for distributing tokens to HTTP clients

## Additional Resources
- Examples: `src/pheno/auth/examples/`
- Tests: `tests/auth/`
- Related concepts: [Operations](../guides/operations.md), [Patterns](../concepts/patterns.md)
