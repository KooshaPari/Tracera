# SwiftRide Test Linking Guide

## Overview

This guide explains how to link the 1,000 generated test items to code files, features, requirements, and other artifacts in TraceRTM.

## Link Types

### 1. Tests → Code Files

Link tests to the code they validate:

```bash
# Example: Link unit test to Python file
trace link create \
  --from UNIT-TEST-001 \
  --to FILE-matching_service.py \
  --type tests

# Example: Link integration test to multiple services
trace link create --from INTEGRATION-TEST-001 --to FILE-trip_service.py --type tests
trace link create --from INTEGRATION-TEST-001 --to FILE-payment_service.py --type tests
```

**Naming Convention for Code Files:**
- Python: `FILE-{service_name}.py`
- Go: `FILE-{service_name}.go`
- TypeScript: `FILE-{component_name}.ts`
- JavaScript: `FILE-{component_name}.js`

### 2. Tests → Features

Link tests to the features they validate:

```bash
# Example: Link test to feature
trace link create \
  --from UNIT-TEST-001 \
  --to FEATURE-driver_matching \
  --type validates

# Example: Link E2E test to multiple features
trace link create --from E2E-TEST-001 --to FEATURE-rider_signup --type validates
trace link create --from E2E-TEST-001 --to FEATURE-ride_booking --type validates
```

**Feature Examples:**
- `FEATURE-driver_matching`
- `FEATURE-surge_pricing`
- `FEATURE-payment_processing`
- `FEATURE-trip_tracking`
- `FEATURE-rider_ratings`

### 3. Tests → Requirements/Stories

Link tests to requirements they verify:

```bash
# Example: Link test to user story
trace link create \
  --from E2E-TEST-001 \
  --to STORY-001 \
  --type verifies

# Example: Link test to epic
trace link create \
  --from INTEGRATION-TEST-001 \
  --to EPIC-001 \
  --type verifies
```

### 4. Tests → Test Data

Link tests to the data they use:

```bash
# Example: Link test to test data
trace link create \
  --from UNIT-TEST-001 \
  --to TEST-DATA-001 \
  --type uses

# Example: Link multiple data sets
trace link create --from E2E-TEST-001 --to TEST-DATA-001 --type uses  # Valid riders
trace link create --from E2E-TEST-001 --to TEST-DATA-021 --type uses  # Completed trips
```

### 5. Tests → Test Scenarios

Link implementation tests to scenarios:

```bash
# Example: Link E2E test to scenario
trace link create \
  --from E2E-TEST-001 \
  --to TEST-SCENARIO-001 \
  --type implements
```

## Linking Patterns by Test Type

### Unit Tests Linking Pattern

```bash
# Unit test typically links to:
# 1. Code file (tests)
# 2. Feature (validates)
# 3. Test data (uses)

trace link create --from UNIT-TEST-001 --to FILE-matching_service.py --type tests
trace link create --from UNIT-TEST-001 --to FEATURE-driver_matching --type validates
trace link create --from UNIT-TEST-001 --to TEST-DATA-002 --type uses
```

### Integration Tests Linking Pattern

```bash
# Integration test typically links to:
# 1. Multiple code files (tests)
# 2. Feature (validates)
# 3. Story/Requirement (verifies)
# 4. Test data (uses)

trace link create --from INTEGRATION-TEST-001 --to FILE-trip_service.py --type tests
trace link create --from INTEGRATION-TEST-001 --to FILE-payment_service.py --type tests
trace link create --from INTEGRATION-TEST-001 --to FEATURE-ride_completion --type validates
trace link create --from INTEGRATION-TEST-001 --to STORY-001 --type verifies
trace link create --from INTEGRATION-TEST-001 --to TEST-DATA-021 --type uses
```

### E2E Tests Linking Pattern

```bash
# E2E test typically links to:
# 1. Multiple code files (tests)
# 2. Multiple features (validates)
# 3. Story/Epic (verifies)
# 4. Test scenario (implements)
# 5. Multiple test data (uses)

trace link create --from E2E-TEST-001 --to STORY-005 --type verifies
trace link create --from E2E-TEST-001 --to FEATURE-rider_signup --type validates
trace link create --from E2E-TEST-001 --to FEATURE-ride_booking --type validates
trace link create --from E2E-TEST-001 --to TEST-SCENARIO-001 --type implements
trace link create --from E2E-TEST-001 --to TEST-DATA-001 --type uses
trace link create --from E2E-TEST-001 --to TEST-DATA-021 --type uses
```

### Performance Tests Linking Pattern

```bash
# Performance test typically links to:
# 1. Code files (tests)
# 2. Feature (validates)
# 3. Performance scenario (implements)

trace link create --from PERFORMANCE-TEST-001 --to FILE-matching_service.py --type tests
trace link create --from PERFORMANCE-TEST-001 --to FEATURE-driver_matching --type validates
```

### Security Tests Linking Pattern

```bash
# Security test typically links to:
# 1. Code files (tests)
# 2. Feature (validates)
# 3. Security requirement (verifies)

trace link create --from SECURITY-TEST-001 --to FILE-api_gateway.py --type tests
trace link create --from SECURITY-TEST-001 --to FEATURE-api_security --type validates
```

## Bulk Linking Script Examples

### Link All Matching Service Unit Tests

