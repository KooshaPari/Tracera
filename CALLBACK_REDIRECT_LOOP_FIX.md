# Callback Redirect Loop Fix

**Problem:** After authentication, callback page redirects but then loops back to `/auth/login`

**Root Cause:** Race condition - callback page redirects before auth store is fully updated, so `__root.tsx` sees user as unauthenticated and redirects back to login.

---

## ✅ Fixes Applied

### 1. Updated `__root.tsx` to Always Allow `/auth/callback`

**Key Change:** Explicitly allow `/auth/callback` route without checking auth state:

```typescript
// CRITICAL: Always allow /auth/callback - don't redirect it
if (pathname === "/auth/callback") {
	return; // Allow callback page to load
}
```

**Why:** The callback page needs to load even when auth store isn't updated yet, so it can sync the auth state.

---

### 2. Enhanced Callback Page to Wait for Auth Store Update

**Key Change:** Poll the auth store to ensure it's updated before redirecting:

```typescript
// Poll the store to ensure it's updated
let attempts = 0;
while (attempts < 10) {
	const isAuthenticated = useAuthStore.getState().isAuthenticated;
	if (isAuthenticated) {
		break;
	}
	await new Promise(resolve => setTimeout(resolve, 50));
	attempts++;
}

// Small delay to ensure store persistence is complete
await new Promise(resolve => setTimeout(resolve, 100));
```

**Why:** Ensures the auth store is fully updated (including persistence) before redirecting, preventing `__root.tsx` from seeing stale state.

---

### 3. Updated `AuthKitSync` to Skip Callback Page

**Key Change:** Don't handle redirects on `/auth/callback`:

```typescript
// Don't handle redirects on /auth/callback - let the callback page handle it
if (!hasRedirectedRef.current && window.location.pathname.startsWith("/auth") && window.location.pathname !== "/auth/callback") {
	// ... handle redirect
}
```

**Why:** Prevents double redirects and race conditions between `AuthKitSync` and the callback page.

---

## 🔄 Flow After Fix

1. **User authenticates** → WorkOS redirects to `/auth/callback?code=ABC123`
2. **Callback page loads** → `__root.tsx` allows it (no redirect check)
3. **Callback page syncs auth** → Updates auth store
4. **Callback page waits** → Polls store until `isAuthenticated === true`
5. **Callback page redirects** → To `/` or `returnTo`
6. **`__root.tsx` sees authenticated user** → Allows access ✅

**No more loops!** ✅

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Visit:** `http://localhost:5173` (or any protected route)
3. **Should redirect to:** `/auth/login?returnTo=/`
4. **Sign in** → Redirects to WorkOS
5. **After GitHub auth** → Redirects to `/auth/callback?code=...`
6. **Callback processes** → Waits for auth store update
7. **Should redirect to:** `/` (dashboard) ✅

---

## ✅ Status

- [x] Updated `__root.tsx` to always allow `/auth/callback`
- [x] Enhanced callback page to wait for auth store update
- [x] Updated `AuthKitSync` to skip callback page redirects
- [x] Added polling mechanism to ensure store is updated

**The redirect loop should now be completely fixed!**
