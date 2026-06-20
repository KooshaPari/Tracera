# Backend Authentication Requirements - HttpOnly Cookies

## Overview

The frontend has been updated to use HttpOnly cookies for authentication. This document specifies the exact backend changes required to support this security model.

---

## Critical Changes Required

### 1. Cookie Setup Configuration

All auth endpoints must set HttpOnly cookies with proper security flags:

```python
# Python/Flask/FastAPI Example
response.set_cookie(
    key="auth_session",
    value=jwt_token,
    max_age=86400,  # 24 hours
    secure=True,    # HTTPS only
    httponly=True,  # JavaScript cannot access
    samesite="Lax", # CSRF protection
    domain=None,    # Current domain
    path="/",       # All paths
)
```

**Cookie Attributes Explanation:**
- `httponly=True` - **CRITICAL:** Prevents XSS access
- `secure=True` - Only sent over HTTPS
- `samesite="Lax"` - CSRF protection (allow same-site requests)
- `max_age=86400` - 24-hour session (adjust as needed)

### 2. Login Endpoint

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```
Set-Cookie: auth_session=eyJ0eXAiOiJKV1QiLCJhbGc...; HttpOnly; Secure; SameSite=Lax; Max-Age=86400
Content-Type: application/json

{
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "https://...",
    "role": "admin"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

**Implementation Example (FastAPI):**
```python
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/api/v1/auth/login")
async def login(email: str, password: str, response: Response):
    # Validate credentials
    user = validate_credentials(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    # Set HttpOnly cookie
    response.set_cookie(
        key="auth_session",
        value=token,
        max_age=86400,
        secure=True,
        httponly=True,
        samesite="Lax",
    )

    # Return user info (NOT token)
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    }
```

### 3. Session Validation Endpoint

**Endpoint:** `GET /api/v1/auth/me`

**Request:**
```
GET /api/v1/auth/me
Cookie: auth_session=eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "account": {
    "id": "acc-456",
    "name": "My Workspace",
    "slug": "my-workspace"
  }
}
```

**Response (401 Unauthorized):**
```json
{}
```

**Implementation Example (FastAPI):**
```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

def get_current_user(request: Request) -> User:
    """Dependency to extract and validate user from cookie"""
    auth_session = request.cookies.get("auth_session")

    if not auth_session:
        raise HTTPException(status_code=401)

    try:
        payload = jwt.decode(auth_session, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        user = get_user(user_id)
        return user
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=401)

@router.get("/api/v1/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    # Get current account for user
    account = get_user_account(user.id)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
        "account": {
            "id": account.id,
            "name": account.name,
            "slug": account.slug,
        }
    }
```

### 4. Logout Endpoint

**Endpoint:** `POST /api/v1/auth/logout`

**Request:**
```
POST /api/v1/auth/logout
Cookie: auth_session=eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```
Set-Cookie: auth_session=; Max-Age=0; Path=/
Content-Type: application/json

{
  "status": "logged_out"
}
```

**Implementation Example:**
```python
@router.post("/api/v1/auth/logout")
async def logout(response: Response):
    # Clear the cookie by setting Max-Age=0
    response.delete_cookie(
        key="auth_session",
        secure=True,
        httponly=True,
        samesite="Lax",
    )

    return {"status": "logged_out"}
```

### 5. Auth Middleware

Apply to all protected endpoints to validate cookies:

```python
# Middleware approach
class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        auth_session = request.cookies.get("auth_session")

        # Skip auth for public endpoints
        if request.url.path in ["/auth/login", "/auth/register", "/health"]:
            return await call_next(request)

        # Validate session
        if not auth_session:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"}
            )

        try:
            payload = jwt.decode(auth_session, SECRET_KEY, algorithms=["HS256"])
            request.state.user_id = payload.get("sub")
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            return JSONResponse(
                status_code=401,
                content={"detail": "Session expired"}
            )

        return await call_next(request)

# Or dependency injection approach
@router.get("/api/v1/projects")
async def list_projects(user: User = Depends(get_current_user)):
    projects = get_user_projects(user.id)
    return {"projects": projects}
```

