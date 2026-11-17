# Tracera intent and domain evidence tree

> GENERATED from STATUS.json. Do not edit this projection.

Generated: `2026-10-18T00:22:20Z` | source SHA-256: `9eda443eb929fc49c81a38ed6548304fc5e2f671a22f5b8da1facec95b4eeaff`

Four dimensions remain separate. Counts are unique evidence leaves, not requirements or completion.
Source-only observations qualify only their stated narrow criterion. Full parent closure requires every required child.
A FAIL parent names a specific counterexample; UNKNOWN identifies unclosed children.

## Intent tree

```text
G01 Authority and mature identity
  Criterion: Owning intent records retain both and define identity-preserving bridge acceptance; no retrospective feature acceptance.
  +-- Implementation: UNKNOWN | STATUS.json#G01.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G01.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G01.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G01.acceptance | Full criterion unclosed; source existence is insufficient
G02 Local trace capture
  Criterion: Real session capture, exact count/content after restart; invalid/foreign/dangling edges rejected.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G02.acceptance,G02.event-normalization,G02.event-capture-mounted,G02.session-capture-mounted | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G02.acceptance,G02.event-normalization,G02.event-capture-mounted,G02.session-capture-mounted | Full criterion unclosed; source existence is insufficient
G03 Cross-run dependency reasoning
  Criterion: Seed known dependency plus unrelated session; persisted query yields exact affected set after reopen. Supplied-links computation alone insufficient.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Counterexample G03.graph-impact-traverse; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Counterexample G03.graph-impact-traverse; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G03.acceptance,G03.swee-directed-queries,G03.persisted-artifact-trace,G03.graph-impact-traverse | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G03.acceptance,G03.swee-directed-queries,G03.persisted-artifact-trace,G03.graph-impact-traverse,G03.trace-matrix | Full criterion unclosed; source existence is insufficient
G04 Memory distillation
  Criterion: Persist memory, link source sessions and serve real consumer; restart restores same accepted entry; private/untrusted input cannot escape into public projection.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | Counterexample G04.memory-durable-restart; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | Counterexample G04.memory-durable-restart; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G04.acceptance,G04.memory-durable-restart,G04.memory-next-session-consumer | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G04.acceptance,G04.memory-pattern-distillation,G04.memory-durable-restart,G04.memory-next-session-consumer | Full criterion unclosed; source existence is insufficient
G05 Audit and evidence replay
  Criterion: Real evidence/source/run timestamps survive restart, altered/missing/stale evidence fails honestly; audit export replay verified.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Counterexample G05.complete-atomic-audit-replay; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Counterexample G05.complete-atomic-audit-replay; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G05.acceptance,G05.item-trace-snapshot,G05.complete-atomic-audit-replay | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G05.acceptance,G05.item-trace-snapshot,G05.complete-atomic-audit-replay | Full criterion unclosed; source existence is insufficient
G06 Product semantic model
  Criterion: Real owned product import and independently adjudicated gap; no cross-product/baseline/capability leakage; source change invalidates affected evidence.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Counterexample G06.item-http-mutations; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Counterexample G06.item-http-mutations; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G06.acceptance,G06.item-http-mutations | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G06.acceptance,G06.item-http-mutations | Full criterion unclosed; source existence is insufficient
G07 Import and canonical identity
  Criterion: Two sources same externalID stay distinct; retry idempotent; late error atomic or explicit recoverable partial contract. Q1 product batch does not automatically repair Story importer.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/ingest/persist.rs:39-39 | Counterexample G07.live-ingestion-atomic-identity; no claim other children fail
  +-- Usability: UNKNOWN | STATUS.json#G07.acceptance,G07.typed-spec-reads,G07.live-ingestion-atomic-identity | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G07.acceptance,G07.typed-spec-reads,G07.live-ingestion-atomic-identity | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G07.acceptance,G07.typed-spec-reads,G07.live-ingestion-atomic-identity | Full criterion unclosed; source existence is insufficient
G08 Project catalog and CIVIS
  Criterion: Item-only and empty project load correctly; all pages complete; failure never reported as empty.
  +-- Implementation: UNKNOWN | STATUS.json#G08.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G08.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G08.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G08.acceptance | Full criterion unclosed; source existence is insufficient
G09 Named artifact fidelity
  Criterion: Click every required sidebar/view and representative typed detail using real IDs; 44 historical rows require current requalification.
  +-- Implementation: UNKNOWN | STATUS.json#G09.acceptance,G09.detail-scope | Full criterion unclosed; source existence is insufficient
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | Counterexample G09.view-01; no claim other children fail
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | Counterexample G09.view-01; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G09.acceptance,G09.detail-scope,G09.view-01,G09.view-02,G09.view-03,G09.view-04,G09.view-05,G09.view-06,G09.view-07,G09.view-08,G09.view-09,G09.view-10,G09.view-11,G09.view-12,G09.view-13,G09.view-14,G09.view-15,G09.view-16,G09.view-17,G09.view-18,G09.view-19,G09.view-20,G09.view-21,G09.view-22,G09.view-23,G09.view-24,G09.view-25,G09.view-26,G09.view-27,G09.view-28,G09.view-29,G09.view-30,G09.view-31,G09.view-32,G09.view-33,G09.view-34,G09.view-35,G09.view-36,G09.view-37,G09.view-38,G09.view-39,G09.view-40,G09.view-41,G09.view-42,G09.view-43,G09.view-44,G09.view-45,G09.view-46,G09.view-47,G09.view-48,G09.view-49,G09.view-50,G09.view-51,G09.view-52,G09.view-53,G09.view-54,G09.view-55,G09.view-56,G09.view-57,G09.view-58,G09.view-59 | Full criterion unclosed; source existence is insufficient
G10 Specifications Hub
  Criterion: Summary shape matches summary-hooks; totals reconcile complete typed collections; missing compliance/pass data null; failures distinct from zero.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Counterexample G10.specification-summary; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Counterexample G10.specification-summary; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G10.acceptance,G10.summary-fallback,G10.specification-summary | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G10.acceptance,G10.summary-fallback,G10.specification-summary | Full criterion unclosed; source existence is insufficient
G11 Authoring and links
  Criterion: Actual scoped CRUD and links survive restart; invalid/cross-project updates rejected; UI cannot advertise unavailable methods as implemented.
  +-- Implementation: UNKNOWN | STATUS.json#G11.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G11.acceptance,G11.ui-crud | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G11.acceptance,G11.ui-crud | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G11.acceptance,G11.ui-crud | Full criterion unclosed; source existence is insufficient
G12 Bounded search and exploration
  Criterion: Known source anchor found; bounded query terminates cycles and marks truncation; no fabricated edge or silently missing page.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | Counterexample G12.postgres-title-search; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | Counterexample G12.postgres-title-search; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G12.acceptance,G12.mcp-graph,G12.sqlite-title-search,G12.postgres-title-search | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G12.acceptance,G12.mcp-graph,G12.sqlite-title-search,G12.postgres-title-search | Full criterion unclosed; source existence is insufficient
G13 Native test/result integration
  Criterion: Ingest actual native report, preserve failed cases/denominators and source revision; unsupported execution honest unavailable.
  +-- Implementation: UNKNOWN | STATUS.json#G13.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G13.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G13.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G13.acceptance | Full criterion unclosed; source existence is insufficient
G14 API CLI MCP parity
  Criterion: One real supported operation roundtrips same IDs across required interfaces; unsupported declared; demo modes excluded from acceptance.
  +-- Implementation: FAIL | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:41 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Usability: UNKNOWN | STATUS.json#G14.acceptance,G14.route-contract,G14.cli-crud-parity,G14.mcp-crud-parity | Full criterion unclosed; source existence is insufficient
  +-- Validation: FAIL | evidence/installed-cli-help.log:1 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G14.acceptance,G14.route-contract,G14.cli-crud-parity,G14.mcp-crud-parity | Full criterion unclosed; source existence is insufficient
G15 Authentication privacy isolation
  Criterion: 401 missing credential,403/404foreign scope, no public backend bypass, redacted logs/export, payload limits and hostile prose tests.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Counterexample G15.producer-tenant-ownership; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Counterexample G15.producer-tenant-ownership; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G15.acceptance,G15.rate-limit-mounted | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G15.acceptance,G15.global-bearer,G15.product-allowlist,G15.producer-tenant-ownership,G15.required-auth-on-local-default,G15.csrf-origin-token,G15.rate-limit-mounted | Full criterion unclosed; source existence is insufficient
G16 Durability recovery migration
  Criterion: Real persistent reopen plus crash/backup/restore/migration trial; compare IDs/content beforeafter; old/new data contract explicit.
  +-- Implementation: UNKNOWN | STATUS.json#G16.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G16.acceptance,G16.postgres-observation-concurrency | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G16.acceptance,G16.postgres-observation-concurrency | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G16.acceptance,G16.observation-reopen,G16.postgres-observation-concurrency | Full criterion unclosed; source existence is insufficient
G17 Install and desktop delivery
  Criterion: Fresh install useful journey, local-first no mandatory remote API, update retains data and recoverable previous artifact.
  +-- Implementation: UNKNOWN | STATUS.json#G17.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: FAIL | evidence/backend/desk-reconciliation.json:1-1 | Counterexample G17.desk-installed-compose-cli; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G17.acceptance,G17.desktop-origin | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G17.acceptance,G17.desktop-origin,G17.desk-installed-compose-cli | Full criterion unclosed; source existence is insufficient
G18 Deployment artifact provenance
  Criterion: Current hosted and installed artifact exact identity, authenticated real path; Q0 isolated readiness does not qualify production.
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:scripts/install-local-runtime.sh:78-78 | Counterexample G18.install-desktop-auth-configuration; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Counterexample G18.backup-whole-product; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G18.acceptance,G18.install-desktop-auth-configuration,G18.backup-whole-product | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G18.acceptance,G18.readiness-store,G18.install-desktop-auth-configuration,G18.backup-whole-product | Full criterion unclosed; source existence is insufficient
G19 UX accessibility and DX
  Criterion: Keyboard/focus/labels/contrast assistive audit without captures; no mock data presented as real; documented command starts actual profile.
  +-- Implementation: UNKNOWN | STATUS.json#G19.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G19.acceptance,G19.focus-source,G19.async-states,G19.explicit-unsupported | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G19.acceptance,G19.focus-source,G19.async-states,G19.explicit-unsupported | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G19.acceptance,G19.focus-source,G19.async-states,G19.explicit-unsupported,G19.cli-help | Full criterion unclosed; source existence is insufficient
G20 Assurance and security gates
  Criterion: Run required local gates with explicit coverage denominator/floor; deliberate regression fails; masked Ruff/Python collection fixed if retained.
  +-- Implementation: UNKNOWN | STATUS.json#G20.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G20.acceptance,G20.route-check-instrument | Full criterion unclosed; source existence is insufficient
  +-- Validation: FAIL | evidence/test-ui-a11y-contract.log:1-6 | Counterexample G20.a11y-check-instrument; no claim other children fail
  +-- Assurance: FAIL | evidence/test-ui-a11y-contract.log:1 | Counterexample G20.a11y-check-instrument; no claim other children fail
G21 Research and alternatives
  Criterion: Version-pin manualworkflow, catalog/search, requirements/source links and dependency exploration peers; matched seeded cases plus idiomatic comparisons.
  +-- Implementation: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
G22 Operations and economic ownership
  Criterion: Restore rehearsal, dependency failure, resource bounds and explicit recurring-job owner; no billed services added; actual hosting cost unknown.
  +-- Implementation: UNKNOWN | STATUS.json#G22.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: FAIL | evidence/backend/live-runtime.json:1-1 | Counterexample G22.desk-manual-runtime-health-ready; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G22.acceptance,G22.metrics-endpoint,G22.fleet-enroll,G22.fleet-heartbeat | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G22.acceptance,G22.desk-manual-runtime-health-ready,G22.metrics-endpoint,G22.fleet-enroll,G22.fleet-heartbeat | Full criterion unclosed; source existence is insufficient
G23 Actual beneficiary acceptance
  Criterion: Unfamiliar authorized user real owned input, recorded task outcome/interventions/feedback, failures retained; fixture pass does not qualify.
  +-- Implementation: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
G24 Full historical parity disposition
  Criterion: Each retained promise maps accepted goal/current contract/closure proof, or explicit authority for supersession/defer/retire; no silent sunset.
  +-- Implementation: UNKNOWN | STATUS.json#G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G24.acceptance | Full criterion unclosed; source existence is insufficient
G25 Unified trace-to-product evidence bridge
  Criterion: Real authorized producer and source anchor, semantic causal navigation, exact restart/replay equality and foreign-product negative controls; meaningful actual user outcome.
  +-- Implementation: UNKNOWN | STATUS.json#G25.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G25.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G25.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G25.acceptance,G25.real-benchmark-causal-bridge | Full criterion unclosed; source existence is insufficient
```

