# Tracera Governance

This directory is the canonical navigation point for governance evidence.

- [`policy/endpoint_traceability_map.md`](policy/endpoint_traceability_map.md)  
  FR→endpoint→test linkage table, source-of-truth for the 24/26 API audit route set.
- [`policy/coverage_matrix_self_application.md`](policy/coverage_matrix_self_application.md)  
  Self-application map that ties each control to code/docs evidence.
- [`policy/adr_index.md`](policy/adr_index.md)  
  ADR inventory and references.

Source oracle for API scope and endpoint lineage:

- [`docs/FEATURE_INVENTORY.md`](../FEATURE_INVENTORY.md)

Recommended runbook:

1. Confirm endpoint lineage in `endpoint_traceability_map.md`.
2. Add test linkage evidence in the same file.
3. Mirror the same status in `coverage_matrix_self_application.md`.
4. Update `adr_index.md` when governance or security rationale changes.

