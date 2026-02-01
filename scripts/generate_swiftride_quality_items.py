#!/usr/bin/env python3
"""
Generate 570+ Quality & Compliance items for SwiftRide project.

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
import asyncpg
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any
import sys

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"
DATABASE_URL = "postgresql://tracertm:tracertm_password@localhost:5432/tracertm"

class SwiftRideQualityGenerator:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
        self.project_id = PROJECT_ID
        self.created_items = {
            'quality_gate': [],
            'code_standard': [],
            'performance_benchmark': [],
            'sla': [],
            'bug': [],
            'technical_debt': [],
            'refactoring_opportunity': []
        }

    async def insert_item(self, title: str, item_type: str, description: str,
                         status: str = "todo", priority: int = 3,
                         metadata: Dict[str, Any] = None, tags: List[str] = None) -> str:
        """Insert item and track by type."""
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        await self.conn.execute(
            """
            INSERT INTO items (
                id, project_id, title, type, description, status,
                priority, metadata, tags, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            item_id, self.project_id, title, item_type, description,
            status, priority, metadata or {}, tags or [], now, now
        )

        self.created_items[item_type].append({
            'id': item_id,
            'title': title,
            'tags': tags or []
        })
        return item_id

    async def generate_all(self):
        """Generate all quality items."""
        print("🚀 Generating SwiftRide Quality & Compliance Items\n")

        await self.generate_quality_gates()
        await self.generate_code_standards()
        await self.generate_performance_benchmarks()
        await self.generate_slas()
        await self.generate_bugs()
        await self.generate_technical_debt()
        await self.generate_refactoring_opportunities()

        total = sum(len(items) for items in self.created_items.values())
        print(f"\n✅ Generated {total} total items!")
        for item_type, items in self.created_items.items():
            print(f"   {item_type}: {len(items)}")

    # Import the data generation methods
    async def generate_quality_gates(self):
        """60 quality gate items."""
        print("📋 Quality Gates...")
        gates_data = __import__('swiftride_data_quality_gates', fromlist=['QUALITY_GATES'])
        for gate in gates_data.QUALITY_GATES:
            await self.insert_item(**gate, item_type="quality_gate", status="active")
        print(f"   ✓ {len(gates_data.QUALITY_GATES)} quality gates")

    async def generate_code_standards(self):
        """70 code standard items."""
        print("📐 Code Standards...")
        standards_data = __import__('swiftride_data_code_standards', fromlist=['CODE_STANDARDS'])
        for standard in standards_data.CODE_STANDARDS:
            await self.insert_item(**standard, item_type="code_standard", status="active")
        print(f"   ✓ {len(standards_data.CODE_STANDARDS)} code standards")

    async def generate_performance_benchmarks(self):
        """80 performance benchmark items."""
        print("⚡ Performance Benchmarks...")
        benchmarks_data = __import__('swiftride_data_performance', fromlist=['BENCHMARKS'])
        for benchmark in benchmarks_data.BENCHMARKS:
            await self.insert_item(**benchmark, item_type="performance_benchmark", status="active")
        print(f"   ✓ {len(benchmarks_data.BENCHMARKS)} benchmarks")

    async def generate_slas(self):
        """50 SLA items."""
        print("📊 SLAs...")
        sla_data = __import__('swiftride_data_slas', fromlist=['SLAS'])
        for sla in sla_data.SLAS:
            await self.insert_item(**sla, item_type="sla", status="active")
        print(f"   ✓ {len(sla_data.SLAS)} SLAs")

    async def generate_bugs(self):
        """150 bug items."""
        print("🐛 Bugs...")
        bug_data = __import__('swiftride_data_bugs', fromlist=['BUGS'])
        for bug in bug_data.BUGS:
            await self.insert_item(**bug, item_type="bug")
        print(f"   ✓ {len(bug_data.BUGS)} bugs")

    async def generate_technical_debt(self):
        """90 technical debt items."""
        print("🔧 Technical Debt...")
        debt_data = __import__('swiftride_data_tech_debt', fromlist=['TECHNICAL_DEBT'])
        for debt in debt_data.TECHNICAL_DEBT:
            await self.insert_item(**debt, item_type="technical_debt")
        print(f"   ✓ {len(debt_data.TECHNICAL_DEBT)} technical debt items")

    async def generate_refactoring_opportunities(self):
        """70 refactoring opportunity items."""
        print("♻️  Refactoring Opportunities...")
        refactor_data = __import__('swiftride_data_refactoring', fromlist=['REFACTORING'])
        for refactor in refactor_data.REFACTORING:
            await self.insert_item(**refactor, item_type="refactoring_opportunity")
        print(f"   ✓ {len(refactor_data.REFACTORING)} refactoring opportunities")

async def main():
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        generator = SwiftRideQualityGenerator(conn)
        await generator.generate_all()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
