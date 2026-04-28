"""
Index backends for Vector-Kit.
"""

from pheno.vector.backends.base import IndexBackend

# Optional backend imports - only available if dependencies are installed
__all__ = ["IndexBackend"]

try:
    from pheno.vector.backends.pgvector import PgVectorBackend
    __all__.append("PgVectorBackend")
except ImportError:
    PgVectorBackend = None

try:
    from pheno.vector.backends.lancedb import LanceDBBackend
    __all__.append("LanceDBBackend")
except ImportError:
    LanceDBBackend = None
