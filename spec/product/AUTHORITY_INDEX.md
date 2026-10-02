# Tracera Product Authority Index

**Status:** canonical entrypoint for product/specification authority  
**Date:** 2026-10-01

When documents conflict, use this precedence for the mature-product recovery program.

## A0 — direct accepted owner intent

Current explicit owner decisions in the recovery program. Raw intent is preserved in recovery/source records and may supersede older repository prose.

## A1 — canonical mature contract

1. `spec/product/mature-contract.v1.json`
2. `spec/product/MATURE_DOMAIN_COVERAGE_MAP.md`
3. `spec/product/requirements/*.json`
4. `spec/product/journeys.semantic.v1.json`
5. `verification/SPECIFICATION_ACCEPTANCE_CONTRACT.md`
6. `verification/*verification-cases*.json`

These define current normative product semantics.

## A2 — accepted architecture/semantic decisions

- product persistence/baseline/reuse/invalidation contracts;
- HTTP composition gate;
- accepted recovery dispositions;
- MACE doctrine;
- Tracera↔AgilePlus authority boundary.

## A3 — recovery/forensic evidence

Historical journey/feature inventories, Jan30–Feb06 forensics, session dossiers and scorecards are evidence. They may reveal obligations/regressions but do not override A1 by themselves.

## A4 — implementation and tests

Source/tests show current behavior and evidence. Implementation divergence from A1 is implementation debt unless an accepted contract revision changes A1.

## A5 — historical/proposed/legacy documentation

README, old WP docs, historical Python/API inventories, absorbed archives, old specs and stale architecture documents are provenance unless explicitly promoted.

### Important rule

A file saying `Status: Active`, `Shipped`, `Complete` or `100%` does not outrank this authority index merely because the text exists.

## Fresh-context recovery sequence

Read:
1. this file;
2. mature-contract manifest;
3. recovered product intent;
4. mature domain map;
5. semantic journeys;
6. non-code finality ledger;
7. implementation map/current-state evidence as needed.

Do not begin from old README/product marketing when making product-authority decisions.
