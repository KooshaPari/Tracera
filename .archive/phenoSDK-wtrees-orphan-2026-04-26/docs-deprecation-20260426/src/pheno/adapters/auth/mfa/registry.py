"""MFA adapter registry for the ``pheno`` namespace.

Provides the same behaviour as ``pheno.auth.mfa.registry`` while the legacy
module remains as a compatibility shim.
"""

from __future__ import annotations

from typing import Any

from pheno.domain.auth.types import ConfigurationError, MFAMethod
from pheno.ports.auth.providers import MFAAdapter


class MFAAdapterRegistry:
    """
    Central in-memory registry for MFA adapters.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, type[MFAAdapter]] = {}
        self._instances: dict[str, MFAAdapter] = {}

    def register_adapter(self, name: str, adapter_class: type[MFAAdapter]) -> None:
        if not issubclass(adapter_class, MFAAdapter):
            raise ValueError("Adapter must inherit from MFAAdapter")
        self._adapters[name] = adapter_class

    def get_adapter_class(self, name: str) -> type[MFAAdapter] | None:
        return self._adapters.get(name)

    def create_adapter(self, name: str, config: dict[str, Any]) -> MFAAdapter:
        adapter_class = self.get_adapter_class(name)
        if not adapter_class:
            raise ConfigurationError(f"MFA adapter '{name}' not found")
        try:
            return adapter_class(name, config)
        except Exception as exc:  # pragma: no cover - adapter failures bubble up
            raise ConfigurationError(f"Failed to create MFA adapter '{name}': {exc}") from exc

    def get_or_create_adapter(self, name: str, config: dict[str, Any]) -> MFAAdapter:
        instance_key = f"{name}:{id(config)}"
        if instance_key not in self._instances:
            self._instances[instance_key] = self.create_adapter(name, config)
        return self._instances[instance_key]

    def list_adapters(self) -> list[str]:
        return list(self._adapters.keys())

    def get_adapters_by_method(self, method: MFAMethod) -> list[str]:
        adapters: list[str] = []
        for name, adapter_class in self._adapters.items():
            try:
                probe = adapter_class(name, {})
            except Exception:
                continue
            if probe.supports_method(method):
                adapters.append(name)
        return adapters

    def unregister_adapter(self, name: str) -> None:
        self._adapters.pop(name, None)
        purge = [key for key in self._instances if key.startswith(f"{name}:")]
        for key in purge:
            self._instances.pop(key, None)

    def clear(self) -> None:
        self._adapters.clear()
        self._instances.clear()


__registry = MFAAdapterRegistry()


def get_registry() -> MFAAdapterRegistry:
    return __registry


def register_adapter(name: str, adapter_class: type[MFAAdapter]) -> None:
    __registry.register_adapter(name, adapter_class)


def create_adapter(name: str, config: dict[str, Any]) -> MFAAdapter:
    return __registry.create_adapter(name, config)


def get_mfa_registry() -> MFAAdapterRegistry:
    """
    Convenience alias for DI wiring.
    """
    return __registry


def register_mfa_adapter(name: str, adapter_class: type[MFAAdapter]) -> None:
    """
    Alias mirroring the legacy function name.
    """
    register_adapter(name, adapter_class)


__all__ = [
    "MFAAdapterRegistry",
    "create_adapter",
    "get_mfa_registry",
    "get_registry",
    "register_adapter",
    "register_mfa_adapter",
]
