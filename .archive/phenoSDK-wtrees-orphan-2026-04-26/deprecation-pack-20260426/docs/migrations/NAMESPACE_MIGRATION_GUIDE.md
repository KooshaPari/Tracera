# Namespace Migration Guide

**Version**: 2.0.0
**Date**: 2025-10-12
**Status**: ✅ Complete

---

## Overview

This guide covers the migration from the old scattered namespace structure to the new canonical namespaces in pheno-sdk v2.0.0. The migration consolidates authentication, service infrastructure, and proxy gateway functionality into unified, well-organized namespaces.

## Breaking Changes Summary

### 🚨 Major Changes

1. **Authentication System Consolidation**
   - Old: Scattered auth implementations across multiple kits
   - New: Unified `pheno.adapters.auth` namespace
   - Impact: All auth-related imports need updating

2. **Service Infrastructure Unification**
   - Old: Mixed service management across different modules
   - New: Centralized `pheno.infra` namespace
   - Impact: Service orchestration code needs updating

3. **Proxy Gateway Standardization**
   - Old: Various proxy implementations
   - New: Unified `pheno.infra.proxy_gateway` namespace
   - Impact: Proxy configuration code needs updating

---

## Migration by Component

### 1. Authentication System

#### Before (v1.x)
```python
# Scattered imports
from authkit_client import AuthKitClient
from some_other_auth import CustomProvider
from auth_middleware import AuthMiddleware

# Multiple auth systems
authkit = AuthKitClient(config)
custom_auth = CustomProvider(settings)
middleware = AuthMiddleware()
```

#### After (v2.0)
```python
# Unified imports
from pheno.auth import AuthManager, Credentials
from pheno.adapters.auth.providers import AuthKitProvider, Auth0Provider
from pheno.adapters.auth.mfa import EmailAdapter, TOTPAdapter

# Single unified system
auth = AuthManager()
auth.register_provider("authkit", AuthKitProvider)
auth.register_provider("auth0", Auth0Provider)
auth.register_mfa_adapter("email", EmailAdapter)
auth.register_mfa_adapter("totp", TOTPAdapter)
```

#### Migration Steps

1. **Update Imports**
   ```bash
   # Find and replace
   find . -name "*.py" -exec sed -i 's/from authkit_client import/from pheno.adapters.auth.providers import/g' {} \;
   find . -name "*.py" -exec sed -i 's/from some_other_auth import/from pheno.adapters.auth.providers import/g' {} \;
   ```

2. **Consolidate Auth Managers**
   ```python
   # Replace multiple auth instances with single AuthManager
   auth = AuthManager()
   # Register all providers with the unified manager
   ```

3. **Update Token Handling**
```python
# Old
token = authkit.get_token()

# New
result = await auth.authenticate("authkit", credentials)
if result.success:
    token = result.tokens.access_token
```

### 1b. Provider Catalog Registry

#### Before (v1.x)
```python
from pheno.providers.registry.compat import OpenAIModelRegistry

registry = OpenAIModelRegistry()
details = registry.get_capabilities("gpt-4")
```

#### After (v2.0)
```python
from pheno.providers.registry import OpenAIModelCatalog

catalog = OpenAIModelCatalog()
details = catalog.get_capabilities("gpt-4")
```

#### Migration Steps
1. Replace imports from `pheno.providers.registry.compat` with `pheno.providers.registry`.
2. Swap registry class names:
   - `ModelProviderRegistry` → `ModelCatalogRegistry`
   - `CapabilityModelRegistry` → `CapabilityCatalogRegistry`
   - `<Vendor>ModelRegistry` → `<Vendor>ModelCatalog`
3. Update any subclassing to inherit from the new catalog classes.
4. Note: Legacy aliases remain available until **31 March 2025**; treat that date as the final cut-over.

### 2. Service Infrastructure

