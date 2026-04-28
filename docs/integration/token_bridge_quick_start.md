# Token Bridge Quick Start

## Setup (5 minutes)

### 1. Generate Shared Secret

```bash
# Generate a secure 64-byte secret
openssl rand -base64 64 > .jwt_secret

# Add to .env (Go backend)
echo "JWT_SECRET=$(cat .jwt_secret)" >> backend/.env

# Add to .env (Python backend)
echo "JWT_SECRET=$(cat .jwt_secret)" >> .env
```

### 2. Configure WorkOS

Add to **both** backend `.env` files:

```bash
# Get these from https://dashboard.workos.com/
WORKOS_CLIENT_ID=client_01HXYZ...
WORKOS_API_KEY=sk_live_...
WORKOS_JWKS_URL=https://api.workos.com/sso/jwks/${WORKOS_CLIENT_ID}
```

### 3. Initialize Token Bridge

**Go (backend/internal/auth/)**:
```go
import "github.com/kooshapari/tracertm-backend/internal/auth"

// In main.go or setup function
bridge, err := auth.NewTokenBridge(
    []byte(os.Getenv("JWT_SECRET")),
    os.Getenv("WORKOS_JWKS_URL"),
    os.Getenv("WORKOS_CLIENT_ID"),  // audience
    "https://api.workos.com/",      // issuer
)
if err != nil {
    log.Fatal(err)
}
defer bridge.Close()

// Create adapter for middleware
authAdapter := auth.NewBridgeAuthAdapter(bridge, db)
```

**Python (src/tracertm/api/)**:
```python
from tracertm.services.token_bridge import get_token_bridge

# Dependency injection (already in deps.py)
bridge = get_token_bridge()  # Auto-configured from env vars
```

## Usage Examples

### Validating User Tokens (Frontend → Backend)

**Scenario**: User logged in via WorkOS, sends RS256 token

**Go**:
```go
// Middleware already handles this
func AuthMiddleware(adapter *auth.BridgeAuthAdapter) echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            token := extractToken(c)
            user, err := adapter.ValidateToken(c.Request().Context(), token)
            if err != nil {
                return echo.ErrUnauthorized
            }
            c.Set("user", user)
            return next(c)
        }
    }
}
```

**Python**:
```python
# FastAPI dependency (already in deps.py)
from fastapi import Depends
from tracertm.api.deps import auth_guard

@router.get("/me")
async def get_user(claims: dict = Depends(auth_guard)):
    return {
        "user_id": claims["sub"],
        "email": claims.get("email"),
        "org_id": claims.get("org_id"),
    }
```

### Creating Service Tokens (Backend → Backend)

**Scenario**: Go service needs to call Python API

**Go → Python**:
```go
// In Go service
bridgeToken, err := bridge.CreateBridgeToken(userID, orgID)
if err != nil {
    return err
}

// Call Python API
req, _ := http.NewRequest("GET", "http://python-api:8000/api/v1/items", nil)
req.Header.Set("Authorization", "Bearer " + bridgeToken)
resp, err := http.DefaultClient.Do(req)
```

**Python → Go**:
```python
# In Python service
from tracertm.services.token_bridge import get_token_bridge

bridge = get_token_bridge()
service_token = bridge.create_bridge_token(user_id, org_id)

# Call Go API
headers = {"Authorization": f"Bearer {service_token}"}
response = httpx.get("http://go-api:8080/api/v1/links", headers=headers)
```

### Testing Tokens

**Test RS256 Token** (requires real WorkOS token):
```bash
# Get token from browser (after login)
TOKEN="eyJhbGciOiJSUzI1NiIs..."

# Test Go backend
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/me

# Test Python backend
curl -H "Authorization: Bearer $TOKEN" http://localhost:4000/api/v1/me
```

**Test HS256 Service Token**:
```go
// Generate test token
bridge, _ := auth.NewTokenBridge(
    []byte("test-secret-at-least-32-bytes-long"),
    "http://unused", "", "",
)
token, _ := bridge.CreateBridgeToken("user_123", "org_456")
fmt.Println(token)
```

```python
# Validate in Python
from tracertm.services.token_bridge import TokenBridge

bridge = TokenBridge(
    hs_secret="test-secret-at-least-32-bytes-long",
    jwks_url="http://unused",
)
claims = bridge.validate_token(token)
print(claims)
```

## Verification Checklist

- [ ] Both backends have same `JWT_SECRET`
- [ ] `JWT_SECRET` is ≥32 bytes
- [ ] WorkOS credentials configured
- [ ] User token validates in both backends
- [ ] Service token validates in both backends
- [ ] Service token expires after 5 minutes
- [ ] JWKS cache refreshes automatically

## Common Issues

### "HS256 secret must be at least 32 bytes"

**Fix**:
```bash
# Check secret length
echo $JWT_SECRET | wc -c

# Regenerate if too short
openssl rand -base64 64
```

### "Token validation failed for both RS256 and HS256"

**Debug**:
```bash
# Decode token (without validating)
echo $TOKEN | cut -d. -f2 | base64 -d | jq .

# Check which algorithm was used
echo $TOKEN | cut -d. -f1 | base64 -d | jq .alg
```

### "Public key not found for kid"

**Fix**:
```bash
# Verify JWKS URL returns keys
curl $WORKOS_JWKS_URL

# Check WorkOS dashboard for correct client ID
echo $WORKOS_CLIENT_ID
```

## Next Steps

- Read [Token Bridge Security Guide](./token_bridge_security.md)
- Set up [secret rotation procedure](./token_bridge_security.md#secret-rotation-procedure)
- Configure [audit logging](./token_bridge_security.md#audit-logging)
- Review [threat model](./token_bridge_security.md#threat-model)
