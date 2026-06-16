"""Registry for pluggable scoring strategies.

Provides a centralized registry for managing agreement scorer implementations
that satisfy the :class:`ScorerPort` protocol. Allows dynamic registration and
lookup of scoring strategies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.tracertm.ports.scorer import ScorerPort


class ScorerRegistry:
    """Pluggable registry for agreement scoring strategies.

    Manages a dictionary of named scorers implementing the :class:`ScorerPort` protocol.
    Provides methods to register new strategies, retrieve by name, and list available scorers.

    The registry is initialized with JaccardScorer as the default strategy.

    Example:
        >>> registry = ScorerRegistry()
        >>> scorer = registry.get("jaccard")
        >>> result = scorer.score("requirement", "artifact")
        >>> print(result.score)
        0.5
    """

    def __init__(self) -> None:
        """Initialize registry with default scorers."""
        self._scorers: dict[str, ScorerPort] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Register default scorers (Jaccard)."""
        # Import here to avoid circular imports
        from src.tracertm.scoring.jaccard_scorer import JaccardScorer

        self.register("jaccard", JaccardScorer())

    def register(self, name: str, scorer: ScorerPort) -> None:
        """Register a new scoring strategy.

        Args:
            name: Stable identifier for the scorer (must match scorer.name).
            scorer: An object implementing the :class:`ScorerPort` protocol.

        Raises:
            ValueError: If name does not match scorer.name.
            TypeError: If scorer does not implement ScorerPort protocol.
        """
        if name != scorer.name:
            raise ValueError(
                f"registration name '{name}' must match scorer.name '{scorer.name}'"
            )

        # Runtime protocol check
        if not hasattr(scorer, "score") or not callable(scorer.score):
            raise TypeError(
                f"scorer must implement ScorerPort protocol (have 'score' method)"
            )
        if not hasattr(scorer, "name"):
            raise TypeError(
                f"scorer must implement ScorerPort protocol (have 'name' property)"
            )

        self._scorers[name] = scorer

    def get(self, name: str) -> ScorerPort:
        """Retrieve a registered scorer by name.

        Args:
            name: The identifier of the scorer to retrieve.

        Returns:
            The registered ScorerPort implementation.

        Raises:
            KeyError: If the scorer is not registered.
        """
        if name not in self._scorers:
            raise KeyError(
                f"scorer '{name}' not registered. Available: {self.list_scorers()}"
            )
        return self._scorers[name]

    def list_scorers(self) -> list[str]:
        """List all registered scorer names.

        Returns:
            A list of registered scorer identifiers.
        """
        return sorted(self._scorers.keys())

    def has(self, name: str) -> bool:
        """Check if a scorer is registered.

        Args:
            name: The identifier to check.

        Returns:
            True if the scorer is registered, False otherwise.
        """
        return name in self._scorers
