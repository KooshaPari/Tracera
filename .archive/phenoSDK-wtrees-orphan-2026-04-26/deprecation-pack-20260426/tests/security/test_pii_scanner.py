import types

import pytest

from pheno.security.pii_scanner import PIIScanner, detect_pii, redact_pii


def test_regex_detection_basic():
    scanner = PIIScanner()
    text = "Email john@example.com and SSN 123-45-6789"
    results = scanner.detect(text)
    types_found = {item["type"] for item in results}
    assert {"EMAIL", "SSN"} <= types_found


def test_detect_pii_helper_custom_patterns():
    patterns = {"ZIP": r"\\b\d{5}(?:-\d{4})?\\b"}
    results = detect_pii("Code 30301", patterns=patterns)
    assert results and results[0]["type"] == "ZIP"


def test_redact_pii_with_presidio(monkeypatch):
    class DummyResult:
        def __init__(self, start: int, end: int, entity_type: str, score: float = 0.5):
            self.start = start
            self.end = end
            self.entity_type = entity_type
            self.score = score

    class DummyAnalyzer:
        def analyze(self, text: str, language: str = "en"):
            idx = text.index("secret")
            return [DummyResult(idx, idx + len("secret"), "SECRET", 0.9)]

    scanner = PIIScanner(use_presidio=True, presidio_analyzer=DummyAnalyzer())
    redacted = scanner.redact("this is secret data", show_type=True)
    assert "[SECRET]" in redacted


def test_presidio_optional_dependency_guard(monkeypatch):
    from pheno.security import pii_scanner as module

    monkeypatch.setattr(module, "AnalyzerEngine", None, raising=False)

    with pytest.raises(ImportError):
        PIIScanner(use_presidio=True)


def test_detect_pii_with_presidio_results(monkeypatch):
    class DummyResult:
        def __init__(self, start, end, entity_type="SECRET", score=0.9):
            self.start = start
            self.end = end
            self.entity_type = entity_type
            self.score = score

    class DummyAnalyzer:
        def analyze(self, text: str, language: str = "en"):
            pos = text.index("token")
            return [DummyResult(pos, pos + len("token"))]

    scanner = PIIScanner(use_presidio=True, presidio_analyzer=DummyAnalyzer())
    detections = scanner.detect("api token here")
    assert any(item["type"] == "SECRET" for item in detections)


def test_redact_pii_helper_kwargs(monkeypatch):
    class DummyAnalyzer:
        def analyze(self, text: str, language: str = "en"):
            idx = text.index("data")
            return [types.SimpleNamespace(start=idx, end=idx + 4, entity_type="DATA", score=1.0)]

    redacted = redact_pii(
        "sensitive data", show_type=False, use_presidio=True, presidio_analyzer=DummyAnalyzer(),
    )
    assert "****" in redacted
