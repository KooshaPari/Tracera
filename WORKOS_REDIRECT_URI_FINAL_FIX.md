# WorkOS Redirect URI Final Fix

**Problem:** WorkOS redirects to `http://localhost:5173` (root) instead of `/auth/callback`, causing "Page not found" error.

**Root Cause:** `redirectPathname` parameter wasn't being properly appended by WorkOS SDK. Need to use full `redirectUri` instead.

---

## ✅ Code Fix Applied

### Updated `auth.login.tsx` and `auth.register.tsx`

**Before (Broken):**
```typescript
signIn({ redirectPathname: "/auth/callback" });
// WorkOS was ignoring this and using root URL
```

**After (Fixed):**
```typescript
const baseUrl = window.location.origin;
const redirectUri = `${baseUrl}/auth/callback`;
signIn({ redirectUri });
// Now explicitly passes full URL: http://localhost:5173/auth/callback
```

---

## 🔧 WorkOS Dashboard Configuration

**CRITICAL:** You must add the **exact full callback URL** to WorkOS Dashboard:

### Required Redirect URIs

1. ✅ **`http://localhost:5173/auth/callback`** ← **SET AS DEFAULT** (for development)
2. ✅ `http://localhost:5173/` (root with trailing slash)
3. ✅ `http://localhost:5173` (root without trailing slash)

### Production URIs

1. ✅ **`https://trace.kooshapari.com/auth/callback`** ← **SET AS DEFAULT** (for production)
2. ✅ `https://trace.kooshapari.com/` (root with trailing slash)
3. ✅ `https://trace.kooshapari.com` (root without trailing slash)

---

## 📝 Steps to Fix in WorkOS Dashboard

1. **Go to:** WorkOS Dashboard → Authentication → Redirects

2. **Add Callback URI:**
   - Click "Add Redirect URI"
   - Enter: `http://localhost:5173/auth/callback`
   - **Click the star/Default button** to set as default

3. **Verify Root URIs:**
   - Ensure `http://localhost:5173/` is in the list
   - Ensure `http://localhost:5173` is in the list (if needed)

4. **For Production:**
   - Add: `https://trace.kooshapari.com/auth/callback`
   - Set as default for production environment

---

## 🧪 Testing After Fix

1. **Clear browser cache/cookies**
2. **Restart dev server:** `bun run dev`
3. **Visit:** `http://localhost:5173`
4. **Should redirect to:** `http://localhost:5173/auth/login?returnTo=/`
5. **Click sign in** → Redirects to WorkOS
6. **After GitHub auth** → Should redirect to: `http://localhost:5173/auth/callback?code=...`
7. **Should then redirect to:** `/` (dashboard) ✅

---

## ⚠️ Important Notes

- **`redirectUri` vs `redirectPathname`:** 
  - `redirectPathname` appends to default redirect URI (didn't work reliably)
  - `redirectUri` uses exact full URL (more reliable)

- **Exact Match Required:**
  - The `redirectUri` in code must **exactly match** a redirect URI in WorkOS Dashboard
  - No wildcards allowed for the default redirect URI
  - Case-sensitive and must include protocol (`http://` or `https://`)

- **Default Redirect URI:**
  - The default redirect URI is used when no `redirectUri` is specified
  - Since we're now explicitly passing `redirectUri`, the default should still be set to the callback URL for consistency

---

## ✅ Status

- [x] Code updated to use full `redirectUri` instead of `redirectPathname`
- [ ] **ACTION REQUIRED:** Update WorkOS Dashboard
  - [ ] Add `http://localhost:5173/auth/callback` to Redirect URIs
  - [ ] Set `http://localhost:5173/auth/callback` as Default Redirect URI
  - [ ] Add production callback URI: `https://trace.kooshapari.com/auth/callback`
- [ ] Test authentication flow

**After updating WorkOS Dashboard, the "Page not found" error should be resolved!**
