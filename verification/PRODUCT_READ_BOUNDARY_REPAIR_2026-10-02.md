# Product read boundary repair — 2026-10-02

## Scope and predecessor

Repository: KooshaPari/Tracera. Recovery PR #1086 remains draft.
Inspected predecessor: `caece123a1f79ff5a4201c8e5e0b1b92969a053d`.
This is a bounded correction of the product read/application composition, not
acceptance of the mature product or a new mutation API.

## Defects found in the predecessor

1. `pub mod application` preceded the product module's inner doc comments.
2. Application read limits were `usize`, while ProductPersistence takes `u32`.
3. The facade called `list_reuse_decisions_for_target`, which did not exist in the
   persistence trait or either adapter.
4. A successful empty membership query was incorrectly used as a baseline
   ownership check. It does not distinguish a legitimate empty baseline from a
   foreign or absent baseline. The following unscoped reuse read could leak data.
5. Bearer middleware exempted any path ending in health/healthz. A product named
   `health` could therefore bypass authentication on its otherwise protected route.
6. Bounded list responses did not expose whether the requested limit was reached.
7. Backend error strings were returned to clients, potentially including internals.
8. The certificate-revocation integration witness used an unimported function.

## Repair

The focused port and object-safe facade now use the same `u32` contract. Reuse
reads carry product identity all the way through both SQL adapters. An explicit
`get_baseline(product_id, baseline_id)` lookup distinguishes scoped existence from
empty membership. SQL additionally checks the target baseline, observation, and
source baseline ownership, and binds candidate identity as a parameter.

Public probe exemptions are exact registered routes, not suffix matching. Errors
retain their HTTP class; backend details stay in server logs. Lists retain their
existing fields and add conservative completeness metadata. At the limit,
`complete=false`, `completeness=unknown_at_limit`, `pagination_supported=false`,
and `continuation=null`: this patch does not invent an implemented cursor API.

The application remains separate from legacy Store. SQLite and Postgres share
semantic contracts but do not depend on each other's concrete types.

## Executed evidence — SQL layer only

Command:

```sh
python3 -m unittest discover -s verification/tests -p test_reuse_projection_sql.py -v
```

Observed: **10 tests passed, 0 failed**, Python 3.13.5, SQLite 3.46.1.
The test reads the production SELECT files and real SQLite migrations 010 and
011. It reproduces the predecessor's empty-membership/unscoped-read failure and
checks the corrected query, exact product/baseline/candidate scope, deterministic
ordering/bounds, parameter binding, corrupt legacy source-scope rows, and unchanged
observation history.

Inputs verified by Git blob identity:

| Input | Git blob SHA-1 |
|---|---|
| SQLite migration 010 | `0eb4affc27da0f19b2817e25e6af15884be413ef` |
| SQLite migration 011 | `9237acb9668ba75d6bdd375b79c99e5e5ee538ed` |
| SQLite production SELECT | `a62f525aaf11bbd13f1a9f77b5b8bb9a1c93d82d` |
| Postgres production SELECT | `1ec5a6c294b24580b831ee921f78047ff5456093` |
| Python witness | `9dbd7d261a4bfd558c676f3ac7e6b25b9cac2e0d` |

The Postgres-related SQL test compares normalized query text/parameter order. It
is **not Postgres execution**. These tests also do not execute Rust, SQLx, the full
migration chain, bearer middleware, or HTTP handlers.

## Authored but not executed here

Eleven tests in `src/handlers/product/tests.rs` exercise the actual router,
application facade, SQLite adapter and real migrations: bearer enforcement,
product ID `health`, foreign/missing baselines versus legitimate empty baselines,
limit metadata, reuse candidate scope, encoded invalidation references, invalid
query inputs, and safe error mapping. The 18 existing db_integration test functions
and their substantive assertions remain; the missing revocation import is repaired.

Native Rust formatting/build/tests, mounted HTTP tests, Postgres integration,
mutations, browser journeys, and product-level acceptance remain **UNVERIFIED**.
The local execution environment has no Rust toolchain. This receipt must not be
used as a native Rust/HTTP/Pg green.

## Trace and limitations

This addresses WBS T5.1/T5.6–T5.14/T5.18 and the product-scope/read-completeness
obligations. It does not close the full T5 gate. Invalidation-history reads remain
behind the existing single configured bearer capability; this is not a new
multi-tenant authorization model. Reuse decisions are historical records, not a
claim that their current applicability survives later invalidation.

Next gate: compile this coherent candidate and run the mounted HTTP and database
integration witnesses before extending the mutating product surface.
