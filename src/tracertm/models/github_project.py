"""GitHub Project model for linking TraceRTM projects to GitHub Projects v2."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin, generate_uuid
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from tracertm.models.project import Project


class GitHubProject(Base, TimestampMixin):
    """GitHub Project model.

    Links a TraceRTM project to a GitHub Project v2, which is inherently tied to a repository.
    """

    __tablename__ = "github_projects"
    __table_args__: tuple[Index, ...] = (
        Index("ix_github_projects_project", "project_id"),
        Index("ix_github_projects_repo", "github_repo_id"),
        Index("ix_github_projects_github_project", "github_project_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # GitHub repository info
    github_repo_id: Mapped[int] = mapped_column(nullable=False, index=True)
    github_repo_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    github_repo_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # GitHub Project v2 info
    github_project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    github_project_number: Mapped[int] = mapped_column(nullable=False)

    # Sync configuration
    auto_sync: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sync_config: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Relationships
    project: Mapped[Project] = relationship("Project")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GitHubProject(id={self.id!r}, project_id={self.project_id!r}, github_project_id={self.github_project_id!r})>"
