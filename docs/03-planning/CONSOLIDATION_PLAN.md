# 🎯 Pheno-SDK Consolidation Plan

**Date**: 2025-10-30
**Status**: 🟢 **READY TO EXECUTE**

---

## Executive Summary

Based on comprehensive analysis of zen-mcp-server, router, and morph, we've identified **1,850-2,300 lines of duplicate code** that can be consolidated into pheno-sdk, plus valuable architectural patterns that will benefit all projects.

---

## Current Progress

### ✅ Repair Phase Complete
- **61 files repaired** (CRUN + pheno-sdk linter corruption)
- **367 undefined-name errors fixed** in pheno-sdk (90% reduction)
- **pheno.cli module completed** (22 exports working)
- **39 auto-fixable ruff issues** resolved

### 📊 Remaining Issues
- **CRUN**: ~1,315 invalid-syntax errors (mostly in dependencies)
- **Pheno-SDK**: 40 undefined-name errors (manual review needed)
- **Both**: ~2,000 linter warnings (non-blocking)

---

## Consolidation Opportunities

### Priority 1: CRITICAL (Immediate - Week 1-2)

#### 1. YAML Configuration Consolidation
**Current**: 99% identical code in 3 projects (268 lines each)

**Files to consolidate**:
- `zen-mcp-server/settings/config.py` (268 lines)
- `morph/settings/config.py` (268 lines)
- Similar patterns in router

**Target**: `pheno-sdk/src/pheno/config/yaml_config.py`

**New exports**:
```python
from pheno.config import BaseYamlAppSettings, BaseYamlSecrets, YamlConfigLoader

class ZenAppSettings(BaseYamlAppSettings):
    app_name: str = "zen-mcp-server"  # Only project-specific overrides

settings = YamlConfigLoader(ZenAppSettings).load()
```

**Savings**: 400-500 LOC across projects

---

#### 2. KInfra Service Setup Consolidation
**Current**: Duplicated infrastructure setup in all projects

**Files to consolidate**:
- `zen-mcp-server/kinfra_setup.py` (13 lines - shim)
- `morph/kinfra_setup.py` (244 lines - full implementation)
- `router/kinfra_setup.py` (25 lines - shim)

**Target**: `pheno-sdk/src/pheno/infra/service_setup.py`

**New exports**:
```python
from pheno.infra import ServiceInfrastructure, TunnelManager, ServiceRegistry

infra = ServiceInfrastructure(
    service_name="zen-mcp-server",
    port_range=(8000, 9000)
)
infra.setup()  # Handles port allocation, tunnels, cleanup
```

**Savings**: 200-250 LOC

---

#### 3. Hexagonal Architecture Ports Pattern
**Current**: Morph has complete ports/adapters, others don't

**Pattern to standardize**:
- 11 domain ports (logging, config, I/O, code analysis, etc.)
- 9 driven adapters (implementations)
- Clean separation of concerns

**Target**: `pheno-sdk/src/pheno/ports/` + `pheno-sdk/src/pheno/adapters/`

**New structure**:
```python
# Define standard interfaces
from pheno.ports import LoggingPort, ConfigPort, IOPort

# Projects implement or use reference adapters
from pheno.adapters import StandardLoggingAdapter

logger = StandardLoggingAdapter()
```

**Value**: 500+ LOC saved per new project + architectural consistency

---

### Priority 2: HIGH (Week 3-4)

#### 4. Logging Pattern Consolidation
**Current**: Multiple implementations across projects

**Files involved**:
- `morph/morph_core/domain/ports/logging.py` (92 lines)
- `morph/morph_core/adapters/driven/logging_adapter.py` (280 lines)
- Various zen-mcp-server logging utils

**Target**: `pheno-sdk/src/pheno/logging/unified.py`

**Consolidate**:
- LogLevel enum
- LogEntry dataclass
- LoggingPort protocol
- StandardLogger implementation
- Metric recording

**Savings**: 250-300 LOC

---

