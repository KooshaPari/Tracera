# Ultra-Strict Python Research Summary

## Overview

Research on modern ultra-strict Python project templates and best practices for 2025, inspired by TypeScript's `--strict` mode.

## Key Resources Analyzed

### 1. **PyStrict** (Ranteck/PyStrict-strict-python)
- **GitHub**: https://github.com/Ranteck/PyStrict-strict-python
- **Stars**: 96
- **Focus**: Maximum strictness for Python projects
- **Philosophy**: Production-grade quality from day one

#### Core Features:
- **Python**: 3.12+
- **Package Manager**: UV (ultra-fast)
- **Type Checker**: basedpyright (strict mode)
- **Linter/Formatter**: ruff (with many plugins)
- **Task Runner**: poethepoet
- **Code Quality**: radon, skylos
- **Testing**: pytest + coverage (80% minimum)
- **Config**: pydantic-settings, typing-extensions

#### Strictness Philosophy:
- No implicit Any (unknown/untyped values are errors)
- Required type annotations on all functions
- Unused imports/variables/functions are errors
- Optional values (None) must be handled explicitly
- Security checks via flake8-bandit rules
- 80% coverage threshold enforced

### 2. **Python Repo Template** (GiovanniGiacometti)
- **GitHub**: https://github.com/GiovanniGiacometti/python-repo-template
- **Stars**: 139
- **Focus**: Ultimate 2025 Python repository template

#### Core Features:
- **Package Manager**: UV
- **Command Runner**: Just (modern, powerful)
- **Linter/Formatter**: Ruff
- **Type Checker**: Mypy
- **Testing**: Pytest with fixtures
- **Logging**: Loguru
- **Infrastructure**: Pre-commit hooks, Docker, GitHub Actions

#### Unique Aspects:
- Uses Just for command runner (more powerful than Make)
- Multi-stage Docker builds with distroless images
- GitHub Actions CI/CD pipeline
- Pre-commit hooks integration

### 3. **Cookiecutter-UV** (fpgmaas)
- **GitHub**: https://github.com/fpgmaas/cookiecutter-uv
- **Stars**: 1.1k
- **Focus**: Modern cookiecutter template for UV projects

#### Features:
- Supports src and flat layout
- CI/CD with GitHub Actions
- Code quality: ruff, mypy/ty, deptry
- PyPI publishing automation
- pytest + codecov
- MkDocs documentation
- tox-uv for multi-version testing
- Docker/Podman containerization
- VSCode devcontainers

## Anti-Slop Patterns (LLM Prevention)

### 1. Pydantic Models for All IO
```python
# ❌ BAD: Raw dict
def process_user_data(data: dict) -> None:
    name = data["name"]  # Could fail, no validation

# ✅ GOOD: Pydantic model
class UserData(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=150)

def process_user_data(data: dict) -> None:
    user = UserData.model_validate(data)
```

### 2. Dataframe Schemas with Pandera
```python
import pandera as pa

class SalesSchema(pa.DataFrameModel):
    product_id: int = pa.Field(gt=0)
    revenue: float = pa.Field(ge=0)
```

### 3. Avoid Boolean Traps
```python
# ❌ BAD: What does True mean?
send_email(user, True, False)

# ✅ GOOD: Use enums or keyword-only args
def send_email(user: User, *, format: EmailFormat, async_send: bool = False) -> None: ...
```

### 4. Keep Functions Simple
- Max complexity: 10 (McCabe)
- Max nested blocks: 3
- Use early returns + helper functions

### 5. No Bare Excepts
```python
# ❌ BAD: Hides all errors
try:
    risky_operation()
except Exception:
    pass

# ✅ GOOD: Catch specific exceptions
try:
    risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Expected error: {e}")
    raise
```

## Tool Comparison

| Tool | Purpose | Speed | Notes |
|------|---------|-------|-------|
| UV | Package Manager | 10-100x faster | Replaces pip, poetry |
| Ruff | Lint/Format | 10-100x faster | Replaces black/flake8/isort |
| basedpyright | Type Checker | Fast | Strict mode, TypeScript-like |
| mypy | Type Checker | Slower | More mature, configurable |
| Just | Task Runner | Modern | Better than Make |
| poethepoet | Task Runner | Python-based | Alternative to Just |

## Recommended Stack for TraceRTM

### Build & Dependencies
- ✅ UV (already using)
- ✅ Hatchling (already using)
- ✅ pydantic-settings (already using)

### Code Quality
- ✅ Ruff (already using)
- ✅ MyPy strict (already using)
- ✅ Add: basedpyright for even stricter checking
- ✅ Add: poethepoet for task automation

### Testing & Coverage
- ✅ pytest (already using)
- ✅ coverage (already using)
- ✅ Add: 80% minimum coverage threshold

### Data Validation
- ✅ Pydantic (already using)
- ✅ Add: Pandera for DataFrame validation (if needed)

### Anti-Slop Prevention
- ✅ Enforce Pydantic models for all IO
- ✅ No boolean traps (FBT rule in ruff)
- ✅ Function complexity limits
- ✅ No bare excepts (BLE rule in ruff)

## Next Steps for TraceRTM

1. **Add basedpyright** for ultra-strict type checking
2. **Add poethepoet** for task automation
3. **Implement 80% coverage threshold**
4. **Add Pandera** for DataFrame validation (if using pandas/polars)
5. **Enforce anti-slop patterns** in code review
6. **Create task runner** for common operations
7. **Document strictness philosophy** for team

## References

- PyStrict: https://github.com/Ranteck/PyStrict-strict-python
- Python Repo Template: https://github.com/GiovanniGiacometti/python-repo-template
- Cookiecutter-UV: https://github.com/fpgmaas/cookiecutter-uv
- UV Docs: https://docs.astral.sh/uv/
- Ruff Docs: https://docs.astral.sh/ruff/
- basedpyright: https://github.com/detachhead/basedpyright
- Pydantic: https://docs.pydantic.dev/
- Pandera: https://pandera.readthedocs.io/

