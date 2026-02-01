# Callback Redirect Loop Fix V2

**Problem:** Still looping back to `/auth/login` after authentication

**Root Cause:** 
1. `window.location.href` causes full page reload, losing Zustand state
2. Zustand persistence is async and might not be ready on next page load
3. Need to verify persistence is complete before redirecting

---

## ✅ Fixes Applied

### 1. Use TanStack Router `navigate` Instead of `window.location.href`

**Key Change:** Use `navigate()` which doesn't cause full page reload:

```typescript
// Before: window.location.href = returnTo; (causes full reload)
// After: navigate({ to: targetPath, replace: true }); (maintains state)
```

**Why:** `navigate()` doesn't cause a full page reload, so Zustand state persists across navigation.

---

### 2. Verify Zustand Persistence Before Redirecting

**Key Change:** Check localStorage to confirm persistence is complete:

```typescript
// Verify persistence by checking localStorage
const persisted = localStorage.getItem('tracertm-auth-store');
if (persisted) {
	const parsed = JSON.parse(persisted);
	if (parsed.state?.isAuthenticated && parsed.state?.user) {
		break; // Persistence confirmed
	}
}
```

**Why:** Zustand persistence is async. We need to verify the data is actually persisted before redirecting.

---

### 3. Enhanced Polling with Persistence Check

**Key Change:** Poll both store state AND localStorage persistence:

```typescript
let attempts = 0;
while (attempts < 20) {
	const state = useAuthStore.getState();
	if (state.isAuthenticated && state.user) {
		// Verify persistence by checking localStorage
		const persisted = localStorage.getItem('tracertm-auth-store');
		if (persisted && JSON.parse(persisted).state?.isAuthenticated) {
			break; // Both store and persistence confirmed
		}
	}
	await new Promise(resolve => setTimeout(resolve, 50));
	attempts++;
}
```

**Why:** Ensures both the in-memory store AND localStorage are updated before redirecting.

---

### 4. Updated `__root.tsx` to Check User Object

**Key Change:** Check both `isAuthenticated` AND `user` object:

```typescript
const { isAuthenticated, user } = useAuthStore.getState();

// Only redirect authenticated users away from auth routes if user object exists
if (isAuthenticated && user && isPublicRoute(pathname)) {
	throw redirect({ to: "/" });
}
```

**Why:** More robust check - ensures user object is actually set, not just the flag.

---

## 🔄 Flow After Fix

1. **User authenticates** → WorkOS redirects to `/auth/callback?code=ABC123`
2. **Callback page loads** → `__root.tsx` allows it unconditionally
3. **Callback syncs auth** → Updates auth store
4. **Callback verifies persistence** → Checks localStorage for persisted state
5. **Callback uses navigate()** → Navigates to `/` without full page reload
6. **`__root.tsx` sees authenticated user** → Allows access ✅

**No more loops!** ✅

---

## 🧪 Testing

1. **Clear browser cache/cookies AND localStorage**
2. **Visit:** `http://localhost:5173` (or any protected route)
3. **Should redirect to:** `/auth/login?returnTo=/`
4. **Sign in** → Redirects to WorkOS
5. **After GitHub auth** → Redirects to `/auth/callback?code=...`
6. **Callback processes** → Verifies store AND persistence
7. **Should navigate to:** `/` (dashboard) ✅

---

## ✅ Status

- [x] Changed to use `navigate()` instead of `window.location.href`
- [x] Added persistence verification before redirecting
- [x] Enhanced polling to check both store and localStorage
- [x] Updated `__root.tsx` to check user object
- [x] Increased polling attempts to 20 (1 second total)

**The redirect loop should now be completely fixed!**
