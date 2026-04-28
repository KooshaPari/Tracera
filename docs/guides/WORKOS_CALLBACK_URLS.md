# WorkOS AuthKit Callback URLs

## For localhost:5173 (Development)

### GitHub OAuth Callback URL (GitHub → WorkOS)
**This is what you configure in GitHub App settings:**

```
https://significant-vessel-93-staging.authkit.app/callback/github
```

**Where:**
- `significant-vessel-93-staging.authkit.app` = Your WorkOS API Hostname (`VITE_WORKOS_API_HOSTNAME`)
- `/callback/github` = WorkOS AuthKit callback endpoint for GitHub

---

### Redirect URLs (WorkOS → Your App)

**Configure these in WorkOS Dashboard → Authentication → Redirects:**

**⚠️ Important:** WorkOS does NOT support wildcards. You must add explicit URLs.

#### Development (localhost:5173)
```
http://localhost:5173
http://localhost:5173/
http://localhost:5173/auth/login
http://localhost:5173/auth/register
```

#### Production
```
https://trace.kooshapari.com
https://trace.kooshapari.com/
https://trace.kooshapari.com/auth/login
https://trace.kooshapari.com/auth/register
```

**Note:** Add all of these URLs. WorkOS will redirect authenticated users to these URLs after successful authentication.

---

## How It Works

### Authentication Flow:

1. **User visits:** `http://localhost:5173/auth/login`
2. **App redirects to:** WorkOS hosted UI (via `signIn()`)
3. **User authenticates with GitHub**
4. **GitHub redirects to:** `https://significant-vessel-93-staging.authkit.app/callback/github`
5. **WorkOS processes auth**
6. **WorkOS redirects back to:** `http://localhost:5173` (or returnTo URL)
7. **AuthKitSync syncs auth state**

---

## Configuration Checklist

### 1. GitHub App Settings
- **Callback URL:** `https://significant-vessel-93-staging.authkit.app/callback/github`
- This is where GitHub redirects after OAuth

### 2. WorkOS Dashboard
- **Authentication → Connections → GitHub**
  - Client ID: (from GitHub App)
  - Client Secret: (from GitHub App)
  - Redirect URI: `https://significant-vessel-93-staging.authkit.app/callback/github`

- **Authentication → Redirects**
  - Add: `http://localhost:5173/*` (for development)
  - Add: `https://trace.kooshapari.com/*` (for production)

---

## Summary

**For localhost:5173:**

- **GitHub App Callback URL:** `https://significant-vessel-93-staging.authkit.app/callback/github`
- **WorkOS Redirect URLs:** `http://localhost:5173/*` (configure in WorkOS Dashboard)

The callback URL is always the WorkOS AuthKit endpoint. The redirect URLs (where WorkOS sends users back) are configured separately in WorkOS Dashboard.
