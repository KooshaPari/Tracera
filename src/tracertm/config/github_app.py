"""GitHub App configuration and JWT token generation."""

import os
import time

import jwt
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class GitHubAppConfig:
    """GitHub App configuration."""

    def __init__(
        self,
        app_id: str | None = None,
        private_key: str | None = None,
        webhook_secret: str | None = None,
    ) -> None:
        """Initialize GitHub App configuration.

        Args:
            app_id: Optional GitHub App id (defaults to env).
            private_key: Optional PEM private key (defaults to env).
            webhook_secret: Optional webhook secret for signature verification (defaults to env).
        """
        self.app_id = app_id or os.environ.get("GITHUB_APP_ID", "")
        self.private_key = private_key or os.environ.get("GITHUB_APP_PRIVATE_KEY", "")
        self.webhook_secret = webhook_secret or os.environ.get("GITHUB_APP_WEBHOOK_SECRET", "")

    def is_configured(self) -> bool:
        """Check if GitHub App is configured."""
        return bool(self.app_id and self.private_key)

    def get_installation_url(self, state: str | None = None) -> str:
        """Generate GitHub App installation URL."""
        base_url = "https://github.com/apps"
        app_slug = os.environ.get("GITHUB_APP_SLUG", "")
        if not app_slug:
            msg = "GITHUB_APP_SLUG is required"
            raise ValueError(msg)

        url = f"{base_url}/{app_slug}/installations/new"
        if state:
            url += f"?state={state}"
        return url

    def generate_jwt_token(self) -> str:
        """Generate a JWT token for GitHub App authentication."""
        if not self.app_id or not self.private_key:
            msg = "GitHub App ID and private key are required"
            raise ValueError(msg)

        # Parse private key
        try:
            private_key = load_pem_private_key(
                self.private_key.encode() if isinstance(self.private_key, str) else self.private_key,
                password=None,
            )
        except Exception as e:
            msg = f"Invalid private key: {e}"
            raise ValueError(msg) from e

        # Generate JWT
        now = int(time.time())
        payload = {
            "iat": now - 60,  # Issued at time (60 seconds in the past for clock skew)
            "exp": now + (10 * 60),  # Expires in 10 minutes
            "iss": self.app_id,  # Issuer (GitHub App ID)
        }

        return jwt.encode(payload, private_key, algorithm="RS256")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        import hashlib
        import hmac

        if not self.webhook_secret:
            return False

        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        # GitHub sends signature as "sha256=<hex>"
        signature = signature.removeprefix("sha256=")

        return hmac.compare_digest(expected_signature, signature)


def get_github_app_config() -> GitHubAppConfig:
    """Get GitHub App configuration from environment."""
    return GitHubAppConfig()
