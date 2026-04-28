# Namespace Mapping Glossary

**Version**: 2.0.0
**Date**: 2025-10-12
**Purpose**: Complete mapping of old names to new canonical identifiers

---

## Overview

This glossary provides a comprehensive mapping of all old names, packages, and identifiers to their new canonical equivalents in pheno-sdk v2.0.0. Use this as a reference during migration and when updating documentation.

---

## Authentication System Mapping

### Package Names

| Old Package | New Package | Status | Notes |
|-------------|-------------|--------|-------|
| `authkit-client` | `pheno.adapters.auth` | ✅ Migrated | Unified auth adapters |
| `authkit_client` | `pheno.adapters.auth` | ✅ Migrated | Python package name |
| `some_other_auth` | `pheno.adapters.auth.providers` | ✅ Migrated | Generic provider adapters |

### Class Names

| Old Class | New Class | Location | Notes |
|-----------|-----------|----------|-------|
| `AuthKitClient` | `AuthKitProvider` | `pheno.adapters.auth.providers.oauth2` | Provider adapter pattern |
| `CustomProvider` | `OAuth2GenericProvider` | `pheno.adapters.auth.providers.oauth2` | Generic OAuth2 provider |
| `AuthMiddleware` | `AuthManager` | `pheno.auth` | Unified auth management |
| `TokenManager` | `FileTokenManager` | `pheno.auth` | Token storage implementation |
| `SessionBroker` | `SessionOAuthBroker` | `pheno.auth` | Session management |

### Function Names

| Old Function | New Function | Location | Notes |
|--------------|--------------|----------|-------|
| `get_auth_token()` | `auth.authenticate()` | `pheno.auth.AuthManager` | Unified authentication |
| `validate_token()` | `auth.validate_token()` | `pheno.auth.AuthManager` | Token validation |
| `refresh_token()` | `auth.refresh_token()` | `pheno.auth.AuthManager` | Token refresh |
| `register_provider()` | `auth.register_provider()` | `pheno.auth.AuthManager` | Provider registration |

### MFA Components

| Old Component | New Component | Location | Notes |
|---------------|---------------|----------|-------|
| `EmailMFA` | `EmailAdapter` | `pheno.adapters.auth.mfa` | MFA adapter pattern |
| `SMSMFA` | `SMSAdapter` | `pheno.adapters.auth.mfa` | MFA adapter pattern |
| `TOTPMFA` | `TOTPAdapter` | `pheno.adapters.auth.mfa` | MFA adapter pattern |
| `PushMFA` | `PushAdapter` | `pheno.adapters.auth.mfa` | MFA adapter pattern |

---

## Service Infrastructure Mapping

### Package Names

| Old Package | New Package | Status | Notes |
|-------------|-------------|--------|-------|
| `service_manager` | `pheno.infra` | ✅ Migrated | Unified service infrastructure |
| `service_manager` | `pheno.infra.service_manager` | ✅ Migrated | Service management module |
| `orchestrator` | `pheno.infra.orchestrator` | ✅ Migrated | Service orchestration |
| `container` | `pheno.infra.container` | ✅ Migrated | Dependency injection |

### Class Names

| Old Class | New Class | Location | Notes |
|-----------|-----------|----------|-------|
| `ServiceManager` | `ServiceManager` | `pheno.infra` | Unified service management |
| `Orchestrator` | `ServiceOrchestrator` | `pheno.infra` | Service orchestration |
| `Container` | `Container` | `pheno.infra.container` | Dependency injection |
| `ServiceConfig` | `ServiceConfig` | `pheno.infra` | Service configuration |
| `HealthMonitor` | `HealthMonitor` | `pheno.infra` | Health monitoring |

### Function Names

| Old Function | New Function | Location | Notes |
|--------------|--------------|----------|-------|
| `register_service()` | `manager.register_service()` | `pheno.infra.ServiceManager` | Service registration |
| `start_all()` | `orchestrator.start_all()` | `pheno.infra.ServiceOrchestrator` | Start all services |
| `stop_all()` | `orchestrator.stop_all()` | `pheno.infra.ServiceOrchestrator` | Stop all services |
| `monitor()` | `orchestrator.monitor()` | `pheno.infra.ServiceOrchestrator` | Service monitoring |

---

## Proxy Gateway Mapping

### Package Names

| Old Package | New Package | Status | Notes |
|-------------|-------------|--------|-------|
| `proxy_server` | `pheno.infra.proxy_gateway` | ✅ Migrated | Unified proxy gateway |
| `proxy_gateway` | `pheno.infra.proxy_gateway` | ✅ Canonical | Gateway functionality |
| `gateway` | `pheno.infra.proxy_gateway` | ✅ Canonical | Gateway components |
| `router` | `pheno.infra.proxy_gateway.server` | ✅ Canonical | Request routing |

### Class Names

