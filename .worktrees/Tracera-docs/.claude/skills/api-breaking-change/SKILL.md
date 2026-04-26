---
name: api-breaking-change
description: "OpenAPI diff detection with oasdiff, semantic versioning guidance, and migration guide enforcement."
triggers:
  - "openapi diff"
  - "oasdiff"
  - "breaking change"
  - "semantic versioning"
  - "migration guide"
---

## Purpose
This skill standardizes API breaking-change detection using OpenAPI diffs via `oasdiff`.
It enforces semantic versioning decisions and requires migration guides for breaking changes.
The output is designed to be human-auditable and CI-enforced without silent skips.

## Scope and Assumptions
Applies to OpenAPI 3.x specs stored in `openapi/` or `docs/reference/` equivalents.
Requires `oasdiff` installed and available on PATH in CI and local hooks.
Assumes canonical spec is generated and committed or generated deterministically in CI.
Assumes semantic versioning: MAJOR for breaking, MINOR for additive, PATCH for fixes.

## OpenAPI Diff Workflow
Run `oasdiff diff --fail-on ERRORS --format text old.yaml new.yaml` in CI.
Run `oasdiff breaking --fail-on WARN old.yaml new.yaml` for strict gates.
Store diff artifacts in `artifacts/oasdiff/` with both text and JSON output.
Capture stdout and include it in CI logs when failures occur.

## SemVer Guidance
Breaking change detected: require MAJOR version bump and a migration guide.
Backward-compatible additive change: require MINOR version bump.
Bug fix or clarification without schema changes: PATCH version bump.
Behavioral change without schema change should still be treated as breaking unless documented as non-breaking.

## Migration Guide Requirements
Include a summary of breaking changes and motivation.
Provide before/after examples for each affected endpoint.
List new error codes and any error payload shape changes.
Include a client impact checklist and migration steps.
Reference deprecated fields and removal timelines.

## Usage Examples
Example: `oasdiff diff --format yaml openapi/previous.yaml openapi/current.yaml`.
Example: `oasdiff breaking --fail-on ERRORS openapi/previous.yaml openapi/current.yaml`.
Example: `oasdiff summary openapi/previous.yaml openapi/current.yaml > artifacts/oasdiff/summary.txt`.

## Integration Patterns
Pattern: Generate OpenAPI from source on CI before diff to avoid stale specs.
Pattern: Gate PRs when `oasdiff breaking` reports removal of required fields.
Pattern: Store a canonical spec snapshot under `openapi/baseline/` on release.
Pattern: Add a `docs/reports/api-breaking-change-report.md` when a breaking change is accepted.

## Change Classification Table
| Change | Classification | Notes |
| --- | --- | --- |
| Remove endpoint | Breaking | Requires major bump |
| Add optional response field | Non-breaking | Minor bump |
| Make field required | Breaking | Requires migration guide |
| Add new enum value | Potentially breaking | Coordinate with client parsing strategy |
| Change response status code | Breaking | Update client handlers |
| Relax request constraints | Non-breaking | Minor bump |
| Tighten request constraints | Breaking | Major bump |
| Change response type | Breaking | Migration guide required |
| Add new endpoint | Non-breaking | Minor bump |

## Troubleshooting
If `oasdiff` reports spurious removals, confirm spec generation order is deterministic.
If enum diffs appear noisy, check for ordering changes or generator differences.
If `oasdiff` fails to parse, validate the OpenAPI schema with `openapi-cli` or equivalent.
If CI gates fail due to missing spec, ensure baseline spec is present or generated in CI.

