# Quick Reference: crun → pheno-sdk Migration

**One-page guide for developers**

---

## 🎯 What to Use Instead

| Instead of... | Use... | Module |
|---------------|--------|--------|
| `crun.shared.exceptions.*` | `pheno.exceptions.*` | Error handling |
| `crun.shared.logger` | `pheno.logging.get_logger()` | Logging |
| `crun.config.loader` | `pheno.config.ConfigManager` | Configuration |
| `crun.shared.console` | `pheno.logging.console` | Console output |
| Custom retry decorators | `pheno.resilience.with_retry()` | Retry logic |
| Custom metrics | `pheno.observability.MetricsCollector` | Metrics |
| `crun.cli.*` | `pheno.cli.*` | CLI framework |
| `crun.execution.*` | `pheno.workflow.*` | Workflows |
| `crun.shared.async_utils` | `pheno.shared.async_utils` | Async utilities |

---

## 📦 Import Cheat Sheet

### Error Handling
```python
# OLD
from crun.shared.exceptions import CrunError, ValidationError

# NEW
from pheno.exceptions import DomainError, ValidationError
from pheno.resilience import with_retry, with_circuit_breaker
```

### Logging
```python
# OLD
from crun.shared.logger import CrunLogger
logger = CrunLogger(__name__)

# NEW
from pheno.logging import get_logger
logger = get_logger(__name__)
```

### Configuration
```python
# OLD
from crun.config.loader import ConfigLoader
config = ConfigLoader("config.yaml").load()

# NEW
from pheno.config import ConfigManager, BaseConfig
config = ConfigManager.load(MyConfig, config_file="config.yaml")
```

### Console Output
```python
# OLD
from crun.shared.console import console
console.print("[green]Success[/green]")

# NEW
from pheno.logging import print_success, print_error, print_info
print_success("Success")
```

### Metrics
```python
# OLD
from crun.shared.metrics import MetricsCollector
metrics = MetricsCollector()

# NEW
from pheno.observability import MetricsCollector
metrics = MetricsCollector(service_name="crun")
```

---

## 🔧 Common Patterns

### Pattern 1: Error Handling with Retry
```python
from pheno.exceptions import ValidationError
from pheno.resilience import with_retry, RetryConfig

@with_retry(RetryConfig(max_attempts=3))
async def my_function():
    if not valid:
        raise ValidationError("Invalid input")
```

### Pattern 2: Structured Logging
```python
from pheno.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing", extra={"user_id": 123, "duration_ms": 45})
```

### Pattern 3: Type-Safe Configuration
```python
from pheno.config import BaseConfig
from pydantic import Field

class MyConfig(BaseConfig):
    max_workers: int = Field(default=4, ge=1)
    timeout: int = Field(default=300)
    
    class Config:
        env_prefix = "CRUN_"
```

### Pattern 4: Metrics Collection
```python
from pheno.observability import MetricsCollector

metrics = MetricsCollector(service_name="crun")
metrics.increment("requests_total", labels={"endpoint": "/api"})

with metrics.timer("operation_duration"):
    # Operation logic
    pass
```

### Pattern 5: CLI Command
```python
from pheno.cli import create_cli_app, command

app = create_cli_app("crun")

@command(app)
def execute(plan: str, workers: int = 4):
    """Execute a plan."""
    # Command logic
    pass
```

---

## 🚀 Quick Start

### Step 1: Install pheno-sdk
```bash
# Already installed as sibling repo
cd ../pheno-sdk
uv sync
```

### Step 2: Update Imports
```bash
# Replace error imports
find crun/ -name "*.py" -exec sed -i '' \
  's/from crun.shared.exceptions/from pheno.exceptions/g' {} \;

# Replace logger imports
find crun/ -name "*.py" -exec sed -i '' \
  's/from crun.shared.logger/from pheno.logging/g' {} \;
```

### Step 3: Update Code
```python
# Before
from crun.shared.exceptions import ValidationError
from crun.shared.logger import CrunLogger

logger = CrunLogger(__name__)

def validate(data):
    if not data:
        raise ValidationError("Invalid data")
    logger.info("Validated")

# After
from pheno.exceptions import ValidationError
from pheno.logging import get_logger

logger = get_logger(__name__)

def validate(data):
    if not data:
        raise ValidationError("Invalid data")
    logger.info("Validated", extra={"data_size": len(data)})
```

### Step 4: Test
```bash
pytest crun/tests/ -v
```

---

## 📋 Migration Checklist

### Phase 1: Quick Wins (1-2 weeks)
- [ ] Replace `crun.shared.exceptions` with `pheno.exceptions`
- [ ] Replace `crun.shared.logger` with `pheno.logging`
- [ ] Replace `crun.config` with `pheno.config`
- [ ] Replace retry logic with `pheno.resilience`
- [ ] Replace metrics with `pheno.observability`
- [ ] Test thoroughly

### Phase 2: Core Infrastructure (3-4 weeks)
- [ ] Migrate CLI to `pheno.cli`
- [ ] Move shared utilities to `pheno.shared`
- [ ] Update documentation
- [ ] Test thoroughly

### Phase 3: Advanced (4-6 weeks)
- [ ] Migrate execution to `pheno.workflow`
- [ ] Migrate UI to `pheno.ui`
- [ ] Test thoroughly

