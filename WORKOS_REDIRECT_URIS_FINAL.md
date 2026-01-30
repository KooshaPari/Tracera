# WorkOS Redirect URIs - Final Configuration

**Date:** 2026-01-28  
**Status:** ✅ Callback route created - Add these URIs to WorkOS

---

## ✅ Required Redirect URIs

Add these **6 explicit URIs** to WorkOS Dashboard → Authentication → Redirects:

### Development (localhost:5173)

```
http://localhost:5173/auth/callback
http://localhost:5173
http://localhost:5173/
```

### Production (trace.kooshapari.com)

```
https://trace.kooshapari.com/auth/callback
https://trace.kooshapari.com
https://trace.kooshapari.com/
```

---

## ✅ What Was Done

1. ✅ Created `/auth/callback` route (`auth.callback.tsx`)
2. ✅ Added route to route tree (`routeTree.gen.ts`)
3. ✅ Route shows loading state while `AuthKitSync` handles auth

---

## 🔄 How It Works

### Authentication Flow:

1. **User visits:** `http://localhost:5173/auth/login`
2. **App redirects to:** WorkOS hosted UI (via `signIn()`)
3. **User authenticates with GitHub**
4. **GitHub redirects to:** `https://significant-vessel-93-staging.authkit.app/callback/github`
5. **WorkOS processes auth:**
   - Creates/updates user account
   - Links GitHub identity
   - Generates access token
6. **WorkOS redirects to:** `http://localhost:5173/auth/callback` (one of your redirect URIs)
7. **Callback route:**
   - Shows loading state
   - `AuthKitSync` component detects authenticated user
   - Syncs auth state to `authStore`
   - Redirects to `/` or `returnTo` URL
8. **User lands on dashboard** ✅

---

## 📝 Configuration Steps

### Step 1: Add Redirect URIs in WorkOS

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Navigate to **Authentication** → **Redirects**
3. Click **Add Redirect URI**
4. Add each URI one by one:

**Development:**
- `http://localhost:5173/auth/callback`
- `http://localhost:5173`
- `http://localhost:5173/`

**Production:**
- `https://trace.kooshapari.com/auth/callback`
- `https://trace.kooshapari.com`
- `https://trace.kooshapari.com/`

### Step 2: Verify Route Works

1. Restart dev server: `bun run dev`
2. Visit: `http://localhost:5173/auth/callback`
3. Should see loading spinner (route is working)

---

## ✅ Checklist

- [x] Created `/auth/callback` route
- [x] Added route to route tree
- [ ] Added `http://localhost:5173/auth/callback` to WorkOS redirects
- [ ] Added `http://localhost:5173` to WorkOS redirects
- [ ] Added `http://localhost:5173/` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com/auth/callback` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com/` to WorkOS redirects
- [ ] Test authentication flow
- [ ] Verify redirects work correctly

---

## 🎯 Summary

**Yes, you need redirect URIs like `/auth/callback`** - these are where WorkOS sends users after authentication.

**Total: 6 URIs** (3 dev + 3 production)

**Primary:** `/auth/callback` - Explicit callback handler  
**Fallback:** `/` and `/` - Root URLs for flexibility

The callback route is now created and ready. Just add the URIs to WorkOS Dashboard!
