# Phase 1 Migration Plan: Quick Wins

**Duration:** 1-2 weeks  
**Goal:** Eliminate obvious duplication with minimal risk  
**Expected Code Reduction:** 15-20%

---

## Overview

Phase 1 focuses on three high-impact, low-risk migrations:
1. Error Handling (1-2 days)
2. Logging & Observability (3-4 days)
3. Configuration Management (2-3 days)

These migrations provide immediate benefits with minimal disruption.

---

## 1. Error Handling Migration

### Objective
Replace custom error handling in crun with pheno-sdk's battle-tested error framework.

### Current State

**crun has:**
- `crun/shared/exceptions.py` - Custom exception classes
- Scattered retry logic across modules
- Inconsistent error handling patterns

**pheno-sdk provides:**
- `pheno.exceptions` - Rich exception taxonomy
- `pheno.resilience` - Circuit breaker, retry, timeout patterns
- Consistent error context and reporting

### Migration Steps

#### Step 1.1: Audit Current Error Usage (2 hours)
```bash
# Find all custom exceptions
grep -r "class.*Error.*Exception" crun/

# Find all retry patterns
grep -r "@retry\|tenacity\|backoff" crun/

# Find all error handling
grep -r "try:\|except\|raise" crun/ | wc -l
```

**Deliverable:** Error usage inventory

#### Step 1.2: Map Exceptions (2 hours)
Create mapping from crun exceptions to pheno exceptions:

```python
# MAPPING.md
crun.shared.exceptions.CrunError -> pheno.exceptions.DomainError
crun.shared.exceptions.ValidationError -> pheno.exceptions.ValidationError
crun.shared.exceptions.ConfigError -> pheno.exceptions.ConfigurationError
crun.shared.exceptions.ExecutionError -> pheno.exceptions.ExecutionError
```

**Deliverable:** Exception mapping document

#### Step 1.3: Replace Exception Classes (4 hours)
```python
# Before: crun/shared/exceptions.py
class CrunError(Exception):
    """Base exception for crun."""
    pass

class ValidationError(CrunError):
    """Validation error."""
    pass

# After: Use pheno.exceptions
from pheno.exceptions import DomainError, ValidationError

# Update all imports
find crun/ -name "*.py" -exec sed -i '' \
  's/from crun.shared.exceptions import/from pheno.exceptions import/g' {} \;
```

**Deliverable:** Updated imports across codebase

#### Step 1.4: Adopt Resilience Patterns (4 hours)
```python
# Before: Custom retry
def retry_on_error(func):
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception:
                if i == 2:
                    raise
                time.sleep(2 ** i)
    return wrapper

# After: Use pheno.resilience
from pheno.resilience import with_retry, RetryConfig

@with_retry(RetryConfig(max_attempts=3, backoff_multiplier=2))
async def my_function():
    # Function logic
    pass
```

**Deliverable:** Standardized retry patterns

#### Step 1.5: Testing (4 hours)
- Run full test suite
- Verify error messages unchanged
- Test retry behavior
- Validate circuit breaker patterns

**Deliverable:** Passing tests with new error handling

### Success Criteria
- [ ] All custom exceptions replaced with pheno.exceptions
- [ ] All retry logic uses pheno.resilience
- [ ] All tests passing
- [ ] No behavioral changes
- [ ] Code reduction: ~5%

### Rollback Plan
- Keep old exceptions.py as exceptions_legacy.py
- Feature flag for new error handling
- Easy revert via git

---

## 2. Logging & Observability Migration

### Objective
Migrate to pheno-sdk's structured logging and observability framework.

### Current State

**crun has:**
- `crun/shared/logger.py` - Custom logger
- `crun/shared/console.py` - Console utilities
- `crun/shared/observability.py` - Basic metrics
- `crun/shared/metrics_models.py` - Metrics models

**pheno-sdk provides:**
- `pheno.logging` - Structured logging with rich context
- `pheno.observability` - OpenTelemetry, metrics, dashboards
- `pheno.correlation_id` - Trace propagation
- Comprehensive monitoring framework

### Migration Steps

#### Step 2.1: Audit Current Logging (2 hours)
```bash
# Find all logger usage
grep -r "logger\|logging\|log\." crun/ | wc -l

# Find all console usage
grep -r "console\|print\|rich" crun/ | wc -l

# Find all metrics
grep -r "metrics\|counter\|gauge" crun/ | wc -l
```

**Deliverable:** Logging usage inventory

#### Step 2.2: Setup pheno.logging (3 hours)
```python
# crun/logging_config.py (NEW)
from pheno.logging import configure_logging, get_logger
from pheno.observability import init_otel

def setup_logging(level: str = "INFO"):
    """Configure logging for crun using pheno-sdk."""
    configure_logging(
        level=level,
        service_name="crun",
        environment="production",
        enable_json=True,
        enable_correlation_id=True
    )
    
    # Initialize OpenTelemetry
    init_otel(
        service_name="crun",
        enable_traces=True,
        enable_metrics=True
    )

# Usage in main
from crun.logging_config import setup_logging
setup_logging()
```

