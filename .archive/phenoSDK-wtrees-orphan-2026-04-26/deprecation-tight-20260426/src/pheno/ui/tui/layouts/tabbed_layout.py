"""
TabbedLayout - Tab-based navigation system.

Provides tabbed interface for organizing content.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

try:
    from textual.app import ComposeResult
    from textual.reactive import reactive
    from textual.widget import Widget
    from textual.widgets import Static, TabbedContent, TabPane

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    Widget = object
    TabbedContent = object
    TabPane = object
    def reactive(x):
        return x
    ComposeResult = object


@dataclass
class Tab:
    """
    Tab definition.
    """

    id: str
    title: str
    content: Widget
    icon: str | None = None
    closeable: bool = False
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TabbedLayout(Static):
    """Tabbed layout container with tab management.

    Features:
    - Dynamic tab creation/removal
    - Tab switching
    - Closeable tabs
    - Custom tab icons
    - Tab callbacks
    """

    active_tab = reactive("")
    tab_count = reactive(0)

    def __init__(self, tabs: list[Tab] | None = None, initial_tab: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.tabs = tabs or []
        self.initial_tab = initial_tab
        self._tab_switch_callbacks: list[Callable[[str, str], None]] = []
        self._tab_close_callbacks: list[Callable[[str], None]] = []
        self.tab_count = len(self.tabs)

    def compose(self) -> ComposeResult:
        """
        Create tabbed layout.
        """
        with TabbedContent(id="tabbed-content"):
            for tab in self.tabs:
                title = f"{tab.icon} {tab.title}" if tab.icon else tab.title
                with TabPane(title, id=tab.id):
                    yield tab.content

        # Set initial tab if specified
        if self.initial_tab:
            self.active_tab = self.initial_tab
        elif self.tabs:
            self.active_tab = self.tabs[0].id

    def add_tab(
        self,
        tab_id: str,
        title: str,
        content: Widget,
        icon: str | None = None,
        closeable: bool = False,
        switch_to: bool = True,
    ) -> Tab:
        """
        Add a new tab.
        """
        tab = Tab(id=tab_id, title=title, content=content, icon=icon, closeable=closeable)

        self.tabs.append(tab)
        self.tab_count = len(self.tabs)

        # Refresh layout to add new tab
        self.refresh(recompose=True)

        # Switch to new tab if requested
        if switch_to:
            self.switch_to_tab(tab_id)

        return tab

    def remove_tab(self, tab_id: str) -> bool:
        """
        Remove a tab.
        """
        # Find tab
        tab_index = None
        for i, tab in enumerate(self.tabs):
            if tab.id == tab_id:
                tab_index = i
                break

        if tab_index is None:
            return False

        tab = self.tabs[tab_index]

        # Check if closeable
        if not tab.closeable:
            return False

        # Remove tab
        self.tabs.pop(tab_index)
        self.tab_count = len(self.tabs)

        # Switch to adjacent tab if this was active
        if self.active_tab == tab_id and self.tabs:
            if tab_index > 0:
                self.switch_to_tab(self.tabs[tab_index - 1].id)
            else:
                self.switch_to_tab(self.tabs[0].id)

        # Notify callbacks
        for callback in self._tab_close_callbacks:
            try:
                callback(tab_id)
            except Exception as e:
                print(f"Tab close callback error: {e}")

        # Refresh layout
        self.refresh(recompose=True)

        return True

    def switch_to_tab(self, tab_id: str) -> bool:
        """
        Switch to a specific tab.
        """
        # Check if tab exists
        if not any(tab.id == tab_id for tab in self.tabs):
            return False

        old_tab = self.active_tab
        self.active_tab = tab_id

        # Notify callbacks
        for callback in self._tab_switch_callbacks:
            try:
                callback(old_tab, tab_id)
            except Exception as e:
                print(f"Tab switch callback error: {e}")

        # Update UI
        try:
            tabbed_content = self.query_one("#tabbed-content", TabbedContent)
            tabbed_content.active = tab_id
        except Exception:
            pass

        return True

    def get_tab(self, tab_id: str) -> Tab | None:
        """
        Get tab by ID.
        """
        for tab in self.tabs:
            if tab.id == tab_id:
                return tab
        return None

    def get_active_tab(self) -> Tab | None:
        """
        Get currently active tab.
        """
        return self.get_tab(self.active_tab)

    def update_tab(self, tab_id: str, title: str | None = None, icon: str | None = None) -> bool:
        """
        Update tab properties.
        """
        tab = self.get_tab(tab_id)
        if not tab:
            return False

        if title is not None:
            tab.title = title

        if icon is not None:
            tab.icon = icon

        # Refresh layout
        self.refresh(recompose=True)

        return True

    def reorder_tabs(self, new_order: list[str]) -> bool:
        """
        Reorder tabs.
        """
        if len(new_order) != len(self.tabs):
            return False

        # Create new tab list in specified order
        new_tabs = []
        for tab_id in new_order:
            tab = self.get_tab(tab_id)
            if not tab:
                return False
            new_tabs.append(tab)

        self.tabs = new_tabs

        # Refresh layout
        self.refresh(recompose=True)

        return True

    def add_tab_switch_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Add callback for tab switches (old_tab_id, new_tab_id).
        """
        self._tab_switch_callbacks.append(callback)

    def add_tab_close_callback(self, callback: Callable[[str], None]) -> None:
        """
        Add callback for tab closures.
        """
        self._tab_close_callbacks.append(callback)

    def get_tab_ids(self) -> list[str]:
        """
        Get list of all tab IDs.
        """
        return [tab.id for tab in self.tabs]

    def get_tab_count(self) -> int:
        """
        Get number of tabs.
        """
        return len(self.tabs)
