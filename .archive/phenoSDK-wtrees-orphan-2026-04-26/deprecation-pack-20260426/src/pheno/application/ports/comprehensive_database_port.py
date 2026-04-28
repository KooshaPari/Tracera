"""Compatibility alias for the legacy ``ComprehensiveDatabasePort`` name.

Historically, atoms exposed both ``DatabasePort`` and
``ComprehensiveDatabasePort`` symbols that pointed at the same contract.  The
alias remains so downstream projects can continue importing the comprehensive
port without code changes.
"""

from __future__ import annotations

from .database_port import DatabasePort

ComprehensiveDatabasePort = DatabasePort

__all__ = ["ComprehensiveDatabasePort"]
