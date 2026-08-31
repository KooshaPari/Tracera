# Spec 013: Desktop Application Hardening

| Field | Value |
|-------|-------|
| **Spec ID** | TRACERA-SPEC-013 |
| **Title** | Desktop App Hardening: Signing, Update, Security |
| **Status** | Draft |
| **Version** | 2.0 |
| **Author** | Tracera Core Team |
| **Date** | 2026-08-30 |

---

## 1. Motivation

Tracera ships native desktop builds for macOS (arm64, x64), Windows (x64), and Linux (x64) via Electrobun. Users expect authentic, tamper-proof, auto-updating, and resilient binaries. This specification defines the hardening measures that make the desktop distribution trustworthy and production-grade.

---

## 2. Code Signing

### 2.1 macOS (Apple Notarization + GPG)

| Property | Requirement |
|----------|-------------|
| Signing identity | Developer ID Application cert |
| Entitlements | App sandbox, hardened runtime |
| Notarization | `xcrun notarytool submit` + App Store Connect API key |
| Stapling | `xcrun stapler staple` before release |
| Verification | `spctl --assess --type execute` |

### 2.2 Windows (Authenticode)

| Property | Requirement |
|----------|-------------|
| Certificate | EV Code Signing from DigiCert/Sectigo |
| Timestamp | `http://timestamp.digicert.com` |
| Sign tool | `signtool sign /fd SHA256 /tr ... /td sha256 /f cert.pfx` |
| Verification | `signtool verify /pa /v Tracera.exe` |
| SmartScreen | EV cert eliminates SmartScreen warnings |

### 2.3 Linux (GPG + Archiving)

| Property | Requirement |
|----------|-------------|
| Signing key | Release GPG key (4096-bit RSA) |
| Artifact | `.tar.gz` + detached `.sig` |
| Verification | `gpg --verify Tracera-linux-x64.tar.gz.sig` |
| Package managers | Flatpak/Snap/APT repo metadata signed |

---

## 3. Auto-Update Mechanism

### 3.1 Update Manifest

```yaml
# https://releases.tracera.io/manifest.json
version: "2.4.0"
channel: "stable"
release_date: "2026-08-30"
min_supported: "2.2.0"
files:
  - platform: darwin-arm64
    url: "https://releases.tracera.io/v2.4.0/Tracera-darwin-arm64.zip"
    sha256: "a1b2c3d4..."
    size_bytes: 78_340_000
  - platform: darwin-x64
    url: "https://releases.tracera.io/v2.4.0/Tracera-darwin-x64.zip"
    sha256: "e5f6a7b8..."
  - platform: win32-x64
    url: "https://releases.tracera.io/v2.4.0/Tracera-win32-x64.zip"
    sha256: "c9d0e1f2..."
  - platform: linux-x64
    url: "https://releases.tracera.io/v2.4.0/Tracera-linux-x64.tar.gz"
    sha256: "a3b4c5d6..."
signature:
  algorithm: "ed25519"
  public_key: "release-update-pub-2026.key"
  signed_manifest: "manifest.json.sig"
```

### 3.2 Release Channels

| Channel | Audience | Frequency | Stability Gate |
|---------|----------|-----------|----------------|
| `stable` | Production users | Bi-weekly | All CI + manual sign-off |
| `beta` | Early adopters | Weekly | All CI green |
| `canary` | Internal dogfood | On merge to main | Build succeeds |

### 3.3 Client-Side Verification Flow

1. Fetch `manifest.json` and `manifest.json.sig` from CDN.
2. Verify Ed25519 signature against embedded public key.
3. Match platform + architecture.
4. Download artifact over HTTPS (TLS 1.2+).
5. Compute SHA-256 and compare to manifest hash.
6. Verify code signature of binary inside archive.
7. Apply update: quit → replace → restart.

### 3.4 Rollback Protection

- Manifest version must be monotonically increasing per channel.
- Client stores last-applied version in encrypted local state.
- If `min_supported` threshold crossed, app blocks use until update.

---

## 4. CI Matrix (GitHub Actions)

```yaml
strategy:
  matrix:
    include:
      - { os: macos-14,    platform: darwin-arm64 }
      - { os: macos-13,    platform: darwin-x64 }
      - { os: windows-2022, platform: win32-x64 }
      - { os: ubuntu-22.04, platform: linux-x64 }
```

### 4.1 CI Gates

| Gate | Tool | Fail Action |
|------|------|-------------|
| Build succeeds | Electrobun | Block |
| Code signing valid | spctl / signtool / gpg | Block |
| Unit tests pass | Vitest | Block |
| Desktop integration tests | Playwright Electron | Block |
| Size budget (< 120 MB) | Custom script | Warn |
| Security scan | Trivy / Gitleaks | Block |
| License compliance | cargo-deny / licensee | Block |

---

## 5. Test Files (10 Files)

| # | Test File | Coverage |
|---|-----------|----------|
| 01 | `test/signing/macos-notarization.test.ts` | Notarization + stapling |
| 02 | `test/signing/windows-authenticode.test.ts` | Authenticode verification |
| 03 | `test/signing/linux-gpg.test.ts` | GPG signature verification |
| 04 | `test/update/manifest-fetch.test.ts` | Manifest download + parse |
| 05 | `test/update/signature-verification.test.ts` | Ed25519 signature check |
| 06 | `test/update/rollback-protection.test.ts` | Version monotonicity |
| 07 | `test/security/sandbox-enforcement.test.ts` | Sandbox / CSP / IPC |
| 08 | `test/resilience/crash-recovery.test.ts` | Crash state restoration |
| 09 | `test/resilience/data-integrity.test.ts` | Atomic writes + checksums |
| 10 | `test/ci/cross-platform-build.test.ts` | Build matrix validation |