#### 5. MCP Server Factory Consolidation
**Current**: Similar patterns for server creation

**Files involved**:
- `zen-mcp-server/server/factory.py`
- `morph/server.py` (FastMCP with DI, middleware)
- Router pipeline patterns

**Target**: `pheno-sdk/src/pheno/mcp/server_factory.py`

**New exports**:
```python
from pheno.mcp import MCPServerFactory, MiddlewareRegistry

server = MCPServerFactory(
    name="zen-mcp-server",
    middleware=[logging_middleware, metrics_middleware]
).create()
```

**Savings**: 200-300 LOC

---

### Priority 3: MEDIUM (Week 5-6)

#### 6. CLI Argument Parsing
**Current**: Duplicated argparse code in 10+ files

**Target**: `pheno-sdk/src/pheno/cli/args.py`

**Savings**: 150-200 LOC

#### 7. Resilience/Error Handling
**Current**: Scattered retry/timeout patterns

**Target**: `pheno-sdk/src/pheno/resilience/`

**Savings**: 100-150 LOC

---

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
```bash
# Create base modules in pheno-sdk
pheno-sdk/src/pheno/
├── config/
│   ├── yaml_config.py          # BaseYamlAppSettings, YamlConfigLoader
│   └── env_override.py
├── infra/
│   ├── service_setup.py        # ServiceInfrastructure
│   └── lifecycle.py
└── ports/                      # NEW - Architecture standard
    ├── __init__.py
    ├── logging.py
    ├── config.py
    └── io.py
```

**Tasks**:
1. Extract common YAML config patterns → `pheno.config.yaml_config`
2. Consolidate kinfra setup → `pheno.infra.service_setup`
3. Define port interfaces → `pheno.ports.*`

**Testing**: Unit tests for each new module, verify existing functionality preserved

---

### Phase 2: Migration (Week 3-4)
```bash
# Update zen-mcp-server first (smallest)
zen-mcp-server/
├── settings/config.py          # Replace with pheno.config import (268→30 lines)
├── kinfra_setup.py             # Replace with pheno.infra import (13→5 lines)
└── server/factory.py           # Use pheno.mcp.server_factory

# Update router
router/
├── kinfra_setup.py             # Replace with pheno.infra import
└── router_core/compat/         # Remove - use pheno directly

# Update morph (most complex)
morph/
├── settings/config.py          # Replace with pheno.config import
├── kinfra_setup.py             # Replace with pheno.infra import
├── morph_core/domain/ports/    # Move interfaces to pheno.ports
└── morph_core/adapters/        # Migrate to pheno.adapters pattern
```

**Tasks**:
1. Create shims in old locations pointing to pheno-sdk
2. Add deprecation warnings
3. Update all imports
4. Run existing test suites

---

### Phase 3: Consolidation (Week 5-6)
```bash
# Add remaining patterns
pheno-sdk/src/pheno/
├── logging/unified.py          # Consolidate logging patterns
├── mcp/server_factory.py       # MCP server lifecycle
├── cli/args.py                 # Standard argument parsing
└── resilience/                 # Retry, circuit breaker, timeout
```

**Tasks**:
1. Extract logging patterns
2. Create server factory
3. Build standard CLI parser
4. Add resilience utilities

---

### Phase 4: Cleanup (Week 7-8)
```bash
# Remove deprecated code
- Delete old config files from all projects
- Remove shims
- Clean up unused imports
- Update documentation
```

**Tasks**:
1. Remove all deprecated shims
2. Update README in each project
3. Write migration guide
4. Create examples

---

## Migration Example

