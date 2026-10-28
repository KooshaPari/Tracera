# Tracera gap-inventory recovery handoff (2026-10-19)

## Purpose

This session **recovered** the context of the Codex session titled
"Inventory Tracera gaps" (`01a13212-4750-73a0-90df-643ddf9a9162`, original
2026-10-12, resumed 2026-10-17), reconciled it against live repository and PR
state, and continued the highest-priority open work (D-04 read-only preflight).

It is a **handoff**, not a status report. A reader who has none of the prior
session context should be able to resume from this document alone.

## 1. Recovered context

### 1.1 Source artifacts

| Artifact                              | Path                                                                                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Original Codex rollout (JSONL)        | `~/.codex/sessions/2026/10/12/rollout-2026-10-12T14-43-41-01a13212-4750-73a0-90df-643ddf9a9162.jsonl`                                      |
| Resumed Codex rollout (JSONL)         | `~/.codex/sessions/2026/10/17/rollout-2026-10-17T23-33-31-01a13212-4750-73a0-90df-643ddf9a9162_01a14db7-2875-7363-9632-7eb7f23a59ce.jsonl` |
| Digest extractor                      | `~/.jcode/scratch/tracera-datamine/extract_codex_digest.py`                                                                                |
| Original-session digest (7,460 lines) | `~/.jcode/scratch/tracera-datamine/original-10-12.txt`                                                                                     |
| Resumed-session digest (422 lines)    | `~/.jcode/scratch/tracera-datamine/resumed-10-17.txt`                                                                                      |

The digests are the authoritative recoverable form of the prior session. If a
question arises about a prior decision, grep the digests rather than the raw
JSONL.

### 1.2 Principal work products (recovered)

| PR    | Branch                                   | Content                                                                         | State at recovery start                        |
| ----- | ---------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------- |
| #1132 | `audit/instinct-live-evidence-20261014`  | Gap inventory (`docs/audit/TRACERA-GAP-INVENTORY.csv`, `TRACERA-GAP-ISSUES.md`) | OPEN, MERGEABLE, CI red                        |
| #1158 | `docs/instinct-state-forward-20261017`   | State/Forward Docket, unified Tracera intent, D-04 preflight material           | OPEN, MERGEABLE, CI red                        |
| #1173 | `fix/d04-readonly-preflight-20261018`    | D-04 CLI read-only preflight / preservation fix                                 | OPEN, **CONFLICTING**, 197 commits behind main |
| #1150 | `docs/intent-usability-forward-20261016` | Intent/usability documentation                                                  | OPEN, CI red                                   |

### 1.2a Inventory count reconciliation (corrected)

Three distinct inventory states exist. The "75 gaps" figure circulating in prior
summaries refers to the **earliest** branch only.

