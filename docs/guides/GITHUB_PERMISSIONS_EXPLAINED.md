# GitHub Permissions: WorkOS AuthKit vs GitHub App

**Question:** Can you derive GitHub App permissions from WorkOS AuthKit, or do you need separate configuration?

**Answer:** **They are separate and serve different purposes.**

---

## Two Separate Systems

### 1. WorkOS AuthKit GitHub Connection
**Purpose:** User authentication only  
**What it requests:** OAuth scopes for user identity

**Typical OAuth Scopes:**
- `read:user` - Read user profile
- `user:email` - Read user email
- `read:org` (optional) - Read organization membership

**Configured in:** WorkOS Dashboard → Authentication → Connections → GitHub

**What it does:**
- Authenticates users via GitHub OAuth
- Gets user identity (name, email, avatar)
- Handles login/signup flows
- **Does NOT** provide repository access
- **Does NOT** provide GitHub API access beyond user profile

---

### 2. GitHub App
**Purpose:** Repository access, webhooks, GitHub API  
**What it requests:** App permissions for repositories and resources

**Required Permissions:**
- **Repository Permissions:**
  - `Contents: Read-only` - Access repository files
  - `Metadata: Read-only` - Basic repo info
  - `Pull requests: Read-only` - PR information
  - `Issues: Read-only` - Issue tracking
  - (etc. based on your needs)

- **Account Permissions:**
  - `Email addresses: Read-only` - User emails
  - `Profile: Read-only` - User profile

**Configured in:** GitHub App Settings → Permissions

**What it does:**
- Provides repository access via GitHub App installation
- Enables webhook events
- Allows GitHub API calls with installation tokens
- Provides access to repositories the app is installed on

---

## Why Both Are Needed

Looking at your codebase, you have:

1. **WorkOS AuthKit** (`AppProviders.tsx`)
   - Handles user authentication
   - Users sign in with GitHub
   - Gets user identity

2. **GitHub App Installation** (`GitHubAppInstall.tsx`)
   - Users install GitHub App on repositories
   - Provides repository access
   - Enables webhooks
   - Allows API calls to GitHub

**These are complementary, not overlapping:**

```
User Flow:
1. User signs in via WorkOS AuthKit → Gets authenticated
2. User installs GitHub App → Gets repository access
3. App can now:
   - Access user's GitHub identity (from WorkOS)
   - Access repositories (from GitHub App installation)
   - Receive webhooks (from GitHub App)
```

---

## Can You Derive Permissions?

### ❌ No - They Cannot Be Fully Derived

**WorkOS AuthKit scopes ≠ GitHub App permissions**

**Reasons:**

1. **Different Systems**
   - WorkOS AuthKit uses OAuth scopes
   - GitHub App uses App permissions
   - These are separate GitHub permission models

2. **Different Purposes**
   - WorkOS: Authentication only
   - GitHub App: Repository/API access

3. **Different Configuration Locations**
   - WorkOS: Configured in WorkOS Dashboard
   - GitHub App: Configured in GitHub App Settings

4. **Different Access Tokens**
   - WorkOS: OAuth access token (user-scoped)
   - GitHub App: Installation access token (repo-scoped)

---

## What WorkOS AuthKit Requests

When you configure GitHub in WorkOS AuthKit, it typically requests:

**OAuth Scopes (for authentication):**
- `read:user` - User profile
- `user:email` - User email
- `read:org` (optional) - Organization membership

**These are NOT the same as GitHub App permissions.**

---

## What You Need to Configure

### In WorkOS Dashboard:
1. **Authentication → Connections → GitHub**
   - Client ID (from GitHub App)
   - Client Secret (from GitHub App)
   - Redirect URI: `https://significant-vessel-93-staging.authkit.app/callback/github`
   - **Scopes:** WorkOS may allow you to configure additional scopes, but these are for OAuth, not App permissions

### In GitHub App Settings:
1. **Permissions** (Repository, Organization, Account)
   - Based on what your app needs to do
   - See `GITHUB_APP_REGISTRATION.md` for details

2. **Webhook Events**
   - Based on what events you need to receive

3. **Installation Target**
   - Where the app can be installed

---

## Recommended Approach

### Step 1: Configure GitHub App First
1. Register GitHub App with required permissions
2. Get Client ID, Client Secret, Private Key
3. Configure webhook secret

### Step 2: Configure WorkOS AuthKit
1. Use GitHub App's Client ID and Client Secret
2. Set redirect URI to WorkOS callback URL
3. WorkOS will request OAuth scopes automatically

### Step 3: Use Both in Your App
1. **Authentication:** WorkOS AuthKit handles login
2. **Repository Access:** GitHub App installation provides access
3. **Webhooks:** GitHub App receives events

---

## Summary

| Aspect | WorkOS AuthKit | GitHub App |
|--------|----------------|------------|
| **Purpose** | User authentication | Repository/API access |
| **Permission Type** | OAuth scopes | App permissions |
| **Configured In** | WorkOS Dashboard | GitHub App Settings |
| **Provides** | User identity | Repository access, webhooks |
| **Can Derive From** | ❌ No | ❌ No |

**Answer:** You need to configure both separately. WorkOS AuthKit handles authentication scopes, but GitHub App permissions must be configured independently based on what your app needs to do with repositories and GitHub API.

---

## Next Steps

1. ✅ Configure GitHub App with required permissions (see `GITHUB_APP_REGISTRATION.md`)
2. ✅ Configure WorkOS AuthKit with GitHub App credentials
3. ✅ Use WorkOS for authentication
4. ✅ Use GitHub App for repository access and webhooks

Both systems work together but are configured separately.
