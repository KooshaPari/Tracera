"""
Push notification based MFA adapter for the ``pheno`` namespace.
"""

from __future__ import annotations

from pheno.domain.auth.types import MFAContext, MFAMethod
from pheno.ports.auth.providers import MFAAdapter


class PushNotificationAdapter(MFAAdapter):
    """
    Minimal push notification adapter placeholder.
    """

    def __init__(self, name: str, config: dict[str, object]):
        super().__init__(name, config)
        self.api_key = config.get("api_key")
        self.app_id = config.get("app_id")
        self.provider = config.get("provider", "fcm")
        self.webhook_url = config.get("webhook_url")

    def supports_method(self, method: MFAMethod) -> bool:
        return method == MFAMethod.PUSH

    async def send_code(self, context: MFAContext) -> str:
        return f"push_challenge_{context.user_id}"

    async def verify_code(self, code: str, context: MFAContext) -> bool:
        if not code:
            return False
        return code.lower() in {"approve", "yes", "1", "true"}

    async def cleanup(self, context: MFAContext) -> None:
        return


PushAdapter = PushNotificationAdapter

__all__ = ["PushAdapter", "PushNotificationAdapter"]
