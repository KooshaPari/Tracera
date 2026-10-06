# Tracera Runtime Execution Queue

**Status:** ordered handoff; source changes not performed in the non-code phase.

## P0 — make native Rust evidence executable

1. Run exact repository formatter on branch Rust changes; commit formatting-only diff.
2. Reconcile `db_integration.rs` with the actual supported `SqliteStore` API:
   - replace nonexistent `pool()` fixture access with a supported test seam;
   - replace nonexistent `connect()` construction with supported persistent/file-backed construction;
   - do not weaken persistence/restart assertions.
3. Re-run targeted product-persistence tests.
4. Re-run full Rust test/lint jobs.
5. Bind resulting logs to the requirement/case IDs in the runtime evidence plan.

## P1 — persistence/invalidation witnesses

Execute:
- product-scoped duplicate local IDs;
- immutable baseline history;
- explicit baseline membership;
- append-only observations;
- file-backed restart;
- certificate revocation preserving observations;
- bounded invalidation + continuation;
- persistence-backed invalidation event count.

## P2 — current browser spine

Execute HJ-PRE-001..008 strictly, then d529 PRESERVE/ADAPT outcomes.

No selector swallowing or page-shell-only pass.

## P3 — historical anchor reproduction

Attempt isolated unmodified anchors:
`0e8b0bdd`, `27262fa4`, `4a897659`, `d5296270`, then stability-loss samples.

## P4 — interface composition/parity

After object-safe ProductApplicationService composition:
HTTP/MCP/CLI parity and bounded invalidation response.

## P5 — scale evidence

Only after semantic correctness witnesses are green. Compare optimized projections against canonical reference truth.

## Separate debt

Python/agent CI divergence and broad repository hygiene are tracked separately unless they block a required product witness.
