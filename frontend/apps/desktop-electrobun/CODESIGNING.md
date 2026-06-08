# Code Signing and Notarization

This document describes the signing inputs needed for the TraceRTM ElectroBun desktop client. Do not commit certificates, passwords, provisioning details, or real organization-specific certificate names to the repository.

ElectroBun's documented configuration uses `build.mac.codesign` and `build.mac.notarize` for macOS signing and notarization. Its platform build blocks are `build.mac`, `build.win`, and `build.linux`; the existing `electrobun.config.ts` should keep platform-specific build settings in those blocks.

## macOS Developer ID

macOS distribution outside the Mac App Store requires a Developer ID Application certificate and Apple notarization.

1. Enroll in the Apple Developer Program. Apple charges $99/year for the program.
2. In Keychain Access, create a certificate signing request for the release identity.
3. In the Apple Developer portal, generate a **Developer ID Application** certificate from that CSR.
4. Install the certificate in the macOS login keychain used for release builds.
5. Export the certificate and private key from Keychain Access as a `.p12` file.
6. Protect the `.p12` export with a strong password.
7. Base64-encode the `.p12` for CI storage.

Add these GitHub repository secrets:

- `MACOS_CERT_P12_BASE64`: base64-encoded Developer ID Application `.p12` export.
- `MACOS_CERT_PASSWORD`: password for the `.p12` export.
- `APPLE_ID`: Apple ID email used for notarization.
- `APPLE_APP_SPECIFIC_PASSWORD`: app-specific password generated from the Apple ID account.
- `APPLE_TEAM_ID`: Apple Developer Team ID.

ElectroBun's macOS signing documentation also references these runtime environment variables for its CLI:

- `ELECTROBUN_DEVELOPER_ID`: Developer ID certificate identity string available in the keychain.
- `ELECTROBUN_TEAMID`: Apple Developer Team ID.
- `ELECTROBUN_APPLEID`: Apple ID email.
- `ELECTROBUN_APPLEIDPASS`: app-specific password.

The GitHub Actions release workflow should import the decoded `.p12` into a temporary keychain, then map the GitHub secrets into the ElectroBun environment variables before packaging.

## Windows code signing

Windows release artifacts should be Authenticode-signed to reduce SmartScreen warnings and provide publisher identity.

1. Buy an EV or OV code signing certificate from a public certificate authority such as Sectigo or DigiCert.
2. Export the signing certificate and private key as `.pfx` or `.p12` if the vendor flow allows file-based export.
3. Protect the export with a strong password.
4. Base64-encode the exported certificate for CI storage.

Add these GitHub repository secrets:

- `WINDOWS_CERT_P12_BASE64`: base64-encoded `.pfx` or `.p12` signing certificate export.
- `WINDOWS_CERT_PASSWORD`: password for the certificate export.

The Windows release workflow should decode the certificate on the Windows runner, import it only for the job duration, and sign the generated `.exe` or installer artifact before upload.

Optional cheaper path: evaluate Azure Trusted Signing if the project prefers managed certificate issuance and signing over owning an EV/OV certificate file. If used, store only the Azure identifiers and credentials required by the signing action or CLI, not certificate private keys.

## Linux signing

Linux packages should be signed when publishing `.deb` or `.rpm` artifacts through a repository or package feed.

1. Generate a dedicated GPG key for TraceRTM desktop package signing.
2. Keep the public key distributable so users and package repositories can verify artifacts.
3. Export the private key for CI only if automated package signing is required.
4. Base64-encode the private key export before storing it as a GitHub secret.

Add these GitHub repository secrets:

- `GPG_PRIVATE_KEY_BASE64`: base64-encoded private GPG key export for package signing.
- `GPG_PASSPHRASE`: passphrase for the private GPG key.

The Linux release workflow should import the key into a temporary `GNUPGHOME`, sign package metadata or package files, then delete the temporary keyring before the job exits.

## CI integration

Create `.github/workflows/desktop-electrobun-release.yml` separately and keep all sensitive material in GitHub repository secrets.

Recommended CI flow:

1. Check out the repository.
2. Install Bun and project dependencies.
3. Build the web renderer that the desktop package consumes.
4. For macOS jobs:
   - Decode `MACOS_CERT_P12_BASE64` into a temporary `.p12` file.
   - Create and unlock a temporary keychain.
   - Import the `.p12` with `MACOS_CERT_PASSWORD`.
   - Export `ELECTROBUN_DEVELOPER_ID`, `ELECTROBUN_TEAMID`, `ELECTROBUN_APPLEID`, and `ELECTROBUN_APPLEIDPASS` from the GitHub secrets.
   - Run the macOS ElectroBun package command.
5. For Windows jobs:
   - Decode `WINDOWS_CERT_P12_BASE64` into a temporary certificate file.
   - Import it for the job or pass it to the selected signing command.
   - Run the Windows ElectroBun package command.
   - Sign the generated Windows artifact if ElectroBun does not sign it directly.
6. For Linux jobs:
   - Decode and import `GPG_PRIVATE_KEY_BASE64` into a temporary keyring.
   - Run the Linux ElectroBun package command.
   - Sign `.deb` or `.rpm` packages and package repository metadata as applicable.
7. Upload only signed release artifacts. Do not upload decoded certificates, temporary keychains, or keyrings.

The `electrobun.config.ts` file should contain the platform blocks consumed by ElectroBun:

```ts
build: {
  mac: {
    codesign: process.env.SIGNING_DISABLED !== "1",
    notarize: process.env.SIGNING_DISABLED !== "1",
  },
  win: {},
  linux: {},
}
```

The real project config may include additional ElectroBun fields in these blocks, such as `bundleCEF`, `defaultRenderer`, `entitlements`, or `icons`. Keep signing behavior environment-driven so CI can sign releases while local development remains unsigned.

## Local dev (unsigned)

Local development builds do not require signing. From `frontend/apps/desktop-electrobun`, run:

```sh
bun run dev
```

For local release packaging tests where signing should be skipped, set `SIGNING_DISABLED=1` before running the package command:

```sh
SIGNING_DISABLED=1 bun run package:mac
SIGNING_DISABLED=1 bun run package:win
SIGNING_DISABLED=1 bun run package:linux
```

Unsigned release test artifacts are for local verification only. Do not publish unsigned artifacts as public releases.
