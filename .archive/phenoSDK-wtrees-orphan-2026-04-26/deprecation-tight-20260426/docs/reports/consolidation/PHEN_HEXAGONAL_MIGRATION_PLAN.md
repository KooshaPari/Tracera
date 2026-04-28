# Pheno Hexagonal Migration Plan

Meta-plan for folding the remaining mixed-layer packages into a strict hexagonal layout while keeping the canonical `src/pheno` namespace. The steps below capture the module moves, interface promotions, and adapter extractions required so that future reorganizations stay mechanical rather than structural refactors.

---

## 1. Authentication Stack

**Current anatomy**

- Domain types and errors live in `src/pheno/auth/types.py`.
- Port contracts (providers, token storage, MFA) are defined in `src/pheno/auth/interfaces.py` and re-exported via `src/pheno/auth/core/interfaces.py`.
- Application orchestration (`AuthManager`) sits in `src/pheno/auth/manager.py`.
- Adapters – concrete providers, MFA channels, token stores – remain under `src/pheno/auth/providers/` and `src/pheno/auth/mfa/`.

**Required refactors**

1. **Domain relocation**
   Move `AuthTokens`, `Credentials`, `MFAContext`, and error hierarchy into `src/pheno/domain/auth/types.py` and adjust imports (`src/pheno/auth/types.py:1-179`, `src/pheno/domain/__init__.py`).
2. **Port extraction**
   Promote `AuthProvider`, `TokenManager`, `CredentialManager`, and `MFAAdapter` interfaces to `src/pheno/ports/auth/providers.py` (source: `src/pheno/auth/interfaces.py:1-160`).
3. **Application layer**
   Re-home `AuthManager` (currently `src/pheno/auth/manager.py:1-140`) under `src/pheno/application/auth/manager.py`, re-wiring it to depend on the new port module names.
4. **Adapters consolidation**
   Transfer concrete provider/mfa/token implementations into `src/pheno/adapters/auth/...` and bind them via DI instead of global registries (`src/pheno/auth/providers/registry.py`, `src/pheno/auth/mfa/*.py`, `src/pheno/auth/token_manager.py`).
5. **Registry cleanup**
   Delete deprecated shims under `src/pheno/auth/core/` after consumers point to the new modules.

---

## 2. Workflow Orchestration

**Current anatomy**

- Core workflow entities/engine live directly in `src/pheno/workflow/core/` and `src/pheno/workflow/task.py`.
- Multi-agent orchestrator resides in `src/pheno/workflow/orchestration/orchestrator.py`.
- Persistence, scheduling, and monitoring helpers sit beside orchestrator code (same package).

**Required refactors**

1. **Domain models**
   Move base workflow/task dataclasses and enums into `src/pheno/domain/workflow/` (`src/pheno/workflow/core/workflow.py`, `src/pheno/workflow/task.py`).
2. **Ports**
   Define explicit port protocols for orchestrator backends, persistence, and monitoring in `src/pheno/ports/workflow/...` (referencing `src/pheno/workflow/core/engine.py:1-166` dependencies).
3. **Application services**
   Place orchestration and engine logic under `src/pheno/application/workflow/` (`src/pheno/workflow/core/engine.py`, `src/pheno/workflow/orchestration/orchestrator.py`).
4. **Adapters**
   Migrate concrete orchestrators (e.g., Temporal backend at `src/pheno/workflow/orchestrators/temporal.py`) and persistence implementations into `src/pheno/adapters/workflow/...`.
5. **Monitoring**
   Ensure metrics helpers (`src/pheno/workflow/monitoring/metrics.py`) become adapters depending on the monitoring ports.

---

## 3. Process & Service Management

**Current anatomy**

- Abstract process base classes live in `src/pheno/process/base/`.
- Concrete process management and launchers (`src/pheno/process/components/`, `src/pheno/process/services/*.py`) mix orchestration with adapter concerns.
- Factories (`src/pheno/process/factories/`) construct adapter instances directly.

**Required refactors**

1. **Domain rules**
   Introduce explicit domain entities/value objects describing processes and service lifecycles (`src/pheno/process/base/process_base.py:1-116`, `src/pheno/process/components/process_manager.py:1-171`).
2. **Ports**
   Define process control contracts (start/stop/status) in `src/pheno/ports/process/` so other layers can depend on stable abstractions.
3. **Application services**
   Rehome orchestration logic (factories, launchers) into `src/pheno/application/process/` with dependency injection against the new ports.
4. **Adapters**
   Deploy concrete subprocess, Go, and Next.js launchers under `src/pheno/adapters/process/` (`src/pheno/process/services/go.py`, `src/pheno/process/services/nextjs.py`, `src/pheno/process/services/launcher.py:1-117`).
5. **KInfra integration**
   Align `src/pheno/infra/service_manager/` and `src/pheno/infra/orchestrator.py` to consume the new ports, shimming only at the adapter boundary.

---

## 4. Infrastructure, Providers, and Resources

**Current anatomy**

- `src/pheno/infra/` still mixes orchestration code (`orchestrator.py:1-160`) with adapter implementations and service templates.
- `src/pheno/providers/registry*.py` maintain legacy registries with warnings.
- Resource management (`src/pheno/resources/*.py`) behaves like a service layer but exposes adapter-specific details.

**Required refactors**

1. **Deprecation removal**
   Remove `src/pheno/providers/registry.py` after introducing a replacement under the new adapter namespace (`src/pheno/providers/registry.py:1-206`).
2. **Port definitions**
   Capture infrastructure contracts (service manager, tunnel sync, resource allocators) under `src/pheno/ports/infra/...`.
3. **Application orchestration**
   Move orchestration logic currently in `src/pheno/infra/orchestrator.py` and `src/pheno/infra/service_manager/manager.py` beneath `src/pheno/application/infra/`.
4. **Adapters**
   Locate concrete implementations (gRPC, fallback server, tunnel handlers) in `src/pheno/adapters/infra/...`.
5. **Resource models**
   Determine which pieces of `src/pheno/resources/` belong to domain (e.g., budget types) versus adapters (storage backends) and move accordingly.

---

## 5. Enabling Tasks Before Rename

1. Update DI/bootstrap utilities to resolve dependencies via the new port modules instead of accessing concrete packages directly (affects `src/pheno/adapters/container_config.py`, `src/pheno/shared/command_engine/unified_engine.py:126`).
2. Expand architecture fitness tests (`tests/architecture/test_import_boundaries.py:7-55`) to watch the new `pheno.domain` and `pheno.ports` packages once they exist.
3. Stage import rewrites with `tools/migrate_imports.py` so that the rename from `pheno` → `pheno` becomes a simple tree move.

---

Tracking this plan in version control lets us execute the migration incrementally: complete each section, update imports/tests, and then flip the package name with confidence.
