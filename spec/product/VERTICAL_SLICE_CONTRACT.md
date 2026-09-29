# Tracera vertical product-truth slice contract

**Status:** proposed acceptance contract; implementation/test generation deferred.  
**Derived from:** recovered Featuregraph intent + research Passes 01–07 + current source reachability.

## Why this slice

The repository already has:
- stable product/baseline/observation domain types;
- product assessment/detectors/query/traversal primitives;
- SQLite/Postgres product tables;
- SWEE/trace-link persistence;
- machine interfaces for the existing SWEE graph;
- human graph/item surfaces including a detached page-decomposition projection.

The missing proof is not another primitive. It is one durable end-to-end path through canonical product truth.

## Scenario fixture

Two products:
- `product-A`
- `product-B`

Each has:
- its own accepted baseline/configuration;
- a capability named `search` (deliberate local-name collision);
- one obligation/criterion;
- persisted product graph relation to an implementation artifact;
- observations from an admitted verifier.

A separate durable external work reference is linked to product A but is not acceptance evidence.

## V1 journey

### 1. Establish accepted product truth

Create product A and B with stable identities and accepted baselines.

**Pass:** restart and recover exact identities/baselines.  
**Fail:** aliases/local labels merge the products or accepted baseline mutates in place.

### 2. Persist a product projection

Persist product→capability→obligation/target relations and at least one explicit cross-layer link to SWEE/implementation evidence.

**Pass:** bounded forward and reverse queries preserve canonical IDs.  
**Fail:** only UI-local state or an in-memory adjacency survives.

### 3. Record exact scoped evidence

Record:
- A/search = pass at A's target baseline/configuration;
- B/search = fail at B's different baseline/configuration;
- optional stale/unknown/inconclusive observations.

**Pass:** observations retain product, capability/subject, baseline/configuration, verifier, result and provenance.  
**Fail:** capability is inferred from product ID or evidence is admitted without enough identity to distinguish A from B.

### 4. Assess product A

Use a frozen evaluation time.

**Pass:** B cannot affect A's status, baseline, observation count, finding IDs or explanation. Explicit Unknown/Stale/Inconclusive cannot become Satisfied.  
**Fail:** global observation slice leaks into A or unsupported enum variants fall through green.

### 5. Expose through a mounted machine interface

One canonical API or MCP surface returns the product projection, assessment and evidence references.

**Pass:** invalid discriminators are explicit errors; bounded query semantics are visible; exact snapshot/configuration selection is distinguishable from historical range queries.  
**Fail:** helper semantics silently change because the transport prefilters differently.

### 6. Expose through a mounted human projection

Mount one useful product projection—preferably reusing the recovered page-decomposition/graph work where appropriate.

**Pass:** the UI displays the same product/baseline/status IDs as the machine interface and can navigate to linked implementation/evidence.  
**Fail:** mock-only/local item state creates a second product truth or UI green disagrees with machine assessment.

### 7. Propose a product delta

Propose one graph/product change without mutating the accepted baseline.

**Pass:** delta, impact and external work reference are recorded separately from accepted state.  
**Fail:** proposal or work creation changes product acceptance.

### 8. Complete external work

Mark the linked work complete.

**Pass:** Tracera remains non-green if new required product evidence is absent.  
**Fail:** Done/merged/closed work directly satisfies the product obligation.

### 9. Re-verify and reconcile

Ingest qualifying new evidence bound to the new candidate/configuration and reassess.

**Pass:** product state changes only from admissible proof; old evidence/history remains queryable against its original baseline/configuration.  
**Fail:** old proof is overwritten or reused outside its applicability without an explicit compatibility rule.

## Required failure controls

- wrong product;
- wrong capability;
- wrong baseline;
- wrong configuration;
- wrong candidate;
- wrong expectation;
- unadmitted verifier;
- stale evidence;
- explicit Unknown;
- explicit Inconclusive;
- conflicting pass/fail;
- collector/verifier error;
- empty denominator;
- invalid query discriminator;
- unbounded traversal request;
- work complete without proof;
- proposal without acceptance;
- restart between evidence collection and assessment;
- worker A replaced by worker B.

## Evidence package

A valid run must retain:
- exact source revision/build artifact;
- database schema revision;
- configuration;
- accepted baseline;
- request/response or MCP transcript;
- UI-visible canonical IDs/status;
- verifier identity/version;
- observation IDs;
- assessment result;
- restart/recovery witness;
- external work reference;
- before/after product delta;
- raw failure-control results.

## Architectural success condition

The slice is successful only if its interfaces and stored identities can be extended to additional projections/stages **without replacing the canonical spine**. Temporary adapters are allowed only with explicit bounded transition debt.

This slice proves a narrow usable Tracera shape. It does not prove mature-product completeness.
