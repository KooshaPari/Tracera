# Tracera Deep Audit — Part 2

Scope: Areas G-Observability, H-Performance, I-Data & Persistence, J-Docs/DX, K-Ops/Deploy, L-Governance/Traceability.  
Rubric: `0–5` score with evidence in `file:line` format (or absence).

## G — Observability

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| Correlation ID propagation | 4/5 | `src/tracertm/api/middleware/request_id.py:23` creates request-context ContextVar, sets outbound header `X-Request-ID` | Middleware is app-level only; background jobs do not inherit the same correlation context. | Add propagation middleware to queue/workers and attach IDs to async background traces. |
| Distributed tracing bootstrap (Go tracer) | 5/5 | `backend/internal/tracing/tracer.go:38` initializes tracer provider, sampler, OTLP exporter, propagator. | Runtime metrics/heartbeat on tracer failures are not surfaced as first-class health signals. | Emit startup/teardown tracer status metrics/events and fail CI if tracer initialization diverges unexpectedly. |
| Distributed tracing bootstrap (Rust trace spans) | 3/5 | `crates/tracera-core/src/tracer.rs:11`-`17` (tracing initialization), `make_span` use. | No explicit OTLP exporter lifecycle tests in Rust crate. | Add exporter transport tests and an end-to-end span smoke test with OTel test collector. |
| Health/readiness endpoints | 4/5 | `src/tracertm/api/main.py:28` (`/healthz`) and `:36` (`/readyz`). | No downstream dependency readouts or explicit liveness/readiness split in Go/Neo4j/Python gateways. | Add dependency checks (DB/cache/queue) behind readiness and return structured probe status payload. |
| Logging structure/levels | 2/5 | `backend/internal/tracing/tracer.go:49`-`113` uses `slog.Info` with key-value pairs; Python has no structured logging callsite near API factory. | Python-side logs are not consistently emitted through a structured logger in these routers/services. | Standardize on structured logging (JSON) in Python API and backend clients; include request-id in each emitted log record. |
| Error reporting/Sentry wiring | 3/5 | `backend/internal/config/config.go:163` and `crates/tracera-core/src/config.rs:229` define Sentry DSN/sample/debug settings. | No consistent error capture examples in API exception paths for Sentry. | Wire global exception handlers in Python + Go to capture exceptions with trace IDs and release metadata. |
| Metrics collection | 0/5 | `backend/internal/observability/otel.go:31`-`52` only sets OTEL endpoints; no metrics API exposed or consumed. | No explicit metric counter/gauge instrumentation in core APIs. | Add Prometheus counters/gauges/histograms for request latency, errors, queue depth, and trace writes. |
| OTEL contract validation in config | 4/5 | `crates/tracera-core/src/config.rs:216`-`228`, `backend/internal/config/config.go:151`-`162` map OTEL vars, prioritized fallback. | Variable names differ across services; no centralized schema registry. | Publish canonical env contract and deprecate unversioned duplicates via strict config validation. |
| Dashboards in deploy topology | 3/5 | `docker-compose.yml:142`-`220` includes Prometheus + Grafana service and exporters. | No committed Grafana alerting/rule sets or screenshoted SLO dashboards. | Commit dashboard JSON + alert rules with a documented import flow. |
| Audit trail for governance/ops events | 1/5 | `src/tracertm/governance.py:49` tracks violations in report objects only; no immutable trail store. | No durable audit record for governance checks and remediation actions. | Persist governance check decisions with actor/time/hash in tamper-evident store. |
| Alerting and incident hooks | 1/5 | No concrete alerting config in repository files read for this area. | No PagerDuty/Slack alert rule set found. | Add deployment and SLO alert routing with runbook links. |
| Observability tests | 2/5 | `backend/internal/observability/otel_test.go:9`-`65`; `backend/internal/tracing/tracer.go` test coverage for defaults absent. | Coverage covers config translation but not runtime metric/tracing pipeline health. | Add contract tests for trace/scope names, metric emission, and endpoint availability checks. |

