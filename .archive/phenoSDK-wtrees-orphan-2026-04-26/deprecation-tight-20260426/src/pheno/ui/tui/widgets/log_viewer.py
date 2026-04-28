"""
LogViewer Widget - Scrolling logs with filtering and search.

Provides a powerful log viewing interface with:
- Automatic scrolling
- Log level filtering
- Search/highlighting
- Time-based filtering
- Export functionality
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from rich.panel import Panel
    from rich.text import Text
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal
    from textual.reactive import reactive
    from textual.widgets import RichLog, Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    RichLog = object
    Static = object
    Text = object
    Panel = object
    Container = object
    Horizontal = object
    ComposeResult = object
    def reactive(x):
        return x


class LogLevel(Enum):
    """
    Log severity levels.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """
    Individual log entry.
    """

    timestamp: float
    level: LogLevel
    message: str
    source: str = ""
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def formatted_time(self) -> str:
        """
        Get formatted timestamp.
        """
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%H:%M:%S.%f")[:-3]

    def to_rich_text(self, highlight_terms: list[str] | None = None) -> Text:
        """
        Convert to Rich Text with optional highlighting.
        """
        # Color based on level
        level_colors = {
            LogLevel.DEBUG: "dim cyan",
            LogLevel.INFO: "green",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red",
        }

        color = level_colors.get(self.level, "white")

        text = Text()
        text.append(f"[{self.formatted_time}] ", style="dim")
        text.append(f"{self.level.value:8s} ", style=color)

        if self.source:
            text.append(f"[{self.source}] ", style="cyan")

        message_text = Text(self.message)

        # Apply highlighting
        if highlight_terms:
            for term in highlight_terms:
                if term.lower() in self.message.lower():
                    # Find and highlight all occurrences
                    msg_lower = self.message.lower()
                    start = 0
                    while True:
                        pos = msg_lower.find(term.lower(), start)
                        if pos == -1:
                            break
                        message_text.stylize("bold yellow on blue", pos, pos + len(term))
                        start = pos + len(term)

        text.append(message_text)
        return text


