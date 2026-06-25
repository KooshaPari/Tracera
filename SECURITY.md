# Security Policy

## Supported Versions

Tracera is in active early development. Security fixes are applied to the current
default branch and the latest released version when releases are available.

## Reporting a Vulnerability

Please **do not** report suspected security vulnerabilities in public issues,
discussions, pull requests, chat logs, or social media. Public disclosure prior
to coordinated mitigation puts every user at risk.

### Private Disclosure Channels

Report vulnerabilities through any of the following **private** channels, in
order of preference:

1. **GitHub Private Vulnerability Reporting** for this repository
   (Security tab → "Report a vulnerability").
2. **Email** the maintainers at the security contact listed in
   `CODEOWNERS` / repository metadata, with `SECURITY: Tracera` in the subject.
3. **Direct message** a maintainer through a verified private channel.

### Required Report Contents

Include as much detail as you can safely share:

- Affected component, crate, endpoint, command, or configuration
- Steps to reproduce or a minimal proof of concept
- Expected and observed impact (confidentiality / integrity / availability)
- Affected versions, commits, tags, or deployment context
- Any known mitigations, workarounds, or threat-model context
- Whether you intend to disclose publicly and on what timeline

## Coordinated Disclosure Timeline

Tracera follows a **90-day coordinated disclosure** policy, modeled on
Google Project Zero and the CN / ISRG coordinated-disclosure guidelines:

| Day    | Milestone                                                           |
|--------|---------------------------------------------------------------------|
| 0      | Report received via private channel.                                |
| ≤ 5 bd | Maintainer acknowledgement with a tracking ID and triage owner.     |
| ≤ 10 bd| Initial status update: severity, scope, reproduction confirmation.  |
| ≤ 90 d | Target for fix, mitigation, or documented accepted-risk decision.   |
| Fix    | Patch released in a tagged version and advisory drafted.            |
| ≤ 90 d | Public disclosure (coordinated with the reporter when feasible).    |

If a fix requires more than 90 days, the maintainers will:

- Notify the reporter of the revised timeline and reasoning.
- Publish a **CVE** reservation through the relevant CNA (GitHub CNA for the
  `KooshaPari/Tracera` namespace by default) once a CVE ID is required.
- Issue a GitHub Security Advisory (`GHSA-xxxx-xxxx-xxxx`) describing the
  impact, affected versions, patched versions, severity, CVSS score, and
  credit (when the reporter consents).
- Coordinate the public advisory with the reporter's preferred disclosure
  date whenever practical.

Early disclosure is welcome and appreciated when a fix is already available;
mutual agreement on a disclosure date is the goal.

## CVE & Advisory Process

- A **CVE ID** is requested as soon as triage confirms the report is a
genuine, reproducible security issue.
- Tracera maintainers use **GitHub Security Advisories** as the canonical
public disclosure surface. The advisory supersedes any earlier informal
note.
- Severity is scored using **CVSS v3.1** and recorded in the advisory.
- Patched versions are tagged and released via the `release-plz` pipeline;
the advisory references the fix commit and the released version.

## Handling Expectations

- Maintainers will keep reports confidential, limit access to people needed
to investigate and remediate the issue, and credit reporters when
requested and appropriate.
- Reporters are expected to avoid privacy violations, data destruction,
service disruption, persistence, lateral movement, and public disclosure
before the maintainers have had a reasonable opportunity to investigate and
remediate the issue.

## Runtime hardening (new)

- All non-probe API requests are routed through `ApiAuthzMiddleware` in
  `src/tracertm/api/main.py`.
- Token and claim validation is centralized in `src/tracertm/api/deps.py`.
- Endpoint-to-feature coverage and authz intent are now documented in the
  governance package under `docs/governance/policy/`.

## Input-validation policy

- Authorization header parsing is strict (`Authorization: Bearer <token>`).
- Required token claims include `sub` and `exp`; expired claims are rejected.
- Scope normalization is enforced through middleware when configured for a route.
- API body/param constraints should be explicit per router model (path,
  query, and request schemas). Missing constraints are tracked in:
  [`docs/governance/policy/coverage_matrix_self_application.md`](docs/governance/policy/coverage_matrix_self_application.md).

## Secrets and configuration

Secrets must be injected via environment values and never checked in:

- `TRACERA_JWT_SECRET`
- `TRACERA_JWT_PUBLIC_KEY`
- `TRACERA_JWT_AUDIENCE`
- `TRACERA_JWT_ISSUER`
- `TRACERA_DB_DSN` and service credentials

Signature verification remains permissive until `TRACERA_JWT_SECRET` is set in
production environments.

## Rate-limiting

A rollout plan is documented in [`docs/security/SECURITY.md`](docs/security/SECURITY.md).
It starts with middleware-level request buckets and moves to a shared Redis-backed
store for multi-instance safety.
