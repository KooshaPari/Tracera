# WorkOS Redirect URI Final Fix

**Problem:** WorkOS error: "This is not a valid redirect URI. Did you mean to use: http://localhost:5173/auth/callback"

**Root Cause:** The default redirect URI in WorkOS Dashboard is set to `http://localhost:5173` (root), but only `http://localhost:5173/auth/callback` is in the allowed redirect URIs list.

---

## ✅ Solution

Use `redirectPathname: "/auth/callback"` which will append to the default redirect URI:

- **Default Redirect URI:** `http://localhost:5173` (from WorkOS Dashboard)
- **redirectPathname:** `/auth/callback`
- **Result:** `http://localhost:5173/auth/callback` ✅

---

## 🔧 WorkOS Dashboard Configuration

**Current Setup:**
- Default Redirect URI: `http://localhost:5173` ✅ (keep this)
- Redirect URIs list includes: `http://localhost:5173/auth/callback` ✅

**How it works:**
- SDK uses default: `http://localhost:5173`
- Appends pathname: `/auth/callback`
- Final redirect: `http://localhost:5173/auth/callback` ✅

---

## ✅ Code Changes

**Updated:**
- `signIn({ redirectPathname: "/auth/callback" })`
- `signUp({ redirectPathname: "/auth/callback" })`

**Why:** `redirectPathname` appends to the default redirect URI, creating the full callback URL that's in the allowed list.

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Restart dev server**
3. **Visit:** `http://localhost:5173`
4. **Should redirect to:** `/auth/login`
5. **Click sign in** → Should redirect to WorkOS (no errors)
6. **After GitHub auth** → Should redirect to `/auth/callback?code=...`

---

## ✅ Status

- [x] Updated `signIn()` to use `redirectPathname: "/auth/callback"`
- [x] Updated `signUp()` to use `redirectPathname: "/auth/callback"`
- [x] Removed `apiHostname` from AuthKitProvider
- [x] WorkOS Dashboard configured correctly

**The redirect URI error should now be resolved!**
