# Security Policy 🔐

## Supported Versions

We provide security updates for the following versions of **TracerTM**:

| Version | Supported          |
| ------- | ------------------ |
| v1.0.x  | :white_check_mark: |
| < v1.0  | :x:                |

## Reporting a Vulnerability

We take the security of **TracerTM** seriously. If you discover a security vulnerability, please do NOT open a public issue. Instead, report it privately.

Please report any security concerns directly to the maintainers at [kooshapari@gmail.com](mailto:kooshapari@gmail.com).

### What to include in your report
- A detailed description of the vulnerability.
- Steps to reproduce (proof of concept).
- Potential impact on the system or user data.
- Any suggested fixes or mitigations.

We will acknowledge your report within 48 hours and provide a timeline for resolution.

## Hardening & Governance Measures

**TracerTM** is designed for high-assurance environments:

- **SLSA Provenance**: All builds produce tamper-evident quality records and attestations.
- **Signed Quality Gates**: Every quality check (Ruff, Go vet, golangci-lint, TSC) must be signed to pass.
- **Rekor Integration**: All attestations are logged to a transparency ledger for auditability.
- **Boundary Enforcement**: `tach` Architectural boundaries prevent unintended dependency leakage.
- **Credential Isolation**: All secrets are managed via HashiCorp Vault in production environments.
- **Audit Trails**: Full traceability of system decisions via WebSocket-synced RTM updates.

---
Thank you for helping keep the traceability ecosystem secure!
