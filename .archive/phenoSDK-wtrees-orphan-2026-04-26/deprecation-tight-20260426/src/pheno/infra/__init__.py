"""
Infrastructure utilities and helper registrations.
"""

from . import utils
from .container import (
    get_container,
    register_default_infrastructure,
    run_container_health_checks,
)
from .service_infra import ServiceInfraManager

# Legacy compatibility - KInfra is now ServiceInfraManager
KInfra = ServiceInfraManager

__all__ = [
    "KInfra",  # Legacy compatibility
    "ServiceInfraManager",
    "get_container",
    "register_default_infrastructure",
    "run_container_health_checks",
]
