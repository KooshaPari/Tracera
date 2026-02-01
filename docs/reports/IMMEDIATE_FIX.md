# ⚡ IMMEDIATE FIX - Get Your Graph Working Now

**Issue:** Authentication expired, graph won't load
**Solution:** 2-step fix (30 seconds)

---

## Step 1: Clear Browser Storage (Run This Now)

**Open browser console** (Cmd+Option+I or F12), paste this, and press Enter:

```javascript
localStorage.clear(); sessionStorage.clear(); document.cookie.split(";").forEach(c => document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/")); setTimeout(() => window.location.href = '/', 500);
```

**What it does:**
- Clears localStorage (expired JWT tokens)
- Clears sessionStorage
- Clears all cookies
- Redirects to home page (will trigger login)

---

## Step 2: Sign In Again

After the page reloads:
1. Click "Sign In" (WorkOS AuthKit)
2. Enter credentials
3. You'll be redirected back

**The graph will now load!** ✅

---

## What You'll See

After re-authentication, the Traceability Graph will show:

**SwiftRide Project:**
- **531 nodes** (Features, Requirements, Stories, Tasks, APIs, Tests, etc.)
- **450 edges** (traceability links)

**Platform Projects:**
- **2,200 nodes** each
- **660 edges** each

---

## Why This Happened

Your JWT token expired while you were working. The backend correctly rejects expired tokens with 401, but this prevented even the logout endpoint from working.

**We fixed two things:**

1. ✅ **Created graph tables** and populated them (4,931 nodes total)
2. ✅ **Added `/logout-expired` endpoint** for future (no auth required)

---

## Alternative: Restart Backend (If Console Doesn't Work)

If you can't access browser console:

```bash
# Kill Python backend
pkill -f "uvicorn tracertm.api.main"

# Restart it
cd src
uvicorn tracertm.api.main:app --reload --port 8000 &

# Clear browser storage manually:
# Settings → Privacy → Clear Website Data → localhost:5173
```

Then sign in again.

---

## Future Prevention

The backend now has **two logout endpoints**:

1. `/api/v1/auth/logout` - Normal logout (requires valid token)
2. `/api/v1/auth/logout-expired` - Expired token logout (no auth required)

Update frontend to try `/logout-expired` when `/logout` returns 401.

---

## Summary

**Quick fix:** Run the JavaScript snippet above → Sign in → Graph works! ✅

**Your data is ready:**
- 4,931 items ✅
- 1,770 links ✅
- 4 graphs populated ✅
- Just need fresh authentication ✅

---

**Do this now:** Paste the JavaScript into your browser console! 🚀
