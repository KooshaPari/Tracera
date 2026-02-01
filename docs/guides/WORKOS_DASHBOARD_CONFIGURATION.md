# WorkOS Dashboard Configuration - Complete Setup

**Date:** 2026-01-28  
**Issue:** Default redirect URI pointing to WorkOS domain instead of your app

---

## 🚨 Critical Issue Found

**Default Redirect URI:** `https://significant-vessel-93-staging.authkit.app/auth/callback` ❌

**This is wrong!** This should point to YOUR app, not WorkOS's domain.

---

## ✅ Required Changes

### 1. Update Default Redirect URI

**Current (Wrong):**
```
https://significant-vessel-93-staging.authkit.app/auth/callback
```

**Should Be:**
```
http://localhost:5173/auth/callback
```
(For development - change to production URL in production)

---

### 2. Add Missing Redirect URIs

**You have:**
- ✅ `http://localhost:5173`
- ✅ `http://localhost:5173/auth/callback`

**Missing:**
- ⚠️ `http://localhost:5173/` (with trailing slash)
- ⚠️ `https://trace.kooshapari.com` (production)
- ⚠️ `https://trace.kooshapari.com/` (production with trailing slash)
- ⚠️ `https://trace.kooshapari.com/auth/callback` (production callback)

---

### 3. Configure Other Settings

**App homepage URL:**
```
https://trace.kooshapari.com
```
✅ Already set correctly

**Sign-in endpoint:**
```
https://trace.kooshapari.com/auth/login
```
⚠️ **Not configured** - Add this!

**Sign-out redirect:**
```
https://trace.kooshapari.com/auth/login
```
⚠️ **Not configured** - Add this!

**Get started URL:**
```
https://trace.kooshapari.com/auth/register
```
⚠️ **Not configured** - Add this!

**User invitation URL:**
```
https://trace.kooshapari.com/auth/login?invite=true
```
⚠️ Currently set to WorkOS domain - Change to your app

**Password reset URL:**
```
https://trace.kooshapari.com/auth/reset-password
```
⚠️ Currently set to WorkOS domain - Change to your app

---

## 📋 Complete Configuration Checklist

### Redirect URIs

**Development:**
- [x] `http://localhost:5173` ✅
- [x] `http://localhost:5173/auth/callback` ✅
- [ ] `http://localhost:5173/` ⚠️ **Add this**

**Production:**
- [ ] `https://trace.kooshapari.com` ⚠️ **Add this**
- [ ] `https://trace.kooshapari.com/` ⚠️ **Add this**
- [ ] `https://trace.kooshapari.com/auth/callback` ⚠️ **Add this**

**Default Redirect URI:**
- [ ] Change from: `https://significant-vessel-93-staging.authkit.app/auth/callback`
- [ ] Change to: `http://localhost:5173/auth/callback` (dev) or `https://trace.kooshapari.com/auth/callback` (prod)

### Other Settings

- [x] **App homepage URL:** `https://kooshapari.com` ✅ (or change to `https://trace.kooshapari.com`)
- [ ] **Sign-in endpoint:** `https://trace.kooshapari.com/auth/login` ⚠️
- [ ] **Sign-out redirect:** `https://trace.kooshapari.com/auth/login` ⚠️
- [ ] **Get started URL:** `https://trace.kooshapari.com/auth/register` ⚠️
- [ ] **User invitation URL:** `https://trace.kooshapari.com/auth/login?invite=true` ⚠️
- [ ] **Password reset URL:** `https://trace.kooshapari.com/auth/reset-password` ⚠️

---

## 🔧 Step-by-Step Fix

### Step 1: Update Default Redirect URI

1. Find **Default** redirect URI in the list
2. Click **Edit** or change it
3. Set to: `http://localhost:5173/auth/callback` (for development)
4. Or: `https://trace.kooshapari.com/auth/callback` (for production)

### Step 2: Add Missing Redirect URIs

Click **Add Redirect URI** and add:

```
http://localhost:5173/
https://trace.kooshapari.com
https://trace.kooshapari.com/
https://trace.kooshapari.com/auth/callback
```

### Step 3: Configure Other Settings

**Sign-in endpoint:**
- Set to: `https://trace.kooshapari.com/auth/login`

**Sign-out redirect:**
- Set to: `https://trace.kooshapari.com/auth/login`

**Get started URL:**
- Set to: `https://trace.kooshapari.com/auth/register`

**User invitation URL:**
- Change from: `https://significant-vessel-93-staging.authkit.app/invite`
- Change to: `https://trace.kooshapari.com/auth/login?invite=true`

**Password reset URL:**
- Change from: `https://significant-vessel-93-staging.authkit.app/reset-password`
- Change to: `https://trace.kooshapari.com/auth/reset-password`

---

## ✅ After Configuration

1. **Clear browser cache/cookies**
2. **Restart dev server:** `bun run dev`
3. **Test authentication:**
   - Visit: `http://localhost:5173/auth/login`
   - Sign in with GitHub
   - Should redirect to: `http://localhost:5173/auth/callback?code=...` ✅
   - Then redirects to dashboard ✅

---

## 🎯 Summary

**Main Issue:** Default redirect URI is set to WorkOS domain instead of your app domain.

**Fix:**
1. Change Default redirect URI to your app domain
2. Add missing redirect URIs (trailing slash, production URLs)
3. Configure sign-in endpoint, sign-out redirect, etc.

**Status:** ⚠️ **URGENT** - Update Default redirect URI immediately

This is why you're getting "Page not found" - WorkOS is using the default redirect which points to its own domain.
