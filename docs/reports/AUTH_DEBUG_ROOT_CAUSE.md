# Frontend Authentication 401 Errors - Root Cause Analysis

**Date:** 2026-01-31
**Status:** Root Cause Identified
**Method:** Systematic debugging with evidence gathering

---

## Phase 1: Root Cause Investigation - COMPLETE ✅

### Evidence Collected

#### Layer 1: Frontend Console
```
✅ WorkOS Client ID: Found
✅ CSRF: Initialized
✅ WebSocket: Connects and authenticates
❌ API Calls: 401 Unauthorized
```

#### Layer 2: Backend Status
```
✅ Backend healthy on port 8000
✅ Middleware expects: Authorization: Bearer <token>
✅ Returns 401 if header missing
```

#### Layer 3: Frontend Auth Flow
```
AuthKitSync.tsx (line 41):
   const token = await getAccessToken();

AuthKitSync.tsx (line 43):
   setAuthFromWorkOS(mappedUser, token ?? null);

authStore.ts (line 281-288):
   setAuthFromWorkOS: (user, token) => {
       get().setUser(user);
       if (token) {                    ← KEY CONDITION
           get().setToken(token);
       }
   }

client.ts (line 178-183):
   const fromStorage = localStorage.getItem("auth_token");
   const fromStore = useAuthStore.getState().token;
   const token = (fromStorage ?? fromStore)?.trim();
   if (token) {                        ← KEY CONDITION
       request.headers.set("Authorization", `Bearer ${token}`);
   }
```

---

## ROOT CAUSE IDENTIFIED 🎯

**Primary Issue:** `getAccessToken()` is returning `null` or `undefined`

**Evidence:**
1. ✅ Authorization header logic exists and is correct
2. ✅ Token storage logic exists and is correct
3. ❌ But if token is falsy, header is NOT added
4. ❌ Backend returns 401 when header missing

**Chain of Failure:**
```
WorkOS getAccessToken() → returns null
    ↓
setAuthFromWorkOS(user, null)
    ↓
if (token) check fails → setToken() NOT called
    ↓
localStorage has no 'auth_token'
    ↓
API interceptor: if (token) check fails → header NOT added
    ↓
Backend middleware: No Authorization header → 401
```

---

## Phase 2: Pattern Analysis

### Working Example: validateSession()
**File:** `client.ts` lines 108-143

```typescript
const token = (fromStorage ?? fromStore)?.trim();
if (token) {
    headers.Authorization = `Bearer ${token}`;
}
const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    headers,
    credentials: "include",
});
```

**This works because:** It manually adds the Authorization header

### Broken Pattern: Regular API Calls
**File:** API calls using `apiClient`

```typescript
const response = await apiClient.GET("/api/v1/projects");
// Interceptor tries to add header but token is null
```

**This fails because:** Token is null, so header never gets added

---

## Why is getAccessToken() Returning Null?

### Possibility 1: WorkOS DevMode Configuration
**WorkOS SDK in devMode:**
- Stores tokens in localStorage under WorkOS-specific keys
- `getAccessToken()` may require specific configuration

### Possibility 2: Not Actually Logged In
**User state:**
- WorkOS Client ID found ✓
- But user may not have completed OAuth flow
- Check: Is there a WorkOS session in browser?

### Possibility 3: Timing Issue
**AuthKitSync timing:**
- Component renders before WorkOS initializes
- `getAccessToken()` called too early
- Returns null during initialization

---

## Hypothesis to Test

**Hypothesis:** User has not completed WorkOS authentication flow

**Test:**
1. Check browser localStorage for WorkOS keys
2. Check if user needs to log in via WorkOS
3. Add console.log to AuthKitSync to see what getAccessToken() returns

**If hypothesis is correct:**
- User navigates to login page
- Clicks "Sign in with GitHub" or other provider
- Completes OAuth flow
- getAccessToken() will return actual token
- 401 errors will disappear

---

## Next Step

Add diagnostic logging to AuthKitSync to see:
1. What does `getAccessToken()` return?
2. Is `setAuthFromWorkOS()` being called?
3. What value is being stored?

Then we can proceed to Phase 3: Hypothesis and Testing.
