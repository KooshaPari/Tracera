"""Tests for observability tracing initialization guards."""

from typing import Any, Never

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from tracertm.observability import tracing


def test_init_tracing_returns_existing_tracer(monkeypatch: Any) -> None:
    tracer = trace.get_tracer("test-existing")
    monkeypatch.setattr(tracing, "_tracer", tracer)
    monkeypatch.setattr(tracing, "_exporter_available", False)

    result = tracing.init_tracing(service_name="test")

    assert result is tracer


def test_get_tracer_initializes_once(monkeypatch: Any) -> None:
    monkeypatch.setattr(tracing, "_tracer", None)
    monkeypatch.setattr(tracing, "_exporter_available", False)

    first = tracing.get_tracer()
    second = tracing.get_tracer()

    assert first is second


def test_init_tracing_skips_overriding_existing_provider(monkeypatch: Any) -> None:
    monkeypatch.setattr(tracing, "_tracer", None)
    monkeypatch.setattr(tracing, "_exporter_available", True)
    monkeypatch.setattr(trace, "get_tracer_provider", TracerProvider)

    def _fail_set_provider(_provider: Any) -> Never:
        msg = "set_tracer_provider should not be called when provider exists"
        raise AssertionError(msg)

    monkeypatch.setattr(trace, "set_tracer_provider", _fail_set_provider)

    tracer = tracing.init_tracing(service_name="test-skip")

    assert tracer is not None
