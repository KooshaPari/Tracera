# ADR-OBS-001 Amendment 1: backend change to Tempo / Loki / Prometheus / Grafana

| Field        | Value                                                             |
| ------------ | ----------------------------------------------------------------- |
| **Status**   | Proposed (needs owner acceptance; not accepted by this document)  |
| **Date**     | 2026-10-14                                                        |
| **Amends**   | ADR-OBS-001 (Accepted 2026-08-30)                                 |
| **Proposer** | Instinct product lane, at owner's stated direction (Oct 11, 2026) |
| **Reviewer** | KooshaPari                                                        |

## Context

ADR-OBS-001 adopts OpenTelemetry and names Jaeger for traces and Prometheus for metrics, with logs as a later goal. The owner has since directed that telemetry be on every deploy, with errors auto-captured, and that the self-hosted backend be an OTel collector feeding Tempo (traces), Loki (logs) and Prometheus (metrics), viewed in Grafana, run in podman on the desk behind Cloudflare Access. As of the default branch, `crates/tracera-server/src/observability.rs` has no OTLP exporter wired, so no backend has received Tracera data yet and nothing needs migrating.

## Decision

1. The OpenTelemetry decision, W3C TraceContext, OTLP as the only export protocol and the SDK choices (Rust, Python, TypeScript) stand unchanged.
2. Replace Jaeger with **Tempo** as the trace backend.
3. Add **Loki** as the log backend. Logs move from "later goal" to Phase 1 for WARN and above, correlated with trace and span ids.
4. Keep **Prometheus** for metrics; add **Grafana** as the single UI for all three signals (replaces "Jaeger dashboard").
5. Deployment: self-hosted, single collector on the desk in podman, tailnet-only or behind Cloudflare Access. This replaces the "high-availability collector" of Phase 1 for the MVP; HA is deferred until there is more than one host or user.
6. Services never export directly to backends; they send OTLP to the collector. The browser sends through a same-origin proxy route, never directly.
7. Instrumentation details live in the Tracera OTel instrumentation spec, not in this ADR.

## Changes to ADR-OBS-001 text

- Core Components 2: "Jaeger exporter" -> "OTLP to collector, stored in Tempo".
- Core Components 4: logs via OTel log bridge to Loki, Phase 1 for WARN+.
- Rollout Plan Phase 1 / Sep 2026 line: "Jaeger/Prometheus" -> "Tempo/Loki/Prometheus/Grafana".
- Success Metrics: "Jaeger dashboard" -> "Grafana service-dependency view".
- References: add Tempo, Loki, Grafana docs; keep Jaeger only as a rejected alternative.
- Add to Alternatives Considered: Jaeger (previous choice) rejected because Tempo shares object storage and Grafana UI with Loki and Prometheus, so one stack to run on one desk host.

## Consequences

- Positive: one UI and one stack; log-to-trace linking works from the start; matches the owner's cross-project telemetry rule, so other projects can reuse it.
- Negative: three stores to run and back up on one host; Loki and Tempo retention must be sized for desk disk (set explicit retention, e.g. 7-14 days, to be confirmed by the desk lane).
- Risk: Cloudflare Access in front of Grafana must be verified; collector must not be publicly reachable.
- No code rework: exporters are OTLP, so only collector config changes.

## Open items

- Retention and storage limits (desk lane).
- Whether the amended ADR supersedes the Aug 30 rollout timeline dates (they predate the MVP push).
- Update the ADR index (`docs/governance/policy/adr_index.md`) entry description to mention the amendment.

## Sources

- ADR-OBS-001 in Tracera repo: docs/governance/ADR-OBS-001-opentelemetry-adoption.md
- Owner direction on telemetry backend: user preference record, Oct 11, 2026 (internal memory)
- crates/tracera-server/src/observability.rs (Tracera default branch)
