# WorkOS AuthKit Redirect URLs - Explicit List

**Date:** 2026-01-28  
**Important:** WorkOS does NOT support wildcards. You must add explicit URLs.

---

## 🔗 Redirect URLs to Configure

### In WorkOS Dashboard

**Go to:** WorkOS Dashboard → Authentication → Redirects

**Add these URLs one by one:**

---

### Development (localhost:5173)

Add these 4 URLs:

```
http://localhost:5173
http://localhost:5173/
http://localhost:5173/auth/login
http://localhost:5173/auth/register
```

**Why these URLs:**
- `http://localhost:5173` - Root redirect (default after auth)
- `http://localhost:5173/` - Root with trailing slash
- `http://localhost:5173/auth/login` - Login page redirect
- `http://localhost:5173/auth/register` - Register page redirect

---

### Production (trace.kooshapari.com)

Add these 4 URLs:

```
https://trace.kooshapari.com
https://trace.kooshapari.com/
https://trace.kooshapari.com/auth/login
https://trace.kooshapari.com/auth/register
```

**Why these URLs:**
- `https://trace.kooshapari.com` - Root redirect (default after auth)
- `https://trace.kooshapari.com/` - Root with trailing slash
- `https://trace.kooshapari.com/auth/login` - Login page redirect
- `https://trace.kooshapari.com/auth/register` - Register page redirect

---

## 🔄 How Redirects Work

### Authentication Flow:

1. **User visits:** `http://localhost:5173/auth/login`
2. **App redirects to:** WorkOS hosted UI
3. **User authenticates with GitHub**
4. **GitHub redirects to:** `https://significant-vessel-93-staging.authkit.app/callback/github`
5. **WorkOS processes auth**
6. **WorkOS redirects back to:** One of the configured redirect URLs
   - Default: `http://localhost:5173` (root)
   - Or: `returnTo` parameter if specified
7. **AuthKitSync syncs auth state**
8. **User sees dashboard**

---

## 📝 Configuration Steps

### Step 1: Add Redirect URLs in WorkOS

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Navigate to **Authentication** → **Redirects**
3. Click **Add Redirect URL**
4. Add each URL one by one:

**Development URLs:**
- `http://localhost:5173`
- `http://localhost:5173/`
- `http://localhost:5173/auth/login`
- `http://localhost:5173/auth/register`

**Production URLs:**
- `https://trace.kooshapari.com`
- `https://trace.kooshapari.com/`
- `https://trace.kooshapari.com/auth/login`
- `https://trace.kooshapari.com/auth/register`

### Step 2: Verify URLs

After adding, verify all URLs are listed in the WorkOS Dashboard.

---

## ✅ Checklist

- [ ] Added `http://localhost:5173` to WorkOS redirects
- [ ] Added `http://localhost:5173/` to WorkOS redirects
- [ ] Added `http://localhost:5173/auth/login` to WorkOS redirects
- [ ] Added `http://localhost:5173/auth/register` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com/` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com/auth/login` to WorkOS redirects
- [ ] Added `https://trace.kooshapari.com/auth/register` to WorkOS redirects

---

## 🚨 Common Issues

### Issue: "Redirect URI mismatch" error

**Solution:** Make sure you've added the exact URL that WorkOS is trying to redirect to. Check:
- Protocol (`http://` vs `https://`)
- Port number (`:5173` for dev)
- Trailing slash (`/` vs no `/`)
- Path (`/auth/login` vs `/`)

### Issue: Redirects to wrong page

**Solution:** Check `AuthKitSync.tsx` - it handles redirects after authentication. Make sure the redirect URLs match what your app expects.

---

## 📚 Related Documentation

- `WORKOS_CALLBACK_URLS.md` - Callback URL configuration
- `WORKOS_FULL_DELEGATION_SETUP.md` - Complete setup guide
- `AUTH_DELEGATION_COMPLETE.md` - Authentication implementation

---

**Status:** ✅ Ready to configure - Add all 8 URLs to WorkOS Dashboard