| Old Class | New Class | Location | Notes |
|-----------|-----------|----------|-------|
| `ProxyServer` | `ProxyServer` | `pheno.infra.proxy_gateway` | Main proxy server |
| `Gateway` | `RequestRouter` | `pheno.infra.proxy_gateway.server` | Request routing |
| `Router` | `RequestRouter` | `pheno.infra.proxy_gateway.server` | Request routing |
| `UpstreamRegistry` | `UpstreamRegistry` | `pheno.infra.proxy_gateway.server` | Upstream management |
| `HealthMonitor` | `HealthMonitor` | `pheno.infra.proxy_gateway.server` | Health monitoring |

### Function Names

| Old Function | New Function | Location | Notes |
|--------------|--------------|----------|-------|
| `add_route()` | `add_upstream()` | `pheno.infra.proxy_gateway.ProxyServer` | Route registration |
| `remove_route()` | `remove_upstream()` | `pheno.infra.proxy_gateway.ProxyServer` | Route removal |
| `start_proxy()` | `start()` | `pheno.infra.proxy_gateway.ProxyServer` | Start proxy server |
| `stop_proxy()` | `stop()` | `pheno.infra.proxy_gateway.ProxyServer` | Stop proxy server |

---

## Namespace Migration Mapping

### Old Namespaces (Removed)

| Old Namespace | New Namespace | Status | Notes |
|---------------|---------------|--------|-------|
| `phen.adapters` | `pheno.adapters` | ✅ Migrated | Moved to pheno namespace |
| `phen.application` | `pheno.application` | ✅ Migrated | Moved to pheno namespace |
| `phen.domain` | `pheno.domain` | ✅ Migrated | Moved to pheno namespace |
| `phen.ports` | `pheno.ports` | ✅ Migrated | Moved to pheno namespace |

### New Canonical Namespaces

| Namespace | Purpose | Components |
|-----------|---------|------------|
| `pheno.adapters.auth` | Authentication adapters | Providers, MFA, token management |
| `pheno.infra` | Service infrastructure | Orchestration, management, monitoring |
| `pheno.infra.service_infra` | Service infrastructure manager | Port allocation, tunnels, info |
| `pheno.infra.proxy_gateway` | Proxy gateway | Routing, health monitoring, fallback |
| `pheno.auth` | Core authentication | Manager, types, interfaces |
| `pheno.application` | Application layer | Use cases, orchestration |
| `pheno.domain` | Domain layer | Entities, value objects, specifications |
| `pheno.ports` | Port layer | Interfaces, protocols, contracts |

---

## Configuration Mapping

### Environment Variables

| Old Variable | New Variable | Notes |
|--------------|--------------|-------|
| `AUTHKIT_CLIENT_ID` | `AUTH_CLIENT_ID` | Unified auth configuration |
| `AUTHKIT_CLIENT_SECRET` | `AUTH_CLIENT_SECRET` | Unified auth configuration |
| `CUSTOM_AUTH_URL` | `AUTH_ISSUER` | Standardized auth issuer |
| `SERVICE_PORT` | `SERVICE_PREFERRED_PORT` | Service port configuration |
| `ORCHESTRATOR_PORT` | `FALLBACK_PORT` | Fallback server port |
| `PROXY_PORT` | `PROXY_PORT` | Proxy server port |

### Configuration Files

| Old File | New File | Notes |
|----------|----------|-------|
| `authkit-client.yaml` | `pheno-config.yaml` | Unified configuration |
| `service-config.yaml` | `pheno-config.yaml` | Unified configuration |
| `proxy-config.yaml` | `pheno-config.yaml` | Unified configuration |

### Configuration Sections

| Old Section | New Section | Notes |
|-------------|-------------|-------|
| `authkit:` | `auth.providers.authkit:` | Nested provider configuration |
| `services:` | `services:` | Service configuration (unchanged) |
| `proxy:` | `proxy:` | Proxy configuration (unchanged) |

---

## Import Statement Mapping

### Authentication Imports

| Old Import | New Import | Notes |
|------------|------------|-------|
| `from authkit_client import AuthKitClient` | `from pheno.adapters.auth.providers import AuthKitProvider` | Provider adapter |
| `from some_other_auth import CustomProvider` | `from pheno.adapters.auth.providers import OAuth2GenericProvider` | Generic provider |
| `from auth_middleware import AuthMiddleware` | `from pheno.auth import AuthManager` | Unified manager |

### Service Infrastructure Imports

| Old Import | New Import | Notes |
|------------|------------|-------|
| `from service_manager import ServiceManager` | `from pheno.infra import ServiceManager` | Unified infrastructure |
| `from orchestrator import Orchestrator` | `from pheno.infra import ServiceOrchestrator` | Service orchestration |
| `from container import Container` | `from pheno.infra.container import Container` | Dependency injection |

### Proxy Gateway Imports

