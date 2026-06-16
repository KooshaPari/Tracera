# Traceability Matrix — Top 5 Features

| Requirement | Source | Test | Status |
|---|---|---|---|
| `FR-001` — Typed-graph schema contract (`GraphPort`) | `src/tracertm/ports/graph_contract.py` | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |
| `FR-002` — Pluggable agreement scorer (`ScorerPort`) | `src/tracertm/ports/scorer.py` | `tests/unit/ports/test_scorer.py` | ✅ Landed |
| `FR-003` — Traceability REST API router | `src/tracertm/api/routers/traceability.py` | `tests/test_traceability_api.py` | ✅ Landed |
| `FR-004` — ML model registry | `src/tracertm/ml/model_registry.py` | `src/tracertm/ml/test_model_registry.py` | ✅ Landed |
| `FR-005` — Performance matrix build & export | `src/tracertm/performance/matrix.py` | `tests/performance/test_matrix_build_benchmark.py` | ✅ Landed |

*Last updated: integration/consolidate branch.*
