# Distributed Tracing - Quick Reference

This quick reference is retained for compatibility with older Tracera-recovered
materials. The supported tracing model is the shared Phenotype collector path:
OTLP spans export to the shared collector endpoint, Grafana Alloy handles local
collection, and Grafana Tempo stores traces for Grafana.

## Compatibility Only

- Legacy wrapper names may still exist in older scripts.
- Do not treat this file as a guide for the current tracing runtime.
- Keep legacy references limited to compatibility notes.

## Canonical Path

Use the shared observability stack for current setup, trace viewing, and
troubleshooting.