| Old Import | New Import | Notes |
|------------|------------|-------|
| `from proxy_server import ProxyServer` | `from pheno.infra.proxy_gateway import ProxyServer` | Unified proxy |
| `from gateway import Gateway` | `from pheno.infra.proxy_gateway.server import RequestRouter` | Request routing |
| `from router import Router` | `from pheno.infra.proxy_gateway.server import RequestRouter` | Request routing |

---

## API Method Mapping

### Authentication API

| Old Method | New Method | Class | Notes |
|------------|------------|-------|-------|
| `authkit.get_token()` | `auth.authenticate()` | `AuthManager` | Unified authentication |
| `authkit.refresh_token()` | `auth.refresh_token()` | `AuthManager` | Token refresh |
| `authkit.validate_token()` | `auth.validate_token()` | `AuthManager` | Token validation |
| `middleware.authenticate()` | `auth.authenticate()` | `AuthManager` | Unified auth |

### Service Infrastructure API

| Old Method | New Method | Class | Notes |
|------------|------------|-------|-------|
| `service_mgr.register_service()` | `manager.register_service()` | `ServiceManager` | Service registration |
| `orchestrator.start_all()` | `orchestrator.start_all()` | `ServiceOrchestrator` | Start services |
| `orchestrator.monitor()` | `orchestrator.monitor()` | `ServiceOrchestrator` | Service monitoring |

### Proxy Gateway API

| Old Method | New Method | Class | Notes |
|------------|------------|-------|-------|
| `proxy.add_route()` | `proxy.add_upstream()` | `ProxyServer` | Route registration |
| `gateway.route()` | `router.handle_request()` | `RequestRouter` | Request handling |
| `proxy.start()` | `proxy.start()` | `ProxyServer` | Start proxy |

---

## File Path Mapping

### Source Files

| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/phen/adapters/auth/` | `src/pheno/adapters/auth/` | Moved to pheno namespace |
| `src/phen/application/` | `src/pheno/application/` | Moved to pheno namespace |
| `src/phen/domain/` | `src/pheno/domain/` | Moved to pheno namespace |
| `src/phen/ports/` | `src/pheno/ports/` | Moved to pheno namespace |

### Configuration Files

| Old Path | New Path | Notes |
|----------|----------|-------|
| `config/authkit-client.yaml` | `config/pheno-config.yaml` | Unified configuration |
| `config/service-config.yaml` | `config/pheno-config.yaml` | Unified configuration |
| `config/proxy-config.yaml` | `config/pheno-config.yaml` | Unified configuration |

### Test Files

| Old Path | New Path | Notes |
|----------|----------|-------|
| `tests/authkit_client/` | `tests/auth/` | Unified auth tests |
| `tests/service_manager/` | `tests/infra/` | Unified infrastructure tests |
| `tests/proxy_gateway/` | `tests/infra/proxy_gateway/` | Proxy gateway tests |

---

## Migration Scripts

### Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/migrate_imports.py` | Update import statements | `python scripts/migrate_imports.py` |
| `scripts/migrate_config.py` | Convert configuration files | `python scripts/migrate_config.py --input old.yaml --output new.yaml` |
| `scripts/migrate_tests.py` | Update test files | `python scripts/migrate_tests.py` |
| `scripts/validate_migration.py` | Validate migration | `python scripts/validate_migration.py` |

### Usage Examples

```bash
# Migrate all imports
python scripts/migrate_imports.py --path src/

# Convert configuration
python scripts/migrate_config.py --input config/old-config.yaml --output config/new-config.yaml

# Update tests
python scripts/migrate_tests.py --path tests/

# Validate migration
python scripts/validate_migration.py --path src/
```

---

## Validation Checklist

### Pre-Migration
- [ ] Backup current codebase
- [ ] Document current configuration
- [ ] Identify all custom implementations
- [ ] Plan migration timeline

### During Migration
- [ ] Update import statements
- [ ] Convert configuration files
- [ ] Update test files
- [ ] Validate functionality

### Post-Migration
- [ ] Run full test suite
- [ ] Validate all integrations
- [ ] Update documentation
- [ ] Deploy to staging

---

## Support Resources

### Documentation
- **Migration Guide**: [docs/migrations/NAMESPACE_MIGRATION_GUIDE.md](migrations/NAMESPACE_MIGRATION_GUIDE.md)
- **Release Notes**: [docs/RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md)
- **API Reference**: [docs/API_REFERENCE.md](API_REFERENCE.md)

### Tools
- **Migration Scripts**: `scripts/migration/`
- **Validation Tools**: `scripts/validation/`
- **Rollback Tools**: `scripts/rollback/`

### Community
- **GitHub Issues**: [github.com/pheno-sdk/issues](https://github.com/pheno-sdk/issues)
- **Discord**: [discord.gg/pheno-sdk](https://discord.gg/pheno-sdk)
- **Documentation**: [docs.pheno-sdk.com](https://docs.pheno-sdk.com)

---

**Last Updated**: 2025-10-12
**Version**: 2.0.0
**Next Review**: 2025-11-12
