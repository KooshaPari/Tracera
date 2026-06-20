# Verification Policy

This document defines the verification and quality assurance policy for the trace project.

## Quality Standards

The project operates at **critical** tier, requiring:
- All must-pass checkers GREEN (Ruff, Go build/vet, golangci-lint, TSC, Tach, Govulncheck)
- SLSA provenance attestation with signature verification
- Rekor transparency log integration
- Comprehensive test coverage across unit, integration, and E2E layers

## Dispute and Challenge Workflow

### Initiating a Dispute

If a verifier (human or automated agent) believes a quality gate decision is incorrect, they may initiate a **dispute** by:

1. Creating a dispute record in `.claude/verification/disputes.jsonl`
2. Including:
   - Timestamp
   - Disputed gate/check
   - Reasoning for dispute
   - Evidence supporting the challenge
   - Contact information or agent ID

### Dispute Resolution Process

1. **Acknowledgment** (within 24 hours)
   - Dispute is logged and acknowledged
   - Status set to "under_review"

2. **Investigation** (within 7 days)
   - Technical review of disputed decision
   - Collection of additional evidence
   - Consultation with relevant stakeholders

3. **Resolution** (within 14 days)
   - Decision documented with rationale
   - Status updated to "resolved" or "escalated"
   - If gate decision was incorrect, corrective action taken

4. **Appeal**
   - If disputer disagrees with resolution, they may escalate
   - Appeals reviewed by senior technical lead or project maintainer
   - Final decision documented in dispute record

### Verifier Escalation

For critical blocking issues or systemic failures:
- **Level 1**: File dispute via standard workflow
- **Level 2**: Escalate to project technical lead
- **Level 3**: Escalate to project owner/maintainer
- **Emergency**: For security or compliance violations, immediate escalation permitted

### Open Dispute Tracking

- Maximum open dispute duration: **14 days** (configurable in `.claude/quality.json`)
- Disputes exceeding max duration trigger alerts
- Monthly dispute summary reports generated
- Dispute trends analyzed for systematic issues

## Attestation and Provenance

All quality gates produce:
- **SLSA attestation** (`.claude/verification/qa-attestation.json`)
- **Digital signature** (`.claude/verification/qa-attestation.sig`)
- **Rekor bundle** (`.claude/verification/qa-attestation.bundle.json`)

These artifacts provide:
- Tamper-evident quality records
- Transparency via public ledger (Rekor)
- Non-repudiation of quality claims
- Auditable verification history

## Compliance Requirements

For critical tier projects:
- Zero tolerance for must-pass checker violations
- Mandatory signed attestations
- Transparency log integration
- Dispute workflow availability
- Regular quality audits

## Policy Updates

This policy may be updated to reflect:
- New quality standards
- Tooling improvements
- Process refinements
- Lessons learned from disputes

All policy changes require:
- Documentation of rationale
- Review by technical lead
- Update of `.claude/quality.json` configuration
