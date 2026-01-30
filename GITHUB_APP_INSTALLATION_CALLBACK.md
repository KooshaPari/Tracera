# GitHub App Installation Callback - Repository Access

**Important:** This is DIFFERENT from OAuth authentication callback!

---

## 🔄 Two Separate Callbacks

### 1. OAuth Callback (Authentication) ✅ Already Configured
**Purpose:** User signs in with GitHub  
**Callback URL:** `https://significant-vessel-93-staging.authkit.app/callback/github`  
**Handled by:** WorkOS AuthKit  
**Result:** User is authenticated

### 2. GitHub App Installation Callback (Repository Access) ⚠️ Needs Your Backend
**Purpose:** User installs GitHub App on repositories for API access  
**Setup URL:** `https://trace.kooshapari.com/projects?setup=github`  
**Handled by:** YOUR backend API  
**Result:** GitHub App installation linked to user account for repository access

---

## ❌ Problem: Installation Callback Cannot Use WorkOS

**The GitHub App installation callback MUST go to YOUR backend, NOT WorkOS.**

**Why:**
- WorkOS handles authentication only
- WorkOS does NOT handle GitHub App installations
- Your backend needs to:
  - Receive installation callback from GitHub
  - Link installation to user account
  - Store installation tokens
  - Enable repository API access

---

## ✅ Correct Configuration

### GitHub App Settings

**Callback URL (OAuth - Authentication):**
```
https://significant-vessel-93-staging.authkit.app/callback/github
```
✅ This is correct - WorkOS handles OAuth

**Setup URL (Installation - Repository Access):**
```
https://trace.kooshapari.com/api/webhooks/github/install
```
⚠️ **This should be YOUR backend endpoint, NOT WorkOS**

---

## 🔧 What Your Backend Needs

### Installation Callback Endpoint

Your backend needs an endpoint to handle GitHub App installation:

**Endpoint:** `POST /api/webhooks/github/install` (or similar)

**What it does:**
1. Receives installation callback from GitHub
2. Verifies webhook signature
3. Extracts installation ID and user account
4. Links installation to authenticated user account
5. Stores installation tokens for API access
6. Redirects user back to frontend

**Example Flow:**
```
User clicks "Install GitHub App"
  ↓
Redirects to GitHub App installation page
  ↓
User selects repositories & authorizes
  ↓
GitHub redirects to: https://trace.kooshapari.com/api/webhooks/github/install
  ↓
Your Backend:
  - Receives installation_id
  - Links to user account (from session/auth token)
  - Stores installation for API access
  ↓
Backend redirects to: https://trace.kooshapari.com/projects?setup=github
  ↓
Frontend shows success, user can now access repositories ✅
```

---

## 📝 GitHub App Registration Form

### Setup URL (Post Installation)

**Current (Wrong):**
```
https://trace.kooshapari.com/projects?setup=github
```

**Should Be (Backend Endpoint):**
```
https://trace.kooshapari.com/api/webhooks/github/install
```

**Or (If Frontend Handles Redirect):**
```
https://trace.kooshapari.com/api/webhooks/github/install?redirect=/projects?setup=github
```

---

## 🔐 Backend Implementation Needed

### 1. Installation Callback Handler

```python
# backend/api/webhooks/github/install.py

@app.post("/api/webhooks/github/install")
async def handle_github_app_installation(
    request: Request,
    installation_id: str = Query(...),
    setup_action: str = Query(...),
    # ... other GitHub callback params
):
    # Verify webhook signature
    # Get authenticated user from session/token
    # Link installation to user account
    # Store installation tokens
    # Redirect to frontend
    pass
```

### 2. Link Installation to User

```python
# Store installation
installation = GitHubInstallation(
    installation_id=installation_id,
    user_id=current_user.id,
    account_id=account_id,
    # ... other fields
)
db.session.add(installation)
db.session.commit()
```

### 3. Use Installation for API Calls

```python
# Get installation token
installation = get_user_installation(user_id)
token = get_installation_token(installation.installation_id)

# Use token for GitHub API calls
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.github.com/user/repos", headers=headers)
```

---

## ✅ Correct Flow

### Authentication (OAuth)
```
User → WorkOS → GitHub → WorkOS Callback → Your App
✅ Handled by WorkOS
```

### Installation (Repository Access)
```
User → GitHub Installation → YOUR Backend Callback → Link to User → Frontend
✅ Handled by YOUR backend
```

---

## 🎯 Summary

**For Repository Access (GitHub App Installation):**

1. ❌ **Cannot use WorkOS callback** - WorkOS doesn't handle installations
2. ✅ **Must use YOUR backend endpoint** - You need to link installation to user
3. ✅ **Backend receives installation callback** - From GitHub
4. ✅ **Backend links to user account** - Based on authenticated session
5. ✅ **Backend stores installation tokens** - For GitHub API access
6. ✅ **Frontend uses installation** - Via your backend API

**The Setup URL in GitHub App registration should point to YOUR backend, not WorkOS.**

---

## 📋 Action Items

1. ✅ OAuth Callback: `https://significant-vessel-93-staging.authkit.app/callback/github` (WorkOS)
2. ⚠️ Installation Setup URL: `https://trace.kooshapari.com/api/webhooks/github/install` (YOUR backend)
3. ⚠️ Create backend endpoint to handle installation callbacks
4. ⚠️ Link installations to authenticated user accounts
5. ⚠️ Store installation tokens for GitHub API access

---

**Bottom Line:** OAuth callback goes to WorkOS ✅, but Installation callback MUST go to YOUR backend ⚠️