class LogViewer(Static):
    """Advanced log viewer widget with filtering and search.

    Features:
    - Real-time log streaming
    - Level-based filtering
    - Search with highlighting
    - Auto-scroll toggle
    - Export to file
    """

    auto_scroll = reactive(True)
    filter_level = reactive(LogLevel.DEBUG)
    search_term = reactive("")
    entry_count = reactive(0)

    def __init__(
        self, max_entries: int = 1000, auto_scroll: bool = True, show_stats: bool = True, **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_entries = max_entries
        self.auto_scroll = auto_scroll
        self.show_stats = show_stats
        self._entries: list[LogEntry] = []
        self._callbacks: list[Callable[[LogEntry], None]] = []

    def compose(self) -> ComposeResult:
        """
        Create log viewer layout.
        """
        if self.show_stats:
            yield Static("", id="log-stats")
        yield RichLog(id="log-display", highlight=True, markup=True, wrap=True)

    def add_log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        source: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a new log entry.
        """
        entry = self._create_log_entry(message, level, source, metadata)
        self._add_entry_to_storage(entry)
        self._update_display_for_entry(entry)
        self._notify_callbacks(entry)

    def _create_log_entry(
        self, message: str, level: LogLevel, source: str, metadata: dict[str, Any] | None,
    ) -> LogEntry:
        """
        Create a new log entry with timestamp.
        """
        return LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            source=source,
            metadata=metadata or {},
        )

    def _add_entry_to_storage(self, entry: LogEntry) -> None:
        """
        Add entry to storage and update counts.
        """
        self._entries.append(entry)
        self.entry_count = len(self._entries)
        self._trim_entries_if_needed()

    def _trim_entries_if_needed(self) -> None:
        """
        Trim entries if they exceed maximum count.
        """
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def _update_display_for_entry(self, entry: LogEntry) -> None:
        """
        Update display for a single entry.
        """
        if self._should_display(entry):
            self._display_entry(entry)

        if self.show_stats:
            self._update_stats()

    def _notify_callbacks(self, entry: LogEntry) -> None:
        """
        Notify all registered callbacks about the new entry.
        """
        for callback in self._callbacks:
            try:
                callback(entry)
            except Exception as e:
                print(f"Log callback error: {e}")

    def _should_display(self, entry: LogEntry) -> bool:
        """
        Check if entry should be displayed based on filters.
        """
        # Level filter
        level_values = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4,
        }

        if level_values[entry.level] < level_values[self.filter_level]:
            return False

        # Search filter
        return not (self.search_term and self.search_term.lower() not in entry.message.lower())

    def _display_entry(self, entry: LogEntry) -> None:
        """
        Display a single entry in the log.
        """
        try:
            log_display = self.query_one("#log-display", RichLog)

            # Get highlight terms
            highlight_terms = [self.search_term] if self.search_term else []

            # Write formatted entry
            rich_text = entry.to_rich_text(highlight_terms)
            log_display.write(rich_text)

            # Auto-scroll if enabled
            if self.auto_scroll:
                log_display.scroll_end(animate=False)

        except Exception:
            # Widget not yet mounted
            pass

    def _update_stats(self) -> None:
        """
        Update statistics display.
        """
        try:
            stats_widget = self.query_one("#log-stats", Static)

            # Count by level
            level_counts = dict.fromkeys(LogLevel, 0)
            for entry in self._entries:
                level_counts[entry.level] += 1

            stats_text = f"Total: {len(self._entries)} | "
            stats_text += f"DEBUG: {level_counts[LogLevel.DEBUG]} | "
            stats_text += f"INFO: {level_counts[LogLevel.INFO]} | "
            stats_text += f"WARN: {level_counts[LogLevel.WARNING]} | "
            stats_text += f"ERROR: {level_counts[LogLevel.ERROR]} | "
            stats_text += f"CRIT: {level_counts[LogLevel.CRITICAL]}"

            if self.search_term:
                stats_text += f" | Search: '{self.search_term}'"

            stats_widget.update(stats_text)

        except Exception:
            pass

    def set_filter_level(self, level: LogLevel) -> None:
        """
        Set minimum log level to display.
        """
        self.filter_level = level
        self.refresh_display()

    def set_search(self, term: str) -> None:
        """
        Set search term.
        """
        self.search_term = term
        self.refresh_display()

    def toggle_auto_scroll(self) -> None:
        """
        Toggle auto-scroll.
        """
        self.auto_scroll = not self.auto_scroll

    def clear(self) -> None:
        """
        Clear all log entries.
        """
        self._entries.clear()
        self.entry_count = 0

        try:
            log_display = self.query_one("#log-display", RichLog)
            log_display.clear()

            if self.show_stats:
                self._update_stats()
        except Exception:
            pass

    def refresh_display(self) -> None:
        """
        Refresh the entire display based on current filters.
        """
        try:
            log_display = self.query_one("#log-display", RichLog)
            log_display.clear()

            # Redisplay all entries that pass filters
            for entry in self._entries:
                if self._should_display(entry):
                    self._display_entry(entry)

            if self.show_stats:
                self._update_stats()

        except Exception:
            pass

    def export_to_file(self, filepath: str, include_metadata: bool = False) -> None:
        """
        Export logs to file.
        """
        with open(filepath, "w") as f:
            for entry in self._entries:
                line = f"[{entry.formatted_time}] {entry.level.value:8s}"
                if entry.source:
                    line += f" [{entry.source}]"
                line += f" {entry.message}\n"

                if include_metadata and entry.metadata:
                    line += f"  Metadata: {entry.metadata}\n"

                f.write(line)

    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """
        Add callback for new log entries.
        """
        self._callbacks.append(callback)

    def get_entries(
        self, level: LogLevel | None = None, source: str | None = None, since: float | None = None,
    ) -> list[LogEntry]:
        """
        Get filtered log entries.
        """
        entries = self._entries

        if level:
            entries = [e for e in entries if e.level == level]

        if source:
            entries = [e for e in entries if e.source == source]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        return entries
