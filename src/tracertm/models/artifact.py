"""Simplified artifact domain model for traceability core."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Artifact:
    id: str
    kind: str
    title: str
    body: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None