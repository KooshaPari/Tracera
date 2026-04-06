# Tracera - AI Agent Context

## Project Overview

Tracera is an AI-powered distributed tracing platform for the Phenotype ecosystem.

## Tech Stack

- **Backend**: Rust (Tokio, gRPC)
- **Frontend**: React + TypeScript
- **AI**: Python (scikit-learn, ONNX Runtime)
- **Storage**: ClickHouse (hot), S3 (cold)

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SDKs       │───▶│  Collector  │───▶│  Storage    │
│ (Auto-inst) │    │  (Rust/gRPC)│    │  (ClickHouse│
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
                                       ┌─────────────┐
                                       │  Query API  │
                                       │  (Rust)     │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  AI Engine  │
                                       │  (Python)   │
                                       └─────────────┘
```

## Key Directories

```
.
├── src/                    # Rust collector
├── sdk/                    # Language SDKs
│   ├── rust/
│   ├── python/
│   └── typescript/
├── web/                    # React frontend
├── ai/                     # ML models
├── tests/                  # Integration tests
└── docs/                   # Documentation
```

## AI Agent Instructions

### Before Coding

1. Read PRD.md for requirements
2. Check FR specs in specs/
3. Run validate_governance.py

### Coding Standards

- Rust: Use tracing crate for logging
- All new code needs #[trace_to("FR-TRAC-XXX")] annotations
- p99 latency must stay < 5ms
- Add metrics for all new operations

### Testing

- Unit tests: `cargo test`
- Integration: `cargo test --features integration`
- Load test: `make bench`

### Validation

```bash
# Check all validations pass
python3 validate_governance.py

# Check FR coverage
cd ../AgilePlus && ./bin/ptrace analyze --path ../Tracera
```

## FRs (Functional Requirements)

| ID | Title | Status |
|----|-------|--------|
| FR-TRAC-001 | Span Ingestion API | ✅ Specified |
| FR-TRAC-002 | Trace Visualization UI | ✅ Specified |
| FR-TRAC-003 | AI Anomaly Detection | 🟡 Draft |
| FR-TRAC-004 | Alerting System | 🟡 Draft |
| FR-TRAC-005 | Historical Search | 🟡 Draft |
| FR-TRAC-006 | Custom Dashboards | 🟡 Draft |

## Integration Points

- **phenotype-logging**: Structured logs with trace context
- **phenotype-metrics**: Metrics correlation with traces
- **phenotype-config**: Runtime configuration

## Performance Budget

| Operation | Target | Current |
|-----------|--------|---------|
| Span ingest | < 1ms | 0.8ms |
| Trace query | < 100ms | 45ms |
| AI inference | < 10ms | 8ms |

---

**Last Updated:** 2026-04-04
