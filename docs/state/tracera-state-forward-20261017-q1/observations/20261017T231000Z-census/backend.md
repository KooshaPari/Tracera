# Backend evidence leaves

> GENERATED from STATUS.json.

```text
G02.event-normalization [observation] Normalize CI/test/commit/review events preserving timestamps and refs
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/events.rs:53-53 | Pure normalizer exists; not ingress/persistence proof
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/events.rs:53-53 | Pure normalizer exists; not ingress/persistence proof
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/events.rs:53-53 | Pure normalizer exists; not ingress/persistence proof
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/events.rs:53-53 | Pure normalizer exists; not ingress/persistence proof
G02.event-capture-mounted [observation] Capture actual session/events through mounted external ingress
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Both events collection/detail explicitly unavailable501; no matching Store contract
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Both events collection/detail explicitly unavailable501; no matching Store contract
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Both events collection/detail explicitly unavailable501; no matching Store contract
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/events.rs:5-5 | Both events collection/detail explicitly unavailable501; no matching Store contract
G02.session-capture-mounted [observation] Capture and query Codex project sessions
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:293-293 | Session routes any(not_implemented); benchmark causality does not substitute session capture
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:293-293 | Session routes any(not_implemented); benchmark causality does not substitute session capture
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:293-293 | Session routes any(not_implemented); benchmark causality does not substitute session capture
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:293-293 | Session routes any(not_implemented); benchmark causality does not substitute session capture
G03.swee-directed-queries [observation] Read persisted directed SWEE graph, paths/cycles and artifact-independent identifiers
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/graph.rs:48-48 | Real Store graph; not artifact graph or crossrun trace by source semantics
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/graph.rs:48-48 | Real Store graph; not artifact graph or crossrun trace by source semantics
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/graph.rs:48-48 | Real Store graph; not artifact graph or crossrun trace by source semantics
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/graph.rs:48-48 | Real Store graph; not artifact graph or crossrun trace by source semantics
G03.persisted-artifact-trace [observation] Read incident persisted artifact links and impact direction
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:339-339 | Separate artifact trace store vsSWEE graph; do not conflate
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:339-339 | Separate artifact trace store vsSWEE graph; do not conflate
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:339-339 | Separate artifact trace store vsSWEE graph; do not conflate
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:339-339 | Separate artifact trace store vsSWEE graph; do not conflate
G03.graph-impact-traverse [observation] Execute specialized impact/traverse/multipath semantics
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Unsupportedhandlers501
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Unsupportedhandlers501
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Unsupportedhandlers501
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:223-223 | Unsupportedhandlers501
G03.trace-matrix [observation] Build coverage matrix and detect missing required linktypes
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/traceability/traceability.rs:124-124; evidence/backend/traceability-tests.log:1 | 9freshpuretestsPASS; not externallycompletejourney
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/traceability/traceability.rs:124-124; evidence/backend/traceability-tests.log:1 | 9freshpuretestsPASS; not externallycompletejourney
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/traceability/traceability.rs:124-124; evidence/backend/traceability-tests.log:1 | 9freshpuretestsPASS; not externallycompletejourney
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/traceability/traceability.rs:124-124; evidence/backend/traceability-tests.log:1 | 9freshpuretestsPASS; not externallycompletejourney
G04.memory-pattern-distillation [observation] Extract recurring graph patterns and manage confidence/pruning
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:198-198; evidence/backend/memory-tests.log:1 | 13freshpuretestsPASS; source module not mounted consumer
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:198-198; evidence/backend/memory-tests.log:1 | 13freshpuretestsPASS; source module not mounted consumer
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:198-198; evidence/backend/memory-tests.log:1 | 13freshpuretestsPASS; source module not mounted consumer
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:198-198; evidence/backend/memory-tests.log:1 | 13freshpuretestsPASS; source module not mounted consumer
G04.memory-durable-restart [observation] Persist distilled memory across restart
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | CurrentVec/Instant state, no Store memorymethods or persistence serialization
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | CurrentVec/Instant state, no Store memorymethods or persistence serialization
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | CurrentVec/Instant state, no Store memorymethods or persistence serialization
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/distiller.rs:14-14 | CurrentVec/Instant state, no Store memorymethods or persistence serialization
G04.memory-next-session-consumer [observation] Consume attributable distilled memory in next real session
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:20-20 | WholecratesRustsearch found no MemoryDistiller externalcall; publicexports alone notintegration
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:20-20 | WholecratesRustsearch found no MemoryDistiller externalcall; publicexports alone notintegration
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:20-20 | WholecratesRustsearch found no MemoryDistiller externalcall; publicexports alone notintegration
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/memory/distillation/mod.rs:20-20 | WholecratesRustsearch found no MemoryDistiller externalcall; publicexports alone notintegration
G05.item-trace-snapshot [observation] Export/import canonical items and internal trace links
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:154-154 | Supported JSON projection only; source includes tests, notfreshlyexecutedhere
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:154-154 | Supported JSON projection only; source includes tests, notfreshlyexecutedhere
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:154-154 | Supported JSON projection only; source includes tests, notfreshlyexecutedhere
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:154-154 | Supported JSON projection only; source includes tests, notfreshlyexecutedhere
G05.complete-atomic-audit-replay [observation] Replay all semantic state atomically including observations and memory
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Item/link create calls sequential; no observations/memory in snapshot; partialwriteerrorspossible
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Item/link create calls sequential; no observations/memory in snapshot; partialwriteerrorspossible
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Item/link create calls sequential; no observations/memory in snapshot; partialwriteerrorspossible
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:207-207 | Item/link create calls sequential; no observations/memory in snapshot; partialwriteerrorspossible
G06.item-http-mutations [observation] External item creation/update/delete mounted with canonical persistence
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Storecreate_item exists butHTTPmutations typed501
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Storecreate_item exists butHTTPmutations typed501
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Storecreate_item exists butHTTPmutations typed501
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/router.rs:196-196 | Storecreate_item exists butHTTPmutations typed501
G10.specification-summary [observation] Specifications Hub aggregate includes ADR/contracts/features health semantics
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Explicit501 replaces olddeceptivestub, missingcapabilityremains
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Explicit501 replaces olddeceptivestub, missingcapabilityremains
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Explicit501 replaces olddeceptivestub, missingcapabilityremains
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:281-281 | Explicit501 replaces olddeceptivestub, missingcapabilityremains
G07.typed-spec-reads [observation] Paginated typed ADR/contract/feature/scenario projections retain canonical data
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:76-76 | Completepagedload+budget+wrongprojectcontrols atsource
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:76-76 | Completepagedload+budget+wrongprojectcontrols atsource
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:76-76 | Completepagedload+budget+wrongprojectcontrols atsource
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/specs.rs:76-76 | Completepagedload+budget+wrongprojectcontrols atsource
G12.sqlite-title-search [observation] Title substring search returns persistedprojectscopeditems
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/items.rs:1-30 | Notsemanticsearch; source defines stableIDorder
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/items.rs:1-30 | Notsemanticsearch; source defines stableIDorder
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/items.rs:1-30 | Notsemanticsearch; source defines stableIDorder
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/items.rs:1-30 | Notsemanticsearch; source defines stableIDorder
G12.postgres-title-search [observation] PostgreSQL supports mountedtitle search
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | PgStoredoesnotoverride defaultUnsupportedOperation
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | PgStoredoesnotoverride defaultUnsupportedOperation
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | PgStoredoesnotoverride defaultUnsupportedOperation
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/store.rs:259-259 | PgStoredoesnotoverride defaultUnsupportedOperation
G07.live-ingestion-atomic-identity [observation] Live GitHub/Jira ingestion is source-namespaced idempotent and atomic
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/ingest/persist.rs:39-39 | story-{external_id}; evidence/linkrandomUUID; independentwrites, notcanonicalobservationatomicbatch
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/ingest/persist.rs:39-39 | story-{external_id}; evidence/linkrandomUUID; independentwrites, notcanonicalobservationatomicbatch
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/ingest/persist.rs:39-39 | story-{external_id}; evidence/linkrandomUUID; independentwrites, notcanonicalobservationatomicbatch
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/ingest/persist.rs:39-39 | story-{external_id}; evidence/linkrandomUUID; independentwrites, notcanonicalobservationatomicbatch
G15.global-bearer [observation] Configured process-wide bearer rejects unauthenticatedrequests
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:15-15; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:15-15; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:15-15; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:15-15; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
G15.product-allowlist [observation] Processproductallowlist denies foreignproduct acrossdurablehandlers
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/auth.rs:124-124; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Globalallowlist only, notperprincipal
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/auth.rs:124-124; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Globalallowlist only, notperprincipal
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/auth.rs:124-124; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Globalallowlist only, notperprincipal
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/auth.rs:124-124; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Globalallowlist only, notperprincipal
G15.producer-tenant-ownership [observation] Authenticate producer/tenantidentity ratherthancallerassertion
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Negativewitnessconfirmedforgedvalidtenantaccepted200; validationPASSmeanswitnessran, notsecurityaccepted
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Negativewitnessconfirmedforgedvalidtenantaccepted200; validationPASSmeanswitnessran, notsecurityaccepted
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Negativewitnessconfirmedforgedvalidtenantaccepted200; validationPASSmeanswitnessran, notsecurityaccepted
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:49-49; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Negativewitnessconfirmedforgedvalidtenantaccepted200; validationPASSmeanswitnessran, notsecurityaccepted
G15.required-auth-on-local-default [observation] Require bearer bydefaultonloopbackproductscope
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:1-30; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/no-token-receipt.json | Anonymousreachesallowlistedhandlerwithouttoken; localdevmodeisexplicitcurrentbehavior,strongerownershipgateunmet
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:1-30; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/no-token-receipt.json | Anonymousreachesallowlistedhandlerwithouttoken; localdevmodeisexplicitcurrentbehavior,strongerownershipgateunmet
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:1-30; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/no-token-receipt.json | Anonymousreachesallowlistedhandlerwithouttoken; localdevmodeisexplicitcurrentbehavior,strongerownershipgateunmet
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/auth.rs:1-30; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/no-token-receipt.json | Anonymousreachesallowlistedhandlerwithouttoken; localdevmodeisexplicitcurrentbehavior,strongerownershipgateunmet
G15.csrf-origin-token [observation] Mutations requirecanonicalbrowseroriginandissuedprocessCSRFtoken
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:22-22; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:22-22; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:22-22; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:22-22; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json
G15.rate-limit-mounted [observation] Mount implemented perIPratelimiter onHTTPsurface
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:103-103 | Functionexistsbutbuild_router/mainnevermountit; noobserved429gate
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:103-103 | Functionexistsbutbuild_router/mainnevermountit; noobserved429gate
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:103-103 | Functionexistsbutbuild_router/mainnevermountit; noobserved429gate
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/middleware.rs:103-103 | Functionexistsbutbuild_router/mainnevermountit; noobserved429gate
G16.observation-reopen [observation] SQLitecanonicalobservationatomicbatch survivesrestartandreplay
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/product_observations.rs:12-12; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/engineering-journey-receipt.json
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/product_observations.rs:12-12; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/engineering-journey-receipt.json
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/product_observations.rs:12-12; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/engineering-journey-receipt.json
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/sqlite_store/product_observations.rs:12-12; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/engineering-journey-receipt.json
G16.postgres-observation-concurrency [observation] PostgreSQL immutableobservationidentityfailsconcurrentconflictatomically
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/pg_store/product_observations.rs:25-25 | 8ddchangedcode; latestrealPGexecutionnotperformedthislane; olderreceipt notcredited
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/pg_store/product_observations.rs:25-25 | 8ddchangedcode; latestrealPGexecutionnotperformedthislane; olderreceipt notcredited
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/pg_store/product_observations.rs:25-25 | 8ddchangedcode; latestrealPGexecutionnotperformedthislane; olderreceipt notcredited
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/pg_store/product_observations.rs:25-25 | 8ddchangedcode; latestrealPGexecutionnotperformedthislane; olderreceipt notcredited
G18.readiness-store [observation] Readiness probesactualStore andreturns503failure
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/health.rs:43-43; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json | Freshpositiveonly; databasefailureunitcasepartof7route tests notreadyznegative
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/health.rs:43-43; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json | Freshpositiveonly; databasefailureunitcasepartof7route tests notreadyznegative
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/health.rs:43-43; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json | Freshpositiveonly; databasefailureunitcasepartof7route tests notreadyznegative
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/health.rs:43-43; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/runtime-receipt.json | Freshpositiveonly; databasefailureunitcasepartof7route tests notreadyznegative
G18.install-desktop-auth-configuration [observation] Desktopbackendinstaller suppliesrequiredproductscopeandcredentialconfiguration
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:scripts/install-local-runtime.sh:78-78 | Generatedlaunchagentsetsbind+DBbutnotnewproductallowlistorcredential; noinstallrunhere
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:scripts/install-local-runtime.sh:78-78 | Generatedlaunchagentsetsbind+DBbutnotnewproductallowlistorcredential; noinstallrunhere
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:scripts/install-local-runtime.sh:78-78 | Generatedlaunchagentsetsbind+DBbutnotnewproductallowlistorcredential; noinstallrunhere
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:scripts/install-local-runtime.sh:78-78 | Generatedlaunchagentsetsbind+DBbutnotnewproductallowlistorcredential; noinstallrunhere
G18.backup-whole-product [observation] Backupandrestoreallpersistedproductstatewithrestartproof
  +-- Implementation: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Narrowitem/linkJSONnotwholeproductstorebackup; observationtablesomitted
  +-- Usability: FAIL | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Narrowitem/linkJSONnotwholeproductstorebackup; observationtablesomitted
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Narrowitem/linkJSONnotwholeproductstorebackup; observationtablesomitted
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/export_import.rs:1-30 | Narrowitem/linkJSONnotwholeproductstorebackup; observationtablesomitted
G22.desk-manual-runtime-health-ready [observation] Existing manualdeskbackend respondshealth/readiness within5seconds
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/health.rs:43-43; live-runtime.json | Differentdeployedartifact6202AB83..., sourceSHAnotproven. Positive8080/8091ready200at22:26 supersededbyallhealth/ready/metricsGETtimeoutsat22:54:33. Processpresentnotregisteredservice.
  +-- Usability: FAIL | evidence/backend/live-runtime.json:1-1 | Differentdeployedartifact6202AB83..., sourceSHAnotproven. Positive8080/8091ready200at22:26 supersededbyallhealth/ready/metricsGETtimeoutsat22:54:33. Processpresentnotregisteredservice.
  +-- Validation: PASS | evidence/backend/live-runtime.json:1-1 | Differentdeployedartifact6202AB83..., sourceSHAnotproven. Positive8080/8091ready200at22:26 supersededbyallhealth/ready/metricsGETtimeoutsat22:54:33. Processpresentnotregisteredservice.
  +-- Assurance: NOT_RUN | evidence/backend/live-runtime.json:1-1 | Differentdeployedartifact6202AB83..., sourceSHAnotproven. Positive8080/8091ready200at22:26 supersededbyallhealth/ready/metricsGETtimeoutsat22:54:33. Processpresentnotregisteredservice.
G22.metrics-endpoint [observation] ExposeprocessPrometheusmetricsincludingunavailablecounter
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/main.rs:156-156 | Mountedsource; noproductionmetricsGETyet
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/main.rs:156-156 | Mountedsource; noproductionmetricsGETyet
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/main.rs:156-156 | Mountedsource; noproductionmetricsGETyet
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/main.rs:156-156 | Mountedsource; noproductionmetricsGETyet
G22.fleet-enroll [observation] Cloudflare Worker fleet enrollment validates bearer and persists node in KV
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:148-184 | Broadened inspection found actual edge implementation; initial server-only FAIL superseded. No fresh deployedWorker witness.
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:148-184 | Broadened inspection found actual edge implementation; initial server-only FAIL superseded. No fresh deployedWorker witness.
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:148-184 | Broadened inspection found actual edge implementation; initial server-only FAIL superseded. No fresh deployedWorker witness.
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:148-184 | Broadened inspection found actual edge implementation; initial server-only FAIL superseded. No fresh deployedWorker witness.
G22.fleet-heartbeat [observation] Fleet status report persists last-seen and desired generation in KV
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:254-274 | Edgefleet_report exists, serverqueue heartbeat separateoptinprimitive; no fresh deployedWorker witness.
  +-- Usability: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:254-274 | Edgefleet_report exists, serverqueue heartbeat separateoptinprimitive; no fresh deployedWorker witness.
  +-- Validation: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:254-274 | Edgefleet_report exists, serverqueue heartbeat separateoptinprimitive; no fresh deployedWorker witness.
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-edge/src/lib.rs:254-274 | Edgefleet_report exists, serverqueue heartbeat separateoptinprimitive; no fresh deployedWorker witness.
G25.real-benchmark-causal-bridge [observation] ActualHeliosoutput->manuallyassignedproduct/capability->durableobservations
  +-- Implementation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:35-35; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Historicalactualproducerreconsumed; nofreshharnessruncredited8dd; notnextsessionmemory/discrepancyjourney
  +-- Usability: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:35-35; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Historicalactualproducerreconsumed; nofreshharnessruncredited8dd; notnextsessionmemory/discrepancyjourney
  +-- Validation: PASS | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:35-35; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Historicalactualproducerreconsumed; nofreshharnessruncredited8dd; notnextsessionmemory/discrepancyjourney
  +-- Assurance: NOT_RUN | 8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6:crates/tracera-server/src/routes/benchmark_observations.rs:35-35; docs/state/tracera-state-forward-20261017-q1/observations/20261017T215321Z-runtime-8dd0e096/evidence/substantive-bridge-journey-receipt.json | Historicalactualproducerreconsumed; nofreshharnessruncredited8dd; notnextsessionmemory/discrepancyjourney
G17.desk-installed-compose-cli [observation] Installed Tracera CLI resolves itsComposeprofile and can reportstackstatus
  +-- Implementation: PASS | evidence/backend/desk-reconciliation.json:1-1 | Installed0.1CLIexists; resolvesrelativeexecutable, missingbundleancestor; actualworktreeComposefileexistselsewhere. Cwdchangealoneisnotdocumentedfix; --rootcandidatebutstatuscanwriteenv/symlinkandwasnotrununderreadonlyconstraint. ExactinstalledCLI sourceSHAunknown; source8ddresolutioncontractiscomparativeevidenceonly.
  +-- Usability: FAIL | evidence/backend/desk-reconciliation.json:1-1 | Installed0.1CLIexists; resolvesrelativeexecutable, missingbundleancestor; actualworktreeComposefileexistselsewhere. Cwdchangealoneisnotdocumentedfix; --rootcandidatebutstatuscanwriteenv/symlinkandwasnotrununderreadonlyconstraint. ExactinstalledCLI sourceSHAunknown; source8ddresolutioncontractiscomparativeevidenceonly.
  +-- Validation: PASS | evidence/backend/desk-reconciliation.json:1-1 | Installed0.1CLIexists; resolvesrelativeexecutable, missingbundleancestor; actualworktreeComposefileexistselsewhere. Cwdchangealoneisnotdocumentedfix; --rootcandidatebutstatuscanwriteenv/symlinkandwasnotrununderreadonlyconstraint. ExactinstalledCLI sourceSHAunknown; source8ddresolutioncontractiscomparativeevidenceonly.
  +-- Assurance: NOT_RUN | evidence/backend/desk-reconciliation.json:1-1 | Installed0.1CLIexists; resolvesrelativeexecutable, missingbundleancestor; actualworktreeComposefileexistselsewhere. Cwdchangealoneisnotdocumentedfix; --rootcandidatebutstatuscanwriteenv/symlinkandwasnotrununderreadonlyconstraint. ExactinstalledCLI sourceSHAunknown; source8ddresolutioncontractiscomparativeevidenceonly.
```