## Domain overlays (aliases; excluded from leaf counts)

```text
code -> G02, G03, G04, G06, G11
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G02.acceptance,G02.event-capture-mounted,G02.event-normalization,G02.session-capture-mounted,G03.acceptance,G03.graph-impact-traverse,G03.persisted-artifact-trace,G03.swee-directed-queries,G04.acceptance,G04.memory-durable-restart,G04.memory-next-session-consumer,G06.acceptance,G06.item-http-mutations,G11.acceptance,G11.ui-crud | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G02.acceptance,G02.event-capture-mounted,G02.event-normalization,G02.session-capture-mounted,G03.acceptance,G03.graph-impact-traverse,G03.persisted-artifact-trace,G03.swee-directed-queries,G03.trace-matrix,G04.acceptance,G04.memory-durable-restart,G04.memory-next-session-consumer,G04.memory-pattern-distillation,G06.acceptance,G06.item-http-mutations,G11.acceptance,G11.ui-crud | Full criterion unclosed; source existence is insufficient
runtime -> G02, G16, G18
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Counterexample G02.event-capture-mounted; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G02.acceptance,G02.event-capture-mounted,G02.event-normalization,G02.session-capture-mounted,G16.acceptance,G16.postgres-observation-concurrency,G18.acceptance,G18.backup-whole-product,G18.install-desktop-auth-configuration | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G02.acceptance,G02.event-capture-mounted,G02.event-normalization,G02.session-capture-mounted,G16.acceptance,G16.observation-reopen,G16.postgres-observation-concurrency,G18.acceptance,G18.backup-whole-product,G18.install-desktop-auth-configuration,G18.readiness-store | Full criterion unclosed; source existence is insufficient
data -> G06, G07, G08, G16
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Counterexample G06.item-http-mutations; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Counterexample G06.item-http-mutations; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G06.acceptance,G06.item-http-mutations,G07.acceptance,G07.live-ingestion-atomic-identity,G07.typed-spec-reads,G08.acceptance,G16.acceptance,G16.postgres-observation-concurrency | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G06.acceptance,G06.item-http-mutations,G07.acceptance,G07.live-ingestion-atomic-identity,G07.typed-spec-reads,G08.acceptance,G16.acceptance,G16.observation-reopen,G16.postgres-observation-concurrency | Full criterion unclosed; source existence is insufficient
UI -> G09, G10, G11, G12, G19
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Counterexample G10.specification-summary; no claim other children fail
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | Counterexample G09.view-01; no claim other children fail
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | Counterexample G09.view-01; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G09.acceptance,G09.detail-scope,G09.view-01,G09.view-02,G09.view-03,G09.view-04,G09.view-05,G09.view-06,G09.view-07,G09.view-08,G09.view-09,G09.view-10,G09.view-11,G09.view-12,G09.view-13,G09.view-14,G09.view-15,G09.view-16,G09.view-17,G09.view-18,G09.view-19,G09.view-20,G09.view-21,G09.view-22,G09.view-23,G09.view-24,G09.view-25,G09.view-26,G09.view-27,G09.view-28,G09.view-29,G09.view-30,G09.view-31,G09.view-32,G09.view-33,G09.view-34,G09.view-35,G09.view-36,G09.view-37,G09.view-38,G09.view-39,G09.view-40,G09.view-41,G09.view-42,G09.view-43,G09.view-44,G09.view-45,G09.view-46,G09.view-47,G09.view-48,G09.view-49,G09.view-50,G09.view-51,G09.view-52,G09.view-53,G09.view-54,G09.view-55,G09.view-56,G09.view-57,G09.view-58,G09.view-59,G10.acceptance,G10.specification-summary,G10.summary-fallback,G11.acceptance,G11.ui-crud,G12.acceptance,G12.mcp-graph,G12.postgres-title-search,G12.sqlite-title-search,G19.acceptance,G19.async-states,G19.cli-help,G19.explicit-unsupported,G19.focus-source | Full criterion unclosed; source existence is insufficient
CLI -> G14, G17
  +-- Implementation: FAIL | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:41 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Usability: FAIL | evidence/backend/desk-reconciliation.json:1-1 | Counterexample G17.desk-installed-compose-cli; no claim other children fail
  +-- Validation: FAIL | evidence/installed-cli-help.log:1 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G14.acceptance,G14.cli-crud-parity,G14.mcp-crud-parity,G14.route-contract,G17.acceptance,G17.desk-installed-compose-cli,G17.desktop-origin | Full criterion unclosed; source existence is insufficient
MCP -> G12, G14
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | Counterexample G12.postgres-title-search; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | Counterexample G12.postgres-title-search; no claim other children fail
  +-- Validation: FAIL | evidence/installed-cli-help.log:1 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G12.acceptance,G12.mcp-graph,G12.postgres-title-search,G12.sqlite-title-search,G14.acceptance,G14.cli-crud-parity,G14.mcp-crud-parity,G14.route-contract | Full criterion unclosed; source existence is insufficient
security -> G15, G20
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Counterexample G15.producer-tenant-ownership; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Counterexample G15.producer-tenant-ownership; no claim other children fail
  +-- Validation: FAIL | evidence/test-ui-a11y-contract.log:1-6 | Counterexample G20.a11y-check-instrument; no claim other children fail
  +-- Assurance: FAIL | evidence/test-ui-a11y-contract.log:1 | Counterexample G20.a11y-check-instrument; no claim other children fail
privacy -> G04, G15
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | Counterexample G04.memory-durable-restart; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | Counterexample G04.memory-durable-restart; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G04.acceptance,G04.memory-durable-restart,G04.memory-next-session-consumer,G15.acceptance,G15.rate-limit-mounted | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G04.acceptance,G04.memory-durable-restart,G04.memory-next-session-consumer,G04.memory-pattern-distillation,G15.acceptance,G15.csrf-origin-token,G15.global-bearer,G15.producer-tenant-ownership,G15.product-allowlist,G15.rate-limit-mounted,G15.required-auth-on-local-default | Full criterion unclosed; source existence is insufficient
AX -> G19, G20
  +-- Implementation: UNKNOWN | STATUS.json#G19.acceptance,G20.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G19.acceptance,G19.async-states,G19.explicit-unsupported,G19.focus-source,G20.acceptance,G20.route-check-instrument | Full criterion unclosed; source existence is insufficient
  +-- Validation: FAIL | evidence/test-ui-a11y-contract.log:1-6 | Counterexample G20.a11y-check-instrument; no claim other children fail
  +-- Assurance: FAIL | evidence/test-ui-a11y-contract.log:1 | Counterexample G20.a11y-check-instrument; no claim other children fail
DX -> G14, G17, G19
  +-- Implementation: FAIL | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:41 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Usability: FAIL | evidence/backend/desk-reconciliation.json:1-1 | Counterexample G17.desk-installed-compose-cli; no claim other children fail
  +-- Validation: FAIL | evidence/installed-cli-help.log:1 | Counterexample G14.cli-crud-parity; no claim other children fail
  +-- Assurance: UNKNOWN | STATUS.json#G14.acceptance,G14.cli-crud-parity,G14.mcp-crud-parity,G14.route-contract,G17.acceptance,G17.desk-installed-compose-cli,G17.desktop-origin,G19.acceptance,G19.async-states,G19.cli-help,G19.explicit-unsupported,G19.focus-source | Full criterion unclosed; source existence is insufficient
deploy -> G18
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Counterexample G18.backup-whole-product; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Counterexample G18.backup-whole-product; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G18.acceptance,G18.backup-whole-product,G18.install-desktop-auth-configuration | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G18.acceptance,G18.backup-whole-product,G18.install-desktop-auth-configuration,G18.readiness-store | Full criterion unclosed; source existence is insufficient
install -> G17
  +-- Implementation: UNKNOWN | STATUS.json#G17.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: FAIL | evidence/backend/desk-reconciliation.json:1-1 | Counterexample G17.desk-installed-compose-cli; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G17.acceptance,G17.desktop-origin | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G17.acceptance,G17.desk-installed-compose-cli,G17.desktop-origin | Full criterion unclosed; source existence is insufficient
ops -> G16, G22
  +-- Implementation: UNKNOWN | STATUS.json#G16.acceptance,G22.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: FAIL | evidence/backend/live-runtime.json:1-1 | Counterexample G22.desk-manual-runtime-health-ready; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G16.acceptance,G16.postgres-observation-concurrency,G22.acceptance,G22.fleet-enroll,G22.fleet-heartbeat,G22.metrics-endpoint | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G16.acceptance,G16.observation-reopen,G16.postgres-observation-concurrency,G22.acceptance,G22.desk-manual-runtime-health-ready,G22.fleet-enroll,G22.fleet-heartbeat,G22.metrics-endpoint | Full criterion unclosed; source existence is insufficient
docs -> G01, G24
  +-- Implementation: UNKNOWN | STATUS.json#G01.acceptance,G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G01.acceptance,G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G01.acceptance,G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G01.acceptance,G24.acceptance | Full criterion unclosed; source existence is insufficient
research -> G21
  +-- Implementation: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G21.acceptance | Full criterion unclosed; source existence is insufficient
feedback -> G23
  +-- Implementation: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G23.acceptance | Full criterion unclosed; source existence is insufficient
lineage -> G05, G25
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Counterexample G05.complete-atomic-audit-replay; no claim other children fail
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Counterexample G05.complete-atomic-audit-replay; no claim other children fail
  +-- Validation: UNKNOWN | STATUS.json#G05.acceptance,G05.complete-atomic-audit-replay,G05.item-trace-snapshot,G25.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Assurance: UNKNOWN | STATUS.json#G05.acceptance,G05.complete-atomic-audit-replay,G05.item-trace-snapshot,G25.acceptance,G25.real-benchmark-causal-bridge | Full criterion unclosed; source existence is insufficient
governance -> G01, G20, G24
  +-- Implementation: UNKNOWN | STATUS.json#G01.acceptance,G20.acceptance,G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Usability: UNKNOWN | STATUS.json#G01.acceptance,G20.acceptance,G20.route-check-instrument,G24.acceptance | Full criterion unclosed; source existence is insufficient
  +-- Validation: FAIL | evidence/test-ui-a11y-contract.log:1-6 | Counterexample G20.a11y-check-instrument; no claim other children fail
  +-- Assurance: FAIL | evidence/test-ui-a11y-contract.log:1 | Counterexample G20.a11y-check-instrument; no claim other children fail
```

