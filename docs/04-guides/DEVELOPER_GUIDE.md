# Developer Guide

Comprehensive guide for developing TraceRTM.

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files
# Add tests
# Update documentation
```

### 3. Run Quality Checks

```bash
# Format code
uv run poe format

# Lint code
uv run poe lint

# Type check
uv run poe type-check-strict

# Run tests
uv run poe test-cov

# Full pipeline
uv run poe all
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 5. Push and Create PR

```bash
git push origin feature/my-feature
# Create PR on GitHub
```

## Adding Features

### 1. Add Models

```python
# src/tracertm/models.py
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    """My model description."""
    
    id: int = Field(gt=0, description="Unique ID")
    name: str = Field(min_length=1, description="Name")
```

### 2. Add Services

```python
# src/tracertm/services/my_service.py
from loguru import logger

class MyService:
    """My service description."""
    
    def process(self, data: MyModel) -> Result:
        """Process data."""
        logger.info(f"Processing {data.id}")
        # Implementation
        return result
```

### 3. Add API Endpoints

```python
# src/tracertm/api/endpoints.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(data: MyModel) -> Result:
    """My endpoint description."""
    service = MyService()
    return service.process(data)
```

### 4. Add Tests

```python
# tests/test_my_feature.py
import pytest
from tracertm.models import MyModel
from tracertm.services import MyService

def test_my_service() -> None:
    """Test my service."""
    service = MyService()
    model = MyModel(id=1, name="Test")
    result = service.process(model)
    assert result is not None
```

### 5. Update Architecture

```yaml
# tach.yaml
modules:
  - name: my_module
    path: src/tracertm/my_module
    description: My module description

dependencies:
  my_module:
    - services
    - models
    - core
    - utils
```

## Testing

### Unit Tests

```bash
uv run poe test-unit
```

### Integration Tests

```bash
uv run poe test-integration
```

### Property-Based Tests

```bash
uv run poe test-property
```

### Coverage

```bash
uv run poe test-cov
# View: htmlcov/index.html
```

### Specific Test

```bash
pytest tests/test_models.py::test_name -vv
```

## Type Checking

### Ty (strict)

```bash
uv run ty check src/ --error-on-warning
```

### Fix Type Errors

```python
# Add type annotations
def my_function(x: int) -> str:
    return str(x)

# Use Optional for nullable values
from typing import Optional
def get_user(id: int) -> Optional[User]:
    return user if found else None

# Use Union for multiple types
from typing import Union
def process(data: Union[str, int]) -> str:
    return str(data)
```

## Logging

### Using Loguru

```python
from loguru import logger

# Debug
logger.debug("Debug message")

# Info
logger.info("Info message")

# Warning
logger.warning("Warning message")

# Error
logger.error("Error message")

# Critical
logger.critical("Critical message")

# With context
logger.bind(user_id=123).info("User action")
```

### Log Levels

- **DEBUG**: Detailed information
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

## Security

### Input Validation

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    """User input with validation."""
    
    email: str = Field(regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(min_length=8)
```

### SQL Injection Prevention

```python
# ✅ GOOD: Parameterized queries
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))

# ❌ BAD: String interpolation
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

### Error Handling

```python
# ✅ GOOD: Specific exceptions
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.error(f"User {user_id} not found")
    raise

# ❌ BAD: Bare except
try:
    user = get_user(user_id)
except:
    pass
```

## Performance

### Profiling

```bash
# Profile tests
pytest tests/ --profile

# Profile code
python -m cProfile -s cumtime script.py
```

### Optimization

```python
# ✅ GOOD: Efficient code
users = [u for u in users if u.active]

# ❌ BAD: Inefficient code
active_users = []
for u in users:
    if u.active:
        active_users.append(u)
```

## Documentation

### Docstrings

```python
def my_function(x: int, y: int) -> int:
    """Calculate sum of two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
        
    Raises:
        ValueError: If inputs are negative
    """
    if x < 0 or y < 0:
        raise ValueError("Inputs must be non-negative")
    return x + y
```

### Comments

```python
# ✅ GOOD: Explain why, not what
# Use binary search for O(log n) performance
result = binary_search(data, target)

# ❌ BAD: Obvious comments
# Add 1 to x
x = x + 1
```

## Debugging

### Print Debugging

```python
logger.debug(f"Variable: {variable}")
```

### Breakpoints

```python
import pdb; pdb.set_trace()
```

### IDE Debugging

- VS Code: F5 to debug
- PyCharm: Shift+F9 to debug

## Deployment

### Build

```bash
uv build
```

### Test Build

```bash
pip install dist/tracertm-*.whl
```

### Release

```bash
git tag v1.0.0
git push origin v1.0.0
# CI/CD handles release
```

## Resources

- Python: https://docs.python.org/3/
- Pydantic: https://docs.pydantic.dev/
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pytest: https://docs.pytest.org/
- Loguru: https://github.com/Delgan/loguru

## Getting Help

1. Check documentation
2. Search GitHub issues
3. Ask in team chat
4. Create GitHub issue

Happy coding! 🚀
