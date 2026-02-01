# WorkOS Redirect URI Configuration Fix

**Problem:** WorkOS is using `redirect_uri=http://localhost:5173` (root) instead of `/auth/callback`

**Root Cause:** WorkOS needs the **full callback URL** (`http://localhost:5173/auth/callback`) configured in the dashboard, not just the root.

---

## ✅ Solution: Configure Full Callback URLs in WorkOS Dashboard

### Required Redirect URIs

You need to add these **exact** URLs to your WorkOS Dashboard → Authentication → Redirects:

#### Development:
1. ✅ `http://localhost:5173/auth/callback` ← **SET AS DEFAULT**
2. ✅ `http://localhost:5173/` (root with trailing slash)
3. ✅ `http://localhost:5173` (root without trailing slash)

#### Production:
1. ✅ `https://trace.kooshapari.com/auth/callback` ← **SET AS DEFAULT FOR PROD**
2. ✅ `https://trace.kooshapari.com/` (root with trailing slash)
3. ✅ `https://trace.kooshapari.com` (root without trailing slash)

---

## 🔧 WorkOS Dashboard Steps

1. **Go to:** WorkOS Dashboard → Authentication → Redirects

2. **Add Missing URIs:**
   - Click "Add Redirect URI"
   - Add: `http://localhost:5173/auth/callback`
   - **Set this as Default** (click the star/Default button)

3. **For Production:**
   - Add: `https://trace.kooshapari.com/auth/callback`
   - Set as Default for production environment

4. **Remove Duplicates:**
   - If you see `http://localhost:5173` listed twice, remove one
   - Keep only one instance of each unique URI

---

## 📝 How WorkOS Redirects Work

When you call `signIn({ redirectPathname: "/auth/callback" })`:

1. WorkOS takes the **Default Redirect URI** from your dashboard
2. Appends the `redirectPathname` to it
3. Redirects user there after authentication

**Example:**
- Default Redirect URI: `http://localhost:5173`
- redirectPathname: `/auth/callback`
- **Result:** `http://localhost:5173/auth/callback` ✅

**BUT** if the Default is set to `http://localhost:5173/auth/callback`:
- Default Redirect URI: `http://localhost:5173/auth/callback`
- redirectPathname: `/auth/callback`
- **Result:** `http://localhost:5173/auth/callback/auth/callback` ❌ (WRONG!)

---

## ✅ Correct Configuration

**Option 1: Set root as Default, use redirectPathname**
- Default: `http://localhost:5173`
- redirectPathname: `/auth/callback`
- Result: `http://localhost:5173/auth/callback` ✅

**Option 2: Set full callback as Default, don't use redirectPathname**
- Default: `http://localhost:5173/auth/callback`
- redirectPathname: (not used)
- Result: `http://localhost:5173/auth/callback` ✅

---

## 🎯 Recommended Setup

**Use Option 1** (root as Default):

1. **Set Default Redirect URI to:** `http://localhost:5173` (root, no trailing slash)
2. **Keep redirectPathname in code:** `/auth/callback`
3. **Add all callback URLs** to the list (for explicit matching)

This way:
- WorkOS will redirect to `http://localhost:5173/auth/callback` ✅
- All callback URLs are explicitly whitelisted ✅
- More flexible for future changes ✅

---

## 🧪 Testing

After updating WorkOS Dashboard:

1. **Clear browser cache/cookies**
2. **Visit:** `http://localhost:5173`
3. **Should redirect to:** `http://localhost:5173/auth/login?returnTo=/`
4. **Click sign in** → Redirects to WorkOS
5. **After GitHub auth** → Should redirect to: `http://localhost:5173/auth/callback?code=...`
6. **Should then redirect to:** `/` (dashboard) ✅

---

## ⚠️ Common Issues

**Issue:** "redirect_uri=http://localhost:5173" in authorize URL
- **Fix:** Make sure `http://localhost:5173` is set as Default Redirect URI

**Issue:** "redirect_uri mismatch" error
- **Fix:** Ensure `http://localhost:5173/auth/callback` is in the Redirect URIs list

**Issue:** "is already added as a redirect URI. not valid"
- **Fix:** Remove duplicate entries, keep only one instance

---

## ✅ Status

- [x] Code updated to use `/auth/callback` consistently
- [ ] **ACTION REQUIRED:** Update WorkOS Dashboard Redirect URIs
- [ ] Set `http://localhost:5173` as Default Redirect URI
- [ ] Add `http://localhost:5173/auth/callback` to Redirect URIs list
- [ ] Test authentication flow