Per-area roll-up: avg `2.67/5`, subtotal `32/60 = 53.3%`.

## H — Performance & Scalability

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| Matrix build complexity | 3/5 | `src/tracertm/performance/matrix.py:66`-`83` uses single-pass grouping and stable tuple storage. | No asymptotic bounds in docs/benchmarks; algorithmic complexity not explicitly communicated. | Document complexity per endpoint and validate against target input scale docs. |
| Deterministic performance baselining | 5/5 | `tests/performance/test_matrix_build_benchmark.py:38`-`46` compares output and regression threshold. | Baseline target currently tied to local reference runtime only. | Add machine-independent warmup and versioned perf budgets with CI thresholds per profile. |
| Load/regression workflow | 5/5 | `.github/workflows/performance-regression.yml:68`-`69`, `235`-`394` include smoke/load/report jobs. | Hard-coded tool/version assumptions for CI environments. | Parameterize runner constraints and publish deterministic environment metadata with results. |
| Async/concurrency handling | 2/5 | `src/tracertm/api/routers/traceability.py:137`-`169` uses deque BFS for traversal; no explicit concurrency controls around queue growth. | Potential unbounded queue growth for dense graphs at scale. | Add queue length/cell count guards and circuit breakers for deep fan-out cases. |
| Backpressure/flow-control | 1/5 | No throttling or queue pressure guard in `blast_radius_service.py`/`traceability.py`. | Burst processing can expand in-memory and exhaust CPU. | Add request-level and per-tenant rate/queue throttles before BFS traversal begins. |
| Caching strategy | 0/5 | No cache lookup path in matrix or impact computation paths reviewed. | Repeated link recomputation under same request key. | Introduce memoized matrix cell/intermediate result cache with invalidation policy. |
| Resource bounds and guardrails | 1/5 | `crates/tracera-core/src/rate_limit.rs` defines limiters, but API usage from routers is not evidenced. | No global in-service limiter wiring at API entry in reviewed files. | Enforce rate limits at gateway and Python API entry using a shared limiter config. |
| Streaming vs buffering | 1/5 | `src/tracertm/performance/matrix.py:73`-`83` builds full `source_ids`, `target_ids`, `cells` collections before return. | High-memory behavior under large inputs. | Add streaming builders and chunked serialization for large matrices. |
| Hot-path profiling | 0/5 | `src/tracertm/performance` has benchmark only; no profiling hooks in API runtime. | No flamegraph/profiler integrations found in core request path. | Add optional request profiling sampling endpoint (pprof/py-spy compatible) for profiling sessions. |
| N+1 and DB query efficiency | 1/5 | API endpoints operate in memory; DB graph reads delegated to storage and blast radius adjacency may be eager from upstream inputs. | No query-batching evidence in this layer. | Audit persistence adapters for eager joins and add prefetch/batch strategies for impact traversal. |
| Timeout/Retry policy | 2/5 | `backend/internal/config/config.go:127`-`170` has env for client and service settings; Rust has typed config with explicit getters. | Cross-language timeout policy not tied to a shared policy doc. | Centralize timeout/retry policies and enforce via config schema + tests. |
| Blast-radius scoring model efficiency | 3/5 | `src/tracertm/services/blast_radius_service.py:57`-`75` BFS with confidence/weight scoring and visited set. | No complexity cap documented for deep/high-degree graphs. | Add per-run visited-node cap and confidence-floor pruning with explicit contract. |
| Memory ceiling / guardrails | 1/5 | `src/tracertm/performance/matrix.py:33` and `traceability.py:188` materialize complete matrices/cell lists. | No memory ceilings or fallback path if limit exceeded. | Introduce hard page/element caps and fallback pagination/continuation tokens. |

Per-area roll-up: avg `1.83/5`, subtotal `22/60 = 36.7%`.

