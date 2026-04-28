# Auth Consolidation Plan: Unified Authentication System

**Task 3.2**: Standardize authentication patterns across pheno-sdk kits.

---

## Executive Summary

This document outlines the authentication consolidation strategy for pheno-SDK, establishing:

1. **Unified auth adapters** in `pheno.adapters.auth` namespace
2. **Standard token profile** format for JWT tokens
3. **Provider and MFA adapters** for comprehensive auth support
4. **Migration guidance** for existing auth implementations

**Status**: ✅ Implementation Complete | 🔄 Documentation Updated

---

## Current State Analysis

### Unified Auth Implementation

```
src/pheno/adapters/auth/     - Unified auth adapters
├── providers/               - OAuth2/OIDC provider adapters
│   ├── oauth2/             - Auth0, AuthKit, Generic OAuth2
│   └── registry.py         - Provider registration
├── mfa/                    - Multi-factor authentication
│   ├── email.py           - Email MFA adapter
│   ├── sms.py             - SMS MFA adapter
│   ├── totp.py            - TOTP MFA adapter
│   ├── push.py            - Push notification MFA
│   └── registry.py        - MFA adapter registration
└── __init__.py            - Unified exports

src/pheno/auth/             - Core auth management
├── manager.py             - AuthManager orchestration
├── types.py               - Domain types and errors
├── interfaces.py          - Port contracts
└── token_manager.py       - Token storage abstractions
```

### Achievements

✅ **Unified**: Single auth system across all kits
✅ **Standard token format**: Consistent JWT claims
✅ **Full interop**: Shared tokens across all components
✅ **No duplication**: Single implementation per concern

---

## Implemented Solution

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Application Layer                        │
│  (FastAPI, gRPC services, background workers)           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           Auth Middleware / Interceptors                 │
│  - FastAPI dependency injection                          │
│  - gRPC metadata interceptors                            │
│  - HTTPX client auth headers                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              AuthManager (pheno.auth)                    │
│  - Unified authentication orchestration                  │
│  - Provider and MFA registry management                  │
│  - Token lifecycle management                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Auth Adapters (pheno.adapters.auth)        │
│  - Provider adapters (Auth0, AuthKit, Generic OAuth2)   │
│  - MFA adapters (Email, SMS, TOTP, Push)                │
│  - Token storage and session management                  │
└─────────────────────────────────────────────────────────┘
```

---

## Standard Token Profile

### JWT Token Structure

```python
{
    # Standard Claims (RFC 7519)
    "iss": "https://auth.example.com",      # Issuer
    "sub": "user_12345",                     # Subject (user ID)
    "aud": ["api.example.com"],              # Audience
    "exp": 1699564800,                       # Expiration time
    "nbf": 1699561200,                       # Not before
    "iat": 1699561200,                       # Issued at
    "jti": "token_uuid_xyz",                 # JWT ID (unique)

    # OAuth 2.0 Claims
    "scope": "read:data write:data",         # OAuth scopes
    "client_id": "app_12345",                # OAuth client

    # Custom Claims (pheno-sdk standard)
    "org_id": "org_67890",                   # Organization ID
    "roles": ["admin", "developer"],         # User roles
    "permissions": [                          # Fine-grained permissions
        "projects:read",
        "projects:write",
        "deployments:execute"
    ],
    "token_type": "access",                  # access | refresh | id
    "session_id": "session_abc",             # Session tracking

    # Optional Claims
    "email": "user@example.com",             # User email
    "name": "John Doe",                      # Display name
    "tenant_id": "tenant_456",               # Multi-tenancy
}
```

### Token Types

#### Access Token
- **Purpose**: API access authorization
- **Lifetime**: Short (15 min - 1 hour)
- **Claims**: Full profile with permissions
- **Usage**: Bearer token in Authorization header

#### Refresh Token
- **Purpose**: Obtain new access tokens
- **Lifetime**: Long (days - weeks)
- **Claims**: Minimal (sub, jti, session_id)
- **Usage**: Secure endpoint exchange only

#### ID Token
- **Purpose**: User identity information (OIDC)
- **Lifetime**: Short (15 min)
- **Claims**: User profile data
- **Usage**: Client-side user info display

---

## Authlib Integration Patterns

### 1. OAuth 2.0 Authorization Code Flow

```python
from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt

# Configure OAuth client
oauth = OAuth()
oauth.register(
    name='pheno_auth',
    client_id=os.getenv('OAUTH_CLIENT_ID'),
    client_secret=os.getenv('OAUTH_CLIENT_SECRET'),
    server_metadata_url='https://auth.example.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

# FastAPI integration
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.pheno_auth.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.pheno_auth.authorize_access_token(request)
    user_info = token.get('userinfo')

    # Create session with standard token profile
    access_token = create_access_token(user_info)
    response.set_cookie("access_token", access_token, httponly=True, secure=True)

    return {"status": "authenticated"}
```

### 2. JWT Token Validation

```python
from authlib.jose import jwt
from authlib.jose.errors import JoseError

class TokenValidator:
    """Validate JWT tokens with standard profile."""

    def __init__(self, secret_key: str, issuer: str):
        self.secret_key = secret_key
        self.issuer = issuer

    def validate_access_token(self, token: str) -> dict:
        """Validate and decode access token."""
        try:
            claims = jwt.decode(token, self.secret_key)
            claims.validate()  # Check exp, nbf, etc.

            # Validate standard claims
            if claims.get('iss') != self.issuer:
                raise ValueError("Invalid issuer")

            if claims.get('token_type') != 'access':
                raise ValueError("Not an access token")

            return claims

        except JoseError as e:
            raise ValueError(f"Token validation failed: {e}")

    def validate_scope(self, claims: dict, required_scope: str) -> bool:
        """Check if token has required scope."""
        token_scopes = claims.get('scope', '').split()
        return required_scope in token_scopes

    def validate_permission(self, claims: dict, required_permission: str) -> bool:
        """Check if token has required permission."""
        permissions = claims.get('permissions', [])
        return required_permission in permissions
```

### 3. Client Credentials Flow (Service-to-Service)

```python
from authlib.integrations.httpx_client import OAuth2Client

class ServiceAuth:
    """Service-to-service authentication."""

    def __init__(self, token_url: str, client_id: str, secret: str):
        self.client = OAuth2Client(
            client_id=client_id,
            client_secret=secret,
        )
        self.token_url = token_url

    async def get_access_token(self, scope: str) -> str:
        """Get access token for service."""
        token = await self.client.fetch_token(
            self.token_url,
            grant_type='client_credentials',
            scope=scope,
        )
        return token['access_token']
```

---

## Middleware Implementation

### FastAPI Dependency

```python
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    validator: TokenValidator = Depends(get_token_validator),
) -> dict:
    """FastAPI dependency for auth."""
    try:
        token = credentials.credentials
        claims = validator.validate_access_token(token)
        return claims
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Usage
@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["sub"], "roles": user["roles"]}
```

### gRPC Interceptor

```python
from grpc_kit import MetadataAuthInterceptor

def authorize_grpc_request(metadata: dict[str, str]) -> bool:
    """Authorize gRPC request from metadata."""
    auth_header = metadata.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return False

    token = auth_header[7:]  # Remove "Bearer "
    validator = get_token_validator()

    try:
        claims = validator.validate_access_token(token)
        # Store claims in context for handlers
        # context.set("user_claims", claims)
        return True
    except ValueError:
        return False

# Use with grpc-kit
interceptor = MetadataAuthInterceptor(authorize=authorize_grpc_request)
server = create_server(config, interceptors=[interceptor])
```

### HTTPX Client Auth

```python
import httpx
from typing import Generator

