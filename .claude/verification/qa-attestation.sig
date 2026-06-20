PLACEHOLDER: Cosign signature required for critical-tier project

To generate proper signature:
1. Install cosign: brew install sigstore/tap/cosign
2. Generate keys: cosign generate-key-pair
3. Sign attestation:
   cosign sign-blob --key cosign.key \
     --output-signature .claude/verification/qa-attestation.sig \
     .claude/verification/qa-attestation.json

See docs/guides/SUPPLY_CHAIN_SETUP.md for detailed instructions.

For development mode (bypass enforcement):
  export QA_SUPPLY_CHAIN_FAIL_CLOSED=false
