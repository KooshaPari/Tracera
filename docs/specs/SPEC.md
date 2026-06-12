# Tracera Observability SLO Contract

## Status

Draft 2026-06-11.

## Scope

This contract defines production service level objectives for Tracera's user-facing API,
background workers, and telemetry pipeline. Each SLO is evaluated over a rolling 28-day
window unless a narrower window is called out below.

## Latency

- API request latency: 99% of successful HTTP requests complete within 500 ms, measured
  from request receipt to response write with `http.server.duration`.
- Write-path latency: 95% of requirement, trace, and evidence mutations complete within
  750 ms, measured at the service boundary with `tracera.operation.duration`.
- Background job latency: 95% of queued jobs start within 60 seconds and finish within
  their declared timeout, measured with `tracera.job.queue_delay` and
  `tracera.job.duration`.

## Error

- API availability: 99.9% of non-health HTTP requests return a non-5xx response.
- Mutation correctness: 99.95% of accepted mutations finish without an application error,
  retry exhaustion, or partial-write compensation event.
- Telemetry export reliability: 99% of spans and metrics accepted by the process are
  exported or intentionally dropped by sampling policy, not by exporter failure.

## Saturation

- CPU saturation: backend CPU utilization remains below 80% for 95% of 5-minute windows.
- Memory saturation: resident memory remains below 85% of the configured container or host
  limit for 95% of 5-minute windows.
- Queue saturation: worker queues stay below 80% of configured capacity for 99% of
  5-minute windows, and oldest pending job age remains below 5 minutes.
- Telemetry saturation: collector/exporter queue utilization stays below 80% for 99% of
  5-minute windows, with exporter failure rate below 1%.

## Metric Contract

Instrumentation must emit stable service, environment, route, operation, and status labels
with bounded cardinality. Alert rules and dashboards consume these canonical signals:

- `http.server.duration`
- `http.server.request.count`
- `tracera.operation.duration`
- `tracera.operation.errors`
- `tracera.job.queue_delay`
- `tracera.job.duration`
- `tracera.job.errors`
- `process.cpu.utilization`
- `process.memory.usage`
- `tracera.queue.utilization`
- `otelcol_exporter_send_failed_spans`
- `otelcol_exporter_queue_size`

## Alerting Contract

Page on fast-burn SLO violations that threaten the 28-day error budget within 2 hours.
Create ticket-only alerts for slow-burn violations, saturation over trend thresholds, and
telemetry export degradation that does not yet affect user-facing availability.