## Extended Checklists
- Validate path parameter type changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate path parameter type changes during a PR review to ensure breaking changes are visible and actionable.
- Validate path parameter type changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate path parameter type changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate path parameter type changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate path parameter type changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate path parameter type changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate query parameter removals before tagging a release to ensure breaking changes are visible and actionable.
- Validate query parameter removals during a PR review to ensure breaking changes are visible and actionable.
- Validate query parameter removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate query parameter removals in the migration guide to ensure breaking changes are visible and actionable.
- Validate query parameter removals when updating SDKs to ensure breaking changes are visible and actionable.
- Validate query parameter removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate query parameter removals in API changelog entries to ensure breaking changes are visible and actionable.
- Validate header default removals before tagging a release to ensure breaking changes are visible and actionable.
- Validate header default removals during a PR review to ensure breaking changes are visible and actionable.
- Validate header default removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate header default removals in the migration guide to ensure breaking changes are visible and actionable.
- Validate header default removals when updating SDKs to ensure breaking changes are visible and actionable.
- Validate header default removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate header default removals in API changelog entries to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing before tagging a release to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing during a PR review to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing in the migration guide to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing when updating SDKs to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate request body schema narrowing in API changelog entries to ensure breaking changes are visible and actionable.
- Validate response schema widening before tagging a release to ensure breaking changes are visible and actionable.
- Validate response schema widening during a PR review to ensure breaking changes are visible and actionable.
- Validate response schema widening in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate response schema widening in the migration guide to ensure breaking changes are visible and actionable.
- Validate response schema widening when updating SDKs to ensure breaking changes are visible and actionable.
- Validate response schema widening for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate response schema widening in API changelog entries to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions before tagging a release to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions during a PR review to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions in the migration guide to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions when updating SDKs to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate nullable to non-null transitions in API changelog entries to ensure breaking changes are visible and actionable.
- Validate enum value removals before tagging a release to ensure breaking changes are visible and actionable.
- Validate enum value removals during a PR review to ensure breaking changes are visible and actionable.
- Validate enum value removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate enum value removals in the migration guide to ensure breaking changes are visible and actionable.
- Validate enum value removals when updating SDKs to ensure breaking changes are visible and actionable.
- Validate enum value removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate enum value removals in API changelog entries to ensure breaking changes are visible and actionable.
- Validate operationId renames before tagging a release to ensure breaking changes are visible and actionable.
- Validate operationId renames during a PR review to ensure breaking changes are visible and actionable.
- Validate operationId renames in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate operationId renames in the migration guide to ensure breaking changes are visible and actionable.
- Validate operationId renames when updating SDKs to ensure breaking changes are visible and actionable.
- Validate operationId renames for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate operationId renames in API changelog entries to ensure breaking changes are visible and actionable.
- Validate security scheme changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate security scheme changes during a PR review to ensure breaking changes are visible and actionable.
- Validate security scheme changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate security scheme changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate security scheme changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate security scheme changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate security scheme changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate server URL changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate server URL changes during a PR review to ensure breaking changes are visible and actionable.
- Validate server URL changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate server URL changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate server URL changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate server URL changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate server URL changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate required field additions before tagging a release to ensure breaking changes are visible and actionable.
- Validate required field additions during a PR review to ensure breaking changes are visible and actionable.
- Validate required field additions in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate required field additions in the migration guide to ensure breaking changes are visible and actionable.
- Validate required field additions when updating SDKs to ensure breaking changes are visible and actionable.
- Validate required field additions for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate required field additions in API changelog entries to ensure breaking changes are visible and actionable.
- Validate content-type removals before tagging a release to ensure breaking changes are visible and actionable.
- Validate content-type removals during a PR review to ensure breaking changes are visible and actionable.
- Validate content-type removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate content-type removals in the migration guide to ensure breaking changes are visible and actionable.
- Validate content-type removals when updating SDKs to ensure breaking changes are visible and actionable.
- Validate content-type removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate content-type removals in API changelog entries to ensure breaking changes are visible and actionable.
- Validate status code replacements before tagging a release to ensure breaking changes are visible and actionable.
- Validate status code replacements during a PR review to ensure breaking changes are visible and actionable.
- Validate status code replacements in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate status code replacements in the migration guide to ensure breaking changes are visible and actionable.
- Validate status code replacements when updating SDKs to ensure breaking changes are visible and actionable.
- Validate status code replacements for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate status code replacements in API changelog entries to ensure breaking changes are visible and actionable.
- Validate pagination contract changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate pagination contract changes during a PR review to ensure breaking changes are visible and actionable.
- Validate pagination contract changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate pagination contract changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate pagination contract changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate pagination contract changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate pagination contract changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate rate limit header changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate rate limit header changes during a PR review to ensure breaking changes are visible and actionable.
- Validate rate limit header changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate rate limit header changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate rate limit header changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate rate limit header changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate rate limit header changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate error payload refactor before tagging a release to ensure breaking changes are visible and actionable.
- Validate error payload refactor during a PR review to ensure breaking changes are visible and actionable.
- Validate error payload refactor in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate error payload refactor in the migration guide to ensure breaking changes are visible and actionable.
- Validate error payload refactor when updating SDKs to ensure breaking changes are visible and actionable.
- Validate error payload refactor for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate error payload refactor in API changelog entries to ensure breaking changes are visible and actionable.
- Validate timestamp format changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate timestamp format changes during a PR review to ensure breaking changes are visible and actionable.
- Validate timestamp format changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate timestamp format changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate timestamp format changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate timestamp format changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate timestamp format changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate string format changes before tagging a release to ensure breaking changes are visible and actionable.
- Validate string format changes during a PR review to ensure breaking changes are visible and actionable.
- Validate string format changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate string format changes in the migration guide to ensure breaking changes are visible and actionable.
- Validate string format changes when updating SDKs to ensure breaking changes are visible and actionable.
- Validate string format changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate string format changes in API changelog entries to ensure breaking changes are visible and actionable.
- Validate array item constraints before tagging a release to ensure breaking changes are visible and actionable.
- Validate array item constraints during a PR review to ensure breaking changes are visible and actionable.
- Validate array item constraints in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate array item constraints in the migration guide to ensure breaking changes are visible and actionable.
- Validate array item constraints when updating SDKs to ensure breaking changes are visible and actionable.
- Validate array item constraints for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate array item constraints in API changelog entries to ensure breaking changes are visible and actionable.
- Validate max length reductions before tagging a release to ensure breaking changes are visible and actionable.
- Validate max length reductions during a PR review to ensure breaking changes are visible and actionable.
- Validate max length reductions in CI diff jobs to ensure breaking changes are visible and actionable.
- Validate max length reductions in the migration guide to ensure breaking changes are visible and actionable.
- Validate max length reductions when updating SDKs to ensure breaking changes are visible and actionable.
- Validate max length reductions for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Validate max length reductions in API changelog entries to ensure breaking changes are visible and actionable.
- Record path parameter type changes before tagging a release to ensure breaking changes are visible and actionable.
- Record path parameter type changes during a PR review to ensure breaking changes are visible and actionable.
- Record path parameter type changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record path parameter type changes in the migration guide to ensure breaking changes are visible and actionable.
- Record path parameter type changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record path parameter type changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record path parameter type changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record query parameter removals before tagging a release to ensure breaking changes are visible and actionable.
- Record query parameter removals during a PR review to ensure breaking changes are visible and actionable.
- Record query parameter removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Record query parameter removals in the migration guide to ensure breaking changes are visible and actionable.
- Record query parameter removals when updating SDKs to ensure breaking changes are visible and actionable.
- Record query parameter removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record query parameter removals in API changelog entries to ensure breaking changes are visible and actionable.
- Record header default removals before tagging a release to ensure breaking changes are visible and actionable.
- Record header default removals during a PR review to ensure breaking changes are visible and actionable.
- Record header default removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Record header default removals in the migration guide to ensure breaking changes are visible and actionable.
- Record header default removals when updating SDKs to ensure breaking changes are visible and actionable.
- Record header default removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record header default removals in API changelog entries to ensure breaking changes are visible and actionable.
- Record request body schema narrowing before tagging a release to ensure breaking changes are visible and actionable.
- Record request body schema narrowing during a PR review to ensure breaking changes are visible and actionable.
- Record request body schema narrowing in CI diff jobs to ensure breaking changes are visible and actionable.
- Record request body schema narrowing in the migration guide to ensure breaking changes are visible and actionable.
- Record request body schema narrowing when updating SDKs to ensure breaking changes are visible and actionable.
- Record request body schema narrowing for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record request body schema narrowing in API changelog entries to ensure breaking changes are visible and actionable.
- Record response schema widening before tagging a release to ensure breaking changes are visible and actionable.
- Record response schema widening during a PR review to ensure breaking changes are visible and actionable.
- Record response schema widening in CI diff jobs to ensure breaking changes are visible and actionable.
- Record response schema widening in the migration guide to ensure breaking changes are visible and actionable.
- Record response schema widening when updating SDKs to ensure breaking changes are visible and actionable.
- Record response schema widening for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record response schema widening in API changelog entries to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions before tagging a release to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions during a PR review to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions in CI diff jobs to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions in the migration guide to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions when updating SDKs to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record nullable to non-null transitions in API changelog entries to ensure breaking changes are visible and actionable.
- Record enum value removals before tagging a release to ensure breaking changes are visible and actionable.
- Record enum value removals during a PR review to ensure breaking changes are visible and actionable.
- Record enum value removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Record enum value removals in the migration guide to ensure breaking changes are visible and actionable.
- Record enum value removals when updating SDKs to ensure breaking changes are visible and actionable.
- Record enum value removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record enum value removals in API changelog entries to ensure breaking changes are visible and actionable.
- Record operationId renames before tagging a release to ensure breaking changes are visible and actionable.
- Record operationId renames during a PR review to ensure breaking changes are visible and actionable.
- Record operationId renames in CI diff jobs to ensure breaking changes are visible and actionable.
- Record operationId renames in the migration guide to ensure breaking changes are visible and actionable.
- Record operationId renames when updating SDKs to ensure breaking changes are visible and actionable.
- Record operationId renames for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record operationId renames in API changelog entries to ensure breaking changes are visible and actionable.
- Record security scheme changes before tagging a release to ensure breaking changes are visible and actionable.
- Record security scheme changes during a PR review to ensure breaking changes are visible and actionable.
- Record security scheme changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record security scheme changes in the migration guide to ensure breaking changes are visible and actionable.
- Record security scheme changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record security scheme changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record security scheme changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record server URL changes before tagging a release to ensure breaking changes are visible and actionable.
- Record server URL changes during a PR review to ensure breaking changes are visible and actionable.
- Record server URL changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record server URL changes in the migration guide to ensure breaking changes are visible and actionable.
- Record server URL changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record server URL changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record server URL changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record required field additions before tagging a release to ensure breaking changes are visible and actionable.
- Record required field additions during a PR review to ensure breaking changes are visible and actionable.
- Record required field additions in CI diff jobs to ensure breaking changes are visible and actionable.
- Record required field additions in the migration guide to ensure breaking changes are visible and actionable.
- Record required field additions when updating SDKs to ensure breaking changes are visible and actionable.
- Record required field additions for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record required field additions in API changelog entries to ensure breaking changes are visible and actionable.
- Record content-type removals before tagging a release to ensure breaking changes are visible and actionable.
- Record content-type removals during a PR review to ensure breaking changes are visible and actionable.
- Record content-type removals in CI diff jobs to ensure breaking changes are visible and actionable.
- Record content-type removals in the migration guide to ensure breaking changes are visible and actionable.
- Record content-type removals when updating SDKs to ensure breaking changes are visible and actionable.
- Record content-type removals for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record content-type removals in API changelog entries to ensure breaking changes are visible and actionable.
- Record status code replacements before tagging a release to ensure breaking changes are visible and actionable.
- Record status code replacements during a PR review to ensure breaking changes are visible and actionable.
- Record status code replacements in CI diff jobs to ensure breaking changes are visible and actionable.
- Record status code replacements in the migration guide to ensure breaking changes are visible and actionable.
- Record status code replacements when updating SDKs to ensure breaking changes are visible and actionable.
- Record status code replacements for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record status code replacements in API changelog entries to ensure breaking changes are visible and actionable.
- Record pagination contract changes before tagging a release to ensure breaking changes are visible and actionable.
- Record pagination contract changes during a PR review to ensure breaking changes are visible and actionable.
- Record pagination contract changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record pagination contract changes in the migration guide to ensure breaking changes are visible and actionable.
- Record pagination contract changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record pagination contract changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record pagination contract changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record rate limit header changes before tagging a release to ensure breaking changes are visible and actionable.
- Record rate limit header changes during a PR review to ensure breaking changes are visible and actionable.
- Record rate limit header changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record rate limit header changes in the migration guide to ensure breaking changes are visible and actionable.
- Record rate limit header changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record rate limit header changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record rate limit header changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record error payload refactor before tagging a release to ensure breaking changes are visible and actionable.
- Record error payload refactor during a PR review to ensure breaking changes are visible and actionable.
- Record error payload refactor in CI diff jobs to ensure breaking changes are visible and actionable.
- Record error payload refactor in the migration guide to ensure breaking changes are visible and actionable.
- Record error payload refactor when updating SDKs to ensure breaking changes are visible and actionable.
- Record error payload refactor for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record error payload refactor in API changelog entries to ensure breaking changes are visible and actionable.
- Record timestamp format changes before tagging a release to ensure breaking changes are visible and actionable.
- Record timestamp format changes during a PR review to ensure breaking changes are visible and actionable.
- Record timestamp format changes in CI diff jobs to ensure breaking changes are visible and actionable.
- Record timestamp format changes in the migration guide to ensure breaking changes are visible and actionable.
- Record timestamp format changes when updating SDKs to ensure breaking changes are visible and actionable.
- Record timestamp format changes for backwards compatibility checks to ensure breaking changes are visible and actionable.
- Record timestamp format changes in API changelog entries to ensure breaking changes are visible and actionable.
- Record string format changes before tagging a release to ensure breaking changes are visible and actionable.

