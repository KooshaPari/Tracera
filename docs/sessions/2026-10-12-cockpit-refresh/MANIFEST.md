# MANIFEST — canonical files vs superseded backups

Last verified: 2026-10-15T07:28Z (`08_SCOPE_CORRECTION.md` added and indexed here: PR #6 closed as misrouted; the /parent/ work belongs in job-cockpit per the operator, and that repo is a Python dashboard with no JS layer, so the SPA implementation cannot be moved as-is).

## Canonical (read these)

| File                        | Last amendment-propagation edit                                                                                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `00_SESSION_OVERVIEW.md`    | 2026-10-14 (title-scoped-only correction, directive #7)                                                                                                                                           |
| `01_OPERATOR_DIRECTIVES.md` | 2026-10-13 (verbatim 23:48Z amendment + table row 9)                                                                                                                                              |
| `02_CURRENT_STATE.md`       | 2026-10-14 (R11: tab-system hedge → preemptive conclusion)                                                                                                                                        |
| `03_PROPOSED_DESIGN.md`     | 2026-10-14 (Phase 1/2 checklists amended)                                                                                                                                                         |
| `04_PR_PIPELINE.md`         | 2026-10-13 (title convention + PR-body template)                                                                                                                                                  |
| `05_BLOCKERS.md`            | original                                                                                                                                                                                          |
| `06_DECISION_LOG.md`        | 2026-10-14 (D14 entry: 23:48Z amendment traceability)                                                                                                                                             |
| `07_TAKEOVER_RECORD.md`     | 2026-10-14 (new: takeover state of record; not a policy file)                                                                                                                                     |
| `08_SCOPE_CORRECTION.md`    | 2026-10-15 (new: operator closed PR #6 as misrouted to koosha-phenotype; job-cockpit vs koosha-phenotype architecture split; 5 review findings to carry forward; DO-NOT-COMMIT redaction warning) |

## Superseded `.bak-*` snapshots — DO NOT use as current

All `.bak-*` files are point-in-time backups created by the backup-before-edit
policy. They contain **pre-amendment policy text** (e.g., unconditional
"`[Instinct]` PR titles") and are retained only for diff history:

- `00_SESSION_OVERVIEW.md.bak-20261013T052900Z`
- `00_SESSION_OVERVIEW.md.bak-20261014T095700Z`
- `01_OPERATOR_DIRECTIVES.md.bak-20261013T231655Z`
- `03_PROPOSED_DESIGN.md.bak-20261014T091700Z`
- `03_PROPOSED_DESIGN.md.bak-20261014T095700Z`
- `04_PR_PIPELINE.md.bak-20261013T224829Z`
- `06_DECISION_LOG.md.bak-20261014T233300Z`
- `00_SESSION_OVERVIEW.md.bak-20261014T234200Z`
- `03_PROPOSED_DESIGN.md.bak-20261014T234700Z`
- `04_PR_PIPELINE.md.bak-20261014T234700Z`
- `02_CURRENT_STATE.md.bak-20261014T235800Z`

## Binding policy (as of 2026-10-12T23:48Z amendment, title-scoped ONLY)

- Heavy/architecture PRs: **plain titles**, no `[Instinct]` prefix.
- Light/legibility PRs: MAY use `[Instinct]` prefix.
- `Authored by Instinct` PR-body first line: **binding for ALL PRs**.
- Other 8 directives from 2026-10-12T22:33Z remain binding.

## Version-control status

Session dir is **untracked** in Tracera; Tracera `main` was 77 behind
`origin/main` with 25 operator-owned M-files at last check (2026-10-14).
Content is current on disk; commit/push pending operator action.

**Loss-prevention backup (2026-10-14T18:22 PDT):** all 8 then-canonical `.md`
files (00–06 + MANIFEST, `.bak-*` excluded) copied byte-verified to
`/Users/kooshapari/CodeProjects/docs/_archive/cockpit-refresh-backup-20261014/`.
That backup predates `07_TAKEOVER_RECORD.md` and is NOT kept in sync with it.

**New finding (2026-10-14):** four branches are named across **two different repos**, which
this manifest previously conflated. In **Tracera**'s origin: `feat/dimensional-layering`,
`feature/cockpit-appshell`, `agent/cockpit-refresh` were all absent. The Phase 1 branch
`feature/cockpit-parent-view` is not a Tracera branch at all — it belongs to **koosha-phenotype**
(`KooshaPari/KooshaPari`), and its absence was observed on _that_ repo's origin.

**Superseded (corrected 2026-10-15):** `feature/cockpit-parent-view` was recreated in
**koosha-phenotype** from an exact `origin/main` match and pushed at `e5f2a03`, then carried
forward with review fixes on `fix/parent-view-review-findings` (`12d51c882`) — see
`07_TAKEOVER_RECORD.md` and `08_SCOPE_CORRECTION.md`. That branch is on **remote** origin for
koosha-phenotype. Phase 1 is no longer blocked on branch availability. The other three were
either superseded by revision 3's single-branch decision (`feature/cockpit-appshell`,
`agent/cockpit-refresh`) or are unrelated operator work (`feat/dimensional-layering`, a
visual-novelty branch).
