> Historical note: this document preserves the pre-Phenotype observability stack. The active org path is the shared collector, Grafana Alloy, and Grafana Tempo. Treat Jaeger and Promtail references below as legacy context only.

# Observability Infrastructure Guide

## The Three Pillars of Observability

### 1. Distributed Tracing
**Purpose:** Track requests across services
**Tools:** OpenTelemetry + Jaeger/Tempo

### 2. Structured Logging
**Purpose:** Understand what happened
**Tools:** Logrus (Go), Structlog (Python), Winston (TypeScript)

### 3. Metrics & Monitoring
**Purpose:** Measure system health
**Tools:** Prometheus + Grafana

## 1. DISTRIBUTED TRACING

### OpenTelemetry Setup (Go)

```go
// backend/internal/observability/tracing.go
package observability

import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/jaeger/otlp"
    "go.opentelemetry.io/otel/sdk/resource"
    "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
)

func InitTracing() (*trace.TracerProvider, error) {
    exporter, err := otlp.New(context.Background())
    if err != nil {
        return nil, err
    }

    tp := trace.NewTracerProvider(
        trace.WithBatcher(exporter),
        trace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String("tracertm-backend"),
        )),
    )

    otel.SetTracerProvider(tp)
    return tp, nil
}
```

### Using Traces

```go
// backend/internal/handlers/project_handler.go
func (h *ProjectHandler) CreateProject(c echo.Context) error {
    ctx := c.Request().Context()
    tracer := otel.Tracer("tracertm")
    
    ctx, span := tracer.Start(ctx, "CreateProject")
    defer span.End()
    
    // Add attributes
    span.SetAttributes(
        attribute.String("project.name", req.Name),
        attribute.String("user.id", userID),
    )
    
    // Call service
    project, err := h.service.CreateProject(ctx, req)
    if err != nil {
        span.RecordError(err)
        return err
    }
    
    return c.JSON(http.StatusCreated, project)
}
```

### Trace Context Propagation

```go
// Automatically propagate trace context across services
import "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

client := &http.Client{
    Transport: otelhttp.NewTransport(http.DefaultTransport),
}

// Trace context automatically included in requests
resp, err := client.Do(req)
```

## 2. STRUCTURED LOGGING

### Python with Structlog

```python
# cli/tracertm/logging.py
import structlog
import logging

def setup_logging(debug: bool = False):
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()

# Usage
logger.info("project_created", project_id="p123", user_id="u456")
logger.error("project_creation_failed", error="validation_error", details={...})
```

### Go with Logrus

```go
// backend/internal/observability/logging.go
import "github.com/sirupsen/logrus"

func InitLogging(debug bool) {
    log := logrus.New()
    log.SetFormatter(&logrus.JSONFormatter{})
    
    if debug {
        log.SetLevel(logrus.DebugLevel)
    } else {
        log.SetLevel(logrus.InfoLevel)
    }
}

// Usage
log.WithFields(logrus.Fields{
    "project_id": projectID,
    "user_id": userID,
}).Info("Project created")
```

### TypeScript with Winston

```typescript
// frontend/src/utils/logger.ts
import winston from 'winston'

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})

// Usage
logger.info('Project created', { projectId: 'p123', userId: 'u456' })
logger.error('Project creation failed', { error: 'validation_error' })
```

## 3. METRICS & MONITORING

### Prometheus Metrics (Go)

```go
// backend/internal/observability/metrics.go
import "github.com/prometheus/client_golang/prometheus"

var (
    projectsCreated = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "tracertm_projects_created_total",
            Help: "Total number of projects created",
        },
        []string{"status"},
    )
    
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "tracertm_request_duration_seconds",
            Help: "Request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
    
    cacheHitRate = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "tracertm_cache_hit_rate",
            Help: "Cache hit rate",
        },
        []string{"cache_name"},
    )
)

func init() {
    prometheus.MustRegister(projectsCreated)
    prometheus.MustRegister(requestDuration)
    prometheus.MustRegister(cacheHitRate)
}
```

### Using Metrics

```go
// Record metric
projectsCreated.WithLabelValues("success").Inc()

// Measure duration
start := time.Now()
// ... do work ...
requestDuration.WithLabelValues("POST", "/projects").Observe(time.Since(start).Seconds())

// Set gauge
cacheHitRate.WithLabelValues("redis").Set(0.95)
```

### Grafana Dashboard

```yaml
# monitoring/grafana/dashboard.json
{
  "dashboard": {
    "title": "TraceRTM Metrics",
    "panels": [
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(tracertm_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Request Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, tracertm_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(tracertm_errors_total[1m])"
          }
        ]
      }
    ]
  }
}
```

## 4. CORRELATION IDS

### Propagate Context Across Services

```go
// backend/internal/middleware/correlation_id.go
func CorrelationIDMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        correlationID := c.Request().Header.Get("X-Correlation-ID")
        if correlationID == "" {
            correlationID = uuid.New().String()
        }
        
        c.Set("correlation_id", correlationID)
        c.Response().Header().Set("X-Correlation-ID", correlationID)
        
        return next(c)
    }
}
```

### Use in Logs and Traces

```go
correlationID := c.Get("correlation_id").(string)

log.WithFields(logrus.Fields{
    "correlation_id": correlationID,
    "project_id": projectID,
}).Info("Project created")

span.SetAttributes(
    attribute.String("correlation_id", correlationID),
)
```

## 5. ALERTING

### Prometheus Alert Rules

```yaml
# monitoring/prometheus/alerts.yml
groups:
  - name: tracertm
    rules:
      - alert: HighErrorRate
        expr: rate(tracertm_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: SlowRequests
        expr: histogram_quantile(0.95, tracertm_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "Slow requests detected"
          
      - alert: LowCacheHitRate
        expr: tracertm_cache_hit_rate < 0.8
        for: 10m
        annotations:
          summary: "Low cache hit rate"
```

## 6. IMPLEMENTATION CHECKLIST

- [ ] Setup OpenTelemetry in Go backend
- [ ] Setup Jaeger for trace collection
- [ ] Configure structured logging (Logrus)
- [ ] Setup Prometheus metrics
- [ ] Create Grafana dashboards
- [ ] Add correlation IDs
- [ ] Setup alert rules
- [ ] Configure log aggregation (ELK/Loki)
- [ ] Add APM (Application Performance Monitoring)
- [ ] Setup health checks

## Summary

Observability enables:
- ✅ Understand system behavior
- ✅ Debug production issues
- ✅ Monitor performance
- ✅ Detect anomalies
- ✅ Improve reliability

**Effort:** 8-10 hours
**Benefit:** Production-grade observability
**ROI:** Very High ✅

