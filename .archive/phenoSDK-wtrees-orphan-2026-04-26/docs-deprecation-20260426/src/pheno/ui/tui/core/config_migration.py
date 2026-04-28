"""
Utilities for managing configuration schema migrations.
"""

import itertools
import logging
from collections import deque
from collections.abc import Callable
from copy import deepcopy
from typing import Any

logger = logging.getLogger(__name__)


class ConfigMigration:
    """
    Registry of upgrade routines between schema versions.
    """

    def __init__(self) -> None:
        self._migrations: dict[str, dict[str, Callable[[dict[str, Any]], dict[str, Any]]]] = {}

    def register(
        self,
        from_version: str,
        to_version: str,
        migration: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> None:
        """
        Register a migration function.
        """

        self._migrations.setdefault(from_version, {})[to_version] = migration
        logger.info("Registered migration: %s -> %s", from_version, to_version)

    def migrate(
        self, payload: dict[str, Any], from_version: str, to_version: str,
    ) -> dict[str, Any]:
        """
        Apply a chain of migrations to reach ``to_version``.
        """

        if from_version == to_version:
            return payload

        path = self._find_path(from_version, to_version)
        if path is None:
            raise ValueError(f"No migration path found from {from_version} to {to_version}")

        result = deepcopy(payload)
        for current, target in itertools.pairwise(path):
            try:
                migration = self._migrations[current][target]
            except KeyError as exc:  # pragma: no cover - defensive guard
                raise ValueError(f"Migration not found: {current} -> {target}") from exc

            logger.info("Applying migration: %s -> %s", current, target)
            result = migration(result)
            result["version"] = target

        return result

    def _find_path(self, start: str, target: str) -> list[str] | None:
        """
        Return the shortest migration path via breadth-first search.
        """

        if start not in self._migrations:
            return None

        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        visited = {start}

        while queue:
            version, path = queue.popleft()
            if version == target:
                return path

            for next_version in self._migrations.get(version, {}):
                if next_version not in visited:
                    visited.add(next_version)
                    queue.append((next_version, [*path, next_version]))

        return None

    def get_version_history(self) -> list[str]:
        """
        Return a sorted list of all known schema versions.
        """

        versions: set[str] = set()
        for source, targets in self._migrations.items():
            versions.add(source)
            versions.update(targets.keys())
        return sorted(versions)


__all__ = ["ConfigMigration"]
