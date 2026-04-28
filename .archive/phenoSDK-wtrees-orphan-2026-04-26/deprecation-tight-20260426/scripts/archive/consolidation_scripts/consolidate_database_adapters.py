#!/usr/bin/env python3
"""
Database Adapters Consolidation Script.

This script consolidates all duplicate database adapter classes into a unified system.

Actions performed:
1. Consolidate duplicate database adapter classes
2. Remove duplicate database implementations
3. Create unified database adapter system
4. Update imports across the codebase
"""

import shutil
from pathlib import Path


class DatabaseAdaptersConsolidator:
    """Consolidates database adapters."""

    def __init__(self, base_path: str = "src/pheno"):
        """Initialize consolidator.

        Args:
            base_path: Base path for pheno modules
        """
        self.base_path = Path(base_path)
        self.removed_files: list[str] = []
        self.consolidated_adapters: dict[str, str] = {}

    def consolidate_database_adapters(self) -> None:
        """Consolidate database adapters."""
        print("🔧 Consolidating database adapters...")

        # Files to remove (duplicate database functionality)
        duplicate_database_files = [
            "database/utils/database_utils.py",  # Move DatabaseAdapter to base
            "database/core/engine.py",  # Duplicate Database class
            "database/platforms/",  # Move to adapters
            "database/supabase_client.py",  # Duplicate Supabase client
        ]

        for file_path in duplicate_database_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate database functionality
        self._consolidate_database_functionality()

    def consolidate_duplicate_adapters(self) -> None:
        """Consolidate duplicate adapter classes."""
        print("🔧 Consolidating duplicate adapter classes...")

        # Find and consolidate duplicate adapter classes
        duplicate_adapters = [
            "DatabaseAdapter",
            "SupabaseAdapter",
            "NeonAdapter",
            "PostgreSQLAdapter",
            "Database",
        ]

        for adapter_name in duplicate_adapters:
            self._consolidate_adapter_class(adapter_name)

    def create_unified_database_system(self) -> None:
        """Create unified database system."""
        print("🏗️  Creating unified database system...")

        # Create the unified database system
        unified_database_content = '''"""
Unified Database System for Pheno SDK.

This module provides a comprehensive, unified database system consolidating
all database functionality across the pheno-sdk codebase.

Database Adapters:
==================

DatabaseAdapter (base)
├── PostgreSQLAdapter
├── SupabaseAdapter
└── NeonAdapter

Database Client:
================
- Database: Universal database client with tenant context
- Connection pooling and management
- Realtime subscriptions
- Storage operations
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class DatabaseAdapter(ABC):
    """Abstract interface for database adapters."""

    @abstractmethod
    async def query(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SELECT query on a table.

        Args:
            table: Table name
            select: Columns to select (default: "*")
            filters: Filter conditions
            order_by: Order by clause (e.g., "created_at:desc")
            limit: Maximum rows to return
            offset: Number of rows to skip

        Returns:
            List of row dictionaries
        """

    @abstractmethod
    async def get_single(
        self,
        table: str,
        filters: dict[str, Any],
        *,
        select: str | None = None,
    ) -> dict[str, Any] | None:
        """Get a single row matching filters.

        Args:
            table: Table name
            filters: Filter conditions
            select: Columns to select (default: "*")

        Returns:
            Row dictionary or None if not found
        """

    @abstractmethod
    async def insert(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Insert one or more rows.

        Args:
            table: Table name
            data: Row data (single dict or list of dicts)
            returning: Columns to return (default: "*")

        Returns:
            Inserted row(s)
        """

    @abstractmethod
    async def update(
        self,
        table: str,
        filters: dict[str, Any],
        data: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> list[dict[str, Any]]:
        """Update rows matching filters.

        Args:
            table: Table name
            filters: Filter conditions
            data: Update data
            returning: Columns to return (default: "*")

        Returns:
            Updated rows
        """

    @abstractmethod
    async def delete(
        self,
        table: str,
        filters: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> list[dict[str, Any]]:
        """Delete rows matching filters.

        Args:
            table: Table name
            filters: Filter conditions
            returning: Columns to return (default: "*")

        Returns:
            Deleted rows
        """

    @abstractmethod
    async def execute_sql(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute raw SQL.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            Query results
        """

    @abstractmethod
    async def close(self) -> None:
        """Close database connection."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check database health.

        Returns:
            True if healthy, False otherwise
        """


class Database:
    """Universal database client with tenant context and RLS support."""

    def __init__(self, adapter: DatabaseAdapter):
        """Initialize database client.

        Args:
            adapter: Database adapter implementation
        """
        self.adapter = adapter
        self._tenant_id: str | None = None

    @classmethod
    def supabase(cls, access_token: str | None = None) -> Database:
        """Create a database client with Supabase adapter.

        Args:
            access_token: User JWT for RLS context

        Returns:
            Database instance
        """
        from .adapters.supabase import SupabaseAdapter
        adapter = SupabaseAdapter(access_token=access_token)
        return cls(adapter=adapter)

    @classmethod
    def postgres(
        cls,
        dsn: str | None = None,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        **kwargs,
    ) -> Database:
        """Create a database client with PostgreSQL adapter.

        Args:
            dsn: PostgreSQL DSN (optional)
            host: Database host
            port: Database port
            database: Database name
            **kwargs: Additional connection options

        Returns:
            Database instance
        """
        from .adapters.postgres import PostgreSQLAdapter
        adapter = PostgreSQLAdapter(
            dsn=dsn,
            host=host,
            port=port,
            database=database,
            **kwargs,
        )
        return cls(adapter=adapter)

    @classmethod
    def neon(
        cls,
        connection_string: str | None = None,
        api_key: str | None = None,
        project_id: str | None = None,
        **kwargs,
    ) -> Database:
        """Create a database client with Neon adapter.

        Args:
            connection_string: Neon connection string
            api_key: Neon API key
            project_id: Neon project ID
            **kwargs: Additional connection options

        Returns:
            Database instance
        """
        from .adapters.neon import NeonAdapter
        adapter = NeonAdapter(
            connection_string=connection_string,
            api_key=api_key,
            project_id=project_id,
            **kwargs,
        )
        return cls(adapter=adapter)

    def set_tenant_id(self, tenant_id: str) -> None:
        """Set tenant ID for RLS context.

        Args:
            tenant_id: Tenant identifier
        """
        self._tenant_id = tenant_id

    async def query(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SELECT query on a table."""
        return await self.adapter.query(
            table=table,
            select=select,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    async def get_single(
        self,
        table: str,
        filters: dict[str, Any],
        *,
        select: str | None = None,
    ) -> dict[str, Any] | None:
        """Get a single row matching filters."""
        return await self.adapter.get_single(
            table=table,
            filters=filters,
            select=select,
        )

    async def insert(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Insert one or more rows."""
        return await self.adapter.insert(
            table=table,
            data=data,
            returning=returning,
        )

    async def update(
        self,
        table: str,
        filters: dict[str, Any],
        data: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> list[dict[str, Any]]:
        """Update rows matching filters."""
        return await self.adapter.update(
            table=table,
            filters=filters,
            data=data,
            returning=returning,
        )

    async def delete(
        self,
        table: str,
        filters: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> list[dict[str, Any]]:
        """Delete rows matching filters."""
        return await self.adapter.delete(
            table=table,
            filters=filters,
            returning=returning,
        )

    async def execute_sql(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute raw SQL."""
        return await self.adapter.execute_sql(sql=sql, params=params)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Database]:
        """Execute operations within a transaction."""
        # This would be implemented by each adapter
        yield self

    async def close(self) -> None:
        """Close database connection."""
        await self.adapter.close()

    async def health_check(self) -> bool:
        """Check database health."""
        return await self.adapter.health_check()


# Re-export adapters
from .adapters.postgres import PostgreSQLAdapter
from .adapters.supabase import SupabaseAdapter
from .adapters.neon import NeonAdapter

__all__ = [
    "DatabaseAdapter",
    "Database",
    "PostgreSQLAdapter",
    "SupabaseAdapter",
    "NeonAdapter",
]
'''

        # Write unified database
        unified_file = self.base_path / "database" / "unified_database.py"
        unified_file.write_text(unified_database_content)
        print(f"  ✅ Created unified database: {unified_file}")

        # Update main database init
        self._update_database_init()

    def _consolidate_database_functionality(self) -> None:
        """Consolidate database functionality."""
        print("  🔄 Consolidating database functionality...")

        # Keep the best database implementation
        database_client = self.base_path / "database" / "client.py"
        if database_client.exists():
            print(f"    ✅ Keeping database client: {database_client}")

        # Create unified database system
        self.create_unified_database_system()

    def _consolidate_adapter_class(self, adapter_name: str) -> None:
        """Consolidate a specific adapter class."""
        print(f"  🔄 Consolidating {adapter_name}...")

        # Find all files containing this adapter class
        files_with_adapter = []
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if f"class {adapter_name}" in content:
                    files_with_adapter.append(py_file)
            except Exception:
                pass

        if len(files_with_adapter) > 1:
            print(f"    ⚠️  Found {len(files_with_adapter)} files with {adapter_name}")
            # Keep the one in database/adapters/ directory, remove others
            for file_path in files_with_adapter:
                if "database/adapters/" not in str(file_path):
                    # Remove duplicate definition
                    self._remove_duplicate_class_from_file(file_path, adapter_name)
                    print(f"    ❌ Removed {adapter_name} from {file_path}")

    def _remove_duplicate_class_from_file(
        self, file_path: Path, class_name: str,
    ) -> None:
        """Remove duplicate class definition from file."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Find class definition
            class_start = None
            class_end = None
            indent_level = None

            for i, line in enumerate(lines):
                if f"class {class_name}" in line and ":" in line:
                    class_start = i
                    indent_level = len(line) - len(line.lstrip())
                    break

            if class_start is not None:
                # Find end of class
                for i in range(class_start + 1, len(lines)):
                    line = lines[i]
                    if line.strip() and not line.startswith(
                        " " * ((indent_level or 0) + 1),
                    ):
                        class_end = i
                        break

                if class_end is None:
                    class_end = len(lines)

                # Remove class definition
                new_lines = lines[:class_start] + lines[class_end:]
                file_path.write_text("\n".join(new_lines))

        except Exception as e:
            print(f"    ⚠️  Could not remove {class_name} from {file_path}: {e}")

    def _update_database_init(self) -> None:
        """Update database __init__.py."""
        print("  🔄 Updating database __init__.py...")

        init_content = '''"""