## I — Data & Persistence

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| Canonical graph schema contract | 5/5 | `src/tracertm/ports/graph_contract.py:26`-`33`, `164`-`192` and protocol methods. | Contract exists but runtime enforcement depends on adapter integrations in callsites. | Add enforcement tests at API and storage boundaries for every mutation path. |
| Versioned migrations present | 5/5 | `alembic/versions/063_add_item_comments.py:3`-`40` with upgrade/downgrade. | Migration coverage for non-comment tables not surfaced in one overview file. | Add migration index/register artifact or catalog with backward compatibility notes. |
| Migrations reversible | 5/5 | `063_add_item_comments.py:39`-`41` includes downgrade drop table. | Reversibility limited to tested path for this specific migration. | Expand downgrade audit in migration smoke tests across full revision chain. |
| Data indexing | 3/5 | `alembic/versions/063_add_item_comments.py:32`-`36` adds 2 indexes. | Indexing strategy is partial; no full traceability-index map in one schema doc. | Add index policy for hotspot query paths (artifact id, requirement/spec joins). |
| Data validation on write | 4/5 | `src/tracertm/ports/graph_contract.py:134`-`160` validate nodes/edges before persistence; tests in `tests/unit/ports/test_graph_contract.py`. | Runtime writes can bypass graph contract if called directly through lower-level writer. | Route all graph writes through validated port adapters with explicit compile-time interface checks. |
| Transaction/session management | 2/5 | `src/tracertm/database/connection.py:20`-`33` and `46`-`47` expose lazy session factory. | No explicit transaction boundaries or retry wrappers shown. | Add transaction decorators/retry wrappers for write-heavy services and test rollback semantics. |
| Backup/restore & disaster recovery | 0/5 | No backup script/docs in reviewed area. | No evidence of snapshot, PITR, or restore drill documentation. | Add backup/restore runbooks and automation with verification restores in CI. |
| Referential integrity constraints | 2/5 | SQL migration uses core columns but no explicit FK examples in shown migration. | Graph link and requirement/project integrity enforced at app-layer only in parts. | Add explicit FK constraints and consistency checks where supported by DB driver. |
| Type fidelity (ID/state) | 2/5 | UUID conversion at writer (`neo4j_trace_link_writer.py:150`, `159`, `193`) and graph nodes typed via enums. | Mixed id types (`str`/`UUID`) appears in several places. | Normalize ID handling through one value object and schema migration if needed. |
| Projecting to storage backends | 4/5 | `src/tracertm/storage/neo4j_graph_port.py:155`-`180` and `src/tracertm/storage/neo4j_trace_link_writer.py:74`-`136`. | Backend adapter supports fallback memory mode, which can hide production write failures in tests. | Fail fast when Neo4j dependency/writer unavailable in non-test environments. |
| Graph query semantics consistency | 3/5 | `neo4j_trace_link_writer.py:154`-`200` and graph-port adapter mapping. | Direction/edge-type conversion logic duplicated and partially lossy (`traces_to` mapping). | Add a canonical mapping contract test for all `EdgeType` round-trips. |
| Data persistence coverage across pillars | 2/5 | POCs exist in GraphPort + Neo4j writer; no cross-feature persistence matrix in docs. | No explicit cross-feature persistence coverage table connecting features↔tables. | Add a persistence matrix in docs linking each endpoint to entities and persistence checks. |
| Audit metadata / provenance | 1/5 | `src/tracertm/storage/neo4j_trace_link_writer.py` stores metadata dicts, but no immutable provenance chain. | No immutable history and hash chaining for changes. | Introduce change-event table with actor/project revision and hash chain. |

Per-area roll-up: avg `2.00/5`, subtotal `24/60 = 40.0%`.