| Branch                                                        | CSV rows | GAP rows | VIEW rows | GAP range        |
| ------------------------------------------------------------- | -------: | -------: | --------: | ---------------- |
| `origin/audit/instinct-gap-inventory-20261012` (earliest)     |       75 |       75 |         0 | GAP-001..GAP-075 |
| `origin/audit/instinct-live-evidence-20261014` (**PR #1132**) |       73 |   **29** |        44 | GAP-001..GAP-029 |
| `origin/docs/instinct-state-forward-20261017` (**PR #1158**)  |       67 |   **23** |        44 | GAP-001..GAP-023 |

So the later inventory **split** the flat 75 into two families: 29 API/behaviour
`GAP-*` rows and 44 `VIEW-*` rows (view-to-artifact parity). 29 + 44 = 73.

The recovered session digest independently attests the "29 gaps" figure
(`original-10-12.txt:4965, 4978, 4896`); see §1.2b.

The `docs/audit/` artifacts live on those branches, **not** on the local `main`
checkout. `docs/audit/` is absent from `origin/main`.

### 1.2b Recovered operator task (verbatim)

> "inventory EVERY gap in Tracera (https://tracera.pheno.studio, private behind
> Cloudflare Access; repo checkout on the Windows desk at `C:\Users\koosh\tracera`,
> reachable via `~/ts/ssh.sh koosh@100.96.135.160`). Read-only audit plus docs.
> No force-push, no secrets in output, no merges."
> — `original-10-12.txt:181`

Required outputs (`original-10-12.txt:184`):

- CSV `docs/audit/TRACERA-GAP-INVENTORY.csv` with columns
  `id, area, view_or_route, expected, actual, severity, evidence, suggested_fix`
- Markdown `docs/audit/TRACERA-GAP-ISSUES.md`, one issue per gap titled `[Instinct] …`
- Branch + PR titled `[Instinct] Tracera gap inventory`
- A 5-line state report when done

Gap #1 as the operator stated it (`original-10-12.txt:182`):
`GET /api/v1/projects/{id}/specifications/summary` returns
`{"items":[], "data":[], "results":[], "total":0, "count":0, "stub":true}` while
the Specifications Hub UI (`SpecificationDashboard.tsx`, hook `summary-hooks.ts`)
expects `{adrs:{total,accepted,averageCompliance}, contracts:{total,active,verified},
features:{total,scenarios,passRate}, healthScore, healthDetails}`. Item data
(26 ADR items etc.) exists; the route is a stub. This is `GAP-001` in the CSV.

### 1.3 Operator constraints carried forward

These remain binding for any continuation of this work:

- **Read-only investigation** for audit/scouting phases. Do not mutate during
  investigation.
- **No force-push.** Branches are advanced by merge, never rewritten.
- **No merges.** PRs are opened and left open for operator review.
- **No secrets in output.** Error messages must not echo configuration values.
- **Preserve unrelated and untracked work.** The `Tracera` main checkout holds
  31 uncommitted paths (including untracked `docs/sessions/2026-10-12-cockpit-refresh/`,
  `docs/sessions/20261015-e2e-optimality/`, `.audit/`, and
  `crates/tracera-server/src/ingest.monolith.rs`). Leave it untouched.
- **Tracera identity:** "Both, with an explicitly unified scope."
- **Evidence discipline:** prefer `UNKNOWN` over an unsupported percentage or
  an unverified claim. Do not claim Windows/Desk validation that was not run.
- **Do NOT run `tracera --root` against the real Desk checkout**
  (`C:\Users\koosh\Tracera`) without the operator's explicit OK. That path
  already has a real `.env.local`; `--root` can create `.env` files and
  symlinks. See §1.3a.

### 1.3a Desk / Windows constraint (recovered, safety-relevant)

The Desk checkout at `C:\Users\koosh\Tracera` has `docker-compose.local.yml`,
`.env.local` **and** `.env.example` — a real, live configuration. The recovered
session recorded these findings:

- Forward path for D-04 is `tracera --root C:\Users\koosh\Tracera status` then
  `up`, but the operator's caveat stands: `C:\Users\koosh\Tracera` already has a
  `.env.local`, so `--root` must **not** be run without explicit approval
  (clobbering real config risk). — `resumed-10-17.txt:145`,
  `original-10-12.txt:1311-1319`
- The Docker-desktop WSL distro is **Stopped**; FedoraLinux-44 WSL is up with
  podman on `:7777`. So `tracera` selecting backend `docker` may not have a
  usable backend. — `resumed-10-17.txt:145`
- The Desk SSH probe **timed out** before returning metadata, so installed-CLI
  identity and Docker/Podman/WSL state remain **UNKNOWN**. Nothing on the Desk
  was touched. — `resumed-10-17.txt:378`
- Desk resources: "one RTX 3090 Ti, mostly occupied by vLLM, and 38 GB free on
  `C:`". Installed CLI and a working stack are separate outcomes, and the
  manually running SQLite API process is a third distinct state. —
  `original-10-12.txt:7438-7451`
- Other Desk worktrees present: `Tracera-w4-test`, `tracera-guard`,
  `tracera-legacy`, `Tracera-w9-unresolved-worker`,
  `tracera-instinct-gap-audit/-inventory`. `docker-compose.local.yml` also
  exists in several `C:\Users\koosh\agents\sandbox\pheno\wt-*` dirs. —
  `resumed-10-17.txt:145`

## 2. What this session changed

### 2.1 PR #1150 — format gate cleared

The `Lint & Format` CI job runs `prettier --check` over changed
md/yml/yaml/json/jsonc/mdx files. Nine audit documents, two operations docs and
`frontend/.oxlintrc.json` on this branch were not prettier-clean.

- Worktree: `repos/.wtree/tracera-pr1150-fix`
- Branch: `fix/pr1150-prettier-20261019`
- Reformatted with prettier **3.6.2** (the version CI installs).
- Commit `d01d23583d8fc34ff98765297eca81f616c837fd`, pushed to
  `origin/docs/intent-usability-forward-20261016`.
- **Result: `Lint & Format` flipped `fail` → `pass`** (run 39325777814).

### 2.2 PR #1173 — conflict resolved, branch merged forward

`fix/d04-readonly-preflight-20261018` was 197 commits behind `main` and
`CONFLICTING`. Force-push is forbidden, so the branch was advanced by **merge**.

- Worktree: `repos/.wtree/tracera-pr1173-rebase`
- Merge commit `c7f5b12698` (`Merge origin/main into fix/d04-readonly-preflight-20261018`).
- Only **one** file conflicted: `Cargo.lock`. Resolution kept the branch's new
  `dotenvy` dependency and main's newer `rand 0.10.3` pin. Verified with
  `cargo metadata --no-deps` (clean).
- **Result: `mergeable` flipped `CONFLICTING` → `MERGEABLE`.**

Post-merge verification:

| Gate  | Command                                | Result                  |
| ----- | -------------------------------------- | ----------------------- |
| Build | `cargo check -p tracera-cli --offline` | clean, 0 errors         |
| Tests | `cargo test -p tracera-cli --offline`  | **13 passed, 0 failed** |

### 2.3 Root cause of the PR #1150 frontend test failure

Not a formatting problem — a **contract drift** problem, and a real one.

PR #1150 un-skipped a set of frontend suites that `main` had deliberately
quarantined with `describe.skip(...)` and the marker:

```
// TODO(#1137 mock drift): quarantined pre-existing failure on main - impl moved from
// safeApiCall to requireAvailable(get(...)) in #1137 and these mocks still target the old
// contract. Repair tracked as follow-up to PR #1172.
```

PR #1137 ("Return honest errors for unavailable Tracera routes") changed the API
wrappers from `safeApiCall` to `requireAvailable`:

```ts
// frontend/apps/web/src/api/events.ts
import { requireAvailable, invalidResponse } from "./availability";
const data = await requireAvailable(
  get("/api/v1/events", { params: { query: params } }),
);
```

The tests still mocked the **old** contract, so un-skipping them re-exposed the
drift.

The important consequence: several of these tests assert the **old, now-wrong**
behaviour. A test named _"should return empty array on error"_ expects
`fetchEvents` to swallow an error and return `[]` — but #1137's entire purpose
was that unavailable routes return **typed errors** instead of empty-or-healthy
success. Repairing these tests therefore means **updating the assertion to the
honest-error contract**, not re-mocking the old one. Weakening or blanket-skipping
would defeat #1137.

### 2.4 PR #1132 and PR #1158 — format gate

Both fail `Lint & Format` for the same reason as #1150 (changed md/yml/yaml/json
not prettier-clean). Both are additionally stale relative to `main`, which is the
likely cause of their `rust-coverage` failures — the #1132 stub-probe count
failure was already fixed on `main` by **#1167** (`cbcf0b0f`).