Each referenced goal has four independently derived cells above. Overlay aliases do not add acceptance.

## Unique leaf cell counts

| Verdict | Implementation | Usability | Validation | Assurance |
| ------- | -------------: | --------: | ---------: | --------: |
| FAIL    |             17 |        20 |          8 |         2 |
| NOT_RUN |              0 |        81 |         86 |        35 |
| PASS    |             91 |         8 |         15 |         0 |
| UNKNOWN |              1 |         0 |          0 |        72 |

Unique counted leaves: 109. Criterion guards and crosscuts excluded: 88 (25 whole-goal guards, 63 crosscuts). Parent and domain aliases excluded.

## Detailed evidence

[Acceptance leaves](acceptance.md) | [Interface leaves](interface.md) | [Backend and Desk leaves](backend.md) | [Store crosscuts](store.md)

Scope and provenance: [README](README.md), [raw intent census](evidence/intent-report.json), [raw interface census](evidence/evidence-cells.json).

## Cheapest remaining evidence work

- Restore or select an authorized frontend subject:5direct8091paths failed and54dynamic paths unrun because frontend absent;later8080projects/itemsAPI200means API-dead inference is invalid.
- Repair quote-sensitive a11y and removed-App.jsx checker inputs in a separately scoped source change, then execute without captures.
- Bind each 59 route observation to actual typed records and invoke text-only external journeys; source existence alone does not close G09.
- Adjudicate retained/superseded/deferred applicability of historical rows before treating them as accepted leaf obligations.

## Authority-dependent work

- G23: independent unfamiliar beneficiary requires an authorized real user and owned input; proposed pilot is not new accepted scope.
- Desk startup qualification follows bundle/runtime/preflight discovery and requires a separately authorized owned action; this observation starts no service.