## J — Docs / Developer Experience

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| README is accurate/authoritative | 4/5 | `README.md:3`-`4` and `README.md:27`-`30` provide canonical work-state and overview. | README includes operational caveats and historical artifacts that may not be production-oriented. | Clarify canonical truth in README and keep progress badges tied to current branch gates only. |
| Quickstart onboarding | 2/5 | `README.md:3`-`4` links to integration/consolidate state, but install/run steps beyond scope are sparse. | Missing one-command onboarding path from clone to serving API + frontend. | Add `quickstart` section with env/bootstrap + first endpoint check. |
| Setup/install instructions | 2/5 | `docs/tooling.md:42`-`77` and `47`-`105` include command matrix. | Commands are command-heavy and contain known caveats (“some make targets missing”). | Add reproducible `task`-first instructions with exact prerequisites matrix. |
| API docs + contracts | 2/5 | `docs/traceability.md:1`-`10` and `docs/operations/journey-traceability.md` imply traceability docs. | Not comprehensive for all endpoints/features. | Expand API reference with endpoints, schema examples, and deprecation status. |
| End-to-end developer flow docs | 1/5 | `docs/operations/journey-traceability.md:11`-`14` are placeholders with unchecked tasks. | No end-to-end journey examples verified with acceptance criteria. | Fill journey manifest workflow and link to smoke test automation. |
| Example quality and runnable code | 1/5 | `docs/ADR_MODEL_DECOUPLE_STRATEGY.md:31`-`35` sets planned implementation steps; `docs/traceability.md` has minimal examples. | Examples are roadmap-like, not runnable code. | Add executable snippets (curl/new tests) with expected outputs. |
| Governance doc structure | 1/5 | `CONTRIBUTING.md:58`-`63` references `docs/governance/background_agent_policy.md`, and `Test-Path` confirms path missing. | Canonical governance policy file absent from repository path checked. | Add `docs/governance/background_agent_policy.md` and link in AGENTS + CONTRIBUTING. |
| ADR practice | 3/5 | `docs/ADR_MODEL_DECOUPLE_STRATEGY.md:1`-`4` + `56`-`57` uses ADR convention. | ADR is DRAFT and explicitly pending decisions. | Promote to approved state or relocate stale ADRs under explicit ADR index. |
| ADR/test traceability | 2/5 | `docs/evidence-contract.md:1`-`13` defines explicit evidence shape. | No link map to implemented ADR IDs in current codebase. | Add ADR index mapping with `doc->owner->file` references. |
| DX command ergonomics | 2/5 | `docs/tooling.md:42`-`120` and `README` scripts define many commands. | Fragmented command surfaces (`make`, `bun`, `uv`, `task`) without canonical one-liner wrappers. | Define one supported command entrypoint per workflow (`task lint`, `task test`, etc.). |
| API reference discoverability | 3/5 | `.github/workflows/openapi-docs.yml:1`-`24` + `53`-`56` generate specs from backend and publish artifacts. | Generated docs may be stale because publish step writes back in same repo via commit push. | Add signed docs artifact checks and immutable docs publishing channel. |
| Traceability docs to code linkage | 2/5 | `docs/traceability.md:5`-`10` and `src/tracertm/ports/graph_contract.py:1`-`5` but no explicit link map. | Matrix rows exist without explicit implementation links for each requirement. | Add FR-to-file ownership map with evidence IDs per requirement. |
| Docs maintenance quality | 2/5 | `docs/SSOT.md:3`-`24` and `docs/operations/journey-traceability.md:9`-`14` are skeletal and checklist-like. | Multiple key docs are placeholders and do not describe runtime behavior. | Rewrite SSOT and Journey docs with current runbooks and ownership matrix. |

Per-area roll-up: avg `2.00/5`, subtotal `24/60 = 40.0%`.

