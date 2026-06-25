# Traceability Matrix

The 24-endpoint governance baseline is now tracked here:

- [`docs/governance/policy/endpoint_traceability_map.md`](governance/policy/endpoint_traceability_map.md)
- [`docs/governance/policy/coverage_matrix_self_application.md`](governance/policy/coverage_matrix_self_application.md)
- [`docs/FEATURE_INVENTORY.md`](FEATURE_INVENTORY.md)

## Governance evidence status

| Item | Status |
|---|---|
| Route inventory completeness | ✅ Mapped in endpoint policy |
| FR→endpoint mapping | ✅ Mapped in endpoint policy |
| Test linkage capture | ⚠ Partial (limited test fixtures exist for governance tests) |
| Unmounted endpoint audit warning | ✅ Captured in policy rows |

`FR-API` routes under `/api/v1` are now explicitly documented and should be used
as the minimum evidence set before the next audit gate.
