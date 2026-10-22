# Incident: a formatting pass broke evidence attestations

Split out of `00_SESSION_OVERVIEW.md` (formerly its sections 7 and 8). The guards recorded here are referenced from `scripts/verify_evidence_hashes.py`, and the detail is worth reading in full before anyone touches `docs/state`.

A formatting pass silently destroyed the attestations of three evidence
corpora. Commits that caused it, one per branch:

| Branch                                             | Commit                                                                                    | Effect                                                                                |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `docs/instinct-state-forward-20261017` (PR #1158)  | `958accfee` `style(docs): apply prettier formatting to instinct state-forward docket`     | 20/50 `SHA256SUMS` entries and 10/33 `EVIDENCE-SHA256.json` entries no longer matched |
| `audit/instinct-live-evidence-20261014` (PR #1132) | `1ad595896` `style(docs): apply prettier formatting to instinct live-evidence audit docs` | 3/7 `SHA256SUMS` entries no longer matched                                            |

Every manifest verified fully at the commit immediately before each prettier
pass (`420212dbb` and `3d02c5279` respectively), so the break was caused by
formatting, not by a bad observation. A whitespace-insensitive diff and a
JSON-semantic comparison showed the content was unchanged: the prettier pass
reflowed single-line JSON and padded markdown table separators.

The subtle part is `observation.json`. It embeds the sha256 of each evidence
file, and it was regenerated after the reflow, so it attested hashes of files
that were never observed. Restoring only the evidence files would have left
`observation.json` describing a state that never existed, so all
manifest-listed artifacts were restored together.

Repair: restore the captured bytes, then exclude the corpora from every tool
that rewrites or reinterprets them.

| Tool         | Guard                                                                                                                                               |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| prettier     | `.prettierignore` excludes `docs/state/**` and `docs/audit/readiness/**`; file is byte-identical in both PRs so they cannot conflict                |
| ruff         | `ruff.toml` `extend-exclude = ["docs/state"]` (`ruff.toml`, not `pyproject.toml`, is the resolved config; confirmed with `--show-settings`)         |
| mypy         | `pyproject.toml` `[tool.mypy] exclude` for `docs/state` and the separate py-sdk project                                                             |
| SonarCloud   | `.sonarcloud.properties` `sonar.exclusions`                                                                                                         |
| verification | `scripts/verify_evidence_hashes.py` checks every `SHA256SUMS`, `input-manifest.json` and `EVIDENCE-SHA256.json`; currently 109/109 entries verified |

Rule for the next session: never reformat a directory that carries a
`SHA256SUMS`, `EVIDENCE-SHA256.json`, or `input-manifest.json`. Run
`python3 scripts/verify_evidence_hashes.py` after any change near
`docs/state`.

## Remaining external blockers (not fixable from the repository)

- `deploy` fails on `main` as well, so it is a pre-existing baseline failure.
- `Vercel` fails with a deployment rate limit ("retry in 24 hours"); external.
- `Kilo Code Review` fails with `Review failed: Assistant request was rate
limited`. Same class as CodeRabbit's earlier "Review rate limited": a
  third-party review bot out of quota, not a finding about the code. Read the
  check-run summary before treating any red review bot as a code verdict.
- GitGuardian on PR #1132 reports one "Generic High Entropy Secret" in
  `docs/audit/TRACERA-GET-METHOD-BATCH.csv` at commit `e4b6ab3ee`. Inspection
  of that file shows the only high-entropy tokens are API route strings such
  as `/api/v1/...`. That reads as a false positive on a long path, but the
  finding lives in PR history, so clearing it needs either a history rewrite
  (prohibited) or a dashboard dismissal. Not resolved here.
