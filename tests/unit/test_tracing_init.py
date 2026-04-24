import logging
from typing import Any

from tracertm.observability import tracing


def test_init_tracing_idempotent(caplog: Any) -> None:
    tracing._tracer = None
    tracing._tracing_initialized = False
    tracing._tracing_init_calls = 0

    with caplog.at_level(logging.WARNING):
        first = tracing.init_tracing()
        second = tracing.init_tracing()

    assert first is second
    assert any("init_tracing called more than once" in record.message for record in caplog.records)
