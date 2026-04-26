# Archived Repo Triage — AtomsBot + chatta

**Date:** 2026-04-26
**Trigger:** Round-6 push agent flagged push 403 on KooshaPari/AtomsBot, KooshaPari/chatta — both archived on GitHub.
**Memory cross-ref:** `reference_archived_repos_locked.md` (16 inert PRs across worktree-manager/Settly/KodeVibeGo/phenoXddLib already known archived; AtomsBot + chatta now extend that list).

## GitHub State

| Repo | archived | pushed_at | updated_at | default_branch |
|------|----------|-----------|------------|----------------|
| AtomsBot | true | 2026-03-05 | 2026-04-06 | main |
| chatta | true | 2026-03-27 | 2026-04-06 | main |

Both `archived: true`. Last push pre-dates the LEGACY hygiene round-32 wave; canonical local clones accumulated commits while remote was read-only.

## Local Commits Orphaned

### AtomsBot — 11 commits ahead of origin/main (+ uncommitted M to SPEC.md, docs/README.md, docs/worklogs/README.md, untracked ADR.md)

Provenance: pure governance / docs / CI hygiene.
- `a71649d` docs(readme): standard badge header (round-32)
- `7cf1968` docs(readme): status badge (round-20)
- `1b31b41` docs(license): MIT license + README section
- `82a61f1` docs(agents): AGENTS.md thin pointer
- `4d06afa` docs(changelog): retroactive CHANGELOG via git-cliff
- `5f6fa0e` docs(fr): scaffold FUNCTIONAL_REQUIREMENTS.md (0 stubs)
- `b402176` chore(ci): adopt phenotype-tooling workflows
- `dff0fd5` chore(governance): standard CLAUDE.md + AGENTS.md
- `53bdc07` chore: AgilePlus scaffolding
- `6fa0b9d` ci(legacy-enforcement): WARN-mode gate
- `9c9777c` docs: README/SPEC/PLAN

**No code fixes. No bug fixes. No security fixes.**

### chatta — 17 commits ahead of origin/main (+ uncommitted M to SPEC.md, docs/worklogs/README.md, frontend/package.json, package.json)

Provenance: governance / docs / CI hygiene + one real refactor.
- `d974fb8` docs(readme): standard badge header (round-32)
- `2b37044` chore(license): MIT LICENSE + README
- `1489868` docs(readme): status badge (round-20)
- `914c9dc` ci: real lint/test/security/build workflows
- `0630351` **refactor(backend): split main.go into modular packages** ← only non-doc commit
- `8d77b8d` docs(readme): hygiene round-9
- `9e05bc5` docs(agents): AGENTS.md thin pointer
- `6d5a996` docs(changelog): retroactive CHANGELOG via git-cliff
- `b3d5530` docs(worklog): bootstrap
- `9a04827` chore(ci): adopt phenotype-tooling workflows
- `1b1c52d` test(ts): vitest runner
- `51f64aa` test(smoke): minimal smoke test
- `7138446` chore(governance): standard CLAUDE.md + AGENTS.md
- `7bf2381` docs(fr): FUNCTIONAL_REQUIREMENTS.md (2 FR stubs)
- `b57fea8` chore: AgilePlus scaffolding
- `28e2e73` ci(legacy-enforcement): WARN-mode gate
- `ba099b3` docs: README/SPEC/PLAN

**No critical bug fixes. The Go refactor (`0630351`) is structural cleanup of a dormant project — not urgent.**

## Verdicts

| Repo | Verdict | Rationale | Urgent? |
|------|---------|-----------|---------|
| AtomsBot | **Archive correct — leave orphaned** | All 11 ahead-commits are batch-applied governance/hygiene from cross-org sweeps. Project is dead per archive. No value in unarchiving for docs. | NO |
| chatta | **Archive correct — leave orphaned** | 16 of 17 commits are governance/hygiene. The Go refactor (`0630351`) is non-urgent restructure of a dormant chat app. No bug fix, no security fix. | NO |

**Recommendation:** Do NOT request unarchive. Local commits remain preserved in `.git/` reflog of each canonical clone if ever needed (cherry-pickable). Add both to the global "archived — skip in cleanup" cohort alongside worktree-manager, Settly, KodeVibeGo, phenoXddLib.

## Action Items

- [x] Document triage (this file)
- [ ] Update `reference_archived_repos_locked.md` memory: extend list to include AtomsBot + chatta (deferred — follow-up memory edit).
- [ ] Future agents: skip `git push` attempts on these repos. Round-N hygiene sweeps must pre-filter `gh api repos/<r> --jq .archived`.
- [ ] Optionally annotate each repo's local `AGENTS.md` with "GitHub archived 2026 — push attempts will 403; do not author new work."

## Cross-Reference

- Memory: `reference_archived_repos_locked.md` — pattern: archived repos have inert PRs; skip in cleanup audits.
- Memory: `feedback_repo_identity_verification.md` — verified: local clones match KooshaPari/AtomsBot + KooshaPari/chatta remotes (origin URL matches GH archived repo).
