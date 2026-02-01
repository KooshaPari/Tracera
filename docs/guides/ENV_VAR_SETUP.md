# Environment Variables Setup - WorkOS AuthKit

**Issue:** `useAuth must be used within an AuthKitProvider`

**Root Cause:** `VITE_WORKOS_CLIENT_ID` environment variable was not set in `.env.local`

---

## ✅ Fix Applied

Added WorkOS environment variables to `.env.local`:

```bash
VITE_WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66
VITE_WORKOS_API_HOSTNAME=significant-vessel-93-staging.authkit.app
```

---

## 📝 Required Environment Variables

### For Development (`.env.local`)

```bash
# WorkOS AuthKit Configuration
VITE_WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66
VITE_WORKOS_API_HOSTNAME=significant-vessel-93-staging.authkit.app
```

### For Production

Set these in your deployment platform (Vercel, Netlify, etc.):

```bash
VITE_WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66
VITE_WORKOS_API_HOSTNAME=significant-vessel-93-staging.authkit.app
```

---

## 🔄 Next Steps

1. **Restart Dev Server**
   ```bash
   # Stop the current dev server (Ctrl+C)
   # Then restart:
   bun run dev
   ```

2. **Verify Setup**
   - Check browser console for: `[AppProviders] WorkOS Client ID: Found`
   - Visit `/auth/login` - should redirect to WorkOS hosted UI
   - No more "useAuth must be used within an AuthKitProvider" error

3. **Test Authentication**
   - Visit `/auth/login`
   - Should redirect to WorkOS hosted UI
   - Sign in with GitHub
   - Should redirect back to app

---

## 🐛 Troubleshooting

### If error persists:

1. **Check env vars are loaded:**
   ```bash
   # In browser console:
   console.log(import.meta.env.VITE_WORKOS_CLIENT_ID)
   # Should show: "client_01K4KYZR40RK7R9X3PPB5SEJ66"
   ```

2. **Restart dev server:**
   - Vite requires restart to pick up new env vars
   - Stop server completely and restart

3. **Check file location:**
   - `.env.local` should be in `frontend/apps/web/` directory
   - Not in root or other directories

4. **Verify file format:**
   - No spaces around `=`
   - No quotes needed (unless value has spaces)
   - One variable per line

---

## ✅ Verification Checklist

- [x] Added `VITE_WORKOS_CLIENT_ID` to `.env.local`
- [x] Added `VITE_WORKOS_API_HOSTNAME` to `.env.local`
- [x] Updated `.env.example` with WorkOS vars
- [x] Updated `AppProviders.tsx` to read env vars correctly
- [x] Added error handling in auth pages
- [ ] Restart dev server
- [ ] Test login flow
- [ ] Verify no more provider errors

---

**Status:** ✅ Environment variables added - Restart dev server to apply changes
