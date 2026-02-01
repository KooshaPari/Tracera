# GitHub App Credentials - Quick Start

**App ID:** 2750779  
**Client ID:** Iv23liGR8KgbxkmtriYr

---

## ⚡ Quick Setup

### 1. Move Private Key (Secure Location)

```bash
# Create secure directory
mkdir -p ~/.ssh/github-apps
chmod 700 ~/.ssh/github-apps

# Move private key
mv /Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem ~/.ssh/github-apps/tracertm-private-key.pem

# Set secure permissions
chmod 600 ~/.ssh/github-apps/tracertm-private-key.pem
```

### 2. Get Client Secret

1. Go to: https://github.com/settings/apps
2. Find **TraceRTM** app
3. **General** → **Client secrets** → **Generate a new client secret**
4. Copy the secret (shown only once!)

### 3. Add to Backend `.env`

```bash
# GitHub App
GITHUB_APP_ID=2750779
GITHUB_APP_CLIENT_ID=Iv23liGR8KgbxkmtriYr
GITHUB_APP_CLIENT_SECRET=your_client_secret_here
GITHUB_WEBHOOK_SECRET=e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910
GITHUB_PRIVATE_KEY_PATH=/Users/kooshapari/.ssh/github-apps/tracertm-private-key.pem
```

### 4. Configure WorkOS

**WorkOS Dashboard** → **Authentication** → **Connections** → **GitHub**:
- **Client ID:** `Iv23liGR8KgbxkmtriYr`
- **Client Secret:** [From GitHub App settings]
- **Redirect URI:** `https://significant-vessel-93-staging.authkit.app/callback/github`

---

## ✅ Done!

After completing these steps:
1. Restart backend server
2. Test GitHub App installation
3. Test OAuth authentication

---

See `GITHUB_APP_CREDENTIALS_SETUP.md` for detailed instructions.