### 6. Token Refresh (Optional but Recommended)

**Endpoint:** `POST /api/v1/auth/refresh`

```python
@router.post("/api/v1/auth/refresh")
async def refresh_token(user: User = Depends(get_current_user), response: Response):
    # Generate new token
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    new_token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    # Set new cookie
    response.set_cookie(
        key="auth_session",
        value=new_token,
        max_age=86400,
        secure=True,
        httponly=True,
        samesite="Lax",
    )

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    }
```

---

## CORS Configuration

**CRITICAL:** Must allow credentials to be sent with cross-origin requests:

```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "http://localhost:3000"],
    allow_credentials=True,  # MUST BE TRUE for HttpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Key Setting:** `allow_credentials=True`

Without this, cookies won't be sent with cross-origin requests.

---

## All Protected Endpoints

These endpoints must use the `get_current_user` dependency:

```
GET /api/v1/projects
GET /api/v1/projects/{projectId}
POST /api/v1/projects
PUT /api/v1/projects/{projectId}
DELETE /api/v1/projects/{projectId}

GET /api/v1/items
POST /api/v1/items
GET /api/v1/items/{itemId}
PUT /api/v1/items/{itemId}
DELETE /api/v1/items/{itemId}

GET /api/v1/links
POST /api/v1/links
GET /api/v1/links/{linkId}
DELETE /api/v1/links/{linkId}

POST /api/v1/accounts/{accountId}/switch
GET /api/v1/auth/me
POST /api/v1/auth/logout

... and all other protected endpoints
```

Each should validate the cookie and return 401 for invalid sessions:

```python
@router.get("/api/v1/projects")
async def list_projects(user: User = Depends(get_current_user)):
    # user is automatically validated
    return get_projects(user.id)
```

---

## Error Handling

### 401 Response Format

For any unauthorized request:

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Session expired" OR "Unauthorized" OR "Invalid token"
}
```

### Do NOT Return Token in Response

The token should **NEVER** be sent in the response body:

```python
# ❌ WRONG
return {
    "user": {...},
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # DON'T DO THIS
}

# ✅ CORRECT
return {
    "user": {...}
    # Token in HttpOnly cookie, not in response
}
```

---

## Security Checklist

- [ ] All cookies have `httponly=True`
- [ ] All cookies have `secure=True` (HTTPS only)
- [ ] All cookies have `samesite="Lax"`
- [ ] Cookie `max_age` set appropriately (24 hours recommended)
- [ ] CORS `allow_credentials=True` configured
- [ ] No tokens in response bodies
- [ ] All protected endpoints validate session
- [ ] 401 responses for invalid/expired sessions
- [ ] Logout endpoint clears cookies
- [ ] JWT tokens signed with strong secret
- [ ] Token expiration enforced

---

## Testing the Implementation

### Test 1: Verify Cookie Set on Login
```bash
curl -v -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Look for:
# Set-Cookie: auth_session=...; HttpOnly; Secure; SameSite=Lax; Max-Age=86400
```

### Test 2: Verify Cookie Sent in Requests
```bash
curl -v -X GET http://localhost:4000/api/v1/auth/me \
  -b "auth_session=<token_from_step_1>"

# Should return 200 with user info
```

### Test 3: Verify 401 on Invalid Cookie
```bash
curl -v -X GET http://localhost:4000/api/v1/auth/me

# Should return 401
```

### Test 4: Verify Cookie Cleared on Logout
```bash
curl -v -X POST http://localhost:4000/api/v1/auth/logout \
  -b "auth_session=<token_from_step_1>"

# Look for:
# Set-Cookie: auth_session=; Max-Age=0
```

