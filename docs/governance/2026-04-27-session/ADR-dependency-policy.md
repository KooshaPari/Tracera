# ADR: Phenotype-Org Dependency-Update Policy
**Date:** 2026-04-27
**Status:** Proposed (refined from this session's mass lockfile-regen)

## Decision
Phenotype-org adopts a **lockfile-only** Dependabot remediation policy with surgical manifest-bumps as exception.

## Process
1. **Default response to Dependabot alert**: lockfile-regen via `lockfile_regen_v2.sh`. Manifests untouched.
2. **If lockfile-regen leaves residual**: open a *separate* PR using one of:
   - `cargo update --precise <crate>@<ver>` (Rust surgical)
   - `npm audit fix --force --package-lock-only` (npm aggressive — risk)
   - Manifest version bump (last resort, requires owner review)
3. **Critical advisories** (CVSS ≥ 9.0): treated as exception — direct manifest bump allowed without owner review, but owner must be notified within 24h.
4. **Lockfile-only PRs** auto-mergeable via `gh pr merge --squash --admin --delete-branch` after build passes locally.

## Forbidden patterns
- `npm install --package-lock-only` from-scratch on an existing repo without owner review (risks breaking peerDeps).
- Combining lockfile + manifest changes in one PR (mixes risk surfaces).
- Bypassing pre-commit hooks (`HOOKS_SKIP=1`) without documenting reason in commit body.

## Quality gates (per PR)
- [ ] Only lockfile changed (verify via `git diff --stat`)
- [ ] Build passes locally
- [ ] No semver-major direct-dep bumps
- [ ] Commit message: `chore(deps): regenerate lockfile for Dependabot advisories (N alerts)`

## Exception process
For manifest-required bumps:
1. Author PR with manifest + lockfile in same commit.
2. Title: `fix(deps): bump <crate> to <ver> (CVE-XXXX-YYYY)`.
3. Body: link to advisory, justify breaking-change risk, name reviewer.
4. Wait 24h for owner ack OR use `gh pr merge --admin` if CRIT (notify owner post-hoc).

## Tooling (committed in this session)
- `repos/docs/scripts/lockfile-regen/lockfile_regen_v2.sh` — canonical lockfile regen
- `repos/docs/scripts/lockfile-regen/branch_cleanup_wide.sh` — stale branch deletion
- `repos/docs/governance/2026-04-27-session/hexakit-residuals-cookbook.md` — surgical bump recipes
- `repos/docs/governance/2026-04-27-session/dependabot-residuals-playbook.md` — diagnosis classes

## Metrics target (next 30 days)
- Org dependabot alerts: 127 → <50 (-60%)
- Critical advisory MTTR: <24h
- Lockfile-regen success rate: >70% (rest need manifest)

## Implementation
Reference `lockfile_regen_v2.sh` for any new repo Dependabot bootstrap. Run weekly as cron-scheduled GitHub Action when Actions billing is restored.
