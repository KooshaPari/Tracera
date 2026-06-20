"""Specification models for TraceRTM.

Provides comprehensive models for:
- Architecture Decision Records (ADR) - design decisions with rationale
- Contracts - formal specifications with pre/post-conditions and state machines
- Features - BDD feature specifications with Gherkin support
- Scenarios - BDD scenario specifications with step definitions
- Step Definitions - Gherkin step implementations and patterns
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_specification_uuid() -> str:
    """Generate a UUID string for specification ID."""
    return str(uuid.uuid4())


# ============================================================================
# ADR (Architecture Decision Record) Enums and Models
# ============================================================================


class ADRStatus(StrEnum):
    """Valid ADR statuses."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class ADR(Base, TimestampMixin):
    """Architecture Decision Record model.

    ADRs document significant architecture decisions with context, rationale,
    and consequences. They serve as architecture documentation and decision
    history for the project.
    """

    __tablename__ = "adrs"

    __table_args__ = (
        Index("idx_adrs_project_status", "project_id", "status"),
        Index("idx_adrs_project_adr_number", "project_id", "adr_number"),
        Index("idx_adrs_status", "status"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_specification_uuid)
    adr_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ADRStatus.PROPOSED.value, index=True)

    # ADR Content - 7-part format
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    consequences: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_drivers: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    considered_options: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSONType,
        nullable=True,
    )  # [{"option": "...", "pros": "...", "cons": "..."}]

    # Traceability
    related_requirements: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    related_adrs: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    supersedes: Mapped[str | None] = mapped_column(String(50), nullable=True)
    superseded_by: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Governance
    compliance_score: Mapped[float | None] = mapped_column(default=0.0)
    stakeholders: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Dates
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Flexible metadata
    adr_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize instance with metadata field aliasing.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        if "metadata" in kwargs and "adr_metadata" not in kwargs:
            kwargs["adr_metadata"] = kwargs.pop("metadata")
        if "metadata_" in kwargs and "adr_metadata" not in kwargs:
            kwargs["adr_metadata"] = kwargs.pop("metadata_")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "adr_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "adr_metadata"
        super().__setattr__(name, value)

    @property
    def metadata_(self) -> dict[str, object]:
        """Alias property for accessing metadata.

        Returns:
            The metadata dictionary.
        """
        return self.adr_metadata

    @metadata_.setter
    def metadata_(self, value: dict[str, object]) -> None:
        self.adr_metadata = value

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ADR(id={self.id!r}, number={self.adr_number!r}, title={self.title!r})>"


# ============================================================================
# Contract Enums and Models
# ============================================================================


class ContractType(StrEnum):
    """Types of contracts."""

    INTERFACE = "interface"
    COMPONENT = "component"
    SERVICE = "service"
    SYSTEM = "system"
    INTEGRATION = "integration"
    DATABASE = "database"


