# HexaKit Residual Advisories Cookbook (post lockfile-regen)

**Context:** HexaKit had 48 alerts. Mass `cargo update` lockfile-regen cleared 6 (PR #102 + #103). Residual: **42** alerts at start of session, dropped to 18 after R6 audit-fix on npm side. Remaining 18 are Rust-only manifest-bound advisories.

## Diagnosis recipe per residual

```bash
# 1. List open alerts
gh api repos/KooshaPari/HexaKit/dependabot/alerts --paginate \
  --jq '.[] | select(.state=="open") | {pkg: .dependency.package.name, ver: .dependency.package.version, sev: .security_advisory.severity}'

# 2. For each pkg: find what direct dep holds it
cd /tmp/HexaKit-clone
cargo tree --invert <pkg> --target all | head -10

# 3. Check if direct dep has a newer version that doesn't pull <pkg>
cargo search <direct-dep-name> | head -3

# 4. Surgical bump:
cargo update -p <direct-dep>@<old-ver> --precise <new-ver>
```

## Common residual classes (HexaKit-specific)
1. **rustls-webpki 0.101.7** — pinned by older `rustls 0.21.x`; needs rustls workspace bump to 0.23+.
2. **inventory 0.1.x** — held by transitive linkme dependents; v0.2 is breaking.
3. **time 0.1.x** — old chrono/serde combos; likely already addressed.

## Strategy
- Open one PR per major bump (separates rustls bump from time bump).
- Do NOT bundle into one big "cargo update --aggressive" PR — increases breakage surface.
- Test `cargo build --workspace` locally before pushing.

## Pre-commit gate
HexaKit has `HOOKS_SKIP=1` env var convention — DON'T use unless absolutely necessary; document in commit message if you do.