---

## 6. Security Hardening

### 6.1 Sandbox (macOS)

| Capability | Status |
|------------|--------|
| Network (outbound) | Allowed |
| Network (inbound) | Denied |
| File: user-selected | Allowed |
| File: app container | Allowed |
| File: system-wide | Denied |
| Camera / Microphone | Denied |

### 6.2 Content Security Policy

```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
connect-src 'self' https://api.tracera.io wss://api.tracera.io;
object-src 'none';
frame-ancestors 'none';
```

### 6.3 IPC Validation

All IPC messages are validated against an allowlist:

| Channel | Direction | Payload |
|---------|-----------|---------|
| `tracera:graph:get` | renderer→main | `{ nodeId: string }` |
| `tracera:graph:result` | main→renderer | `{ nodes: Node[] }` |
| `tracera:coverage:summary` | renderer→main | `{ range: DateRange }` |
| `tracera:notification:push` | main→renderer | `{ notif: Notif }` |
| `tracera:update:check` | renderer→main | `{}` |

Unknown channels are logged and dropped. Max payload: 1 MB. Rate limit: 100 msg/s.

### 6.4 Privilege Minimization

| Principle | Implementation |
|-----------|---------------|
| Least privilege | Renderer has no Node.js access |
| Context isolation | `contextIsolation: true`, `nodeIntegration: false` |
| External links | `shell.openExternal` → system browser |
| Secrets | Never passed to renderer process |

---

## 7. Resilience

### 7.1 Crash Recovery (Journal Pattern)

```typescript
async function writeWithRecovery(path: string, data: Buffer): Promise<void> {
  const journalPath = `${path}.journal`;
  const tmpPath = `${path}.tmp`;
  await fs.writeFile(tmpPath, data);
  await fs.writeFile(journalPath, JSON.stringify({
    action: 'replace', target: path, tmp: tmpPath, timestamp: Date.now(),
  }));
  await fs.rename(tmpPath, path);
  await fs.unlink(journalPath);
}
```

### 7.2 Data Integrity

| Mechanism | Detail |
|-----------|--------|
| Checksums | SHA-256 on write, verified on read |
| Backup rotation | 3 most recent in `data/backups/` |
| Max backup size | 50 MB total |
| Integrity check | On app startup |

### 7.3 Log Rotation

| Property | Value |
|----------|-------|
| Location | `{appData}/tracera/logs/` |
| Max file size | 10 MB |
| Max retained | 30 files |
| Compression | Gzip on rotation |
| Sensitive data | Emails, tokens redacted |
| Format | JSON `{ timestamp, level, component, message }` |

---

## 8. Threat Model

| Threat | Mitigation |
|--------|-----------|
| Tampered binary | Code signing + manifest signature |
| MITM on update | TLS 1.2+ + pinned certificate |
| IPC privilege escalation | Channel allowlist + schema validation |
| Renderer escape | Sandbox + contextIsolation + CSP |
| Data corruption | Journaling + atomic writes + backups |
| Secret leakage | Redaction filter on log writes |
| Supply chain attack | CI signing + reproducible builds + Trivy |
| Old manifest replay | Version monotonicity + min_supported |

---

## 9. Acceptance Criteria

| # | Criterion |
|---|-----------|
| AC-01 | macOS builds pass `spctl --assess` and `notarytool` |
| AC-02 | Windows builds pass `signtool verify` with valid timestamp |
| AC-03 | Linux builds include GPG detached signature |
| AC-04 | Auto-update manifest signed with Ed25519, verified client-side |
| AC-05 | Tampered manifest rejected (1-bit flip test) |
| AC-06 | Rollback to older version blocked |
| AC-07 | CI matrix produces all 4 platform artifacts |
| AC-08 | All 10 test files pass across macOS, Linux, Windows |
| AC-09 | macOS sandbox restricts file/network as specified |
| AC-10 | CSP blocks `object-src`, `frame-ancestors`, unauthorized origins |
| AC-11 | Unknown IPC channels dropped and logged |
| AC-12 | IPC payload validation rejects malformed messages in < 1ms |
| AC-13 | Crash during write recoverable via journal replay |
| AC-14 | Data integrity verified on startup (SHA-256) |
| AC-15 | Log rotation produces daily gzipped files, ≤ 30 days retained |
| AC-16 | No secrets in renderer process or log files |
| AC-17 | Auto-update download resumes after network interruption |
| AC-18 | Forced update blocks app when version < `min_supported` |
| AC-19 | All CI gates pass before release |
| AC-20 | Desktop artifact ≤ 120 MB per platform |

---

## 10. Implementation Timeline

| Phase | Deliverables | Duration |
|-------|-------------|----------|
| 1 | Signing infrastructure (CI secrets + scripts) | Week 1-2 |
| 2 | Auto-update client + manifest pipeline | Week 3-4 |
| 3 | Security hardening (sandbox, CSP, IPC) | Week 5-6 |
| 4 | Resilience (journaling, integrity, logs) | Week 7-8 |
| 5 | Test suite (10 files) + CI matrix | Week 9-10 |
| 6 | Pen test + external audit | Week 11 |

---

*End of Spec 013 — TRACERA-SPEC-013 v2.0*
