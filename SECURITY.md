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

## Desktop Code Signing (ElectroBun Distribution)

The Tracera ElectroBun desktop client (`frontend/apps/desktop-electrobun/`) ships signed binaries for macOS, Windows, and Linux. This section documents the code-signing trust model and secret rotation policy for the signing infrastructure.

### Signing Trust Model

| Platform | Signing Authority | Trust Anchor |
|----------|------------------|--------------|
| macOS | Apple Developer ID Application | Apple Root CA → Worldwide Developer Relations CA |
| macOS (notarization) | Apple Notary Service | Apple Root CA |
| Windows | EV or OV code-signing cert (Sectigo / DigiCert) | DigiCert / Sectigo root |
| Linux (.deb) | GPG key (maintainer) | User's GPG trust db |
| Linux (.rpm) | GPG key (maintainer) | User's GPG trust db |

### GitHub Secrets

The following GitHub repository secrets protect the signing keys. **Rotation cadence: 90 days for active certs, immediately on any suspected compromise.** See `.github/workflows/desktop-electrobun-release.yml` and `frontend/apps/desktop-electrobun/CODESIGNING.md` for usage.

| Secret | What it protects | Rotation |
|--------|------------------|----------|
| `MACOS_CERT_P12_BASE64` | Apple Developer ID Application cert (base64) | Annual (cert expiry) + on compromise |
| `MACOS_CERT_PASSWORD` | Password for the .p12 | On rotation |
| `APPLE_ID` | Apple Developer account email | On account change |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password for notarytool | On rotation |
| `APPLE_TEAM_ID` | Apple Developer Team ID | Static (org-level) |
| `WINDOWS_CERT_P12_BASE64` | Windows code-signing cert (base64) | Annual + on compromise |
| `WINDOWS_CERT_PASSWORD` | Password for the .p12 | On rotation |
| `GPG_PRIVATE_KEY_BASE64` | Linux GPG signing key (base64) | Annual + on compromise |
| `GPG_PASSPHRASE` | GPG key passphrase | On rotation |

### What to do if a signing secret is compromised

1. **macOS cert**: Revoke the Developer ID Application cert via Apple Developer portal immediately. Generate a new cert. Re-export and re-upload the new `.p12` (rotated `MACOS_CERT_P12_BASE64` and `MACOS_CERT_PASSWORD`). Notify users via GitHub Security Advisory that builds between [date] and [date] should be considered untrusted.

2. **Windows cert**: Contact the issuing CA (Sectigo/DigiCert) to revoke. Issue a replacement cert. Re-upload as `WINDOWS_CERT_P12_BASE64`. Notify users via Security Advisory.

3. **GPG key**: Revoke the key on a public keyserver (`gpg --keyserver pgp.mit.edu --send-keys <KEY_ID>`). Generate a new key. Re-export. Notify users.

4. **Apple ID compromise**: Reset the Apple ID password, enable 2FA, rotate `APPLE_APP_SPECIFIC_PASSWORD`. Audit Apple Developer portal for unauthorized certs/profiles.

5. **All four after compromise**: Open a GitHub Security Advisory with severity `critical` and publish a CVE if warranted.

### Local development

For local builds, signing is **disabled by default** via `SIGNING_DISABLED=1`. Untrusted local builds are clearly marked in the OS (macOS: "unidentified developer"; Windows: "Unknown publisher"). End users should only install signed builds from the official GitHub Releases.

### Audit trail

Every signed release is logged to:
- GitHub Actions run history (`.github/workflows/desktop-electrobun-release.yml` invocations)
- Apple Notary Service log (for macOS)
- Rekor transparency log (SLSA attestations)
- The repo's `CHANGELOG.md` entry for that release

Any release artifact can be verified against the corresponding GitHub Release's `SHA256SUMS` file.

---
Thank you for helping keep the traceability ecosystem secure!
