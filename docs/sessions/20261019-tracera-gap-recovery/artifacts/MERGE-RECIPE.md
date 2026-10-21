# Verified four-PR merge recipe

Split out of `00_SESSION_OVERVIEW.md` (formerly its section 9). The conflict and its resolution were established by simulation in a throwaway worktree, not by reading diffs.

All four PRs were merged into a throwaway worktree to find conflicts before
the operator hits them. Each PR merges cleanly into `main` on its own. In
combination there is exactly one real conflict, between #1132 and #1158.

The conflict is two files: `docs/audit/TRACERA-GAP-INVENTORY.csv` and
`docs/audit/TRACERA-GAP-ISSUES.md`. It is decidable rather than a judgement
call, because #1158's inventory is a strict subset of #1132's:

| Branch                                          | GAP rows | VIEW rows | GAP ids present  |
| ----------------------------------------------- | -------- | --------- | ---------------- |
| `audit/instinct-live-evidence-20261014` (#1132) | 29       | 44        | GAP-001..GAP-029 |
| `docs/instinct-state-forward-20261017` (#1158)  | 23       | 44        | GAP-001..GAP-023 |

Both files contain exactly `GAP-001..023` on both branches, and #1132 adds
`GAP-024..029`. Nothing is unique to #1158 in either file, in both the CSV
row ids and the `### [Instinct] GAP-nnn` headings.

Verified order, which leaves no conflict to resolve by hand beyond taking
#1132's side on those two files:

1. Merge #1158.
2. Merge #1132, resolving the two gap files with `git checkout --theirs --
docs/audit/TRACERA-GAP-INVENTORY.csv docs/audit/TRACERA-GAP-ISSUES.md`.
3. Merge #1150 and #1173; both apply cleanly.

A note on two workflow files. `.github/workflows/ci.yml` and `ci-agents.yml`
appear to "lose" the PR branches' blacksmith runner options in that merge.
They are not lost by the merge: `main` removed those options itself in
`6f94d38d8` ("ci: gate workflows to self-hosted desk runners", #1202), and
the branches predate that removal, so main's deletion correctly wins the
three-way merge.

Post-merge state of the combined tree, all observed:

| Check                                       | Result                      |
| ------------------------------------------- | --------------------------- |
| `ruff check .`                              | All checks passed           |
| `ruff format --check .`                     | 242 files already formatted |
| `python3 scripts/verify_evidence_hashes.py` | 109/109 verified, PASS      |
| prettier on files changed vs `main`         | clean                       |
| `crates/tracera-cli/src/*` vs #1173         | byte-identical              |

Shared config is deliberately byte-identical across branches so this stays
true: `.prettierignore` in #1132 and #1158, and `.sonarcloud.properties`
plus the `[tool.mypy]` block in #1158 and #1173.
