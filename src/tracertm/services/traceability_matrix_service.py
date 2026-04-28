"""Traceability matrix generation service for TraceRTM."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


@dataclass
class TraceabilityMatrix:
    """Traceability matrix data structure."""

    project_id: str
    rows: list[dict]  # Source items
    columns: list[dict]  # Target items
    matrix: list[list[str]]  # Link types or empty
    coverage: float  # Percentage of traced items
    total_links: int


class TraceabilityMatrixService:
    """Service for generating traceability matrices.

    Functional Requirements:
    - FR-RPT-007
    - FR-RPT-008

    User Stories:
    - US-MATRIX-001
    - US-MATRIX-002

    Epics:
    - EPIC-007
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def generate_matrix(
        self,
        project_id: str,
        source_view: str | None = None,
        target_view: str | None = None,
        link_types: list[str] | None = None,
    ) -> TraceabilityMatrix:
        """Generate traceability matrix for items.

        Args:
            project_id: Project ID
            source_view: Optional filter for source view
            target_view: Optional filter for target view
            link_types: Optional list of link types to include

        Returns:
            TraceabilityMatrix with matrix data

        Complexity: O(n * m) where n = sources, m = targets
        """
        # Get source items
        source_items = await self.items.get_by_project(project_id)
        if source_view:
            source_items = [i for i in source_items if i.view == source_view]

        # Get target items
        target_items = await self.items.get_by_project(project_id)
        if target_view:
            target_items = [i for i in target_items if i.view == target_view]

        # Get all links
        all_links = await self.links.get_by_project(project_id)

        # Build link map
        link_map: dict[tuple, str] = {}
        for link in all_links:
            # Filter by link types if specified
            if link_types and link.link_type not in link_types:
                continue

            key = (str(link.source_item_id), str(link.target_item_id))
            link_map[key] = link.link_type

        # Build matrix
        matrix: list[list[str]] = []
        traced_count = 0

        for source in source_items:
            row: list[str] = []
            for target in target_items:
                key = (str(source.id), str(target.id))
                if key in link_map:
                    row.append(link_map[key])
                    traced_count += 1
                else:
                    row.append("")
            matrix.append(row)

        # Calculate coverage
        total_cells = len(source_items) * len(target_items)
        coverage = (traced_count / total_cells * 100) if total_cells > 0 else 0

        return TraceabilityMatrix(
            project_id=project_id,
            rows=[
                {
                    "id": str(item.id),
                    "title": item.title,
                    "view": item.view,
                    "type": item.item_type,
                }
                for item in source_items
            ],
            columns=[
                {
                    "id": str(item.id),
                    "title": item.title,
                    "view": item.view,
                    "type": item.item_type,
                }
                for item in target_items
            ],
            matrix=matrix,
            coverage=coverage,
            total_links=traced_count,
        )

    async def export_matrix_csv(
        self,
        matrix: TraceabilityMatrix,
    ) -> str:
        """Export traceability matrix as CSV.

        Args:
            matrix: TraceabilityMatrix to export

        Returns:
            CSV string
        """
        lines = []

        # Header row
        header = ["Source"] + [col["title"] for col in matrix.columns]
        lines.append(",".join(f'"{h}"' for h in header))

        # Data rows
        for i, row_item in enumerate(matrix.rows):
            row = [f'"{row_item["title"]}"']
            for _j, cell in enumerate(matrix.matrix[i]):
                row.append(f'"{cell}"')
            lines.append(",".join(row))

        # Summary
        lines.extend(("", f"Total Links,{matrix.total_links}", f"Coverage,{matrix.coverage:.1f}%"))

        return "\n".join(lines)

    async def export_matrix_html(
        self,
        matrix: TraceabilityMatrix,
    ) -> str:
        """Export traceability matrix as HTML table.

        Args:
            matrix: TraceabilityMatrix to export

        Returns:
            HTML string
        """
        html = ['<table border="1" cellpadding="5">']

        # Header row
        html.extend(("<tr>", "<th>Source</th>"))
        html.extend(f"<th>{col['title']}</th>" for col in matrix.columns)
        html.append("</tr>")

        # Data rows
        for i, row_item in enumerate(matrix.rows):
            html.extend(("<tr>", f"<td><strong>{row_item['title']}</strong></td>"))
            for _j, cell in enumerate(matrix.matrix[i]):
                if cell:
                    html.append(f'<td style="background-color: #90EE90;">{cell}</td>')
                else:
                    html.append("<td></td>")
            html.append("</tr>")

        # Summary
        html.extend(
            (
                "</table>",
                f"<p>Total Links: {matrix.total_links}</p>",
                f"<p>Coverage: {matrix.coverage:.1f}%</p>",
            ),
        )

        return "\n".join(html)

    async def get_uncovered_items(
        self,
        matrix: TraceabilityMatrix,
    ) -> dict[str, list[str]]:
        """Get items that are not traced in the matrix.

        Args:
            matrix: TraceabilityMatrix

        Returns:
            Dict with uncovered sources and targets
        """
        uncovered_sources = []
        uncovered_targets = []

        # Check sources
        for i, row in enumerate(matrix.matrix):
            if not any(cell for cell in row):
                uncovered_sources.append(matrix.rows[i]["id"])

        # Check targets
        uncovered_targets = [
            matrix.columns[j]["id"]
            for j in range(len(matrix.columns))
            if not any(matrix.matrix[i][j] for i in range(len(matrix.rows)))
        ]

        return {
            "uncovered_sources": uncovered_sources,
            "uncovered_targets": uncovered_targets,
        }