### Before (zen-mcp-server/settings/config.py - 268 lines)
```python
class YamlAppSettings(BaseModel):
    app_name: str = Field(default="zen-mcp-server")
    version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    server_host: str = Field(default="localhost")
    server_port: int = Field(default=8000)
    # ... 30 more fields

class YamlSecrets(BaseModel):
    api_keys_openrouter: str | None = None
    api_keys_anthropic: str | None = None
    # ... 20 more fields

class YamlSettings:
    _instance = None

    def __init__(self):
        # 50 lines of YAML loading logic
        pass

    def _load_config(self) -> YamlAppSettings:
        # 50 lines of config parsing
        pass

    def _load_secrets(self) -> YamlSecrets:
        # 50 lines of secret loading
        pass

    @classmethod
    def get_instance(cls):
        # Singleton pattern
        pass

# Global instance
settings = YamlSettings.get_instance()
```

### After (zen-mcp-server/settings/config.py - ~30 lines)
```python
from pheno.config import BaseYamlAppSettings, BaseYamlSecrets, YamlConfigLoader

class ZenAppSettings(BaseYamlAppSettings):
    # Only zen-specific fields (app_name already has default)
    app_name: str = "zen-mcp-server"
    # All other fields inherited from BaseYamlAppSettings

class ZenSecrets(BaseYamlSecrets):
    # Only zen-specific secrets
    # Common API keys inherited from BaseYamlSecrets
    pass

# One-liner to load everything
settings = YamlConfigLoader(
    app_settings_class=ZenAppSettings,
    secrets_class=ZenSecrets
).load()
```

**Reduction**: 268 → 30 lines = **238 lines saved**

---

## Testing Strategy

### Unit Tests
```python
# pheno-sdk/tests/config/test_yaml_config.py
def test_yaml_config_loader():
    loader = YamlConfigLoader(BaseYamlAppSettings)
    settings = loader.load()
    assert settings.app_name == "test-app"

def test_config_inheritance():
    class CustomSettings(BaseYamlAppSettings):
        custom_field: str = "custom"

    loader = YamlConfigLoader(CustomSettings)
    settings = loader.load()
    assert settings.custom_field == "custom"
    assert hasattr(settings, "version")  # Inherited
```

### Integration Tests
```python
# zen-mcp-server/tests/test_config_integration.py
def test_config_loads_correctly():
    from settings.config import settings
    assert settings.app.app_name == "zen-mcp-server"
    assert settings.secrets.api_keys_openrouter is not None
```

### Migration Tests
```bash
# Run existing test suites for each project
cd zen-mcp-server && pytest
cd router && pytest
cd morph && pytest

# All tests must pass after migration
```

---

## Success Metrics

### Code Reduction
- **Target**: 1,850-2,300 LOC removed
- **Measure**: Run `cloc` before/after on each project
- **Goal**: >80% of target achieved

### Consistency
- **Target**: All 3 projects using same patterns
- **Measure**: Code review checklist
- **Goal**: 100% standardization for consolidated patterns

### Maintainability
- **Target**: Single source of truth for common code
- **Measure**: Count of duplicate functions/classes
- **Goal**: 0 duplicates for consolidated patterns

### New Project Bootstrap
- **Target**: Can create new MCP server in <100 LOC
- **Measure**: Create example skeleton project
- **Goal**: Functional server with logging, config, infra in <100 LOC

### Test Coverage
- **Target**: >90% coverage for pheno-sdk shared code
- **Measure**: pytest --cov
- **Goal**: All new modules have high coverage

---

## Risk Mitigation

### Low Risk
- ✅ YAML Config - Pure data, easy to test
- ✅ CLI Args - Well-defined interface
- ✅ KInfra Setup - Already abstracted

### Medium Risk
- ⚠️ Logging - Need flexible interface for all use cases
- ⚠️ Server Factory - Different middleware needs per project

**Mitigation**:
- Extensive testing
- Incremental rollout (zen → router → morph)
- Keep old code as fallback initially

### High Risk
- ⚠️ Ports/Adapters - Architecture change for some projects

**Mitigation**:
- Optional adoption
- Provide both old and new patterns
- Detailed migration guide

---

## Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Phase 1: Foundation | 2 weeks | YAML config, kinfra, ports in pheno-sdk |
| Phase 2: Migration | 2 weeks | All 3 projects using Phase 1 modules |
| Phase 3: Consolidation | 2 weeks | Logging, server factory, CLI added |
| Phase 4: Cleanup | 2 weeks | Deprecated code removed, docs updated |
| **Total** | **8 weeks** | **Complete consolidation** |

---

## Next Steps

### Immediate (This Week)
1. ✅ **Review this plan** - Get team approval
2. 📝 **Create pheno-sdk branch** - `feat/consolidation`
3. 🔧 **Start with YAML Config** - Lowest risk, highest duplication
4. ✅ **Write unit tests** - Test-driven development
5. 📚 **Document migration path** - Clear examples

### Week 1 Focus
```bash
# Day 1-2: YAML Config
- Extract BaseYamlAppSettings from morph/zen
- Create YamlConfigLoader with tests
- Test with zen-mcp-server

# Day 3-4: KInfra Setup
- Extract ServiceInfrastructure from morph
- Add port allocation, tunneling
- Test with all 3 projects

# Day 5: Ports Pattern
- Define port interfaces
- Document pattern
- Create example adapter
```

---

## Files to Create

### Priority 1 (Week 1-2)
```
pheno-sdk/src/pheno/config/yaml_config.py
pheno-sdk/src/pheno/config/env_override.py
pheno-sdk/src/pheno/infra/service_setup.py
pheno-sdk/src/pheno/infra/lifecycle.py
pheno-sdk/src/pheno/ports/__init__.py
pheno-sdk/src/pheno/ports/logging.py
pheno-sdk/src/pheno/ports/config.py
pheno-sdk/src/pheno/ports/io.py
pheno-sdk/tests/config/test_yaml_config.py
pheno-sdk/tests/infra/test_service_setup.py
```

### Priority 2 (Week 3-4)
```
pheno-sdk/src/pheno/logging/unified.py
pheno-sdk/src/pheno/mcp/server_factory.py
pheno-sdk/src/pheno/mcp/middleware.py
pheno-sdk/src/pheno/adapters/__init__.py
pheno-sdk/src/pheno/adapters/logging_adapter.py
pheno-sdk/tests/logging/test_unified.py
pheno-sdk/tests/mcp/test_server_factory.py
```

### Priority 3 (Week 5-6)
```
pheno-sdk/src/pheno/cli/args.py
pheno-sdk/src/pheno/resilience/__init__.py
pheno-sdk/src/pheno/resilience/retry.py
pheno-sdk/src/pheno/resilience/circuit_breaker.py
pheno-sdk/tests/cli/test_args.py
pheno-sdk/tests/resilience/test_retry.py
```

---

## Documentation to Create

### For Each Module
```
# Module README
- Purpose and motivation
- API reference
- Usage examples
- Migration guide from old pattern

# Example:
pheno-sdk/docs/config/yaml_config.md
pheno-sdk/docs/infra/service_setup.md
pheno-sdk/docs/migration/from_duplicate_config.md
```

### Project Updates
```
zen-mcp-server/docs/MIGRATION_TO_PHENO_SDK.md
router/docs/MIGRATION_TO_PHENO_SDK.md
morph/docs/MIGRATION_TO_PHENO_SDK.md
```

---

## Summary

This plan consolidates **1,850-2,300 lines** of duplicate code across zen-mcp-server, router, and morph into pheno-sdk, providing:

- ✅ **Reduced duplication** - Single source of truth
- ✅ **Faster development** - New projects bootstrap in <100 LOC
- ✅ **Better maintainability** - Bug fixes benefit all projects
- ✅ **Architectural consistency** - All projects follow same patterns
- ✅ **Lower risk** - Incremental rollout with fallbacks

**Ready to execute Phase 1 starting with YAML Configuration consolidation.**

---

*Report prepared by*: Pattern Analysis System
*Date*: 2025-10-30
*Status*: 🟢 READY TO EXECUTE
*Next Step*: Create `pheno-sdk/src/pheno/config/yaml_config.py`
