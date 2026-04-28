"""Compatibility interface for database operations.

Historically, the atoms codebase exposed a ``DatabasePort`` abstract base
class.  During the pheno-sdk consolidation the richer database APIs moved to
``pheno.database``.  This module provides a light-weight alias so existing
imports like ``from application.ports import DatabasePort`` continue to
resolve to the primary database abstraction exposed by the SDK.
"""

from __future__ import annotations

from pheno.database.adapters.base import DatabaseAdapter

# NOTE:
# Rather than duplicate the full legacy abstraction (which largely mirrors the
# modern ``DatabaseAdapter`` contract), we surface the adapter directly.  This
# keeps type hints intact for projects that still reference DatabasePort while
# centralising the implementation in the pheno database layer.
DatabasePort = DatabaseAdapter

__all__ = ["DatabasePort"]
