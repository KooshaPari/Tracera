# Specifications

## Acceptance Criteria

- Add the Sladge badge near the top of the current README.
- Keep all canonical `Tracera` local changes untouched.
- Record validation and known blockers in downstream and projects-landing
  ledgers.
- Do not repair or delete stale `Tracera-recovered` git metadata in this badge
  lane.

## Assumptions, Risks, Uncertainties

- Assumption: live `Tracera` supersedes the older `Tracera-recovered` ledger
  path.
- Risk: LFS pointer warnings make broad validation noisy.
- Mitigation: keep the change README/session-doc scoped and document the LFS
  warning as pre-existing checkout behavior.
