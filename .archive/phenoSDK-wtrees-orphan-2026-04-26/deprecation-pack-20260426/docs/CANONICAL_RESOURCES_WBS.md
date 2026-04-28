# Canonical Resource & Secrets Management - Work Breakdown Structure

**Project:** Pheno SDK - Canonical Resource & Secrets Management
**Version:** 1.0
**Date:** 2025-10-13
**Status:** In Progress

---

## 📋 Project Overview

Implement a centralized system for managing shared infrastructure resources and encrypted secrets across all Pheno SDK projects.

### Goals
1. **Shared Resources:** Single PostgreSQL/Redis/NATS/MongoDB/RabbitMQ instances shared across projects
2. **Encrypted Secrets:** Passkey-protected secrets storage with global/project/local scopes
3. **Automatic Migration:** Consume and migrate .env files to encrypted store
4. **Multi-Tenancy:** Project-specific databases/namespaces within shared resources
5. **CLI Integration:** Complete CLI for managing resources and secrets

---

## 🎯 Success Criteria

### Technical Metrics
- ✅ All resource types supported (PostgreSQL, Redis, NATS, MongoDB, RabbitMQ, MinIO, Elasticsearch)
- ✅ Passkey-protected secrets with AES-256 encryption
- ✅ Automatic .env migration with backup
- ✅ Multi-scope secrets (global, project, local)
- ✅ Resource registry tracking usage across projects
- ✅ Health checking and auto-restart
- ✅ CLI commands for all operations

### Quality Metrics
- Test coverage >90%
- Type coverage 100%
- Documentation complete
- Examples provided

---

## 📊 Work Breakdown Structure

### Phase 1: Secrets Management (Week 1) ✅

#### Task 1.1: Passkey Management ✅
- [x] PasskeyManager class
- [x] PBKDF2 key derivation
- [x] Passkey initialization
- [x] Passkey verification
- [x] Passkey change functionality
- [x] Session management (cache passkey)
- [x] PasskeyValidator for strength checking

**Deliverables:**
- `src/pheno/infrastructure/secrets/passkey.py`
- Passkey prompt with confirmation
- Session start/end commands

#### Task 1.2: Encrypted Secrets Store ✅
- [x] SecretsStore base class
- [x] EncryptedSecretsStore implementation
- [x] AES-256-GCM encryption
- [x] JSON storage format
- [x] Metadata support (created_at, updated_at, description)
- [x] Secret rotation

**Deliverables:**
- `src/pheno/infrastructure/secrets/store.py`
- Encrypted file format: `~/.pheno/secrets/*.enc`

#### Task 1.3: Secret Scopes ✅
- [x] SecretScope enum (GLOBAL, PROJECT, LOCAL, AUTO)
- [x] Scope descriptions and priorities
- [x] Resolution order (local > project > global)

**Deliverables:**
- `src/pheno/infrastructure/secrets/scope.py`

#### Task 1.4: Secrets Broker ✅
- [x] SecretsBroker main interface
- [x] Multi-scope support
- [x] Automatic scope resolution
- [x] Session management
- [x] get(), set(), delete(), list_keys(), get_all()
- [x] to_env() for environment export
- [x] Project name detection

**Deliverables:**
- `src/pheno/infrastructure/secrets/broker.py`
- Global store: `~/.pheno/secrets/global.enc`
- Project store: `~/.pheno/secrets/projects/{project}.enc`
- Local store: `./.pheno/secrets.local.enc`

#### Task 1.5: .env Migration ✅
- [x] EnvMigrator class
- [x] Parse .env files
- [x] Automatic backup (.env.backup.{timestamp})
- [x] Migrate to encrypted store
- [x] Optional removal of original
- [x] Update .gitignore
- [x] Export to .env (for compatibility)

**Deliverables:**
- `src/pheno/infrastructure/secrets/migration.py`

#### Task 1.6: Secrets Providers ✅
- [x] SecretsProvider base class
- [x] FileSecretsProvider (default)
- [ ] VaultSecretsProvider (HashiCorp Vault)
- [ ] AWSSecretsProvider (AWS Secrets Manager)
- [ ] AzureSecretsProvider (Azure Key Vault)

**Deliverables:**
- `src/pheno/infrastructure/secrets/providers.py`

#### Task 1.7: Credential Manager ✅
- [x] CredentialManager high-level interface
- [x] Database credential storage
- [x] API key storage
- [x] Typed credential interfaces

**Deliverables:**
- `src/pheno/infrastructure/secrets/credential_manager.py`

---

### Phase 2: Resource Management (Week 2)

