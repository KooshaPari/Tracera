# Push Conflict Resolutions — 2026-04-26

Three repos blocked the 9/12 push wave. This doc proposes resolutions for each. **Nothing has been executed.** User confirms direction, then runs the commands below (or `cp` the pre-staged files into place).

Pre-staged resolution files live under:
`repos/docs/org-audit-2026-04/proposals/push_conflict_2026_04_26/`

---

## 1. AgilePlus — README rebase conflict

### Diagnosis

Both sides intentionally rewrote `README.md`:

- **Local (`a59c681`)** — RED rewrite: replaced stale/fictional content with technical detail (stack versions, repo layout, dev commands, `Known limitations`).
- **Upstream (`6bc7a26` via PR #410)** — also a stale-content replacement but with cleaner quick-start framing, `docs/guide/` vs `docs/guides/` clarification, and a Contributing section.

They are NOT redundant — they emphasize different things. Local is denser and more accurate on internals; upstream is more onboarding-friendly. A simple "ours/theirs" pick discards real signal either way.

### Recommended fix — hand-merged README

A unified README is pre-staged at:

```
repos/docs/org-audit-2026-04/proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md
```

It keeps:
- Upstream's tagline + Quick Start (3-step flow) at the top
- Local's `Status:`, "What it does", `Stack`, `Known limitations` sections
- A unified Repository Layout block (covers both views)
- Upstream's `docs/guide/` vs `docs/guides/` callout
- Local's full Documentation table merged with upstream's Quick-start row
- Upstream's Governance + Contributing sections

### Commands

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
git fetch origin main
git rebase origin/main
# rebase will halt on README.md conflict
cp ../docs/org-audit-2026-04/proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md README.md
git add README.md
git rebase --continue
git push origin main
```

### Decision needed from user

- [ ] Accept the hand-merged README as proposed, OR
- [ ] Keep local verbatim (`git checkout --ours README.md`), OR
- [ ] Keep upstream verbatim (`git checkout --theirs README.md`).

---

## 2. BytePort — untracked files block pull --rebase

### Diagnosis

Six untracked roots block rebase:

| Path | What it is | Recommendation |
|------|-----------|----------------|
| `Cargo.toml` | 4-line workspace stub (`members = ["frontend/web/src-tauri"]`) | **commit** — needed for the existing tracked `frontend/web/src-tauri/Cargo.toml` to build as a workspace member. Real WIP. |
| `Cargo.lock` | 134 KB resolved lock for the workspace stub above | **commit** — RFC 3050: this repo has a binary crate (`src-tauri`), so lockfile commits are correct. |
| `go.mod` | `module github.com/KooshaPari/byteport`, go 1.22 | **commit** — module root for `backend/` Go code. |
| `tests/smoke_test.rs` | "Traces to: FR-ORG-AUDIT-2026-04-001" smoke test | **commit** — audit-wave artifact, has FR trace, real coverage. |
| `backend/byteport/tests/smoke_test.rs` | identical smoke test | **commit** — same provenance. |
| `docs/` | `FUNCTIONAL_REQUIREMENTS.md`, `adr/` (14 ADRs), `reference/`, `research/`, `worklogs/` | **commit** — substantial governance content, definitely not generated. |

None of these are throwaway artifacts. All are MODE 2 (pre-existing audit-wave WIP) or MODE 1 work. The push wave skipped them only because of the "no untracked" guardrail.

### Recommended fix

Commit all untracked, then rebase + push.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/BytePort

# Per dirty-tree commit discipline, split by provenance:

# MODE 1: build/scaffold roots (workspace + go module + lockfile)
git add Cargo.toml Cargo.lock go.mod
git commit -m "chore(scaffold): add workspace Cargo.toml/Cargo.lock and go.mod root"

# MODE 1: smoke tests (FR-traced)
git add tests/smoke_test.rs backend/byteport/tests/smoke_test.rs
git commit -m "test(smoke): add FR-ORG-AUDIT-2026-04-001 smoke harness"

# MODE 1: governance docs from audit wave
git add docs/
git commit -m "docs(governance): add FUNCTIONAL_REQUIREMENTS, 14 ADRs, reference/research/worklogs"

# Now rebase+push is unblocked
git pull --rebase origin main
git push origin main
```

### Decision needed from user

- [ ] Confirm all six paths should be committed (recommended), OR
- [ ] Specify any subset to gitignore/delete instead.

If the user wants to gitignore Rust/Go build outputs, that's a separate `.gitignore` PR — none of the listed paths are build outputs.

---

## 3. GDK — add/add conflict on `.github/workflows/quality-gate.yml`

### Diagnosis

| Side | Content | Style |
|------|---------|-------|
| **Local** (21 lines) | Inline build of `phenotype-tooling/quality-gate` binary, `--quick` invocation, `continue-on-error: true`, `\|\| true` everywhere | Ad-hoc, defensive, always-green |
| **Upstream** (11 lines, via PRs #21–#26 CI bootstrap) | Calls reusable `KooshaPari/phenotype-infrakit/.github/workflows/quality-gate.yml@main`, `secrets: inherit` | Standard org pattern, fails loud |

Upstream is the correct pattern — it matches the org-wide CI bootstrap landed in PRs #21–#26 across many repos. Local is a one-off local hack that pre-dated the reusable workflow.

The **local README badge** (added in `397c9f4`) likely points at this workflow file — the badge URL works regardless of file content as long as the path stays `.github/workflows/quality-gate.yml`. Both versions have that path, so the badge link continues to resolve.

### Recommended fix — take upstream

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/GDK
git fetch origin main
git rebase origin/main
# rebase halts on add/add conflict
git checkout --theirs .github/workflows/quality-gate.yml
git add .github/workflows/quality-gate.yml
git rebase --continue
# Verify badge in README still references the same workflow path
grep -n quality-gate README.md
git push origin main
```

Pre-staged file:
```
repos/docs/org-audit-2026-04/proposals/push_conflict_2026_04_26/GDK_quality-gate.yml
```

### Decision needed from user

- [ ] Accept upstream (recommended — matches org pattern), OR
- [ ] Keep local hack (only if the reusable workflow has a known regression).

---

## Summary Table

| Repo | Conflict | Recommendation | User decision |
|------|----------|---------------|---------------|
| AgilePlus | README rewrite collision | Hand-merge (file pre-staged) | accept merge / pick one verbatim |
| BytePort | 6 untracked roots block rebase | Commit all 6 in 3 provenance-split commits | confirm all, or specify excludes |
| GDK | add/add on quality-gate.yml | `--theirs` (upstream is org-standard) | accept upstream / keep local |

No execution performed. No org-audit doc pushed (Tracera origin). All three resolutions are mechanical once direction is confirmed.
