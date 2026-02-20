# Python Quality Quick Reference

## Metrics at a Glance

| Metric | Value | Status |
|--------|-------|--------|
| Type Hints | 88.2% (3,491/3,957) | 🟡 88% |
| Docstrings | 80.4% functions, 90.8% classes | 🟡 80% |
| Linting Issues | 355 (1 critical blocker) | 🔴 CRITICAL |
| MyPy Errors | 1 syntax-only | 🔴 CRITICAL |
| Test Files | 488 | ✅ |
| Code Quality Score | 85/100 | 🟡 STRONG |

## Critical Issues

### 1. Syntax Error in item_specs.py (Line 395-402)
```bash
# Check syntax
python3 -c "import src.tracertm.api.routers.item_specs"
# Expected: SyntaxError

# Fix automatically
python3 -m ruff check src/tracertm/api/routers/item_specs.py --fix

# Verify
python3 -c "from src.tracertm.api.routers import item_specs; print('OK')"
```

## Essential Commands

### Quality Checks
```bash
# Format code
poe format
python3 -m ruff format src/tracertm

# Lint with fixes
poe lint
python3 -m ruff check src/tracertm --fix

# Type checking
poe type-check
python3 -m ty check src/tracertm

# Security scan
poe bandit
python3 -m bandit -r src/ --severity-level medium

# Dependency audit
poe pip-audit
python3 -m pip-audit
```

### Testing & Coverage
```bash
# Unit tests only
python3 -m pytest tests/ -m unit -v

# With coverage
python3 -m pytest tests/ -m unit --cov=src/tracertm --cov-report=html

# Full test suite
python3 -m pytest tests/

# Generate HTML report
open htmlcov/index.html
```

### Coverage Report
```bash
# Terminal output
python3 -m pytest tests/ --cov=src/tracertm --cov-report=term-missing

# JSON export
python3 -m pytest tests/ --cov=src/tracertm --cov-report=json

# Parse coverage
python3 << 'EOF'
import json
with open('coverage.json') as f:
    data = json.load(f)
    total = data['totals']['percent_covered']
    print(f"Total Coverage: {total:.1f}%")
EOF
```

## Docstring Coverage
```bash
# Basic report (skip badge generation)
python3 -m interrogate src/tracertm -p

# Detailed verbose output
python3 -m interrogate src/tracertm -vv -p

# Summary by file
python3 -m interrogate src/tracertm -p --fail-under=85
```

## Type Hints Analysis
```bash
# Count coverage
python3 << 'EOF'
import ast
from pathlib import Path
from collections import defaultdict

coverage = defaultdict(int)
total = {"funcs": 0, "with_types": 0}

for py_file in Path("src/tracertm").rglob("*.py"):
    try:
        with open(py_file) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total["funcs"] += 1
                if node.returns:
                    total["with_types"] += 1
    except:
        pass

pct = 100 * total["with_types"] / total["funcs"]
print(f"Type Hints: {total['with_types']}/{total['funcs']} ({pct:.1f}%)")
EOF
```

## Find Missing Items

### Missing Return Type Hints
```bash
python3 << 'EOF'
import ast
from pathlib import Path

missing = []
for py_file in Path("src/tracertm").rglob("*.py"):
    try:
        with open(py_file) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.returns and node.name.startswith(('_get', 'create', 'list', 'update', 'delete')):
                    missing.append(f"{py_file}:{node.lineno} {node.name}()")
    except:
        pass

for item in missing[:20]:
    print(item)
print(f"... and {max(0, len(missing)-20)} more")
EOF
```

### Missing Docstrings
```bash
python3 << 'EOF'
import ast
from pathlib import Path

missing = []
for py_file in Path("src/tracertm").rglob("*.py"):
    try:
        with open(py_file) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    missing.append(f"{py_file}:{node.lineno} {node.name}()")
    except:
        pass

for item in missing[:20]:
    print(item)
print(f"... and {max(0, len(missing)-20)} more")
EOF
```

## Linting Issues Summary
```bash
# Count by type
python3 -m ruff check src/tracertm --output-format=json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
from collections import Counter
issues = Counter(d['code'] for d in data)
for code, count in issues.most_common(10):
    print(f"{code}: {count}")
EOF

# Show top files with issues
python3 -m ruff check src/tracertm --output-format=json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
from collections import Counter
files = Counter(d['filename'] for d in data)
for fname, count in files.most_common(5):
    print(f"{fname}: {count}")
EOF
```

## Full Quality Pipeline
```bash
# Single command
poe all

# Or step by step
poe format         # Format
poe lint          # Lint + fix
poe type-check    # Type check
poe bandit        # Security
poe pip-audit     # Dependencies
pytest            # Tests
```

## CI Integration

### GitHub Actions
```yaml
- name: Python Quality
  run: |
    python3 -m ruff format . --check
    python3 -m ruff check src/
    python3 -m ty check src/tracertm/
    python3 -m pytest tests/ --cov=src/tracertm --cov-report=term-missing
```

### Pre-commit Hook
```bash
# Install
pre-commit install

# Manual run
pre-commit run --all-files
```

## Target Improvements

| Metric | Current | Target | Effort |
|--------|---------|--------|--------|
| Type Hints | 88.2% | 95% | 30 min |
| Docstrings | 80.4% | 95% | 45 min |
| Linting Issues | 355 | <50 | 45 min |
| Coverage | TBD | 90% | 60 min |
| MyPy Errors | 1 | 0 | 10 min |

## Priority Checklist

- [ ] Fix syntax error in item_specs.py
- [ ] Run `poe lint --fix`
- [ ] Run `poe type-check`
- [ ] Add missing return types (top 100 public functions)
- [ ] Add missing docstrings (top 100 public functions)
- [ ] Run full test suite with coverage
- [ ] Achieve 90% coverage threshold
- [ ] Pass `poe all` pipeline

---

**Last Updated:** 2026-02-06
**Quick Reference Version:** 1.0
