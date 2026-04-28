# OAuth Integration

The Pheno SDK's OAuth Integration provides comprehensive OAuth flow management with automatic token refresh, multiple provider support, and seamless integration with the credentials broker system.

## Table of Contents

- [Overview](#overview)
- [Supported Providers](#supported-providers)
- [Quick Start](#quick-start)
- [OAuth Flows](#oauth-flows)
- [Token Management](#token-management)
- [Automatic Refresh](#automatic-refresh)
- [CLI Commands](#cli-commands)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The OAuth integration provides:

- **Multiple Provider Support**: GitHub, Google, Microsoft, OpenAI, and custom OAuth2
- **Automatic Token Refresh**: Background refresh scheduling
- **Flow Management**: Complete OAuth2 authorization code flow
- **Credential Integration**: Seamless integration with the credentials broker
- **CLI Interface**: Command-line OAuth management
- **Security**: Secure token storage and management

## Supported Providers

### Built-in Providers

- **GitHub**: Repository and user access
- **Google**: Google Cloud Platform and Google APIs
- **Microsoft**: Microsoft Graph and Azure services
- **OpenAI**: OpenAI API access
- **Custom OAuth2**: Any OAuth2-compliant provider

### Provider Configuration

Each provider requires specific configuration:

```python
# GitHub
{
    "client_id": "your-github-client-id",
    "client_secret": "your-github-client-secret",
    "scopes": ["repo", "user", "admin:org"],
    "authorization_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "user_info_url": "https://api.github.com/user"
}

# Google
{
    "client_id": "your-google-client-id",
    "client_secret": "your-google-client-secret",
    "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
    "authorization_url": "https://accounts.google.com/o/oauth2/auth",
    "token_url": "https://oauth2.googleapis.com/token",
    "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo"
}

# Microsoft
{
    "client_id": "your-microsoft-client-id",
    "client_secret": "your-microsoft-client-secret",
    "scopes": ["https://graph.microsoft.com/.default"],
    "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    "user_info_url": "https://graph.microsoft.com/v1.0/me"
}

# OpenAI
{
    "client_id": "your-openai-client-id",
    "client_secret": "your-openai-client-secret",
    "scopes": ["openai"],
    "authorization_url": "https://auth0.openai.com/authorize",
    "token_url": "https://auth0.openai.com/oauth/token",
    "user_info_url": "https://api.openai.com/v1/user"
}
```

## Quick Start

### Basic Setup

```python
from pheno.credentials.oauth import OAuthFlowManager

# Initialize OAuth manager
oauth_manager = OAuthFlowManager()

# Add GitHub provider
oauth_manager.add_provider(
    "github",
    client_id="your-client-id",
    client_secret="your-client-secret",
    scopes=["repo", "user"]
)

# Start OAuth flow
flow = oauth_manager.start_flow("github")
print(f"Visit: {flow.authorization_url}")

# Complete flow with authorization code
token = oauth_manager.complete_flow(flow, authorization_code="code")
print(f"Access token: {token.access_token}")
```

### Integration with Credentials Broker

```python
from pheno.credentials import CredentialBroker
from pheno.credentials.oauth import OAuthFlowManager

# Initialize both systems
broker = CredentialBroker()
oauth_manager = OAuthFlowManager()

# Configure OAuth
oauth_manager.add_provider("github", client_id="...", client_secret="...")

# Start flow
flow = oauth_manager.start_flow("github")
print(f"Visit: {flow.authorization_url}")

# Complete flow
token = oauth_manager.complete_flow(flow, authorization_code="code")

# Store token in credentials broker
broker.store_credential(
    "GITHUB_TOKEN",
    token.access_token,
    credential_type="oauth_token",
    metadata={
        "provider": "github",
        "expires_at": token.expires_at.isoformat(),
        "refresh_token": token.refresh_token,
        "scopes": token.scopes
    }
)
```

## OAuth Flows

### Authorization Code Flow

The standard OAuth2 authorization code flow:

```python
# 1. Start flow
flow = oauth_manager.start_flow("github")
print(f"Visit: {flow.authorization_url}")

# 2. User authorizes and gets code
authorization_code = "user-provided-code"

# 3. Complete flow
token = oauth_manager.complete_flow(flow, authorization_code)
```

### Implicit Flow

For single-page applications:

```python
# Start implicit flow
flow = oauth_manager.start_flow("github", response_type="token")
print(f"Visit: {flow.authorization_url}")

# Token is returned directly in the callback URL
```

### Client Credentials Flow

For server-to-server authentication:

```python
# Start client credentials flow
token = oauth_manager.start_client_credentials_flow("github")
print(f"Access token: {token.access_token}")
```

## Token Management

### Token Storage

Tokens are stored securely in the credentials broker:

```python
# Store token with metadata
broker.store_credential(
    "GITHUB_TOKEN",
    token.access_token,
    credential_type="oauth_token",
    metadata={
        "provider": "github",
        "expires_at": token.expires_at.isoformat(),
        "refresh_token": token.refresh_token,
        "scopes": token.scopes,
        "token_type": token.token_type
    }
)
```

### Token Retrieval

```python
# Get token
token_data = broker.get_credential("GITHUB_TOKEN")
if token_data:
    access_token = token_data.value
    metadata = token_data.metadata
    expires_at = metadata.get("expires_at")
    refresh_token = metadata.get("refresh_token")
```

### Token Validation

```python
# Check if token is valid
is_valid = oauth_manager.validate_token("github", access_token)
if not is_valid:
    # Token is expired or invalid
    new_token = oauth_manager.refresh_token("github")
```

## Automatic Refresh

### Refresh Scheduling

Set up automatic token refresh:

```python
# Configure refresh for a provider
oauth_manager.configure_refresh(
    provider="github",
    refresh_token="refresh-token",
    expires_in=3600  # 1 hour
)

# Start refresh scheduler
oauth_manager.start_refresh_scheduler()

# Scheduler will automatically refresh tokens before they expire
```

### Manual Refresh

```python
# Manually refresh a token
new_token = oauth_manager.refresh_token("github")
print(f"New access token: {new_token.access_token}")
```

### Refresh Callbacks

Handle refresh events:

```python
def on_token_refreshed(provider: str, new_token: OAuthToken):
    print(f"Token refreshed for {provider}")
    # Update stored token
    broker.store_credential(
        f"{provider.upper()}_TOKEN",
        new_token.access_token,
        credential_type="oauth_token",
        metadata={
            "provider": provider,
            "expires_at": new_token.expires_at.isoformat(),
            "refresh_token": new_token.refresh_token
        }
    )

# Register callback
oauth_manager.on_token_refreshed = on_token_refreshed
```

## CLI Commands

### Provider Management

```bash
# List providers
pheno-cli oauth list-providers

# Configure provider
pheno-cli oauth configure github --client-id "..." --client-secret "..." --scopes "repo,user"

# Remove provider
pheno-cli oauth remove-provider github
```

### OAuth Flows

```bash
# Start OAuth flow
pheno-cli oauth start-flow github

# Complete OAuth flow
pheno-cli oauth complete-flow github --code "authorization-code"

# Start client credentials flow
pheno-cli oauth start-client-credentials github
```

### Token Management

```bash
# List OAuth tokens
pheno-cli oauth list-tokens

# Refresh token
pheno-cli oauth refresh github

# Validate token
pheno-cli oauth validate github

# Revoke token
pheno-cli oauth revoke github
```

### Refresh Management

```bash
# Start refresh scheduler
pheno-cli oauth start-scheduler

# Stop refresh scheduler
pheno-cli oauth stop-scheduler

# Configure refresh
pheno-cli oauth configure-refresh github --refresh-token "..." --expires-in 3600
```

## API Reference

### OAuthFlowManager

```python
class OAuthFlowManager:
    def __init__(self):
        """Initialize OAuth flow manager."""
    
    def add_provider(self, name: str, **config) -> bool:
        """Add OAuth provider."""
    
    def remove_provider(self, name: str) -> bool:
        """Remove OAuth provider."""
    
    def get_provider(self, name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider."""
    
    def list_providers(self) -> List[str]:
        """List all providers."""
    
    def start_flow(self, provider: str, **kwargs) -> OAuthFlow:
        """Start OAuth flow."""
    
    def complete_flow(self, flow: OAuthFlow, authorization_code: str) -> OAuthToken:
        """Complete OAuth flow."""
    
    def start_client_credentials_flow(self, provider: str) -> OAuthToken:
        """Start client credentials flow."""
    
    def refresh_token(self, provider: str) -> OAuthToken:
        """Refresh OAuth token."""
    
    def validate_token(self, provider: str, token: str) -> bool:
        """Validate OAuth token."""
    
    def revoke_token(self, provider: str, token: str) -> bool:
        """Revoke OAuth token."""
    
    def configure_refresh(self, provider: str, refresh_token: str, expires_in: int) -> bool:
        """Configure automatic refresh."""
    
    def start_refresh_scheduler(self) -> None:
        """Start refresh scheduler."""
    
    def stop_refresh_scheduler(self) -> None:
        """Stop refresh scheduler."""
```

### OAuthFlow

```python
class OAuthFlow:
    def __init__(self, provider: str, authorization_url: str, state: str):
        """Initialize OAuth flow."""
    
    @property
    def authorization_url(self) -> str:
        """Get authorization URL."""
    
    @property
    def state(self) -> str:
        """Get state parameter."""
    
    @property
    def provider(self) -> str:
        """Get provider name."""
```

### OAuthToken

```python
class OAuthToken:
    def __init__(self, access_token: str, token_type: str, expires_in: int, 
                 refresh_token: str = None, scopes: List[str] = None):
        """Initialize OAuth token."""
    
    @property
    def access_token(self) -> str:
        """Get access token."""
    
    @property
    def token_type(self) -> str:
        """Get token type."""
    
    @property
    def expires_at(self) -> datetime:
        """Get expiration time."""
    
    @property
    def refresh_token(self) -> Optional[str]:
        """Get refresh token."""
    
    @property
    def scopes(self) -> List[str]:
        """Get token scopes."""
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
    
    def expires_in_seconds(self) -> int:
        """Get seconds until expiration."""
```

### OAuthProvider

```python
class OAuthProvider:
    def __init__(self, name: str, **config):
        """Initialize OAuth provider."""
    
    @property
    def name(self) -> str:
        """Get provider name."""
    
    @property
    def client_id(self) -> str:
        """Get client ID."""
    
    @property
    def client_secret(self) -> str:
        """Get client secret."""
    
    @property
    def scopes(self) -> List[str]:
        """Get scopes."""
    
    def get_authorization_url(self, state: str, **kwargs) -> str:
        """Get authorization URL."""
    
    def exchange_code(self, authorization_code: str, **kwargs) -> OAuthToken:
        """Exchange authorization code for token."""
    
    def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token."""
    
    def validate_token(self, token: str) -> bool:
        """Validate access token."""
    
    def revoke_token(self, token: str) -> bool:
        """Revoke access token."""
```

## Configuration

### Environment Variables

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret

# OpenAI OAuth
OPENAI_CLIENT_ID=your-client-id
OPENAI_CLIENT_SECRET=your-client-secret
```

### Configuration File

Create `~/.pheno/oauth.yaml`:

```yaml
providers:
  github:
    client_id: "your-github-client-id"
    client_secret: "your-github-client-secret"
    scopes: ["repo", "user", "admin:org"]
  google:
    client_id: "your-google-client-id"
    client_secret: "your-google-client-secret"
    scopes: ["https://www.googleapis.com/auth/cloud-platform"]
  microsoft:
    client_id: "your-microsoft-client-id"
    client_secret: "your-microsoft-client-secret"
    scopes: ["https://graph.microsoft.com/.default"]
  openai:
    client_id: "your-openai-client-id"
    client_secret: "your-openai-client-secret"
    scopes: ["openai"]

refresh:
  enabled: true
  check_interval: 300  # 5 minutes
  refresh_before_expiry: 300  # 5 minutes before expiry
```

## Best Practices

### 1. Use Minimal Scopes

Only request the scopes you actually need:

```python
# Good - minimal scopes
oauth_manager.add_provider("github", scopes=["repo"])

# Bad - excessive scopes
oauth_manager.add_provider("github", scopes=["repo", "user", "admin:org", "admin:public_key"])
```

### 2. Handle Token Expiration

Always check token expiration:

```python
token_data = broker.get_credential("GITHUB_TOKEN")
if token_data:
    metadata = token_data.metadata
    expires_at = datetime.fromisoformat(metadata.get("expires_at", ""))
    
    if expires_at < datetime.now():
        # Token is expired, refresh it
        new_token = oauth_manager.refresh_token("github")
        # Update stored token
```

### 3. Use Automatic Refresh

Set up automatic refresh for long-running applications:

```python
# Configure refresh
oauth_manager.configure_refresh(
    provider="github",
    refresh_token=refresh_token,
    expires_in=3600
)

# Start scheduler
oauth_manager.start_refresh_scheduler()
```

### 4. Secure Token Storage

Store tokens securely in the credentials broker:

```python
# Store with proper metadata
broker.store_credential(
    "GITHUB_TOKEN",
    token.access_token,
    credential_type="oauth_token",
    metadata={
        "provider": "github",
        "expires_at": token.expires_at.isoformat(),
        "refresh_token": token.refresh_token,
        "scopes": token.scopes
    }
)
```

### 5. Handle Errors Gracefully

```python
try:
    token = oauth_manager.refresh_token("github")
except OAuthError as e:
    if e.error_code == "invalid_grant":
        # Refresh token is invalid, need to re-authenticate
        flow = oauth_manager.start_flow("github")
        # Handle re-authentication
    else:
        # Other error
        print(f"OAuth error: {e}")
```

## Examples

### Complete GitHub Integration

```python
from pheno.credentials import CredentialBroker
from pheno.credentials.oauth import OAuthFlowManager
import httpx

# Initialize systems
broker = CredentialBroker()
oauth_manager = OAuthFlowManager()

# Configure GitHub
oauth_manager.add_provider(
    "github",
    client_id="your-client-id",
    client_secret="your-client-secret",
    scopes=["repo", "user"]
)

# Start OAuth flow
flow = oauth_manager.start_flow("github")
print(f"Visit: {flow.authorization_url}")

# Complete flow (in real app, this would be from callback)
authorization_code = "user-provided-code"
token = oauth_manager.complete_flow(flow, authorization_code)

# Store token
broker.store_credential(
    "GITHUB_TOKEN",
    token.access_token,
    credential_type="oauth_token",
    metadata={
        "provider": "github",
        "expires_at": token.expires_at.isoformat(),
        "refresh_token": token.refresh_token,
        "scopes": token.scopes
    }
)

# Use token
token_data = broker.get_credential("GITHUB_TOKEN")
if token_data:
    access_token = token_data.value
    
    # Make API call
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = response.json()
        print(f"User: {user_data['login']}")
```

### Multi-Provider Setup

```python
# Configure multiple providers
providers = {
    "github": {
        "client_id": "github-client-id",
        "client_secret": "github-client-secret",
        "scopes": ["repo", "user"]
    },
    "google": {
        "client_id": "google-client-id",
        "client_secret": "google-client-secret",
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
    },
    "microsoft": {
        "client_id": "microsoft-client-id",
        "client_secret": "microsoft-client-secret",
        "scopes": ["https://graph.microsoft.com/.default"]
    }
}

# Add all providers
for name, config in providers.items():
    oauth_manager.add_provider(name, **config)

# Start flows for all providers
flows = {}
for provider in providers.keys():
    flows[provider] = oauth_manager.start_flow(provider)
    print(f"{provider}: {flows[provider].authorization_url}")

# Complete flows and store tokens
for provider, flow in flows.items():
    # In real app, get authorization code from callback
    authorization_code = f"{provider}-code"
    token = oauth_manager.complete_flow(flow, authorization_code)
    
    broker.store_credential(
        f"{provider.upper()}_TOKEN",
        token.access_token,
        credential_type="oauth_token",
        metadata={
            "provider": provider,
            "expires_at": token.expires_at.isoformat(),
            "refresh_token": token.refresh_token,
            "scopes": token.scopes
        }
    )
```

### CLI Workflow

```bash
# Configure providers
pheno-cli oauth configure github --client-id "..." --client-secret "..." --scopes "repo,user"
pheno-cli oauth configure google --client-id "..." --client-secret "..." --scopes "https://www.googleapis.com/auth/cloud-platform"

# Start OAuth flows
pheno-cli oauth start-flow github
pheno-cli oauth start-flow google

# Complete flows
pheno-cli oauth complete-flow github --code "github-code"
pheno-cli oauth complete-flow google --code "google-code"

# List tokens
pheno-cli oauth list-tokens

# Start refresh scheduler
pheno-cli oauth start-scheduler

# Check status
pheno-cli oauth validate github
pheno-cli oauth validate google
```

This OAuth integration provides comprehensive OAuth2 support with automatic token management, making it easy to integrate with various OAuth providers while maintaining security and ease of use.