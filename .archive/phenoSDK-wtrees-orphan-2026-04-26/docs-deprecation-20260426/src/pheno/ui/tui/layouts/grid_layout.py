"""
GridLayout - Responsive grid system.

Provides flexible grid-based layouts.
"""

import contextlib
from dataclasses import dataclass

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Grid
    from textual.reactive import reactive
    from textual.widget import Widget
    from textual.widgets import Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    Widget = object
    Container = object
    Grid = object
    def reactive(x):
        return x
    ComposeResult = object


@dataclass
class GridCell:
    """
    Grid cell definition.
    """

    widget: Widget
    row: int = 0
    col: int = 0
    row_span: int = 1
    col_span: int = 1


class GridLayout(Static):
    """Responsive grid layout container.

    Features:
    - Flexible grid sizing
    - Cell spanning
    - Dynamic cell management
    - Responsive breakpoints
    """

    grid_rows = reactive(3)
    grid_cols = reactive(3)

    def __init__(
        self, rows: int = 3, cols: int = 3, cells: list[GridCell] | None = None, gutter: int = 1, **kwargs,
    ):
        super().__init__(**kwargs)
        self.grid_rows = rows
        self.grid_cols = cols
        self.cells = cells or []
        self.gutter = gutter
        self._grid: Grid | None = None

    def compose(self) -> ComposeResult:
        """
        Create grid layout.
        """
        grid = Grid(id="grid-container")
        grid.styles.grid_size_rows = self.grid_rows
        grid.styles.grid_size_columns = self.grid_cols
        grid.styles.grid_gutter_horizontal = self.gutter
        grid.styles.grid_gutter_vertical = self.gutter

        self._grid = grid

        # Add cells
        for cell in self.cells:
            cell.widget.styles.row_span = cell.row_span
            cell.widget.styles.column_span = cell.col_span
            grid.mount(cell.widget)

        yield grid

    def add_cell(
        self, widget: Widget, row: int = 0, col: int = 0, row_span: int = 1, col_span: int = 1,
    ) -> GridCell:
        """
        Add a cell to the grid.
        """
        cell = GridCell(widget=widget, row=row, col=col, row_span=row_span, col_span=col_span)

        self.cells.append(cell)

        # Add to grid if mounted
        if self._grid:
            widget.styles.row_span = row_span
            widget.styles.column_span = col_span
            self._grid.mount(widget)

        return cell

    def remove_cell(self, widget: Widget) -> bool:
        """
        Remove a cell from the grid.
        """
        # Find cell
        cell_index = None
        for i, cell in enumerate(self.cells):
            if cell.widget == widget:
                cell_index = i
                break

        if cell_index is None:
            return False

        # Remove from cells
        self.cells.pop(cell_index)

        # Remove from grid
        if self._grid:
            with contextlib.suppress(Exception):
                widget.remove()

        return True

    def update_cell(
        self,
        widget: Widget,
        row: int | None = None,
        col: int | None = None,
        row_span: int | None = None,
        col_span: int | None = None,
    ) -> bool:
        """
        Update cell properties.
        """
        # Find cell
        cell = None
        for c in self.cells:
            if c.widget == widget:
                cell = c
                break

        if not cell:
            return False

        # Update properties
        if row is not None:
            cell.row = row

        if col is not None:
            cell.col = col

        if row_span is not None:
            cell.row_span = row_span
            widget.styles.row_span = row_span

        if col_span is not None:
            cell.col_span = col_span
            widget.styles.column_span = col_span

        # Refresh grid
        self.refresh()

        return True

    def set_grid_size(self, rows: int, cols: int) -> None:
        """
        Set grid dimensions.
        """
        self.grid_rows = rows
        self.grid_cols = cols

        if self._grid:
            self._grid.styles.grid_size_rows = rows
            self._grid.styles.grid_size_columns = cols
            self.refresh()

    def clear_grid(self) -> None:
        """
        Remove all cells from grid.
        """
        if self._grid:
            for cell in self.cells:
                with contextlib.suppress(Exception):
                    cell.widget.remove()

        self.cells.clear()

    def get_cell_at(self, row: int, col: int) -> GridCell | None:
        """
        Get cell at specific position.
        """
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        return None

    def get_cells(self) -> list[GridCell]:
        """
        Get all cells.
        """
        return self.cells.copy()

    def set_gutter(self, gutter: int) -> None:
        """
        Set grid gutter size.
        """
        self.gutter = gutter

        if self._grid:
            self._grid.styles.grid_gutter_horizontal = gutter
            self._grid.styles.grid_gutter_vertical = gutter
            self.refresh()
