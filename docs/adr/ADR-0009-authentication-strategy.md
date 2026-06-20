# ADR-0009: Authentication Strategy

**Status:** Accepted
**Date:** 2026-02-04
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM requires secure authentication for:

1. **Web application:** Users log in via browser
2. **API access:** REST endpoints, GraphQL, MCP tools
3. **CLI tools:** Desktop app, command-line interface
4. **SSO integration:** Enterprise customers need Google/Microsoft/Okta login
5. **Session management:** Stateless auth (JWT) or stateful (Redis sessions)

Authentication requirements:
- **Multi-tenant:** Support multiple organizations/projects
- **Role-based access:** Admin, Editor, Viewer roles
- **API keys:** For automation (CI/CD, scripts)
- **OAuth providers:** Google, GitHub, Microsoft (optional)
- **Security:** Protection against CSRF, XSS, token theft

Technology constraints:
- **Backend:** FastAPI (Python), Echo (Go)
- **Frontend:** React 19 + TanStack Router
- **Database:** PostgreSQL (user storage)
- **Cache:** Redis (session storage, if needed)

## Decision

We will use **WorkOS SSO** for authentication with **JWT tokens** for API access.

**Primary auth flow:**
1. **Web login:** WorkOS SSO (Google, Microsoft, SAML)
2. **Token storage:** JWT (access token) + Refresh token (HttpOnly cookie)
3. **API authentication:** Bearer token (`Authorization: Bearer <jwt>`)
4. **CLI authentication:** OAuth device flow OR API key

**Session management:** Stateless (JWT) with Redis-backed refresh token rotation

## Rationale

### Technology Stack

**From pyproject.toml:**
```toml
dependencies = [
    "workos>=5.40.0",          # WorkOS SSO SDK
    "pyjwt>=2.11.0",           # JWT encoding/decoding
    "cryptography>=46.0.4",    # Encryption for secrets
    "bcrypt>=5.0.0",           # Password hashing (fallback)
    "keyring>=25.7.0",         # CLI credential storage
]
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Client (Web/CLI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. User clicks "Login with Google"                  │  │
│  │  2. Redirect to WorkOS OAuth endpoint                │  │
│  │  3. User authenticates with IdP (Google, Microsoft)  │  │
│  │  4. WorkOS redirects back with auth code             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ POST /api/auth/callback?code=...
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Auth Handler (/api/auth/)                           │  │
│  │  1. Exchange code for WorkOS user profile            │  │
│  │  2. Create/update user in PostgreSQL                 │  │
│  │  3. Generate JWT access token (15 min expiry)        │  │
│  │  4. Generate refresh token (7 day expiry)            │  │
│  │  5. Store refresh token in Redis (for rotation)      │  │
│  │  6. Set HttpOnly cookie (refresh_token)              │  │
│  │  7. Return JSON ({ access_token, user })             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Store user
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL (Users table)                        │
│  users:                                                      │
│    ├─ id (UUID)                                             │
│    ├─ email (unique)                                        │
│    ├─ name                                                  │
│    ├─ workos_user_id (unique, nullable)                    │
│    ├─ role (admin, editor, viewer)                         │
│    └─ created_at                                            │
└─────────────────────────────────────────────────────────────┘
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid-123",           // User ID
    "email": "user@example.com",      // Email
    "name": "Alice Smith",            // Display name
    "role": "editor",                 // Role (admin, editor, viewer)
    "org_id": "org-uuid-456",         // Organization ID
    "exp": 1735689600,                // Expiry (15 min from issue)
    "iat": 1735688700,                // Issued at
    "jti": "token-id-789"             // Token ID (for revocation)
  },
  "signature": "..."
}
```

### WorkOS Integration (Python)

```python
from workos import WorkOS
from fastapi import APIRouter, HTTPException

workos = WorkOS(api_key=settings.WORKOS_API_KEY)

@router.get("/auth/login")
async def login():
    """Redirect to WorkOS SSO login."""
    authorization_url = workos.sso.get_authorization_url(
        organization="org_123",  # From request or config
        redirect_uri="https://app.tracertm.com/auth/callback",
        provider="GoogleOAuth",  # Or "MicrosoftOAuth", "OktaSAML"
    )
    return RedirectResponse(authorization_url)

@router.get("/auth/callback")
async def callback(code: str, session: AsyncSession):
    """Handle OAuth callback."""
    # Exchange code for user profile
    profile = workos.sso.get_profile_and_token(code=code)

    # Create or update user
    user = await user_service.get_or_create_by_email(
        session=session,
        email=profile.email,
        name=profile.first_name + " " + profile.last_name,
        workos_user_id=profile.id,
    )

    # Generate JWT
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    # Store refresh token in Redis
    await redis.setex(f"refresh:{refresh_token}", 7 * 24 * 3600, user.id)

    # Set HttpOnly cookie
    response = JSONResponse({"access_token": access_token, "user": user.dict()})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )
    return response
```

### JWT Middleware (FastAPI Dependency)

```python
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract user from JWT."""
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await user_service.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Usage in routes
@router.get("/api/projects")
async def list_projects(user: User = Depends(get_current_user)):
    return await project_service.list_by_user(user.id)
```

### CLI Authentication (Device Flow)

