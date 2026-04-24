> Historical note: this document is retained only for archive compatibility. The
> active tracing path is the shared Phenotype collector, Grafana Alloy, and
> Grafana Tempo.

# Legacy Jaeger Distributed Tracing Implementation Summary

This file preserves the original Jaeger-era implementation notes for old links
and historical review. It is not current operating guidance.

## Current Path

- OTLP spans export to the shared collector endpoint.
- Grafana Alloy handles local collection and forwarding.
- Grafana Tempo stores traces for Grafana inspection.

## Archived Context

The original Jaeger service, environment variables, and Docker Compose wiring
described in older revisions have been superseded by the Tempo-backed stack.

