"""Re-export canonical artifact model from trace_link (shared-core vocabulary)."""

from tracertm.models.trace_link import (
    Artifact,
    ArtifactKind,
    Requirement,
    RequirementStatus,
    TraceLink,
    TraceLinkType,
    VerificationMethod,
)

__all__ = [
    "Artifact",
    "ArtifactKind",
    "Requirement",
    "RequirementStatus",
    "TraceLink",
    "TraceLinkType",
    "VerificationMethod",
]
