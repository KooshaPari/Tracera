"""
Detector adapters.
"""

from .detect_secrets_adapter import run_detect_secrets
from .entropy import scan_entropy
from .trufflehog_adapter import run_trufflehog

__all__ = [
    "run_detect_secrets",
    "run_trufflehog",
    "scan_entropy",
]
