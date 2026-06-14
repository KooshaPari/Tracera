"""Trace-link domain model (Artifact, Requirement, TraceLink)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class ArtifactKind(str, Enum):
    REQUIREMENT = "Requirement"
    DESIGN = "Design"
    RATIONALE = "Rationale"
    CODE = "Code"
    TEST = "Test"
    EVIDENCE = "Evidence"


class RequirementStatus(str, Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    DEPRECATED = "Deprecated"


class TraceLinkType(str, Enum):
    IMPLEMENTS = "IMPLEMENTS"
    VERIFIES = "VERIFIES"
    DUPLICATES = "DUPLICATES"
    SATISFIES = "SATISFIES"
    DERIVES_FROM = "DERIVES_FROM"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    REFINES = "REFINES"


@dataclass
class Artifact:
    id: UUID
    project_id: UUID
    kind: ArtifactKind
    title: str
    description: str | None = None
    external_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Requirement(Artifact):
    status: RequirementStatus = RequirementStatus.DRAFT
    priority: str | None = None
    rationale: str | None = None
    acceptance_criteria: list[str] = field(default_factory=list)
    verification_method: str | None = None


@dataclass
class TraceLink:
    project_id: UUID
    source_artifact_id: UUID
    target_artifact_id: UUID
    link_type: TraceLinkType
    confidence: float = 1.0
    rationale: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": str(self.project_id),
            "source_artifact_id": str(self.source_artifact_id),
            "target_artifact_id": str(self.target_artifact_id),
            "link_type": self.link_type.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "metadata": self.metadata,
            "id": str(self.id) if self.id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraceLink:
        return cls(
            project_id=UUID(data["project_id"]),
            source_artifact_id=UUID(data["source_artifact_id"]),
            target_artifact_id=UUID(data["target_artifact_id"]),
            link_type=TraceLinkType(data["link_type"]),
            confidence=float(data.get("confidence", 1.0)),
            rationale=data.get("rationale"),
            metadata=dict(data.get("metadata") or {}),
            id=UUID(data["id"]) if data.get("id") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
