## 1. Language Tiering Strategy for Migration

## Status
Accepted

## Context
The migration needs a constrained execution model that keeps critical path performance and reliability high while preserving developer velocity. Phase-0 inventory shows substantial endpoint consolidation across routers, so migration decisions must be made per component based on observed value and risk, not by filename.

## Decision
- Use **Rust**, **Zig**, and **Mojo** as **Tier-1 cores** for latency-sensitive, resource-intensive components with the highest migration complexity/value density.
- Use **Python 3.14** and **Bun/TypeScript 7** as **Tier-2 edges** for orchestration, glue, compatibility, and fast iteration.
- Apply **per-component tiering by merit** (runtime criticality, data throughput, correctness risk, ownership, and replacement cost), revisiting each component as migration evidence evolves.

## Consequences
- Enables selective modernization rather than a risky monolithic rewrite.
- Preserves stability by keeping low-risk edges in mature ecosystems while hardening throughput/control plane work in Tier-1.
- Allows capability-level parity checks to dominate migration quality gates, so language choices remain an implementation detail behind endpoint behavior.
