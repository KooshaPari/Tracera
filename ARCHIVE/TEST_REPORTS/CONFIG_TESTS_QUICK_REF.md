# Configuration & Initialization Tests - Quick Reference

## Overview

**92 new test cases** for TraceRTM configuration and initialization, targeting **+2% coverage** on config/init paths.

## Test Files

```
tests/unit/config/
├── __init__.py                          # Module init
├── test_settings_comprehensive.py       # 37 tests - Settings module
├── test_config_schema.py               # 41 tests - Schema validation
└── test_logging_init.py                # 14 tests - Logging setup
```

## Quick Commands

```bash
# Run all config tests
pytest tests/unit/config/ -v

# Run specific file
pytest tests/unit/config/test_settings_comprehensive.py -v

# Run by class
pytest tests/unit/config/ -k "TestDatabaseSettings" -v

# Fast mode (no verbose)
pytest tests/unit/config/ -q

# With coverage report
pytest tests/unit/config/ --cov=src/tracertm/config --cov-report=term-missing
```

## Test Statistics

| File | Tests | Focus |
|------|-------|-------|
| `test_settings_comprehensive.py` | 37 | DatabaseSettings, TraceSettings, environment vars, singleton |
| `test_config_schema.py` | 41 | Config validation, API config, sync settings, aliases |
| `test_logging_init.py` | 14 | Logger setup, log levels, integration |
| **TOTAL** | **92** | Configuration & Initialization |

## Coverage Areas

### Settings Module (37 tests)
- DatabaseSettings: defaults, validation, constraints
- TraceSettings: defaults, custom values, validation
- Directories: creation, paths, nesting
- Environment variables: prefix, case sensitivity, conversion
- Singleton: get/reset pattern
- Feature flags: cache, async, validation

### Schema Module (41 tests)
- Database URL validation (6 tests)
- View types & formats (4 tests)
- Log level validation (2 tests)
- API configuration (8 tests)
- Sync configuration (6 tests)
- Project settings (3 tests)
- Aliases management (3 tests)

### Logging Module (14 tests)
- Logger instantiation (5 tests)
- Setup & configuration (3 tests)
- Integration with settings (2 tests)
- Error handling (1 test)
- Multiple log levels (3 tests)

## Key Test Classes

### DatabaseSettings
- Defaults: `url`, `echo`, `pool_size`, `max_overflow`
- Validation: PostgreSQL/SQLite URLs, constraints

### TraceSettings
- All fields with validation
- Environment variable precedence
- Singleton pattern (get_settings, reset_settings)
- Directory creation

### Config Schema
- All pydantic validators
- Enum constraints
- Range validation
- Relationship testing

### Logging
- get_logger() for all module names
- setup_logging() integration
- File and console handlers

## Running in CI/CD

```bash
# In your CI pipeline
pytest tests/unit/config/ \
  --tb=short \
  --junit-xml=reports/config-tests.xml \
  --cov=src/tracertm/config \
  --cov-report=xml
```

## Key Validation Tests

- Database URLs: PostgreSQL, SQLite, invalid rejection
- Numeric ranges: max_agents (1-10000), cache_ttl (0-3600), etc.
- Enum values: log levels, output formats, view types
- API config: timeouts, retries, URLs
- Environment variables: prefix, conversion, override

## Test Isolation Features

- Fixtures for setup/teardown
- Monkeypatch for env vars
- Mock objects for logging
- Temporary directories
- No shared state

## Expected Outcomes

✓ All 92 tests pass
✓ Execution time < 2 seconds
✓ No external dependencies
✓ Covers validation & edge cases
✓ Full constraint testing
✓ Integration scenarios

## Files Under Test

- `src/tracertm/config/settings.py` (37 tests)
- `src/tracertm/config/schema.py` (41 tests)
- `src/tracertm/logging_config.py` (14 tests)

## Integration with Existing Tests

- Existing config manager tests: 5 PASSED
- New config tests: 92 PASSED
- Combined: 97 PASSED

Total test suite compatible with all CI/CD pipelines.
