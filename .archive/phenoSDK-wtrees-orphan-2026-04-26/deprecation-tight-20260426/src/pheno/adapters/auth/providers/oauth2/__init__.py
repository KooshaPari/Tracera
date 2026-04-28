"""
OAuth2 providers for the ``pheno`` authentication adapters.
"""

from .auth0 import Auth0Provider
from .authkit import AuthKitProvider
from .generic import OAuth2GenericProvider

__all__ = [
    "Auth0Provider",
    "AuthKitProvider",
    "OAuth2GenericProvider",
]
