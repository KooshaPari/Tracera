"""
Authentication adapters and registries for the ``pheno`` package.
"""

from pheno.core.registry import (
    ProviderRegistry,
    get_provider_registry,
)

from .mfa.registry import (
    MFAAdapterRegistry,
    get_mfa_registry,
    register_mfa_adapter,
)

__all__ = [
    "MFAAdapterRegistry",
    "ProviderRegistry",
    "get_mfa_registry",
    "get_provider_registry",
    "register_mfa_adapter",
]
