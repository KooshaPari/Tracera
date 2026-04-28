# Pheno-SDK Detailed Service & Feature Index

## Directory: /src/pheno

### 1. Adapter Layer (pheno/adapters)
**Status**: FUNCTIONAL
**Purpose**: Database and service adapters
- **persistence/**: In-memory implementations
  - InMemoryUserRepository
  - InMemoryDeploymentRepository
  - InMemoryServiceRepository
  - InMemoryConfigurationRepository
- **Completeness**: 50% (in-memory only, no SQLAlchemy/MongoDB)

### 2. Analytics (pheno/analytics)
**Status**: PARTIAL
**Purpose**: Code analysis and metrics
- **code/dependencies.py**: Dependency graph analysis
  - TODO: unused import detection not implemented
- **Completeness**: 70%

### 3. Application (pheno/application)
**Status**: SPARSE
**Purpose**: Application-level abstractions
- Ports and base types
- **Completeness**: 40%

### 4. Architecture (pheno/architecture)
**Status**: REFERENCE/DOCS
**Purpose**: Documentation of architectural patterns
- **Completeness**: 30% (mostly reference material)

### 5. Async (pheno/async)
**Status**: PARTIAL
**Purpose**: Async task orchestration
- **storage.py**: InMemory, File, SQLite task storage
  - NotImplementedError for function availability checks
- **Completeness**: 50%

### 6. Auth (pheno/auth)
**Status**: PARTIAL
**Purpose**: Authentication and OAuth
- **session_broker.py**: OAuth token management (WORKING)
- **playwright_adapter.py**: Browser automation (BROKEN - NotImplementedError)
- **unified_auth/**: Unified authentication system
- **Completeness**: 40%

### 7. CI/CD (pheno/cicd)
**Status**: PARTIAL
**Purpose**: CI/CD pipeline integration
- **Completeness**: 50%

### 8. CLI (pheno/cli)
**Status**: PARTIAL
**Purpose**: Command-line interface
- **app/commands/**:
  - ✅ control_center.py
  - ❌ build.py (coming soon)
  - ❌ ui.py (coming soon)
  - ❌ manage.py (coming soon)
- **Completeness**: 60%

### 9. CLink (pheno/clink)
**Status**: MINIMAL
**Purpose**: Command-line parsing framework
- **parsers/base.py**: Abstract parser (NotImplementedError)
- **Completeness**: 30%

### 10. Configuration (pheno/config)
**Status**: COMPLETE ✅
**Purpose**: Configuration management
- **core.py**: 
  - Config.from_env() ✅
  - Config.from_file() ✅
  - Config.load() with cascade ✅
- **Completeness**: 100%

### 11. Core Registry (pheno/core/registry)
**Status**: FUNCTIONAL
**Purpose**: Adapter and plugin registry
- **adapters/registry.py**: AdapterRegistry
  - Auto-detect adapter type: NotImplementedError
  - Health checks ✅
  - Plugin hooks ✅
  - Singleton/Factory patterns ✅
- **Completeness**: 95%

### 12. Credentials (pheno/credentials)
**Status**: PARTIAL
**Purpose**: Credential management
- **Completeness**: 50%

### 13. Database (pheno/database)
**Status**: PARTIAL
**Purpose**: Database abstractions
- Supabase integration
- Entity mapping
- **Completeness**: 60%

### 14. Deployment (pheno/deployment)
**Status**: PARTIAL
**Purpose**: Deployment automation
- **Completeness**: 50%

### 15. Dev (pheno/dev)
**Status**: FUNCTIONAL
**Purpose**: Development utilities
- **utils/logging.py**: Verbose logging setup
- **Completeness**: 70%

### 16. Domain (pheno/domain)
**Status**: SPARSE
**Purpose**: Domain models and entities
- **models/project.py**: ProjectRegistry ✅
- **auth/types.py**: Basic auth types
- **value_objects/**: Common VOs
- **Completeness**: 40%

### 17. Errors (pheno/errors)
**Status**: COMPLETE ✅
**Purpose**: Error handling and categorization
- **exceptions.py**: ZenMCPError hierarchy ✅
- **unified.py**: Unified error handler ✅
  - ErrorCategory enum ✅
  - ErrorSeverity enum ✅
  - Retry logic ✅
- **Completeness**: 100%

### 18. Events (pheno/events)
**Status**: PARTIAL
**Purpose**: Event bus and event handling
- **Completeness**: 60%

### 19. Infra (pheno/infra)
**Status**: PARTIAL
**Purpose**: Infrastructure utilities
- **control_center/**: Desktop application
- **service_manager/**: Service health and status
- **tunnel_sync/**: CloudFlare tunnel integration
- **Completeness**: 60%

### 20. Infrastructure (pheno/infrastructure)
**Status**: PARTIAL
**Purpose**: Infrastructure bootstrap and adapters
- **adapters/container.py**:
  - register_default_adapters() (Supabase only)
  - run_health_checks() ✅
- **Completeness**: 70%

### 21. Integration (pheno/integration)
**Status**: PARTIAL
**Purpose**: System integration
- **validation/types.py**: Validation types
- **Completeness**: 50%

### 22. LLM (pheno/llm)
**Status**: PARTIAL
**Purpose**: LLM integrations
- **Completeness**: 50%

### 23. Logging (pheno/logging)
**Status**: COMPLETE ✅
**Purpose**: Logging system
- **core/logger.py**: Logger implementation ✅
- **handlers/**: 
  - console.py ✅
  - file.py ✅
  - json.py ✅
  - syslog.py ✅
- **integrations/structlog_adapter.py** ✅
- **Completeness**: 100%

### 24. MCP (pheno/mcp)
**Status**: PARTIAL
**Purpose**: Model Context Protocol integration
- **entry_points/**: AtomsMCPEntryPoint ✅
- **resources/handlers.py**: NotImplementedError (schema handlers)
- **resources/schemes/**: Log, env schemes
- **qa/**: QA and reporting
- **Completeness**: 70%

### 25. Observability (pheno/observability)
**Status**: PARTIAL
**Purpose**: Observability infrastructure
- **Completeness**: 60%

### 26. Patterns (pheno/patterns)
**Status**: PARTIAL
**Purpose**: Design patterns
- **creational/repository_factory.py**: 
  - InMemory ✅
  - SQLAlchemy ❌ (NotImplementedError)
  - MongoDB ❌ (NotImplementedError)
  - Redis ❌ (NotImplementedError)
- **crud/base.py**: CRUD base class
- **Completeness**: 25%

### 27. Plugins (pheno/plugins)
**Status**: MINIMAL
**Purpose**: Plugin system
- **load_plugin()**: Dynamic import ✅
- **supabase/**: Supabase plugin
- No discovery/lifecycle hooks
- **Completeness**: 30%

### 28. Ports (pheno/ports)
**Status**: COMPLETE ✅
**Purpose**: Port/interface definitions
- **observability.py**: Logger, Tracer, Meter, HealthChecker, Alerter ✅
- **registry.py**: Registry protocol variants ✅
- **auth/providers.py**: AuthProvider, CredentialManager ✅
- **mcp/**: MCP provider protocols ✅
- **Completeness**: 100%

### 29. Providers (pheno/providers)
**Status**: PARTIAL
**Purpose**: Provider implementations
- **registry_provider_mixin.py**: Abstract base
- **Completeness**: 40%

### 30. Quality (pheno/quality)
**Status**: PARTIAL
**Purpose**: Quality assurance
- **Completeness**: 50%

### 31. Resilience (pheno/resilience)
**Status**: PARTIAL
**Purpose**: Resilience patterns
- **bulkhead.py**: Async context (NotImplementedError for sync)
- **Completeness**: 50%

### 32. Resources (pheno/resources)
**Status**: PARTIAL
**Purpose**: Resource management
- **Completeness**: 50%

### 33. Security (pheno/security)
**Status**: PARTIAL
**Purpose**: Security utilities
- **scanners/models.py**: Security scan types
- **Completeness**: 50%

### 34. Shared (pheno/shared)
**Status**: FUNCTIONAL
**Purpose**: Shared utilities
- **cli_framework/**: CLI framework
  - base.py, logging.py, environment.py ✅
  - mcp_cli.py ✅
  - command_engine/validators.py ✅
- **mcp_entry_points/**: MCP entry points
  - atoms.py ✅ (Atoms specific)
  - zen.py ✅
- **Completeness**: 85%

### 35. Storage (pheno/storage)
**Status**: PARTIAL
**Purpose**: Storage backends
- **Completeness**: 50%

### 36. Testing (pheno/testing)
**Status**: PARTIAL
**Purpose**: Testing utilities
- **utils.py**: Test helpers
- **Completeness**: 60%

### 37. Tools (pheno/tools)
**Status**: PARTIAL
**Purpose**: Tool definitions and utilities
- **Completeness**: 50%

### 38. TUI (pheno/tui)
**Status**: PARTIAL
**Purpose**: Terminal UI components
- **widgets/**: Various widgets
- **core/**: TUI core framework
- **Completeness**: 70%

### 39. UI (pheno/ui)
**Status**: PARTIAL
**Purpose**: User interface components
- **tui/**: Terminal UI
- **Completeness**: 60%

### 40. Utilities (pheno/utilities)
**Status**: PARTIAL
**Purpose**: General utilities
- **Completeness**: 60%

### 41. Vector (pheno/vector)
**Status**: INCOMPLETE ❌
**Purpose**: Vector search and embeddings
- **client.py**:
  - Supabase backend ✅
  - pgvector ❌ (NotImplementedError: "coming soon")
  - OpenAI ❌ (NotImplementedError: "coming soon")
  - FAISS ❌ (NotImplementedError: "coming soon")
  - LanceDB ❌ (NotImplementedError: "coming soon")
- **Completeness**: 25%

### 42. Web (pheno/web)
**Status**: MINIMAL
**Purpose**: Web framework integration
- **Completeness**: 30%

### 43. Workflow (pheno/workflow)
**Status**: INCOMPLETE ❌
**Purpose**: Workflow orchestration
- **orchestrators/temporal/base.py**: 
  - `orchestrate()` method: NotImplementedError (abstract)
- **orchestration/agents/task_manager/storage.py**:
  - 5 NotImplementedError instances
  - InMemoryTaskStorage ✅
  - FileTaskStorage ✅
  - Redis ❌
  - Database ❌
- **Completeness**: 20%

---

## Summary Statistics

- **Total Modules**: 43
- **Complete Modules**: 5 (Config, Errors, Logging, Observability Ports, Registry Ports)
- **Functional Modules**: 12 (70-90% complete)
- **Partial Modules**: 22 (40-60% complete)
- **Incomplete Modules**: 4 (0-30% complete)

**Critical NotImplementedError Instances**: 60+
- Vector: 5
- Repository Factory: 12
- Workflow: 5
- Auth: 3
- Async/Storage: 5
- Others: 30+

---

## Quick Reference: What to Use vs Avoid

### ✅ SAFE FOR PRODUCTION
- Configuration loading
- Error handling & retry logic
- Logging (all handlers)
- Observability ports
- Registry system
- MCP entry points (Atoms)
- In-memory task storage
- Supabase database

### ⚠️ USE WITH CAUTION
- CLI framework (mostly works)
- MCP integration (incomplete handlers)
- Auth (basic OAuth works, Playwright broken)
- Development utilities

### ❌ AVOID/NOT READY
- pgvector backend
- OpenAI/FAISS/LanceDB embeddings
- SQLAlchemy/MongoDB/Redis repositories
- Workflow orchestration (Temporal)
- Advanced auth (browser automation)
- Build/UI/Manage CLI commands

---

## File Size & Complexity

- **Largest/Most Complex**: 
  - src/pheno/README.md (453KB - documentation)
  - src/pheno/infra/ (many infrastructure utilities)
  - src/pheno/ui/tui/ (comprehensive TUI implementation)

- **Most Test Coverage**:
  - Logging system
  - Configuration system
  - Error handling

---

## Notes for atoms_mcp-old Integration

1. **Core dependencies** pheno-sdk provides:
   - Configuration ✅
   - Logging ✅
   - Error handling ✅
   - MCP entry points ✅

2. **Risky dependencies** if used:
   - Vector search (only Supabase works)
   - Task storage (only in-memory/file work)
   - Advanced workflows (not implemented)
   - Repository pattern (only in-memory works)

3. **Path dependencies**:
   - Assumes atoms_mcp-old is at repo_root / "atoms_mcp-old"
   - Entry point looks for atoms-mcp-enhanced.py

4. **Environment variables**:
   - PHENO_SDK_ROOT: Override SDK root path
   - SKIP_PHENO_PATHS: Skip path injection
   - ATOMS_VERBOSE: Verbose logging
   - ATOMS_NO_TUNNEL: Disable tunnel