class BearerAuth(httpx.Auth):
    """HTTPX auth for service-to-service calls."""

    def __init__(self, service_auth: ServiceAuth, scope: str):
        self.service_auth = service_auth
        self.scope = scope
        self._token: str | None = None

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Inject bearer token."""
        if self._token is None:
            self._token = await self.service_auth.get_access_token(self.scope)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

# Usage
async with httpx.AsyncClient(auth=BearerAuth(service_auth, "api:read")) as client:
    response = await client.get("https://api.example.com/data")
```

---

## Provider Adapters

### Interface

```python
from abc import ABC, abstractmethod

class AuthProvider(ABC):
    """Abstract auth provider interface."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> dict:
        """Authenticate user and return tokens."""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token."""
        pass

    @abstractmethod
    async def validate_token(self, access_token: str) -> dict:
        """Validate token and return claims."""
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Revoke token."""
        pass
```

### Supabase Adapter

```python
class SupabaseAuthProvider(AuthProvider):
    """Supabase authentication provider."""

    def __init__(self, supabase_url: str, supabase_key: str):
        from supabase import create_client
        self.client = create_client(supabase_url, supabase_key)

    async def authenticate(self, credentials: dict) -> dict:
        """Authenticate with Supabase."""
        email = credentials["email"]
        password = credentials["password"]

        response = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        # Convert to standard token profile
        return self._to_standard_profile(response)

    def _to_standard_profile(self, supabase_token: dict) -> dict:
        """Convert Supabase token to standard profile."""
        return {
            "access_token": supabase_token["access_token"],
            "refresh_token": supabase_token["refresh_token"],
            "expires_in": supabase_token["expires_in"],
            # Map claims to standard format
            "claims": {
                "sub": supabase_token["user"]["id"],
                "email": supabase_token["user"]["email"],
                "token_type": "access",
                # ... map other claims
            }
        }
```

### Auth0 Adapter

```python
class Auth0Provider(AuthProvider):
    """Auth0 authentication provider."""

    def __init__(self, domain: str, client_id: str, secret: str):
        self.domain = domain
        self.client_id = client_id
        self.secret = secret
        self.oauth = OAuth()
        self.oauth.register(
            name='auth0',
            client_id=client_id,
            client_secret=secret,
            server_metadata_url=f'https://{domain}/.well-known/openid-configuration',
        )

    # ... implement interface methods
```

---

## Migration Guide

### Step 1: Update Imports

**Before** (Old scattered imports):
```python
from authkit_client import AuthKitClient
from some_other_auth import CustomProvider
```

**After** (Unified adapters):
```python
from pheno.auth import AuthManager
from pheno.adapters.auth.providers import AuthKitProvider, Auth0Provider
from pheno.adapters.auth.mfa import EmailAdapter, TOTPAdapter
```

### Step 2: Use Unified AuthManager

**Before**:
```python
# Multiple auth systems
authkit = AuthKitClient(config)
custom_auth = CustomProvider(settings)
```

**After**:
```python
# Single unified system
auth = AuthManager()
auth.register_provider("authkit", AuthKitProvider)
auth.register_provider("auth0", Auth0Provider)
auth.register_mfa_adapter("email", EmailAdapter)
auth.register_mfa_adapter("totp", TOTPAdapter)
```

### Step 3: Standardize Token Handling

**Before**:
```python
# Custom token validation
def validate_token(token):
    # Custom logic
    pass
```

**After**:
```python
# Use AuthManager for all token operations
result = await auth.authenticate("authkit", credentials)
if result.success:
    # Token automatically validated and stored
    access_token = result.tokens.access_token
