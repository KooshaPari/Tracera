"""
SMS based MFA adapter for the ``pheno`` namespace.
"""

from __future__ import annotations

from pheno.domain.auth.types import MFAContext, MFAMethod
from pheno.ports.auth.providers import MFAAdapter


class SMSMFAAdapter(MFAAdapter):
    """
    Minimal SMS MFA adapter placeholder.
    """

    def __init__(self, name: str, config: dict[str, object]):
        super().__init__(name, config)
        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")
        self.from_number = config.get("from_number")
        self.provider = config.get("provider", "twilio")

    def supports_method(self, method: MFAMethod) -> bool:
        return method == MFAMethod.SMS

    async def send_code(self, context: MFAContext) -> str:
        return f"sms_challenge_{context.user_id}"

    async def verify_code(self, code: str, context: MFAContext) -> bool:
        return bool(code and len(code) >= 4 and code.isdigit())

    async def cleanup(self, context: MFAContext) -> None:
        return


SMSAdapter = SMSMFAAdapter

__all__ = ["SMSAdapter", "SMSMFAAdapter"]