Other failures on those PRs, with cause:

| Check                     | PR #1132 | PR #1158 | Cause                                                            |
| ------------------------- | -------- | -------- | ---------------------------------------------------------------- |
| Vercel                    | fail     | —        | **External**: 24-hour build-rate limit                           |
| `guard`                   | —        | fail     | **External**: runner shutdown / cancellation, not a code failure |
| GitGuardian               | fail     | —        | Needs triage                                                     |
| SonarCloud                | —        | fail     | Needs triage                                                     |
| Python Lint / `ci / lint` | —        | fail     | Needs triage                                                     |
| `deploy`                  | fail     | fail     | Needs triage                                                     |

### 2.5 One conflict worth knowing about: `scripts/w9_inventory.py`

Refreshing against `main` conflicted here, because the same Ruff B023 / mypy
`misc` problem was fixed twice, differently:

- this session: `_placeholder(match, counter)` driven by `functools.partial`
- `main`: `_make_param_replacer(counter)` returning a typed closure

Both work. I took **`main`'s** version rather than keeping mine, because it is
already merged and keeping both would leave two implementations of the same
fix in different branches.

Verified equivalent rather than assumed: both produce identical output —
254 lines, sha256 prefix `f2a98c13593ce819`, deterministic across runs — and
`main`'s version passes `ruff check`, `ruff format --check` and `mypy` clean.

## 3. Current state

### 3.1 Evidence tree

Cells use `PASS / FAIL / NOT_RUN / UNKNOWN / BLOCKED / NOT_APPLICABLE / ?`.
A cell with no citation is `UNKNOWN`, never a guess.

```
PR #1150 format gate
  Implementation: PASS | prettier 3.6.2 --write over changed md/yml/yaml/json set
  Usability:       PASS | Lint & Format check run 39325777814 = pass
  Validation:      FAIL | frontend suites un-skipped by this PR assert the pre-#1137 contract
  Assurance:       ?    | repair in flight; re-check pending

PR #1173 D-04 preflight
  Implementation: PASS | cargo check -p tracera-cli --offline = clean
  Validation:      PASS | cargo test -p tracera-cli --offline = 13/13
  Merge state:     PASS | mergeable CONFLICTING -> MERGEABLE, merge commit c7f5b12698
  Compose parity:  FAIL | colon separators + some double-quoted escapes rejected
  Desk readiness:  UNKNOWN | SSH 100.96.135.160:22 timed out; no Desk binary run
  Windows path:    NOT_RUN | create_new branch statically reviewed only

PR #1132 / #1158
  Implementation: FAIL | changed files not prettier-clean
  Validation:      UNKNOWN | stale vs main; rust-coverage cause not yet confirmed
```

