"""
SplitLayout - Horizontal and vertical split panes.

Provides resizable split views with multiple panes.
"""

from enum import Enum

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widget import Widget
    from textual.widgets import Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    Widget = object
    Container = object
    Horizontal = object
    Vertical = object
    def reactive(x):
        return x
    ComposeResult = object


class SplitDirection(Enum):
    """
    Split direction.
    """

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class SplitLayout(Static):
    """Split layout container with resizable panes.

    Features:
    - Horizontal or vertical splits
    - Resizable panes
    - Nested splits
    - Customizable ratios
    """

    split_ratio = reactive(0.5)

    def __init__(
        self,
        direction: SplitDirection = SplitDirection.HORIZONTAL,
        panes: list[Widget] | None = None,
        ratios: list[float] | None = None,
        min_size: int = 10,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.direction = direction
        self.panes = panes or []
        self.ratios = ratios or [1.0 / len(self.panes) if self.panes else 0.5]
        self.min_size = min_size
        self._containers: list[Container] = []

    def compose(self) -> ComposeResult:
        """
        Create split layout.
        """
        if self.direction == SplitDirection.HORIZONTAL:
            with Horizontal(id="split-container"):
                for i, pane in enumerate(self.panes):
                    ratio = self.ratios[i] if i < len(self.ratios) else 1.0
                    with Container(classes="split-pane"):
                        pane.styles.width = f"{int(ratio * 100)}%"
                        yield pane
        else:  # VERTICAL
            with Vertical(id="split-container"):
                for i, pane in enumerate(self.panes):
                    ratio = self.ratios[i] if i < len(self.ratios) else 1.0
                    with Container(classes="split-pane"):
                        pane.styles.height = f"{int(ratio * 100)}%"
                        yield pane

    def add_pane(self, widget: Widget, ratio: float = 1.0, index: int | None = None) -> None:
        """
        Add a new pane to the layout.
        """
        if index is None:
            self.panes.append(widget)
            self.ratios.append(ratio)
        else:
            self.panes.insert(index, widget)
            self.ratios.insert(index, ratio)

        # Normalize ratios
        total = sum(self.ratios)
        self.ratios = [r / total for r in self.ratios]

        # Refresh layout
        self.refresh(recompose=True)

    def remove_pane(self, index: int) -> Widget | None:
        """
        Remove a pane from the layout.
        """
        if index < 0 or index >= len(self.panes):
            return None

        widget = self.panes.pop(index)
        self.ratios.pop(index)

        # Normalize ratios
        if self.ratios:
            total = sum(self.ratios)
            self.ratios = [r / total for r in self.ratios]

        # Refresh layout
        self.refresh(recompose=True)

        return widget

    def set_ratio(self, index: int, ratio: float) -> None:
        """
        Set the ratio for a specific pane.
        """
        if index < 0 or index >= len(self.ratios):
            return

        self.ratios[index] = ratio

        # Normalize ratios
        total = sum(self.ratios)
        self.ratios = [r / total for r in self.ratios]

        # Refresh layout
        self.refresh(recompose=True)

    def set_ratios(self, ratios: list[float]) -> None:
        """
        Set ratios for all panes.
        """
        if len(ratios) != len(self.panes):
            return

        self.ratios = ratios

        # Normalize ratios
        total = sum(self.ratios)
        self.ratios = [r / total for r in self.ratios]

        # Refresh layout
        self.refresh(recompose=True)

    def get_pane(self, index: int) -> Widget | None:
        """
        Get pane widget by index.
        """
        if index < 0 or index >= len(self.panes):
            return None
        return self.panes[index]

    def swap_panes(self, index1: int, index2: int) -> None:
        """
        Swap two panes.
        """
        if index1 < 0 or index1 >= len(self.panes) or index2 < 0 or index2 >= len(self.panes):
            return

        self.panes[index1], self.panes[index2] = self.panes[index2], self.panes[index1]
        self.ratios[index1], self.ratios[index2] = self.ratios[index2], self.ratios[index1]

        # Refresh layout
        self.refresh(recompose=True)
