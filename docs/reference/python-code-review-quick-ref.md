# Python Code Review - Quick Reference

**Date:** 2026-02-01 | **Full Report:** [python-backend-review.md](../reports/python-backend-review.md)

---

## 🚨 Critical Issues (Fix Immediately)

### 1. Shell Injection Vulnerability (P0)

**File:** `populate_projects.py:16`

```python
# ❌ VULNERABLE
subprocess.run(cmd, shell=True, ...)

# ✅ SECURE
cmd_args = ['rtm', 'item', 'create', title, '--view', view, ...]
subprocess.run(cmd_args, ...)
```

**Impact:** Arbitrary command execution
**Fix Time:** 2 hours

### 2. Missing Type Hints (P0)

**Files:** Root scripts (0-7% coverage)

```python
# ❌ NO TYPES
def create_item(project_path, title, view, item_type):
    pass

# ✅ WITH TYPES
def create_item(
    project_path: str,
    title: str,
    view: str,
    item_type: str
) -> Optional[str]:
    pass
```

**Fix Time:** 4 hours

---

## 📊 Quick Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total Python LOC | 5,301 | - |
| Docstring Coverage | 90.5% | ✅ |
| Type Hints Coverage | 35.1% | ❌ |
| Security Issues | 4 | ⚠️ |
| Test Coverage (Utils) | 0% | ❌ |

---

## ✅ Action Checklist

### This Week (P0)

- [ ] Fix shell injection in `populate_projects.py`
- [ ] Add type hints to root scripts
- [ ] Create `pyproject.toml` with dependencies
- [ ] Remove hardcoded test credentials

### This Sprint (P1)

- [ ] Write unit tests for utility scripts (target: 80%)
- [ ] Replace try/except pass with logging
- [ ] Refactor long functions (100+ LOC)
- [ ] Add constants file for magic strings

### Next Sprint (P2)

- [ ] Use `tempfile.mkdtemp()` instead of `/tmp/`
- [ ] Add input validation
- [ ] Improve test organization
- [ ] Set up automated security scanning

---

## 🛠️ Development Commands

### Security Scan

```bash
# Install bandit
pip install bandit

# Scan for security issues
bandit -r . -f txt

# Audit dependencies
pip install pip-audit
pip-audit
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Run type checker
mypy conftest.py create_links.py populate_projects.py --strict
```

### Linting

```bash
# Install pylint
pip install pylint

# Run linter
pylint *.py --score=yes
```

### Testing

```bash
# Run integration tests
pytest backend/tests/integration/ -v

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## 📁 File Structure

```
Python Files:
├── Root (902 LOC)
│   ├── conftest.py (207)          - Pytest config
│   ├── create_links.py (244)      - Link utility
│   └── populate_projects.py (451) - Mock data
│
└── Backend Tests (4,399 LOC)
    └── tests/integration/
        ├── conftest.py (431)           - Test fixtures
        ├── test_helpers.py (579)       - Helper functions
        └── test_nats_events.py (588)   - Event tests
```

---

## 🔒 Security Fixes

### 1. Shell Injection (HIGH)

```python
# Before
cmd = f'rtm item create "{title}" --view {view}'
subprocess.run(cmd, shell=True)

# After
cmd_args = ['rtm', 'item', 'create', title, '--view', view]
subprocess.run(cmd_args)
```

### 2. Hardcoded Credentials (MEDIUM)

```python
# Before
"postgres_url": os.getenv(
    "TEST_POSTGRES_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/tracertm_test"
)

# After
"postgres_url": os.getenv("TEST_POSTGRES_URL")  # Required, no default
if not TEST_CONFIG["postgres_url"]:
    raise ValueError("TEST_POSTGRES_URL environment variable required")
```

### 3. Try/Except Pass (LOW)

```python
# Before
except Exception:
    pass

# After
except Exception as e:
    logger.warning(f"Failed to delete stream: {e}")
```

---

## 📝 Code Standards

### Type Hints Example

```python
from typing import Optional, Dict, Any, List
from pathlib import Path

def add_link_to_item(
    item_path: Path,
    target_id: str,
    link_type: str
) -> bool:
    """Add a link to an item's frontmatter.

    Args:
        item_path: Path to the item file
        target_id: ID of the target item
        link_type: Type of link relationship

    Returns:
        True if link was added, False if already exists
    """
    if not item_path.exists():
        return False
    # ...
```

### Docstring Example

```python
def create_test_session(
    db_session: AsyncSession,
    neo4j_driver: AsyncDriver,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a test session in both PostgreSQL and Neo4j.

    Args:
        db_session: SQLAlchemy async session
        neo4j_driver: Neo4j async driver
        project_id: Optional project ID (generates UUID if not provided)

    Returns:
        Session data dictionary containing:
        - session_id: UUID of created session
        - project_id: Associated project ID
        - user_id: User who created session
        - sandbox_root: Path to sandbox directory
        - status: Session status ('active')
        - created_at: Timestamp of creation

    Raises:
        SQLAlchemyError: If database operations fail
    """
    # Implementation...
```

---

## 🎯 Quality Targets

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Type Hints | 35% | 80% | -45% |
| Test Coverage | 0% (utils) | 80% | -80% |
| Security Issues | 4 | 0 | -4 |
| Docstrings | 90.5% | 80% | +10.5% ✅ |

---

## 📚 Resources

- [Full Review Report](../reports/python-backend-review.md)
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 🤝 Contact

- **Questions?** See full report or contact development team
- **Security Issues?** Report to security team immediately
- **Next Review:** After P0/P1 fixes (2 weeks)
