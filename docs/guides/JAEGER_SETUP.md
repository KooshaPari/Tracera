# Shared Tracing Setup Guide

This file is retained for compatibility with older Tracera-recovered references.
The supported tracing path is the shared Phenotype collector model:
applications emit OTLP spans to the shared collector endpoint, Grafana Alloy
handles local collection and forwarding, and Grafana Tempo stores traces for
Grafana UI inspection.

## Compatibility Only

- Legacy wrapper environment names may still appear in older scripts.
- Legacy process names may still appear in historical scripts.
- This file does not define the current tracing runtime.

## Canonical Path

Use the shared observability stack and current collector settings documented in
the shared Phenotype observability materials.
