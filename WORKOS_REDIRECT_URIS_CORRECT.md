# WorkOS Redirect URIs - Correct Configuration for TraceRTM

**Date:** 2026-01-28  
**Domain:** trace.kooshapari.com  
**Dev:** localhost:5173

---

## ✅ Required Redirect URIs

Based on your existing pattern (`/auth/callback`), you should add these explicit URIs:

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

## 🔄 How It Works

### Current Flow (Without Callback Route)

1. User visits `/auth/login`
2. App calls `signIn()` → Redirects to WorkOS
3. WorkOS handles auth
4. **WorkOS redirects to:** One of your redirect URIs (e.g., `http://localhost:5173/auth/callback`)
5. **Your app receives redirect:**
   - `AuthKitSync` component detects authenticated user
   - Syncs auth state
   - Redirects to `/` or `returnTo`

### With Callback Route (Recommended)

If you create `/auth/callback` route:

1. User visits `/auth/login`
2. App calls `signIn()` → Redirects to WorkOS
3. WorkOS handles auth
4. **WorkOS redirects to:** `http://localhost:5173/auth/callback`
5. **Callback route:**
   - `AuthKitSync` syncs auth state
   - Redirects to `/` or `returnTo`
   - Cleaner separation of concerns

---

## 📝 Recommended Redirect URIs

Add these to WorkOS Dashboard → Authentication → Redirects:

### Development
```
http://localhost:5173/auth/callback
http://localhost:5173
http://localhost:5173/
```

### Production
```
https://trace.kooshapari.com/auth/callback
https://trace.kooshapari.com
https://trace.kooshapari.com/
```

**Total: 6 URIs** (3 dev + 3 production)

---

## 🎯 Why `/auth/callback`?

**Benefits:**
- ✅ Explicit callback handler
- ✅ Matches your existing pattern (`/auth/callback`)
- ✅ Cleaner separation from login/register pages
- ✅ Easier to debug (you know where callbacks land)
- ✅ Can add loading states or error handling

**Alternative (simpler):**
- Just use root URLs (`/` and `/`)
- `AuthKitSync` handles redirects from any page
- Less explicit but works fine

---

## 🔧 Implementation Options

### Option 1: Create Callback Route (Recommended)

Create `frontend/apps/web/src/routes/auth.callback.tsx`:

```typescript
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/auth/callback")({
  component: AuthCallbackPage,
});

function AuthCallbackPage() {
  // AuthKitSync handles the actual auth sync
  // This page just shows loading state
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-background/50 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
        <p className="text-muted-foreground">Completing authentication...</p>
      </div>
    </div>
  );
}
```

**Pros:**
- Explicit callback handler
- Can add custom logic
- Matches your existing pattern

**Cons:**
- Extra route to maintain

---

### Option 2: Use Root URLs Only (Simpler)

Just use:
- `http://localhost:5173`
- `https://trace.kooshapari.com`

**Pros:**
- Simpler
- Fewer URIs to manage
- `AuthKitSync` handles everything

**Cons:**
- Less explicit
- Callbacks land on root page

---

## ✅ Recommended Configuration

**Use Option 1** - Create `/auth/callback` route and add these URIs:

### Development
```
http://localhost:5173/auth/callback  ← Primary callback
http://localhost:5173               ← Fallback
http://localhost:5173/              ← Fallback with slash
```

### Production
```
https://trace.kooshapari.com/auth/callback  ← Primary callback
https://trace.kooshapari.com                ← Fallback
https://trace.kooshapari.com/               ← Fallback with slash
```

**Total: 6 URIs**

---

## 📋 Checklist

- [ ] Create `/auth/callback` route (optional but recommended)
- [ ] Add `http://localhost:5173/auth/callback` to WorkOS redirects
- [ ] Add `http://localhost:5173` to WorkOS redirects
- [ ] Add `http://localhost:5173/` to WorkOS redirects
- [ ] Add `https://trace.kooshapari.com/auth/callback` to WorkOS redirects
- [ ] Add `https://trace.kooshapari.com` to WorkOS redirects
- [ ] Add `https://trace.kooshapari.com/` to WorkOS redirects
- [ ] Test authentication flow
- [ ] Verify redirects work correctly

---

## 🎯 Summary

**Yes, you need redirect URIs like `/auth/callback`** - these are where WorkOS sends users after authentication.

**Recommended:**
- Primary: `/auth/callback` (explicit callback handler)
- Fallback: `/` and `/` (root URLs)

**Total: 6 URIs** (3 dev + 3 production)

This matches your existing pattern and provides clean callback handling.
