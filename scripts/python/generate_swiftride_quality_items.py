#!/usr/bin/env python3
"""Generate 570+ Quality & Compliance items for SwiftRide project.

Generates:
- 60 quality_gate items
- 70 code_standard items
- 80 performance_benchmark items
- 50 sla items
- 150 bug items
- 90 technical_debt items
- 70 refactoring_opportunity items
"""

import asyncio
import sys
import uuid
from datetime import UTC, datetime
from typing import Any

import asyncpg

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"
DATABASE_URL = "postgresql://tracertm:tracertm_password@localhost:5432/tracertm"


class SwiftRideQualityGenerator:
    """SwiftRideQualityGenerator."""

    def __init__(self, conn: asyncpg.Connection) -> None:
        """Initialize."""
        self.conn = conn
        self.project_id = PROJECT_ID
        self.created_items = {
            "quality_gate": [],
            "code_standard": [],
            "performance_benchmark": [],
            "sla": [],
            "bug": [],
            "technical_debt": [],
            "refactoring_opportunity": [],
        }

    async def insert_item(
        self,
        title: str,
        item_type: str,
        description: str,
        status: str = "todo",
        priority: int = 3,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Insert item and track by type."""
        item_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        await self.conn.execute(
            """
            INSERT INTO items (
                id, project_id, title, type, description, status,
                priority, metadata, tags, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            item_id,
            self.project_id,
            title,
            item_type,
            description,
            status,
            priority,
            metadata or {},
            tags or [],
            now,
            now,
        )

        self.created_items[item_type].append({"id": item_id, "title": title, "tags": tags or []})
        return item_id

    async def generate_all(self) -> None:
        """Generate all quality items."""
        await self.generate_quality_gates()
        await self.generate_code_standards()
        await self.generate_performance_benchmarks()
        await self.generate_slas()
        await self.generate_bugs()
        await self.generate_technical_debt()
        await self.generate_refactoring_opportunities()

        sum(len(items) for items in self.created_items.values())
        for _item_type, _items in self.created_items.items():
            pass

    # Import the data generation methods
    async def generate_quality_gates(self) -> None:
        """60 quality gate items."""
        gates_data = __import__("swiftride_data_quality_gates", fromlist=["QUALITY_GATES"])
        quality_gates = getattr(gates_data, "QUALITY_GATES", [])
        for gate in quality_gates:
            await self.insert_item(**gate, item_type="quality_gate", status="active")

    async def generate_code_standards(self) -> None:
        """70 code standard items."""
        standards_data = __import__("swiftride_data_code_standards", fromlist=["CODE_STANDARDS"])
        code_standards = getattr(standards_data, "CODE_STANDARDS", [])
        for standard in code_standards:
            await self.insert_item(**standard, item_type="code_standard", status="active")

    async def generate_performance_benchmarks(self) -> None:
        """80 performance benchmark items."""
        benchmarks_data = __import__("swiftride_data_performance", fromlist=["BENCHMARKS"])
        benchmarks = getattr(benchmarks_data, "BENCHMARKS", [])
        for benchmark in benchmarks:
            await self.insert_item(**benchmark, item_type="performance_benchmark", status="active")

    async def generate_slas(self) -> None:
        """50 SLA items."""
        sla_data = __import__("swiftride_data_slas", fromlist=["SLAS"])
        slas = getattr(sla_data, "SLAS", [])
        for sla in slas:
            await self.insert_item(**sla, item_type="sla", status="active")

    async def generate_bugs(self) -> None:
        """150 bug items."""
        bug_data = __import__("swiftride_data_bugs", fromlist=["BUGS"])
        bugs = getattr(bug_data, "BUGS", [])
        for bug in bugs:
            await self.insert_item(**bug, item_type="bug")

    async def generate_technical_debt(self) -> None:
        """90 technical debt items."""
        debt_data = __import__("swiftride_data_tech_debt", fromlist=["TECHNICAL_DEBT"])
        technical_debt = getattr(debt_data, "TECHNICAL_DEBT", [])
        for debt in technical_debt:
            await self.insert_item(**debt, item_type="technical_debt")

    async def generate_refactoring_opportunities(self) -> None:
        """70 refactoring opportunity items."""
        refactor_data = __import__("swiftride_data_refactoring", fromlist=["REFACTORING"])
        refactoring = getattr(refactor_data, "REFACTORING", [])
        for refactor in refactoring:
            await self.insert_item(**refactor, item_type="refactoring_opportunity")


async def main() -> None:
    """Main."""
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        generator = SwiftRideQualityGenerator(conn)
        await generator.generate_all()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
