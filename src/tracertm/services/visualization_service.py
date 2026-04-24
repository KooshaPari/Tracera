"""Visualization service for TraceRTM.

Provides ASCII graph and tree visualization for items and links.


Functional Requirements: FR-RPT-008
"""

from __future__ import annotations

from typing import Any


def _get_item_level(
    item_id: str,
    links: list[dict[str, Any]],
    visited: set[str],
    current_level: int = 0,
) -> int:
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
                target_level = _get_item_level(target, links, visited, current_level + 1)
                max_level = max(max_level, target_level)

    return max_level


def _calculate_levels(
    items: dict[str, dict[str, Any]],
    links: list[dict[str, Any]],
) -> dict[int, list[str]]:
    """Calculate levels for each item in the graph."""
    levels: dict[int, list[str]] = {}
    visited: set[str] = set()

    for item_id in items:
        level = _get_item_level(item_id, links, visited)
        if level not in levels:
            levels[level] = []
        levels[level].append(item_id)

    return levels


def _render_link(
    link: dict[str, Any],
    items: dict[str, dict[str, Any]],
) -> str | None:
    """Render a single link as string."""
    source_key = link.get("source")
    target_key = link.get("target")
    if isinstance(source_key, str) and isinstance(target_key, str):
        source_item = items.get(source_key, {})
        target_item = items.get(target_key, {})
        if isinstance(source_item, dict) and isinstance(target_item, dict):
            source = source_item.get("title", source_key)
            target = target_item.get("title", target_key)
            link_type = link.get("type", "relates_to")
            return f"  {source} --[{link_type}]--> {target}"
    return None


def _render_levels(
    items: dict[str, dict[str, Any]],
    levels: dict[int, list[str]],
) -> list[str]:
    """Render items grouped by level."""
    lines: list[str] = []
    for level in sorted(levels.keys()):
        lines.append(f"\nLevel {level}:")
        for item_id in levels[level]:
            item = items[item_id]
            lines.append(f"  [{item_id}] {item.get('title', 'Unknown')}")
    return lines


class VisualizationService:
    """Service for visualizing items and links."""

    @staticmethod
    def render_tree(
        items: list[dict[str, Any]],
        _root_id: str | None = None,
        prefix: str = "",
        _is_last: bool = True,
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

        lines: list[str] = []

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
                    _is_last=is_last_item,
                )
                if child_tree:
                    lines.append(child_tree)

        return "\n".join(lines)

    @staticmethod
    def render_graph(
        items: dict[str, dict[str, Any]],
        links: list[dict[str, Any]],
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

        lines: list[str] = []
        lines.extend(("Item Dependency Graph", "=" * 40))

        # Calculate levels for items
        levels = _calculate_levels(items, links)

        # Render items by level
        lines.extend(_render_levels(items, levels))

        # Render links
        lines.append("\nDependencies:")
        for link in links:
            rendered = _render_link(link, items)
            if rendered:
                lines.append(rendered)

        return "\n".join(lines)

    @staticmethod
    def render_dependency_matrix(
        items: dict[str, dict[str, Any]],
        links: list[dict[str, Any]],
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
        lines: list[str] = []

        # Header
        header = "     " + " ".join(f"{i:3d}" for i in range(len(item_ids)))
        lines.append(header)

        # Matrix
        for i, source_id in enumerate(item_ids):
            row = f"{i:3d} "
            for target_id in item_ids:
                # Check if there's a link from source to target
                has_link = any(link.get("source") == source_id and link.get("target") == target_id for link in links)
                row += "  X " if has_link else "    "
            lines.append(row)

        lines.append("\nLegend:")
        for i, item_id in enumerate(item_ids):
            item = items[item_id]
            lines.append(f"  {i}: {item.get('title', item_id)}")

        return "\n".join(lines)

    @staticmethod
    def render_item_summary(
        item: dict[str, Any],
        max_title_length: int = 40,
    ) -> str:
        """Render a single item summary.

        Args:
            item: Item to render
            max_title_length: Maximum title length

        Returns:
            Item summary as string
        """
        title: str = str(item.get("title", item.get("id", "Unknown")))
        if len(title) > max_title_length:
            title = title[: max_title_length - 3] + "..."

        lines: list[str] = []
        lines.extend((f"  {title}", f"  ID: {item.get('id', 'N/A')}"))

        item_type = item.get("type", item.get("item_type", "N/A"))
        lines.append(f"  Type: {item_type}")

        status = item.get("status")
        if status:
            lines.append(f"  Status: {status}")

        return "\n".join(lines)
