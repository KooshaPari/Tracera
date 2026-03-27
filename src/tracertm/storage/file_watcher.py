"""File watcher for auto-indexing .trace/ changes into SQLite.

This module provides a file watcher that monitors .trace/ directory changes
and automatically indexes them into the local SQLite database. It supports
debouncing rapid changes and optional remote sync queuing.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock, Timer
from typing import TYPE_CHECKING, Any

import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from tracertm.storage.markdown_parser import (
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
)

if TYPE_CHECKING:
    from tracertm.storage.local_storage import LocalStorageManager

logger = logging.getLogger(__name__)


class TraceFileWatcher:
    """File watcher for auto-indexing .trace/ directory changes.

    Watches for changes to:
    - .trace/**/*.md - Item markdown files
    - .trace/**/*.yaml - Config and links files
    - .trace/project.yaml - Project metadata

    Features:
    - Debouncing (500ms by default)
    - Auto-indexes changes to SQLite
    - Optional remote sync queuing
    - Real-time status reporting
    """

    def __init__(
        self,
        project_path: Path,
        storage: LocalStorageManager,
        debounce_ms: int = 500,
        auto_sync: bool = False,  # noqa: FBT001,FBT002
    ) -> None:
        """Initialize file watcher.

        Args:
            project_path: Path to project root (containing .trace/)
            storage: LocalStorageManager instance
            debounce_ms: Debounce delay in milliseconds (default: 500)
            auto_sync: Enable auto-queuing for remote sync (default: False)
        """
        self.project_path = Path(project_path).resolve()
        self.trace_path = self.project_path / ".trace"
        self.storage = storage
        self.debounce_delay = debounce_ms / 1000.0
        self.auto_sync = auto_sync

        if not self.trace_path.exists():
            msg = f"No .trace/ directory found at {self.project_path}"
            raise ValueError(msg)

        # Debouncing state
        self._debounce_timers: dict[Path, Timer] = {}
        self._debounce_lock = Lock()

        # Event tracking
        self._events_processed = 0
        self._events_pending = 0
        self._last_event_time: datetime | None = None
        self._changes_by_type: dict[str, int] = defaultdict(int)

        # Watchdog observer
        self._observer: Observer | None = None  # type: ignore[valid-type]  # watchdog Observer type stubs incomplete
        self._event_handler = _TraceEventHandler(self)

        # Load or create project in database
        self._init_project()

    def _init_project(self) -> None:
        """Initialize project in database if not exists."""
        # Try to load project.yaml
        project_yaml_path = self.trace_path / "project.yaml"
        if project_yaml_path.exists():
            try:
                config = parse_config_yaml(project_yaml_path)
                project_name = config.get("name", self.project_path.name)
                description = config.get("description")
            except (FileNotFoundError, OSError, ValueError, yaml.YAMLError, TypeError) as e:
                logger.warning("Failed to parse project.yaml: %s, using defaults", e)
                project_name = self.project_path.name
                description = None
        else:
            project_name = self.project_path.name
            description = None

        # Create or get project in database
        project_storage = self.storage.get_project_storage(project_name)
        self.project = project_storage.create_or_update_project(
            name=project_name,
            description=description,
            metadata={"project_path": str(self.project_path)},
        )
        self.project_storage = project_storage
        self.item_storage = project_storage.get_item_storage(self.project)

        logger.info("Initialized project: %s (ID: %s)", project_name, self.project.id)

    def start(self) -> None:
        """Start watching .trace/ for changes."""
        if self._observer is not None:
            logger.warning("File watcher is already running")
            return

        self._observer = Observer()
        if self._observer is not None:
            self._observer.schedule(self._event_handler, str(self.trace_path), recursive=True)
            self._observer.start()

        logger.info("Started watching: %s", self.trace_path)
        logger.info("Debounce delay: %sms", self.debounce_delay * 1000)
        logger.info("Auto-sync: %s", self.auto_sync)

    def stop(self) -> None:
        """Stop watching."""
        if self._observer is None:
            logger.warning("File watcher is not running")
            return

        # Cancel any pending debounce timers
        with self._debounce_lock:
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()

        self._observer.stop()
        self._observer.join()
        self._observer = None

        logger.info("Stopped watching: %s", self.trace_path)

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._observer is not None and self._observer.is_alive()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about file watcher activity."""
        return {
            "events_processed": self._events_processed,
            "events_pending": self._events_pending,
            "last_event_time": self._last_event_time.isoformat() if self._last_event_time else None,
            "changes_by_type": dict(self._changes_by_type),
            "is_running": self.is_running(),
        }

    def _debounce_event(self, path: Path, event_type: str) -> None:
        """Debounce file system events.

        Args:
            path: Path to changed file
            event_type: Type of event (created, modified, deleted)
        """
        with self._debounce_lock:
            # Cancel existing timer for this path
            if path in self._debounce_timers:
                self._debounce_timers[path].cancel()

            # Create new timer
            timer = Timer(
                self.debounce_delay,
                self._process_event,
                args=(path, event_type),
            )
            self._debounce_timers[path] = timer
            timer.start()

            self._events_pending += 1

    def _process_event(self, path: Path, event_type: str) -> None:
        """Process a file system event after debouncing.

        Args:
            path: Path to changed file
            event_type: Type of event (created, modified, deleted)
        """
        try:
            # Remove from debounce tracking
            with self._debounce_lock:
                self._debounce_timers.pop(path, None)
                self._events_pending -= 1

            # Route to appropriate handler
            if path.suffix == ".md":
                self._handle_item_change(path, event_type)
            elif path.name == "links.yaml":
                self._handle_links_change(path, event_type)
            elif path.name == "project.yaml":
                self._handle_project_change(path, event_type)
            else:
                logger.debug("Ignoring change to: %s", path)

            # Update stats
            self._events_processed += 1
            self._last_event_time = datetime.now(UTC)
            self._changes_by_type[event_type] += 1

        except Exception:
            logger.exception("Error processing %s event for %s", event_type, path)

    def _handle_item_change(self, path: Path, event_type: str) -> None:
        """Handle change to an item markdown file.

        Args:
            path: Path to item .md file
            event_type: Type of event (created, modified, deleted)
        """
        logger.info("Processing %s for item: %s", event_type, path.name)

        if event_type == "deleted":
            # Try to find and soft-delete the item
            # Extract external_id from filename (e.g., EPIC-001.md -> EPIC-001)
            external_id = path.stem

            # Find item by external_id
            session = self.storage.get_session()
            try:
                from tracertm.models import Item

                item = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == self.project.id,
                        Item.item_metadata["external_id"].astext == external_id,
                    )
                    .first()
                )

                if item:
                    self.item_storage.delete_item(str(item.id))
                    logger.info("Deleted item: %s", external_id)
                else:
                    logger.warning("Item not found for deletion: %s", external_id)
            finally:
                session.close()

        else:
            # Parse the markdown file
            try:
                item_data = parse_item_markdown(path)
            except Exception:
                logger.exception("Failed to parse %s", path)
                return

            # Check if item already exists
            session = self.storage.get_session()
            try:
                from tracertm.models import Item

                existing_item = session.get(Item, item_data.id)

                if existing_item:
                    # Update existing item
                    self.item_storage.update_item(
                        item_id=item_data.id,
                        title=item_data.title,
                        description=item_data.description,
                        status=item_data.status,
                        priority=item_data.priority,
                        owner=item_data.owner,
                        metadata={
                            "external_id": item_data.external_id,
                            "tags": item_data.tags,
                            "custom_fields": item_data.custom_fields,
                        },
                    )
                    logger.info("Updated item: %s", item_data.external_id)
                else:
                    # Create new item
                    self.item_storage.create_item(
                        title=item_data.title,
                        item_type=item_data.item_type,
                        item_id=item_data.id,
                        external_id=item_data.external_id,
                        description=item_data.description,
                        status=item_data.status,
                        priority=item_data.priority or "medium",
                        owner=item_data.owner,
                        parent_id=item_data.parent,
                        metadata={
                            "tags": item_data.tags,
                            "custom_fields": item_data.custom_fields,
                        },
                    )
                    logger.info("Created item: %s", item_data.external_id)
            finally:
                session.close()

    def _handle_links_change(self, path: Path, event_type: str) -> None:
        """Handle change to links.yaml file.

        Args:
            path: Path to links.yaml
            event_type: Type of event (created, modified, deleted)
        """
        logger.info("Processing %s for links: %s", event_type, path.name)

        if event_type == "deleted":
            logger.warning("links.yaml deleted, skipping link sync")
            return

        # Parse links.yaml
        try:
            links = parse_links_yaml(path)
        except Exception:
            logger.exception("Failed to parse links.yaml")
            return

        # Sync links to database
        # This is a simplified implementation - a full version would do:
        # 1. Compare with existing links
        # 2. Create new links
        # 3. Delete removed links
        # 4. Update modified links

        logger.info("Parsed %s links from %s", len(links), path.name)
        # tracked: https://github.com/KooshaPari/trace/issues/218

    def _handle_project_change(self, path: Path, event_type: str) -> None:
        """Handle change to project.yaml file.

        Args:
            path: Path to project.yaml
            event_type: Type of event (created, modified, deleted)
        """
        logger.info("Processing %s for project config: %s", event_type, path.name)

        if event_type == "deleted":
            logger.warning("project.yaml deleted, skipping project update")
            return

        # Parse project.yaml
        try:
            config = parse_config_yaml(path)
        except Exception:
            logger.exception("Failed to parse project.yaml")
            return

        # Update project metadata
        project_name = config.get("name", self.project.name)
        description = config.get("description", self.project.description)

        self.project_storage.create_or_update_project(
            name=project_name,
            description=description,
            metadata=config,
        )

        logger.info("Updated project config: %s", project_name)

    def _queue_for_sync(self, entity_type: str, entity_id: str, operation: str, payload: dict[str, Any]) -> None:
        """Queue a change for remote sync.

        Args:
            entity_type: Type of entity (project, item, link)
            entity_id: Entity ID
            operation: Operation (create, update, delete)
            payload: Entity data
        """
        if not self.auto_sync:
            return

        self.storage.queue_sync(entity_type, entity_id, operation, payload)
        logger.debug("Queued for sync: %s %s (%s)", entity_type, entity_id, operation)


