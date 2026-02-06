"""Service for managing view types and registry."""

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar


class ViewType(StrEnum):
    """All supported view types."""

    # Core views (Phase 1)
    FEATURE = "FEATURE"
    CODE = "CODE"
    TEST = "TEST"
    REQUIREMENT = "REQUIREMENT"
    DESIGN = "DESIGN"
    DOCUMENTATION = "DOCUMENTATION"
    EPIC = "EPIC"
    ROADMAP = "ROADMAP"

    # UX Views (Phase 2)
    PERSONA = "PERSONA"
    USER_JOURNEY = "USER_JOURNEY"
    USER_FLOW = "USER_FLOW"

    # Technical Views (Phase 2)
    ARCHITECTURE = "ARCHITECTURE"
    SEQUENCE = "SEQUENCE"
    STATE_MACHINE = "STATE_MACHINE"
    PSEUDOCODE = "PSEUDOCODE"

    # Quality Views (Phase 2)
    TEST_RESULTS = "TEST_RESULTS"
    COVERAGE_REPORT = "COVERAGE_REPORT"
    SECURITY_SCAN = "SECURITY_SCAN"
    QUALITY_METRICS = "QUALITY_METRICS"

    # Operations Views (Phase 2)
    DEPLOYMENT = "DEPLOYMENT"
    MONITORING = "MONITORING"
    LOGS = "LOGS"
    ALERT = "ALERT"

    # Additional Views (Phase 2)
    MOCKUP = "MOCKUP"
    DESIGN_SYSTEM = "DESIGN_SYSTEM"
    DATA_MODEL = "DATA_MODEL"
    API_SPEC = "API_SPEC"
    DECISION = "DECISION"
    RISK = "RISK"
    DEPENDENCY = "DEPENDENCY"
    RESOURCE = "RESOURCE"


@dataclass
class ViewMetadata:
    """Metadata for a view type."""

    name: str
    description: str
    icon: str
    color: str
    category: str
    phase: int
    supports_hierarchy: bool = True
    supports_linking: bool = True
    supports_status: bool = True


