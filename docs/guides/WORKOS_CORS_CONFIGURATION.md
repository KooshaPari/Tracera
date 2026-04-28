# WorkOS CORS Configuration Guide

**Problem:** CORS error preventing WorkOS SDK from exchanging authorization code

**Error:** `No 'Access-Control-Allow-Origin' header is present on the requested resource`

---

## Root Cause

WorkOS SDK makes API calls from the browser to `api.workos.com`. These calls require CORS (Cross-Origin Resource Sharing) to be configured in the WorkOS Dashboard.

---

## Solution: Configure CORS in WorkOS Dashboard

### Step 1: Access CORS Configuration

1. **Go to:** https://dashboard.workos.com
2. **Navigate to:** Authentication → **Configure CORS** (button/link)
3. You should see a list of allowed origins

### Step 2: Add Your Development Origin

1. **Click:** "Add Origin" or similar button
2. **Enter:** `http://localhost:5173`
3. **Save** the configuration

### Step 3: Add Production Origin (When Ready)

For production, add:
- `https://trace.kooshapari.com`

---

## Verification

After configuring CORS:

1. **Clear browser cache/cookies**
2. **Restart dev server**
3. **Try authentication flow**
4. **Check browser console** - CORS errors should be gone

---

## Common Issues

### Issue: "Configure CORS" button not visible

**Solution:** 
- Make sure you're in the correct environment (Staging/Production)
- Check that AuthKit is properly set up
- Try refreshing the dashboard page

### Issue: CORS still failing after configuration

**Solutions:**
1. **Verify origin matches exactly:**
   - Development: `http://localhost:5173` (not `https://`, not port 3000)
   - No trailing slash
   - Exact match required

2. **Check browser console for specific CORS error:**
   - Look for the exact origin being blocked
   - Ensure it matches what you configured

3. **Wait a few minutes:**
   - CORS changes may take a minute to propagate

---

## Code Changes Applied

The code has been updated to:
1. **Extract code from `window.location.search` directly** - bypasses TanStack Router search param issues
2. **Detect CORS errors** - shows user-friendly error messages
3. **Wait longer for WorkOS** - gives SDK more time to exchange code

---

## Testing Checklist

- [ ] CORS configured in WorkOS Dashboard for `http://localhost:5173`
- [ ] Browser cache cleared
- [ ] Dev server restarted
- [ ] Authentication flow tested
- [ ] No CORS errors in browser console
- [ ] Code parameter preserved in callback URL
- [ ] User successfully authenticated

---

## Additional Notes

- CORS must be configured for **each environment** (Staging/Production)
- Origins are case-sensitive and must match exactly
- Wildcards are NOT supported for CORS origins
- Changes may take 1-2 minutes to propagate

---

## Status

- [x] Code updated to extract code from URL directly
- [x] CORS error detection added
- [x] User-friendly error messages added
- [ ] **ACTION REQUIRED:** Configure CORS in WorkOS Dashboard

**After configuring CORS, the authentication flow should work correctly!**
