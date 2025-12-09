# Unified Test CLI Command

## Overview

The `rtm test` command provides a unified interface for running tests across the TracerTM project. It supports multiple languages (Python, Go, Frontend), test scopes (unit, integration, e2e), domain grouping, and multiple output formats.

## Command Syntax

```bash
rtm test [OPTIONS]
```

### Options

- `--lang [python|go|frontend|all]` - Programming language to test (default: all)
- `--scope [unit|integration|e2e]` - Test scope to run (default: all scopes)
- `--by-domain` - Group test results by functional domain
- `--format [text|json]` - Output format (default: text)
- `--verbose` - Show detailed test execution logs
- `--fail-fast` - Stop on first test failure

## Usage Examples

### Run All Tests
```bash
rtm test --lang all
```

### Run Python Unit Tests Only
```bash
rtm test --lang python --scope unit
```

### Frontend Tests Grouped by Domain
```bash
rtm test --lang frontend --by-domain
```

### Output Results as JSON
```bash
rtm test --format json
```

### Run Integration Tests for All Languages
```bash
rtm test --scope integration
```

## Output Formats

### Text Format (Default)
Human-readable output with test names, statuses, and summary statistics.

```
✓ 234 tests passed
✗ 2 tests failed
⊘ 5 tests skipped
Total: 241 tests | Time: 45.2s
```

### JSON Format
Structured output for programmatic consumption:

```json
{
  "summary": {
    "passed": 234,
    "failed": 2,
    "skipped": 5,
    "total": 241,
    "duration": 45.2
  },
  "results": [...]
}
```

## Test Discovery

The CLI automatically discovers tests based on language:

- **Python**: `tests/` directory and `*_test.py` files
- **Go**: `*_test.go` files
- **Frontend**: `src/__tests__/` and `*.test.ts(x)` files

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
- `2` - Invalid command arguments
- `3` - Test discovery or setup error
