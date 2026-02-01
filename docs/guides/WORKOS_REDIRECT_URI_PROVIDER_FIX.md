# WorkOS Redirect URI Provider Fix

**Problem:** WorkOS error: "This is not a valid redirect URI" - trying to use `http://localhost:5173` but only `http://localhost:5173/auth/callback` is allowed.

**Root Cause:** The `redirectUri` should be set on `AuthKitProvider`, not passed to `signIn()` or `signUp()`.

---

## ✅ Fix Applied

### 1. Set `redirectUri` on AuthKitProvider

**File:** `AppProviders.tsx`

```typescript
const providerProps: { clientId: string; redirectUri?: string } = {
	clientId: workosClientId,
};

// Set redirectUri on provider - used when constructing sign-in/sign-up URLs
if (typeof window !== 'undefined') {
	providerProps.redirectUri = `${window.location.origin}/auth/callback`;
}
```

**Why:** According to WorkOS React SDK docs, `redirectUri` is a prop on `AuthKitProvider`, not a parameter to `signIn()`.

### 2. Removed redirectUri from signIn/signUp calls

**Before:**
```typescript
signIn({ redirectUri });
```

**After:**
```typescript
signIn(); // Uses redirectUri from AuthKitProvider
```

**Why:** `signIn()` and `signUp()` don't accept `redirectUri` as a parameter - they use the one from the provider.

---

## 🔧 WorkOS Dashboard Configuration

**Required Configuration:**

1. **Go to:** WorkOS Dashboard → Authentication → Redirects
2. **Ensure this is in Redirect URIs list:**
   - ✅ `http://localhost:5173/auth/callback` (must be exact match)
3. **Default Redirect URI can be:** `http://localhost:5173` or `http://localhost:5173/auth/callback`

**Important:** The `redirectUri` in `AuthKitProvider` (`http://localhost:5173/auth/callback`) must match EXACTLY an entry in the Redirect URIs list.

---

## 🧪 Testing

1. **Clear browser cache/cookies**
2. **Restart dev server**
3. **Visit:** `http://localhost:5173`
4. **Should redirect to:** `/auth/login`
5. **Click sign in** → Should redirect to WorkOS (no redirect URI errors)
6. **After GitHub auth** → Should redirect to `/auth/callback?code=...`

---

## ✅ Status

- [x] Set `redirectUri` on `AuthKitProvider`
- [x] Removed `redirectUri` from `signIn()` and `signUp()` calls
- [x] Updated both login and register pages
- [ ] **ACTION REQUIRED:** Verify `http://localhost:5173/auth/callback` is in WorkOS Dashboard Redirect URIs list

**The redirect URI error should now be resolved!**
