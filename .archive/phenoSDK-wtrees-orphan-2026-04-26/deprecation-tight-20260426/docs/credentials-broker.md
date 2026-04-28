# Credentials Broker System

The Pheno SDK Credentials Broker is a comprehensive credential management system that provides secure storage, hierarchical scoping, OAuth integration, and automation capabilities for managing authentication tokens and secrets across projects.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [Hierarchical Scoping](#hierarchical-scoping)
- [OAuth Integration](#oauth-integration)
- [CLI Commands](#cli-commands)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Security](#security)
- [Migration Guide](#migration-guide)

## Overview

The Credentials Broker system provides:

- **Secure Storage**: OS keyring integration with encryption fallbacks
- **Hierarchical Scoping**: Global → Group → Org → Program → Portfolio → Project scoping
- **OAuth Management**: Automated token refresh and flow management
- **Environment Integration**: Enhanced environment variable management
- **CLI Interface**: Rich TUI for credential management
- **Automation**: Rule-based credential refresh and cleanup

## Quick Start

### Installation

```bash
pip install pheno-sdk
```

### Basic Usage

```python
from pheno.credentials import CredentialBroker

# Initialize the broker
broker = CredentialBroker()

# Store a credential
broker.store_credential("API_KEY", "your-api-key", credential_type="secret")

# Retrieve a credential
api_key = broker.get_credential("API_KEY")
print(f"API Key: {api_key}")

# Use enhanced environment variable access
from pheno.credentials import getenv
api_key = getenv("API_KEY")  # Checks secure store first, then env
```

### CLI Usage

```bash
# List all credentials
pheno-cli credentials list

# Store a new credential
pheno-cli credentials store API_KEY "your-key" --type secret

# Interactive TUI
pheno-cli credentials tui
```

## Core Features

### 1. Secure Storage

The broker uses multiple storage backends with security fallbacks:

- **Primary**: OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- **Fallback**: Encrypted file storage using Fernet encryption
- **Development**: In-memory storage for testing

```python
# Store with specific type
broker.store_credential(
    name="DATABASE_URL",
    value="postgresql://user:pass@localhost/db",
    credential_type="connection_string",
    project_id="my-project"
)

# Store with metadata
broker.store_credential(
    name="GITHUB_TOKEN",
    value="ghp_...",
    credential_type="oauth_token",
    metadata={
        "provider": "github",
        "expires_at": "2024-12-31T23:59:59Z",
        "scopes": ["repo", "user"]
    }
)
```

### 2. Enhanced Environment Variables

The broker provides an enhanced `getenv` function that checks secure storage first:

```python
from pheno.credentials import getenv, setenv

# This checks secure store first, then environment
api_key = getenv("API_KEY")

# Set in both secure store and environment
setenv("API_KEY", "new-value")

# With fallback
api_key = getenv("API_KEY", default="fallback-value")
```

### 3. Project Scoping

Credentials can be scoped to specific projects:

```python
# Global credential (available everywhere)
broker.store_credential("GLOBAL_API_KEY", "key", project_id=None)

# Project-specific credential
broker.store_credential("PROJECT_API_KEY", "key", project_id="my-project")

# List project credentials
project_creds = broker.list_credentials(project_id="my-project")
```

## Hierarchical Scoping

The hierarchical scoping system provides deeply composable credential management with unlimited nesting levels.

### Scope Types

- **GLOBAL**: Available to all projects
- **GROUP**: Organization-level grouping
- **ORG**: Organization-specific credentials
- **PROGRAM**: Program-level credentials
- **PORTFOLIO**: Portfolio-level credentials
- **PROJECT**: Project-specific credentials
- **ENVIRONMENT**: Environment-specific (dev, staging, prod)
- **USER**: User-specific credentials

### Creating Hierarchies

```python
from pheno.credentials.hierarchy import ScopeBuilder

# Create a new hierarchy
builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform", "Platform team", parent_path="atoms")
builder.add_program("ai-ml", "AI/ML program", parent_path="platform")
builder.add_portfolio("llm-ops", "LLM Operations portfolio", parent_path="ai-ml")
builder.add_project("krouter", "KRouter project", parent_path="llm-ops")

hierarchy = builder.build()
broker.create_hierarchy("enterprise", hierarchy)
```

### Scope Resolution

Credentials are resolved using a hierarchical fallback chain:

```python
# Resolve credential with hierarchical scoping
credential = broker.resolve_credential_hierarchical(
    name="API_KEY",
    scope_path="atoms/platform/ai-ml/llm-ops/krouter",
    hierarchy_name="enterprise"
)

# The resolution order:
# 1. krouter project scope
# 2. llm-ops portfolio scope
# 3. ai-ml program scope
# 4. platform group scope
# 5. atoms org scope
# 6. global scope
```

### Scope Templates

Pre-built templates for common organizational structures:

```python
from pheno.credentials.hierarchy import ScopeTemplate

# Enterprise template
enterprise = ScopeTemplate.create_enterprise_hierarchy("atoms")
hierarchy = enterprise.build()

# Development template
dev = ScopeTemplate.create_development_hierarchy("atoms")
hierarchy = dev.build()
```

## OAuth Integration

The broker provides comprehensive OAuth flow management with automatic token refresh.

### Supported Providers

- GitHub
- Google
- Microsoft
- OpenAI
- Custom OAuth2 providers

### OAuth Flow Management

```python
from pheno.credentials.oauth import OAuthFlowManager

# Initialize OAuth manager
oauth_manager = OAuthFlowManager()

# Configure GitHub OAuth
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
```

### Automatic Token Refresh

```python
# Configure automatic refresh
oauth_manager.configure_refresh(
    provider="github",
    refresh_token="refresh-token",
    expires_in=3600
)

# Start refresh scheduler
oauth_manager.start_refresh_scheduler()

# Manual refresh
new_token = oauth_manager.refresh_token("github")
```

### OAuth CLI Commands

```bash
# List OAuth providers
pheno-cli oauth list-providers

# Start OAuth flow
pheno-cli oauth start-flow github

# Complete OAuth flow
pheno-cli oauth complete-flow github --code "authorization-code"

# Refresh token
pheno-cli oauth refresh github
```

## CLI Commands

### Credential Management

```bash
# List all credentials
pheno-cli credentials list

# Store credential
pheno-cli credentials store NAME VALUE [--type TYPE] [--project PROJECT]

# Get credential
pheno-cli credentials get NAME [--project PROJECT]

# Delete credential
pheno-cli credentials delete NAME [--project PROJECT]

# Interactive TUI
pheno-cli credentials tui
```

### Hierarchical Scoping

```bash
# List hierarchies
pheno-cli hierarchy list

# Create hierarchy
pheno-cli hierarchy create NAME [--description DESCRIPTION]

# Show hierarchy tree
pheno-cli hierarchy show NAME

# Resolve credential
pheno-cli scope resolve NAME SCOPE_PATH [--hierarchy HIERARCHY]

# List scope credentials
pheno-cli scope list SCOPE_PATH [--hierarchy HIERARCHY]

# Create scope credential
pheno-cli scope create NAME VALUE SCOPE_PATH [--type TYPE]

# Show scope statistics
pheno-cli scope stats [--hierarchy HIERARCHY]
```

### OAuth Management

```bash
# List OAuth providers
pheno-cli oauth list-providers

# Configure provider
pheno-cli oauth configure PROVIDER --client-id ID --client-secret SECRET

# Start OAuth flow
pheno-cli oauth start-flow PROVIDER

# Complete OAuth flow
pheno-cli oauth complete-flow PROVIDER --code CODE

# Refresh token
pheno-cli oauth refresh PROVIDER

# List OAuth tokens
pheno-cli oauth list-tokens
```

## API Reference

### CredentialBroker

```python
class CredentialBroker:
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the credential broker."""
    
    def store_credential(self, name: str, value: str, **kwargs) -> bool:
        """Store a credential securely."""
    
    def get_credential(self, name: str, **kwargs) -> Optional[str]:
        """Retrieve a credential."""
    
    def delete_credential(self, name: str, **kwargs) -> bool:
        """Delete a credential."""
    
    def list_credentials(self, **kwargs) -> List[Credential]:
        """List credentials."""
    
    # Hierarchical scoping methods
    def create_hierarchy(self, name: str, hierarchy: ScopeHierarchy) -> bool:
        """Create a new scope hierarchy."""
    
    def resolve_credential_hierarchical(self, name: str, scope_path: str, 
                                      hierarchy_name: str = "default") -> Optional[str]:
        """Resolve credential using hierarchical scoping."""
    
    def get_scope_credentials(self, scope_path: str, 
                            hierarchy_name: str = "default") -> List[Credential]:
        """Get all credentials for a scope."""
    
    def create_scope_credential(self, name: str, value: str, scope_path: str,
                              credential_type: str = "secret", 
                              hierarchy_name: str = "default") -> bool:
        """Create a credential in a specific scope."""
```

### Hierarchical Scoping

```python
class ScopeHierarchy:
    def __init__(self, name: str, nodes: Dict[UUID, ScopeNode]):
        """Initialize scope hierarchy."""
    
    def add_node(self, node: ScopeNode) -> bool:
        """Add a node to the hierarchy."""
    
    def get_node(self, node_id: UUID) -> Optional[ScopeNode]:
        """Get a node by ID."""
    
    def get_children(self, node_id: UUID) -> List[ScopeNode]:
        """Get child nodes."""
    
    def get_ancestors(self, node_id: UUID) -> List[ScopeNode]:
        """Get ancestor nodes."""
    
    def validate(self) -> bool:
        """Validate hierarchy structure."""

class ScopeNode:
    def __init__(self, name: str, type: ScopeType, path: str, 
                 parent_id: Optional[UUID] = None):
        """Initialize scope node."""
    
    def get_full_path(self) -> str:
        """Get full hierarchical path."""
    
    def is_ancestor_of(self, other: 'ScopeNode') -> bool:
        """Check if this node is an ancestor of another."""
    
    def is_descendant_of(self, other: 'ScopeNode') -> bool:
        """Check if this node is a descendant of another."""
```

### OAuth Integration

```python
class OAuthFlowManager:
    def __init__(self):
        """Initialize OAuth flow manager."""
    
    def add_provider(self, name: str, **config) -> bool:
        """Add OAuth provider."""
    
    def start_flow(self, provider: str, **kwargs) -> OAuthFlow:
        """Start OAuth flow."""
    
    def complete_flow(self, flow: OAuthFlow, authorization_code: str) -> OAuthToken:
        """Complete OAuth flow."""
    
    def refresh_token(self, provider: str) -> OAuthToken:
        """Refresh OAuth token."""
    
    def start_refresh_scheduler(self) -> None:
        """Start automatic token refresh scheduler."""
```

## Configuration

### Environment Variables

```bash
# Data directory for credential storage
PHENO_CREDENTIALS_DATA_DIR=/path/to/data

# Encryption key (if not using OS keyring)
PHENO_CREDENTIALS_ENCRYPTION_KEY=your-encryption-key

# OAuth configuration
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Configuration File

Create `~/.pheno/credentials.yaml`:

```yaml
data_dir: ~/.pheno/credentials
encryption:
  key: "your-encryption-key"
  algorithm: "fernet"
oauth:
  providers:
    github:
      client_id: "your-client-id"
      client_secret: "your-client-secret"
      scopes: ["repo", "user"]
    google:
      client_id: "your-client-id"
      client_secret: "your-client-secret"
      scopes: ["https://www.googleapis.com/auth/cloud-platform"]
hierarchies:
  default:
    name: "Default Hierarchy"
    description: "Default scope hierarchy"
    nodes:
      - type: "global"
        name: "global"
        path: "global"
```

## Security

### Encryption

- **OS Keyring**: Uses platform-native secure storage
- **File Storage**: Fernet encryption with PBKDF2 key derivation
- **Memory**: Encrypted in-memory storage for development

### Access Control

- **Project Isolation**: Credentials are isolated by project
- **Scope Permissions**: Hierarchical access control
- **Audit Logging**: All credential access is logged

### Best Practices

1. **Use OS Keyring**: Prefer OS keyring over file storage
2. **Rotate Keys**: Regularly rotate encryption keys
3. **Minimal Scopes**: Use minimal OAuth scopes
4. **Audit Access**: Regularly review credential access logs
5. **Secure Storage**: Never store credentials in plain text

## Migration Guide

### From Environment Variables

```python
# Old way
import os
api_key = os.getenv("API_KEY")

# New way
from pheno.credentials import getenv
api_key = getenv("API_KEY")  # Checks secure store first
```

### From Manual OAuth

```python
# Old way
import requests
response = requests.post("https://api.github.com/user", 
                        headers={"Authorization": f"token {token}"})

# New way
from pheno.credentials.oauth import OAuthFlowManager
oauth_manager = OAuthFlowManager()
token = oauth_manager.get_token("github")
response = requests.post("https://api.github.com/user",
                        headers={"Authorization": f"token {token}"})
```

### From Project-Specific Storage

```python
# Old way
project_creds = load_project_credentials("my-project")
api_key = project_creds.get("API_KEY")

# New way
api_key = broker.resolve_credential_hierarchical(
    "API_KEY", 
    "atoms/platform/my-project",
    "enterprise"
)
```

## Examples

### Complete Setup

```python
from pheno.credentials import CredentialBroker
from pheno.credentials.hierarchy import ScopeBuilder
from pheno.credentials.oauth import OAuthFlowManager

# Initialize broker
broker = CredentialBroker()

# Create enterprise hierarchy
builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform", "Platform team", parent_path="atoms")
builder.add_project("krouter", "KRouter project", parent_path="atoms/platform")

hierarchy = builder.build()
broker.create_hierarchy("enterprise", hierarchy)

# Store credentials at different scopes
broker.create_scope_credential("GLOBAL_API_KEY", "global-key", "global", "secret", "enterprise")
broker.create_scope_credential("ORG_API_KEY", "org-key", "atoms", "secret", "enterprise")
broker.create_scope_credential("PROJECT_API_KEY", "project-key", "atoms/platform/krouter", "secret", "enterprise")

# Resolve credentials (with fallback)
global_key = broker.resolve_credential_hierarchical("GLOBAL_API_KEY", "atoms/platform/krouter", "enterprise")
# Returns: "global-key"

project_key = broker.resolve_credential_hierarchical("PROJECT_API_KEY", "atoms/platform/krouter", "enterprise")
# Returns: "project-key"

# OAuth setup
oauth_manager = OAuthFlowManager()
oauth_manager.add_provider("github", client_id="...", client_secret="...")
flow = oauth_manager.start_flow("github")
# Complete flow and store token
```

### CLI Workflow

```bash
# Create hierarchy
pheno-cli hierarchy create enterprise --description "Enterprise hierarchy"

# Add OAuth provider
pheno-cli oauth configure github --client-id "..." --client-secret "..."

# Start OAuth flow
pheno-cli oauth start-flow github

# Store credentials
pheno-cli scope create GLOBAL_API_KEY "global-key" global --type secret --hierarchy enterprise
pheno-cli scope create PROJECT_API_KEY "project-key" atoms/platform/krouter --type secret --hierarchy enterprise

# List credentials
pheno-cli scope list atoms/platform/krouter --hierarchy enterprise

# Interactive management
pheno-cli credentials tui
```

This comprehensive documentation covers all aspects of the Credentials Broker system, including the new hierarchical scoping and OAuth integration features.