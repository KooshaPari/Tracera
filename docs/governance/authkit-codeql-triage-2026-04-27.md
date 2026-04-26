# AuthKit CodeQL Critical Alert Triage — 2026-04-27

**Repo:** `KooshaPari/AuthKit` (archived=false, default=main)
**Scope:** 26 open critical alerts, all CodeQL Rust.
**Method:** API-only (`gh api code-scanning/alerts`); no clones.

## Single-Rule Cluster

All 26 alerts share one rule:

- **Rule:** `rust/hard-coded-cryptographic-value`
- **Message:** "This hard-coded value is used as a password."
- **Scan commit:** `b3cabd6` (paths since reorganized; alerts persist on legacy paths)

## File Distribution

| File | Count | Category | Verdict |
|------|------:|----------|---------|
| `tests/integration_tests.rs` | 22 | Test code | False positive |
| `benches/benchmarks.rs` | 2 | Bench code | False positive |
| `src/adapters/hashers.rs` (lines 82, 90) | 2 | `#[cfg(test)]` block — verified via Contents API | False positive |

`src/adapters/hashers.rs` lines 82 & 90 sit inside `mod tests` (`Argon2Hasher`/`BcryptHasher` round-trip tests using literal `"password123"`).

## Classification

- **False-positive cluster (test/bench/`#[cfg(test)]`):** 26/26
- **Real-issue candidates:** 0
- **Vendor/third-party:** 0

## Suggested Bulk Dismissal

All 26 alerts (numbers 1–26 confirmed for the two src/ alerts; full list available via `--paginate`) are eligible for:

```
state=dismissed
dismissed_reason=false positive
dismissed_comment="Hard-coded test fixtures in test/bench code (incl. #[cfg(test)] in src/adapters/hashers.rs); not production secrets."
```

Recommended path filter for future scans: add `paths-ignore: [tests/**, benches/**]` to CodeQL workflow, or annotate test modules with `// lgtm[rust/hard-coded-cryptographic-value]` suppressions with justification.

**DO NOT auto-dismiss — user triage required per protocol.**
