# WorkOS Default Redirect URI Fix

**Problem:** WorkOS is using `http://localhost:5173` as redirect URI, but only `http://localhost:5173/auth/callback` is allowed.

**Error:** "This is not a valid redirect URI. Did you mean to use: http://localhost:5173/auth/callback"

**Root Cause:** The Default Redirect URI in WorkOS Dashboard is set to `http://localhost:5173` (root), but the SDK is using it directly without appending the pathname.

---

## ✅ Solution: Update WorkOS Dashboard

**You need to change the Default Redirect URI in WorkOS Dashboard:**

1. **Go to:** WorkOS Dashboard → Authentication → Redirects
2. **Find:** "Default Redirect URI" (should currently be `http://localhost:5173`)
3. **Change it to:** `http://localhost:5173/auth/callback`
4. **Click Save**

**Why:** The SDK uses the Default Redirect URI directly. If it's set to the root, it won't append `/auth/callback` even with `redirectPathname`.

---

## 🔧 Alternative: Use redirectUri Parameter

If changing the Default Redirect URI doesn't work, we can try passing the full `redirectUri`:

```typescript
signIn({ redirectUri: "http://localhost:5173/auth/callback" });
```

But first, try updating the Default Redirect URI in WorkOS Dashboard.

---

## ✅ Current Code

The code is already set up correctly:
- `signIn({ redirectPathname: "/auth/callback" })`
- `signUp({ redirectPathname: "/auth/callback" })`

But the SDK might not be appending the pathname if the default is the root.

---

## 🎯 Action Required

**Update WorkOS Dashboard:**
1. Go to: https://dashboard.workos.com
2. Navigate to: Authentication → Redirects
3. **Change Default Redirect URI from:** `http://localhost:5173`
4. **To:** `http://localhost:5173/auth/callback`
5. Save

**Then test again!**
