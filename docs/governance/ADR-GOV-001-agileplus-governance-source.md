# ADR-GOV-001: AgilePlus as the Single Authoritative Governance Source

## Status

**Accepted** (2026-08-30)

## Context

The organization currently suffers from significant governance sprawl. Regulatory compliance, architectural standards, and quality gates are fragmented across multiple tools and repositories. This lack of centralization has resulted in multiple 'sources of truth' that often conflict with one another.

### Definitions
- **Governance Sprawl**: The uncontrolled growth of governance rules across disparate systems, leading to duplication and inconsistency.
- **SSOT (Single Source of Truth)**: A principle that every data element is mastered in only one place and is referenced by other systems.

1.  **GitHub Actions Workflows**: Scattered across `.github/workflows` with inconsistent naming and overlapping triggers. Many workflows duplicate logic for checking lint, test coverage, and security vulnerabilities.
2.  **Documentation Repositories**: `docs/`, `governance/`, and `adr/` folders often contain conflicting or outdated directives. For example, the README might state a requirement that is not enforced in CI.
3.  **Local Scripts**: Ad-hoc `*.ps1` and `*.sh` scripts in the root directory performing "shadow" governance checks. These scripts are often run manually and are not version-controlled in a central location.
4.  **External Dashboards**: Manual spreadsheets and dashboards tracking compliance status, often out of sync with actual repository state. These are updated sporadically and lack automation.

This fragmentation leads to:
- **Inconsistency**: Different branches enforce different rules. A PR might pass CI on a feature branch but fail on `main` due to different workflow triggers.
- **Drift**: Manual updates to documentation often lag behind code changes. It is common for a "required" step to be documented but not enforced.
- **Opacity**: It is difficult for new contributors or auditors to understand the "source of truth" for governance. There is no single place to look for "how we do things here."
- **Duplication**: The same quality gate is often defined in three different places (CI, docs, and scripts), leading to maintenance nightmares.
- **Audit Risk**: During compliance reviews, the lack of a single authoritative source makes it difficult to prove that all required controls are in place and active.

AgilePlus has emerged as the primary orchestration layer for CI/CD and quality gates, yet it is not currently recognized as the *authoritative* source of governance. This lack of formal authority creates confusion regarding which tool is the final arbiter of governance rules.

## Decision

We will establish **AgilePlus** as the **Single Source of Truth (SSOT)** for all governance-related definitions, including quality gates, compliance requirements, and architectural standards.

All other tools (GitHub Actions, local scripts, documentation) will either be deprecated or refactored to *consume* governance definitions from AgilePlus rather than defining their own. 

AgilePlus is the system of record for:
- Quality Gate Definitions (e.g., test coverage thresholds, linting rules)
- Compliance Checks (e.g., dependency audits, license scanning)
- Architectural Constraints (e.g., allowed crate dependencies, module boundaries)
- Release Criteria (e.g., versioning rules, changelog requirements)

This decision formalizes the role of AgilePlus as the central governance engine.

## Consequences

### Positive

- **Consistency**: A single definition of a "quality gate" ensures that local development, CI, and production environments all enforce the same rules.
- **Auditability**: AgilePlus provides a centralized log of governance decisions and enforcement actions, making it easier to pass audits.
- **Maintainability**: Updating a governance rule in AgilePlus automatically propagates to all integrated systems, reducing manual overhead.
- **Clarity**: Developers and auditors have a single location to consult for all compliance and quality standards.
- **Velocity**: Reduces the time spent reconciling conflicting rules across different systems and accelerates onboarding.

### Negative

- **Migration Effort**: Significant work is required to refactor existing GitHub Actions and local scripts to use the new SSOT. This is estimated at 4-6 weeks of engineering time.
- **Dependency Risk**: Systems become dependent on the availability and performance of the AgilePlus platform. We must ensure high availability (SLA 99.9%).
- **Learning Curve**: Team members accustomed to manual or ad-hoc governance processes will need training on AgilePlus.
- **Initial Overhead**: Setting up the SSOT definitions requires an initial investment of time to ensure accuracy and completeness.
- **Resistance to Change**: Some team members may prefer their existing scripts or workflows and may resist the transition to a centralized model.
- **Platform Lock-in**: Deep integration with AgilePlus may make it difficult to switch to a different governance platform in the future.
- **Performance Overhead**: Centralized queries to the SSOT may introduce latency in the CI pipeline if not optimized correctly.

## Directives

1.  **Prohibition of Shadow Governance**: No new quality gates, compliance checks, or architectural rules may be defined outside of AgilePlus. Any new rule must be first defined in the AgilePlus governance configuration.
2.  **Workflow Refactoring**: All existing `.github/workflows` that implement governance logic must be refactored to call AgilePlus APIs or use AgilePlus-maintained reusable actions within the next 60 days.
3.  **Script Deprecation**: Local `*.ps1` and `*.sh` scripts performing governance tasks will be deprecated within 30 days and replaced by `agileplus-cli enforce` commands.
4.  **Documentation Synchronization**: The `docs/governance/` directory will be automatically generated from AgilePlus metadata, not manually maintained. Manual edits to this directory will be overwritten by CI.
5.  **Audit Trail Integration**: All governance enforcement actions must be reported back to the AgilePlus central ledger for centralized auditing and reporting. This includes CI results and local CLI runs.

## Implementation Plan

### Phase 1: Assessment and Preparation (Weeks 1-2)

- **Inventory**: Catalog all existing governance rules across GitHub Actions, documentation, and scripts. Create a comprehensive list of all current quality gates and their owners.
- **Gap Analysis**: Identify gaps in AgilePlus's current coverage of these rules. Determine which rules can be directly migrated and which require new features or extensions.
- **Configuration**: Set up AgilePlus as the central store for the initial set of migrated rules. Define the data schema, API interfaces, and access control policies.
- **Stakeholder Buy-in**: Present the plan to the engineering leads and obtain agreement on the migration timeline and milestones.

### Phase 2: Migration and Refactoring (Weeks 3-6)

- **Refactor Workflows**: Update `.github/workflows` to use the new `agileplus/gate-check` action. This action will query the SSOT for rules and enforce them.
- **CLI Integration**: Replace local scripts with `agileplus-cli enforce` commands. This allows developers to run the same governance checks locally that CI runs.
- **Documentation Generation**: Implement the automated sync from AgilePlus to `docs/governance/`. This ensures that the documentation is always up-to-date with the actual rules.
- **Testing**: Develop a comprehensive test suite to ensure that the migration does not introduce regressions in governance enforcement.
- **Pilot Program**: Run a pilot project to validate the new model before rolling it out to the entire organization.

### Phase 3: Full Adoption and Enforcement (Weeks 7-8)

- **Blocking Enforcement**: Enable "blocking" mode in AgilePlus to prevent merges that do not meet SSOT-governed standards. This is the final step in establishing the SSOT.
- **Training**: Conduct workshops for the engineering team on the new governance model. Provide documentation, examples, and best practices for common tasks.
- **Monitoring**: Establish dashboards to monitor governance compliance in real-time. Set up alerts for failures or drift.
- **Review**: Conduct a post-implementation review to assess the effectiveness of the new model and identify areas for continuous improvement.
- **Decommission**: Formally decommission old scripts and workflows that have been replaced by the AgilePlus SSOT.
- **Success Metrics**: Establish KPIs (e.g., 100% rule coverage, 50% reduction in governance-related PR failures) to measure the success of the migration.

## Related Decisions

- **ADR-GOV-002**: Workflow Standardization (Pending)
- **ADR-GOV-003**: Documentation Generation Pipeline (Pending)
