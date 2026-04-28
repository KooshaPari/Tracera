"""
API routes for Pheno SDK REST API.
"""

from .configurations import router as configurations_router
from .deployments import router as deployments_router
from .services import router as services_router
from .users import router as users_router

__all__ = [
    "configurations_router",
    "deployments_router",
    "services_router",
    "users_router",
]
