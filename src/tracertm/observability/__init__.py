"""Observability module for TraceRTM.

Provides comprehensive APM (Application Performance Monitoring) capabilities including:
- Distributed tracing with OpenTelemetry
- Metrics collection and export
- Database query instrumentation
- HTTP/API request instrumentation
- Custom span decorators
"""

from .tracing import init_tracing, get_tracer, trace_method
from .instrumentation import instrument_app, instrument_database

__all__ = [
    "init_tracing",
    "get_tracer",
    "trace_method",
    "instrument_app",
    "instrument_database",
]