class ContractStatus(StrEnum):
    """Valid contract statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Contract(Base, TimestampMixin):
    """Contract/Formal Specification model.

    Contracts specify behavior through preconditions, postconditions, invariants,
    and state machines. Supports executable specifications and verification.
    """

    __tablename__ = "contracts"

    __table_args__ = (
        Index("idx_contracts_project_status", "project_id", "status"),
        Index("idx_contracts_project_type", "project_id", "contract_type"),
        Index("idx_contracts_contract_number", "project_id", "contract_number"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_specification_uuid)
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    contract_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ContractType.INTERFACE.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ContractStatus.DRAFT.value, index=True)

    # Contract Specifications
    preconditions: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    postconditions: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    invariants: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # State Machine
    states: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    transitions: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSONType,
        nullable=True,
    )  # [{"from": "state1", "to": "state2", "condition": "...", "action": "..."}]

    # Executable Specification
    executable_spec: Mapped[str | None] = mapped_column(Text, nullable=True)
    spec_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_result: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    verification_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Governance
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Classification
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Flexible metadata
    contract_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize instance with metadata field aliasing.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        if "metadata" in kwargs and "contract_metadata" not in kwargs:
            kwargs["contract_metadata"] = kwargs.pop("metadata")
        if "metadata_" in kwargs and "contract_metadata" not in kwargs:
            kwargs["contract_metadata"] = kwargs.pop("metadata_")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "contract_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "contract_metadata"
        super().__setattr__(name, value)

    @property
    def metadata_(self) -> dict[str, object]:
        """Alias property for accessing metadata.

        Returns:
            The metadata dictionary.
        """
        return self.contract_metadata

    @metadata_.setter
    def metadata_(self, value: dict[str, object]) -> None:
        self.contract_metadata = value

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Contract(id={self.id!r}, number={self.contract_number!r}, title={self.title!r})>"


# ============================================================================
# Feature Enums and Models
# ============================================================================


class FeatureStatus(StrEnum):
    """Valid feature statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Feature(Base, TimestampMixin):
    """BDD Feature model.

    Features represent user stories in Gherkin format with background steps
    and traceability to requirements and ADRs.
    """

    __tablename__ = "features"

    __table_args__ = (
        Index("idx_features_project_status", "project_id", "status"),
        Index("idx_features_project_number", "project_id", "feature_number"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_specification_uuid)
    feature_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User Story Format
    as_a: Mapped[str | None] = mapped_column(String(255), nullable=True)
    i_want: Mapped[str | None] = mapped_column(String(255), nullable=True)
    so_that: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Feature Definition
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=FeatureStatus.DRAFT.value, index=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Traceability
    related_requirements: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    related_adrs: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Governance
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Flexible metadata
    feature_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    scenarios = relationship(
        "tracertm.models.specification.Scenario",
        back_populates="feature",
        cascade="all, delete-orphan",
        viewonly=True,
    )

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize instance with metadata field aliasing.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        if "metadata" in kwargs and "feature_metadata" not in kwargs:
            kwargs["feature_metadata"] = kwargs.pop("metadata")
        if "metadata_" in kwargs and "feature_metadata" not in kwargs:
            kwargs["feature_metadata"] = kwargs.pop("metadata_")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "feature_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "feature_metadata"
        super().__setattr__(name, value)

    @property
    def metadata_(self) -> dict[str, object]:
        """Alias property for accessing metadata.

        Returns:
            The metadata dictionary.
        """
        return self.feature_metadata

    @metadata_.setter
    def metadata_(self, value: dict[str, object]) -> None:
        self.feature_metadata = value

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Feature(id={self.id!r}, number={self.feature_number!r}, name={self.name!r})>"


# ============================================================================
# Scenario Enums and Models
# ============================================================================


class ScenarioStatus(StrEnum):
    """Valid scenario statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


# Association table for Scenario to TestCase many-to-many relationship
scenario_test_case_association = Table(
    "scenario_test_case_association",
    Base.metadata,
    Column("scenario_id", String(255), ForeignKey("scenarios.id", ondelete="CASCADE")),
    Column("test_case_id", String(255), ForeignKey("test_cases.id", ondelete="CASCADE")),
    Index("idx_scenario_test_case", "scenario_id", "test_case_id"),
)


class Scenario(Base, TimestampMixin):
    """BDD Scenario model.

    Scenarios represent concrete examples in Gherkin format (Given-When-Then).
    Can be outline scenarios with multiple examples and link to test cases.
    """

    __tablename__ = "scenarios"

    __table_args__ = (
        Index("idx_scenarios_feature_status", "feature_id", "status"),
        Index("idx_scenarios_scenario_number", "scenario_number"),
        Index("idx_scenarios_status", "status"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_specification_uuid)
    scenario_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    feature_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    gherkin_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Gherkin Steps
    background: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    given_steps: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    when_steps: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    then_steps: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)

    # Scenario Outline
    is_outline: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    examples: Mapped[list[dict[str, object]] | None] = mapped_column(
        JSONType,
        nullable=True,
    )  # [{columns: [...], rows: [...]}]

    # Classification
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ScenarioStatus.DRAFT.value, index=True)

    # Traceability
    requirement_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    test_case_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Flexible metadata
    # Execution Statistics
    pass_rate: Mapped[float | None] = mapped_column(default=0.0)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Governance
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Flexible metadata
    scenario_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    feature = relationship(
        "tracertm.models.specification.Feature",
        back_populates="scenarios",
        viewonly=True,
    )
    test_cases = relationship(
        "TestCase",
        secondary=scenario_test_case_association,
        backref="scenarios",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize Scenario instance.

        Handles metadata field aliasing for backward compatibility,
        automatically converting 'metadata' and 'metadata_' kwargs
        to 'scenario_metadata'.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        if "metadata" in kwargs and "scenario_metadata" not in kwargs:
            kwargs["scenario_metadata"] = kwargs.pop("metadata")
        if "metadata_" in kwargs and "scenario_metadata" not in kwargs:
            kwargs["scenario_metadata"] = kwargs.pop("metadata_")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """Get attribute value with metadata aliasing.

        Transparently redirects 'metadata' attribute access to 'scenario_metadata'
        for backward compatibility.

        Args:
            name: Attribute name to retrieve.

        Returns:
            Attribute value, with 'metadata' redirected to 'scenario_metadata'.
        """
        if name == "metadata":
            return object.__getattribute__(self, "scenario_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """Set attribute value with metadata aliasing.

        Transparently redirects 'metadata' attribute assignment to 'scenario_metadata'
        for backward compatibility.

        Args:
            name: Attribute name to set.
            value: Value to assign.
        """
        if name == "metadata":
            name = "scenario_metadata"
        super().__setattr__(name, value)

    @property
    def metadata_(self) -> dict[str, object]:
        """Alias property for accessing scenario_metadata.

        Returns:
            The scenario metadata dictionary.
        """
        return self.scenario_metadata

    @metadata_.setter
    def metadata_(self, value: dict[str, object]) -> None:
        self.scenario_metadata = value

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Scenario(id={self.id!r}, number={self.scenario_number!r}, title={self.title!r})>"


# ============================================================================
# Step Definition Enums and Models
# ============================================================================


class StepType(StrEnum):
    """Types of Gherkin steps."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"
    AND = "and"
    BUT = "but"


class StepDefinition(Base, TimestampMixin):
    """Step Definition model.

    Step definitions map Gherkin step text to implementation code.
    Supports regex patterns, parameter extraction, and usage tracking.
    """

    __tablename__ = "step_definitions"

    __table_args__ = (
        Index("idx_step_definitions_type", "step_type"),
        Index("idx_step_definitions_pattern", "pattern"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_specification_uuid)

    # Step Classification
    step_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pattern: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    regex_pattern: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Implementation
    implementation_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    implementation_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Documentation
    documentation: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Tracking
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Flexible metadata
    step_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize StepDefinition instance.

        Handles metadata field aliasing for backward compatibility,
        automatically converting 'metadata' kwargs to 'step_metadata'.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        if "metadata" in kwargs and "step_metadata" not in kwargs:
            kwargs["step_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """Get attribute value with metadata aliasing.

        Transparently redirects 'metadata' attribute access to 'step_metadata'
        for backward compatibility.

        Args:
            name: Attribute name to retrieve.

        Returns:
            Attribute value, with 'metadata' redirected to 'step_metadata'.
        """
        if name == "metadata":
            return object.__getattribute__(self, "step_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """Set attribute value with metadata aliasing.

        Transparently redirects 'metadata' attribute assignment to 'step_metadata'
        for backward compatibility.

        Args:
            name: Attribute name to set.
            value: Value to assign.
        """
        if name == "metadata":
            name = "step_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation of StepDefinition.

        Returns:
            String showing StepDefinition ID, type, and pattern.
        """
        return f"<StepDefinition(id={self.id!r}, type={self.step_type!r}, pattern={self.pattern!r})>"