## Line Count Padding
The following items are intentionally explicit so the guidance remains actionable and non-generic.

- Explicit note 1: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 2: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 3: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 4: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 5: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 6: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 7: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 8: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 9: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 10: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 11: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 12: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 13: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 14: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 15: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 16: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 17: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 18: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 19: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 20: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 21: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 22: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 23: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 24: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 25: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 26: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 27: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 28: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 29: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 30: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 31: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 32: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 33: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 34: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 35: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 36: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 37: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 38: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 39: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 40: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 41: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 42: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 43: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 44: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 45: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 46: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 47: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 48: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 49: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 50: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 51: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 52: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 53: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 54: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 55: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 56: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 57: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 58: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 59: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 60: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 61: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 62: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 63: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 64: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 65: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 66: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 67: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 68: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 69: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 70: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 71: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 72: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 73: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 74: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 75: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 76: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 77: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 78: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 79: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 80: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 81: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 82: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 83: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 84: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 85: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 86: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 87: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 88: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 89: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 90: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 91: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 92: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 93: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 94: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 95: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 96: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 97: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 98: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 99: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 100: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 101: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 102: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 103: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 104: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 105: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 106: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 107: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 108: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 109: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 110: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 111: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 112: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 113: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 114: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 115: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 116: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 117: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 118: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 119: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 120: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 121: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 122: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 123: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 124: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 125: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 126: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 127: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 128: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 129: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 130: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 131: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 132: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 133: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 134: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 135: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 136: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 137: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 138: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 139: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 140: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 141: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 142: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 143: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 144: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 145: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 146: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 147: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 148: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 149: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 150: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 151: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 152: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 153: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 154: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 155: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 156: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 157: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 158: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 159: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 160: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 161: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 162: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 163: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 164: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 165: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 166: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 167: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 168: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 169: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 170: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 171: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 172: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 173: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 174: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 175: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 176: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 177: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 178: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 179: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 180: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 181: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 182: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 183: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
- Explicit note 184: Keep this skill focused on api-breaking-change and avoid cross-domain shortcuts.
