# WorkOS 404 Authorize Endpoint Fix

**Problem:** WorkOS returning 404 on `/user_management/authorize` endpoint

**Error:**
```
GET https://significant-vessel-93-staging.authkit.app/user_management/authorize?... 404 (Not Found)
```

**Root Cause:** Using `redirectUri` parameter might be causing the SDK to construct the wrong URL. The WorkOS React SDK expects `redirectPathname` instead.

---

## ✅ Fixes Applied

### 1. Changed from `redirectUri` to `redirectPathname`

**Before:**
```typescript
const redirectUri = `${baseUrl}/auth/callback`;
signIn({ redirectUri });
```

**After:**
```typescript
signIn({ redirectPathname: "/auth/callback" });
```

**Why:** The WorkOS React SDK expects `redirectPathname` which it appends to the base redirect URI configured in the WorkOS Dashboard. Using `redirectUri` might cause the SDK to construct incorrect URLs.

### 2. Removed `redirectUri` from AuthKitProvider

**Before:**
```typescript
providerProps.redirectUri = `${window.location.origin}/auth/callback`;
```

**After:**
```typescript
// Removed - SDK uses redirect URI from WorkOS Dashboard
```

**Why:** The `redirectUri` prop in `AuthKitProvider` might not be the correct way to configure it. The SDK should use the redirect URI from WorkOS Dashboard configuration.

---

## 🔧 WorkOS Dashboard Configuration

**CRITICAL:** Ensure WorkOS Dashboard is configured correctly:

1. **Go to:** WorkOS Dashboard → Authentication → Redirects
2. **Set Default Redirect URI to:** `http://localhost:5173` (root, no trailing slash)
3. **Add to Redirect URIs list:**
   - `http://localhost:5173`
   - `http://localhost:5173/`
   - `http://localhost:5173/auth/callback`

**How it works:**
- Default Redirect URI: `http://localhost:5173`
- redirectPathname: `/auth/callback`
- **Result:** `http://localhost:5173/auth/callback` ✅

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Restart dev server**
3. **Visit:** `http://localhost:5173`
4. **Should redirect to:** `/auth/login`
5. **Click sign in** → Should redirect to WorkOS (no 404)
6. **After GitHub auth** → Should redirect to `/auth/callback?code=...`

---

## ✅ Status

- [x] Changed `signIn()` to use `redirectPathname`
- [x] Changed `signUp()` to use `redirectPathname`
- [x] Removed `redirectUri` from AuthKitProvider
- [ ] **ACTION REQUIRED:** Verify WorkOS Dashboard Default Redirect URI is `http://localhost:5173`

**The 404 error should now be resolved!**