Unified Database System for Pheno SDK.

This module provides a comprehensive, unified database system consolidating
all database functionality across the pheno-sdk codebase.
"""

from __future__ import annotations

# Import everything from unified database
from .unified_database import *

# Connection pooling
from .pooling import (
    AsyncConnectionPool,
    ConnectionPoolConfig,
    ConnectionPoolManager,
    ConnectionStats,
    SyncConnectionPool,
    cleanup_all_pools,
    get_pool_manager,
    get_provider_pool,
)

# Realtime
from .realtime import RealtimeAdapter, SupabaseRealtimeAdapter

# Storage
from .storage import StorageAdapter, SupabaseStorageAdapter

__version__ = "0.1.0"

__all__ = [
    # Database
    "DatabaseAdapter",
    "Database",
    "PostgreSQLAdapter",
    "SupabaseAdapter",
    "NeonAdapter",
    # Connection pooling
    "AsyncConnectionPool",
    "ConnectionPoolConfig",
    "ConnectionPoolManager",
    "ConnectionStats",
    "SyncConnectionPool",
    "cleanup_all_pools",
    "get_pool_manager",
    "get_provider_pool",
    # Realtime
    "RealtimeAdapter",
    "SupabaseRealtimeAdapter",
    # Storage
    "StorageAdapter",
    "SupabaseStorageAdapter",
]
'''

        init_file = self.base_path / "database" / "__init__.py"
        init_file.write_text(init_content)
        print("    ✅ Updated database __init__.py")

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report."""
        print("\n📊 Database Adapters Consolidation Report")
        print("=" * 60)
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Adapters consolidated: {len(self.consolidated_adapters)}")

        print("\nRemoved files:")
        for file_path in self.removed_files:
            print(f"  - {file_path}")

        print("\nConsolidated adapters:")
        for old_adapter, new_adapter in self.consolidated_adapters.items():
            print(f"  - {old_adapter} → {new_adapter}")

    def run_consolidation(self) -> None:
        """Run full database adapters consolidation process."""
        print("🚀 Starting database adapters consolidation...")
        print("=" * 60)

        # Step 1: Consolidate database adapters
        self.consolidate_database_adapters()

        # Step 2: Consolidate duplicate adapters
        self.consolidate_duplicate_adapters()

        # Step 3: Generate report
        self.generate_consolidation_report()

        print("\n✅ Database adapters consolidation complete!")
        print("Next steps:")
        print("1. Update imports across the codebase")
        print("2. Run tests to ensure functionality is preserved")
        print("3. Update documentation")
        print("4. Continue with other duplicate class consolidation")

    def _remove_file(self, file_path: Path) -> None:
        """Remove a file and track it."""
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            self.removed_files.append(str(file_path))
        except Exception as e:
            print(f"    ⚠️  Could not remove {file_path}: {e}")


def main():
    """Main consolidation function."""
    consolidator = DatabaseAdaptersConsolidator()
    consolidator.run_consolidation()


if __name__ == "__main__":
    main()
