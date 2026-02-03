"""Observability module for TraceRTM.

Provides comprehensive APM (Application Performance Monitoring) capabilities including:
- Distributed tracing with OpenTelemetry
- Metrics collection and export
- Database query instrumentation
- HTTP/API request instrumentation
- Custom span decorators
"""

from .instrumentation import instrument_all, instrument_app, instrument_database
from .tracing import get_tracer, init_tracing, trace_method

__all__ = [
    "get_tracer",
    "init_tracing",
    "instrument_all",
    "instrument_app",
    "instrument_database",
    "trace_method",
]
