"""
Visualization service for TraceRTM.

Provides ASCII graph and tree visualization for items and links.
"""


class VisualizationService:
    """Service for visualizing items and links."""

    @staticmethod
    def render_tree(
        items: list[dict[str, object]],
        root_id: str | None = None,
        prefix: str = "",
        is_last: bool = True,
    ) -> str:
        """Render items as a tree structure.

        Args:
            items: List of items with id, title, children
            root_id: Root item ID (optional)
            prefix: Prefix for tree lines
            is_last: Whether this is the last item

        Returns:
            Tree visualization as string
        """
        if not items:
            return ""

        lines = []

        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1

            # Add tree branch
            if prefix:
                branch = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{branch}{item.get('title', item.get('id'))}")
            else:
                lines.append(f"└── {item.get('title', item.get('id'))}")

            # Add children
            children = item.get("children", [])
            if isinstance(children, list):
                extension = "    " if is_last_item else "│   "
                child_prefix = prefix + extension if prefix else extension
                child_tree = VisualizationService.render_tree(
                    children,
                    prefix=child_prefix,
                    is_last=is_last_item,
                )
                if child_tree:
                    lines.append(child_tree)

        return "\n".join(lines)

    @staticmethod
    def render_graph(
        items: dict[str, dict[str, object]],
        links: list[dict[str, object]],
    ) -> str:
        """Render items and links as ASCII graph.

        Args:
            items: Dictionary of items by ID
            links: List of links with source, target

        Returns:
            Graph visualization as string
        """
        if not items:
            return ""

        lines = []
        lines.append("Item Dependency Graph")
        lines.append("=" * 40)

        # Group items by level
        levels: dict[int, list[str]] = {}
        visited: set[str] = set()

        def get_level(item_id: str, current_level: int = 0) -> int:
            """Get level of item in graph."""
            if item_id in visited:
                return current_level

            visited.add(item_id)
            max_level = current_level

            # Find items that depend on this one
            for link in links:
                if link.get("source") == item_id:
                    target = link.get("target")
                    if isinstance(target, str):
                        target_level = get_level(target, current_level + 1)
                        max_level = max(max_level, target_level)

            return max_level

        # Calculate levels
        for item_id in items:
            level = get_level(item_id)
            if level not in levels:
                levels[level] = []
            levels[level].append(item_id)

        # Render by level
        for level in sorted(levels.keys()):
            lines.append(f"\nLevel {level}:")
            for item_id in levels[level]:
                item = items[item_id]
                lines.append(f"  [{item_id}] {item.get('title', 'Unknown')}")

        # Render links
        lines.append("\nDependencies:")
        for link in links:
            source_key = link.get("source")
            target_key = link.get("target")
            if isinstance(source_key, str) and isinstance(target_key, str):
                source_item = items.get(source_key, {})
                target_item = items.get(target_key, {})
                if isinstance(source_item, dict) and isinstance(target_item, dict):
                    source = source_item.get("title", source_key)
                    target = target_item.get("title", target_key)
                    link_type = link.get("type", "relates_to")
                    lines.append(f"  {source} --[{link_type}]--> {target}")

        return "\n".join(lines)

    @staticmethod
    def render_dependency_matrix(
        items: dict[str, dict[str, object]],
        links: list[dict[str, object]],
    ) -> str:
        """Render dependency matrix.

        Args:
            items: Dictionary of items by ID
            links: List of links

        Returns:
            Dependency matrix as string
        """
        if not items:
            return ""

        item_ids = sorted(items.keys())
        lines = []

        # Header
        header = "     " + " ".join(f"{i:3d}" for i in range(len(item_ids)))
        lines.append(header)

        # Matrix
        for i, source_id in enumerate(item_ids):
            row = f"{i:3d} "
            for _j, target_id in enumerate(item_ids):
                # Check if there's a link
                has_link = any(link["source"] == source_id and link["target"] == target_id for link in links)
                row += " X " if has_link else " . "
            lines.append(row)

        # Legend
        lines.append("\nLegend:")
        lines.append("  X = dependency exists")
        lines.append("  . = no dependency")

        return "\n".join(lines)
