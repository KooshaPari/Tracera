# INTG-A3 – Secret Scanning Pipeline Specification

**Status:** ✅ Design Complete
**Date:** 2025-10-14
**Owner:** Security & Compliance WG
**Consumers:** Morph security adapters, Router configuration auditing

---

## 1. Purpose

Create a shared secret scanning pipeline under `pheno.security.scanners` that integrates detect-secrets and trufflehog, exposes entropy heuristics, and emits structured findings Morph and Router can consume.

---

## 2. Architecture Overview

```
pheno/security/scanners/
├── __init__.py
├── detectors/
│   ├── detect_secrets_adapter.py
│   ├── trufflehog_adapter.py
│   └── entropy.py
├── models.py
├── pipeline.py
└── suppressions.py
```

- Pipeline orchestrates multiple detectors, consolidates results, applies suppressions, and outputs `SecretFinding` dataclasses.
- Provides both synchronous and async entry points with thread pool offloading.

---

## 3. Data Models

```python
@dataclass(frozen=True)
class SecretFinding:
    detector: Literal["detect-secrets", "trufflehog", "entropy"]
    file_path: Path
    line: int
    context: str
    severity: Literal["low", "medium", "high"]
    entropy: float | None
    fingerprint: str
    tags: set[str]

@dataclass(frozen=True)
class ScanSummary:
    findings: tuple[SecretFinding, ...]
    suppressed: tuple[SecretFinding, ...]
    duration_ms: int
```

---

## 4. Pipeline API

```python
async def scan_paths(
    paths: Iterable[Path],
    *,
    include_patterns: Sequence[str] | None = None,
    exclude_patterns: Sequence[str] | None = None,
    suppression_rules: SuppressionRules | None = None,
    entropy_threshold: float = 4.5,
    telemetry: TelemetryContext | None = None,
) -> ScanSummary:
    """Run combined secret scanners across given paths."""
```

- `SuppressionRules` supports inline comments, global allowlists, and repository-specific configurations.
- Telemetry integrates with `pheno.observability` to track findings count, severity distribution.

---

## 5. Integration Notes

- `detect-secrets` provides baseline detectors; configure via JSON templates under `pheno/security/scanners/detectors/config`.
- `trufflehog` handles high-entropy strings and credential formats; run in `--no-update` mode to avoid network calls by default.
- Entropy heuristics: custom module computing Shannon entropy with adjustable thresholds; flagged findings labelled `"entropy"`.
- Provide CLI wrapper `pheno-security-scan` for local runs (optional).

---

## 6. Performance Targets

- Scan 1k files of mixed sizes within 30s on modern hardware.
- Support incremental scans (hash cache stored in `.pheno/secrets/cache.sqlite`).
- Allow concurrency limit configuration `PHENO_SECURITY_MAX_WORKERS`.

---

## 7. Testing

- Unit tests for data models, suppression logic.
- Integration tests using fixtures from Morph/Router repositories containing synthetic secrets.
- Performance smoke tests measuring runtime and detection accuracy.
- False positive review harness to adjust entropy thresholds.

---

## 8. Deliverables

- [x] Specification (this document).
- [ ] Implementation and tests (future sprint).
- [ ] Documentation for Morph/Router migration (INTG-A6).
- [ ] Security review sign-off before GA.

Approved 2025-10-14.