```python
# CLI command: tracertm login
import webbrowser
import http.server

def login_cli():
    """OAuth device flow for CLI."""
    # 1. Start local server to receive callback
    server = http.server.HTTPServer(("localhost", 8888), CallbackHandler)

    # 2. Open browser to WorkOS OAuth
    auth_url = f"https://api.workos.com/sso/authorize?client_id={CLIENT_ID}&redirect_uri=http://localhost:8888/callback"
    webbrowser.open(auth_url)

    # 3. Wait for callback
    server.handle_request()

    # 4. Store token in keyring
    keyring.set_password("tracertm", "access_token", token)
    print("✅ Logged in successfully")

# Usage in CLI commands
@cli.command()
def list_projects():
    token = keyring.get_password("tracertm", "access_token")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.tracertm.com/projects", headers=headers)
    print(response.json())
```

## Alternatives Rejected

### Alternative 1: Username/Password (Self-hosted Auth)

- **Description:** Store bcrypt-hashed passwords in PostgreSQL
- **Pros:** Full control, no third-party dependency
- **Cons:** Security responsibility (password reset, 2FA, breach detection), poor UX (users prefer SSO)
- **Why Rejected:** WorkOS provides enterprise SSO (Google, Microsoft, Okta) out-of-box. Self-hosting auth is high security risk.

### Alternative 2: Auth0

- **Description:** Third-party auth platform (alternative to WorkOS)
- **Pros:** Mature, feature-rich, supports all OAuth providers
- **Cons:** Expensive ($240/month for SSO), complex pricing, vendor lock-in
- **Why Rejected:** WorkOS simpler pricing ($125/month for SSO), better developer experience. Auth0 overkill for traceability app.

### Alternative 3: Firebase Authentication

- **Description:** Google's managed auth service
- **Pros:** Free tier, easy integration, mobile SDKs
- **Cons:** Vendor lock-in (Google), limited enterprise SSO (no SAML), poor B2B features
- **Why Rejected:** TraceRTM targets enterprise teams (need SAML, AD sync). Firebase is consumer-focused.

### Alternative 4: Session Cookies (Stateful Auth)

- **Description:** Store session IDs in Redis, use cookies for auth
- **Pros:** Easier revocation (delete session from Redis), no JWT expiry issues
- **Cons:** Stateful (requires Redis lookup per request), harder horizontal scaling
- **Why Rejected:** JWT stateless auth scales better (no database lookup). Refresh token rotation handles revocation.

## Consequences

### Positive

- **Enterprise SSO:** Google Workspace, Microsoft 365, Okta (critical for B2B sales)
- **Stateless auth:** JWT scales horizontally (no session database)
- **Security:** WorkOS handles OIDC/SAML complexity, reduces attack surface
- **Developer experience:** `workos` SDK abstracts OAuth flows
- **CLI support:** OAuth device flow works for desktop apps

### Negative

- **WorkOS dependency:** Vendor lock-in (mitigated by standard OAuth/SAML)
- **Cost:** $125/month for SSO (acceptable for B2B product)
- **JWT expiry:** 15-minute access tokens require refresh token flow
- **Token revocation:** JWT can't be revoked before expiry (use short expiry + refresh rotation)

### Neutral

- **API keys:** For automation (CI/CD), generate long-lived API keys (separate from JWT)
- **2FA:** WorkOS supports 2FA (delegated to IdP like Google)
- **Audit logs:** Track login events, token generation in PostgreSQL

## Implementation

### Affected Components

- `src/tracertm/services/workos_auth_service.py` - WorkOS integration
- `src/tracertm/api/routers/auth.py` - Auth endpoints (/login, /callback, /refresh)
- `src/tracertm/api/middleware/jwt_middleware.py` - JWT verification
- `frontend/apps/web/src/auth/AuthProvider.tsx` - React auth context
- `src/tracertm/cli/auth.py` - CLI login command

### Migration Strategy

**Phase 1: WorkOS Setup (Week 1)**
- Create WorkOS account
- Configure SSO providers (Google, Microsoft)
- Implement `/auth/login`, `/auth/callback` endpoints

**Phase 2: JWT Infrastructure (Week 2)**
- Generate JWT access/refresh tokens
- Implement refresh token rotation (Redis)
- Add JWT middleware to all API routes

**Phase 3: Frontend Integration (Week 3)**
- React AuthProvider (context)
- Login/logout flows
- Token refresh logic (axios interceptors)

**Phase 4: CLI Support (Week 4)**
- OAuth device flow for CLI
- Store tokens in system keyring
- `tracertm login`, `tracertm logout` commands

### Rollout Plan

- **Phase 1:** MVP (WorkOS SSO only, no email/password)
- **Phase 2:** API keys for automation
- **Phase 3:** CLI authentication
- **Phase 4:** Advanced features (SAML, AD sync)

### Success Criteria

- [ ] Users can log in with Google/Microsoft
- [ ] JWT tokens valid for 15 minutes
- [ ] Refresh tokens rotate on use (7-day expiry)
- [ ] API endpoints reject invalid/expired tokens
- [ ] CLI login works via device flow
- [ ] Logout clears tokens (client + server)

## References

- [WorkOS Documentation](https://workos.com/docs)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OAuth Device Flow](https://oauth.net/2/device-flow/)
- [ADR-0006: Deployment Architecture](ADR-0006-deployment-architecture.md)
- [src/tracertm/services/workos_auth_service.py](../../src/tracertm/services/workos_auth_service.py)

---

**Notes:**
- **WorkOS pricing:** $125/month for SSO (up to 1000 users), $0.05/user after
- **JWT secret:** Store in environment variable (`SECRET_KEY`), rotate periodically
- **Token revocation:** Short expiry (15 min) + refresh rotation prevents long-lived stolen tokens
- **CSRF protection:** SameSite=Lax cookies + double-submit cookie pattern