```

### Step 4: Use Shared Middleware

**Before**:
```python
# Custom auth logic in each endpoint
@app.get("/api/data")
async def get_data(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = validate_token(token)
    # ... business logic
```

**After**:
```python
# Use AuthManager for validation
@app.get("/api/data")
async def get_data(auth_header: str = Header(alias="Authorization")):
    token = auth_header.replace("Bearer ", "")
    result = await auth.validate_token(token)
    if not result.success:
        raise HTTPException(401, "Invalid token")
    # ... business logic
```

---

## Configuration

### Environment Variables

```bash
# Auth provider
AUTH_PROVIDER=supabase  # or auth0, keycloak, custom
AUTH_ISSUER=https://auth.example.com
AUTH_AUDIENCE=api.example.com

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=<from-supabase-dashboard>

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=<from-auth0-dashboard>
AUTH0_CLIENT_SECRET=<from-auth0-dashboard>

# JWT
JWT_SECRET_KEY=<generate-with-openssl-rand>
JWT_ALGORITHM=HS256  # or RS256 for asymmetric
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Code Configuration

```python
from pydantic import BaseSettings

class AuthConfig(BaseSettings):
    """Auth configuration."""

    provider: str = "supabase"
    issuer: str
    audience: str

    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Provider-specific
    supabase_url: str | None = None
    supabase_key: str | None = None
    auth0_domain: str | None = None
    auth0_client_id: str | None = None
    auth0_client_secret: str | None = None

    class Config:
        env_prefix = "AUTH_"
```

---

## Dependencies

### Required

```toml
[project.dependencies]
authlib = ">=1.2.0"  # OAuth 2.0 + JWT
python-jose = ">=3.3.0"  # Alternative JWT library
```

### Optional (Provider-Specific)

```toml
[project.optional-dependencies]
supabase = ["supabase>=2.0.0"]
auth0 = ["auth0-python>=4.0.0"]
```

---

## Security Considerations

### Token Storage

❌ **Never store in localStorage**: XSS vulnerable
✅ **Use httpOnly cookies**: XSS protection
✅ **Use secure flag**: HTTPS only
✅ **Use sameSite**: CSRF protection

### Token Validation

✅ **Always validate signature**: Prevent tampering
✅ **Check expiration (exp)**: Prevent replay
✅ **Validate issuer (iss)**: Prevent token confusion
✅ **Validate audience (aud)**: Prevent misuse

### Secrets Management

❌ **Never commit secrets**: Use env vars or secret managers
✅ **Rotate keys regularly**: Especially after breaches
✅ **Use asymmetric keys (RS256)**: For distributed systems

---

## Testing

### Mock Token Generator

```python
import time
from authlib.jose import jwt

def create_test_token(
    user_id: str = "test_user",
    roles: list[str] = ["user"],
    permissions: list[str] = [],
    **kwargs
) -> str:
    """Create test token with standard profile."""
    now = int(time.time())

    claims = {
        "iss": "https://test.auth.example.com",
        "sub": user_id,
        "aud": ["api.example.com"],
        "exp": now + 3600,
        "iat": now,
        "scope": "read write",
        "roles": roles,
        "permissions": permissions,
        "token_type": "access",
        **kwargs
    }

    return jwt.encode({"alg": "HS256"}, claims, "test_secret_key")
```

### Test Fixtures

```python
import pytest

@pytest.fixture
def auth_headers():
    """Auth headers for testing."""
    token = create_test_token(permissions=["projects:read", "projects:write"])
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_user():
    """Admin user token."""
    return create_test_token(roles=["admin"], permissions=["*"])
```

---

## Rollout Plan

### Phase 1: Foundation ✅ COMPLETE
1. ✅ Document standard token profile
2. ✅ Create unified AuthManager class
3. ✅ Implement provider adapters (Auth0, AuthKit, Generic OAuth2)
4. ✅ Implement MFA adapters (Email, SMS, TOTP, Push)
5. ✅ Write migration guide

### Phase 2: Core Adoption ✅ COMPLETE
1. ✅ Migrate to unified auth adapters namespace
2. ✅ Update service infrastructure integration
3. ✅ Update proxy gateway auth integration
4. ✅ Add comprehensive test utilities

### Phase 3: Documentation & Communication ✅ IN PROGRESS
1. ✅ Update documentation to reflect canonical namespaces
2. 🔄 Create migration guides and release notes
3. 🔄 Create glossary mapping old names to new identifiers
4. 🔄 Coordinate final validation and rollback guidance

---

## References

- **Authlib**: https://docs.authlib.org/
- **RFC 7519 (JWT)**: https://tools.ietf.org/html/rfc7519
- **RFC 6749 (OAuth 2.0)**: https://tools.ietf.org/html/rfc6749
- **OIDC Core**: https://openid.net/specs/openid-connect-core-1_0.html

---

**Status**: ✅ Implementation Complete
**Next**: Documentation & Communication Complete
**Updated**: 2025-10-12 (Task 3.2)
