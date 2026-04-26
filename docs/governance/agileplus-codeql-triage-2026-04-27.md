# AgilePlus CodeQL Critical Alerts Triage — 2026-04-27

**Repo:** KooshaPari/AgilePlus (archived=false)
**Method:** API-only (`gh api .../code-scanning/alerts` + Contents API)
**Scope:** 5 open critical alerts. **No dismissals — inventory only.**

## Inventory

| # | Rule | File | Line | Snippet | Classification |
|---|------|------|------|---------|----------------|
| 55 | rust/hard-coded-cryptographic-value | libs/cipher/src/key_derivation.rs | 100 | `derive_key("password123", …)` (test fn `derive_key_produces_32_bytes`) | TEST FIXTURE |
| 56 | rust/hard-coded-cryptographic-value | libs/cipher/src/key_derivation.rs | 106 | `let salt = b"fixedsalt12345678901234567890"` (test fn `derive_key_with_salt_deterministic`) | TEST FIXTURE |
| 57 | rust/hard-coded-cryptographic-value | libs/cipher/src/key_derivation.rs | 108 | `derive_key_with_salt("password", salt, domain)` | TEST FIXTURE |
| 58 | rust/hard-coded-cryptographic-value | libs/cipher/src/key_derivation.rs | 109 | `derive_key_with_salt("password", salt, domain)` (2nd call, determinism check) | TEST FIXTURE |
| 59 | rust/hard-coded-cryptographic-value | libs/cipher/src/key_derivation.rs | 115 | `hash_password("mysecretpassword")` (test fn `password_hash_verify`) | TEST FIXTURE |

## Classification Summary

- **Real product code:** 0 / 5
- **Test/vendor/.archive:** 5 / 5 (all inside `#[cfg(test)] mod tests` block, lines 100–125)
- **Browser-history / secret-export overlap:** 0 / 5 (no overlap with PR #414 `data/safari/` or `gemini_export.html`)

## Disposition

All 5 criticals are intentional hard-coded test vectors validating Argon2 KDF determinism and password-hash round-trip. Standard CodeQL false-positive pattern for crypto unit tests. **Recommended action (NOT yet taken):** suppress via CodeQL config `paths-ignore` for `**/*` test modules, or add `// lgtm[rust/hard-coded-cryptographic-value]` with FR justification. **DO NOT dismiss without spec linkage.**

## Source

- API: `gh api repos/KooshaPari/AgilePlus/code-scanning/alerts?state=open --paginate`
- Contents: `gh api repos/KooshaPari/AgilePlus/contents/libs/cipher/src/key_derivation.rs?ref=main`
