# Token Bridge Security Guide

## Overview

The Token Bridge provides bidirectional authentication between:
- **WorkOS RS256 tokens** (asymmetric, user authentication)
- **Internal HS256 service tokens** (symmetric, service-to-service)

## Token Lifecycle

### User Tokens (RS256)

**Source**: WorkOS AuthKit
**Algorithm**: RS256 (RSA with SHA-256)
**Validation**: JWKS public keys from WorkOS
**Lifetime**: Managed by WorkOS (typically 1 hour)
**Refresh**: Via WorkOS refresh tokens

**Claims**:
```json
{
  "sub": "user_01HXYZ...",
  "email": "user@example.com",
  "org_id": "org_01HXYZ...",
  "aud": "client_01HXYZ...",
  "iss": "https://api.workos.com/",
  "exp": 1234567890,
  "iat": 1234567000
}
```

**Usage**:
- Frontend → Backend authentication
- API requests from logged-in users
- Long-lived sessions with refresh tokens

### Service Tokens (HS256)

**Source**: Token Bridge
**Algorithm**: HS256 (HMAC with SHA-256)
**Validation**: Shared secret (`JWT_SECRET`)
**Lifetime**: **5 minutes** (hardcoded)
**Refresh**: Create new token when needed

**Claims**:
```json
{
  "sub": "user_01HXYZ...",
  "org_id": "org_01HXYZ...",
  "type": "service",
  "exp": 1234567890,
  "iat": 1234567000
}
```

**Usage**:
- Go backend → Python backend
- Python backend → Go backend
- Temporary authentication for cross-service calls

## Validation Flow

```
┌─────────────────────────────────────────────────────┐
│ Token arrives at endpoint                           │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ TokenBridge.ValidateToken()                         │
└─────────────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Try RS256        │    │ Try HS256        │
│ (JWKS)           │    │ (shared secret)  │
└──────────────────┘    └──────────────────┘
         │                       │
         │ Success               │ Success
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ User Token       │    │ Service Token    │
│ - Sync profile   │    │ - Direct use     │
│ - Full claims    │    │ - Short TTL      │
└──────────────────┘    └──────────────────┘
```

## Secret Management

### JWT_SECRET Requirements

- **Minimum length**: 32 bytes (256 bits)
- **Generation**: `openssl rand -base64 64`
- **Sharing**: **MUST** be identical in Go and Python environments
- **Storage**: Environment variable, never in code
- **Rotation**: See rotation procedure below

### Environment Variables

**Required for All Environments**:
```bash
JWT_SECRET=your-secret-min-32-bytes
WORKOS_CLIENT_ID=client_your_id
WORKOS_API_KEY=sk_your_key
```

**Optional (with defaults)**:
```bash
WORKOS_API_BASE_URL=https://api.workos.com
WORKOS_JWKS_URL=https://api.workos.com/sso/jwks/${WORKOS_CLIENT_ID}
WORKOS_JWT_ISSUER=https://api.workos.com/
WORKOS_JWT_AUDIENCE=${WORKOS_CLIENT_ID}
```

## Security Best Practices

### 1. Token Expiry Policies

| Token Type | TTL | Rationale |
|------------|-----|-----------|
| User (RS256) | 1 hour | WorkOS default, balances security and UX |
| Service (HS256) | **5 minutes** | Minimal window for compromise |
| Refresh token | 30 days | WorkOS default |

### 2. JWKS Caching

- **Cache duration**: 24 hours
- **Automatic refresh**: On validation failure
- **Key rotation**: Handled automatically via JWKS
- **Fallback**: Retry with cache refresh on kid mismatch

### 3. Audience/Issuer Validation

**Always validate**:
- `aud` (audience): Must match `WORKOS_CLIENT_ID`
- `iss` (issuer): Must match `WORKOS_API_BASE_URL`
- `exp` (expiry): Must be in the future
- `nbf` (not before): Must be in the past

### 4. Algorithm Confusion Prevention

**Mitigations**:
- Explicit algorithm whitelist: `["RS256"]` or `["HS256"]`
- No algorithm=none allowed
- Header `alg` must match expected method
- Separate code paths for RS256 vs HS256

## Secret Rotation Procedure

### Pre-Rotation

1. **Notification**: Announce rotation window (e.g., 24 hours)
2. **Backup**: Save current `JWT_SECRET`
3. **Generate**: New secret with `openssl rand -base64 64`

### During Rotation

**Option A: Zero-Downtime (Dual Validation)**

