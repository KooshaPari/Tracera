# Tracera Q0 runtime qualification

Observed 2026-10-16 PDT (runtime receipts 2026-10-17 03:25 UTC).

**Gate: isolated Rust/SQLite operation READY; product CVP NOT READY.** A current-main binary built, accepted genuine HTTP requests, persisted a supplied issue, and returned the same story after process restart. This does not qualify the hosted deployment, frontend, automatic discrepancy discovery, or unfamiliar-user pilot.

## Ownership and source manifest

| Component                 | Exact receipt                                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| Source                    | `ae68aea7febd772282606bf1e142d507316cfea0`, current main when qualified; journey read PR #1149          |
| Local preserved source    | `/tmp/tracera-q0-runtime-20261016` before switching its fresh clone to the documentation branch         |
| Windows source            | `C:\Users\koosh\agents\tracera-q0-ae68aea7-src` extracted from exact source archive                     |
| Archive SHA256            | `cd47f92f359e5d34ec52cd43003ec8e4af532002598444d534a0bc4ecd2c932e`; matched independently on both hosts |
| Candidate binary          | `target/debug/tracera-server.exe` under that Windows source root                                        |
| Binary SHA256             | `cd69e6d1f72ac2c1e19cbd319b5661f577b2cfb6af81229786ec3cc202018742`                                      |
| Runtime/store             | New sibling `tracera-q0-ae68aea7-runtime`, dedicated `q0.db` SQLite file                                |
| Listener                  | `127.0.0.1:18173`; no public bind or Access policy change                                               |
| Owned processes           | Initial PID 315612; restart PID 316428; both stopped                                                    |
| Existing Windows checkout | Observed HEAD `3e23c76ec0f621a3dbe696ed22bd05048a65a878`; untouched                                     |
| Existing ports            | 8080 and 8091 had no listeners; no restart or takeover attempted                                        |

Placement was **remote compute with remote output**: Windows reported 68,612,255,744 bytes RAM (64 GiB), cargo 1.98.1. This avoids a heavy build on the 16 GiB Mac. An initially slow full clone eventually completed in separate `tracera-q0-20261016`; archive transfer established the exact build input independently. No shared checkout was reset or overwritten.

## Reproducible launch and build

Repository README advertises `cargo run -p tracera-server`. Source `crates/tracera-server/src/main.rs:184-230` accepts PostgreSQL or SQLite and runs migrations. `db.rs` applies SQLite foreign keys, WAL for file stores, and a bounded acquisition timeout.

The successful attributable build was:

```text
cargo build --locked -p tracera-server --target-dir <candidate-source>/target
exit 0; dev profile; 2m 36s
```

An earlier build also passed (2m 51s), but inherited the workstation's shared Cargo target directory. It was not used for runtime provenance. The explicit-target rebuild produced the hashed candidate binary above. Logs remain in sibling `tracera-q0-ae68aea7-isolated-build.log` and `tracera-q0-ae68aea7-build.log`.

The candidate process used only:

```text
DATABASE_URL=sqlite://<candidate-runtime>/q0.db?mode=rwc
TRACERA_BIND_ADDR=127.0.0.1:18173
```

Live GitHub/Jira source variables and optional service/auth configuration were removed from its process environment before launch. No credential values were printed. The server's health version is package `0.2.0`, not a commit SHA; the source/archive/binary manifest supplies that missing provenance.

Only the owned candidate processes were stopped. A subsequent independent process/listener query returned no owned PIDs and no listeners at 18173, 8080, or 8091. Candidate database and logs were preserved; no shared service was changed.

## HTTP receipts and independent controls

| Probe                                           | Observed result                                                | Meaning                                                                             |
| ----------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| GET `/readyz`                                   | 200, `status=ready`, `backend=sqlite`, `version=0.2.0`         | Store readiness succeeds, beyond liveness                                           |
| GET `/api/v1/items` in fresh store              | 200, `items=[]`, `total=0`, `store=items`, no stub marker      | Genuine empty-store response                                                        |
| GET `/api/v1/items?limit=-1`                    | 400                                                            | Invalid-query negative control                                                      |
| GET `/api/v1/items/q0-never-created`            | 404                                                            | Missing-record negative control                                                     |
| POST `/ingest/github`, `{}` without live source | 422                                                            | Actual handler contradicts checked-in YAML's 200 oracle                             |
| POST `/ingest/github`, one supplied issue       | 200, processed 1, created 1, links 0, errors empty             | Real fixture persistence through mounted handler                                    |
| GET `/api/v1/stories`                           | 200, one story                                                 | Persisted fixture visible independently of ingestion response                       |
| Stop, restart, GET `/readyz`                    | 200 ready, SQLite                                              | New process opens same dedicated store                                              |
| GET `/api/v1/stories` after restart             | Same ID/title/body/status and exact created/updated timestamps | Durable issue/story witness                                                         |
| GET `/api/v1/projects`                          | 200, count 0, items empty                                      | This story fixture is not demonstrated project identity; do not infer Item behavior |

The supplied issue was number `8675309`, title `Q0 isolated persistence witness`, body `candidate fixture only`, state `open`; resulting ID `story-8675309`. Creation/update timestamp remained `2026-10-17T03:25:12.488662900Z` before and after restart.

Mutating requests occurred only against the isolated candidate. CSRF token was obtained from its own `/api/v1/csrf-token`; the request Origin matched the source's allowed `http://127.0.0.1:18000`. This hardcoded origin is a deployment constraint, not evidence that arbitrary browser origins work.

## Product acceptance and forward path

See [Q0 acceptance contract](TRACERA-Q0-ACCEPTANCE-SLICE.md). Its proposed empty-input execution gate is now witnessed here: the live isolated process returned 422 against the checked-in 200 contract. The acceptance document's source-only wording records its independent author's boundary; this report adds execution evidence.

This is a genuine **manually established contract discrepancy**. It is not proof that Tracera automatically imported source anchors, created canonical product observations, detected the mismatch, explained its evidence, reconciled a source change, or persisted that product-semantic pipeline. Existing story durability must not be substituted for product-model durability.

Next source candidate is the acceptance document's canonical product/observation identity and persistent detector wiring, with cross-product and cross-capability counterexamples. No source implementation is included here. Hosted Access, full frontend artifact journeys, PostgreSQL, authorization/isolation, user acceptance, install/update supervision, and broad historical baseline closure remain unqualified. No product coverage percentage is claimed.

The original audit boundary remains read-only product inspection plus documentation; this candidate used a new disposable test store and no production mutation. No screenshots, recordings, merges, force pushes, secret output, or history rewriting occurred.

## Validation ledger attestation

Commit `64bd0a856611a6d6b33c30bbd8cb383a25566f1e` published the source/archive/binary manifest and HTTP/restart receipts above. Its `tx-validated` line had leading whitespace, so this follow-up records a formal trailer correction without rewriting that commit. Validation was the successful explicit-target build, isolated HTTP probes, persistence/restart observation, owned-process cleanup check, and documentation diff check. No unit-test suite was run, and no additional runtime or test execution is claimed by this ledger correction. The 422 versus 200 discrepancy concerns a stale checked-in contract oracle; the handler's explicit no-source error is not established as a defect. An imported Story is not an Item, so the empty project projection from this fixture establishes no new project-discovery defect.
