# GitHub App Registration Guide for TraceRTM

**Date:** 2026-01-28  
**Integration:** WorkOS AuthKit + GitHub OAuth  
**Database:** PostgreSQL (postgres:5432/agent_api)

---

## 📋 GitHub App Registration Form

### Basic Information

**GitHub App name:**
```
TraceRTM
```

**Description:**
```markdown
TraceRTM is a traceability management platform that helps teams track requirements, features, and their relationships across software projects. This GitHub App enables seamless authentication and integration with GitHub repositories for enhanced traceability workflows.
```

**Homepage URL:**
```
https://trace.kooshapari.com
```

---

### Identifying and Authorizing Users

**Callback URL:**
```
https://significant-vessel-93-staging.authkit.app/callback/github
```

**Note:** This is your WorkOS AuthKit callback URL. WorkOS handles the OAuth flow, so GitHub redirects to WorkOS, which then redirects to your app.

**Expire user authorization tokens:**
- ✅ **Checked** (Enable this)
  - Provides refresh_token for token renewal
  - Better security and user experience

**Request user authorization (OAuth) during installation:**
- ✅ **Checked** (Enable this)
  - Required for user identification
  - Allows access to user's GitHub identity

**Enable Device Flow:**
- ⬜ **Unchecked** (Optional)
  - Only enable if you need device-based authentication
  - Not typically needed for web apps

---

### Post Installation

**Setup URL (optional):**
```
https://trace.kooshapari.com/projects?setup=github
```

**Redirect on update:**
- ✅ **Checked** (Enable this)
  - Redirects users after installation updates
  - Helps complete setup when repositories are added/removed

---

### Webhook Configuration

**Active:**
- ✅ **Checked** (Enable webhooks)

**Webhook URL:**
```
https://trace.kooshapari.com/api/webhooks/github
```

**Secret:**
```
[Generate a secure random string - store in environment variable]
```

**Example secret generation:**
```bash
openssl rand -hex 32
# Store as: GITHUB_WEBHOOK_SECRET=your_generated_secret
```

---

### Permissions

#### Repository Permissions

**Contents:**
- **Read-only** ✅
  - Access repository contents
  - Needed for reading files, commits, etc.

**Metadata:**
- **Read-only** ✅
  - Access basic repository information
  - Always required

**Pull requests:**
- **Read-only** ✅ (if you need PR info)
- **Read & write** ⬜ (if you need to create/update PRs)

**Issues:**
- **Read-only** ✅ (if you need issue tracking)
- **Read & write** ⬜ (if you need to create/update issues)

**Commit statuses:**
- **Read-only** ✅ (if you need CI/CD status)
- **Read & write** ⬜ (if you need to update statuses)

**Repository hooks:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

**Repository projects:**
- **Read-only** ⬜ (if you need project boards)
- **Read & write** ⬜

**Repository administration:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

**Single file:**
- **Read-only** ⬜ (if you need specific file access)
- **Read & write** ⬜

**Checks:**
- **Read-only** ⬜
- **Read & write** ⬜ (if you need to create check runs)

**Code scanning alerts:**
- **Read-only** ⬜ (if you need security scanning data)

**Dependabot alerts:**
- **Read-only** ⬜ (if you need dependency alerts)

**Secret scanning alerts:**
- **Read-only** ⬜ (if you need secret scanning data)

**Vulnerability alerts:**
- **Read-only** ⬜ (if you need vulnerability data)

#### Organization Permissions

**Members:**
- **Read-only** ⬜ (if you need org member info)

**Organization administration:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

**Organization projects:**
- **Read-only** ⬜
- **Read & write** ⬜

**Organization secrets:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

**Organization user blocking:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

**Plan:**
- **Read-only** ⬜ (if you need org plan info)

#### Account Permissions

**Email addresses:**
- **Read-only** ✅
  - Access user's email addresses
  - Needed for user identification

**Profile:**
- **Read-only** ✅
  - Access user's profile information
  - Needed for user display

**Follow:**
- **Read-only** ⬜
- **Read & write** ⬜ (usually not needed)

---