class _TraceEventHandler(FileSystemEventHandler):
    """Internal event handler for watchdog."""

    def __init__(self, watcher: TraceFileWatcher) -> None:
        """Initialize event handler.

        Args:
            watcher: Parent TraceFileWatcher instance
        """
        self.watcher = watcher

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation."""
        if event.is_directory:
            return

        src_path = event.src_path if isinstance(event.src_path, str) else event.src_path.decode("utf-8")
        path = Path(src_path)
        if self._should_process(path):
            logger.debug("File created: %s", path)
            self.watcher._debounce_event(path, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file/directory modification."""
        if event.is_directory:
            return

        src_path = event.src_path if isinstance(event.src_path, str) else event.src_path.decode("utf-8")
        path = Path(src_path)
        if self._should_process(path):
            logger.debug("File modified: %s", path)
            self.watcher._debounce_event(path, "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion."""
        if event.is_directory:
            return

        src_path = event.src_path if isinstance(event.src_path, str) else event.src_path.decode("utf-8")
        path = Path(src_path)
        if self._should_process(path):
            logger.debug("File deleted: %s", path)
            self.watcher._debounce_event(path, "deleted")

    def _should_process(self, path: Path) -> bool:
        """Determine if a file should be processed.

        Args:
            path: Path to file

        Returns:
            True if file should be processed
        """
        # Only process .md and .yaml files
        if path.suffix not in {".md", ".yaml", ".yml"}:
            return False

        # Skip hidden files and directories
        if any(part.startswith(".") for part in path.parts if part not in {".trace", ".meta"}):
            return False

        # Skip sync.yaml (local-only)
        return path.name != "sync.yaml"
