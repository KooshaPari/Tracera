"""
CSS-like cascade helpers for theming.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class Specificity:
    """
    CSS-like specificity calculation.
    """

    def __init__(self, inline: int = 0, ids: int = 0, classes: int = 0, elements: int = 0):
        self.inline = inline
        self.ids = ids
        self.classes = classes
        self.elements = elements

    def __lt__(self, other: Specificity) -> bool:
        """
        Compare specificities.
        """
        return (self.inline, self.ids, self.classes, self.elements) < (
            other.inline,
            other.ids,
            other.classes,
            other.elements,
        )

    def __eq__(self, other: Specificity) -> bool:
        """
        Check if specificities are equal.
        """
        return (self.inline, self.ids, self.classes, self.elements) == (
            other.inline,
            other.ids,
            other.classes,
            other.elements,
        )

    @classmethod
    def from_selector(cls, selector: str) -> Specificity:
        """
        Calculate specificity from CSS selector.
        """
        inline = 1 if selector.startswith("style=") else 0
        ids = selector.count("#")
        classes = selector.count(".")
        elements = len(
            [part for part in selector.split() if part and not part.startswith(("#", ".", "["))],
        )

        return cls(inline=inline, ids=ids, classes=classes, elements=elements)


@dataclass
class StyleRule:
    """
    CSS-like style rule with specificity.
    """

    selector: str
    properties: dict[str, Any]
    specificity: Specificity
    source_order: int = 0

    def __post_init__(self):
        if not hasattr(self, "specificity"):
            self.specificity = Specificity.from_selector(self.selector)
