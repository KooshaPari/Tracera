# ADR-OBS-001: Adoption of OpenTelemetry for Distributed Tracing and Metrics

| Field        | Value                                     |
|--------------|-------------------------------------------|
| **Status**   | Accepted                                  |
| **Date**     | 2026-08-30                                |
| **Deciders** | Tracera Engineering, SRE                  |

## Context

As Tracera scales to handle high-volume data pipelines, our current observability stack—composed of ad-hoc logging and legacy internal metrics—has reached its limits. We face several critical challenges:

- **Observability Gaps**: We lack a unified view of request flows across service boundaries. Debugging production issues often requires manually correlating timestamps across disparate log files, which is time-consuming and error-prone.
- **Vendor Lock-in**: Existing metrics solutions are tightly coupled with our current cloud provider, making portability difficult.
- **Inconsistent Instrumentation**: There is no standardized way for services to expose performance data, leading to blind spots in latency and error rate monitoring.
- **Scalability Concerns**: The current logging infrastructure struggles to keep up with the increasing throughput of the platform, leading to dropped data and incomplete audits.

We need a robust, open-standard framework that can provide end-to-end visibility without introducing significant performance overhead or vendor dependency. The goal is to move from a reactive debugging posture to a proactive monitoring stance where potential issues are identified before they impact customers.

## Decision

We will adopt **OpenTelemetry (OTel)** as the primary framework for all future observability instrumentation across the Tracera stack.

### Core Components:
1.  **OTel SDK**: We will instrument all new and existing core services using the official OTel SDKs (Rust, Python, and TypeScript).
2.  **Traces**: We will deploy a **Jaeger** exporter to collect, store, and visualize distributed traces. This will allow us to pinpoint latency bottlenecks and service dependencies in real-time.
3.  **Metrics**: We will use **Prometheus** as the metrics backend. OTel will export standard metrics (counters, histograms, gauges) that will be scraped by our Prometheus instances for alerting and dashboarding.
4.  **Logs**: While not the primary focus of this ADR, we will work towards integrating logs with traces using OTel's log bridge capabilities to enable "logs in context."

### Configuration:
- Instrumentation will be auto-instrumented where possible to minimize initial friction.
- Custom spans will be defined for critical business logic and data processing stages.
- We will standardize on W3C TraceContext for context propagation across services.

### Alternatives Considered:
- **Proprietary APM Tools (e.g., Datadog, New Relic)**: While offering a quick start, these lead to high licensing costs and deep vendor lock-in.
- **Custom In-house Solution**: Building a custom solution would require significant engineering overhead and would lack the community-driven integrations of OTel.
- **ELK Stack (Logs only)**: Provides great log analysis but lacks the native distributed tracing and structured metrics capabilities required for our high-throughput environment.

## Scope

This ADR applies to all services within the Tracera platform, including data ingestion, transformation, and API layers. It covers distributed tracing and infrastructure metrics. Application-level business metrics (e.g., revenue tracking) are outside the scope of this specific decision but will eventually follow the same export patterns.

### Positive:
- **Unified Observability**: Provides a single pane of glass for traces, metrics, and (eventually) logs.
- **Open Standard**: Eliminates vendor lock-in and allows us to switch backends if needed.
- **Improved Debugging**: Distributed tracing will significantly reduce MTTR (Mean Time To Resolution) by visualizing request lifecycles.
- **Community Support**: Leverages a massive ecosystem of libraries and integrations.

### Negative:
- **Resource Overhead**: The OTel Collector and exporters will consume additional CPU and memory resources.
- **Learning Curve**: Engineering teams will need training on OTel concepts (spans, traces, context propagation).
- **Migration Effort**: Retrofitting existing services will require dedicated sprint time over the coming quarters.

## Consequences
- **Performance Impact**: High-frequency spans might impact service throughput. We will conduct load testing to ensure instrumentation overhead remains under 5% of CPU usage.
- **Cultural Shift**: Engineers must transition from purely log-based debugging to a trace-first mindset.

## Rollout Plan

To ensure a smooth transition, we will adopt a phased rollout strategy:

### Phase 1: Foundation (Current Quarter)
- Deploy the OTel Collector in a high-availability configuration.
- Integrate Jaeger and Prometheus backends.
- Instrument the **Ingestion Service** and **Query API** as pilot projects.

### Phase 2: Expansion (Next Quarter)
- Expand instrumentation to the **Transformation Engine** and **Scheduler**.
- Establish baseline performance dashboards and SLOs (Service Level Objectives) using the new metrics.
- Roll out "Trace Context Propagation" across all internal gRPC and HTTP interfaces.

### Phase 3: Optimization & Logging (Q4)
- Implement tail-based sampling to reduce noise and focus on high-value traces.
- Begin integrating structured logs with the trace context.
- Finalize training workshops and documentation for the broader engineering team.
- Evaluate the need for additional exporters (e.g., Zipkin) or OTel collectors for specific workloads.

### Rollout Timeline:
- **Sep 2026**: Deployment of OTel Collectors and Jaeger/Prometheus integration.
- **Oct 2026**: Pilot instrumentation of Ingestion Service.
- **Dec 2026**: 50% service coverage achieved.
- **Mar 2027**: Full stack visibility and tail-based sampling operational.

### Risks:
- **Data Volume**: Uncontrolled instrumentation could lead to excessive data generation, impacting storage and network costs. We will implement sampling strategies (tail-based sampling) to mitigate this.
- **High Cardinality**: Certain user-defined labels could explode the metrics series. We will enforce strict naming conventions to prevent this.

## Future Considerations
- **Profiling**: Evaluate OTel Profiling for CPU and memory analysis in high-performance modules.
- **Incident Management**: Integrate OTel alerts with PagerDuty for automated incident lifecycle management.
- **External Integrations**: Support OpenTelemetry Protocol (OTLP) for seamless data sharing with third-party partners.
## Success Metrics
- Reduction in MTTR (Mean Time To Resolution) for production incidents by at least 20%.
- Achieving 80% service coverage for tracing by the end of Q4.
- Sustained high visibility of service dependencies in the Jaeger dashboard.
- Performance overhead of instrumentation remains consistently under 5% of total service CPU.
## References
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
