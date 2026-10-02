# Tracera semantic review findings

Snapshot: `17eef2379d4a673e1c8cc71ed7663fae9e94309b`

These are specification/implementation reconciliation findings. They are not automatically defects until the cited requirement is accepted and the implementation is verified against a concrete case.

## F-001 — assessment capability scoping is inconsistent

`AssessmentEngine::assess_product` builds a product-filtered map, but calls `assess_capability(cap_id, observations)` with the entire input observation slice. It also derives baseline and observation_count from the entire slice.

**Risks:** cross-product evidence can influence status, baseline and counts.

**Mapped obligations:** TRC-R-OBS-SCOPE, TRC-R-ASSESS-DETERMINISTIC.

**Required verification:** construct product A and B observations with contradictory results and prove B cannot affect A.

## F-002 — capability identity is conflated with product identity in assessment

`assess_product` groups by `obs.product_id`; `assess_with_intents` filters observations where `o.product_id == intent.id` even though `Observation` already has `capability_id`.

**Risk:** product and capability namespaces are semantically confused.

**Mapped obligations:** TRC-R-OBS-SCOPE, TRC-R-PRODUCT-GRAPH.

## F-003 — Unknown/Stale observation results can fall through to Satisfied

`assess_capability` explicitly checks Failed, Passed and Inconclusive. A fresh `Unknown` observation, or a mix whose explicit result is `Stale` but whose timestamp is fresh, can reach the final "all relevant observations passed" branch.

**Risk:** false green.

**Mapped obligations:** TRC-R-ASSESS-STATUS, TRC-R-ASSESS-MISSING, TRC-R-COLLECTOR-FAIL.

## F-004 — determinism claim is qualified by wall-clock reads

Assessment calls `Utc::now()` internally for freshness and `assessed_at`. Identical serialized inputs evaluated at different times can cross a freshness boundary.

**Required interpretation:** deterministic for a fixed effective evaluation time, not merely fixed serialized observations.

**Mapped obligation:** TRC-R-ASSESS-DETERMINISTIC.

## F-005 — current Rust SWEE taxonomy conflicts materially with Spec 011

Spec 011 defines a different 30-node/35-edge model (AgentNode, OrganizationNode, TestRunNode, etc.) and bitemporal/performance/Cypher obligations. Current Rust `NodeKind` instead includes Requirement, SourceFile, Module, Class, Function, Evidence, Problem, ChangeRequest, etc.; `EdgeKind` likewise differs.

**Risk:** treating Spec 011 as fully accepted/current would create contradictory requirements.

**Action:** reconcile each Spec 011 semantic obligation as accepted, superseded, proposed, or still desired; do not copy the tables wholesale.

## F-006 — stale reconciliation statements cannot be current implementation evidence

WP-00 says product identity and automatic dissatisfaction have no code. Current `product/{identity,baseline,observation,assessment,detectors,queries}.rs` now exists.

**Action:** preserve WP-00 as historical accepted-horizon provenance; refresh implementation mapping from current snapshot.

## F-007 — proposal semantics differ by surface

Baseline proposals model explicit Draft→Submitted→Accepted/Rejected deltas. MCP `propose` currently creates a synthetic SWEE Requirement node with subtype `proposal`.

**Risk:** callers may assume MCP proposal participates in the accepted baseline proposal workflow when it does not.

**Mapped obligation:** TRC-R-PROPOSE-NOMUT; additional interface-parity requirement likely needed after MCP review.

## F-008 — product assessment is not yet the stage/product-shape grader

Current assessment evaluates capability observations. The user-required mature completeness, VP projection, journey closure, structural shape, survivability and transition burden model is a distinct higher-level grading layer.

**Action:** do not label current AssessmentEngine as satisfying the product progress oracle.