#### Before (v1.x)
```python
# Mixed service management
from service_manager import ServiceManager
from orchestrator import Orchestrator
from container import Container

# Multiple orchestration systems
service_mgr = ServiceManager()
orchestrator = Orchestrator()
container = Container()
```

#### After (v2.0)
```python
# Unified service infrastructure
from pheno.infra import ServiceManager, ServiceConfig, ServiceOrchestrator
from pheno.infra.container import Container

# Single orchestration system
orchestrator = ServiceOrchestrator()
manager = ServiceManager()
container = Container()
```

#### Migration Steps

1. **Update Service Registration**
   ```python
   # Old
   service_mgr.register_service("api", command=["python", "api.py"])

   # New
   config = ServiceConfig(
       name="api",
       command=["python", "api.py"],
       preferred_port=8000,
       enable_tunnel=True
   )
   manager.register_service(config)
   ```

2. **Consolidate Orchestration**
   ```python
   # Old
   await service_mgr.start_all()
   await orchestrator.monitor()

   # New
   await orchestrator.start_all()
   await orchestrator.monitor()
   ```

### 3. Proxy Gateway

#### Before (v1.x)
```python
# Various proxy implementations
from proxy_server import ProxyServer
from gateway import Gateway
from router import Router

# Multiple proxy systems
proxy = ProxyServer(port=9100)
gateway = Gateway()
router = Router()
```

### 4. Tunnel API Modernisation

- **Legacy:** `ServiceInfra.start_tunnel(...)`, `ServiceInfra.get_service_url(...)`
- **Canonical:** `ServiceInfra.create_tunnel(...)`, `ServiceInfra.get_public_url(...)`

#### Update Plan
1. Replace every call to `start_tunnel` with `create_tunnel` (supports the same parameters).
2. Swap `get_service_url` for `get_public_url`.
3. Watch the runtime logs: the legacy methods now emit warnings indicating they will be removed after **31 March 2025**.

### 5. HTTP Client Transition

- **Legacy:** `from pheno.dev.http import HTTPClient`
- **Canonical:** `from pheno.dev.http import create_client, create_async_client`

#### Migration Steps
1. Replace `HTTPClient` instantiations with `create_client(base_url=..., timeout=...)`.
2. Update context managers and response handling to the httpx semantics (responses act like `httpx.Response`).
3. The legacy `HTTPClient` now issues a `DeprecationWarning` on construction with the same 31 March 2025 removal date—plan remediation accordingly.

#### After (v2.0)
```python
# Unified proxy gateway
from pheno.infra.proxy_gateway import ProxyServer
from pheno.infra.proxy_gateway.server.router import RequestRouter

# Single proxy system
proxy = ProxyServer(proxy_port=9100, fallback_port=9000)
```

#### Migration Steps

1. **Update Proxy Configuration**
   ```python
   # Old
   proxy.add_route("/api", "http://localhost:8000")

   # New
   proxy.add_upstream("/api", port=8000, host="localhost")
   ```

2. **Consolidate Routing**
   ```python
   # Old
   await proxy.start()
   await gateway.start()

   # New
   await proxy.start()
   # Gateway functionality integrated into proxy
   ```

---

## Configuration Migration

### Environment Variables

#### Before (v1.x)
```bash
# Scattered auth configs
AUTHKIT_CLIENT_ID=xxx
AUTHKIT_CLIENT_SECRET=xxx
CUSTOM_AUTH_URL=xxx
CUSTOM_AUTH_SECRET=xxx

# Mixed service configs
SERVICE_PORT=8000
ORCHESTRATOR_PORT=9000
PROXY_PORT=9100
```

#### After (v2.0)
```bash
# Unified auth config
AUTH_PROVIDER=authkit
AUTH_CLIENT_ID=xxx
AUTH_CLIENT_SECRET=xxx
AUTH_ISSUER=https://auth.example.com

# Unified service config
SERVICE_PREFERRED_PORT=8000
PROXY_PORT=9100
FALLBACK_PORT=9000
```

