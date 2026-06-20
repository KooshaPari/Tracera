# Distributed Tracing Implementation Guide

This guide is retained for compatibility with older Tracera-recovered
references. The supported tracing model is the shared Phenotype collector
path: OTLP instrumentation exports to the shared collector endpoint, Grafana
Alloy handles local collection, and Grafana Tempo backs Grafana trace search.

## Compatibility Only

- Legacy wrapper names may still appear in older launch scripts.
- This guide does not describe the current tracing runtime.
- New examples should use the shared collector endpoint and the
  Grafana Alloy / Tempo model.

## Canonical Path

Refer to the shared observability stack for current setup details.
