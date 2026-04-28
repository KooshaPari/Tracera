"""
Email based MFA adapter for the ``pheno`` namespace.
"""

from __future__ import annotations

from pheno.domain.auth.types import MFAContext, MFAMethod
from pheno.ports.auth.providers import MFAAdapter


class EmailMFAAdapter(MFAAdapter):
    """
    Simple email MFA adapter placeholder.
    """

    def __init__(self, name: str, config: dict[str, object]):
        super().__init__(name, config)
        self.smtp_host = config.get("smtp_host")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_username = config.get("smtp_username")
        self.smtp_password = config.get("smtp_password")
        self.from_email = config.get("from_email")
        self.template = config.get("template", "Your MFA code is: {code}")

    def supports_method(self, method: MFAMethod) -> bool:
        return method == MFAMethod.EMAIL

    async def send_code(self, context: MFAContext) -> str:
        return f"email_challenge_{context.user_id}"

    async def verify_code(self, code: str, context: MFAContext) -> bool:
        return bool(code and len(code) >= 4 and code.isdigit())

    async def cleanup(self, context: MFAContext) -> None:
        return


EmailAdapter = EmailMFAAdapter

__all__ = ["EmailAdapter", "EmailMFAAdapter"]