---

## 🔍 Finding What to Migrate

### Find Custom Exceptions
```bash
grep -r "class.*Error.*Exception" crun/
```

### Find Logger Usage
```bash
grep -r "logger\|logging\.getLogger" crun/
```

### Find Config Loading
```bash
grep -r "load_config\|ConfigLoader" crun/
```

### Find Retry Logic
```bash
grep -r "@retry\|tenacity\|backoff" crun/
```

### Find Metrics
```bash
grep -r "metrics\|counter\|gauge" crun/
```

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest crun/tests/ -v

# Specific module
pytest crun/tests/test_exceptions.py -v

# With coverage
pytest crun/tests/ --cov=crun --cov-report=html
```

### Verify Behavior
```bash
# Before migration
python -m crun execute plan.json > before.txt

# After migration
python -m crun execute plan.json > after.txt

# Compare
diff before.txt after.txt
```

---

## 📚 Documentation

### Key Documents
1. **CODE_CONSOLIDATION_ANALYSIS.md** - Full analysis
2. **MIGRATION_PLAN_PHASE1.md** - Detailed Phase 1 plan
3. **MIGRATION_CODE_EXAMPLES.md** - Before/after examples
4. **CONSOLIDATION_SUMMARY.md** - Executive summary
5. **QUICK_REFERENCE.md** - This document

### pheno-sdk Docs
- `pheno-sdk/docs/` - Full documentation
- `pheno-sdk/examples/` - Usage examples
- `zen-mcp-server/` - Reference implementation

---

## 🆘 Troubleshooting

### Import Errors
```python
# Error: ModuleNotFoundError: No module named 'pheno'
# Solution: Ensure pheno-sdk is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:../pheno-sdk/src"
```

### Type Errors
```python
# Error: Type mismatch
# Solution: Update type hints
from pheno.exceptions import ValidationError  # Not crun.shared.exceptions
```

### Test Failures
```bash
# Error: Tests failing after migration
# Solution: Update test fixtures
from pheno.testing import create_test_client
```

---

## 💡 Tips & Best Practices

### Do's ✅
- ✅ Migrate one module at a time
- ✅ Test after each change
- ✅ Keep rollback plans
- ✅ Update documentation
- ✅ Use type hints
- ✅ Add structured logging

### Don'ts ❌
- ❌ Don't mix old and new patterns
- ❌ Don't skip testing
- ❌ Don't forget to update imports
- ❌ Don't ignore type errors
- ❌ Don't remove old code immediately

---

## 🎯 Success Metrics

### Code Quality
- [ ] Reduced duplication
- [ ] Consistent patterns
- [ ] Better type safety
- [ ] Improved error handling

### Observability
- [ ] Structured logging
- [ ] Correlation IDs
- [ ] Metrics collection
- [ ] Better debugging

### Maintainability
- [ ] Single source of truth
- [ ] Reusable components
- [ ] Clear patterns
- [ ] Good documentation

---

## 📞 Getting Help

### Questions?
1. Check pheno-sdk docs: `pheno-sdk/docs/`
2. Look at examples: `pheno-sdk/examples/`
3. Reference zen-mcp-server implementation
4. Ask the team

### Common Issues
- **Import errors:** Check PYTHONPATH
- **Type errors:** Update type hints
- **Test failures:** Update fixtures
- **Performance issues:** Profile and optimize

---

## 🎉 Quick Wins

### Easiest Migrations (Start Here)
1. **Error Handling** (1-2 days)
   - Replace exceptions
   - Add retry logic
   - High impact, low risk

2. **Logging** (3-4 days)
   - Replace logger
   - Add structured logging
   - High impact, low risk

3. **Configuration** (2-3 days)
   - Replace config loader
   - Add type safety
   - High impact, medium risk

---

## 📊 Expected Results

### After Phase 1
- **Code Reduction:** 15-20%
- **Consistency:** +100%
- **Observability:** +200%
- **Type Safety:** +100%

### After All Phases
- **Code Reduction:** 35-40%
- **Maintainability:** +50%
- **Development Speed:** +30%
- **Bug Reduction:** -40%

---

## 🚦 Status Indicators

### Ready to Migrate ✅
- Error handling
- Logging
- Configuration
- Retry logic
- Metrics

### Needs Planning 🟡
- CLI framework
- Execution engines
- UI components

### Future Work 🔵
- Agent patterns
- Advanced workflows
- Custom integrations

---

## 📅 Timeline

| Phase | Duration | Focus | Status |
|-------|----------|-------|--------|
| Phase 1 | 1-2 weeks | Quick wins | Ready |
| Phase 2 | 3-4 weeks | Core infrastructure | Planning |
| Phase 3 | 4-6 weeks | Advanced patterns | Future |

---

## 🎯 Next Action

**Start with error handling migration:**
1. Review `MIGRATION_CODE_EXAMPLES.md`
2. Create feature branch
3. Replace `crun.shared.exceptions` with `pheno.exceptions`
4. Test thoroughly
5. Commit and move to next migration

**Estimated Time:** 1-2 days  
**Risk Level:** Low  
**Impact:** High

---

**Remember:** Migrate incrementally, test thoroughly, and keep rollback plans!

