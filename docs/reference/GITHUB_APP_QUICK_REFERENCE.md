# GitHub App Registration - Quick Reference

## 📋 Form Fields (Copy-Paste Ready)

### Basic Information

**GitHub App name:**
```
TraceRTM
```

**Description:**
```
TraceRTM is a traceability management platform that helps teams track requirements, features, and their relationships across software projects. This GitHub App enables seamless authentication and integration with GitHub repositories for enhanced traceability workflows.
```

**Homepage URL:**
```
https://trace.kooshapari.com
```

### Callback URL
```
https://significant-vessel-93-staging.authkit.app/callback/github
```

### Setup URL (optional)
```
https://trace.kooshapari.com/projects?setup=github
```

### Webhook URL
```
https://trace.kooshapari.com/api/webhooks/github
```

### Webhook Secret
Generate with:
```bash
openssl rand -hex 32
```

---

## ✅ Checkboxes to Enable

- ✅ Expire user authorization tokens
- ✅ Request user authorization (OAuth) during installation
- ✅ Redirect on update
- ✅ Active (Webhooks)

---

## 🔐 Minimum Required Permissions

### Repository Permissions
- **Contents:** Read-only ✅
- **Metadata:** Read-only ✅

### Account Permissions
- **Email addresses:** Read-only ✅
- **Profile:** Read-only ✅

---

## 📡 Subscribe to Events

- ✅ Push
- ✅ Pull request
- ✅ Installation
- ✅ Installation repositories
- ✅ Meta

---

## 🎯 Installation Target

- ✅ **Any account**

---

## 🔄 After Registration

1. **Save credentials:**
   - App ID
   - Client ID
   - Client Secret
   - Private Key (.pem file)
   - Webhook Secret

2. **Configure WorkOS:**
   - Add GitHub connection
   - Use Client ID and Client Secret from GitHub
   - Set redirect URI: `https://significant-vessel-93-staging.authkit.app/callback/github`

3. **Add to .env:**
   ```bash
   GITHUB_APP_ID=your_app_id
   GITHUB_APP_CLIENT_ID=your_client_id
   GITHUB_APP_CLIENT_SECRET=your_client_secret
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
   ```

4. **Test:**
   - Install app on test repo
   - Try GitHub login
   - Verify webhooks work

---

**Full guide:** See `GITHUB_APP_REGISTRATION.md` for detailed instructions.
