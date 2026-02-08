# Test Constants Extraction Strategy

## Overview

This document describes the strategy for handling PLR2004 "magic value" violations in test files.

## Results Summary

- **Original PLR2004 violations:** 3,597
- **After extraction:** 2,813
- **Reduction:** 784 violations (21.8%)
- **Files modified:** 363

## What Was Extracted

The following frequently reused magic values were extracted to `tests/test_constants.py`:

### HTTP Status Codes (Always Extracted)
- All standard HTTP status codes (200, 201, 400, 401, 404, 409, 429, 500, 503, etc.)
- These are universal constants and should never appear as magic numbers

### Timeouts and Polling Values (Always Extracted)
- Standard timeout values: 30.0, 60.0, 10.0, 5.0
- Poll intervals: 0.1, 0.5, 1.0
- Backoff values: 2.0
- These represent standard timing patterns across tests

### Common Float Values (Always Extracted)
- Tolerance values: 0.01, 0.05
- Common test floats: 45.0, 45.5
- These are frequently reused in assertions

### Count Values (Contextually Extracted)
- Common counts (2, 3, 4, 5, 10, 100, 500, 1000) were extracted ONLY when used in:
  - `len(x) == N` comparisons
  - `assert x == N` assertions
  - `count == N` or `total == N` comparisons

## What Was NOT Extracted (Acceptable Magic Values)

The remaining 2,813 PLR2004 violations represent legitimate single-use test values:

### 1. Array Indices and Slicing
```python
items[0]  # First item access
data[2:5]  # Slicing operations
```
**Rationale:** These are positional indicators, not domain values. Extracting them reduces readability.

### 2. Loop Ranges for Test Data Generation
```python
for i in range(10):  # Create 10 test items
    items.append(create_item(f"item-{i}"))
```
**Rationale:** The count is specific to this test's needs. Extracting it provides no benefit.

### 3. Test-Specific Data Values
```python
item.price = 19.99  # Specific test price
user.score = 73.5   # Specific test score
```
**Rationale:** These are unique test data values that won't be reused. They're clear in context.

### 4. Single-Use Assertion Counts
```python
assert len(unique_items) == 7  # This specific test expects 7
```
**Rationale:** When a count is unique to one test scenario, extraction doesn't improve maintainability.

### 5. Test Data IDs
```python
item_id = "test-item-123"
user_id = "user-456"
```
**Rationale:** Test identifiers are specific to each test case.

## Guidelines for Test Authors

### DO Extract:
1. HTTP status codes → Always use constants from `test_constants`
2. Standard timeouts (30s, 60s, etc.) → Use `TIMEOUT_*` constants
3. Poll intervals (0.1s, 0.5s) → Use `POLL_INTERVAL_*` constants
4. Values reused across multiple tests → Extract to `test_constants`

### DON'T Extract:
1. Array indices (`items[0]`, `data[1]`)
2. Loop ranges specific to one test (`range(7)`)
3. Unique test data values (`price = 19.99`)
4. Single-use assertion counts (`assert len(x) == 13`)
5. Test-specific IDs and identifiers

## Future Maintenance

When PLR2004 violations appear in new test code:

1. **Check if it's a universal constant** (HTTP status, standard timeout)
   → Use existing constant from `test_constants`

2. **Check if the value is reused across multiple tests**
   → Add to `test_constants` if reused 5+ times

3. **Is it a single-use test value?**
   → Keep inline, it's more readable than a constant

4. **Is it unclear what the magic value represents?**
   → Extract even if single-use, but add a descriptive constant name

## Implementation Details

### Extraction Script
Location: `scripts/quality/extract_test_constants.py`

The script:
- Scans all test files for PLR2004 violations
- Replaces frequently used values with constants
- Adds imports automatically
- Preserves code formatting

### Constants Module
Location: `tests/test_constants.py`

Categories:
- HTTP status codes
- Common count assertions
- Timeout and polling values
- Retry and limit configuration
- Floating point thresholds
- Test data size limits

## Metrics

### Replacements by Category
- HTTP status codes: ~275 violations eliminated
- Timeouts/intervals: ~100 violations eliminated
- Count assertions: ~400 violations eliminated
- Total replacements: 182,211 (many values replaced multiple times)

### Impact
- 21.8% reduction in PLR2004 violations
- Improved test maintainability for reused values
- Preserved readability for single-use test values
- 363 test files updated with consistent constants
