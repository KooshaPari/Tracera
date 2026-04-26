# Observability Configs

Logging, metrics, tracing, and alerting configurations.

## Purpose
Standardized observability stack across services.

## Structure
```
observability/
├── logging/          # Structured logging configs
│   └── structured-json.yaml
├── metrics/          # Prometheus configs
│   └── prometheus.yml
├── tracing/          # OpenTelemetry configs
│   └── otel-collector.yml
└── alerting/         # Alert rules
    └── rules/
```

## Components
| Component | Tool | Purpose |
|-----------|------|---------|
| Logging | JSON structured logs | Application logs |
| Metrics | Prometheus | System/application metrics |
| Tracing | OpenTelemetry | Distributed tracing |
| Alerting | Alertmanager | Alert routing |

## Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `SAMPLE_RATE` | Trace sampling rate | `0.1` |
| `LOG_LEVEL` | Minimum log level | `INFO` |
| `RETENTION_DAYS` | Log retention | `30` |

## Usage
```yaml
# In your service config
observability:
  logging:
    format: json
    level: ${LOG_LEVEL}
  metrics:
    enabled: true
    port: 9090
  tracing:
    enabled: true
    sample_rate: ${SAMPLE_RATE}
```

## Related
- [scripts/](../scripts/) - Scripts to apply configs
- [configs/infra/](../configs/infra/) - Infra that emits metrics
