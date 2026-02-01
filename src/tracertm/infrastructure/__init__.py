"""Infrastructure layer for TraceRTM."""

from tracertm.infrastructure.nats_client import NATSClient
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.feature_flags import (
    FeatureFlagStore,
    FLAG_NATS_EVENTS,
    FLAG_CROSS_BACKEND_CALLS,
    FLAG_SHARED_CACHE,
    FLAG_PYTHON_SPEC_ANALYTICS,
    FLAG_GO_GRAPH_ANALYSIS,
    FLAG_ENHANCED_LOGGING,
    FLAG_METRICS_COLLECTION,
    FLAG_DISTRIBUTED_TRACING,
)

__all__ = [
    "NATSClient",
    "EventBus",
    "FeatureFlagStore",
    "FLAG_NATS_EVENTS",
    "FLAG_CROSS_BACKEND_CALLS",
    "FLAG_SHARED_CACHE",
    "FLAG_PYTHON_SPEC_ANALYTICS",
    "FLAG_GO_GRAPH_ANALYSIS",
    "FLAG_ENHANCED_LOGGING",
    "FLAG_METRICS_COLLECTION",
    "FLAG_DISTRIBUTED_TRACING",
]
