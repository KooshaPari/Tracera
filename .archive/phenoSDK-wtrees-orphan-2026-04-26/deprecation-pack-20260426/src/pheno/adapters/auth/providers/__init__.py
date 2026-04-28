"""
Authentication providers for the ``pheno`` adapters namespace.
"""

from .oauth2 import Auth0Provider, AuthKitProvider, OAuth2GenericProvider
from .registry import (
    ProviderRegistry,
    create_provider,
    get_registry,
    register_provider,
)

__all__ = [
    "Auth0Provider",
    "AuthKitProvider",
    "OAuth2GenericProvider",
    "ProviderRegistry",
    "create_provider",
    "get_registry",
    "register_provider",
]
