# GitHub App Credentials - Summary

**Date:** 2026-01-28  
**Status:** ✅ Credentials received, private key secured

---

## 🔐 Credentials

### Received:
- ✅ **App ID:** `2750779`
- ✅ **Client ID:** `Iv23liGR8KgbxkmtriYr`
- ✅ **Webhook Secret:** `e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910`
- ✅ **Private Key:** Secured at `/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem`

### Still Needed:
- ⚠️ **Client Secret:** Get from GitHub App settings

---

## ✅ Completed

1. ✅ Private key moved to secure location
2. ✅ Permissions set (600 - owner read/write only)
3. ✅ Credentials documented

---

## 📋 Next Steps

### 1. Get Client Secret

1. Visit: https://github.com/settings/apps
2. Find **TraceRTM** app (App ID: 2750779)
3. Go to **General** → **Client secrets**
4. Click **Generate a new client secret**
5. Copy immediately (shown only once!)

### 2. Add to Backend Environment Variables

Add these to your backend `.env` file:

```bash
# GitHub App (Repository Access & API)
GITHUB_APP_ID=2750779
GITHUB_APP_CLIENT_ID=Iv23liGR8KgbxkmtriYr
GITHUB_APP_CLIENT_SECRET=your_client_secret_here
GITHUB_WEBHOOK_SECRET=e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910
GITHUB_PRIVATE_KEY_PATH=/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem
```

### 3. Configure WorkOS

**WorkOS Dashboard** → **Authentication** → **Connections** → **GitHub**:

- **Client ID:** `Iv23liGR8KgbxkmtriYr`
- **Client Secret:** [From GitHub App settings - same as backend]
- **Redirect URI:** `https://significant-vessel-93-staging.authkit.app/callback/github`

---

## 🔒 Security Notes

- ✅ Private key secured at: `/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem`
- ✅ Permissions: `600` (owner read/write only)
- ⚠️ **Never commit private key to git**
- ⚠️ **Never commit Client Secret to git**
- ⚠️ **Use environment variables or secrets management**

---

## 📚 Documentation

- `GITHUB_APP_CREDENTIALS_SETUP.md` - Complete setup guide
- `GITHUB_APP_QUICK_START.md` - Quick reference
- `GITHUB_APP_REPOSITORY_ACCESS_FORM.md` - Form fill-out guide

---

**Status:** ✅ Ready - Get Client Secret and add to backend `.env`