class ViewRegistryService:
    """Service for managing view types."""

    # View metadata registry
    REGISTRY: ClassVar[dict[ViewType, ViewMetadata]] = {
        # Core views
        ViewType.FEATURE: ViewMetadata(
            name="Feature",
            description="Product features and user stories",
            icon="✨",
            color="blue",
            category="core",
            phase=1,
        ),
        ViewType.CODE: ViewMetadata(
            name="Code",
            description="Source code files and modules",
            icon="💻",
            color="green",
            category="core",
            phase=1,
        ),
        ViewType.TEST: ViewMetadata(
            name="Test",
            description="Test cases and test suites",
            icon="✅",
            color="purple",
            category="core",
            phase=1,
        ),
        ViewType.REQUIREMENT: ViewMetadata(
            name="Requirement",
            description="Business and technical requirements",
            icon="📋",
            color="orange",
            category="core",
            phase=1,
        ),
        ViewType.DESIGN: ViewMetadata(
            name="Design",
            description="Design documents and specifications",
            icon="🎨",
            color="pink",
            category="core",
            phase=1,
        ),
        ViewType.DOCUMENTATION: ViewMetadata(
            name="Documentation",
            description="User and technical documentation",
            icon="📚",
            color="gray",
            category="core",
            phase=1,
        ),
        ViewType.EPIC: ViewMetadata(
            name="Epic",
            description="Large features and initiatives",
            icon="🚀",
            color="red",
            category="core",
            phase=1,
        ),
        ViewType.ROADMAP: ViewMetadata(
            name="Roadmap",
            description="Project roadmap and timeline",
            icon="🗺️",
            color="cyan",
            category="core",
            phase=1,
        ),
        # UX Views
        ViewType.PERSONA: ViewMetadata(
            name="Persona",
            description="User personas and profiles",
            icon="👤",
            color="blue",
            category="ux",
            phase=2,
        ),
        ViewType.USER_JOURNEY: ViewMetadata(
            name="User Journey",
            description="User journey maps",
            icon="🛤️",
            color="blue",
            category="ux",
            phase=2,
        ),
        ViewType.USER_FLOW: ViewMetadata(
            name="User Flow",
            description="User flow diagrams",
            icon="🔄",
            color="blue",
            category="ux",
            phase=2,
        ),
        # Technical Views
        ViewType.ARCHITECTURE: ViewMetadata(
            name="Architecture",
            description="System architecture",
            icon="🏗️",
            color="green",
            category="technical",
            phase=2,
        ),
        ViewType.SEQUENCE: ViewMetadata(
            name="Sequence",
            description="Sequence diagrams",
            icon="📊",
            color="green",
            category="technical",
            phase=2,
        ),
        ViewType.STATE_MACHINE: ViewMetadata(
            name="State Machine",
            description="State machine diagrams",
            icon="⚙️",
            color="green",
            category="technical",
            phase=2,
        ),
        ViewType.PSEUDOCODE: ViewMetadata(
            name="Pseudocode",
            description="Algorithm pseudocode",
            icon="📝",
            color="green",
            category="technical",
            phase=2,
        ),
        # Quality Views
        ViewType.TEST_RESULTS: ViewMetadata(
            name="Test Results",
            description="Test execution results",
            icon="📈",
            color="purple",
            category="quality",
            phase=2,
        ),
        ViewType.COVERAGE_REPORT: ViewMetadata(
            name="Coverage Report",
            description="Code coverage reports",
            icon="📊",
            color="purple",
            category="quality",
            phase=2,
        ),
        ViewType.SECURITY_SCAN: ViewMetadata(
            name="Security Scan",
            description="Security scan results",
            icon="🔒",
            color="purple",
            category="quality",
            phase=2,
        ),
        ViewType.QUALITY_METRICS: ViewMetadata(
            name="Quality Metrics",
            description="Code quality metrics",
            icon="📉",
            color="purple",
            category="quality",
            phase=2,
        ),
        # Operations Views
        ViewType.DEPLOYMENT: ViewMetadata(
            name="Deployment",
            description="Deployment status",
            icon="🚢",
            color="orange",
            category="operations",
            phase=2,
        ),
        ViewType.MONITORING: ViewMetadata(
            name="Monitoring",
            description="System monitoring",
            icon="📡",
            color="orange",
            category="operations",
            phase=2,
        ),
        ViewType.LOGS: ViewMetadata(
            name="Logs",
            description="Application logs",
            icon="📋",
            color="orange",
            category="operations",
            phase=2,
        ),
        ViewType.ALERT: ViewMetadata(
            name="Alert",
            description="Alert definitions",
            icon="🚨",
            color="orange",
            category="operations",
            phase=2,
        ),
        # Additional Views
        ViewType.MOCKUP: ViewMetadata(
            name="Mockup",
            description="UI mockups",
            icon="🖼️",
            color="pink",
            category="design",
            phase=2,
        ),
        ViewType.DESIGN_SYSTEM: ViewMetadata(
            name="Design System",
            description="Design system components",
            icon="🎨",
            color="pink",
            category="design",
            phase=2,
        ),
        ViewType.DATA_MODEL: ViewMetadata(
            name="Data Model",
            description="Data model diagrams",
            icon="🗄️",
            color="cyan",
            category="technical",
            phase=2,
        ),
        ViewType.API_SPEC: ViewMetadata(
            name="API Spec",
            description="API specifications",
            icon="🔌",
            color="cyan",
            category="technical",
            phase=2,
        ),
        ViewType.DECISION: ViewMetadata(
            name="Decision",
            description="Architecture decisions",
            icon="⚖️",
            color="gray",
            category="documentation",
            phase=2,
        ),
        ViewType.RISK: ViewMetadata(
            name="Risk",
            description="Risk assessments",
            icon="⚠️",
            color="red",
            category="operations",
            phase=2,
        ),
        ViewType.DEPENDENCY: ViewMetadata(
            name="Dependency",
            description="Dependency graphs",
            icon="🔗",
            color="cyan",
            category="technical",
            phase=2,
        ),
        ViewType.RESOURCE: ViewMetadata(
            name="Resource",
            description="Resource allocation",
            icon="👥",
            color="orange",
            category="operations",
            phase=2,
        ),
    }

    @classmethod
    def get_view(cls, view_type: ViewType) -> ViewMetadata | None:
        """Get view metadata."""
        return cls.REGISTRY.get(view_type)

    @classmethod
    def list_views(cls, phase: int | None = None, category: str | None = None) -> list[ViewMetadata]:
        """List all views, optionally filtered."""
        views = list(cls.REGISTRY.values())

        if phase:
            views = [v for v in views if v.phase == phase]

        if category:
            views = [v for v in views if v.category == category]

        return views

    @classmethod
    def get_phase_one_views(cls) -> list[ViewMetadata]:
        """Get Phase 1 views."""
        return cls.list_views(phase=1)

    @classmethod
    def get_phase_two_views(cls) -> list[ViewMetadata]:
        """Get Phase 2 views."""
        return cls.list_views(phase=2)

    @classmethod
    def get_views_by_category(cls, category: str) -> list[ViewMetadata]:
        """Get views by category."""
        return cls.list_views(category=category)
