"""Self-tracing module for NFR-TRC-012: Evidence emission linking spec→code→test→commit."""

from tracertm.self_tracing.evidence_emitter import EvidenceEmitter
from tracertm.self_tracing.pytest_plugin import TraceabilityPlugin

__all__ = [
    "EvidenceEmitter",
    "TraceabilityPlugin",
]