```bash
#!/bin/bash
# Link matching service tests

for i in {1..40}; do
  TEST_ID=$(printf "UNIT-TEST-%03d" $i)
  trace link create --from $TEST_ID --to FILE-matching_service.py --type tests
  trace link create --from $TEST_ID --to FEATURE-driver_matching --type validates
done
```

### Link Payment Service Tests

```bash
#!/bin/bash
# Link payment service tests (76-110)

for i in {76..110}; do
  TEST_ID=$(printf "UNIT-TEST-%03d" $i)
  trace link create --from $TEST_ID --to FILE-payment_service.py --type tests
  trace link create --from $TEST_ID --to FEATURE-payment_processing --type validates
done
```

## Test Coverage Matrix

Create a coverage matrix by linking tests to requirements:

```bash
# Story STORY-001 (User Login) coverage
trace link create --from UNIT-TEST-001 --to STORY-001 --type verifies
trace link create --from INTEGRATION-TEST-005 --to STORY-001 --type verifies
trace link create --from E2E-TEST-001 --to STORY-001 --type verifies
trace link create --from SECURITY-TEST-001 --to STORY-001 --type verifies

# Query coverage for a story
trace query links --target STORY-001 --type verifies
```

## Creating Test Suites

Group related tests into suites:

```bash
# Create test suite for matching service
trace item create \
  --type test_suite \
  --title "Matching Service Test Suite" \
  --description "All tests for driver matching functionality"

# Link tests to suite
trace link create --from UNIT-TEST-001 --to TEST-SUITE-001 --type belongs_to
trace link create --from INTEGRATION-TEST-001 --to TEST-SUITE-001 --type belongs_to
```

## Test Execution Tracking

Update test status and link to defects:

```bash
# Run test and update status
trace item update UNIT-TEST-001 --status in_progress
trace item update UNIT-TEST-001 --status passed

# If test fails, create and link defect
trace item create --type defect --title "Driver matching fails for edge case"
trace link create --from DEFECT-001 --to UNIT-TEST-001 --type found_by
trace link create --from DEFECT-001 --to FILE-matching_service.py --type affects
```

## Recommended Linking Workflow

### Phase 1: Link Tests to Code
1. Identify code files for each service
2. Create FILE items if not exists
3. Link unit and integration tests to code files

### Phase 2: Link Tests to Features
1. Identify features from requirements
2. Create FEATURE items if not exists
3. Link all test types to features

### Phase 3: Link Tests to Requirements
1. Map tests to stories/epics
2. Create coverage matrix
3. Identify gaps

### Phase 4: Link Test Data
1. Link tests to test data sets
2. Ensure data completeness
3. Create missing data sets

### Phase 5: Create Test Suites
1. Group tests by service
2. Group tests by feature
3. Group tests by priority

## Automation Script Template

```python
#!/usr/bin/env python3
"""
Automated test linking script
"""

import subprocess

# Test to code mappings
test_code_mapping = {
    "matching_service": {
        "file": "FILE-matching_service.py",
        "tests": list(range(1, 41)),  # UNIT-TEST-001 to UNIT-TEST-040
        "feature": "FEATURE-driver_matching"
    },
    "pricing_service": {
        "file": "FILE-pricing_service.py",
        "tests": list(range(41, 76)),  # UNIT-TEST-041 to UNIT-TEST-075
        "feature": "FEATURE-pricing_calculation"
    },
    # Add more services...
}

def create_link(source, target, link_type):
    """Create a link between items"""
    cmd = [
        "trace", "link", "create",
        "--from", source,
        "--to", target,
        "--type", link_type
    ]
    subprocess.run(cmd)

def link_service_tests(service_config):
    """Link all tests for a service"""
    file_id = service_config["file"]
    feature_id = service_config["feature"]

    for test_num in service_config["tests"]:
        test_id = f"UNIT-TEST-{test_num:03d}"
        create_link(test_id, file_id, "tests")
        create_link(test_id, feature_id, "validates")
        print(f"✓ Linked {test_id}")

# Run linking
for service_name, config in test_code_mapping.items():
    print(f"\nLinking {service_name} tests...")
    link_service_tests(config)
```

## Verification Queries

### Check Test Coverage

```bash
# Find tests for a specific file
trace query links --target FILE-matching_service.py --type tests

# Find tests validating a feature
trace query links --target FEATURE-driver_matching --type validates

# Find tests verifying a story
trace query links --target STORY-001 --type verifies

# Find unlinked tests
trace query items --type unit_test --no-links
```

### Coverage Reports

```bash
# Get coverage statistics
trace report coverage --by-feature
trace report coverage --by-story
trace report coverage --by-test-type
```

## Next Steps

1. **Review Test Items**: Browse generated tests in `.trace/` directories
2. **Create Code Items**: Create FILE items for all code files
3. **Create Feature Items**: Create FEATURE items for all features
4. **Start Linking**: Begin with critical priority tests first
5. **Verify Coverage**: Run coverage queries to identify gaps
6. **Create Suites**: Organize tests into logical suites
7. **Automate**: Use scripts for bulk linking operations

## Reference

- TraceRTM Link Types Documentation
- Test Management Best Practices
- SwiftRide Architecture Documentation
- Test Layer Documentation: SWIFTRIDE_TEST_LAYER_DOCUMENTATION.md

---

**Generated:** 2026-01-31
**Version:** 1.0
**Total Tests:** 1,000 items ready for linking