**Deliverable:** Centralized logging configuration

#### Step 2.3: Replace Logger Instances (6 hours)
```python
# Before: crun/shared/logger.py
import logging
logger = logging.getLogger(__name__)

# After: Use pheno.logging
from pheno.logging import get_logger
logger = get_logger(__name__)

# Update all files
find crun/ -name "*.py" -exec sed -i '' \
  's/import logging/from pheno.logging import get_logger/g' {} \;
find crun/ -name "*.py" -exec sed -i '' \
  's/logging.getLogger(__name__)/get_logger(__name__)/g' {} \;
```

**Deliverable:** Updated logger usage

#### Step 2.4: Migrate Console Utilities (4 hours)
```python
# Before: crun/shared/console.py
from rich.console import Console
console = Console()

# After: Use pheno.logging console utilities
from pheno.logging import console, print_status, print_error, print_success

# Replace all console usage
console.print("Info") -> print_status("Info")
console.print("[red]Error[/red]") -> print_error("Error")
console.print("[green]Success[/green]") -> print_success("Success")
```

**Deliverable:** Standardized console output

#### Step 2.5: Add Correlation IDs (3 hours)
```python
# Add correlation ID middleware
from pheno.correlation_id import correlation_id_middleware

# In FastAPI app
app.add_middleware(correlation_id_middleware)

# In async functions
from pheno.correlation_id import set_correlation_id, get_correlation_id

async def my_function():
    correlation_id = get_correlation_id()
    logger.info("Processing request", extra={"correlation_id": correlation_id})
```

**Deliverable:** Trace propagation enabled

#### Step 2.6: Setup Metrics (4 hours)
```python
# Before: Custom metrics
class Metrics:
    def __init__(self):
        self.counters = {}
    
    def increment(self, name: str):
        self.counters[name] = self.counters.get(name, 0) + 1

# After: Use pheno.observability
from pheno.observability import MetricsCollector

metrics = MetricsCollector(service_name="crun")
metrics.increment("requests_total", labels={"endpoint": "/api/v1"})
metrics.gauge("active_connections", 42)
metrics.histogram("request_duration", 0.123)
```

**Deliverable:** Standardized metrics collection

#### Step 2.7: Testing (4 hours)
- Verify log output format
- Test correlation ID propagation
- Validate metrics collection
- Check OpenTelemetry integration

**Deliverable:** Passing tests with new logging

### Success Criteria
- [ ] All logging uses pheno.logging
- [ ] Correlation IDs propagate correctly
- [ ] Metrics collected via pheno.observability
- [ ] OpenTelemetry enabled
- [ ] All tests passing
- [ ] Code reduction: ~7%

### Rollback Plan
- Keep old logger.py as logger_legacy.py
- Feature flag for new logging
- Easy revert via environment variable

---

## 3. Configuration Management Migration

### Objective
Replace custom configuration loading with pheno-sdk's configuration framework.

### Current State

**crun has:**
- `crun/config/loader.py` - YAML/JSON loading
- `crun/config/manager.py` - Config management
- `crun/config/validator.py` - Validation logic
- `crun/config/settings_loader.py` - Settings loading

**pheno-sdk provides:**
- `pheno.config` - Comprehensive config framework
- Environment variable binding
- Validation with Pydantic
- Config hot-reloading
- Multi-environment support

### Migration Steps

#### Step 3.1: Audit Current Config (2 hours)
```bash
# Find all config files
find crun/ -name "*.yaml" -o -name "*.yml" -o -name "*.json"

# Find all config loading
grep -r "load_config\|ConfigLoader\|settings" crun/

# Find all environment variables
grep -r "os.getenv\|os.environ" crun/
```

**Deliverable:** Configuration inventory

#### Step 3.2: Define Config Schema (3 hours)
```python
# crun/config/schema.py (NEW)
from pheno.config import BaseConfig
from pydantic import Field

class CrunConfig(BaseConfig):
    """Main configuration for crun."""
    
    # Execution settings
    max_workers: int = Field(default=4, ge=1, le=32)
    timeout: int = Field(default=300, ge=1)
    
    # Logging settings
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Database settings
    database_url: str = Field(default="sqlite:///crun.db")
    
    # Feature flags
    enable_parallel: bool = Field(default=True)
    enable_caching: bool = Field(default=True)
    
    class Config:
        env_prefix = "CRUN_"
        env_file = ".env"
```

**Deliverable:** Typed configuration schema

