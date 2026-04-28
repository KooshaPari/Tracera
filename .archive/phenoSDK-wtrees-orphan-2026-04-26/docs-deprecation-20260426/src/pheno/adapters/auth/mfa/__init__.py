"""
MFA adapters for the ``pheno`` authentication namespace.
"""

from .email import EmailAdapter, EmailMFAAdapter
from .push import PushAdapter, PushNotificationAdapter
from .registry import (
    MFAAdapterRegistry,
    create_adapter,
    get_mfa_registry,
    get_registry,
    register_adapter,
    register_mfa_adapter,
)
from .sms import SMSAdapter, SMSMFAAdapter
from .totp import TOTPAdapter

__all__ = [
    "EmailAdapter",
    "EmailMFAAdapter",
    "MFAAdapterRegistry",
    "PushAdapter",
    "PushNotificationAdapter",
    "SMSAdapter",
    "SMSMFAAdapter",
    "TOTPAdapter",
    "create_adapter",
    "get_mfa_registry",
    "get_registry",
    "register_adapter",
    "register_mfa_adapter",
]
