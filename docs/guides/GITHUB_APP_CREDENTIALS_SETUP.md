# GitHub App Credentials Setup

**Date:** 2026-01-28  
**App ID:** 2750779  
**Client ID:** Iv23liGR8KgbxkmtriYr

---

## 🔐 Credentials Received

### From GitHub App Registration:

- **App ID:** `2750779`
- **Client ID:** `Iv23liGR8KgbxkmtriYr`
- **Client Secret:** [Get from GitHub App settings - not provided yet]
- **Webhook Secret:** `e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910`
- **Private Key:** `/Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem`

---

## ⚠️ Get Missing Credentials

### 1. Get Client Secret

1. Go to [GitHub App Settings](https://github.com/settings/apps)
2. Find your app (TraceRTM)
3. Go to **General** → **Client secrets**
4. Click **Generate a new client secret**
5. Copy the secret (you'll only see it once!)

### 2. Verify Private Key

The private key file should be at:
```
/Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem
```

**Move it to a secure location:**
```bash
# Create secure directory
mkdir -p ~/.ssh/github-apps

# Move private key
mv /Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem ~/.ssh/github-apps/tracertm-private-key.pem

# Set secure permissions
chmod 600 ~/.ssh/github-apps/tracertm-private-key.pem
```

---

## 📝 Environment Variables Setup

### Backend Environment Variables

Add to your backend `.env` file (or wherever you store backend env vars):

```bash
# GitHub App (Repository Access & API)
GITHUB_APP_ID=2750779
GITHUB_APP_CLIENT_ID=Iv23liGR8KgbxkmtriYr
GITHUB_APP_CLIENT_SECRET=your_client_secret_here
GITHUB_WEBHOOK_SECRET=e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910
GITHUB_PRIVATE_KEY_PATH=/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem

# OR use inline private key (if preferred):
# GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
```

### Frontend Environment Variables (if needed)

The frontend typically doesn't need GitHub App credentials directly, but if you need them:

```bash
# Frontend .env.local (usually not needed)
# GitHub App credentials are handled by backend
```

---

## 🔧 WorkOS Configuration

### For OAuth Authentication (WorkOS Dashboard)

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Navigate to **Authentication** → **Connections**
3. Click **Add Connection** → Select **GitHub**
4. Enter:
   - **Client ID:** `Iv23liGR8KgbxkmtriYr`
   - **Client Secret:** [Get from GitHub App settings]
   - **Redirect URI:** `https://significant-vessel-93-staging.authkit.app/callback/github`

**Note:** WorkOS uses the same Client ID/Secret for OAuth authentication.

---

## 📋 Complete Setup Checklist

### 1. Secure Private Key
- [ ] Move private key to secure location (`~/.ssh/github-apps/`)
- [ ] Set permissions: `chmod 600`
- [ ] Verify key file exists and is readable

### 2. Get Client Secret
- [ ] Go to GitHub App settings
- [ ] Generate new client secret
- [ ] Copy and store securely

### 3. Backend Configuration
- [ ] Add `GITHUB_APP_ID=2750779` to backend `.env`
- [ ] Add `GITHUB_APP_CLIENT_ID=Iv23liGR8KgbxkmtriYr` to backend `.env`
- [ ] Add `GITHUB_APP_CLIENT_SECRET=...` to backend `.env`
- [ ] Add `GITHUB_WEBHOOK_SECRET=e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910` to backend `.env`
- [ ] Add `GITHUB_PRIVATE_KEY_PATH=...` to backend `.env`
- [ ] Restart backend server

### 4. WorkOS Configuration
- [ ] Add GitHub connection in WorkOS Dashboard
- [ ] Use Client ID: `Iv23liGR8KgbxkmtriYr`
- [ ] Use Client Secret from GitHub
- [ ] Set Redirect URI: `https://significant-vessel-93-staging.authkit.app/callback/github`

### 5. Test Configuration
- [ ] Test GitHub App installation flow
- [ ] Test webhook events
- [ ] Test repository API access
- [ ] Test OAuth authentication via WorkOS

---

## 🔒 Security Best Practices

### Private Key Storage

**Option 1: File Path (Recommended)**
```bash
GITHUB_PRIVATE_KEY_PATH=/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem
```

**Option 2: Inline (Less Secure)**
```bash
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
```

**Option 3: Environment Variable (Production)**
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit private keys to git
- Use different keys for dev/staging/production

### File Permissions

```bash
# Private key should be readable only by owner
chmod 600 ~/.ssh/github-apps/tracertm-private-key.pem

# Directory should be readable/executable by owner
chmod 700 ~/.ssh/github-apps
```

---

## 🧪 Testing

### Test GitHub App Installation

1. Visit your app's GitHub integration page
2. Click "Install GitHub App"
3. Select repositories
4. Authorize installation
5. Should redirect to `/projects?setup=github`
6. Verify installation appears in your app

### Test Webhook Events

1. Make a change in a connected repository (push, PR, issue)
2. Check webhook logs in your backend
3. Verify events are received at `/api/webhooks/github`

### Test OAuth Authentication

1. Visit `/auth/login`
2. Click "Sign in with GitHub"
3. Authorize on GitHub
4. Should redirect back to your app
5. Verify user is authenticated

---

## 📚 Related Documentation

- `GITHUB_APP_REPOSITORY_ACCESS_FORM.md` - Complete form fill-out
- `GITHUB_APP_INSTALLATION_CALLBACK.md` - Installation callback details
- `WORKOS_CALLBACK_URLS.md` - WorkOS redirect URLs

---

## 🚨 Important Notes

1. **Client Secret:** You need to get this from GitHub App settings (not provided)
2. **Private Key:** Move to secure location, never commit to git
3. **Webhook Secret:** Keep secure, used to verify webhook signatures
4. **Two Uses:** Same Client ID/Secret used for:
   - WorkOS OAuth authentication
   - GitHub App installation OAuth

---

**Status:** ✅ Credentials received - Complete setup steps above