### 3.2 D-04 contract (must not be weakened)

1. **Read-only preflight** — never mutate existing configuration.
2. **Exclusive creation only for absent configuration** — create-if-missing,
   never clobber.
3. **Fail-closed on invalid existing configuration**, without exposing values.
4. **Preserve** existing files, directories and symlinks exactly (including
   dangling symlinks).
5. **Fail on bundle-link conflicts.**
6. Invalid or existing configuration must not create parent directories as a
   side effect.

Canonical detail: `docs/sessions/20261018-d04-preflight/STATUS.md`,
`STATUS.json`, `REVIEW.md` on branch `fix/d04-readonly-preflight-20261018`.
`STATUS.json` is the source of truth; `STATUS.md` is rendered from it by
`render_status.py`.

### 3.3 Known D-04 gaps

| Gap                                                   | Status                          |
| ----------------------------------------------------- | ------------------------------- |
| Compose-valid `KEY: value` colon assignments rejected | open, being worked              |
| Quoted tab / carriage-return escape handling          | open, being worked              |
| Windows exclusive-copy path never exercised           | `NOT_RUN` — no Windows runtime  |
| Locked-workspace validation                           | pending                         |
| Desk installed-binary identity unknown                | `UNKNOWN` — SSH probe timed out |
| Real Docker/WSL readiness unknown                     | `UNKNOWN` — no Desk execution   |

**Do not** claim Windows or Desk validation. It has not been run.

## 4. Work in flight at handoff time

| Agent                        | Scope                                  | Worktree                                                 |
| ---------------------------- | -------------------------------------- | -------------------------------------------------------- |
| frontend test-drift repair   | PR #1150 suites un-skipped by the PR   | `.wtree/tracera-pr1150-fix`                              |
| D-04 Compose parity          | `crates/tracera-cli/src/env_config.rs` | `.wtree/tracera-pr1173-rebase`                           |
| #1132/#1158 prettier + merge | format gate and stale-branch refresh   | `.wtree/tracera-pr1132-fix`, `.wtree/tracera-pr1158-fix` |
| Codex session mining         | digest → report                        | `~/.jcode/scratch/tracera-datamine/`                     |

## 5. Next steps

1. Land the frontend test-drift repair on PR #1150 and re-check CI. Assert the
   **honest-error** contract; do not re-mock the old one.
2. Land the D-04 Compose parity fix (colon form, quoted tab/CR) on PR #1173,
   keeping the fail-closed and no-secret-leakage properties intact. Update
   `STATUS.json` and re-render `STATUS.md`.
3. Apply the prettier fix to PR #1132 and PR #1158, and merge `origin/main`
   into each so the #1167 stub-probe fix arrives. Re-check CI.
4. Re-check PR #1173 CI end-to-end. The remaining blockers (`deploy`, Vercel
   rate limit, `guard`) are largely external.
5. Separately reassess the Windows Desk path. It is **not** covered by the
   current CI and needs a real Windows host.
6. Triage GitGuardian and SonarCloud failures once the format gate is green.

## 6. Rules for the next session

- Do not re-derive the prior session. Read the digests in §1.1.
- Do not touch the `Tracera` main checkout's uncommitted work.
- Do not force-push. Merge forward.
- Do not merge any PR. Leave it open for the operator.
- Do not mark a validation cell `PASS` without an observed result and a citation.
- Keep every file under 500 lines (target 350).

## 7. Findings with their own write-up

Three topics outgrew this file and were moved to artifacts rather than
compressed until they stopped being useful.

| Topic                                                                                                                                                 | File                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| A formatting pass silently broke 30+ evidence attestations, the per-tool guards that now prevent it, and the external blockers that remain            | `artifacts/INCIDENT-EVIDENCE-INTEGRITY.md` |
| The verified merge order for the four PRs, and the one decidable conflict between #1132 and #1158                                                     | `artifacts/MERGE-RECIPE.md`                |
| Why `lint-rust`, `osv` and `test-py (3.13)` fail without implicating the D-04 work: RUSTSEC advisories, npm advisories, and a dead self-hosted runner | `artifacts/CI-BASELINE-FAILURES.md`        |