#### Task 2.1: Resource Registry
- [x] ResourceRegistry class
- [x] ResourceInfo dataclass
- [x] ResourceStatus enum
- [x] YAML-based storage (~/.pheno/resources/registry.yaml)
- [x] Track projects using each resource
- [x] Update status
- [x] List unused resources

**Deliverables:**
- `src/pheno/infrastructure/resources/registry.py`

#### Task 2.2: Resource Definitions
- [x] ResourceDefinition base class
- [x] HealthCheck configuration
- [x] PostgreSQLResource
- [x] RedisResource
- [x] MongoDBResource
- [x] NATSResource
- [x] RabbitMQResource
- [x] MinIOResource
- [x] ElasticsearchResource

**Deliverables:**
- `src/pheno/infrastructure/resources/definitions/base.py`
- `src/pheno/infrastructure/resources/definitions/postgres.py`
- `src/pheno/infrastructure/resources/definitions/redis.py`
- `src/pheno/infrastructure/resources/definitions/mongodb.py`
- `src/pheno/infrastructure/resources/definitions/nats.py`
- `src/pheno/infrastructure/resources/definitions/rabbitmq.py`
- `src/pheno/infrastructure/resources/definitions/minio.py`
- `src/pheno/infrastructure/resources/definitions/elasticsearch.py`

#### Task 2.3: Resource Providers
- [ ] ResourceProvider base class
- [ ] DockerResourceProvider
  - [ ] Docker client integration
  - [ ] Container creation
  - [ ] Container start/stop
  - [ ] Health checking
  - [ ] Volume management
- [ ] LocalResourceProvider (for non-Docker resources)
- [ ] CloudResourceProvider (future: AWS RDS, etc.)

**Deliverables:**
- `src/pheno/infrastructure/resources/providers/base.py`
- `src/pheno/infrastructure/resources/providers/docker.py`
- `src/pheno/infrastructure/resources/providers/local.py`

#### Task 2.4: Resource Manager
- [ ] ResourceManager main interface
- [ ] get_or_create() - Get existing or create new resource
- [ ] get_database_url() - Get project-specific connection
- [ ] list_resources() - List all resources
- [ ] health_check() - Check resource health
- [ ] cleanup_unused() - Remove unused resources
- [ ] Integration with ResourceRegistry
- [ ] Integration with SecretsBroker

**Deliverables:**
- `src/pheno/infrastructure/resources/manager.py`

---

### Phase 3: Configuration Management (Week 3)

#### Task 3.1: Configuration Hierarchy
- [ ] ConfigScope enum (GLOBAL, PROJECT, LOCAL, DEFAULT)
- [ ] HierarchicalConfig class
- [ ] Merge strategy (local > project > global > defaults)
- [ ] Dot-notation access (config.get("resources.postgres.port"))

**Deliverables:**
- `src/pheno/infrastructure/config/scope.py`
- `src/pheno/infrastructure/config/hierarchical.py`

#### Task 3.2: Configuration Loader
- [ ] ConfigLoader class
- [ ] Load from YAML files
- [ ] Load from environment variables
- [ ] Load from defaults
- [ ] Merge all sources

**Deliverables:**
- `src/pheno/infrastructure/config/loader.py`

#### Task 3.3: Configuration Manager
- [ ] ConfigManager main interface
- [ ] load() - Load all configuration
- [ ] get() - Get configuration value
- [ ] set() - Set configuration value
- [ ] validate() - Validate configuration
- [ ] get_effective() - Get merged configuration

**Deliverables:**
- `src/pheno/infrastructure/config/manager.py`

#### Task 3.4: Configuration Files
- [ ] Global config: `~/.pheno/config.yaml`
- [ ] Project config: `.pheno.yaml`
- [ ] Local config: `.pheno.local.yaml` (git-ignored)
- [ ] Default configuration embedded in code

**Deliverables:**
- Configuration file schemas
- Example configurations

---

### Phase 4: CLI Integration (Week 4)

#### Task 4.1: Secrets CLI Commands
- [ ] `pheno secrets init` - Initialize secrets system
- [ ] `pheno secrets session start` - Start secrets session
- [ ] `pheno secrets session end` - End secrets session
- [ ] `pheno secrets get <KEY>` - Get secret value
- [ ] `pheno secrets set <KEY> <VALUE>` - Set secret value
- [ ] `pheno secrets delete <KEY>` - Delete secret
- [ ] `pheno secrets list` - List all secrets
- [ ] `pheno secrets migrate <ENV_FILE>` - Migrate .env file
- [ ] `pheno secrets export <OUTPUT>` - Export to .env
- [ ] `pheno secrets rotate <KEY>` - Rotate secret
- [ ] `pheno secrets change-passkey` - Change master passkey

**Deliverables:**
- `src/pheno/cli/commands/secrets.py`

