# Hexagonal Refactoring Patterns Guide

A comprehensive guide to analyzing, extracting, and validating hexagonal architecture patterns in Python codebases.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Refactoring Strategies](#refactoring-strategies)
5. [Code Analysis](#code-analysis)
6. [Code Extraction](#code-extraction)
7. [Architecture Validation](#architecture-validation)
8. [CLI Reference](#cli-reference)
9. [Integration Patterns](#integration-patterns)
10. [Performance Considerations](#performance-considerations)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

## Quick Start

### Basic Analysis

```python
from pheno.patterns.refactoring import CodeAnalyzer
from pathlib import Path

# Create analyzer
analyzer = CodeAnalyzer(
    size_threshold=500,
    complexity_threshold=10
)

# Analyze a file
result = await analyzer.analyze_file(Path('myfile.py'))

# Check results
print(f"Lines of Code: {result.metrics.lines_of_code}")
print(f"Complexity: {result.metrics.cyclomatic_complexity}")
print(f"Needs Refactoring: {result.metrics.needs_refactoring}")

# Review violations
for violation in result.violations:
    print(f"{violation.severity}: {violation.message}")
```

### Basic Extraction

```python
from pheno.patterns.refactoring import ClassExtractor
from pathlib import Path

# Create extractor
extractor = ClassExtractor()

# Extract a class
result = await extractor.extract_class(
    source_file=Path('source.py'),
    class_name='MyClass',
    target_file=Path('target.py')
)

# Write extracted code
if result.success:
    Path(result.target_file).write_text(result.extracted_code)
    Path(result.source_file).write_text(result.remaining_code)
```

### Basic Validation

```python
from pheno.patterns.refactoring import validate_layers
from pathlib import Path

# Validate architecture
result = await validate_layers(Path('myfile.py'))

# Check validation
if result.is_valid:
    print("✓ Architecture is valid")
else:
    print(f"✗ Found {result.error_count} errors")
    for issue in result.issues:
        print(f"  {issue}")
```

## Installation

The refactoring patterns module is part of the pheno-sdk package:

```bash
pip install pheno-sdk
```

Or install from source:

```bash
git clone https://github.com/yourusername/pheno-sdk
cd pheno-sdk
pip install -e .
```

## Core Concepts

### Hexagonal Architecture

Hexagonal Architecture (also known as Ports and Adapters) organizes code into distinct layers:

1. **Domain Layer**: Core business logic, entities, and value objects
   - No dependencies on other layers
   - Pure business rules and domain models

2. **Ports Layer**: Interfaces and abstractions
   - Defines contracts for external interactions
   - Uses Protocol or ABC for interface definitions

3. **Application Layer**: Use cases and application services
   - Orchestrates domain logic
   - Depends on domain and ports

4. **Adapters Layer**: Concrete implementations
   - Implements port interfaces
   - Adapts external systems to domain needs

5. **Infrastructure Layer**: External concerns
   - Database, caching, messaging
   - Framework-specific code

### Dependency Rules

```
Infrastructure → Adapters → Application → Ports → Domain
                                          ↑
                                          |
                                    (all layers can depend on domain)
```

Key principles:
- Dependencies flow toward the domain
- Domain has no dependencies
- Use dependency inversion for infrastructure
- Adapters implement port interfaces

## Refactoring Strategies

The module provides four main extraction strategies:

### 1. Class Extraction

Extract individual classes to separate files for better organization.

**When to use:**
- File has multiple unrelated classes
- Class is large and self-contained
- Class can be reused elsewhere

**Example:**

```python
from pheno.patterns.refactoring import ClassExtractor

extractor = ClassExtractor()

result = await extractor.extract_class(
    source_file=Path('models.py'),
    class_name='User',
    target_file=Path('user.py')
)
```

**Before:**
```python
# models.py (500 lines)
class User:
    def __init__(self, name: str): ...
    def validate(self): ...
    # ... 50 more methods

class Product:
    def __init__(self, name: str): ...
    # ... 50 more methods

class Order:
    def __init__(self, user: User): ...
    # ... 50 more methods
```

**After:**
```python
# user.py
class User:
    def __init__(self, name: str): ...
    def validate(self): ...
    # ... 50 more methods

# product.py
class Product:
    def __init__(self, name: str): ...
    # ... 50 more methods

# order.py
class Order:
    def __init__(self, user: User): ...
    # ... 50 more methods
```

### 2. Concern Extraction

Extract code by functional concern (authentication, validation, caching, etc.).

**When to use:**
- Related functionality scattered across file
- Cross-cutting concerns mixed with business logic
- Need to isolate specific responsibilities

**Example:**

```python
from pheno.patterns.refactoring import ConcernExtractor

extractor = ConcernExtractor()

result = await extractor.extract_concern(
    source_file=Path('service.py'),
    concern='authentication',
    target_dir=Path('auth/')
)
```

**Supported Concerns:**
- `authentication`: Login, tokens, credentials
- `validation`: Data validation, verification
- `caching`: Cache operations, memoization
- `logging`: Logging and audit trails
- `monitoring`: Metrics, tracking, observability
- `serialization`: JSON/XML conversion
- `database`: DB operations, repositories
- `api`: API endpoints, routes, controllers

**Before:**
```python
# service.py
class UserService:
    def create_user(self, data):
        # Validation logic
        if not self.validate_email(data['email']):
            raise ValueError("Invalid email")

        # Authentication logic
        token = self.generate_token(data)

        # Business logic
        user = User(**data)
        self.repository.save(user)

        return user

    def validate_email(self, email): ...
    def generate_token(self, data): ...
```

**After:**
```python
# validation.py
def validate_email(email): ...

# authentication.py
def generate_token(data): ...

# service.py
from .validation import validate_email
from .authentication import generate_token

class UserService:
    def create_user(self, data):
        if not validate_email(data['email']):
            raise ValueError("Invalid email")

        token = generate_token(data)
        user = User(**data)
        self.repository.save(user)

        return user
```

### 3. Pattern Extraction

Extract design patterns to dedicated modules.

**When to use:**
- Design patterns implemented inline
- Pattern can be reused
- Pattern obscures business logic

**Example:**

```python
from pheno.patterns.refactoring import PatternExtractor

extractor = PatternExtractor()

result = await extractor.extract_pattern(
    source_file=Path('services.py'),
    pattern_type='factory',
    target_dir=Path('patterns/')
)
```

**Supported Patterns:**
- `factory`: Factory and Builder patterns
- `singleton`: Singleton pattern
- `strategy`: Strategy pattern
- `observer`: Observer/Listener patterns

**Factory Pattern Example:**

**Before:**
```python
# services.py
class ServiceFactory:
    def create_service(self, service_type: str):
        if service_type == 'user':
            return UserService()
        elif service_type == 'product':
            return ProductService()
        # ... many more conditions

class UserService: ...
class ProductService: ...
```

**After:**
```python
# factory.py
class ServiceFactory:
    def create_service(self, service_type: str):
        if service_type == 'user':
            return UserService()
        elif service_type == 'product':
            return ProductService()

# services.py
from .factory import ServiceFactory

class UserService: ...
class ProductService: ...
```

### 4. Layer Extraction

Extract code by architectural layer.

**When to use:**
- Mixed layers in single file
- Violates layer separation
- Need to enforce hexagonal architecture

**Example:**

```python
from pheno.patterns.refactoring import LayerExtractor

extractor = LayerExtractor()

result = await extractor.extract_layer(
    source_file=Path('mixed.py'),
    layer='domain',
    target_dir=Path('domain/')
)
```

**Supported Layers:**
- `domain`: Entities, value objects, aggregates
- `application`: Services, use cases, commands
- `adapters`: Controllers, repositories, presenters
- `infrastructure`: Config, database, cache
- `ports`: Interfaces, protocols

**Before:**
```python
# mixed.py
# Domain entity
class User:
    def __init__(self, name: str):
        self.name = name

# Application service
class UserService:
    def create_user(self, name: str):
        return User(name)

# Adapter
class UserRepository:
    def save(self, user: User):
        db.save(user)
```

**After:**
```python
# domain/entities.py
class User:
    def __init__(self, name: str):
        self.name = name

# application/services.py
from ..domain.entities import User

class UserService:
    def create_user(self, name: str):
        return User(name)

# adapters/repositories.py
from ..domain.entities import User

class UserRepository:
    def save(self, user: User):
        db.save(user)
```

## Code Analysis

### Metrics Collected

The analyzer collects comprehensive metrics:

```python
from pheno.patterns.refactoring import CodeAnalyzer

analyzer = CodeAnalyzer()
result = await analyzer.analyze_file(Path('myfile.py'))

metrics = result.metrics
# metrics.lines_of_code: int
# metrics.cyclomatic_complexity: int
# metrics.cognitive_complexity: int
# metrics.class_count: int
# metrics.function_count: int
# metrics.import_count: int
# metrics.dependency_depth: int
```

### Complexity Metrics

**Cyclomatic Complexity:**
- Measures number of linearly independent paths
- Based on control flow (if, for, while, etc.)
- Target: < 10 per function, < 50 per file

**Cognitive Complexity:**
- Measures how difficult code is to understand
- Accounts for nesting and boolean operators
- Target: < 15 per function

**Example:**

```python
# Low complexity (2)
def simple_function(x):
    if x > 0:
        return True
    return False

# High complexity (8)
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return True
            else:
                return False
        elif y < 0:
            return None
    elif x < 0:
        if y > 0:
            return False
    return None
```

### Violation Detection

The analyzer detects various architectural violations:

1. **Layer Dependency Violations**
   - Domain depending on infrastructure
   - Application depending on adapters
   - Violations of dependency rules

2. **God Classes**
   - Classes with > 15 methods
   - Classes with multiple responsibilities
   - Violation of Single Responsibility Principle

3. **Circular Dependencies**
   - Relative imports between modules
   - Potential circular import chains

4. **Missing Abstractions**
   - Adapters without port interfaces
   - Concrete implementations without abstractions

**Example:**

```python
result = await analyzer.analyze_file(Path('myfile.py'))

for violation in result.violations:
    print(f"[{violation.severity}] {violation.violation_type}")
    print(f"  Line {violation.line_number}: {violation.message}")
    if violation.suggested_fix:
        print(f"  Fix: {violation.suggested_fix}")
```

### Refactoring Priorities

The analyzer assigns priority levels based on severity:

- **Critical**: Severity score >= 20
  - Multiple critical violations
  - Immediate refactoring required

- **High**: Severity score >= 10
  - Several high-severity violations
  - Refactor soon

- **Medium**: Severity score >= 5
  - Some violations or complexity issues
  - Plan refactoring

- **Low**: Severity score < 5
  - Minor issues
  - Optional refactoring

```python
result = await analyzer.analyze_file(Path('myfile.py'))
print(f"Priority: {result.priority}")
print(f"Severity Score: {result.severity_score}")
```

## Code Extraction

### Extraction Workflow

1. **Analyze Source**
   - Parse AST
   - Identify components
   - Extract dependencies

2. **Build Extracted Code**
   - Include necessary imports
   - Preserve documentation
   - Maintain formatting

3. **Update Source**
   - Remove extracted code
   - Add import statements
   - Clean up unused code

4. **Validate Result**
   - Check syntax
   - Verify imports
   - Test extraction

### Handling Dependencies

The extractor automatically manages dependencies:

```python
from pheno.patterns.refactoring import ClassExtractor

extractor = ClassExtractor()
result = await extractor.extract_class(
    Path('source.py'),
    'MyClass',
    Path('target.py')
)

# Dependencies are automatically included
print(f"Dependencies: {result.dependencies}")
# ['from typing import List', 'import logging', ...]
```

### Dry Run Mode

Test extractions without modifying files:

```python
# Using CLI
$ python -m pheno.patterns.refactoring.cli extract class \
    source.py MyClass --dry-run

# Programmatically
result = await extractor.extract_class(...)
print("Preview:", result.extracted_code[:500])
# Don't write files
```

### Batch Extraction

Extract multiple components:

```python
from pheno.patterns.refactoring import ClassExtractor
from pathlib import Path

extractor = ClassExtractor()
classes_to_extract = ['User', 'Product', 'Order']

for class_name in classes_to_extract:
    result = await extractor.extract_class(
        source_file=Path('models.py'),
        class_name=class_name,
        target_file=Path(f'{class_name.lower()}.py')
    )

    if result.success:
        Path(result.target_file).write_text(result.extracted_code)
        print(f"✓ Extracted {class_name}")
    else:
        print(f"✗ Failed to extract {class_name}: {result.error}")
```

## Architecture Validation

### Port/Adapter Validation

Validate port/adapter pattern compliance:

```python
from pheno.patterns.refactoring import validate_port_adapter

# Validate port interface
result = await validate_port_adapter(
    Path('ports/user_repository.py'),
    is_port=True
)

# Validate adapter implementation
result = await validate_port_adapter(
    Path('adapters/sql_user_repository.py'),
    is_port=False
)

# Check results
if not result.is_valid:
    for issue in result.issues:
        print(f"{issue.severity}: {issue.message}")
```

**Port Interface Requirements:**
- Must use ABC or Protocol
- Should not contain implementation
- Should define clear contracts

**Good Port:**
```python
from typing import Protocol
from ..domain import User

class UserRepository(Protocol):
    """Port for user repository."""

    async def save(self, user: User) -> None:
        """Save a user."""
        ...

    async def find_by_id(self, user_id: str) -> User:
        """Find user by ID."""
        ...
```

**Good Adapter:**
```python
from ..ports import UserRepository
from ..domain import User

class SqlUserRepository(UserRepository):
    """SQL implementation of user repository."""

    async def save(self, user: User) -> None:
        await self.db.execute("INSERT INTO users ...")

    async def find_by_id(self, user_id: str) -> User:
        row = await self.db.fetch_one("SELECT * FROM users ...")
        return User.from_row(row)
```

### Layer Validation

Validate layer separation:

```python
from pheno.patterns.refactoring import validate_layers

result = await validate_layers(Path('application/service.py'))

if not result.is_valid:
    print(f"Found {result.error_count} layer violations")
    for issue in result.issues:
        print(f"  {issue.message}")
```

**Layer Rules:**
- Domain: No dependencies
- Ports: Can depend on domain
- Application: Can depend on domain and ports
- Adapters: Can depend on domain, ports, application
- Infrastructure: Can depend on all layers

**Violation Example:**
```python
# domain/user.py - VIOLATION!
from ..adapters.database import Database  # Domain shouldn't depend on adapters

class User:
    def save(self):
        db = Database()  # Domain logic shouldn't access infrastructure
        db.save(self)
```

**Correct:**
```python
# domain/user.py
class User:
    def __init__(self, name: str):
        self.name = name

# ports/user_repository.py
class UserRepository(Protocol):
    def save(self, user: User) -> None: ...

# application/user_service.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, name: str) -> User:
        user = User(name)
        self.repository.save(user)
        return user
```

### Dependency Validation

Validate dependency rules:

```python
from pheno.patterns.refactoring import validate_dependencies

result = await validate_dependencies(
    Path('myfile.py'),
    project_root=Path('.')
)

if not result.is_valid:
    for issue in result.issues:
        print(f"{issue.rule_name}: {issue.message}")
```

**Checks:**
- No circular imports
- Dependency inversion compliance
- Reasonable dependency count
- Proper abstraction usage

## CLI Reference

### Installation

The CLI is included with pheno-sdk:

```bash
pip install pheno-sdk
```

### Global Options

```bash
python -m pheno.patterns.refactoring.cli [OPTIONS] COMMAND [ARGS]

Options:
  -v, --verbose  Enable verbose logging
  -q, --quiet    Suppress all output except errors
  --help         Show this message and exit
```

### Analyze Commands

#### analyze file

Analyze a single file:

```bash
python -m pheno.patterns.refactoring.cli analyze file PATH [OPTIONS]

Options:
  -o, --output [text|json|html]  Output format (default: text)
  -t, --threshold INTEGER        LOC threshold (default: 500)
```

**Example:**
```bash
# Text output
python -m pheno.patterns.refactoring.cli analyze file src/service.py

# JSON output
python -m pheno.patterns.refactoring.cli analyze file src/service.py -o json

# Custom threshold
python -m pheno.patterns.refactoring.cli analyze file src/service.py -t 300
```

#### analyze directory

Analyze all files in directory:

```bash
python -m pheno.patterns.refactoring.cli analyze directory PATH [OPTIONS]

Options:
  -o, --output [text|json|html]  Output format (default: text)
  -e, --exclude TEXT             Patterns to exclude (multiple)
  -t, --threshold INTEGER        LOC threshold (default: 500)
```

**Example:**
```bash
# Analyze directory
python -m pheno.patterns.refactoring.cli analyze directory src/

# Exclude tests
python -m pheno.patterns.refactoring.cli analyze directory src/ \
  -e "test_" -e "__pycache__"

# JSON output
python -m pheno.patterns.refactoring.cli analyze directory src/ -o json
```

### Extract Commands

#### extract class

Extract a class to separate file:

```bash
python -m pheno.patterns.refactoring.cli extract class FILE CLASS [OPTIONS]

Options:
  -t, --target PATH  Target file path
  --dry-run          Preview without writing
```

**Example:**
```bash
# Extract class
python -m pheno.patterns.refactoring.cli extract class \
  src/models.py User -t src/user.py

# Dry run
python -m pheno.patterns.refactoring.cli extract class \
  src/models.py User --dry-run
```

#### extract concern

Extract by functional concern:

```bash
python -m pheno.patterns.refactoring.cli extract concern FILE CONCERN [OPTIONS]

Options:
  -d, --target-dir PATH  Target directory
  --dry-run              Preview without writing

Concerns:
  authentication, validation, caching, logging, monitoring,
  serialization, database, api
```

**Example:**
```bash
# Extract authentication
python -m pheno.patterns.refactoring.cli extract concern \
  src/service.py authentication -d src/auth/

# Extract validation
python -m pheno.patterns.refactoring.cli extract concern \
  src/service.py validation --dry-run
```

#### extract pattern

Extract design pattern:

```bash
python -m pheno.patterns.refactoring.cli extract pattern FILE PATTERN [OPTIONS]

Options:
  -d, --target-dir PATH  Target directory
  --dry-run              Preview without writing

Patterns:
  factory, singleton, strategy, observer
```

**Example:**
```bash
# Extract factory
python -m pheno.patterns.refactoring.cli extract pattern \
  src/services.py factory -d src/patterns/

# Extract singleton
python -m pheno.patterns.refactoring.cli extract pattern \
  src/config.py singleton
```

#### extract layer

Extract by architectural layer:

```bash
python -m pheno.patterns.refactoring.cli extract layer FILE LAYER [OPTIONS]

Options:
  -d, --target-dir PATH  Target directory
  --dry-run              Preview without writing

Layers:
  domain, application, adapters, infrastructure, ports
```

**Example:**
```bash
# Extract domain layer
python -m pheno.patterns.refactoring.cli extract layer \
  src/mixed.py domain -d src/domain/

# Extract adapters
python -m pheno.patterns.refactoring.cli extract layer \
  src/mixed.py adapters -d src/adapters/
```

### Validate Commands

#### validate port-adapter

Validate port/adapter compliance:

```bash
python -m pheno.patterns.refactoring.cli validate port-adapter FILE [OPTIONS]

Options:
  --is-port              Validate as port interface
  -o, --output [text|json]  Output format (default: text)
```

**Example:**
```bash
# Validate port
python -m pheno.patterns.refactoring.cli validate port-adapter \
  src/ports/repository.py --is-port

# Validate adapter
python -m pheno.patterns.refactoring.cli validate port-adapter \
  src/adapters/sql_repository.py

# JSON output
python -m pheno.patterns.refactoring.cli validate port-adapter \
  src/adapters/sql_repository.py -o json
```

#### validate layers

Validate layer separation:

```bash
python -m pheno.patterns.refactoring.cli validate layers FILE [OPTIONS]

Options:
  -o, --output [text|json]  Output format (default: text)
```

**Example:**
```bash
# Validate layers
python -m pheno.patterns.refactoring.cli validate layers \
  src/application/service.py

# JSON output
python -m pheno.patterns.refactoring.cli validate layers \
  src/application/service.py -o json
```

#### validate dependencies

Validate dependency rules:

```bash
python -m pheno.patterns.refactoring.cli validate dependencies FILE [OPTIONS]

Options:
  -o, --output [text|json]  Output format (default: text)
```

**Example:**
```bash
# Validate dependencies
python -m pheno.patterns.refactoring.cli validate dependencies \
  src/service.py

# JSON output
python -m pheno.patterns.refactoring.cli validate dependencies \
  src/service.py -o json
```

### Report Command

Generate comprehensive report:

```bash
python -m pheno.patterns.refactoring.cli report DIRECTORY [OPTIONS]

Options:
  -o, --output PATH                Output file path
  -f, --format [text|json|html|markdown]  Report format (default: text)
```

**Example:**
```bash
# Text report to console
python -m pheno.patterns.refactoring.cli report src/

# Markdown report to file
python -m pheno.patterns.refactoring.cli report src/ \
  -f markdown -o refactoring-report.md

# JSON report
python -m pheno.patterns.refactoring.cli report src/ \
  -f json -o report.json

# HTML report
python -m pheno.patterns.refactoring.cli report src/ \
  -f html -o report.html
```

## Integration Patterns

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/refactoring-check.yml
name: Architecture Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install pheno-sdk

      - name: Analyze codebase
        run: |
          python -m pheno.patterns.refactoring.cli analyze directory src/ \
            -o json > analysis.json

      - name: Validate architecture
        run: |
          python -m pheno.patterns.refactoring.cli report src/ \
            -f markdown -o report.md

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: refactoring-report
          path: report.md
```

### Pre-commit Hook

Add validation to pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: architecture-validation
        name: Validate Architecture
        entry: python -m pheno.patterns.refactoring.cli validate layers
        language: system
        types: [python]
```

### IDE Integration

#### VS Code Task

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Analyze File",
      "type": "shell",
      "command": "python -m pheno.patterns.refactoring.cli analyze file ${file}",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Validate Architecture",
      "type": "shell",
      "command": "python -m pheno.patterns.refactoring.cli validate layers ${file}",
      "group": "test"
    }
  ]
}
```

### Programmatic Integration

```python
from pheno.patterns.refactoring import (
    CodeAnalyzer,
    validate_layers,
    detect_violations
)
from pathlib import Path

async def validate_project(project_root: Path):
    """Validate entire project architecture."""

    # Analyze all files
    analyzer = CodeAnalyzer()
    results = []

    for py_file in project_root.rglob('*.py'):
        if 'test' not in str(py_file):
            result = await analyzer.analyze_file(py_file)
            results.append(result)

    # Find critical issues
    critical = [r for r in results if r.priority == 'critical']

    if critical:
        print(f"Found {len(critical)} critical files:")
        for r in critical:
            print(f"  {r.file_path}")
            for s in r.refactoring_suggestions:
                print(f"    • {s}")

    # Validate layers
    violations = await detect_violations(project_root)
    layer_violations = [v for v in violations if v.violation_type == 'layer_dependency']

    if layer_violations:
        print(f"\nFound {len(layer_violations)} layer violations:")
        for v in layer_violations[:10]:
            print(f"  {v}")

    return len(critical) == 0 and len(layer_violations) == 0
```

## Performance Considerations

### Large Codebases

For large projects (>100k LOC):

1. **Use Exclusion Patterns**
   ```python
   exclude_patterns = [
       'test_',
       '__pycache__',
       '.git',
       'migrations',
       'vendor'
   ]

   large_files = await detect_large_files(
       project_root,
       exclude_patterns=exclude_patterns
   )
   ```

2. **Batch Processing**
   ```python
   import asyncio

   async def analyze_batch(files: List[Path], batch_size: int = 10):
       for i in range(0, len(files), batch_size):
           batch = files[i:i+batch_size]
           results = await asyncio.gather(*[
               analyzer.analyze_file(f) for f in batch
           ])
           yield results
   ```

3. **Caching Results**
   ```python
   import pickle
   from pathlib import Path

   cache_file = Path('.refactoring_cache.pkl')

   if cache_file.exists():
       with open(cache_file, 'rb') as f:
           cached_results = pickle.load(f)
   else:
       # Run analysis
       results = await analyze_project(project_root)

       # Cache results
       with open(cache_file, 'wb') as f:
           pickle.dump(results, f)
   ```

### Memory Management

For files with many violations:

```python
from pheno.patterns.refactoring import CodeAnalyzer

# Use generators for large datasets
async def analyze_large_project(root: Path):
    analyzer = CodeAnalyzer()

    for py_file in root.rglob('*.py'):
        result = await analyzer.analyze_file(py_file)

        # Process immediately, don't accumulate
        if result.priority in ['critical', 'high']:
            process_result(result)

        # Clear result to free memory
        del result
```

### Parallel Processing

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def parallel_analysis(files: List[Path]):
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [
            loop.run_in_executor(executor, analyze_file_sync, f)
            for f in files
        ]

        results = await asyncio.gather(*futures)

    return results

def analyze_file_sync(file: Path):
    # Synchronous wrapper for multiprocessing
    import asyncio
    return asyncio.run(analyzer.analyze_file(file))
```

## Troubleshooting

### Common Issues

#### Issue: "Module not found" after extraction

**Cause:** Import paths not updated after extraction

**Solution:**
```python
# After extracting User class from models.py to user.py

# models.py - Add import
from .user import User

# Other files using User
# Before:
from .models import User

# After:
from .user import User
```

#### Issue: Circular import detected

**Cause:** Relative imports creating circular dependencies

**Solution:**
```python
# Instead of:
from ..domain import User  # Relative import

# Use:
from pheno.domain import User  # Absolute import
```

#### Issue: "Class not found" during extraction

**Cause:** Class name typo or class doesn't exist

**Solution:**
```python
# List all classes first
import ast

with open('file.py') as f:
    tree = ast.parse(f.read())

classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
print("Available classes:", classes)
```

#### Issue: Layer validation fails unexpectedly

**Cause:** File not in recognized layer directory

**Solution:**
```python
# Ensure files are in proper directories:
# src/domain/
# src/ports/
# src/application/
# src/adapters/
# src/infrastructure/

# Or specify layer explicitly in validation
```

#### Issue: High memory usage during analysis

**Cause:** Analyzing too many files at once

**Solution:**
```python
# Use batch processing
async def analyze_in_batches(files: List[Path], batch_size: int = 50):
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        results = []

        for file in batch:
            result = await analyzer.analyze_file(file)
            results.append(result)

        # Process batch
        process_batch(results)

        # Clear memory
        results.clear()
```

### Debug Mode

Enable verbose logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run analysis
result = await analyzer.analyze_file(Path('file.py'))
```

Or via CLI:

```bash
python -m pheno.patterns.refactoring.cli -v analyze file myfile.py
```

## FAQ

### Q1: What's the difference between cyclomatic and cognitive complexity?

**A:** Cyclomatic complexity counts the number of decision points (if, for, while). Cognitive complexity measures how hard the code is to understand, accounting for nesting depth and Boolean operators.

Example:
```python
# Same cyclomatic complexity (3), different cognitive complexity

# Low cognitive complexity (3)
if a: return 1
if b: return 2
if c: return 3

# High cognitive complexity (6)
if a:           # +1
    if b:       # +2 (nested)
        if c:   # +3 (nested)
            return 1
```

### Q2: Should I extract every class to its own file?

**A:** No. Extract classes when:
- File exceeds 500 LOC
- Classes are unrelated
- Class can be reused elsewhere
- Class has clear single responsibility

Keep related small classes together:
```python
# OK - related value objects
# value_objects.py
class Money: ...
class Currency: ...
class ExchangeRate: ...
```

### Q3: How do I handle dependencies after extraction?

**A:** The extractor automatically includes import statements in extracted code. Update source file imports:

```python
# Before extraction
# models.py
class User: ...
class UserService:
    def create(self): return User()

# After extracting User to user.py
# models.py
from .user import User

class UserService:
    def create(self): return User()
```

### Q4: What if validation shows false positives?

**A:** Validation uses heuristics and may flag intentional design choices. Review each issue:

```python
result = await validate_layers(file)

for issue in result.issues:
    if issue.severity == 'warning':
        # Review warnings - may be acceptable
        print(f"Review: {issue.message}")
    elif issue.severity in ['error', 'critical']:
        # Errors should be fixed
        print(f"Fix: {issue.message}")
```

### Q5: Can I customize validation rules?

**A:** Yes, create custom validators:

```python
from pheno.patterns.refactoring import LayerValidator

class CustomLayerValidator(LayerValidator):
    # Override allowed dependencies
    ALLOWED_DEPENDENCIES = {
        'domain': set(),
        'application': {'domain', 'ports', 'infrastructure'},  # Custom rule
        # ...
    }

validator = CustomLayerValidator()
result = await validator.validate_layers(file)
```

### Q6: How do I handle monorepo structures?

**A:** Analyze each package separately:

```python
monorepo_root = Path('/my-monorepo')
packages = ['service-a', 'service-b', 'shared']

for package in packages:
    package_path = monorepo_root / package
    violations = await detect_violations(package_path)
    print(f"{package}: {len(violations)} violations")
```

### Q7: What's the recommended file size limit?

**A:**
- **Target**: 200-300 LOC per file
- **Warning**: 500 LOC (default threshold)
- **Critical**: 1000+ LOC

Exceptions:
- Generated code
- Configuration files
- Test fixtures

### Q8: How do I prioritize refactoring work?

**A:**
1. Fix critical violations first (architecture violations)
2. Refactor high-priority files (priority='critical')
3. Address god classes (>15 methods)
4. Reduce high complexity (>10)
5. Split large files (>500 LOC)

```python
# Get prioritized list
results = await analyze_directory(root)
critical = [r for r in results if r.priority == 'critical']
high = [r for r in results if r.priority == 'high']

print("Refactoring Priority:")
print(f"1. Critical: {len(critical)} files")
print(f"2. High: {len(high)} files")
```

### Q9: Can I use this with other tools?

**A:** Yes, integrates with:

- **Ruff**: For linting
  ```bash
  ruff check . && python -m pheno.patterns.refactoring.cli report .
  ```

- **MyPy**: For type checking
  ```bash
  mypy . && python -m pheno.patterns.refactoring.cli validate layers src/
  ```

- **Pytest**: For testing
  ```python
  def test_architecture():
      result = await validate_project(Path('.'))
      assert result.is_valid
  ```

### Q10: How do I roll back an extraction?

**A:** Extractions modify files, so use version control:

```bash
# Before extraction
git add -A
git commit -m "Before extraction"

# Perform extraction
python -m pheno.patterns.refactoring.cli extract class models.py User

# If issues arise
git reset --hard HEAD  # Roll back

# Or keep changes but review
git diff  # Review changes
```

---

## Additional Resources

- **API Documentation**: See inline docstrings for detailed API docs
- **Examples**: Check `examples/refactoring_patterns_example.py`
- **GitHub Issues**: Report bugs and request features
- **Pheno SDK Docs**: https://github.com/yourusername/pheno-sdk

## License

This module is part of pheno-sdk, licensed under MIT License.

---

**Last Updated**: 2025-10-16
**Version**: 1.0.0
**Maintainer**: Pheno SDK Team
