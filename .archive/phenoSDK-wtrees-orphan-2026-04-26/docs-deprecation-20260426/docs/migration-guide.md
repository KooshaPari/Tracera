# Migration Guide

This guide helps you migrate from existing credential management solutions to the Pheno SDK Credentials Broker system.

## Table of Contents

- [From Environment Variables](#from-environment-variables)
- [From Manual OAuth](#from-manual-oauth)
- [From Project-Specific Storage](#from-project-specific-storage)
- [From Other Credential Managers](#from-other-credential-managers)
- [Migration Checklist](#migration-checklist)
- [Common Issues](#common-issues)
- [Best Practices](#best-practices)

## From Environment Variables

### Before (Environment Variables)

```python
import os

# Get environment variable
api_key = os.getenv("API_KEY")
database_url = os.getenv("DATABASE_URL")

# Set environment variable
os.environ["API_KEY"] = "new-key"

# With fallback
api_key = os.getenv("API_KEY", "default-value")
```

### After (Credentials Broker)

```python
from pheno.credentials import getenv, setenv

# Get credential (checks secure store first, then environment)
api_key = getenv("API_KEY")
database_url = getenv("DATABASE_URL")

# Set credential (stores in secure store and environment)
setenv("API_KEY", "new-key")

# With fallback
api_key = getenv("API_KEY", "default-value")
```

### Migration Steps

1. **Install Pheno SDK**:
   ```bash
   pip install pheno-sdk
   ```

2. **Update imports**:
   ```python
   # Replace
   import os
   
   # With
   from pheno.credentials import getenv, setenv
   ```

3. **Update credential access**:
   ```python
   # Replace
   api_key = os.getenv("API_KEY")
   
   # With
   api_key = getenv("API_KEY")
   ```

4. **Update credential storage**:
   ```python
   # Replace
   os.environ["API_KEY"] = "new-key"
   
   # With
   setenv("API_KEY", "new-key")
   ```

5. **Migrate existing credentials**:
   ```python
   from pheno.credentials import CredentialBroker
   
   broker = CredentialBroker()
   
   # Migrate from environment to secure storage
   env_vars = ["API_KEY", "DATABASE_URL", "SECRET_KEY"]
   for var in env_vars:
       value = os.getenv(var)
       if value:
           broker.store_credential(var, value, credential_type="secret")
   ```

## From Manual OAuth

### Before (Manual OAuth)

```python
import requests
import json

# Manual OAuth flow
def get_github_token():
    # Step 1: Get authorization URL
    auth_url = "https://github.com/login/oauth/authorize"
    params = {
        "client_id": "your-client-id",
        "scope": "repo,user",
        "state": "random-state"
    }
    response = requests.get(auth_url, params=params)
    
    # Step 2: User authorizes and gets code
    authorization_code = "user-provided-code"
    
    # Step 3: Exchange code for token
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "code": authorization_code
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()
    
    return token_data["access_token"]

# Manual token refresh
def refresh_github_token(refresh_token):
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=data)
    return response.json()["access_token"]

# Manual API calls
def make_github_api_call(endpoint, token):
    headers = {"Authorization": f"token {token}"}
    response = requests.get(f"https://api.github.com{endpoint}", headers=headers)
    return response.json()
```

### After (OAuth Integration)

```python
from pheno.credentials.oauth import OAuthFlowManager
from pheno.credentials import CredentialBroker

# Initialize OAuth manager
oauth_manager = OAuthFlowManager()
broker = CredentialBroker()

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

# Complete flow
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

# Automatic token refresh
oauth_manager.configure_refresh(
    provider="github",
    refresh_token=token.refresh_token,
    expires_in=3600
)
oauth_manager.start_refresh_scheduler()

# Use token
token_data = broker.get_credential("GITHUB_TOKEN")
if token_data:
    access_token = token_data.value
    # Make API call
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    )
```

### Migration Steps

1. **Replace manual OAuth with OAuth manager**:
   ```python
   # Replace manual OAuth code with OAuthFlowManager
   oauth_manager = OAuthFlowManager()
   oauth_manager.add_provider("github", client_id="...", client_secret="...")
   ```

2. **Update token storage**:
   ```python
   # Replace manual token storage with credentials broker
   broker.store_credential("GITHUB_TOKEN", token.access_token, ...)
   ```

3. **Set up automatic refresh**:
   ```python
   # Replace manual refresh with automatic refresh
   oauth_manager.configure_refresh("github", refresh_token, expires_in)
   oauth_manager.start_refresh_scheduler()
   ```

## From Project-Specific Storage

### Before (Project-Specific Storage)

```python
import json
import os
from pathlib import Path

class ProjectCredentials:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.creds_file = self.project_path / ".credentials.json"
    
    def load_credentials(self):
        if self.creds_file.exists():
            with open(self.creds_file) as f:
                return json.load(f)
        return {}
    
    def save_credential(self, name, value):
        creds = self.load_credentials()
        creds[name] = value
        with open(self.creds_file, 'w') as f:
            json.dump(creds, f)
    
    def get_credential(self, name):
        creds = self.load_credentials()
        return creds.get(name)

# Usage
project_creds = ProjectCredentials("/path/to/project")
project_creds.save_credential("API_KEY", "project-key")
api_key = project_creds.get_credential("API_KEY")
```

### After (Hierarchical Scoping)

```python
from pheno.credentials import CredentialBroker
from pheno.credentials.hierarchy import ScopeBuilder

# Initialize broker
broker = CredentialBroker()

# Create hierarchy
builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform", "Platform team", parent_path="atoms")
builder.add_project("krouter", "KRouter project", parent_path="atoms/platform")

hierarchy = builder.build()
broker.create_hierarchy("enterprise", hierarchy)

# Store project credential
broker.create_scope_credential(
    "API_KEY",
    "project-key",
    "atoms/platform/krouter",
    "secret",
    "enterprise"
)

# Retrieve project credential
api_key = broker.resolve_credential_hierarchical(
    "API_KEY",
    "atoms/platform/krouter",
    "enterprise"
)
```

### Migration Steps

1. **Create hierarchy structure**:
   ```python
   # Map your project structure to hierarchy
   builder = ScopeBuilder("enterprise")
   # Add your organizational structure
   ```

2. **Migrate existing credentials**:
   ```python
   # Load existing credentials
   old_creds = load_old_credentials()
   
   # Store in new system
   for name, value in old_creds.items():
       broker.create_scope_credential(name, value, project_path, "secret", "enterprise")
   ```

3. **Update credential access**:
   ```python
   # Replace project-specific access with hierarchical access
   api_key = broker.resolve_credential_hierarchical("API_KEY", project_path, "enterprise")
   ```

## From Other Credential Managers

### From AWS Secrets Manager

```python
# Before
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# After
from pheno.credentials import getenv

def get_secret(secret_name):
    return getenv(secret_name)
```

### From Azure Key Vault

```python
# Before
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret(secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value

# After
from pheno.credentials import getenv

def get_secret(secret_name):
    return getenv(secret_name)
```

### From HashiCorp Vault

```python
# Before
import hvac

def get_secret(secret_path):
    client = hvac.Client(url='https://vault.example.com')
    client.token = 'your-token'
    response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return response['data']['data']

# After
from pheno.credentials import getenv

def get_secret(secret_name):
    return getenv(secret_name)
```

## Migration Checklist

### Pre-Migration

- [ ] **Audit existing credentials**: List all credentials currently in use
- [ ] **Identify credential types**: Categorize credentials by type (API keys, tokens, connection strings, etc.)
- [ ] **Map organizational structure**: Understand your organization's hierarchy
- [ ] **Plan scope structure**: Design your hierarchical scoping structure
- [ ] **Backup existing credentials**: Ensure you have backups of all credentials

### During Migration

- [ ] **Install Pheno SDK**: `pip install pheno-sdk`
- [ ] **Create hierarchy**: Set up your organizational hierarchy
- [ ] **Migrate credentials**: Move credentials to the new system
- [ ] **Update code**: Replace old credential access with new system
- [ ] **Test thoroughly**: Ensure all credentials work correctly
- [ ] **Set up OAuth**: Configure OAuth providers if needed
- [ ] **Configure refresh**: Set up automatic token refresh

### Post-Migration

- [ ] **Verify security**: Ensure credentials are stored securely
- [ ] **Update documentation**: Update your documentation
- [ ] **Train team**: Train your team on the new system
- [ ] **Monitor usage**: Monitor credential usage and access
- [ ] **Clean up**: Remove old credential storage systems
- [ ] **Set up monitoring**: Set up monitoring and alerting

## Common Issues

### Issue: Credentials not found after migration

**Problem**: Credentials are not being found after migration.

**Solution**: Check that credentials are stored in the correct scope and that the scope path is correct.

```python
# Check if credential exists
credential = broker.get_credential("API_KEY")
if not credential:
    print("Credential not found")

# Check scope resolution
credential = broker.resolve_credential_hierarchical("API_KEY", "correct/scope/path", "hierarchy")
```

### Issue: OAuth tokens not refreshing

**Problem**: OAuth tokens are not refreshing automatically.

**Solution**: Ensure refresh tokens are stored correctly and refresh scheduler is running.

```python
# Check refresh configuration
oauth_manager.configure_refresh("github", refresh_token, expires_in)
oauth_manager.start_refresh_scheduler()

# Check if scheduler is running
if oauth_manager.scheduler_running:
    print("Refresh scheduler is running")
```

### Issue: Permission denied errors

**Problem**: Getting permission denied errors when accessing credentials.

**Solution**: Check that the credentials broker has proper permissions and that the data directory is accessible.

```python
# Check data directory permissions
from pathlib import Path
data_dir = Path.home() / ".pheno" / "credentials"
if not data_dir.exists():
    data_dir.mkdir(parents=True, exist_ok=True)
```

### Issue: Environment variables not working

**Problem**: Environment variables are not being read correctly.

**Solution**: Ensure you're using the enhanced `getenv` function from the credentials broker.

```python
# Wrong
import os
value = os.getenv("API_KEY")

# Correct
from pheno.credentials import getenv
value = getenv("API_KEY")
```

## Best Practices

### 1. Gradual Migration

Migrate gradually rather than all at once:

```python
# Phase 1: Install and test
from pheno.credentials import getenv
test_value = getenv("TEST_KEY")

# Phase 2: Migrate critical credentials
broker.store_credential("CRITICAL_KEY", "value")

# Phase 3: Migrate all credentials
# Migrate remaining credentials

# Phase 4: Remove old system
# Remove old credential management code
```

### 2. Test Thoroughly

Test each credential after migration:

```python
# Test credential access
def test_credential(name, expected_value):
    actual_value = getenv(name)
    assert actual_value == expected_value, f"Credential {name} mismatch"
    print(f"✅ {name} working correctly")

# Test all credentials
test_credential("API_KEY", "expected-api-key")
test_credential("DATABASE_URL", "expected-database-url")
```

### 3. Use Hierarchical Scoping

Organize credentials using hierarchical scoping:

```python
# Create meaningful hierarchy
builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform", "Platform team", parent_path="atoms")
builder.add_project("krouter", "KRouter project", parent_path="atoms/platform")

# Store credentials at appropriate levels
broker.create_scope_credential("GLOBAL_API_KEY", "global-key", "global", "secret", "enterprise")
broker.create_scope_credential("PROJECT_API_KEY", "project-key", "atoms/platform/krouter", "secret", "enterprise")
```

### 4. Set Up Monitoring

Monitor credential usage and access:

```python
# Enable audit logging
broker.enable_audit_logging()

# Check credential statistics
stats = broker.get_scope_statistics()
print(f"Total credentials: {stats['total_credentials']}")
```

### 5. Document Changes

Document all changes made during migration:

```markdown
# Migration Documentation

## Credentials Migrated
- API_KEY: Moved from environment to secure storage
- DATABASE_URL: Moved from project file to hierarchical scoping
- GITHUB_TOKEN: Moved from manual OAuth to OAuth integration

## Hierarchy Structure
- global
  - atoms (org)
    - platform (group)
      - krouter (project)

## OAuth Providers
- GitHub: Configured with repo, user scopes
- Google: Configured with cloud-platform scope
```

This migration guide provides comprehensive steps for migrating from various credential management solutions to the Pheno SDK Credentials Broker system.