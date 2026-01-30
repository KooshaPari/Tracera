# GitHub App Registration Form - Repository Access & API Usage

**Purpose:** GitHub App for repository access, API calls, and webhooks  
**NOT for authentication** (authentication handled by WorkOS AuthKit)

---

## 📋 Form Fields - Complete Fill-Out

### Basic Information

**GitHub App name:**
```
TraceRTM
```

**Description (Markdown):**
```markdown
TraceRTM is a traceability management platform that helps teams track requirements, features, and their relationships across software projects. This GitHub App enables repository access, code integration, webhook events, and GitHub API integration for enhanced traceability workflows.
```

**Homepage URL:**
```
https://trace.kooshapari.com
```

---

### Identifying and Authorizing Users

**Callback URL:**
```
https://trace.kooshapari.com/api/webhooks/github/install
```

**Important:** This is YOUR backend endpoint that handles GitHub App installation callbacks. This is NOT for OAuth authentication (that's handled by WorkOS).

**Expire user authorization tokens:**
- ✅ **Checked** (Enable this)
  - Provides `refresh_token` for token renewal
  - Better security and user experience
  - Allows long-lived sessions for API access

**Request user authorization (OAuth) during installation:**
- ✅ **Checked** (Enable this)
  - Required to identify which user installed the app
  - Allows linking installation to user account
  - Needed for account-based repository access

**Enable Device Flow:**
- ⬜ **Unchecked** (Not needed)
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
  - Better user experience

---

### Webhook

**Active:**
- ✅ **Checked** (Enable webhooks)

**Webhook URL:**
```
https://trace.kooshapari.com/api/webhooks/github
```

**Secret:**
```
[Generate a secure random string - see instructions below]
```

**Generate Webhook Secret:**
```bash
# Generate a secure random secret
openssl rand -hex 32

# Example output (use this):
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# Store this in your environment variables as:
# GITHUB_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

---

### Permissions

#### Account Permissions

**Email addresses:**
- ✅ **Read-only**
  - Access user's email addresses
  - Needed to identify user who installed the app
  - Required for linking installation to user account

**Profile:**
- ✅ **Read-only**
  - Access user's profile information
  - Needed for user display and identification

**Follow:**
- ⬜ **No access** (Not needed)

---

#### Repository Permissions

**Contents:**
- ✅ **Read-only**
  - Access repository contents
  - Needed for reading files, commits, code
  - Required for traceability features

**Metadata:**
- ✅ **Read-only**
  - Access basic repository information
  - Always required
  - Needed for repository listing

**Pull requests:**
- ✅ **Read-only**
  - Access pull request information
  - Needed for PR tracking and traceability
  - Required for traceability workflows

**Issues:**
- ✅ **Read-only**
  - Access issue information
  - Needed for issue tracking
  - Required for traceability features

**Commit statuses:**
- ⬜ **No access** (Optional - enable if you need CI/CD status)

**Repository hooks:**
- ⬜ **No access** (Not needed)

**Repository projects:**
- ⬜ **No access** (Optional - enable if you need project boards)

**Repository administration:**
- ⬜ **No access** (Not needed - security best practice)

**Single file:**
- ⬜ **No access** (Not needed)

**Checks:**
- ⬜ **No access** (Optional - enable if you need check runs)

**Code scanning alerts:**
- ⬜ **No access** (Optional - enable if you need security scanning)

**Dependabot alerts:**
- ⬜ **No access** (Optional - enable if you need dependency alerts)

**Secret scanning alerts:**
- ⬜ **No access** (Optional - enable if you need secret scanning)

**Vulnerability alerts:**
- ⬜ **No access** (Optional - enable if you need vulnerability data)

---

#### Organization Permissions

**Members:**
- ⬜ **No access** (Optional - enable if you need org member info)

**Organization administration:**
- ⬜ **No access** (Not needed - security best practice)

**Organization projects:**
- ⬜ **No access** (Optional - enable if you need org projects)

**Organization secrets:**
- ⬜ **No access** (Not needed - security best practice)

**Organization user blocking:**
- ⬜ **No access** (Not needed)

**Plan:**
- ⬜ **No access** (Optional - enable if you need org plan info)

---

### Subscribe to Events

Based on the permissions selected, subscribe to these events:

**Repository Events:**
- ✅ **Push** - Code changes (needed for traceability)
- ✅ **Pull request** - PR opened/closed/merged (needed for PR tracking)
- ✅ **Issues** - Issue opened/closed (needed for issue tracking)
- ✅ **Create** - Branch/tag creation (optional but useful)
- ✅ **Delete** - Branch/tag deletion (optional but useful)
- ✅ **Release** - Releases published (optional but useful)

**Installation Events:**
- ✅ **Installation** - App installed (required)
- ✅ **Installation repositories** - Repositories added/removed (required)

**Meta Events:**
- ✅ **Meta** - App deleted/hook removed (required)

**Optional Events (if needed later):**
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
  - Required for multi-user scenarios

---

## ✅ Summary Checklist

### Basic Info
- [x] App name: `TraceRTM`
- [x] Description: Traceability platform with GitHub integration
- [x] Homepage: `https://trace.kooshapari.com`

### OAuth & Installation
- [x] Callback URL: `https://trace.kooshapari.com/api/webhooks/github/install` (YOUR backend)
- [x] Expire tokens: ✅ Enabled
- [x] Request OAuth: ✅ Enabled
- [x] Device Flow: ⬜ Disabled

### Post Installation
- [x] Setup URL: `https://trace.kooshapari.com/projects?setup=github`
- [x] Redirect on update: ✅ Enabled

### Webhook
- [x] Active: ✅ Enabled
- [x] Webhook URL: `https://trace.kooshapari.com/api/webhooks/github`
- [x] Secret: [Generate with `openssl rand -hex 32`]

### Permissions
- [x] Account: Email (read), Profile (read)
- [x] Repository: Contents (read), Metadata (read), Pull requests (read), Issues (read)
- [x] Organization: None (unless needed)

### Events
- [x] Push, Pull request, Issues, Create, Delete, Release
- [x] Installation, Installation repositories
- [x] Meta

### Installation
- [x] Any account: ✅ Enabled

---

## 🔐 After Registration

### 1. Save Credentials

After submitting, GitHub will provide:
- **App ID** - Unique identifier
- **Client ID** - OAuth client ID (for installation OAuth)
- **Client Secret** - OAuth client secret (for installation OAuth)
- **Private Key** - Download the `.pem` file
- **Webhook Secret** - The secret you generated

### 2. Add Environment Variables

Add to your backend `.env`:

```bash
# GitHub App (Repository Access)
GITHUB_APP_ID=your_app_id_here
GITHUB_APP_CLIENT_ID=your_client_id_here
GITHUB_APP_CLIENT_SECRET=your_client_secret_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
# OR
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
```

### 3. Backend Endpoints Needed

Your backend should have:

**Installation Callback Handler:**
```
POST /api/webhooks/github/install
```
- Receives installation callback from GitHub
- Links installation to authenticated user
- Redirects to frontend

**Webhook Handler:**
```
POST /api/webhooks/github
```
- Receives webhook events from GitHub
- Processes events (push, PR, issues, etc.)
- Updates traceability data

---

## 🎯 Key Differences from OAuth App

| Aspect | OAuth App (WorkOS) | GitHub App (This Form) |
|--------|-------------------|------------------------|
| **Purpose** | User authentication | Repository access & API |
| **Callback URL** | WorkOS AuthKit | Your backend |
| **Handled By** | WorkOS | Your backend |
| **Provides** | User identity | Repository access, webhooks |
| **Used For** | Login/signup | Code integration, API calls |

---

## 📝 Notes

1. **Callback URL:** Points to YOUR backend (`/api/webhooks/github/install`), NOT WorkOS
2. **Setup URL:** Points to YOUR frontend (`/projects?setup=github`)
3. **Webhook URL:** Points to YOUR backend (`/api/webhooks/github`)
4. **Permissions:** Read-only for security (add write only if needed)
5. **Events:** Subscribe to events you actually need

---

**Status:** ✅ Ready to submit! Fill out the form with the values above.

This GitHub App is for repository access and API usage, separate from WorkOS authentication.
