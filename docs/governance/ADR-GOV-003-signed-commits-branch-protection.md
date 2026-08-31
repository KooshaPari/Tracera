# ADR-GOV-003: Signed commits and branch protection policy

- **Status**: Accepted
- **Date**: 2026-08-30
- **Authors**: KooshaPari
- **Supersedes**: none
- **Related**:
  - [`ADR-SERVER-001-endpoint-regression-audit.md`](../policy/ADR-SERVER-001-endpoint-regression-audit.md)
  - [`adr_index.md`](../policy/adr_index.md) — governance ADR inventory

## Context

The Tracera repository has grown into a multi-contributor project with CI
gates, release workflows, and governance artifacts. Currently there are no
enforced branch-protection rules on `main`: any committer can push directly,
merge without review, and land unsigned commits. This creates three risks:

1. **Commit provenance** — unsigned commits can be trivially forged via
   `git config user.name`, making authorship unverifiable.
2. **Supply-chain integrity** — a direct push bypasses PR review and CI.
3. **Audit trail gaps** — governance requires a verifiable chain of custody
   from author through reviewer to merge.

## Decision

### 1. Require signed commits

All commits on `main` must carry a valid GPG or SSH signature that GitHub
can verify. Unsigned or unverified signatures will be rejected.

### 2. Protect the `main` branch

| Rule | Setting |
|------|---------|
| Require pull request before merging | Enabled (min 1 approval) |
| Required status checks | `ci / build-and-test`, `ci / clippy`, `ci / fmt-check` |
| Require conversation resolution | Enabled |
| Require linear history | Enabled (squash merge only) |
| Include administrators | Enabled (no bypass) |
| Allow force pushes | Disabled |
| Allow deletions | Disabled |

### 3. Require pull request reviews

Every change must flow through a PR with at least one approved review from
a write-access contributor. Stale approvals are dismissed on new pushes.

### 4. Require status checks

CI must pass before merge: build-and-test, Clippy (zero warnings), and
`rustfmt` formatting. Additional checks (e.g. `cargo-audit`, coverage
thresholds) may be added as the pipeline matures.

## Consequences

### Positive

- Every commit on `main` carries a cryptographic signature — authorship is
  auditable and forgery is detectable.
- No code reaches production without peer review, reducing regressions.
- Status checks guarantee the build, linter, and formatter all pass before
  merge.
- Squash-merge-only preserves a linear, bisectable `main` log.
- "Include administrators" prevents bypasses even by repository owners.

### Negative

- Contributors must configure GPG/SSH signing locally (one-time friction).
- CI bots (Dependabot, Mergify) must use the GitHub API for merges rather
  than direct pushes; Dependabot PRs via the UI are signed automatically.
- Requiring reviews and checks adds latency to the merge flow for small
  changes.

## Implementation steps

1. **Generate and register signing keys** — each contributor generates a
   GPG or SSH key pair and uploads the public key to GitHub under
   *Settings → SSH and GPG keys*.
2. **Configure local Git** — set `commit.gpgSign = true` and specify
   `user.signingKey` in the global or local config.
3. **Enable branch protection on `main`** — apply the rules in section 2
   via *Settings → Branches → Add rule*.
4. **Verify required status checks** — confirm the CI workflow produces
   check runs named `ci / build-and-test`, `ci / clippy`, and
   `ci / fmt-check`, and add them to the required checks list.
5. **Migrate bot workflows** — move any local automation that pushes
   directly to `main` to open PRs instead.
6. **Audit retroactively** — run `git log --show-signature main` to
   verify recent commits carry valid signatures. Existing unsigned
   commits are grandfathered; future pushes are gated.
7. **Update governance index** — add this ADR to
   `docs/governance/policy/adr_index.md`.

## References

- [GitHub Docs: Branch protection rules](https://docs.github.com/en/repositories/configuring-a-branches-and-protections-branches/managing-a-branch-protection-rule)
- [GitHub Docs: Signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
- [`docs/governance/policy/adr_index.md`](../policy/adr_index.md)
