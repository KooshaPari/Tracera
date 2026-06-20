# Redirect Loop Fix - returnTo Parameter Issue

**Problem:** Stuck in redirect loop with `returnTo=%2F%5Bobject+Object%5D`

**Root Cause:** `location.search` is an object in TanStack Router, but was being concatenated as a string, resulting in `[object Object]`.

---

## ✅ Fix Applied

### Updated `__root.tsx`

**Before (Broken):**
```typescript
const returnTo = pathname + location.search; // location.search is an object!
// Results in: "/path[object Object]"
```

**After (Fixed):**
```typescript
// Properly serialize location.search object to URLSearchParams string
let returnTo = pathname;
if (location.search && typeof location.search === 'object') {
  const searchParams = new URLSearchParams();
  Object.entries(location.search).forEach(([key, value]) => {
    // Handle string, number, boolean, array values
    searchParams.set(key, String(value));
  });
  returnTo += `?${searchParams.toString()}`;
}
```

### Updated `auth-utils.ts`

Enhanced `getReturnTo()` to handle:
- URLSearchParams objects
- String search params
- Object search params
- Invalid values (like `[object Object]`)

---

## 🧪 Testing

After fix:

1. **Clear browser cache/cookies**
2. **Visit:** `http://localhost:5173` (or any protected route)
3. **Should redirect to:** `http://localhost:5173/auth/login?returnTo=/`
4. **Sign in with GitHub**
5. **Should redirect to:** `http://localhost:5173/auth/callback?code=...`
6. **Should then redirect to:** `/` (dashboard) ✅

---

## ✅ Status

- [x] Fixed `__root.tsx` to properly serialize search params
- [x] Enhanced `getReturnTo()` to handle edge cases
- [x] Added validation to prevent `[object Object]` values

**The redirect loop should now be fixed!**
