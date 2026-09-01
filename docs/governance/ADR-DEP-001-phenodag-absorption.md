# ADR-DEP-001: Phenodag Queue Absorption

| Field        | Value             |
| ------------ | ----------------- |
| **Status**   | Accepted          |
| **Date**     | 2026-08-30        |
| **Deciders** | Tracera Core Team |

## Context

Phenodag currently operates a dedicated event ingestion queue that is physically and logically separated from the main Tracera ingestion pipeline. This isolation was originally designed to provide a safe "sandbox" for early-stage graph data experimentation, allowing for rapid prototyping without risking the stability of the core Tracera pipeline.

However, as Phenodag has matured and its data volume has increased significantly, this separate queue has become a major operational and architectural burden.

### Key Drivers for Change

1. **Operational Overhead**: Maintaining two distinct queueing systems (separate brokers, distinct monitoring, and independent scaling) significantly increases DevOps complexity, maintenance costs, and cognitive load for the engineering team.
2. **Throughput Inefficiency**: Phenodag events are currently batched and forwarded to Tracera via a custom bridge component. This introduces artificial latency (often 10-15 minutes) and frequent data lags during peak loads.
3. **Divergent Standards**: The two queues have drifted in terms of schema enforcement, retry policies, and observability metrics. This lack of consistency makes holistic debugging and performance tuning extremely difficult.
4. **Security Risks**: Dual-queue configurations create a wider attack surface for event interception and manipulation between the ingestion points, complicating our overall security posture.

Given the maturity of the Tracera ingestion pipeline and the increasing demands of Phenodag workloads, the cost of maintaining separate queues now clearly outweighs the benefits of isolation.

## Decision

We will **absorb the Phenodag queue directly into the Tracera ingestion pipeline**. This involves decommissioning the standalone Phenodag broker and routing all its events through the primary Tracera stream.

### Implementation Steps

1. **Schema Unification**: Extend the Tracera event schema to include Phenodag-specific attributes as optional metadata fields, ensuring full backward compatibility for existing consumers.
2. **Producer Migration**: Update Phenodag producers to publish directly to the unified Tracera ingestion topic using the new unified schema.
3. **Consumer Alignment**: Decommission Phenodag-specific consumers and re-route their logic into Tracera’s existing high-performance processing workers.
4. **Infrastructure Teardown**: Remove the standalone Phenodag queue brokers and their associated monitoring dashboards once the unified system has been verified stable for 14 days.
5. **Rate Limiting**: Implement a per-tenant rate limiter at the ingestion layer to prevent high-volume Phenodag traffic from starving other critical Tracera services.
6. **Monitoring Integration**: Consolidate the Phenodag health checks into the primary Tracera Grafana dashboards and alerting rules.

## Consequences

### Positive

- **Simplified Architecture**: Reduces the total number of managed services and network hops across the stack, making the system easier to reason about and maintain.
- **Improved Latency**: Events reach the core ingestion layer immediately, eliminating the multi-step bridge-induced delay and improving real-time data availability.
- **Unified Observability**: Gains a single pane of glass for monitoring all ingestion health metrics, data quality, and throughput.
- **Enhanced Security**: Reduces the number of integration points, simplifying the overall security posture and access control.

### Negative

- **Migration Risk**: The transition period requires careful orchestration to avoid duplicate events or data loss during the switchover.
- **Resource Contention**: High-volume Phenodag bursts may temporarily impact the performance of other Tracera ingestion workloads, though this is mitigated by the new rate limiter.
- **Backward Incompatibility**: Downstream systems relying on Phenodag’s specific queue offsets, consumer groups, or direct broker connections will require updates.

## Alternatives Considered

- **Keeping Separate Queues**: Rejected due to the increasing operational costs, latency issues, and growing maintenance debt.
- **Polling/Bridge Upgrade**: Replacing the current bridge with a high-speed "pull" model was considered, but it does not solve the underlying problem of architectural fragmentation or the risk of message drift.
- **Event Sourcing / Replay**: While a replay mechanism was considered for historical data migration, it was deemed out of scope for this specific architectural consolidation.

## Rollback Plan

If the absorption causes critical instability, we will revert the producer changes to the legacy bridge endpoint and re-enable the Phenodag broker instances. This rollback will be executed within 30 minutes of a critical alert and involves the following steps:

1. Re-deploy legacy Phenodag producers.
2. Restore the bridge component's configuration.
3. Verify data flow to the separate Phenodag broker.