### Test 5: Verify CORS Works with Credentials
```javascript
// In browser console
fetch('https://api.example.com/api/v1/auth/me', {
  credentials: 'include'  // CRITICAL
})
  .then(r => r.json())
  .then(d => console.log(d))

// Should work without errors
// Should include auth_session cookie in request
```

---

## Integration Timeline

### Phase 1: Implement Auth Endpoints (Day 1-2)
- [ ] Create login endpoint with HttpOnly cookies
- [ ] Create logout endpoint that clears cookies
- [ ] Create /auth/me endpoint for session validation

### Phase 2: Protect Existing Endpoints (Day 2-3)
- [ ] Add auth middleware to all protected endpoints
- [ ] Configure CORS for credentials
- [ ] Test with Frontend API calls

### Phase 3: Test & Debug (Day 3-4)
- [ ] Manual testing with curl/Postman
- [ ] Browser testing with DevTools
- [ ] E2E testing with Playwright

### Phase 4: Deploy (Day 4-5)
- [ ] Staging environment
- [ ] Production rollout

---

## Troubleshooting

### Issue: Cookies not being set
**Check:**
- Is `Set-Cookie` header in response?
- Is `httponly=True` set?
- Is domain correct?
- Is path correct (`/`)?

### Issue: Cookies not being sent
**Check:**
- Is `credentials: 'include'` in fetch?
- Does CORS `allow_credentials=True`?
- Are origins correct in CORS config?

### Issue: 401 errors after login
**Check:**
- Is JWT signature correct?
- Is token expiring immediately?
- Is cookie being parsed correctly?
- Is middleware correctly extracting from cookies?

### Issue: XSS still possible
**Verify:**
- Tokens in HttpOnly cookies (not localStorage)
- CSRF tokens still required
- CSP headers set correctly
- Input validation on all endpoints

---

## Code Examples by Framework

### FastAPI (Python)
See examples above - all use FastAPI

### Flask (Python)
```python
from flask import Flask, request, jsonify, make_response
import jwt

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.json
    user = validate_user(data['email'], data['password'])

    if not user:
        return jsonify({'detail': 'Invalid'}), 401

    token = jwt.encode({'sub': user.id}, SECRET_KEY)
    response = make_response(jsonify({'user': user.dict()}))
    response.set_cookie('auth_session', token,
                       max_age=86400, secure=True,
                       httponly=True, samesite='Lax')
    return response
```

### Express.js (Node.js)
```javascript
app.post('/api/v1/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = validateUser(email, password);

  if (!user) {
    return res.status(401).json({ detail: 'Invalid' });
  }

  const token = jwt.sign({ sub: user.id }, SECRET_KEY);
  res.cookie('auth_session', token, {
    maxAge: 86400000,
    secure: true,
    httpOnly: true,
    sameSite: 'lax'
  });

  return res.json({ user });
});
```

### Django (Python)
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import jwt

@require_http_methods(["POST"])
def login_view(request):
    data = json.loads(request.body)
    user = authenticate(email=data['email'], password=data['password'])

    if not user:
        return JsonResponse({'detail': 'Invalid'}, status=401)

    token = jwt.encode({'sub': user.id}, SECRET_KEY)
    response = JsonResponse({'user': model_to_dict(user)})
    response.set_cookie('auth_session', token,
                       max_age=86400, secure=True,
                       httponly=True, samesite='Lax')
    return response
```

---

## Next Steps

1. Implement the 4 required endpoints (login, logout, /auth/me, refresh)
2. Add auth middleware to protect endpoints
3. Configure CORS for credentials
4. Test with Frontend
5. Deploy to staging
6. Run security audit
7. Deploy to production

---

## Support & Questions

If you have questions about these requirements:
1. Review this document thoroughly
2. Check the code examples for your framework
3. Test with the troubleshooting guide
4. Consult the Frontend documentation in `COOKIE_AUTH_UPDATE.md`

---

**Version:** 1.0
**Last Updated:** 2026-01-29
**Status:** Ready for Implementation
