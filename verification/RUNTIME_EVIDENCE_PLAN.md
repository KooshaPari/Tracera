# Tracera Runtime Evidence Plan

**Status:** execution-ready plan; no execution result is implied  
**Date:** 2026-10-01

This document is the handoff from mature semantic specification to implementation/runtime verification. It intentionally contains no production-code changes.

## Evidence identity

Every executed witness must record:
- requirement/case IDs;
- exact Git candidate SHA/tree;
- product/baseline/configuration fixture;
- verifier/tool identity and version;
- environment/runtime identity;
- start/end time;
- raw artifact/log/screenshot/result reference;
- explicit status: Satisfied / Unsatisfied / Inconclusive / Unknown / NotConfigured / Stale;
- known limitations.

A green command exit without these bindings is supporting evidence, not product proof.

## Track R1 — historical anchors

Run isolated worktrees for:
1. `0e8b0bdd` — strongest pre-performance candidate;
2. `27262fa4` — progressive-loading transition;
3. `4a897659` — documented edge-mapping repair;
4. `d5296270` — scope-collapse mega-transaction;
5. selected stability-loss anchors around Feb 1–6.

For each:
- recover documented toolchain/dependencies without modifying the commit;
- record build/start success/failure separately;
- record reachable routes/journeys;
- never patch the historical commit and call the patched state historical evidence.

## Track R2 — recovered browser spine

Strictly execute:
- HJ-PRE-001 project open;
- HJ-PRE-002 selected-project inventory;
- HJ-PRE-003 unified graph;
- HJ-PRE-004 graph modes/perspectives;
- HJ-PRE-005 matrix;
- HJ-PRE-006 item detail;
- HJ-PRE-007 relationship inspection/management outcome;
- HJ-PRE-008 typed projections.

Required assertions:
- selected product identity remains stable;
- partial/progressive data is explicit;
- no required selector/action is swallowed;
- route shell load alone is not success;
- canonical IDs/count explanations survive projection changes.

## Track R3 — d529 breadth

Execute dispositioned PRESERVE/ADAPT surfaces:
- page decomposition;
- specialized journey semantics;
- problem/dissatisfaction;
- process structure;
- multi-dimensional graph behavior.

An unreachable historical component may be satisfied by a superseding current surface only if the accepted outcome is demonstrated and the disposition trace names it.

## Track R4 — product persistence

Execute SQLite and Postgres parity witnesses for:
- product-scoped duplicate local IDs;
- immutable baselines;
- explicit baseline membership;
- append-only observations;
- restart persistence;
- evidence reuse decision history;
- certificate revocation preserving observations;
- invalidation event persistence;
- migration/backup/recovery where supported.

## Track R5 — assessment/invalidation

Execute all spine and mature breadth verification catalogues, prioritizing:
- empty denominator;
- wrong product/baseline/configuration;
- stale/conflicting evidence;
- collector failure;
- dependency uncertainty;
- bounded propagation continuation;
- certificate revocation;
- historical-valid/current-invalid distinction;
- work Done without product proof.

## Track R6 — interfaces

After object-safe application composition exists:
- HTTP/MCP/CLI supported-surface parity;
- auth/mutation authority;
- error classes;
- pagination/continuation;
- capability discovery;
- bounded invalidation response exposes affected + continuation + complete + persisted event count.

## Track R7 — scale

Benchmark exact profiles rather than vague “10K nodes”:
- node/edge counts and distributions;
- graph projection/mode;
- initial vs complete data;
- browser/runtime/hardware;
- TTFR/interaction/frame/resource metrics;
- correctness comparison against canonical unoptimized query truth.

Performance pass is invalid if canonical data silently disappears.

## Promotion rule

PR #1086 remains draft until the agreed runtime gate subset has exact evidence. Runtime failures revise implementation or, only through explicit accepted product change, the contract. They do not silently weaken the oracle.
