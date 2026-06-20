# Observability Options Research

This document summarizes the research into observability tools, comparing the current project setup against potential alternatives like Sentry, SigNoz, and Highlight.io.

## Current Setup: The "Gold Standard" Stack

The project currently uses a modular, industry-standard observability stack managed via `process-compose`.

- **Metrics**: Prometheus (Port 9090)
- **Logs**: Loki + Promtail (Port 3100)
- **Traces**: Jaeger (Port 16686 / OTLP 4317)
- **Visualization**: Grafana (Port 3000)

### Status
- **Go Backend**: Integrated with OpenTelemetry (OTEL) for tracing and Prometheus for metrics.
- **Python Backend**: Integrated with OpenTelemetry for tracing.
- **Frontend**: Basic error handling; tracing ready for integration.

---

## Alternative 1: Sentry (Error Tracking)

Sentry is a developer-first error tracking and performance monitoring platform.

- **Free Tier**: "Developer" plan includes 5,000 errors and 10,000 transactions per month.
- **Local Alternative**: **GlitchTip** (Open-source, Sentry-SDK compatible).
- **Pros**: Zero setup for SaaS, excellent error grouping, and issue management.
- **Cons**: Data leaves your server (SaaS); heavy resource requirements for self-hosting.

---

## Alternative 2: SigNoz (Unified Observability)

SigNoz is an open-source alternative to Datadog, native to OpenTelemetry.

- **Key Feature**: Unified storage (ClickHouse) for logs, metrics, and traces.
- **Pros**:
    - **Native Correlation**: Automatically links traces to logs for seamless debugging.
    - **Single UI**: Replaces Jaeger, Loki, and Grafana UIs with one interface.
    - **Performance**: ClickHouse is highly efficient for high-volume telemetry.
- **Cons**:
    - **Resource Heavy**: ClickHouse and the SigNoz stack require significant RAM (8GB+ recommended).
    - **Migration Cost**: Would require disabling existing Grafana/Prometheus configurations.

---

## Alternative 3: Highlight.io (Product-Focused Observability)

Highlight.io is a modern platform that adds "Session Replay" to the standard monitoring suite.

- **The "Superpower"**: **Session Replay**. Watch a video-like playback of what the user saw and clicked when an error occurred.
- **Pros**:
    - **Frontend Visibility**: Perfect for debugging complex UI state issues.
    - **Cohesive Product**: Integrated logs, traces, and errors.
- **Cons**:
    - **Overhead**: Recording the DOM adds a small performance cost to the frontend.
    - **Self-Hosting**: Requires ~8GB RAM and Docker setup.

---

## Comparison Matrix

| Feature | Current Setup (Grafana+) | SigNoz | Highlight.io |
| :--- | :--- | :--- | :--- |
| **Tracing** | Jaeger (OTEL) | ClickHouse (OTEL) | Built-in |
| **Logging** | Loki | ClickHouse | Built-in |
| **Metrics** | Prometheus | Built-in | Built-in |
| **Session Replay** | No | No | **Yes** |
| **Unified UI** | Partial (Grafana) | **Yes** | **Yes** |
| **Setup Complexity** | High (Modular) | Medium (Unified) | Medium (Unified) |

---

## Recommendations

### 1. Short Term: Stay with Current Stack
The current stack is already running, integrated, and "free" in terms of infrastructure. Stick with it if your focus is on backend performance and system stability.

### 2. If you need better Error Tracking: Use GlitchTip
Since the Go backend already has the Sentry SDK integrated (configurable via `SENTRY_DSN`), you can point it to a local **GlitchTip** instance for a lightweight, self-hosted error tracker that is compatible with Sentry's SDKs.

### 3. If you need better Frontend Debugging: Use Highlight.io
If your React frontend has complex state interactions that are hard to reproduce, Highlight.io's **Session Replay** is the most valuable tool to add.

### 4. For Unified APM: Use SigNoz
If you find that switching between Grafana, Jaeger, and Loki is too cumbersome, SigNoz provides the best "single-pane-of-glass" experience built on the project's existing OpenTelemetry foundation.
