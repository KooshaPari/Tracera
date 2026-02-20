"""Database setup script - Initialize database schema.

Usage:
    python scripts/setup_db.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.db_init import init_database
from services import DatabaseService
from services.database import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> bool | None:
    """Main setup function."""
    logger.info("Starting database setup...")

    # Create database service
    config = DatabaseConfig(
        postgres_url="postgresql://mcp_user:mcp_password@localhost/mcp_db",
        memgraph_url="bolt://localhost:7687",
        qdrant_url="http://localhost:6333",
        valkey_url="redis://localhost:6379",
    )

    db_service = DatabaseService(config)

    try:
        # Connect to databases
        logger.info("Connecting to databases...")
        await db_service.connect()
        logger.info("✓ Database connections established")

        # Initialize schema
        logger.info("Initializing database schema...")
        if await init_database(db_service):
            logger.info("✓ Database schema initialized")
        else:
            logger.error("✗ Database schema initialization failed")
            return False

        # Verify schema
        from infrastructure.db_init import DatabaseInitializer

        initializer = DatabaseInitializer(db_service)
        verification = await initializer.verify_schema()

        if verification.get("success"):
            logger.info("✓ Schema verification successful")
            logger.info("  Tables: %s", verification["table_count"])
            logger.info("  Indexes: %s", verification["index_count"])
            logger.info("  Functions: %s", verification["function_count"])
        else:
            logger.error("✗ Schema verification failed")
            return False

        logger.info("✓ Database setup complete!")
        return True

    except Exception as e:
        logger.exception("✗ Setup failed: %s", e)
        return False

    finally:
        # Disconnect
        logger.info("Disconnecting from databases...")
        await db_service.disconnect()
        logger.info("✓ Disconnected")


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
