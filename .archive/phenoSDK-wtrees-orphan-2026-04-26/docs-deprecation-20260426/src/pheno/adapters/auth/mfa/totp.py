"""
TOTP (time-based one-time password) MFA adapter for the ``pheno`` namespace.
"""

from __future__ import annotations

import time

from pheno.domain.auth.types import MFAContext, MFAMethod
from pheno.ports.auth.providers import MFAAdapter


class TOTPAdapter(MFAAdapter):
    """
    Minimal TOTP adapter placeholder.
    """

    def __init__(self, name: str, config: dict[str, object]):
        super().__init__(name, config)
        self.issuer = config.get("issuer", "Pheno Auth")
        self.algorithm = config.get("algorithm", "sha1")
        self.digits = config.get("digits", 6)
        self.period = config.get("period", 30)
        self.window = config.get("window", 1)

    def supports_method(self, method: MFAMethod) -> bool:
        return method == MFAMethod.TOTP

    async def send_code(self, context: MFAContext) -> str:
        return f"totp_challenge_{context.user_id}_{int(time.time())}"

    async def verify_code(self, code: str, context: MFAContext) -> bool:
        if not code or len(code) != self.digits:
            return False
        return code.isdigit()

    async def cleanup(self, context: MFAContext) -> None:
        return


__all__ = ["TOTPAdapter"]
