# WorkOS Redirect 404 Fix

**Problem:** WorkOS redirects to `http://localhost:5173/auth/callback` but shows "page not found" on WorkOS domain

**URL:** `https://significant-vessel-93-staging.authkit.app/user_management/authorize?...&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fcallback&...`

**Issue:** The redirect URI is correct, but WorkOS might be having issues redirecting to localhost.

---

## ✅ Verification Steps

1. **Route is Registered:** ✅ Confirmed in `routeTree.gen.ts`
   - Route path: `/auth/callback`
   - Route ID: `/auth/callback`
   - Component: `AuthCallbackPage`

2. **Redirect URI is Correct:** ✅
   - Encoded: `http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fcallback`
   - Decoded: `http://localhost:5173/auth/callback`
   - Matches route path exactly

---

## 🔍 Possible Causes

1. **WorkOS Dashboard Configuration:**
   - Redirect URI might not be set as Default
   - Redirect URI might have trailing slash or mismatch
   - Redirect URI might not be in the allowed list

2. **Localhost Access:**
   - WorkOS might have issues redirecting to `localhost`
   - Try using `127.0.0.1` instead
   - Or use a tunnel (ngrok) for testing

3. **CORS/Network Issues:**
   - Browser blocking redirect
   - Network configuration issue

---

## 🎯 Solutions to Try

### Solution 1: Verify WorkOS Dashboard

1. Go to WorkOS Dashboard → Authentication → Redirects
2. Ensure `http://localhost:5173/auth/callback` is listed
3. **Set as Default Redirect URI**
4. Remove any trailing slashes
5. Ensure no duplicates

### Solution 2: Try 127.0.0.1 Instead

If localhost doesn't work, try:
1. Add `http://127.0.0.1:5173/auth/callback` to WorkOS Redirects
2. Update code to use `127.0.0.1`:
   ```typescript
   const redirectUri = `http://127.0.0.1:5173/auth/callback`;
   ```

### Solution 3: Use ngrok for Testing

1. Install ngrok: `brew install ngrok` (or download)
2. Start tunnel: `ngrok http 5173`
3. Use ngrok URL in WorkOS Dashboard: `https://your-ngrok-url.ngrok.io/auth/callback`
4. Update code to use ngrok URL

### Solution 4: Check Browser Console

1. Open browser DevTools → Network tab
2. Try authentication flow
3. Look for:
   - Failed redirects
   - CORS errors
   - 404 errors
   - Blocked requests

---

## ✅ Immediate Action

**Check WorkOS Dashboard:**
1. Go to: https://dashboard.workos.com
2. Navigate to: Authentication → Redirects
3. Verify: `http://localhost:5173/auth/callback` is listed
4. **Set as Default** (click star/Default button)
5. Ensure no trailing slash

**Then test again!**
