# WorkOS AuthKit Full Authentication Restoration

## Changes Made

### ✅ Removed All Dev Mode Fallbacks

1. **`src/tracertm/api/main.py`**
   - Removed dev mode fallback from `verify_token()` - now requires WorkOS
   - Removed dev mode fallback from `auth_guard()` - now requires WorkOS authentication
   - Updated WebSocket endpoint to require WorkOS authentication token

2. **`src/tracertm/services/workos_auth_service.py`**
   - Fixed PyJWT attribute compatibility (`Algorithm` vs `algorithm`)
   - No dev mode fallbacks - requires WORKOS_CLIENT_ID

### ✅ Updated WebSocket Authentication

**Backend (`src/tracertm/api/main.py`):**
- WebSocket endpoint now requires authentication token
- Token can be provided via:
  - Query parameter: `ws://localhost:8000/ws?token=YOUR_TOKEN`
  - Authorization header: `Authorization: Bearer YOUR_TOKEN`
- Rejects connections without valid WorkOS tokens

**Frontend (`frontend/apps/web/src/api/websocket.ts`):**
- WebSocketManager now requires token getter function
- Automatically includes token in WebSocket URL
- Uses WorkOS `getAccessToken()` for authentication
- Falls back to localStorage `auth_token` if token getter not provided

**Frontend (`frontend/apps/web/src/providers/AppProviders.tsx`):**
- WebSocketInitializer now uses WorkOS `useAuth()` hook
- Passes `getAccessToken` function to WebSocketManager
- Only connects when user is authenticated via WorkOS

## Authentication Flow

### HTTP API Endpoints

1. Client makes request with `Authorization: Bearer <token>` header
2. Backend `auth_guard()` extracts token
3. `verify_token()` calls `workos_auth_service.verify_access_token()`
4. WorkOS JWKS validates token signature
5. Returns user claims or raises error

### WebSocket Connections

1. Client calls `getAccessToken()` from WorkOS SDK
2. WebSocketManager includes token in URL: `ws://localhost:8000/ws?token=<token>`
3. Backend WebSocket endpoint extracts token from query params
4. Backend verifies token using WorkOS AuthKit
5. Connection accepted or rejected based on token validity

## Required Configuration

### Backend (.env)

```bash
WORKOS_CLIENT_ID=your_client_id_here
WORKOS_API_KEY=your_api_key_here
WORKOS_AUTHKIT_DOMAIN=your_domain.authkit.app

# Optional
WORKOS_JWKS_URL=https://your-domain.authkit.app/oauth2/jwks
WORKOS_JWT_ISSUER=https://your-domain.authkit.app
WORKOS_JWT_AUDIENCE=your_client_id_here
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

### Frontend (.env.local)

```bash
VITE_WORKOS_CLIENT_ID=your_client_id_here
VITE_API_URL=http://localhost:8000
```

## No Dev Mode Fallbacks

**All endpoints now require WorkOS authentication:**
- ❌ No "dev-user" fallback
- ❌ No "accept all" behavior
- ❌ No bypassing authentication
- ✅ Full WorkOS AuthKit hosted UI required
- ✅ All requests must include valid WorkOS tokens

## Testing

### Test API Authentication

```bash
# Without token - should fail
curl http://localhost:8000/api/v1/projects
# Expected: 500 error or "Authorization required"

# With token - should work
curl -H "Authorization: Bearer YOUR_WORKOS_TOKEN" \
     http://localhost:8000/api/v1/projects
```

### Test WebSocket Authentication

```bash
# Without token - should fail
wscat -c ws://localhost:8000/ws
# Expected: Connection closed with code 1008

# With token - should work
wscat -c "ws://localhost:8000/ws?token=YOUR_WORKOS_TOKEN"
```

### Test from Frontend

1. User signs in via WorkOS hosted UI
2. Frontend receives access token
3. All API calls include `Authorization: Bearer <token>` header
4. WebSocket connects with token in URL
5. Backend validates all tokens via WorkOS

## Error Handling

### Missing WORKOS_CLIENT_ID

**Backend:**
- Will raise `ValueError: WORKOS_CLIENT_ID is required for AuthKit`
- All endpoints will fail with authentication errors
- No dev mode fallback

### Invalid Token

**Backend:**
- Returns `ValueError: Invalid token` or specific JWT error
- HTTP endpoints return 500 with error message
- WebSocket connections closed with code 1008

### Expired Token

**Frontend:**
- WorkOS SDK handles token refresh automatically
- WebSocketManager will get fresh token on reconnect
- API client should handle 401 and refresh tokens

## Files Modified

1. `src/tracertm/api/main.py`
   - Removed dev mode from `verify_token()`
   - Removed dev mode from `auth_guard()`
   - Added authentication to WebSocket endpoint

2. `src/tracertm/services/workos_auth_service.py`
   - Fixed PyJWT `Algorithm` attribute compatibility

3. `frontend/apps/web/src/api/websocket.ts`
   - Added token getter support
   - Made `connect()` async
   - Includes token in WebSocket URL

4. `frontend/apps/web/src/providers/AppProviders.tsx`
   - Updated WebSocketInitializer to use WorkOS `getAccessToken()`

5. `frontend/apps/web/src/stores/websocketStore.ts`
   - Made `connect()` async

## Migration Notes

**If you were relying on dev mode:**
- You must now configure WorkOS in `.env`
- All requests require valid WorkOS tokens
- WebSocket requires authentication
- No workarounds or bypasses available

**For production:**
- Ensure `WORKOS_CLIENT_ID` is set
- Ensure `WORKOS_API_KEY` is set
- Configure CORS origins properly
- Test authentication flow end-to-end

## Status

✅ **Full WorkOS AuthKit authentication restored**
✅ **No dev mode fallbacks**
✅ **No "accept all" behavior**
✅ **WebSocket requires authentication**
✅ **All endpoints require WorkOS tokens**
