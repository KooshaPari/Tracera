"""
Foundational primitives for the pheno adapter framework.

The abstractions defined here follow hexagonal architecture principles:
adapters mediate between domain ports and external technologies while
remaining explicit about their abstraction level on the 0.01 → 0.99 scale.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping, Sequence

AbstractionValue = float


@dataclass(frozen=True, slots=True)
class AbstractionBand:
    """Taxonomy entry describing a slice of the abstraction spectrum."""

    lower: AbstractionValue
    upper: AbstractionValue
    label: str
    summary: str
    primary_concerns: str

    def contains(self, value: AbstractionValue) -> bool:
        return self.lower <= value <= self.upper

    def clamp(self, value: AbstractionValue) -> AbstractionValue:
        return max(self.lower, min(self.upper, value))


ABSTRACTION_TAXONOMY: tuple[AbstractionBand, ...] = (
    AbstractionBand(
        lower=0.01,
        upper=0.15,
        label="0.01 – 0.15 Direct Mapping",
        summary="Minimal indirection; mirrors hardware or raw API contracts.",
        primary_concerns="Latency, protocol fidelity, vendor quirks.",
    ),
    AbstractionBand(
        lower=0.16,
        upper=0.35,
        label="0.16 – 0.35 Protocol Wrapper",
        summary="Adds life-cycle handling and error translation, keeps call shape intact.",
        primary_concerns="Connection pooling, retries, diagnostics.",
    ),
    AbstractionBand(
        lower=0.36,
        upper=0.55,
        label="0.36 – 0.55 Service Orchestration",
        summary="Introduces policy, composition, and cross-cutting concerns.",
        primary_concerns="Policy injection, resilience, observability hooks.",
    ),
    AbstractionBand(
        lower=0.56,
        upper=0.75,
        label="0.56 – 0.75 Domain-Aware Adapter",
        summary="Shapes payloads for domain ports and enforces domain contracts.",
        primary_concerns="Domain translation, canonical models, invariants.",
    ),
    AbstractionBand(
        lower=0.76,
        upper=0.99,
        label="0.76 – 0.99 Plug-and-Play",
        summary="Preconfigured adapters with safe defaults and opinionated flows.",
        primary_concerns="Operational guardrails, golden paths, compliance.",
    ),
)


def normalize_abstraction_level(level: AbstractionValue) -> AbstractionValue:
    """Clamp and round to the supported 0.01 → 0.99 scale."""
    if level < 0.0 or level > 1.0:
        raise ValueError("Abstraction level must be between 0.0 and 1.0 inclusive.")
    if level < 0.01:
        return 0.01
    if level > 0.99:
        return 0.99
    return round(level, 2)


def describe_abstraction_level(level: AbstractionValue) -> AbstractionBand:
    """Return the taxonomy band that best describes the supplied level."""
    normalized = normalize_abstraction_level(level)
    for band in ABSTRACTION_TAXONOMY:
        if band.contains(normalized):
            return band
    return ABSTRACTION_TAXONOMY[-1]


@dataclass(slots=True)
class AdapterContext:
    """
    Context object passed into adapters when they are materialised.

    Keeps domain-side ports separated from infrastructure concerns.
    """

    inbound_port: PrimaryPort | None = None
    outbound_port: SecondaryPort | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
    environment: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AdapterConfig:
    """Configuration payload recognised by all adapters."""

    name: str
    abstraction_level: AbstractionValue = 0.5
    capabilities: Sequence[str] = ()
    fixed_parameters: Mapping[str, Any] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "abstraction_level",
            normalize_abstraction_level(self.abstraction_level),
        )


@runtime_checkable
class PrimaryPort(Protocol):
    """Inbound port: driven by the outside world towards the domain."""

    def handle(self, payload: Any, **kwargs: Any) -> Any:
        ...


@runtime_checkable
class SecondaryPort(Protocol):
    """Outbound port: driven by the domain towards infrastructure."""

    def execute(self, payload: Any, **kwargs: Any) -> Any:
        ...


class AdapterError(RuntimeError):
    """Raised when adapter initialisation or execution fails."""


class BaseAdapter(ABC):
    """
    Base class for all concrete adapters.

    Each adapter bridges a domain port with a technology-specific implementation
    and advertises its abstraction level so orchestration can select the right
    fit for a given deployment.
    """

    def __init__(self, config: AdapterConfig, context: AdapterContext | None = None):
        self.config = config
        self.context = context or AdapterContext()
        band = describe_abstraction_level(self.config.abstraction_level)
        self.taxonomy_band = band

    @property
    def abstraction_level(self) -> AbstractionValue:
        return self.config.abstraction_level

    @abstractmethod
    def start(self) -> None:
        """Initialise network connections, pools, or session state."""

    @abstractmethod
    def invoke(self, payload: Any, **kwargs: Any) -> Any:
        """Execute adapter logic."""

    def stop(self) -> None:
        """Gracefully tear down resources."""

    def describe(self) -> dict[str, Any]:
        """Return metadata used by the registry for diagnostics."""
        return {
            "name": self.config.name,
            "abstraction_level": self.abstraction_level,
            "band": self.taxonomy_band.label,
            "capabilities": list(self.config.capabilities),
            "notes": self.config.notes,
        }


class StatelessAdapter(BaseAdapter):
    """Convenience base for adapters that do not manage explicit lifecycle."""

    def start(self) -> None:  # pragma: no cover - trivial default
        return None

    def stop(self) -> None:  # pragma: no cover - trivial default
        return None
