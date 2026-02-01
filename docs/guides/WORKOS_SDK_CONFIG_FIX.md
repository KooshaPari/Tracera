# WorkOS SDK Configuration Fix

**Problem:** Still getting 404 on WorkOS authorize endpoint

**Error:** `GET https://significant-vessel-93-staging.authkit.app/user_management/authorize?... 404`

**Root Cause:** The `apiHostname` configuration might be causing the SDK to use incorrect endpoints.

---

## ✅ Fixes Applied

### 1. Removed `apiHostname` from AuthKitProvider

**Before:**
```typescript
if (workosApiHostname && workosApiHostname.trim() !== "") {
	providerProps.apiHostname = workosApiHostname;
}
```

**After:**
```typescript
// Removed apiHostname - SDK will use default WorkOS endpoints
```

**Why:** The `apiHostname` prop might be causing the SDK to construct incorrect URLs. For standard AuthKit usage, the SDK should use default WorkOS API endpoints.

### 2. Removed Redirect Parameters from signIn/signUp

**Before:**
```typescript
signIn({ redirectPathname: "/auth/callback" });
```

**After:**
```typescript
signIn(); // Use default from WorkOS Dashboard
```

**Why:** Let the SDK use the default redirect URI configured in WorkOS Dashboard. This ensures consistency.

---

## 🔧 WorkOS Dashboard Configuration

**CRITICAL:** Set the Default Redirect URI in WorkOS Dashboard:

1. **Go to:** WorkOS Dashboard → Authentication → Redirects
2. **Set Default Redirect URI to:** `http://localhost:5173/auth/callback`
3. **Add to Redirect URIs list:**
   - `http://localhost:5173/auth/callback` ← **SET AS DEFAULT**
   - `http://localhost:5173/`
   - `http://localhost:5173`

**Important:** The Default Redirect URI should be the FULL callback URL, not just the root.

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

- [x] Removed `apiHostname` from AuthKitProvider
- [x] Removed redirect parameters from `signIn()` and `signUp()`
- [ ] **ACTION REQUIRED:** Set Default Redirect URI in WorkOS Dashboard to `http://localhost:5173/auth/callback`

**The 404 error should now be resolved!**