1. Deploy with **both** old and new secrets
2. Validate against both (accept either)
3. Issue new tokens with new secret only
4. Wait for old tokens to expire (5 min + buffer)
5. Remove old secret

**Option B: Brief Outage (Simple)**

1. Maintenance window announcement
2. Update `JWT_SECRET` in all services simultaneously
3. Restart all services
4. Users re-authenticate (WorkOS tokens unaffected)

### Post-Rotation

1. **Verify**: Test service-to-service calls
2. **Monitor**: Check logs for validation failures
3. **Cleanup**: Remove old secret from backups after 30 days

## Audit Logging

### Required Log Events

**Authentication Events**:
```go
log.Printf("Validated RS256 token for user %s", claims.UserID)
log.Printf("Validated HS256 service token for user %s", claims.UserID)
log.Printf("Token validation failed: %v", err)
```

**Token Creation**:
```go
log.Printf("Created bridge token for user %s (org %s), expires in 5 minutes", userID, orgID)
```

**JWKS Operations**:
```go
log.Printf("Refreshed JWKS cache with %d keys", keyCount)
log.Printf("JWKS refresh failed: %v", err)
```

### Log Fields (Structured)

```json
{
  "event": "token_validated",
  "type": "rs256" | "hs256",
  "user_id": "user_01HXYZ...",
  "org_id": "org_01HXYZ...",
  "token_type": "service" | null,
  "expires_at": "2024-01-30T12:34:56Z",
  "ip": "192.168.1.1",
  "timestamp": "2024-01-30T12:30:00Z"
}
```

## Threat Model

### Threats Mitigated

1. **Token Forgery**: RS256 uses asymmetric crypto, HS256 uses strong shared secret
2. **Replay Attacks**: Short TTL (5 min) for service tokens
3. **Algorithm Confusion**: Explicit algorithm validation
4. **Key Compromise**: JWKS auto-rotation, manual secret rotation
5. **Token Theft**: HTTPS-only transport, short expiry

### Residual Risks

1. **HS256 Secret Compromise**:
   - Impact: Attacker can create service tokens
   - Mitigation: 5-minute TTL limits exposure window
   - Response: Immediate secret rotation

2. **JWKS Endpoint Compromise**:
   - Impact: Attacker controls RS256 validation
   - Mitigation: HTTPS + WorkOS infrastructure security
   - Response: Contact WorkOS, rotate to new client

3. **Man-in-the-Middle**:
   - Impact: Token interception
   - Mitigation: TLS 1.3 required, certificate pinning
   - Response: Revoke tokens, rotate secrets

## Compliance Checklist

- [ ] `JWT_SECRET` is at least 32 bytes
- [ ] Secrets stored in secure vault (not in `.env` files in production)
- [ ] HTTPS enforced for all endpoints
- [ ] Token expiry validated on every request
- [ ] Audience and issuer claims validated
- [ ] JWKS cache refreshed daily
- [ ] Failed validation attempts logged
- [ ] Secret rotation procedure tested
- [ ] Audit logs retained for 90+ days
- [ ] Service tokens never sent to frontend

## Troubleshooting

### "Token validation failed for both RS256 and HS256"

**Causes**:
- Invalid token format
- Expired token
- Wrong secret or JWKS URL
- Network issue fetching JWKS

**Debug**:
```bash
# Check token structure
echo $TOKEN | cut -d. -f2 | base64 -d | jq .

# Verify JWKS endpoint
curl $WORKOS_JWKS_URL

# Test secret
echo $JWT_SECRET | wc -c  # Should be ≥32
```

### "Public key not found for kid"

**Causes**:
- JWKS cache stale
- Token signed with rotated key
- Wrong JWKS URL

**Resolution**:
1. Force JWKS refresh: `bridge.RefreshJWKS()`
2. Verify `WORKOS_JWKS_URL` matches WorkOS dashboard
3. Check WorkOS key rotation logs

### "Invalid audience/issuer"

**Causes**:
- Environment variable mismatch
- Token from different WorkOS client
- Copy-paste error in config

**Resolution**:
1. Verify `WORKOS_CLIENT_ID` matches token `aud`
2. Check token issuer: `jwt.io` to decode
3. Ensure all services use same WorkOS client

## References

- [RFC 7519: JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7517: JSON Web Key (JWK)](https://tools.ietf.org/html/rfc7517)
- [WorkOS AuthKit Documentation](https://workos.com/docs/user-management/authkit)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