#### Step 3.3: Replace Config Loading (4 hours)
```python
# Before: crun/config/loader.py
def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

# After: Use pheno.config
from pheno.config import ConfigManager
from crun.config.schema import CrunConfig

# Load config
config = ConfigManager.load(
    CrunConfig,
    config_file="config.yaml",
    env_file=".env"
)

# Access config
max_workers = config.max_workers
log_level = config.log_level
```

**Deliverable:** Standardized config loading

#### Step 3.4: Update All Config Usage (5 hours)
```python
# Before: Direct dict access
config = load_config("config.yaml")
workers = config.get("max_workers", 4)

# After: Typed access
from crun.config import get_config
config = get_config()
workers = config.max_workers  # Type-safe, validated
```

**Deliverable:** Type-safe configuration access

#### Step 3.5: Environment Variable Migration (3 hours)
```python
# Before: Manual env var handling
import os
max_workers = int(os.getenv("MAX_WORKERS", "4"))

# After: Automatic via pheno.config
# Just define in schema with env_prefix
class CrunConfig(BaseConfig):
    max_workers: int = Field(default=4)
    
    class Config:
        env_prefix = "CRUN_"  # Reads CRUN_MAX_WORKERS

# Usage
config = get_config()
max_workers = config.max_workers  # Automatically from env or config file
```

**Deliverable:** Automatic environment variable handling

#### Step 3.6: Testing (3 hours)
- Test config loading from files
- Test environment variable override
- Test validation
- Test default values

**Deliverable:** Passing tests with new config

### Success Criteria
- [ ] All config loading uses pheno.config
- [ ] Type-safe configuration access
- [ ] Environment variables handled automatically
- [ ] Validation working correctly
- [ ] All tests passing
- [ ] Code reduction: ~8%

### Rollback Plan
- Keep old config/ as config_legacy/
- Feature flag for new config system
- Easy revert via import changes

---

## Phase 1 Timeline

| Week | Days | Task | Owner | Status |
|------|------|------|-------|--------|
| 1 | Mon-Tue | Error Handling Migration | TBD | Not Started |
| 1 | Wed-Fri | Logging Migration (Part 1) | TBD | Not Started |
| 2 | Mon-Tue | Logging Migration (Part 2) | TBD | Not Started |
| 2 | Wed-Fri | Configuration Migration | TBD | Not Started |

---

## Testing Strategy

### Unit Tests
- Test each migration in isolation
- Verify behavior unchanged
- Check error messages
- Validate configuration

### Integration Tests
- Test interactions between migrated components
- Verify end-to-end workflows
- Check logging output
- Validate metrics collection

### Performance Tests
- Benchmark before and after
- Ensure no performance degradation
- Monitor memory usage
- Check startup time

---

## Monitoring & Validation

### Metrics to Track
- Code lines removed
- Test coverage
- Performance benchmarks
- Error rates
- Log volume

### Success Indicators
- ✅ 15-20% code reduction achieved
- ✅ All tests passing
- ✅ No performance degradation
- ✅ Improved consistency
- ✅ Better observability

---

## Risk Mitigation

### Low Risk Items
- Error handling (well-tested)
- Logging (drop-in replacement)

### Medium Risk Items
- Configuration (wide impact)

### Mitigation Strategies
1. **Feature Flags:** Enable gradual rollout
2. **Comprehensive Testing:** Catch issues early
3. **Rollback Plan:** Quick revert if needed
4. **Monitoring:** Track metrics closely
5. **Documentation:** Clear migration guides

---

## Next Steps

1. **Review this plan** with the team
2. **Assign owners** for each migration
3. **Set up tracking** (Jira/GitHub issues)
4. **Create feature branches**
5. **Begin with error handling** (lowest risk)

---

## Appendix: Useful Commands

### Find and Replace
```bash
# Replace imports
find crun/ -name "*.py" -exec sed -i '' \
  's/from crun.shared.exceptions/from pheno.exceptions/g' {} \;

# Replace logger
find crun/ -name "*.py" -exec sed -i '' \
  's/logging.getLogger/get_logger/g' {} \;

# Replace config
find crun/ -name "*.py" -exec sed -i '' \
  's/load_config/ConfigManager.load/g' {} \;
```

### Testing
```bash
# Run tests
pytest crun/tests/ -v

# Run with coverage
pytest crun/tests/ --cov=crun --cov-report=html

# Run specific test
pytest crun/tests/test_exceptions.py -v
```

### Code Analysis
```bash
# Count lines of code
cloc crun/

# Find duplicates
jscpd crun/

# Check complexity
radon cc crun/ -a
```

---

## Conclusion

Phase 1 provides quick wins with minimal risk. By focusing on error handling, logging, and configuration, we can achieve 15-20% code reduction while improving consistency and maintainability.

**Recommendation:** Begin immediately with error handling migration.

