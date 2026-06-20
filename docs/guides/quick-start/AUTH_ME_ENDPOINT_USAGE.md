# /auth/me Endpoint - Quick Start Guide

Get current authenticated user information from WorkOS.

---

## Endpoint

```
GET /api/v1/auth/me
```

---

## Authentication

Requires a valid WorkOS JWT access token in the Authorization header.

```bash
Authorization: Bearer <access_token>
```

---

## Quick Examples

### Using curl

```bash
# With valid access token
curl -H "Authorization: Bearer eyJhbGc..." \
     http://localhost:4000/api/v1/auth/me

# Response:
{
  "user": {
    "id": "user_01HXYZ123",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "emailVerified": true,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-15T00:00:00Z",
    "profilePictureUrl": "https://example.com/photo.jpg"
  },
  "claims": {
    "sub": "user_01HXYZ123",
    "email": "user@example.com",
    "iat": 1234567890,
    "exp": 1234571490,
    "org_id": "org_01ABC",
    "org_name": "Acme Corp"
  },
  "account": {
    "id": "org_01ABC",
    "name": "Acme Corp"
  }
}
```

### Using JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:4000/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
});

const data = await response.json();
console.log('User:', data.user);
console.log('Account:', data.account);
```

### Using Python Requests

```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
}

response = requests.get('http://localhost:4000/api/v1/auth/me', headers=headers)
data = response.json()

print(f"User: {data['user']['email']}")
print(f"Account: {data['account']['name']}")
```

---

## Response Fields

### User Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | WorkOS user ID |
| `email` | string | User email address |
| `firstName` | string\|null | User first name |
| `lastName` | string\|null | User last name |
| `emailVerified` | boolean | Email verification status |
| `createdAt` | string | ISO 8601 timestamp |
| `updatedAt` | string | ISO 8601 timestamp |
| `profilePictureUrl` | string\|null | Profile picture URL |

### Claims Object
Contains the JWT token claims:
- `sub`: User ID
- `email`: User email
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp
- `org_id`: Organization ID (if available)
- `org_name`: Organization name (if available)

### Account Object
Organization/account information (nullable):
- `id`: Organization ID
- `name`: Organization name

---

## Error Responses

### 401 Unauthorized - Missing Token
```bash
curl http://localhost:4000/api/v1/auth/me

# Response:
{
  "detail": "Authorization required"
}
```

### 401 Unauthorized - Invalid Token
```bash
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:4000/api/v1/auth/me

# Response:
{
  "detail": "Invalid token: missing user ID"
}
```

### 404 Not Found - User Not Found
```bash
# If user_id in token doesn't exist in WorkOS
{
  "detail": "User user_01HXYZ123 not found"
}
```

### 500 Internal Server Error - WorkOS Not Configured
```bash
# If WORKOS_API_KEY is not set
{
  "detail": "Authentication service not configured"
}
```

### 500 Internal Server Error - API Error
```bash
# If WorkOS API is unreachable
{
  "detail": "Failed to fetch user information"
}
```

---

## How It Works

1. **Token Verification**
   - Extracts token from `Authorization: Bearer <token>` header
   - Verifies JWT signature using WorkOS JWKS
   - Validates issuer, audience, and expiration
   - Extracts user_id from `sub` claim

2. **User Fetch**
   - Calls WorkOS User Management API: `GET /users/{user_id}`
   - Retrieves current user profile data
   - Maps WorkOS fields to application format

3. **Response Assembly**
   - Combines user data from WorkOS
   - Includes JWT claims for debugging
   - Extracts account info from JWT (org_id, org_name)

---

## Environment Setup

Requires these environment variables:

```bash
# Required for JWT verification
WORKOS_CLIENT_ID=client_01ABC...

# Required for fetching user data
WORKOS_API_KEY=sk_live_ABC123...

# Optional (uses defaults if not set)
WORKOS_API_BASE_URL=https://api.workos.com
WORKOS_JWKS_URL=https://api.workos.com/sso/jwks/{client_id}
```

---

## Testing

### Manual Test with Valid Token

1. Get a valid access token from WorkOS (via login or device flow)
2. Make request with token:

```bash
TOKEN="your_valid_token_here"
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:4000/api/v1/auth/me | jq
```

### Using the CLI Device Flow

```bash
# 1. Start device flow
curl -X POST http://localhost:4000/api/v1/auth/device/code \
     -H "Content-Type: application/json" \
     -d '{"client_id": "your_client_id"}'

# 2. Authenticate in browser with user_code

# 3. Exchange device code for token
curl -X POST http://localhost:4000/api/v1/auth/device/token \
     -H "Content-Type: application/json" \
     -d '{
       "device_code": "...",
       "client_id": "your_client_id"
     }'

# 4. Use access_token with /me endpoint
curl -H "Authorization: Bearer <access_token>" \
     http://localhost:4000/api/v1/auth/me
```

---

## Integration Examples

### React/Frontend

```typescript
// hooks/useCurrentUser.ts
import { useQuery } from '@tanstack/react-query';

export function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No token');

      const response = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to fetch user');
      return response.json();
    },
  });
}

// Usage in component
function UserProfile() {
  const { data, isLoading, error } = useCurrentUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>{data.user.firstName} {data.user.lastName}</h1>
      <p>{data.user.email}</p>
      {data.account && <p>Account: {data.account.name}</p>}
    </div>
  );
}
```

### Python Backend Integration

```python
import httpx

async def get_current_user_info(access_token: str) -> dict:
    """Fetch current user from /auth/me endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:4000/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()

# Usage
try:
    user_data = await get_current_user_info(token)
    user_id = user_data["user"]["id"]
    user_email = user_data["user"]["email"]
    print(f"Logged in as: {user_email}")
except httpx.HTTPStatusError as e:
    print(f"Error: {e.response.status_code}")
```

---

## Troubleshooting

### "Authorization required"
**Solution:** Add `Authorization: Bearer <token>` header

### "Invalid token: missing user ID"
**Solution:** Token is missing `sub` claim. Ensure token is from WorkOS AuthKit.

### "User not found"
**Solution:** User ID in token doesn't exist in WorkOS. User may have been deleted.

### "Authentication service not configured"
**Solution:** Set `WORKOS_API_KEY` environment variable.

### "Failed to fetch user information"
**Solution:** Check WorkOS API status, verify API key is valid, check network connectivity.

---

## Security Notes

1. **Always use HTTPS in production** to protect tokens in transit
2. **Never log or expose tokens** in error messages or logs
3. **Validate token on every request** - the endpoint uses `auth_guard` dependency
4. **Short token lifetimes** - WorkOS tokens typically expire in 1 hour
5. **Use refresh tokens** for long-lived sessions

---

## Related Endpoints

- `POST /api/v1/auth/device/code` - Start device authorization flow
- `POST /api/v1/auth/device/token` - Exchange device code for token
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Log out and revoke tokens

---

## More Information

- Implementation details: `docs/reports/B1_AUTH_ME_IMPLEMENTATION_COMPLETE.md`
- WorkOS User Management API: https://workos.com/docs/user-management
- JWT verification: `src/tracertm/services/workos_auth_service.py`
- Auth guard implementation: `src/tracertm/api/deps.py`
