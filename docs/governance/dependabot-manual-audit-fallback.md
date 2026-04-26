# Manual Dependabot Audit Fallback

When GitHub's Dependabot API is unavailable or not enabled, use native package manager auditing tools.

## Quick Reference Table

| Repository | Primary Stack | Audit Command | Lock File |
|------------|---------------|---------------|-----------|
| **BytePort** | (detect via `ls src/`) | TBD | `Cargo.lock`, `package-lock.json`, or `go.mod` |
| **AgilePlus** | Rust (monorepo) | `cargo audit` | `Cargo.lock` |
| **hwLedger** | Rust + Swift | `cargo audit` + `swift package show-dependencies` | `Cargo.lock` |

---

## Step 1: Detect Repository Stack

### BytePort
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/BytePort
find . -maxdepth 2 \( -name "Cargo.toml" -o -name "package.json" -o -name "go.mod" -o -name "requirements.txt" \) | head -5
```

### AgilePlus
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
find . -maxdepth 2 -name "Cargo.toml" | wc -l
# Should find multiple (monorepo)
```

### hwLedger
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/hwLedger
ls -la src/ | head
ls -la Sources/ 2>/dev/null | head  # Swift
```

---

## Step 2: Run Native Audits

### Rust (Cargo)
```bash
cd /path/to/repo
cargo audit --deny warnings  # Fail on warnings
cargo audit fix --allow-dirty  # Auto-fix if safe
```

**Output interpretation:**
- `0 vulnerabilities`: ✓ safe
- `N vulnerabilities`: list each with severity (CRITICAL, HIGH, MEDIUM, LOW)
- Fixed via `cargo update`: commit Cargo.lock changes

### Node.js (npm/pnpm)
```bash
cd /path/to/repo
npm audit  # or pnpm audit
npm audit fix  # or pnpm audit --fix
```

### Go
```bash
cd /path/to/repo
go list -u -m all | grep -v "go: "  # Show outdated
govulncheck ./...  # Security audit (requires Go 1.18+)
```

### Python
```bash
cd /path/to/repo
pip-audit --desc  # Show descriptions
pip-audit --fix   # Auto-upgrade safe packages
```

---

## Step 3: Commit & Document

After running manual audits:

```bash
git add Cargo.lock package-lock.json go.mod requirements.txt
git commit -m "chore(deps): audit and upgrade dependencies

- Ran: cargo audit, npm audit, go list
- Fixed: [list specifics, e.g., 'openssl patch 1.1.1w → 1.1.1x']
- Residuals: [any CRITICAL/HIGH not auto-fixed]

Co-Authored-By: Claude Code Agent <noreply@anthropic.com>"
```

---

## Step 4: Upstream (Dependabot API Check)

Once audits are complete, confirm Dependabot is enabled:

```bash
gh api repos/KooshaPari/BytePort \
  --jq '.security_and_analysis | {
    secret_scanning: .secret_scanning,
    secret_scanning_non_provider_patterns: .secret_scanning_non_provider_patterns,
    dependabot_security_updates: .dependabot_security_updates,
    dependabot_alerts: .dependabot_alerts
  }'
```

If any field is `null` or `disabled`, enable via Settings.

---

## Playbook: Enable Dependabot in GitHub UI

1. Go to **https://github.com/KooshaPari/{repo}/settings/security_analysis**
2. Under "Code security and analysis":
   - Toggle **Dependabot alerts** → ON
   - Toggle **Dependabot security updates** → ON (optional but recommended)
3. Wait 15–30 min for initial scan
4. Re-run `gh api repos/KooshaPari/{repo}/dependabot/alerts`

---

## Known Limitations

- **Dependabot API 404**: Indicates Dependabot not enabled or repo is archived
- **Swift/iOS**: No native GitHub Dependabot support; use `swift package show-dependencies` + manual review
- **Monorepo (AgilePlus)**: `cargo audit` runs workspace-wide; filter output by workspace member name if needed
- **Disk constraint (25Gi)**: Avoid running `cargo build` during audit; `cargo audit` is metadata-only

---

**Updated**: 2026-04-26  
**Status**: Fallback ready pending Dependabot re-enablement
