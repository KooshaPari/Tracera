# WorkOS Code Exchange Issue

**Problem:** WorkOS `useAuth()` hook is not automatically exchanging the authorization code for a user.

**Symptoms:**
- Code is present in URL: `?code=01KG49STM46S3RMQE47161NPH7`
- `isLoading` becomes `false`
- But `user` remains `null`
- After timeout, redirects to login

---

## Root Cause

WorkOS React SDK's `useAuth()` hook should automatically detect the code in the URL and exchange it for user info, but it's not working. This could be due to:

1. **Redirect URI Mismatch** - The redirect URI in WorkOS Dashboard doesn't match exactly
2. **Client ID Mismatch** - The Client ID doesn't match
3. **SDK Configuration** - Missing `redirectUri` prop in `AuthKitProvider`
4. **Code Expiration** - Code expired (codes are valid for 10 minutes)

---

## ✅ Fixes Applied

### 1. Added `redirectUri` to AuthKitProvider

**File:** `AppProviders.tsx`

```typescript
providerProps.redirectUri = `${window.location.origin}/auth/callback`;
```

**Why:** WorkOS SDK might need explicit redirectUri to process callbacks correctly.

### 2. Enhanced Error Messages

**File:** `auth.callback.tsx`

Added detailed error messages to help diagnose the issue:
- Lists possible causes
- Shows code snippet (first 20 chars)
- Provides user-friendly alert

### 3. Increased Wait Time

Changed timeout from 3 seconds to 5 seconds to give WorkOS more time.

---

## 🔍 Debugging Steps

1. **Verify WorkOS Dashboard Configuration:**
   - Go to WorkOS Dashboard → Authentication → Redirects
   - Ensure `http://localhost:5173/auth/callback` is listed
   - Set it as **Default Redirect URI**
   - Verify it matches EXACTLY (no trailing slash, correct protocol)

2. **Verify Client ID:**
   - Check `.env` file: `VITE_WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66`
   - Verify it matches WorkOS Dashboard → API Keys → Client ID

3. **Check Browser Console:**
   - Look for WorkOS SDK errors
   - Check network tab for failed API calls
   - Verify code is being sent to WorkOS

4. **Test with Fresh Code:**
   - Clear cookies/localStorage
   - Get a new code by signing in again
   - Codes expire after 10 minutes

---

## 🎯 Next Steps

1. **Check WorkOS Dashboard:**
   - Verify redirect URI is exactly: `http://localhost:5173/auth/callback`
   - No trailing slash, correct protocol (http not https for localhost)

2. **Check Console Logs:**
   - Look for any WorkOS SDK errors
   - Check network requests to WorkOS API

3. **Try Manual Code Exchange:**
   - If SDK doesn't work, we might need to manually exchange code server-side

---

## ⚠️ Possible Solutions

If the SDK still doesn't work, we might need to:

1. **Server-Side Code Exchange:**
   - Create a backend endpoint to exchange code for tokens
   - Call it from the callback page

2. **Check WorkOS SDK Version:**
   - Ensure we're using the latest version
   - Check for known issues/bugs

3. **Contact WorkOS Support:**
   - If configuration is correct but SDK still fails
   - Provide error logs and configuration details

---

## ✅ Status

- [x] Added `redirectUri` to AuthKitProvider
- [x] Enhanced error messages
- [x] Increased wait time
- [ ] **ACTION REQUIRED:** Verify WorkOS Dashboard configuration
- [ ] **ACTION REQUIRED:** Check browser console for WorkOS errors
- [ ] **ACTION REQUIRED:** Test with fresh authentication code
