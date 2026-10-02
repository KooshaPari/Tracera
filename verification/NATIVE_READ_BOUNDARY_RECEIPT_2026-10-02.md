# Native product persistence/read boundary receipt — 2026-10-02

## Exact evidence scope

- Repository: KooshaPari/Tracera; recovery PR #1086 remains draft.
- PR head under test: `fd61a416835aeb9a2ea6bfee23062aeece621d57`.
- The runner actually checked out the PR merge candidate:
  `03ec8cbd525cc0622391ed0db17f075c7945d8ec`.
- Its base was `ad4ce0c35ffa09537548ed2134f9ecaa75260323`.
- CI run: `36998559381`; native Rust Test job: `110811320961`.
- Command: `cargo test --all --workspace --verbose`.
- Raw evidence: https://github.com/KooshaPari/Tracera/actions/runs/36998559381/job/110811320961

This receipt records observed native execution, not merely authored tests or an
aggregate CI badge. It does not assert that a different/latest branch SHA is green.

## Results inspected

**18 database integration tests passed.** Their exercised behavior includes the
ProductPersistence port roundtrip, product-scoped identity and baseline membership,
cross-product rejection with no leaked rows, observation/reuse history,
file-backed SQLite reopen, bounded invalidation and its continuation, atomic
invalidation batches, exact replay, and certificate revocation preserving the
historical observation.

**11 product handler/router tests passed.** They exercise the mounted Axum router,
object-safe ProductApplicationService, real SQLite adapter and migrations. The
checks cover bearer enforcement, the product ID `health` not becoming a public
probe, foreign/missing baselines versus legitimate empty baselines, bounded-list
partiality, product/candidate scope on reuse, encoded invalidation references,
invalid inputs, and HTTP error/redaction behavior.

These results supersede the *not executed here* status of those specific SQLite
and HTTP witnesses in `PRODUCT_READ_BOUNDARY_REPAIR_2026-10-02.md` for this tested
merge candidate only. The earlier ten Python SQL tests remain a separate,
narrower evidence layer; they are not the source of the native result.

## WBS disposition

| Work | Current evidence meaning |
| --- | --- |
| T3 SQLite product persistence witnesses | Native exercised subset passed on the pinned merge candidate. |
| T4 persistence-backed invalidation witnesses | Native exercised subset passed, including rollback/replay/continuation. |
| T5 object-safe composition and mounted read routes | Native SQLite/HTTP witnesses passed on the pinned merge candidate. |
| T3/T4 Postgres behavioral parity | Not established by compiling the adapter. Native Postgres execution remains required. |
| T5 mutation routes and product-scoped authority | Not established by these read-route tests. |
| T6 browser product journeys | Not exercised by these API tests. |
| T7 historical build/LKG parity | Not exercised. |
| T8 graph scale and interactive performance | Not exercised. |

## Non-green boundaries

Rust formatting/lint and broader CI quality gates remain separate from the passing
Rust test job. No merge or product-stage promotion is authorized by this receipt.
A working read endpoint does not prove a complete usable Tracera product, and
historical reuse records are not a claim of present evidence applicability.
