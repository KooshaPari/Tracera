# Completion estimates and uncertainty

Requested engineering estimates, not promised dates. Unit: one person-day = approximately six focused engineering hours including implementation, relevant validation and review preparation. Estimates are analyst judgment from the specific source gaps and integration work, not measured team throughput. No calendar forecast or completion percentage is defensible yet.

Assumptions: one accountable integration owner; existing code/PRs reused; reliable desk compute and credentials through approved paths; limited supported CVP profiles; no product rewrite; independent review and acceptance time included as effort, external waiting excluded. Parallel agents reduce some elapsed time, not the sum of effort, and shared schema/UI/acceptance work serializes. Confidence is low-to-medium until C1 establishes actual deployed parity.

| Package                           | Low-high person-days | Rationale / confidence                                                 |
| --------------------------------- | -------------------: | ---------------------------------------------------------------------- |
| C1 identity/convergence           |                  3-6 | Several overlapping branches and dirty checkout; medium                |
| C2 persistence/mutations          |                 8-15 | In-memory observations and competing canonical graph path; low         |
| C3 assessment isolation           |                  4-8 | Precise known cases, unresolved product/baseline API semantics; medium |
| C4 traversal/search/matrix        |                 6-12 | SWEE cannot simply substitute for canonical graph; low-medium          |
| C5 consumer UI journey            |                 5-10 | Existing app reusable; many view semantics unqualified; low-medium     |
| C6 handoff/verification           |                  4-8 | Minimal one-agent integration, no full autonomous platform; low        |
| C7 persistent deployment/recovery |                 6-12 | Snapshot/cutover, Access, real artifact and restore proof; low         |
| C8 quality/security/CI            |                 5-10 | Existing failures and dependency convergence; low-medium               |
| C9 independent dogfood pilot      |                 5-10 | Real fixture/oracle, unfamiliar operator and retained failures; medium |
| C10 bounded release/hardening     |                  4-8 | Supported-profile closure and consumer docs; medium                    |
| **CVP / first usable MVP total**  |            **50-99** | Additive effort; no Friday or automated-calendar promise               |

CVP means the accepted real-product loop, not all historical stubs. A read-only demonstrator can be smaller, but it cannot be relabeled as a persistent product authority. Some package low bounds overlap operationally; the total deliberately retains integration allowance instead of claiming linear swarm speedup.

| Additional mature package                  | Low-high person-days | Principal uncertainty                                                  |
| ------------------------------------------ | -------------------: | ---------------------------------------------------------------------- |
| M1 full surface closure                    |                15-35 | Final API/view denominator and owner retirement decisions              |
| M2 incremental ingestion/version semantics |                20-45 | Supported ecosystems, source/index freshness and conflict semantics    |
| M3 scale and semantic navigation           |                15-35 | Dataset density, graph shape, accessibility and response budgets       |
| M4 auth/federation/concurrency/recovery    |                20-40 | Trust boundaries and deployment profiles                               |
| M5 approved model-driven changes           |                20-45 | Exact effect/approval contracts and external engine integration        |
| M6 spatial representations                 |                15-30 | Read-only semantic projection scope; high-fidelity CAD breadth unknown |
| M7 distribution/API parity                 |                15-35 | Supported OS/store/SDK denominator                                     |
| M8 independent comparative/adoption pilot  |                15-30 | Recruitable users, comparator profiles and oracle construction         |
| M9 consolidation/accepted edge cases       |                10-20 | Feedback and retained material obligations                             |
| **Additional bounded maturity**            |          **145-315** | Low confidence; scope gates must narrow uncertainty                    |
| **CVP plus bounded maturity**              |          **195-414** | Person-days, not elapsed days or a universal full-product ceiling      |

Complete CAD formats, every language/platform, arbitrary autonomous editing and unlimited future feature parity are **UNKNOWN**, outside the bounded total until profiled. No speculative market/revenue estimate is assigned.

Re-estimation checkpoints:

1. After C1: classify code already deployed but not merged; revise 50-99 upward/downward with exact receipts.
2. After C2/C3: measure one durable/import/assessment slice; replace persistence and oracle estimates with actual throughput.
3. After C9: require user evidence that the core model reduces reconciliation effort. If it does not, narrow to a useful adapter/explorer or stop expansion.
4. Before M5/M6: scope approval effects and spatial/CAD fidelity explicitly; publish a fresh range rather than treating this estimate as authority.

Scope/reliability risks: source/deployed divergence, stale documentation, hidden tenant coupling, unsupported build profiles, incomplete migration data, review bottlenecks and external service policy. These are work/uncertainty drivers; they are not claims that solved credential provisioning or billing requires operator intervention.