#### Task 4.2: Resources CLI Commands
- [ ] `pheno resources list` - List all resources
- [ ] `pheno resources start <NAME>` - Start resource
- [ ] `pheno resources stop <NAME>` - Stop resource
- [ ] `pheno resources restart <NAME>` - Restart resource
- [ ] `pheno resources status <NAME>` - Check resource status
- [ ] `pheno resources health <NAME>` - Health check
- [ ] `pheno resources cleanup` - Remove unused resources
- [ ] `pheno resources logs <NAME>` - View resource logs

**Deliverables:**
- `src/pheno/cli/commands/resources.py`

#### Task 4.3: Init CLI Command
- [ ] `pheno init` - Initialize project
  - [ ] Create .pheno.yaml
  - [ ] Discover/create shared resources
  - [ ] Create project-specific databases
  - [ ] Migrate .env if exists
  - [ ] Generate connection strings
  - [ ] Store in secrets

**Deliverables:**
- `src/pheno/cli/commands/init.py`

---

### Phase 5: Testing (Week 5)

#### Task 5.1: Unit Tests
- [ ] Passkey management tests
- [ ] Secrets store tests
- [ ] Secrets broker tests
- [ ] .env migration tests
- [ ] Resource registry tests
- [ ] Resource definitions tests
- [ ] Configuration tests

**Deliverables:**
- `tests/unit/infrastructure/test_passkey.py`
- `tests/unit/infrastructure/test_secrets_store.py`
- `tests/unit/infrastructure/test_secrets_broker.py`
- `tests/unit/infrastructure/test_env_migration.py`
- `tests/unit/infrastructure/test_resource_registry.py`
- `tests/unit/infrastructure/test_resource_definitions.py`

#### Task 5.2: Integration Tests
- [ ] End-to-end secrets workflow
- [ ] End-to-end resource workflow
- [ ] Multi-project resource sharing
- [ ] .env migration workflow
- [ ] CLI integration tests

**Deliverables:**
- `tests/integration/test_secrets_workflow.py`
- `tests/integration/test_resources_workflow.py`
- `tests/integration/test_multi_project.py`

---

### Phase 6: Documentation (Week 6)

#### Task 6.1: User Documentation
- [ ] Getting Started guide
- [ ] Secrets management guide
- [ ] Resource management guide
- [ ] Configuration guide
- [ ] CLI reference
- [ ] Migration guide

**Deliverables:**
- `docs/CANONICAL_RESOURCES_GUIDE.md`
- `docs/SECRETS_MANAGEMENT.md`
- `docs/RESOURCE_MANAGEMENT.md`
- `docs/CLI_REFERENCE.md`

#### Task 6.2: Examples
- [ ] Basic secrets usage
- [ ] Multi-project setup
- [ ] .env migration example
- [ ] Custom resource definitions
- [ ] Cloud provider integration

**Deliverables:**
- `examples/canonical_resources/`

---

## 📦 Deliverables Summary

### Code Components: 50+
- Secrets Management: 10 files
- Resource Management: 15 files
- Configuration Management: 5 files
- CLI Commands: 3 files
- Tests: 15+ files
- Documentation: 6 files

### Resource Types Supported: 7
- PostgreSQL
- Redis
- MongoDB
- NATS
- RabbitMQ
- MinIO
- Elasticsearch

### Secret Scopes: 3
- Global (shared across projects)
- Project (project-specific)
- Local (machine-specific)

---

## 🎯 Current Status

### Completed ✅
- Phase 1: Secrets Management (100%)
  - Passkey management with session support
  - Encrypted secrets store
  - Multi-scope secrets broker
  - .env migration
  - Credential manager

- Phase 2: Resource Management (60%)
  - Resource registry
  - 7 resource definitions (PostgreSQL, Redis, MongoDB, NATS, RabbitMQ, MinIO, Elasticsearch)

### In Progress 🔄
- Phase 2: Resource Management (40%)
  - Resource providers (Docker, Local)
  - Resource manager

### Not Started ⏳
- Phase 3: Configuration Management
- Phase 4: CLI Integration
- Phase 5: Testing
- Phase 6: Documentation

---

## 📈 Timeline

| Week | Phase | Status |
|------|-------|--------|
| Week 1 | Secrets Management | ✅ Complete |
| Week 2 | Resource Management | 🔄 60% |
| Week 3 | Configuration Management | ⏳ Not Started |
| Week 4 | CLI Integration | ⏳ Not Started |
| Week 5 | Testing | ⏳ Not Started |
| Week 6 | Documentation | ⏳ Not Started |

**Overall Progress:** 30% Complete

---

**Next Steps:**
1. Complete Resource Providers (Docker, Local)
2. Implement Resource Manager
3. Begin Configuration Management
4. Start CLI Integration
