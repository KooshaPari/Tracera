# Dependabot Residual-Advisory Playbook (phenotype-org)
**Date:** 2026-04-27
**Context:** After mass lockfile-regen, ~30% of advisories remain. These are NOT clearable by `cargo update`/`npm update --package-lock-only`/`uv lock --upgrade` alone.

## Diagnosis classes

### 1. Yanked transitive holds upstream version pin
**Signature:** `cargo update` reports "Locking 0 packages" but advisory persists.
**Cause:** A direct dep pins to ^X.Y where the patched version is in X.(Y+N) — semver-incompatible.
**Fix:** Bump the parent dep's manifest version requirement.
```bash
cargo tree --invert <vulnerable-pkg> | head -5  # find parent
# Then bump that parent in Cargo.toml.
```

### 2. peerDependency override conflicts (npm)
**Signature:** `npm audit fix --force` reports "Override for X conflicts with direct dependency".
**Cause:** Manual `overrides` in package.json blocks the audit-fix bump.
**Fix:** Remove or update the override; if intentional (security pin), document in CHANGELOG.

### 3. Submodule URL config block
**Signature:** Clone fails with "no URL configured for submodule X".
**Cause:** `.gitmodules` has stale entry without `url=`.
**Fix:** Either set the URL or `git rm --cached` the submodule entirely.

### 4. Workspace-bound version (Cargo workspace)
**Signature:** Workspace member's Cargo.toml uses `workspace = true` for the vulnerable dep, but root workspace [workspace.dependencies] still points to old version.
**Fix:** Bump in the root workspace [workspace.dependencies] table.

### 5. Lock file at root, but advisory in nested package
**Signature:** `cargo update` at root succeeds but nested-crate advisory persists.
**Cause:** Nested member's Cargo.lock is separate (`[workspace] resolver=2` not enforced).
**Fix:** Run `cargo update` from each crate's directory.

## Aggressive fallback: `npm audit fix --force`
Use when normal regen fails. **Risks:**
- May install breaking semver-major versions of direct deps.
- Verify build passes locally before merging.
- Avoid on production-critical npm packages without owner review.

## Surgical bump: `cargo update --precise`
For one specific advisory:
```bash
cargo update -p <crate> --precise <version>
```
This locks to a single version without disturbing other deps.

## When to abandon
- Advisory severity LOW + transitive 5+ levels deep → archive as accepted risk.
- Advisory in dev/test-only dep → annotate `cargo-deny.toml` with allow.
- Advisory in optional feature flag → annotate or strip the feature.

## Tooling
- `cargo tree --invert <pkg>` — find what holds a transitive.
- `cargo audit` — manual rescan.
- `npm ls <pkg>` — find why a transitive is installed.
- GitHub Contents API — `.github/dependabot.yml` to add target-branch + ignore rules.
