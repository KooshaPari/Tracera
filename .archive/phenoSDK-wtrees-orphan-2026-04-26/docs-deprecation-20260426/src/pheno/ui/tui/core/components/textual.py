"""
Textual integration for components.
"""

from __future__ import annotations

from .base import BaseComponent
from .environment import HAS_TEXTUAL, ComposeResult, Container, Widget

if HAS_TEXTUAL:

    class TextualComponent(BaseComponent, Widget):
        """
        Base component wired into the Textual widget system.
        """

        def __init__(self, **kwargs):
            BaseComponent.__init__(self, **kwargs)
            Widget.__init__(self, **kwargs)

        def compose(self) -> ComposeResult:
            return super().compose()

        def on_mount(self) -> None:
            super().on_mount()

        def on_unmount(self) -> None:
            super().on_unmount()

        def refresh(self) -> None:
            if hasattr(super(), "refresh"):
                super().refresh()  # type: ignore[misc]

    class TextualContainer(TextualComponent, Container):
        """
        Container variant that mixes in Textual's container type.
        """

        def __init__(self, **kwargs):
            TextualComponent.__init__(self, **kwargs)
            Container.__init__(self, **kwargs)

        def compose(self) -> ComposeResult:
            return super().compose()

else:

    class TextualComponent(BaseComponent):
        """
        Fallback component used when Textual is unavailable.
        """

        def compose(self) -> ComposeResult:
            return super().compose()

    class TextualContainer(TextualComponent):
        """
        Fallback container component mirroring the Textual API.
        """

        def compose(self) -> ComposeResult:
            return super().compose()


__all__ = ["TextualComponent", "TextualContainer"]