## K — Ops / Deploy

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| Containerized delivery | 4/5 | `docker-compose.yml:1`-`252` defines multi-service stack with health checks. | No explicit production hardening matrix (resource limits, securityContext). | Add production overlay profile with hardened runtime settings. |
| Compose stack completeness | 2/5 | `docker-compose.yml` lacks neo4j/minio despite docs/tooling saying production stack has them (`docs/tooling.md:27`-`31`). | Mismatch between docs and root compose artifacts. | Align compose files to one canonical environment manifest and remove drift. |
| Testing/test env compose | 4/5 | `backend/docker-compose.test.yml:2`-`84` includes postgres/redis/neo4j/nats with health checks. | Only covers integration surface; no chaos/chaos testing profile. | Add chaos/rollback rehearsal compose profile. |
| Process compose for local ops | 3/5 | `process-compose.yml:3`-`95` defines API/frontend/dev process orchestration. | No environment/credential bootstrap step shown. | Add local bootstrap and required env docs for process-compose. |
| Deploy pipeline implementation | 1/5 | `.github/workflows/ci-cd.yml:145`-`155` placeholder `echo "Deploying to production..."`. | Deployment commands are placeholders and no real rollout behavior. | Replace with concrete deploy action, artifact promotion, and post-deploy checks. |
| Rollback pipeline implementation | 1/5 | `.github/workflows/deployment-rollback.yml:113`-`146` and `179`-`217` contain placeholder comments only. | No actual rollback command execution path. | Implement platform-specific rollback automation + verification matrix + dry-run mode. |
| Health checks in deploy gates | 2/5 | `.github/workflows/deployment-rollback.yml:73`-`84` and `152`-`163` run simple curl health checks pre/post rollback. | No retry/backoff with SLO-based thresholds for production safety. | Add bounded retry + traffic impact guardrails + manual approval gates for prod. |
| Secrets management | 2/5 | `docker-compose.yml:57`-`60` and env placeholders pass secrets through repo env; `GRAFANA` uses required vars. | Secrets embedded in CI command lines or environment defaults not fully formalized. | Move secrets to vault/manager integration and forbid local files in CI. |
| Release/rollback visibility | 2/5 | `.github/workflows/deployment-rollback.yml` and CI include minimal issue/comment automation. | No release artifact changelog or signed rollout evidence. | Add release manifest with canary → rollout → promote evidence. |
| Reproducible builds | 3/5 | `.github/workflows/ci-cd.yml:136`-`145` and `135` builds image; `go build` in tests. | No SBOM/hash pinning at artifact level for reproducibility. | Add image digest pinning and dependency lock attestation. |
| Security guardrails in CI | 4/5 | `.github/workflows/governance-gates.yml:17`-`42`, `security-scans.yml:38`-`95`, `security-guard.yml:24`-`27`. | Guardrails are present but some gates are shallow/no-fail with `|| true`. | Tighten gates to fail on high-risk findings and policy violations. |
| Dependency vulnerability policy | 4/5 | `security-scans.yml:26`-`36`, `55`-`61`, `78`-`95`. | `npm/pip` scans continue on warnings; no gate-to-gate escalation. | Enforce CVSS thresholds and block merge on high-severity new vulns. |
| Ops runbook completeness | 1/5 | `docs/operations/journey-traceability.md` and `docs/SSOT.md` are incomplete for runbooks. | No single deployment runbook or incident playbook in one location. | Add `docs/ops/runbooks/deploy.md` with rollback and incident timelines. |
| Env/schema governance | 2/5 | `src/tracertm/database/connection.py` and `crates/tracera-core/src/config.rs` have defaults in code, while `docs/tooling` mentions multiple command surfaces. | Config schema spread across files and docs. | Centralize config schema in one generated reference used by CI/docs. |

Per-area roll-up: avg `2.25/5`, subtotal `42?` with 14 pillars = `31/70 = 44.3%`.

## L — Governance / Traceability

