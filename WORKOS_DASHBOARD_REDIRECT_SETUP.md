# WorkOS Dashboard Redirect URI Setup - URGENT FIX

**Problem:** WorkOS is using `redirect_uri=http://localhost:5173` (root) in authorize URL, but we need `/auth/callback`

**Solution:** Configure WorkOS Dashboard Redirect URIs correctly

---

## 🎯 Required Configuration

### Step 1: Set Default Redirect URI

1. Go to: **WorkOS Dashboard → Authentication → Redirects**
2. Find the **"Default Redirect URI"** field (marked with a star ⭐)
3. Set it to: `http://localhost:5173` (root, **NO trailing slash**)
4. Click **Save**

### Step 2: Add All Required Redirect URIs

Add these **exact** URLs to your Redirect URIs list:

#### Development:
- ✅ `http://localhost:5173` ← **SET AS DEFAULT** (no trailing slash)
- ✅ `http://localhost:5173/` (with trailing slash)
- ✅ `http://localhost:5173/auth/callback` ← **REQUIRED for callback**

#### Production:
- ✅ `https://trace.kooshapari.com` ← **SET AS DEFAULT FOR PROD** (no trailing slash)
- ✅ `https://trace.kooshapari.com/` (with trailing slash)
- ✅ `https://trace.kooshapari.com/auth/callback` ← **REQUIRED for callback**

---

## 🔧 How It Works

When you call `signIn({ redirectPathname: "/auth/callback" })`:

1. WorkOS takes the **Default Redirect URI**: `http://localhost:5173`
2. Appends the `redirectPathname`: `/auth/callback`
3. **Result:** `http://localhost:5173/auth/callback` ✅

**BUT** this final URL (`http://localhost:5173/auth/callback`) **MUST** be in your Redirect URIs list, otherwise WorkOS will reject it!

---

## ⚠️ Current Issue

You're seeing:
```
redirect_uri=http://localhost:5173
```

This means:
- ✅ Default Redirect URI is correctly set to `http://localhost:5173`
- ❌ But `http://localhost:5173/auth/callback` is **missing** from Redirect URIs list

---

## ✅ Fix Steps

1. **Go to WorkOS Dashboard → Authentication → Redirects**

2. **Check Default Redirect URI:**
   - Should be: `http://localhost:5173` (no trailing slash)
   - If not, change it

3. **Add Missing URI:**
   - Click **"Add Redirect URI"**
   - Enter: `http://localhost:5173/auth/callback`
   - Click **Add**

4. **Verify List Contains:**
   - `http://localhost:5173` (Default)
   - `http://localhost:5173/`
   - `http://localhost:5173/auth/callback` ← **THIS ONE WAS MISSING**

5. **For Production:**
   - Add: `https://trace.kooshapari.com/auth/callback`
   - Set Default to: `https://trace.kooshapari.com` (for prod environment)

---

## 🧪 Testing

After updating:

1. **Clear browser cache/cookies**
2. **Visit:** `http://localhost:5173`
3. **Should redirect to:** `http://localhost:5173/auth/login?returnTo=/`
4. **Click sign in** → Redirects to WorkOS
5. **After GitHub auth** → Should redirect to: `http://localhost:5173/auth/callback?code=...` ✅
6. **Should then redirect to:** `/` (dashboard) ✅

---

## 📝 Code Status

✅ Code is already correct:
- `signIn({ redirectPathname: "/auth/callback" })` ✅
- Callback route exists at `/auth/callback` ✅

**Only WorkOS Dashboard configuration needed!**

---

## 🚨 If Still Not Working

If you still see `redirect_uri=http://localhost:5173` after adding `/auth/callback`:

1. **Check for duplicates** - Remove any duplicate `http://localhost:5173` entries
2. **Verify Default** - Default should be `http://localhost:5173` (no trailing slash)
3. **Check environment** - Make sure you're editing the correct environment (staging vs production)
4. **Wait 30 seconds** - Changes may take a moment to propagate

---

## ✅ Summary

**Action Required:**
- [ ] Add `http://localhost:5173/auth/callback` to Redirect URIs
- [ ] Verify Default is `http://localhost:5173` (no trailing slash)
- [ ] Add production callback: `https://trace.kooshapari.com/auth/callback`
- [ ] Test authentication flow

**Code:** ✅ Already correct, no changes needed
