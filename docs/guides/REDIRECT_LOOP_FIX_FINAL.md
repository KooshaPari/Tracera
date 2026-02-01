# Redirect Loop Fix - Final Solution

**Problem:** Stuck in redirect loop: `http://localhost:5173/auth/login?returnTo=%2Fauth%2Fcallback%3Fcode%3D...`

**Root Cause:** 
1. `/auth/callback` wasn't treated as a public route, so unauthenticated users were redirected to login
2. `returnTo` parameter included auth callback URLs with codes, causing loops
3. Query params (including auth codes) were being included in `returnTo`

---

## ✅ Fixes Applied

### 1. Added `/auth/callback` to Public Routes

**File:** `auth-utils.ts`

```typescript
export function isPublicRoute(pathname: string): boolean {
	const publicRoutes = ["/auth/login", "/auth/register", "/auth/reset-password", "/auth/callback"];
	return publicRoutes.some((route) => pathname.startsWith(route));
}
```

**Why:** Allows unauthenticated users to access `/auth/callback` so WorkOS can process the auth code.

---

### 2. Enhanced `getReturnTo()` to Filter Auth Routes

**File:** `auth-utils.ts`

**Key Changes:**
- Added `isAuthRoute()` helper to detect auth URLs
- Filters out any `returnTo` that points to `/auth/*` routes
- Extracts only pathname (removes query params to avoid including auth codes)
- Validates and sanitizes returnTo values

**Example:**
```typescript
// Before: returnTo="/auth/callback?code=ABC123" → Would cause loop
// After: returnTo="/auth/callback?code=ABC123" → Returns "/" (filtered out)
```

---

### 3. Updated `__root.tsx` to Allow `/auth/callback`

**File:** `__root.tsx`

**Key Changes:**
- Allows `/auth/callback` even when not authenticated (WorkOS handles auth)
- Removed query params from `returnTo` (only uses pathname)
- Prevents redirect loops by not including search params in returnTo

```typescript
// Before: returnTo="/some/path?code=ABC123" → Includes auth code
// After: returnTo="/some/path" → Clean pathname only
```

---

### 4. Updated Callback Page to Filter Auth Routes

**File:** `auth.callback.tsx`

**Key Changes:**
- Uses `getReturnTo()` which already filters auth routes
- Double-checks before redirecting (never redirects to `/auth/*`)
- Falls back to `/` if returnTo is invalid or an auth route

---

## 🔄 Flow After Fix

1. **User visits protected route:** `/dashboard`
2. **Redirected to:** `/auth/login?returnTo=/dashboard` ✅ (clean pathname)
3. **Signs in with GitHub** → WorkOS redirects to: `/auth/callback?code=ABC123`
4. **Callback page processes code** → User authenticated
5. **Redirects to:** `/dashboard` ✅ (from returnTo, filtered and validated)

**No more loops!** ✅

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Visit:** `http://localhost:5173` (or any protected route)
3. **Should redirect to:** `http://localhost:5173/auth/login?returnTo=/`
4. **Sign in** → Redirects to WorkOS
5. **After GitHub auth** → Redirects to: `http://localhost:5173/auth/callback?code=...`
6. **Should then redirect to:** `/` (dashboard) ✅

---

## ✅ Status

- [x] Added `/auth/callback` to public routes
- [x] Enhanced `getReturnTo()` to filter auth routes
- [x] Updated `__root.tsx` to allow callback route
- [x] Updated callback page to validate returnTo
- [x] Removed query params from returnTo to prevent code leakage

**The redirect loop should now be completely fixed!**