| PILLAR | score/5 | evidence (file:line or absence) | gap | remediation |
|---|---|---|---|---|
| FR/NFR baseline traceability | 3/5 | `docs/traceability.md:1`-`10` and `src/tracertm/api/routers/traceability.py:103`-`116` map request->response. | Top-level matrix only shows a few representative feature rows. | Expand matrix with all active FR/NFR and current status. |
| Spec-first governance checks | 3/5 | `src/tracertm/governance.py:49`-`77` and `96`-`110` implement gate with explicit codes. | Gate result is local report only; no centralized audit record. | Persist gate outputs in evidence contract with immutable references. |
| Evidence contract schema | 3/5 | `docs/evidence-contract.md:13`-`103` defines canonical fields and status transitions. | Contract is documentation-first without implementation validator in app path. | Add schema validator + migration check for every report write. |
| Orphan/spec mismatch detection | 3/5 | `src/tracertm/governance.py:65`-`69` marks orphan traces; tests currently not present for this path in same area read. | Lacks property-based tests for mismatch and duplicate paths. | Add unit tests for duplicate/orphan/spec-mismatch edge cases. |
| Traceability of tests to requirements | 2/5 | `docs/traceability.md:5`-`10` includes requirement/test row linking, but no global enforcement. | No static check linking each FR to tests and evidence artifacts. | Implement ADR-anchored linter requiring FR references in spec/tests. |
| No-untraced capability policy | 1/5 | No repository-wide enforcement found in reviewed audit sources. | FR traceability can drift per new module without gate enforcement. | Add CI gate that rejects features without traceability row or evidence link. |
| ProgressionGate integration | 2/5 | `.github/workflows/governance-gates.yml` calls `scripts/qa-gates/*.sh` only (minimal). | Governance is a thin pre-merge check, not full progression gate. | Expand scripts to include requirement/test/evidence presence checks. |
| ADR governance coverage | 2/5 | `docs/ADR_MODEL_DECOUPLE_STRATEGY.md:24` and `56`-`57` show draft ADR state. | ADR list exists but no strict lifecycle status transitions in code reviews. | Add ADR lifecycle dashboard and status enforcement in CI labels. |
| Traceability governance docs | 1/5 | `CONTRIBUTING.md:58`-`63` references missing `docs/governance/background_agent_policy.md`; `docs/governance` folder absent. | Missing canonical governance documentation root. | Create governance folder and canonical policy artifacts (change control, incident model). |
| Governance actionability | 2/5 | `src/tracertm/governance.py:79`-`80` and `109`-`116` provide violation codes/messages. | Violation remediation tasks not linked to owner/priority/slack channel. | Add ownership fields and auto-routing of violations to issue templates. |
| Coverage gap reporting | 3/5 | `tests/unit/ports/test_graph_contract.py` validates contract behavior and examples. | No full project-level governance gap report generation in repo root. | Generate gap report during CI with failing threshold for missing evidence items. |
| Auditability of decisions | 2/5 | Evidence contracts define status and gap reasons, but no append-only decision log in code. | Decision provenance currently advisory only. | Add immutable audit log table + verifier for signed decision entries. |
| Traceability for migrations | 2/5 | `alembic/versions/063...` and feature list in `_tracera_feature_inventory` show migration lineage. | No mapping from FR IDs to migration IDs. | Add migration-to-requirement registry in docs and checks that migrations are justified. |

Per-area roll-up: avg `2.17/5`, subtotal `26/60 = 43.3%`.

## Ranked backlog (worst-first across G-L)

1. **K-Ops/Deploy** (`44.3%`) — implement real deployment + rollback mechanics before placeholder examples; add artifactized release flow and health-safe rollback gating.
2. **I-Data & Persistence** (`40.0%`) and **J-Docs/DX** (`40.0%`) — close backup/restore gaps first; then raise doc completeness for SSOT and governance policy.
3. **L-Governance/Traceability** (`43.3%`) — missing `docs/governance` policy and weak enforcement of FR→traceability linkage.
4. **H-Performance** (`36.7%`) — add resource/backpressure controls and profiling, plus documented load ceilings.
5. **G-Observability** (`53.3%`) — strengthen metrics/alerting and audit event capture; traces and request correlation already partially present.

