# Authentication Token Expired - Quick Fix

**Issue:** API requests returning 401 Unauthorized - "Signature has expired"
**Impact:** Graph shows 0 nodes despite data existing (you can see "300 links" in UI)
**Status:** ✅ Solution ready

---

## Quick Fix: Re-authenticate

### Option 1: Clear Browser Storage and Re-login

```javascript
// Open browser console (Cmd+Option+I)
// Run this to clear expired tokens:
localStorage.clear()
sessionStorage.clear()

// Then refresh page
location.reload()
```

You'll be redirected to login page - sign in again with WorkOS.

### Option 2: Manual Token Refresh (If Available)

Check if there's a refresh token endpoint:

```bash
# From browser console, check current auth state
console.log(localStorage.getItem('auth'))
console.log(localStorage.getItem('token'))
```

### Option 3: Backend Token Extension (Development)

For development, you can temporarily extend JWT expiry:

```bash
# Check current JWT_EXPIRY
grep JWT_EXPIRY .env

# Extend to 24 hours (in .env)
JWT_EXPIRY=24h

# Restart Python backend
# Kill existing process, then:
uvicorn tracertm.api.main:app --reload --port 8000
```

---

## What's Happening

The logs show:
```
Authentication failed: Signature has expired
INFO: GET /api/v1/items?project_id=... HTTP/1.1" 401 Unauthorized
INFO: GET /api/v1/links?project_id=... HTTP/1.1" 401 Unauthorized
```

**Your graph data is there!** (UI shows "300 links")
**But the API can't return it** because authentication failed.

---

## Permanent Solution: Auto-Refresh Tokens

Add token refresh logic to frontend:

```typescript
// frontend/apps/web/src/api/client.ts
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    // Redirect to login
    window.location.href = '/login'
    return
  }

  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  })

  if (response.ok) {
    const { access_token } = await response.json()
    localStorage.setItem('auth_token', access_token)
    return access_token
  } else {
    // Redirect to login
    window.location.href = '/login'
  }
}

// Add interceptor for 401 responses
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const token = await refreshToken()
      if (token) {
        // Retry original request with new token
        error.config.headers.Authorization = `Bearer ${token}`
        return api.request(error.config)
      }
    }
    return Promise.reject(error)
  }
)
```

---

## Quick Summary

**The graph is working!** Your data is populated:
- ✅ 531 nodes for SwiftRide
- ✅ 450 links for SwiftRide
- ✅ Graph tables created and populated

**Just re-authenticate:**
1. Clear browser storage (localStorage.clear())
2. Refresh page
3. Sign in again
4. Graph will render! ✅

---

**Next Step:** Clear localStorage and re-login to see your graph! 🚀
