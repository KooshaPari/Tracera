"""HashiCorp Vault client for TracerTM secrets management."""

from .client import VaultClient, VaultError

__all__ = ["VaultClient", "VaultError"]
