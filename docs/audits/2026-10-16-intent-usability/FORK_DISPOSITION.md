# Repository and component disposition

This assessment treats `KooshaPari/Tracera` as the owned product repository. The inspected local origin and an additional remote named upstream both target the same owned project; a remote's name does not establish an independent upstream. No upstream publishing is part of this work.

| Object                                                           | Disposition                                          | Required proof                                                             |
| ---------------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| Main                                                             | Preserve owned product and accepted wider intent     | Exact source/artifact baseline with receipts                               |
| Canonical persistence branches1099/1126                          | Reconcile and reuse before new implementation        | Semantic delta inventory, tests and store migration/profile compatibility  |
| Spatial branches1104/1122                                        | Retain as proposed mature work                       | Independent read/write/geometry-truth acceptance, no implied 3D completion |
| Existing audit1132/docs1133                                      | Reuse as dated evidence and planning                 | Refresh only changed facts; no copying stale runtime findings as current   |
| SWEE versus canonical item/product graph                         | Define distinct authorities and adapters             | Same identity/scope/provenance cannot silently change meaning              |
| Redis                                                            | Optional acceleration                                | Measured need, invalidation/operational cost proof                         |
| Neo4j                                                            | Possible derived replica, not canonical store        | Outbox/backfill, lag and SQL parity before graph reads depend on it        |
| SCIP/LSP, native parsers/search, established requirement formats | Prefer adopt/wrap when fit                           | Functional/performance/security/maintenance comparison on actual profiles  |
| ALM/work engine                                                  | External execution state distinct from product model | Versioned handoff/result contract; no duplicate product authority          |

Owned release integration must bind commit, build profile, store schema, artifact digest, auth/deploy config and tested installation/update/restore. Existing release tags are historical receipts, not installed current identity. The versioning owner should reconcile product/server/package versions before releasing; this docs plan assigns no new version or release tag.

Fork-specific rebranding semver applies only where an actual upstream fork component is distributed; keep base version and custom suffix provenance. Do not infer a standalone fork delta from the main Tracera remote labels. Full dependency/custom subsystem disposition remains M1/M2/M7 work, not an unverified claim this audit covered every material source file.