### Configuration Files

#### Before (v1.x)
```yaml
# authkit-client.yaml
authkit:
  client_id: xxx
  client_secret: xxx

# service-config.yaml
services:
  api:
    port: 8000
    command: ["python", "api.py"]
```

#### After (v2.0)
```yaml
# pheno-config.yaml
auth:
  providers:
    authkit:
      client_id: xxx
      client_secret: xxx
  mfa:
    email:
      enabled: true
      smtp_host: smtp.example.com

services:
  api:
    name: api
    command: ["python", "api.py"]
    preferred_port: 8000
    enable_tunnel: true
    enable_fallback: true
```

---

## Testing Migration

### Test Configuration

#### Before (v1.x)
```python
# Multiple test setups
@pytest.fixture
def authkit_client():
    return AuthKitClient(test_config)

@pytest.fixture
def service_manager():
    return ServiceManager(test_config)
```

#### After (v2.0)
```python
# Unified test setup
@pytest.fixture
def auth_manager():
    auth = AuthManager()
    auth.register_provider("test", MockProvider)
    return auth

@pytest.fixture
def service_orchestrator():
    return ServiceOrchestrator(test_config)
```

### Mock Providers

#### Before (v1.x)
```python
# Multiple mock implementations
class MockAuthKitClient:
    def get_token(self):
        return "mock_token"

class MockServiceManager:
    def start_all(self):
        pass
```

#### After (v2.0)
```python
# Unified mock system
from pheno.adapters.auth.providers import AuthProvider

class MockProvider(AuthProvider):
    async def authenticate(self, credentials):
        return AuthResult(success=True, tokens=MockTokens())
```

---

## Rollback Strategy

If issues arise during migration, you can rollback using these steps:

### 1. Revert Code Changes
```bash
# Revert to previous version
git checkout v1.x
pip install -r requirements-v1.txt
```

### 2. Restore Configuration
```bash
# Restore old config files
cp config/authkit-client.yaml.backup config/
cp config/service-config.yaml.backup config/
```

### 3. Database Migration
```bash
# If database schema changed
python migrate_rollback.py
```

### 4. Service Restart
```bash
# Restart all services
systemctl restart pheno-services
```

---

## Validation Checklist

After migration, verify these components work correctly:

### Authentication
- [ ] OAuth2 flows work with all providers
- [ ] MFA adapters function correctly
- [ ] Token refresh works properly
- [ ] Session management is stable

### Service Infrastructure
- [ ] Services start and stop correctly
- [ ] Health checks are working
- [ ] Port allocation is consistent
- [ ] Orchestration is stable

### Proxy Gateway
- [ ] Request routing works correctly
- [ ] Health-aware routing functions
- [ ] Fallback pages display properly
- [ ] Admin API is accessible

### Integration
- [ ] All kits work together
- [ ] Configuration is consistent
- [ ] Logging and metrics are working
- [ ] Error handling is proper

---

## Support

### Getting Help

- **Documentation**: [docs.pheno-sdk.com](https://docs.pheno-sdk.com)
- **GitHub Issues**: [github.com/pheno-sdk/issues](https://github.com/pheno-sdk/issues)
- **Discord**: [discord.gg/pheno-sdk](https://discord.gg/pheno-sdk)

### Migration Support

- **Migration Scripts**: Available in `scripts/migration/`
- **Test Suite**: Run `pytest tests/migration/` to validate
- **Rollback Tools**: Available in `scripts/rollback/`

---

## Timeline

- **v2.0.0 Release**: 2025-10-12
- **Migration Period**: 2025-10-12 to 2025-11-12
- **v1.x Deprecation**: 2025-11-12
- **v1.x EOL**: 2026-01-12

---

**Next Steps**: After completing migration, see [Release Notes](RELEASE_NOTES_v2.0.0.md) for new features and improvements.
