# MACE/adversarial oracles and bidirectional traceability

**Status:** design of verifiers, not executed evidence. Independent falsification is required before claiming completion.

## Contract obligations versus quality overlays

| Intent / requirement | Design rule / spec | Source candidate | Independent positive oracle | Negative/adversarial oracle |
| --- | --- | --- | --- | --- |
| Direct user spatial traversal | Spec 015 ST-001/ST-006 | Product queries + future compiler | From capability to nested subsystem and back with canonical ref | Wrong scope / missing component flagged; no fabricated geometry truth |
| Product authority preserved | ST-002/ST-003 | Identity/baseline + typed graph | 3D ⇄ 2D ⇄ list selection resolves same entity + typed edge | Forged/duplicated mesh ID cannot become a product |
| Literal vs metaphor | ST-004/ST-014 | Future CAD adapter | Real measured import retains units/source | Semantic mesh cannot claim physical length |
| Durable layout/time | ST-005/ST-009 | Baseline/revision concepts | Replay pinned scope returns stable home coordinates | Changed baseline/config not silently merged |
| Detect real dissatisfaction | ST-007/ST-008 | Assessment/detectors | Verified failing obligation linked to observed source | Stale/missing telemetry yields unknown, not healthy |
| Safe scale | ST-010 | Graph queries + 2D spatial index | Bounded visible set with explicit member expansion | Hidden edges/permission denials cannot appear as full graph |
| Universal navigation | ST-011 | Frontend, design tokens | Keyboard and assistive tech complete same task | Pointer-only controls fail |
| Reviewable change | ST-012 | Governance/AgilePlus integration | Proposal can be inspected and authorized separately | Dragging never deploys or modifies canonical state |
| Permission truth | ST-013 | Authorized query/cache | Principal sees allowed projection only | Aggregate counts/layout cannot reveal restricted graph |

## Example independent fixture set

- F1 synthetic product with a capability linked to one source and one test (positive).
- F2 product with two conflicting baselines and stale observation (temporal contradiction).
- F3 permission-filtered graph with hidden high-degree hub and known aggregation (no leakage).
- F4 imported unit-bearing CAD part and nearby purely metaphorical software component.
- F5 dense/cyclic graph with edge bundling, incomplete crawl and force-directed layout stress.
- F6 no telemetry/unknown deployment, disconnected evidence, orphan requirement.
- F7 malicious/untrusted geometry metadata, source URL and labels; scanner/renderer isolation.

## Evidence identity protocol

Each attempted acceptance must record `claim_id`, `requirement_id`, `model_revision`, `source_sha`, `build_artifact`, `environment`, `test_runner_version`, `fixture_id`, `timestamp`, `result`, `source/trace links`, `independent_reviewer`, and whether evidence is current/stale/skipped/blocked. Mark no test as passed merely because an example exists. Attach exact native proof plus consumer-visible UI/API evidence.

## Task-based comparator gate

Pre-register representative tasks: find an interface, trace a failure, identify a missing test, understand cross-domain control, compare revisions and query dense dependencies. Randomize 3D/2D order; record correctness, time, navigation steps, recovery from mistakes, confidence calibration, accessibility and resource costs. Reject unsupported 3D superiority claims. Cross-links to registry [interop checks](https://github.com/KooshaPari/PhenoRegistry/blob/main/docs/specs/spatial-product-twin-ecosystem-contract.md) are required before fleet integration.
