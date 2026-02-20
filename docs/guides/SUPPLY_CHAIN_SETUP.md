# Supply Chain Security Setup Guide

**Project:** TracerTM
**Criticality Tier:** Critical
**Last Updated:** 2026-02-14

## Overview

TracerTM is configured as a **critical-tier** project, requiring cryptographic attestation and supply chain verification. This guide explains how to set up the required tooling.

---

## Required Components

### 1. Cosign Installation

Install [cosign](https://github.com/sigstore/cosign) for signing attestations:

```bash
# macOS
brew install sigstore/tap/cosign

# Linux
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Verify installation
cosign version
```

### 2. Generate Signing Keys

**Option A: Key-based Signing (Recommended for local development)**

```bash
# Generate key pair
cosign generate-key-pair

# This creates:
# - cosign.key (private key, keep secure!)
# - cosign.pub (public key)

# Move to project verification directory
mv cosign.pub .claude/
# Store cosign.key securely (NOT in git)
```

**Option B: Keyless Signing (OIDC-based)**

Requires GitHub Actions or similar CI environment with OIDC support.

```bash
# Set environment variables
export COSIGN_EXPERIMENTAL=1
export QA_COSIGN_CERT="path/to/cert.pem"
export QA_COSIGN_IDENTITY="your-identity-regexp"
export QA_COSIGN_ISSUER="https://token.actions.githubusercontent.com"
```

---

## Configuration

### Environment Variables

Add to your shell profile or CI environment:

```bash
# Key-based signing
export QA_COSIGN_PUBLIC_KEY="$HOME/path/to/.claude/cosign.pub"

# Or keyless signing
export QA_COSIGN_CERT="path/to/cert.pem"
export QA_COSIGN_IDENTITY="^https://github.com/myorg/.*$"
export QA_COSIGN_ISSUER="https://token.actions.githubusercontent.com"
```

### Supply Chain Requirements

Critical-tier projects enforce:

- `QA_REQUIRE_SIGNED_ATTESTATION=true` - Must have cryptographic signature
- `QA_REQUIRE_SLSA_PROVENANCE=true` - Must have SLSA attestation
- `QA_REQUIRE_REKOR_VERIFICATION=true` - Must have Rekor transparency log entry

These are automatically set for critical-tier projects.

---

## Manual Signing Workflow

If cosign is not available in automated pipelines, you can sign manually:

### 1. Generate Attestation

Quality gates automatically create `.claude/verification/qa-attestation.json`

### 2. Sign Attestation

```bash
# Key-based signing
cosign sign-blob \
  --key cosign.key \
  --output-signature .claude/verification/qa-attestation.sig \
  .claude/verification/qa-attestation.json

# Keyless signing (requires OIDC)
cosign sign-blob \
  --output-signature .claude/verification/qa-attestation.sig \
  --output-certificate .claude/verification/qa-attestation.cert \
  .claude/verification/qa-attestation.json
```

### 3. Upload to Rekor (Optional)

```bash
# Create Rekor bundle
cosign verify-blob \
  --key cosign.pub \
  --signature .claude/verification/qa-attestation.sig \
  --bundle .claude/verification/qa-attestation.bundle.json \
  .claude/verification/qa-attestation.json
```

---

## Verification

### Manual Verification

```bash
# Verify signature with public key
cosign verify-blob \
  --key .claude/cosign.pub \
  --signature .claude/verification/qa-attestation.sig \
  .claude/verification/qa-attestation.json

# Verify with bundle (includes Rekor verification)
cosign verify-blob \
  --bundle .claude/verification/qa-attestation.bundle.json \
  --signature .claude/verification/qa-attestation.sig \
  .claude/verification/qa-attestation.json
```

### Automated Verification

The `qa-supply-chain-verifier.sh` hook runs on Stop events and verifies:

1. Attestation file exists
2. Signature file exists (if signing required)
3. Signature is valid (if cosign available)
4. Rekor bundle is valid (if Rekor verification required)

---

## Development Workflow

### Without Cosign (Development Mode)

For local development without cosign installed:

1. Set environment variable to disable enforcement:
   ```bash
   export QA_SUPPLY_CHAIN_FAIL_CLOSED=false
   ```

2. The hook will warn but not block on missing signatures

3. **Note:** CI/production MUST have cosign installed and enforcement enabled

### With Cosign (Production Mode)

1. Ensure cosign is installed and keys configured
2. Quality gates run automatically
3. Attestations are signed automatically (if hooks configured)
4. Verification runs on every Stop event

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Quality Gate
on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For keyless signing
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Install cosign
        uses: sigstore/cosign-installer@v3

      - name: Run quality gates
        run: make quality

      - name: Sign attestation (keyless)
        env:
          COSIGN_EXPERIMENTAL: 1
        run: |
          cosign sign-blob \
            --yes \
            --output-signature .claude/verification/qa-attestation.sig \
            --output-certificate .claude/verification/qa-attestation.cert \
            .claude/verification/qa-attestation.json

      - name: Verify signature
        run: |
          cosign verify-blob \
            --certificate .claude/verification/qa-attestation.cert \
            --signature .claude/verification/qa-attestation.sig \
            --certificate-identity-regexp "^https://github.com/myorg/.*$" \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com \
            .claude/verification/qa-attestation.json
```

---

## Troubleshooting

### "cosign not installed"

Install cosign following instructions above.

### "required attestation file missing"

Quality gates must run first to generate `.claude/verification/qa-attestation.json`

### "cosign verification failed"

- Check that public key matches private key used for signing
- Verify signature file is not corrupted
- Ensure attestation file hasn't changed since signing

### "Rekor verification required but bundle missing"

Generate Rekor bundle using `cosign verify-blob --bundle ...`

---

## Security Best Practices

1. **Never commit private keys** (`cosign.key`) to version control
2. **Rotate keys regularly** (quarterly for critical projects)
3. **Use keyless signing in CI** to avoid key management
4. **Enable Rekor transparency log** for non-repudiation
5. **Verify signatures** before deploying artifacts
6. **Audit Rekor logs** periodically for unauthorized signatures

---

## References

- [Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [SLSA Provenance Spec](https://slsa.dev/provenance/v1)
- [Rekor Transparency Log](https://docs.sigstore.dev/rekor/overview/)
- [TracerTM Verification Policy](../../VERIFICATION_POLICY.md)
