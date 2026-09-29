# Tracera first vertical slice — implementation map

**Status:** implementation design, not implementation completion.  
**Based on current branch:** `a92c11b6c66285d47f58cdae447a1a8480ff3656`.

## Current seam inventory

### Server

`crates/tracera-server/src/router.rs` has mounted SWEE endpoints but many legacy/product-facing item/link/graph routes intentionally return 501.

Do not resurrect the entire legacy API to prove the new product model.

Add a small explicit product namespace, e.g.:

```
GET  /api/v1/products/{product_id}/baselines/{baseline_id}
GET  /api/v1/products/{product_id}/graph
GET  /api/v1/products/{product_id}/assessment
POST /api/v1/products/{product_id}/observations
POST /api/v1/products/{product_id}/changes
```

Exact paths remain subject to API review; the key is semantic isolation from legacy `items/links`.

### Store

Extend the existing Store boundary or introduce a narrow `ProductRepository` port implemented by both SQLite/Postgres. Do not make handlers issue backend-specific SQL.

Required operations for slice:
- put/get product identity;
- put/get accepted baseline;
- put/list product entities/assertions for exact product+baseline/config;
- append/list observations for exact subject;
- put/get product change proposal;
- transactionally accept a baseline/change where applicable.

### Assessment

Repair before mounting:
- typed product/capability/subject identity;
- exhaustive `ObservationResult` handling;
- fixed/injected evaluation time;
- exact scoped observation set;
- result baseline/configuration derived from requested subject, not arbitrary max/global observation;
- counts/findings only from qualifying evidence.

### Machine interface

Prefer HTTP as the first mounted contract because the frontend already has an OpenAPI client and server router. MCP should call the same application service/repository semantics rather than own a second assessment implementation.

MCP parity can follow in the same slice once HTTP behavior is stable.

### Human projection

Do not wire the new product model into the legacy `/api/v1/items` routes merely to make an existing screen light up.

Create a product-model adapter/view model that can feed:
- bounded graph view;
- recovered `PageDecompositionView` for experience projection when entity kinds support it;
- assessment/finding panel.

Canonical IDs/statuses come from the product API. UI-local layout/selection is presentation state only.

### SWEE bridge

Reuse current SWEE Store/NodeKind/EdgeKind for engineering evidence. Product assertions may reference SWEE node IDs through explicit bridge assertions. Do not duplicate source/test/build/deployment nodes into the product table unless identity semantics require a product-level entity.

## Work packets

### VS-01 — identity and repository contract
Define typed IDs and repository interfaces compatible with ontology v0 while preserving current serialized compatibility where practical.

### VS-02 — SQLite persistence
Implement exact product/baseline/entity/assertion/observation persistence and restart witness.

### VS-03 — PostgreSQL parity
Run the same repository contract cases. Do not call parity from schema similarity alone.

### VS-04 — assessment correction
Implement the two-product/two-capability adversarial fixture and exhaustive result truth table.

### VS-05 — HTTP product surface
Mount the minimal read/observe/assess/change-proposal API with explicit invalid-input errors and bounded query.

### VS-06 — SWEE bridge
Link one product obligation/capability to a real SWEE implementation/test/evidence node and support forward/reverse navigation.

### VS-07 — UI product projection
Mount one canonical product page/graph projection. Reuse existing graph/page-decomposition components where they fit after data-contract adaptation.

### VS-08 — external work boundary
Attach a durable external/AgilePlus work reference. Work completion alone must leave product assessment unchanged.

### VS-09 — re-verification
Record new exact evidence for a changed candidate/configuration and reconcile assessment while retaining historical proof.

### VS-10 — MCP parity
Expose the same canonical query/assessment/change-proposal semantics through MCP without a second source of truth.

## Required evidence before calling the slice closed

- SQLite and Postgres repository contract results;
- restart/recovery result;
- two-product isolation;
- two-capability isolation;
- all observation result variants;
- fixed-time reproducibility;
- invalid query rejection;
- bounded traversal;
- HTTP canonical IDs/status;
- UI canonical IDs/status;
- SWEE bridge forward/reverse;
- work-complete-without-proof remains non-green;
- re-verification changes state;
- old baseline/evidence remains queryable;
- MCP parity;
- raw candidate/build/config/verifier identities.

## Rewrite constraint

The slice should grow by:
- enriching identity/configuration;
- adding projections;
- adding adapters;
- adding criteria/evidence;

not by replacing the canonical persistence/assessment boundary at MVP.

Any known temporary adapter must declare replacement and migration cost before the slice can be described as transition-healthy.
