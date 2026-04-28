# WorkOS Redirect URI Exact Match Fix

**Problem:** WorkOS error: "This is not a valid redirect URI" - trying to use `http://localhost:5173` but only `http://localhost:5173/auth/callback` is allowed.

**Root Cause:** `redirectPathname` might not be working as expected. Need to pass the full `redirectUri` that matches exactly what's in WorkOS Dashboard.

---

## ✅ Fix Applied

Changed to use full `redirectUri` parameter:

**Before:**
```typescript
signIn({ redirectPathname: "/auth/callback" });
```

**After:**
```typescript
const redirectUri = `${window.location.origin}/auth/callback`;
signIn({ redirectUri });
```

**Why:** The full `redirectUri` must match EXACTLY an entry in the WorkOS Dashboard Redirect URIs list.

---

## 🔧 WorkOS Dashboard Configuration

**Required Configuration:**

1. **Go to:** WorkOS Dashboard → Authentication → Redirects
2. **Ensure this is in Redirect URIs list:**
   - ✅ `http://localhost:5173/auth/callback` (must be exact match)
3. **Default Redirect URI can be:** `http://localhost:5173` or `http://localhost:5173/auth/callback`

**Important:** The `redirectUri` in code (`http://localhost:5173/auth/callback`) must match EXACTLY an entry in the Redirect URIs list.

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Restart dev server**
3. **Visit:** `http://localhost:5173`
4. **Should redirect to:** `/auth/login`
5. **Click sign in** → Should redirect to WorkOS (no redirect URI errors)
6. **After GitHub auth** → Should redirect to `/auth/callback?code=...`

---

## ✅ Status

- [x] Changed to use full `redirectUri` parameter
- [x] Updated both `signIn()` and `signUp()`
- [ ] **ACTION REQUIRED:** Verify `http://localhost:5173/auth/callback` is in WorkOS Dashboard Redirect URIs list

**The redirect URI error should now be resolved!**
