# QA Gates

These scripts are intentionally thin pre-merge governance checks. Each exits
with status 1 when it detects a violation.

## qa-artifact-gate

Verifies that canonical QA artifact locations and configuration files are
present so pre-merge evidence has a stable home.

## qa-assurance-gate

Verifies that the repository still has runnable assurance surfaces, including
test directories and package/build manifests.

## antipattern-detect

Scans tracked source and documentation paths for governance antipatterns such
as temporal status/final markdown files and temporary implementation markers.
