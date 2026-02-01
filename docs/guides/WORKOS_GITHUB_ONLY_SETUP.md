# WorkOS AuthKit - GitHub Only SSO Setup

**Date:** 2026-01-28  
**Requirement:** Only GitHub SSO, no email/password authentication

---

## ✅ Changes Made

### 1. Login Page (`routes/auth.login.tsx`)
- ✅ Removed all email/password form code
- ✅ Removed custom login UI
- ✅ Now redirects immediately to WorkOS AuthKit hosted login UI
- ✅ Uses `signIn()` with `redirectUrl` parameter
- ✅ Shows loading state during redirect

### 2. Register Page (`routes/auth.register.tsx`)
- ✅ Removed all email/password form code
- ✅ Removed custom registration UI
- ✅ Now redirects immediately to WorkOS AuthKit hosted signup UI
- ✅ Uses `signUp()` with `redirectUrl` parameter
- ✅ Shows loading state during redirect

### 3. Code Cleanup
- ✅ Removed unused imports (Eye, EyeOff, Input, Checkbox, etc.)
- ✅ Removed form validation logic
- ✅ Removed email/password state management
- ✅ Simplified to use WorkOS hosted UI only

---

## 🔧 WorkOS Dashboard Configuration

To enable **GitHub-only SSO** (no email/password), configure in WorkOS dashboard:

### Step 1: Configure GitHub Connection
1. Go to **WorkOS Dashboard** → **Authentication** → **Connections**
2. Find **GitHub** connection
3. Ensure it's **Enabled**
4. Configure with GitHub App credentials:
   - **Client ID:** From GitHub App registration
   - **Client Secret:** From GitHub App registration
   - **Redirect URI:** `https://significant-vessel-93-staging.authkit.app/callback/github`

### Step 2: Disable Email/Password
1. Go to **WorkOS Dashboard** → **Authentication** → **Settings**
2. Find **Email/Password** connection
3. **Disable** it (or remove it)
4. Ensure only **GitHub** is enabled

### Step 3: Configure Hosted UI
1. Go to **WorkOS Dashboard** → **Authentication** → **Hosted UI**
2. Ensure **Hosted UI** is enabled
3. Configure branding (optional):
   - Logo
   - Colors
   - Custom domain (if applicable)

### Step 4: Set Redirect URLs
1. Go to **WorkOS Dashboard** → **Authentication** → **Settings**
2. Add **Redirect URLs**:
   - `https://trace.kooshapari.com/*`
   - `http://localhost:3000/*` (for development)

---

## 🔄 Authentication Flow

### Login Flow
1. User visits `/auth/login`
2. Page immediately redirects to WorkOS hosted login UI
3. WorkOS shows GitHub OAuth button (only option)
4. User clicks GitHub, authorizes on GitHub
5. GitHub redirects to WorkOS callback
6. WorkOS redirects back to app with auth token
7. `AuthKitSync` component syncs auth state
8. User is redirected to dashboard (or returnTo URL)

### Signup Flow
1. User visits `/auth/register`
2. Page immediately redirects to WorkOS hosted signup UI
3. WorkOS shows GitHub OAuth button (only option)
4. User clicks GitHub, authorizes on GitHub
5. GitHub redirects to WorkOS callback
6. WorkOS creates account and redirects back
7. `AuthKitSync` component syncs auth state
8. User is redirected to dashboard

---

## 📝 Environment Variables

Ensure these are set in `.env`:

```bash
# WorkOS (Required)
VITE_WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66
WORKOS_API_KEY=sk_test_a2V5KYZR40RK7R9X3PPB5SEJ66
VITE_WORKOS_API_HOSTNAME=significant-vessel-93-staging.authkit.app

# GitHub App (After registration)
GITHUB_APP_ID=your_app_id
GITHUB_APP_CLIENT_ID=your_client_id
GITHUB_APP_CLIENT_SECRET=your_client_secret
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

---

## 🧪 Testing

### Test Login
1. Visit `http://localhost:3000/auth/login`
2. Should immediately redirect to WorkOS hosted UI
3. Should only show GitHub option
4. After GitHub auth, should redirect back to app

### Test Signup
1. Visit `http://localhost:3000/auth/register`
2. Should immediately redirect to WorkOS hosted signup UI
3. Should only show GitHub option
4. After GitHub auth, should create account and redirect back

### Test Protected Routes
1. Try accessing `/` without auth
2. Should redirect to `/auth/login`
3. After login, should redirect back to `/`

---

## ⚠️ Important Notes

1. **WorkOS Required:** The app now requires WorkOS to be enabled. If `VITE_WORKOS_CLIENT_ID` is not set, the auth pages will still try to redirect but will fail.

2. **No Fallback:** There's no email/password fallback anymore. Users MUST use GitHub SSO.

3. **Hosted UI:** All authentication UI is now handled by WorkOS. You cannot customize the login/signup forms directly.

4. **Customization:** To customize the hosted UI appearance, use WorkOS dashboard settings.

5. **Redirect Handling:** The `redirectUrl` parameter ensures users return to the correct page after authentication.

---

## 🔗 Related Files

- `frontend/apps/web/src/routes/auth.login.tsx` - Login page (redirects to WorkOS)
- `frontend/apps/web/src/routes/auth.register.tsx` - Register page (redirects to WorkOS)
- `frontend/apps/web/src/components/auth/AuthKitSync.tsx` - Syncs WorkOS auth state
- `frontend/apps/web/src/providers/AppProviders.tsx` - AuthKitProvider setup
- `frontend/apps/web/src/routes/__root.tsx` - Route protection logic

---

## ✅ Checklist

- [x] Removed email/password forms from login page
- [x] Removed email/password forms from register page
- [x] Updated login to use WorkOS hosted UI
- [x] Updated register to use WorkOS hosted UI
- [x] Removed unused imports and code
- [ ] Configure WorkOS dashboard to disable email/password
- [ ] Configure WorkOS dashboard to enable GitHub only
- [ ] Test login flow end-to-end
- [ ] Test signup flow end-to-end
- [ ] Test protected route redirects
- [ ] Verify GitHub OAuth callback works

---

**Status:** ✅ Code changes complete - Ready for WorkOS dashboard configuration
