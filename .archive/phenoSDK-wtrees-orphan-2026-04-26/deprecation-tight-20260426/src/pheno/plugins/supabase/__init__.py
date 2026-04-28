"""
Unified entry point for Supabase integrations.
"""

from .auth import SupabaseAuthClient, SupabaseAuthError
from .client import (
    MissingSupabaseConfig,
    cache_stats,
    get_supabase,
    reset_client_cache,
)
from .database import SupabaseAdapter
from .fakes import InMemorySupabaseAuth, InMemorySupabaseClient
from .vector import (
    get_vector_embedding_service,
    get_vector_search_service,
    reset_vector_services,
    vector_provider_status,
)

__all__ = [
    # Testing helpers
    "InMemorySupabaseAuth",
    "InMemorySupabaseClient",
    # Client
    "MissingSupabaseConfig",
    # Database
    "SupabaseAdapter",
    # Auth
    "SupabaseAuthClient",
    "SupabaseAuthError",
    "cache_stats",
    "get_supabase",
    # Vector
    "get_vector_embedding_service",
    "get_vector_search_service",
    "reset_client_cache",
    "reset_vector_services",
    "vector_provider_status",
]
