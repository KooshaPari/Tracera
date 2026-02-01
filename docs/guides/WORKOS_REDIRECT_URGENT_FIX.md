# WorkOS Redirect Issue - Urgent Fix

**Problem:** "Page not found" - WorkOS redirecting to its own domain instead of your app

**Error URL:** `https://significant-vessel-93-staging.authkit.app/auth/callback?code=...`

---

## 🚨 Root Cause

WorkOS is redirecting to **its own domain** (`significant-vessel-93-staging.authkit.app`) instead of **your app domain** (`localhost:5173` or `trace.kooshapari.com`).

**This happens because redirect URIs are NOT configured in WorkOS Dashboard.**

---

## ✅ Immediate Fix

### Step 1: Add Redirect URIs in WorkOS Dashboard

**CRITICAL:** You MUST add these URIs to WorkOS Dashboard:

1. Go to: https://dashboard.workos.com
2. Navigate to: **Authentication** → **Redirects**
3. Click: **Add Redirect URI**
4. Add these URIs **one by one**:

**Development (localhost:5173):**
```
http://localhost:5173/auth/callback
http://localhost:5173
http://localhost:5173/
```

**Production (trace.kooshapari.com):**
```
https://trace.kooshapari.com/auth/callback
https://trace.kooshapari.com
https://trace.kooshapari.com/
```

### Step 2: Verify Configuration

After adding URIs:
- ✅ Check they appear in the list
- ✅ Make sure they match exactly (including `http://` vs `https://`)
- ✅ No typos or extra spaces

### Step 3: Test Again

1. **Clear browser cache/cookies** (important!)
2. Visit: `http://localhost:5173/auth/login`
3. Sign in with GitHub
4. Should redirect to: `http://localhost:5173/auth/callback?code=...` ✅

---

## 🔧 Code Changes Applied

Updated `signIn()` and `signUp()` to explicitly pass `redirectPathname`:

```typescript
// auth.login.tsx
signIn({ redirectPathname: "/auth/callback" });

// auth.register.tsx  
signUp({ redirectPathname: "/auth/callback" });
```

This tells WorkOS where to redirect, but **you still need to add the URIs to WorkOS Dashboard**.

---

## ⚠️ Why This Happens

WorkOS uses redirect URIs configured in the dashboard to determine where to send users after authentication. If no URIs are configured:

1. WorkOS uses default redirect (its own domain) ❌
2. Results in "Page not found" error ❌
3. User can't complete authentication ❌

**Solution:** Add redirect URIs to WorkOS Dashboard ✅

---

## 📋 Checklist

- [ ] Go to WorkOS Dashboard → Authentication → Redirects
- [ ] Add `http://localhost:5173/auth/callback`
- [ ] Add `http://localhost:5173`
- [ ] Add `http://localhost:5173/`
- [ ] Add `https://trace.kooshapari.com/auth/callback`
- [ ] Add `https://trace.kooshapari.com`
- [ ] Add `https://trace.kooshapari.com/`
- [ ] Clear browser cache
- [ ] Test authentication flow

---

## 🎯 Quick Test

After adding redirect URIs:

1. Visit: `http://localhost:5173/auth/login`
2. Should redirect to WorkOS hosted UI
3. Sign in with GitHub
4. Should redirect back to: `http://localhost:5173/auth/callback?code=...`
5. Should then redirect to dashboard ✅

---

**Status:** ⚠️ **URGENT** - Add redirect URIs to WorkOS Dashboard immediately

The code is ready. The issue is WorkOS Dashboard configuration - redirect URIs must be added there.