### Subscribe to Events

Based on the permissions selected, subscribe to these events:

**Repository Events:**
- ✅ **Push** - Code changes
- ✅ **Pull request** - PR opened/closed/merged
- ✅ **Issues** - Issue opened/closed (if using issues)
- ✅ **Create** - Branch/tag creation
- ✅ **Delete** - Branch/tag deletion
- ✅ **Release** - Releases published

**Installation Events:**
- ✅ **Installation** - App installed
- ✅ **Installation repositories** - Repositories added/removed

**Meta Events:**
- ✅ **Meta** - App deleted/hook removed

**Optional Events (if needed):**
- ⬜ **Commit comment** - Comments on commits
- ⬜ **Issue comment** - Comments on issues
- ⬜ **Pull request review** - PR reviews
- ⬜ **Status** - Commit status updates
- ⬜ **Check run** - Check run updates

---

### Installation Target

**Where can this GitHub App be installed?**

- ⬜ **Only on this account** (@KooshaPari)
- ✅ **Any account** (Recommended)
  - Allows installation by any user or organization
  - Better for broader adoption

---

## 🔐 Environment Variables Needed

Add these to your `.env` file:

```bash
# WorkOS (Already configured)
WORKOS_CLIENT_ID=client_01K4KYZR40RK7R9X3PPB5SEJ66
WORKOS_API_KEY=sk_test_a2V5XzAxSzRLWVpRSkFNUURWS0tWR0JZQVFGUkZWLGNsYmZHcTZmTVc0bFlicHA3bXNjMEpIVTE
AUTHKIT_URL=significant-vessel-93-staging.authkit.app

# GitHub App (Add these after registration)
GITHUB_APP_ID=your_app_id_here
GITHUB_APP_CLIENT_ID=your_client_id_here
GITHUB_APP_CLIENT_SECRET=your_client_secret_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
# OR
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

# Database (Already configured)
DATABASE_URL=postgresql://user:password@postgres:5432/agent_api
```

---

## 📝 After Registration

### 1. Get Your Credentials

After submitting the form, GitHub will provide:
- **App ID** - Unique identifier
- **Client ID** - OAuth client ID
- **Client Secret** - OAuth client secret
- **Private Key** - Download the `.pem` file
- **Webhook Secret** - The secret you generated

### 2. Configure WorkOS AuthKit

In your WorkOS dashboard:
1. Go to **Authentication** → **Connections**
2. Add **GitHub** connection
3. Enter:
   - **Client ID:** From GitHub App registration
   - **Client Secret:** From GitHub App registration
   - **Redirect URI:** `https://significant-vessel-93-staging.authkit.app/callback/github`

### 3. Update Your Application

Update your code to:
- Remove Google SSO (as requested)
- Ensure GitHub OAuth flows through WorkOS
- Handle webhook events at `/api/webhooks/github`

### 4. Test the Integration

1. Install the GitHub App on a test repository
2. Try logging in with GitHub
3. Verify webhook events are received
4. Test repository access

---

## 🚫 Removing Google SSO

Since you only want GitHub authentication:

1. **Remove Google OAuth button** from login page
2. **Update WorkOS AuthKit** to only enable GitHub connection
3. **Remove Google-related code** from authentication flows

---

## ✅ Checklist

- [ ] Fill out GitHub App registration form
- [ ] Download private key (.pem file)
- [ ] Save all credentials securely
- [ ] Configure WorkOS AuthKit with GitHub credentials
- [ ] Set up webhook endpoint at `/api/webhooks/github`
- [ ] Add environment variables to `.env`
- [ ] Remove Google SSO from codebase
- [ ] Test GitHub OAuth flow
- [ ] Test webhook events
- [ ] Update documentation

---

## 🔗 Useful Links

- [GitHub App Documentation](https://docs.github.com/en/apps)
- [WorkOS AuthKit GitHub Integration](https://workos.com/docs/authkit/connections/github)
- [GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)

---

**Note:** The callback URL points to WorkOS AuthKit, which handles the OAuth flow and redirects to your application. This is the standard pattern for WorkOS integrations.
