"""HashiCorp Vault client for TracerTM.

Provides type-safe access to secrets stored in Vault KV v2 engine.
"""

import os
from typing import Any

import hvac  # hvac has no type stubs (third-party limitation)
from pydantic import BaseModel


class VaultError(Exception):
    """Raised when Vault operations fail."""


class DatabaseCredentials(BaseModel):
    """Database connection credentials."""

    url: str
    host: str = ""
    port: str = ""
    user: str = ""
    password: str = ""
    name: str = ""


class RedisCredentials(BaseModel):
    """Redis connection credentials."""

    url: str
    host: str = ""
    port: str = ""


class Neo4jCredentials(BaseModel):
    """Neo4j graph database credentials."""

    uri: str
    user: str
    password: str
    auth: str = ""


class S3Credentials(BaseModel):
    """S3/MinIO storage credentials."""

    endpoint: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    bucket: str = ""
    region: str = "us-east-1"


class WorkOSCredentials(BaseModel):
    """WorkOS authentication credentials."""

    api_key: str = ""
    client_id: str = ""
    redirect_uri: str = ""


class VaultClient:
    """HashiCorp Vault client for TracerTM secrets management.

    Usage:
        client = VaultClient()
        jwt_secret = client.get_jwt_secret()
        db_creds = client.get_database_credentials()
    """

    def __init__(
        self,
        vault_addr: str | None = None,
        vault_token: str | None = None,
        mount_point: str = "secret",
        namespace: str = "tracertm",
    ) -> None:
        """Initialize Vault client.

        Args:
            vault_addr: Vault server address (default: VAULT_ADDR env or http://127.0.0.1:8200)
            vault_token: Vault authentication token (default: VAULT_TOKEN env)
            mount_point: KV secrets engine mount point (default: secret)
            namespace: Secret namespace prefix (default: tracertm)

        Raises:
            VaultError: If Vault connection fails
        """
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self.namespace = namespace

        if not self.vault_token:
            msg = "VAULT_TOKEN environment variable not set"
            raise VaultError(msg)

        try:
            self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

            if not self.client.is_authenticated():
                msg = "Vault authentication failed"
                raise VaultError(msg)

        except Exception as e:
            msg = f"Failed to initialize Vault client: {e}"
            raise VaultError(msg) from e

    def get_secret(self, path: str) -> dict[str, Any]:
        """Retrieve a secret from Vault KV v2.

        Args:
            path: Secret path relative to namespace (e.g., "jwt", "database")

        Returns:
            Dictionary of secret data

        Raises:
            VaultError: If secret retrieval fails
        """
        full_path = f"{self.namespace}/{path}"

        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=full_path, mount_point=self.mount_point)

            if not response or "data" not in response or "data" not in response["data"]:
                msg = f"Secret not found or invalid format: {full_path}"
                raise VaultError(msg)

            return response["data"]["data"]

        except hvac.exceptions.InvalidPath as e:
            msg = f"Secret not found: {full_path}"
            raise VaultError(msg) from e
        except Exception as e:
            msg = f"Failed to read secret {full_path}: {e}"
            raise VaultError(msg) from e

    def get_secret_field(self, path: str, field: str) -> str:
        """Retrieve a specific field from a Vault secret.

        Args:
            path: Secret path
            field: Field name

        Returns:
            Field value as string

        Raises:
            VaultError: If field not found
        """
        data = self.get_secret(path)

        if field not in data:
            msg = f"Field '{field}' not found in secret '{path}'"
            raise VaultError(msg)

        value = data[field]
        if not isinstance(value, str):
            msg = f"Field '{field}' in secret '{path}' is not a string (got {type(value).__name__})"
            raise VaultError(msg)

        return value

    def get_jwt_secret(self) -> str:
        """Retrieve JWT signing secret."""
        return self.get_secret_field("jwt", "secret")

    def get_database_url(self) -> str:
        """Retrieve database connection URL."""
        return self.get_secret_field("database", "url")

    def get_database_credentials(self) -> DatabaseCredentials:
        """Retrieve structured database credentials."""
        data = self.get_secret("database")
        return DatabaseCredentials(**data)

    def get_redis_url(self) -> str:
        """Retrieve Redis connection URL."""
        return self.get_secret_field("redis", "url")

    def get_redis_credentials(self) -> RedisCredentials:
        """Retrieve structured Redis credentials."""
        data = self.get_secret("redis")
        return RedisCredentials(**data)

    def get_neo4j_credentials(self) -> Neo4jCredentials:
        """Retrieve Neo4j connection credentials."""
        data = self.get_secret("neo4j")
        return Neo4jCredentials(**data)

    def get_s3_credentials(self) -> S3Credentials:
        """Retrieve S3/MinIO credentials."""
        data = self.get_secret("s3")
        return S3Credentials(**data)

    def get_workos_credentials(self) -> WorkOSCredentials:
        """Retrieve WorkOS authentication credentials.

        Returns empty credentials if not found (WorkOS is optional).
        """
        try:
            data = self.get_secret("workos")
            return WorkOSCredentials(**data)
        except VaultError:
            return WorkOSCredentials()

    def health_check(self) -> bool:
        """Check Vault connectivity and authentication.

        Returns:
            True if Vault is healthy and authenticated

        Raises:
            VaultError: If health check fails
        """
        try:
            if not self.client.is_authenticated():
                msg = "Not authenticated"
                raise VaultError(msg)

            # Try to read seal status as a health check
            self.client.sys.read_health_status()
        except Exception as e:
            msg = f"Health check failed: {e}"
            raise VaultError(msg) from e
        else:
            return True


def load_config_from_vault() -> dict[str, Any]:
    """Load configuration from Vault (convenience function).

    Returns:
        Dictionary with all credentials

    Raises:
        VaultError: If any credential fails to load
    """
    client = VaultClient()

    return {
        "jwt_secret": client.get_jwt_secret(),
        "database": client.get_database_credentials().model_dump(),
        "redis": client.get_redis_credentials().model_dump(),
        "neo4j": client.get_neo4j_credentials().model_dump(),
        "s3": client.get_s3_credentials().model_dump(),
        "workos": client.get_workos_credentials().model_dump(),
    }
