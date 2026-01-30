# WorkOS Redirect Issue - Fix

**Problem:** WorkOS redirecting to `https://significant-vessel-93-staging.authkit.app/auth/callback` instead of your app

**Error:** Page not found on WorkOS domain

---

## 🔍 Issue Analysis

The URL `https://significant-vessel-93-staging.authkit.app/auth/callback?code=...` shows WorkOS is redirecting to its own domain instead of your app domain.

**Possible Causes:**
1. Redirect URIs not configured in WorkOS Dashboard
2. WorkOS using default redirect (its own domain)
3. Missing redirect URI configuration

---

## ✅ Solution

### Step 1: Configure Redirect URIs in WorkOS Dashboard

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Navigate to **Authentication** → **Redirects**
3. **Add these URIs:**

**Development:**
```
http://localhost:5173/auth/callback
http://localhost:5173
http://localhost:5173/
```

**Production:**
```
https://trace.kooshapari.com/auth/callback
https://trace.kooshapari.com
https://trace.kooshapari.com/
```

### Step 2: Verify Redirect URI Configuration

**Important:** Make sure:
- ✅ URIs are added to WorkOS Dashboard
- ✅ URIs match exactly (including protocol, port, path)
- ✅ No trailing slashes mismatch (add both `/auth/callback` and `/auth/callback/` if needed)

### Step 3: Check WorkOS Connection Settings

**WorkOS Dashboard** → **Authentication** → **Connections** → **GitHub**:

- Verify **Redirect URI** is set to: `https://significant-vessel-93-staging.authkit.app/callback/github`
- This is where GitHub redirects TO WorkOS (correct)
- But WorkOS should redirect BACK to your app URIs (configured in Redirects)

---

## 🔄 How It Should Work

### Correct Flow:

1. User visits: `http://localhost:5173/auth/login`
2. App calls `signIn()` → Redirects to WorkOS hosted UI
3. User authenticates with GitHub
4. GitHub redirects to: `https://significant-vessel-93-staging.authkit.app/callback/github` ✅
5. WorkOS processes auth
6. **WorkOS redirects to:** `http://localhost:5173/auth/callback` ✅ (YOUR app)
7. Your app processes callback
8. User lands on dashboard ✅

### Current (Broken) Flow:

1-5. Same as above
6. **WorkOS redirects to:** `https://significant-vessel-93-staging.authkit.app/auth/callback` ❌ (WorkOS domain)
7. Page not found ❌

---

## 🔧 Additional Fixes Applied

### Updated Callback Route

The `/auth/callback` route now:
- ✅ Handles `code` parameter from WorkOS
- ✅ Handles `returnTo` parameter
- ✅ Processes authentication
- ✅ Redirects appropriately

---

## 📝 Configuration Checklist

### WorkOS Dashboard Configuration:

- [ ] **Redirect URIs Added:**
  - [ ] `http://localhost:5173/auth/callback`
  - [ ] `http://localhost:5173`
  - [ ] `http://localhost:5173/`
  - [ ] `https://trace.kooshapari.com/auth/callback`
  - [ ] `https://trace.kooshapari.com`
  - [ ] `https://trace.kooshapari.com/`

- [ ] **GitHub Connection Verified:**
  - [ ] Client ID: `Iv23liGR8KgbxkmtriYr`
  - [ ] Client Secret: [From GitHub App]
  - [ ] Redirect URI: `https://significant-vessel-93-staging.authkit.app/callback/github`

### Code Changes:

- [x] Callback route updated to handle `code` parameter
- [x] Callback route handles redirects properly
- [x] Route registered in route tree

---

## 🧪 Testing

After configuring redirect URIs in WorkOS:

1. **Clear browser cache/cookies** (important!)
2. Visit: `http://localhost:5173/auth/login`
3. Click "Sign in with GitHub"
4. Authorize on GitHub
5. Should redirect to: `http://localhost:5173/auth/callback?code=...`
6. Should then redirect to dashboard

---

## 🚨 Common Issues

### Issue: Still redirecting to WorkOS domain

**Solution:**
- Double-check redirect URIs are added in WorkOS Dashboard
- Make sure URIs match exactly (including `http://` vs `https://`)
- Clear browser cache and try again
- Check WorkOS Dashboard → Redirects → Verify URIs are listed

### Issue: "Redirect URI mismatch"

**Solution:**
- Verify redirect URI in GitHub Connection matches exactly
- Should be: `https://significant-vessel-93-staging.authkit.app/callback/github`

### Issue: Callback route not found

**Solution:**
- Restart dev server: `bun run dev`
- Verify route exists: `http://localhost:5173/auth/callback`
- Check route tree registration

---

## 📚 Related Documentation

- `WORKOS_REDIRECT_URIS_FINAL.md` - Redirect URI configuration
- `WORKOS_CALLBACK_URLS.md` - Callback URL details
- `AUTH_DELEGATION_COMPLETE.md` - Authentication setup

---

**Status:** ⚠️ Fix applied - Configure redirect URIs in WorkOS Dashboard

The callback route is updated. The main issue is that redirect URIs need to be configured in WorkOS Dashboard so WorkOS knows where to redirect users after authentication.
