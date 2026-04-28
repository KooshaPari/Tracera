"""
Adapter registry utilities that layer framework-specific features on top of
the core registry implementation.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import asdict, replace
from typing import Any

from pheno.core.registry.adapters import (
    AdapterRegistry,
    AdapterType,
    get_adapter_registry,
)

from .base import (
    AbstractionBand,
    AbstractionValue,
    AdapterConfig,
    AdapterContext,
    BaseAdapter,
    describe_abstraction_level,
    normalize_abstraction_level,
)

MetadataMapping = MutableMapping[str, Any]


class FrameworkAdapterRegistry:
    """
    High-level registry that annotates adapters with abstraction metadata.

    It composes the core registry while exposing helper APIs that operate on
    framework primitives.
    """

    def __init__(self, registry: AdapterRegistry | None = None):
        self._registry = registry or get_adapter_registry()

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register(
        self,
        *,
        adapter_type: AdapterType,
        adapter_class: type[BaseAdapter],
        name: str | None = None,
        config: AdapterConfig | None = None,
        abstraction_level: AbstractionValue | None = None,
        description: str = "",
        capabilities: Sequence[str] | None = None,
        tags: Sequence[str] | None = None,
        fixed_parameters: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        replace_existing: bool = False,
        singleton: bool = True,
        auto_start: bool = True,
    ) -> None:
        """Register a framework adapter."""

        entry_name = name or adapter_class.__name__.lower()

        base_config = config or AdapterConfig(
            name=entry_name,
            abstraction_level=abstraction_level or 0.5,
            capabilities=capabilities or getattr(adapter_class, "CAPABILITIES", ()),
            fixed_parameters=fixed_parameters or {},
            notes=description,
        )

        level = abstraction_level or base_config.abstraction_level
        normalized_level = normalize_abstraction_level(level)
        taxonomy_band = describe_abstraction_level(normalized_level)

        merged_metadata: MetadataMapping = {
            "abstraction_level": normalized_level,
            "abstraction_band": taxonomy_band.label,
            "description": description,
            "capabilities": list(base_config.capabilities),
            "tags": list(tags or getattr(adapter_class, "TAGS", [])),
            "fixed_parameters": dict(base_config.fixed_parameters),
            "auto_start": auto_start,
        }
        if metadata:
            merged_metadata.update(metadata)
        merged_metadata["default_config"] = asdict(base_config)

        factory = self._build_factory(
            adapter_class=adapter_class,
            base_config=base_config,
            auto_start=auto_start,
        )

        self._registry.register_adapter(
            adapter_type=adapter_type,
            name=entry_name,
            adapter_class=adapter_class,
            metadata=merged_metadata,
            replace=replace_existing,
            factory=factory,
            singleton=singleton,
        )

    def _build_factory(
        self,
        *,
        adapter_class: type[BaseAdapter],
        base_config: AdapterConfig,
        auto_start: bool,
    ) -> Callable[..., BaseAdapter]:
        def factory(
            *,
            config: AdapterConfig | None = None,
            context: AdapterContext | None = None,
            overrides: Mapping[str, Any] | None = None,
        ) -> BaseAdapter:
            cfg = config or base_config
            if overrides:
                cfg = replace(
                    cfg,
                    fixed_parameters={**cfg.fixed_parameters, **overrides},
                )
            adapter = adapter_class(config=cfg, context=context)
            if auto_start:
                adapter.start()
            return adapter

        return factory

    # ------------------------------------------------------------------ #
    # Lookup helpers
    # ------------------------------------------------------------------ #
    def get_underlying(self) -> AdapterRegistry:
        return self._registry

    def classify(self, name: str, adapter_type: AdapterType) -> AbstractionBand:
        entry = self._registry._adapters[adapter_type][name]  # type: ignore[attr-defined]
        level = entry.metadata.get("abstraction_level")
        if level is None:
            raise KeyError(f"No abstraction metadata for adapter '{name}'.")
        return describe_abstraction_level(float(level))

    def list_by_band(
        self,
        adapter_type: AdapterType,
        *,
        minimum: AbstractionValue | None = None,
        maximum: AbstractionValue | None = None,
    ) -> list[str]:
        names = self._registry.list_adapters(adapter_type)
        filtered: list[str] = []
        for name in names:
            entry = self._registry._adapters[adapter_type][name]  # type: ignore[attr-defined]
            level = entry.metadata.get("abstraction_level")
            if level is None:
                continue
            if minimum is not None and level < minimum:
                continue
            if maximum is not None and level > maximum:
                continue
            filtered.append(name)
        return filtered

    # ------------------------------------------------------------------ #
    # Pass-through
    # ------------------------------------------------------------------ #
    def __getattr__(self, item: str) -> Any:
        return getattr(self._registry, item)


_framework_registry: FrameworkAdapterRegistry | None = None


def get_framework_registry() -> FrameworkAdapterRegistry:
    global _framework_registry
    if _framework_registry is None:
        _framework_registry = FrameworkAdapterRegistry()
    return _framework_registry


get_registry = get_framework_registry

__all__ = [
    "AdapterRegistry",
    "AdapterType",
    "FrameworkAdapterRegistry",
    "get_adapter_registry",
    "get_framework_registry",
    "get_registry",
]
