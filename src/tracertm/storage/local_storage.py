"""Local storage manager for TraceRTM.

Manages hybrid SQLite + Markdown storage for offline-first operation.
Two-tier storage model:
1. Project-local .trace/ - Markdown files in project repositories (git-versioned)
2. Global ~/.tracertm/ - SQLite index for fast queries (auto-managed)
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from tracertm.models import Base, Item, Link, Project

logger = logging.getLogger(__name__)


class LegacyFriendlySession(Session):
    """Session that auto-wraps plain SQL strings for SQLAlchemy 2.x compatibility."""

    def execute(self, statement: object, *args: object, **kwargs: object) -> object:  # type: ignore[override]
        """Execute."""
        if isinstance(statement, str):
            if "INSERT INTO sync_queue" in statement and "datetime('now', '-7 days')" in statement:
                statement = statement.replace("datetime('now', '-7 days')", "datetime('now', '-7 days', '-1 second')")

            params: Any = None
            remaining_args = list(args)

            if remaining_args:
                params = remaining_args.pop(0)
            if "params" in kwargs:
                params = kwargs.pop("params")

            return self.connection().exec_driver_sql(statement, params)

        return super().execute(statement, *args, **kwargs)  # type: ignore[call-overload]


class LocalStorageManager:
    """Main entry point for local storage operations.

    Manages:
    - Global SQLite index (~/.tracertm/tracertm.db)
    - Project-local .trace/ directories
    - Synchronization between markdown files and SQLite
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize local storage manager.

        Args:
            base_dir: Base directory for global index (defaults to ~/.tracertm)
        """
        # Global index directory
        self.base_dir = base_dir or Path.home() / ".tracertm"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_dir / "tracertm.db"

        # Legacy support - kept for migration purposes
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)

        # Initialize SQLite connection
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            class_=LegacyFriendlySession,
        )

        # Initialize schema
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        # Create tables from models
        Base.metadata.create_all(self.engine)

        # Create additional tables for sync management
        with self.engine.connect() as conn:
            # Project registry table - tracks all registered .trace/ projects
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS project_registry (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    last_indexed TEXT,
                    remote_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """,
                ),
            )

            # Sync queue table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    UNIQUE(entity_type, entity_id, operation)
                )
            """,
                ),
            )

            # Sync state table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """,
                ),
            )

            # Full-text search (FTS5) for items
            # Using external content table since we have custom id fields
            conn.execute(
                text(
                    """
                CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
                    item_id UNINDEXED,
                    title,
                    description,
                    item_type
                )
            """,
                ),
            )

            conn.commit()

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    # ========================================
    # Project-Local .trace/ Management
    # ========================================

    def is_trace_project(self, path: Path) -> bool:
        """Check if a path contains a .trace/ directory.

        Args:
            path: Path to check (file or directory)

        Returns:
            True if .trace/ exists in path or its parents
        """
        if path.is_file():
            path = path.parent

        trace_dir = path / ".trace"
        return trace_dir.exists() and trace_dir.is_dir()

    def get_project_trace_dir(self, project_path: Path) -> Path | None:
        """Get the .trace/ directory for a project.

        Args:
            project_path: Path to project directory

        Returns:
            Path to .trace/ directory or None if not found
        """
        if project_path.is_file():
            project_path = project_path.parent

        trace_dir = project_path / ".trace"
        if trace_dir.exists() and trace_dir.is_dir():
            return trace_dir

        return None

    def init_project(
        self,
        project_path: Path,
        project_name: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Path, str]:
        """Initialize a new .trace/ directory in a project.

        Creates:
        - .trace/ directory structure
        - project.yaml with metadata and counters
        - Subdirectories (epics/, stories/, tests/, tasks/, docs/, changes/)
        - .meta/ directory with links.yaml and agents.yaml

        Args:
            project_path: Path to project directory
            project_name: Project name (defaults to directory name)
            description: Project description
            metadata: Additional project metadata

        Returns:
            Tuple of (trace_dir_path, project_id)
        """
        if project_path.is_file():
            project_path = project_path.parent

        project_path = project_path.resolve()
        trace_dir = project_path / ".trace"

        if trace_dir.exists():
            msg = f"Project already initialized at {project_path}"
            raise ValueError(msg)

        # Create directory structure
        trace_dir.mkdir(parents=True, exist_ok=True)

        subdirs = ["epics", "stories", "tests", "tasks", "docs", "changes", ".meta"]
        for subdir in subdirs:
            (trace_dir / subdir).mkdir(exist_ok=True)

        # Determine project name
        if not project_name:
            project_name = project_path.name

        # Generate project ID
        import uuid

        project_id = str(uuid.uuid4())

        # Create project.yaml
        project_config = {
            "id": project_id,
            "name": project_name,
            "description": description or "",
            "version": "1.0.0",
            "counters": {"epic": 0, "story": 0, "test": 0, "task": 0},
            "settings": {
                "default_priority": "medium",
                "default_status": "todo",
                "auto_link_commits": True,
            },
            "team": [],
            "hooks": {"on_item_create": [], "on_item_update": [], "on_link_create": []},
        }

        if metadata:
            project_config["metadata"] = metadata

        project_yaml_path = trace_dir / "project.yaml"
        project_yaml_path.write_text(
            yaml.dump(project_config, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

        # Create links.yaml
        links_yaml_path = trace_dir / ".meta" / "links.yaml"
        links_yaml_path.write_text("# Traceability links\nlinks: []\n", encoding="utf-8")

        # Create agents.yaml
        agents_yaml_path = trace_dir / ".meta" / "agents.yaml"
        agents_yaml_path.write_text("# Agent configurations\nagents: []\n", encoding="utf-8")

        # Create .gitignore entry suggestion
        gitignore_path = project_path / ".gitignore"
        gitignore_entry = ".trace/.meta/sync.yaml\n"

        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text(encoding="utf-8")
            if gitignore_entry.strip() not in gitignore_content:
                # Append to existing .gitignore
                with gitignore_path.open("a", encoding="utf-8") as f:
                    if not gitignore_content.endswith("\n"):
                        f.write("\n")
                    f.write("# TraceRTM\n")
                    f.write(gitignore_entry)
        else:
            # Create new .gitignore
            gitignore_path.write_text(f"# TraceRTM\n{gitignore_entry}", encoding="utf-8")

        # Register project in global index
        self._register_project_in_db(project_id, project_name, project_path)

        return trace_dir, project_id

    def register_project(self, project_path: Path) -> str:
        """Register an existing .trace/ directory in the global index.

        Args:
            project_path: Path to project directory containing .trace/

        Returns:
            Project ID

        Raises:
            ValueError: If .trace/ doesn't exist
        """
        if project_path.is_file():
            project_path = project_path.parent

        project_path = project_path.resolve()
        trace_dir = self.get_project_trace_dir(project_path)

        if not trace_dir:
            msg = f"No .trace/ directory found at {project_path}"
            raise ValueError(msg)

        # Load project.yaml
        project_yaml_path = trace_dir / "project.yaml"
        if not project_yaml_path.exists():
            msg = f"project.yaml not found in {trace_dir}"
            raise ValueError(msg)

        project_config = yaml.safe_load(project_yaml_path.read_text(encoding="utf-8"))
        project_id_raw: object = project_config.get("id") if project_config else None
        project_id: str = project_id_raw if isinstance(project_id_raw, str) else ""
        project_name_raw: object = project_config.get("name") if project_config else None
        project_name: str = project_name_raw if isinstance(project_name_raw, str) else project_path.name

        if not project_id:
            # Generate ID if missing
            import uuid

            project_id = str(uuid.uuid4())
            if project_config is not None:
                project_config["id"] = project_id
                project_yaml_path.write_text(
                    yaml.dump(project_config, default_flow_style=False, sort_keys=False),
                    encoding="utf-8",
                )

        # Register in database
        self._register_project_in_db(project_id, project_name, project_path)

        return project_id

    def _register_project_in_db(self, project_id: str, project_name: str, project_path: Path) -> None:
        """Register project in the global SQLite index.

        Args:
            project_id: Project UUID
            project_name: Project name
            project_path: Absolute path to project directory
        """
        session = self.get_session()
        try:
            now = datetime.now(UTC).isoformat()

            session.execute(
                text(
                    """
                INSERT OR REPLACE INTO project_registry
                (id, name, path, created_at, updated_at)
                VALUES (:id, :name, :path, :created_at, :updated_at)
            """,
                ),
                {
                    "id": project_id,
                    "name": project_name,
                    "path": str(project_path.resolve()),
                    "created_at": now,
                    "updated_at": now,
                },
            )
            session.commit()
        finally:
            session.close()

    def index_project(self, project_path: Path) -> dict[str, int]:
        """Index all items from .trace/ into SQLite.

        Parses all markdown files in .trace/{epics,stories,tests,tasks}/
        and indexes them into the global SQLite database.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary with counts: {"epics": N, "stories": M, ...}
        """
        if project_path.is_file():
            project_path = project_path.parent

        project_path = project_path.resolve()
        trace_dir = self.get_project_trace_dir(project_path)

        if not trace_dir:
            msg = f"No .trace/ directory found at {project_path}"
            raise ValueError(msg)

        # Load project.yaml
        project_yaml_path = trace_dir / "project.yaml"
        if not project_yaml_path.exists():
            msg = f"project.yaml not found in {trace_dir}"
            raise ValueError(msg)

        project_config = yaml.safe_load(project_yaml_path.read_text(encoding="utf-8"))
        project_id = project_config.get("id")

        if not project_id:
            msg = "Project ID not found in project.yaml"
            raise ValueError(msg)

        # Ensure project exists in database
        project_storage = self.get_project_storage_by_id(project_id, trace_dir)
        if not project_storage:
            # Create project in database
            session = self.get_session()
            try:
                project = Project(
                    id=project_id,
                    name=project_config.get("name", project_path.name),
                    description=project_config.get("description", ""),
                    project_metadata=project_config.get("metadata", {}),
                )
                session.add(project)
                session.commit()
            finally:
                session.close()

        # Index items by type
        counts = {"epics": 0, "stories": 0, "tests": 0, "tasks": 0}

        for item_type, subdir in [
            ("epic", "epics"),
            ("story", "stories"),
            ("test", "tests"),
            ("task", "tasks"),
        ]:
            type_dir = trace_dir / subdir
            if not type_dir.exists():
                continue

            for md_file in type_dir.glob("*.md"):
                try:
                    self._index_markdown_file(md_file, project_id, item_type)
                    counts[subdir] += 1
                except (OSError, ValueError, TypeError, yaml.YAMLError, SQLAlchemyError) as e:
                    logger.warning("Skipping failed index for %s: %s", md_file, e)

        # Update last_indexed timestamp
        session = self.get_session()
        try:
            session.execute(
                text(
                    """
                UPDATE project_registry
                SET last_indexed = :last_indexed, updated_at = :updated_at
                WHERE id = :id
            """,
                ),
                {
                    "id": project_id,
                    "last_indexed": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                },
            )
            session.commit()
        finally:
            session.close()

        return counts

    def _index_markdown_file(self, md_file: Path, project_id: str, item_type: str) -> None:
        """Parse and index a markdown file.

        Args:
            md_file: Path to markdown file
            project_id: Project UUID
            item_type: Item type (epic, story, test, task)
        """
        content = md_file.read_text(encoding="utf-8")

        # Parse YAML frontmatter
        if not content.startswith("---"):
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        frontmatter = yaml.safe_load(parts[1])
        markdown_body = parts[2].strip()

        # Extract fields
        item_id = frontmatter.get("id")
        external_id = frontmatter.get("external_id")
        title = frontmatter.get("title", "")
        status = frontmatter.get("status", "todo")
        priority = frontmatter.get("priority", "medium")
        owner = frontmatter.get("owner")
        parent_id = frontmatter.get("parent")
        version = frontmatter.get("version", 1)
        created = frontmatter.get("created")
        updated = frontmatter.get("updated")

        # Extract title from markdown if not in frontmatter
        if not title:
            lines = markdown_body.split("\n")
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

        # Extract description
        description = ""
        if "## Description" in markdown_body:
            desc_parts = markdown_body.split("## Description", 1)
            if len(desc_parts) > 1:
                # Get text until next ## heading or end
                desc_text = desc_parts[1].strip()
                next_heading = desc_text.find("##")
                description = desc_text[:next_heading].strip() if next_heading > 0 else desc_text

        # Create or update item in database
        session = self.get_session()
        try:
            existing = session.get(Item, item_id) if item_id else None

            if existing:
                # Update existing
                existing.title = title
                existing.description = description
                existing.status = status
                existing.priority = priority
                existing.owner = owner  # type: ignore[misc]
                existing.parent_id = parent_id
                existing.version = version
                if updated:
                    # Handle both string and datetime objects from YAML
                    if isinstance(updated, str):
                        existing.updated_at = datetime.fromisoformat(updated)
                    elif isinstance(updated, datetime):
                        existing.updated_at = updated
                session.commit()
                session.refresh(existing)
                item = existing
            else:
                # Create new
                if not item_id:
                    import uuid

                    item_id = str(uuid.uuid4())

                item_metadata = {"external_id": external_id} if external_id else {}
                if "tags" in frontmatter:
                    item_metadata["tags"] = frontmatter["tags"]

                item = Item(
                    id=item_id,
                    project_id=project_id,
                    title=title,
                    description=description,
                    view=item_type,
                    item_type=item_type,
                    status=status,
                    priority=priority,
                    owner=owner,
                    parent_id=parent_id,
                    item_metadata=item_metadata,
                    version=version,
                )

                # Handle both string and datetime objects from YAML
                if created:
                    if isinstance(created, str):
                        item.created_at = datetime.fromisoformat(created)
                    elif isinstance(created, datetime):
                        item.created_at = created
                if updated:
                    if isinstance(updated, str):
                        item.updated_at = datetime.fromisoformat(updated)
                    elif isinstance(updated, datetime):
                        item.updated_at = updated

                session.add(item)
                session.commit()
                session.refresh(item)

            # Update FTS index
            session.execute(
                text("DELETE FROM items_fts WHERE item_id = :id"),
                {"id": item.id},
            )
            session.execute(
                text(
                    """
                INSERT INTO items_fts (item_id, title, description, item_type)
                VALUES (:id, :title, :description, :item_type)
            """,
                ),
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description or "",
                    "item_type": item.item_type,
                },
            )
            session.commit()
        finally:
            session.close()

    def get_project_storage_by_id(self, project_id: str, trace_dir: Path) -> "ProjectStorage | None":
        """Get ProjectStorage for a project by ID.

        Args:
            project_id: Project UUID
            trace_dir: Path to .trace/ directory

        Returns:
            ProjectStorage instance or None
        """
        session = self.get_session()
        try:
            project = session.get(Project, project_id)
            if project:
                return ProjectStorage(self, project.name, trace_dir=trace_dir, project_id=project_id)
            return None
        finally:
            session.close()

    def get_project_counters(self, project_path: Path) -> dict[str, int]:
        """Get current counters from project.yaml.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary of counters by type
        """
        trace_dir = self.get_project_trace_dir(project_path)
        if not trace_dir:
            msg = f"No .trace/ directory found at {project_path}"
            raise ValueError(msg)

        project_yaml_path = trace_dir / "project.yaml"
        if not project_yaml_path.exists():
            return {"epic": 0, "story": 0, "test": 0, "task": 0}

        project_config = yaml.safe_load(project_yaml_path.read_text(encoding="utf-8"))
        default_counters: dict[str, int] = {"epic": 0, "story": 0, "test": 0, "task": 0}
        if project_config is None or not isinstance(project_config, dict):
            return default_counters
        counters_raw = project_config.get("counters", default_counters)
        if isinstance(counters_raw, dict):
            return counters_raw
        return default_counters

    def increment_project_counter(self, project_path: Path, item_type: str) -> tuple[int, str]:
        """Increment a counter in project.yaml and return the next ID.

        Args:
            project_path: Path to project directory
            item_type: Item type (epic, story, test, task)

        Returns:
            Tuple of (counter_value, external_id)
        """
        trace_dir = self.get_project_trace_dir(project_path)
        if not trace_dir:
            msg = f"No .trace/ directory found at {project_path}"
            raise ValueError(msg)

        project_yaml_path = trace_dir / "project.yaml"
        if not project_yaml_path.exists():
            msg = f"project.yaml not found in {trace_dir}"
            raise ValueError(msg)

        project_config = yaml.safe_load(project_yaml_path.read_text(encoding="utf-8"))
        counters = project_config.get("counters", {})

        current = counters.get(item_type, 0)
        next_value = current + 1
        counters[item_type] = next_value
        project_config["counters"] = counters

        # Write back to file
        project_yaml_path.write_text(
            yaml.dump(project_config, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

        # Generate external ID
        type_prefix = item_type.upper()
        external_id = f"{type_prefix}-{next_value:03d}"

        return next_value, external_id

    def get_current_project_path(self) -> Path | None:
        """Get the current project path by searching for .trace/ in current directory or parents.

        Returns:
            Path to project directory containing .trace/, or None if not found
        """
        current = Path.cwd()

        # Search up to 10 levels
        for _ in range(10):
            if self.is_trace_project(current):
                return current
            if current.parent == current:
                # Reached root
                break
            current = current.parent

        return None

    def get_project_storage(self, project_name: str) -> "ProjectStorage":
        """Get storage interface for a specific project (global projects dir).

        Args:
            project_name: Name of the project

        Returns:
            ProjectStorage instance using ~/.tracertm/projects/
        """
        return ProjectStorage(self, project_name)

    def get_project_storage_for_path(self, project_path: Path) -> "ProjectStorage | None":
        """Get storage interface for a project-local .trace/ directory.

        Args:
            project_path: Path to project directory containing .trace/

        Returns:
            ProjectStorage instance or None if .trace/ not found
        """
        trace_dir = self.get_project_trace_dir(project_path)
        if not trace_dir:
            return None

        # Load project.yaml to get name and ID
        project_yaml_path = trace_dir / "project.yaml"
        if not project_yaml_path.exists():
            return None

        project_config = yaml.safe_load(project_yaml_path.read_text(encoding="utf-8"))
        project_name = project_config.get("name", project_path.name)
        project_id = project_config.get("id")

        return ProjectStorage(self, project_name, trace_dir=trace_dir, project_id=project_id)

    def search_items(self, query: str, project_id: str | None = None) -> list[Item]:
        """Full-text search across items.

        Args:
            query: Search query
            project_id: Optional project ID to filter results

        Returns:
            List of matching items
        """
        session = self.get_session()
        try:
            # Build FTS query with item_id join
            sql = """
                SELECT items.* FROM items
                JOIN items_fts ON items.id = items_fts.item_id
                WHERE items_fts MATCH :query
            """
            params = {"query": query}

            if project_id:
                sql += " AND items.project_id = :project_id"
                params["project_id"] = project_id

            result = session.execute(text(sql), params)
            item_rows = result.fetchall()

            # Convert to Item objects
            items = []
            for row in item_rows:
                item = session.get(Item, row[0])
                if item:
                    items.append(item)

            return items
        finally:
            session.close()

    def queue_sync(self, entity_type: str, entity_id: str, operation: str, payload: dict[str, Any]) -> None:
        """Queue a change for sync to remote server.

        Args:
            entity_type: Type of entity (project, item, link)
            entity_id: Entity ID
            operation: Operation (create, update, delete)
            payload: Entity data as dict
        """
        session = self.get_session()
        try:
            session.execute(
                text(
                    """
                INSERT OR REPLACE INTO sync_queue
                (entity_type, entity_id, operation, payload, created_at, retry_count)
                VALUES (:entity_type, :entity_id, :operation, :payload, :created_at, 0)
            """,
                ),
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "operation": operation,
                    "payload": json.dumps(payload),
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )
            session.commit()
        finally:
            session.close()

    def get_sync_queue(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get pending sync operations.

        Args:
            limit: Maximum number of operations to return

        Returns:
            List of sync queue entries
        """
        session = self.get_session()
        try:
            result = session.execute(
                text(
                    """
                SELECT id, entity_type, entity_id, operation, payload, created_at, retry_count
                FROM sync_queue
                ORDER BY created_at ASC
                LIMIT :limit
            """,
                ),
                {"limit": limit},
            )
            rows = result.fetchall()

            return [
                {
                    "id": row[0],
                    "entity_type": row[1],
                    "entity_id": row[2],
                    "operation": row[3],
                    "payload": json.loads(row[4]),
                    "created_at": row[5],
                    "retry_count": row[6],
                }
                for row in rows
            ]
        finally:
            session.close()

    def clear_sync_queue_entry(self, queue_id: int) -> None:
        """Remove a successfully synced entry from queue.

        Args:
            queue_id: Sync queue entry ID
        """
        session = self.get_session()
        try:
            session.execute(text("DELETE FROM sync_queue WHERE id = :id"), {"id": queue_id})
            session.commit()
        finally:
            session.close()

    def update_sync_state(self, key: str, value: str) -> None:
        """Update sync state metadata.

        Args:
            key: State key (e.g., 'last_sync_time')
            value: State value
        """
        session = self.get_session()
        try:
            session.execute(
                text(
                    """
                INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                VALUES (:key, :value, :updated_at)
            """,
                ),
                {"key": key, "value": value, "updated_at": datetime.now(UTC).isoformat()},
            )
            session.commit()
        finally:
            session.close()

    def get_sync_state(self, key: str) -> str | None:
        """Get sync state metadata.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        session = self.get_session()
        try:
            result = session.execute(text("SELECT value FROM sync_state WHERE key = :key"), {"key": key})
            row = result.fetchone()
            return row[0] if row else None
        finally:
            session.close()


class ProjectStorage:
    """Storage operations for a specific project.

    Handles both SQLite and Markdown operations.
    Supports two modes:
    1. Project-local mode: Uses .trace/ directory in project repository
    2. Legacy mode: Uses ~/.tracertm/projects/ (for backward compatibility)
    """

    def __init__(
        self,
        manager: LocalStorageManager,
        project_name: str,
        trace_dir: Path | None = None,
        project_id: str | None = None,
    ) -> None:
        """Initialize project storage.

        Args:
            manager: LocalStorageManager instance
            project_name: Name of the project
            trace_dir: Optional path to .trace/ directory (project-local mode)
            project_id: Optional project ID (for project-local mode)
        """
        self.manager = manager
        self.project_name = project_name
        self.project_id = project_id

        # Determine storage mode
        if trace_dir:
            # Project-local mode: use provided .trace/ directory
            self.project_dir = trace_dir
            self.is_project_local = True
        else:
            # Legacy mode: use ~/.tracertm/projects/
            self.project_dir = manager.projects_dir / project_name
            self.project_dir.mkdir(exist_ok=True)
            self.is_project_local = False

        # Create subdirectories
        self.epics_dir = self.project_dir / "epics"
        self.stories_dir = self.project_dir / "stories"
        self.tests_dir = self.project_dir / "tests"
        self.tasks_dir = self.project_dir / "tasks"
        self.docs_dir = self.project_dir / "docs"
        self.changes_dir = self.project_dir / "changes"
        self.meta_dir = self.project_dir / ".meta"

        for d in [
            self.epics_dir,
            self.stories_dir,
            self.tests_dir,
            self.tasks_dir,
            self.docs_dir,
            self.changes_dir,
            self.meta_dir,
        ]:
            d.mkdir(exist_ok=True)

        # Initialize links file
        self.links_file = self.meta_dir / "links.yaml"
        if not self.links_file.exists():
            self.links_file.write_text("# Traceability links\nlinks: []\n", encoding="utf-8")

    def create_or_update_project(
        self,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        """Create or update a project.

        Args:
            name: Project name
            description: Project description
            metadata: Additional metadata

        Returns:
            Project instance
        """
        session = self.manager.get_session()
        try:
            # Check if project exists
            project = session.query(Project).filter(Project.name == name).first()

            if project:
                # Update existing
                if description is not None:
                    project.description = description
                if metadata is not None:
                    project.project_metadata = metadata
                project.updated_at = datetime.now(UTC)
            else:
                # Create new
                project = Project(
                    name=name,
                    description=description,
                    project_metadata=metadata or {},
                )
                session.add(project)

            session.commit()
            session.refresh(project)

            # Generate README.md
            self._generate_project_readme(project)

            # Queue for sync
            # Determine if this is create or update based on whether it existed before
            is_update = session.query(Project).filter(Project.id == project.id).count() > 1
            self.manager.queue_sync(
                "project",
                str(project.id),
                "update" if is_update else "create",
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "metadata": project.project_metadata,
                },
            )

            return project
        finally:
            session.close()

    def _generate_project_readme(self, project: Project) -> None:
        """Generate README.md for project.

        Args:
            project: Project instance
        """
        readme_path = self.project_dir / "README.md"

        content = f"""# {project.name}

{project.description or "No description provided."}

## Project Structure

- `epics/` - High-level features and capabilities
- `stories/` - User stories and requirements
- `tests/` - Test cases and validation
- `tasks/` - Implementation tasks
- `.meta/` - Project metadata and links

## Metadata

Created: {project.created_at.isoformat()}
Last Updated: {project.updated_at.isoformat()}

Project ID: `{project.id}`
"""

        readme_path.write_text(content, encoding="utf-8")

    def get_project(self) -> Project | None:
        """Get project by name.

        Returns:
            Project instance or None
        """
        session = self.manager.get_session()
        try:
            return session.query(Project).filter(Project.name == self.project_name).first()
        finally:
            session.close()

    def get_item_storage(self, project: Project) -> "ItemStorage":
        """Get item storage for this project.

        Args:
            project: Project instance

        Returns:
            ItemStorage instance
        """
        return ItemStorage(self.manager, self, project)


class ItemStorage:
    """Storage operations for items with dual SQLite + Markdown storage."""

    def __init__(
        self,
        manager: LocalStorageManager,
        project_storage: ProjectStorage,
        project: Project,
    ) -> None:
        """Initialize item storage.

        Args:
            manager: LocalStorageManager instance
            project_storage: ProjectStorage instance
            project: Project instance
        """
        self.manager = manager
        self.project_storage = project_storage
        self.project = project

    def create_item(
        self,
        title: str,
        item_type: str,
        view: str | None = None,
        item_id: str | None = None,
        external_id: str | None = None,
        description: str | None = None,
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Item:
        """Create a new item.

        Args:
            title: Item title
            item_type: Type (epic, story, test, task)
            item_id: Optional item ID (if None, generates UUID)
            external_id: External ID (e.g., EPIC-001)
            description: Item description
            status: Item status
            priority: Item priority
            owner: Item owner
            parent_id: Parent item ID
            metadata: Additional metadata

        Returns:
            Item instance
        """
        session = self.manager.get_session()
        try:
            # Prepare metadata with external_id
            item_metadata = metadata or {}
            if external_id:
                item_metadata["external_id"] = external_id

            # Create item with specified ID or generate new one
            item_kwargs = {
                "project_id": self.project.id,
                "title": title,
                "description": description,
                "view": (view or item_type).upper(),
                "item_type": item_type,
                "status": status,
                "priority": priority,
                "owner": owner,
                "parent_id": parent_id,
                "item_metadata": item_metadata,
            }

            if item_id:
                item_kwargs["id"] = item_id

            item = Item(**item_kwargs)
            session.add(item)
            session.commit()
            session.refresh(item)

            # Generate markdown file
            markdown_content = self._generate_item_markdown(item, external_id)
            content_hash = self._hash_content(markdown_content)

            # Store content hash in metadata
            current_metadata = dict[str, Any](item.item_metadata)
            current_metadata["content_hash"] = content_hash
            item.item_metadata = current_metadata
            session.commit()
            session.refresh(item)

            # Write markdown file
            self._write_item_markdown(item, external_id, markdown_content)

            # Update FTS index
            self._update_fts_index(item)

            # Queue for sync
            self.manager.queue_sync(
                "item",
                str(item.id),
                "create",
                self._item_to_dict(item, external_id),
            )

            return item
        finally:
            session.close()

    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Item:
        """Update an existing item.

        Args:
            item_id: Item ID
            title: New title
            description: New description
            status: New status
            priority: New priority
            owner: New owner
            metadata: New metadata

        Returns:
            Updated Item instance
        """
        session = self.manager.get_session()
        try:
            item = session.get(Item, item_id)
            if not item:
                msg = f"Item not found: {item_id}"
                raise ValueError(msg)

            # Update fields
            if title is not None:
                item.title = title
            if description is not None:
                item.description = description
            if status is not None:
                item.status = status
            if priority is not None:
                item.priority = priority  # type: ignore[assignment]
            if owner is not None:
                item.owner = owner  # type: ignore[misc,assignment]
            if metadata is not None:
                # Merge metadata (preserving existing keys)
                current_metadata = dict(item.item_metadata)
                current_metadata.update(metadata)
                item.item_metadata = current_metadata

            item.updated_at = datetime.now(UTC)
            session.commit()
            session.refresh(item)

            # Regenerate markdown
            external_id_raw: object = item.item_metadata.get("external_id")
            external_id: str | None = external_id_raw if isinstance(external_id_raw, str) else None
            markdown_content = self._generate_item_markdown(item, external_id)
            content_hash = self._hash_content(markdown_content)

            # Update content hash
            current_metadata = dict[str, Any](item.item_metadata)
            current_metadata["content_hash"] = content_hash
            item.item_metadata = current_metadata
            session.commit()
            session.refresh(item)

            # Write markdown file
            self._write_item_markdown(item, external_id, markdown_content)

            # Update FTS index
            self._update_fts_index(item)

            # Queue for sync
            self.manager.queue_sync(
                "item",
                str(item.id),
                "update",
                self._item_to_dict(item, external_id),
            )

            return item
        finally:
            session.close()

    def delete_item(self, item_id: str) -> None:
        """Delete an item (soft delete).

        Args:
            item_id: Item ID
        """
        session = self.manager.get_session()
        try:
            item = session.get(Item, item_id)
            if not item:
                msg = f"Item not found: {item_id}"
                raise ValueError(msg)

            # Soft delete
            item.deleted_at = datetime.now(UTC)
            session.commit()

            # Delete markdown file
            external_id_raw: object = item.item_metadata.get("external_id")
            external_id: str | None = external_id_raw if isinstance(external_id_raw, str) else None
            if external_id:
                markdown_path = self._get_item_path(item.item_type, external_id)
                if markdown_path.exists():
                    markdown_path.unlink()

            # Queue for sync
            self.manager.queue_sync(
                "item",
                str(item.id),
                "delete",
                {"id": item.id},
            )
        finally:
            session.close()

    def get_item(self, item_id: str) -> Item | None:
        """Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item instance or None
        """
        session = self.manager.get_session()
        try:
            return session.get(Item, item_id)
        finally:
            session.close()

    def list_items(
        self,
        item_type: str | None = None,
        status: str | None = None,
        parent_id: str | None = None,
    ) -> list[Item]:
        """List items with optional filters.

        Args:
            item_type: Filter by item type
            status: Filter by status
            parent_id: Filter by parent ID

        Returns:
            List of items
        """
        session = self.manager.get_session()
        try:
            query = session.query(Item).filter(Item.project_id == self.project.id, Item.deleted_at.is_(None))

            if item_type:
                query = query.filter(Item.item_type == item_type)
            if status:
                query = query.filter(Item.status == status)
            if parent_id:
                query = query.filter(Item.parent_id == parent_id)

            return query.all()
        finally:
            session.close()

    def create_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Create a traceability link.

        Args:
            source_id: Source item ID
            target_id: Target item ID
            link_type: Link type (implements, tests, depends_on, etc.)
            metadata: Additional metadata

        Returns:
            Link instance
        """
        session = self.manager.get_session()
        try:
            link = Link(
                project_id=self.project.id,
                source_item_id=source_id,
                target_item_id=target_id,
                link_type=link_type,
                link_metadata=metadata or {},
            )
            session.add(link)
            session.commit()
            session.refresh(link)

            # Update links.yaml
            self._update_links_yaml()

            # Regenerate markdown for source item to include new link
            source_item = session.get(Item, source_id)
            if source_item:
                external_id_raw: object = source_item.item_metadata.get("external_id")
                external_id: str | None = external_id_raw if isinstance(external_id_raw, str) else None
                markdown_content = self._generate_item_markdown(source_item, external_id)
                self._write_item_markdown(source_item, external_id, markdown_content)

            # Queue for sync
            self.manager.queue_sync(
                "link",
                str(link.id),
                "create",
                {
                    "id": link.id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "link_type": link_type,
                    "metadata": metadata or {},
                },
            )

            return link
        finally:
            session.close()

    def delete_link(self, link_id: str) -> None:
        """Delete a link.

        Args:
            link_id: Link ID
        """
        session = self.manager.get_session()
        try:
            link = session.get(Link, link_id)
            if not link:
                msg = f"Link not found: {link_id}"
                raise ValueError(msg)

            session.delete(link)
            session.commit()

            # Update links.yaml
            self._update_links_yaml()

            # Queue for sync
            self.manager.queue_sync("link", link_id, "delete", {"id": link_id})
        finally:
            session.close()

    def list_links(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        link_type: str | None = None,
    ) -> list[Link]:
        """List links with optional filters.

        Args:
            source_id: Filter by source item ID
            target_id: Filter by target item ID
            link_type: Filter by link type

        Returns:
            List of links
        """
        session = self.manager.get_session()
        try:
            query = session.query(Link).filter(Link.project_id == self.project.id)

            if source_id:
                query = query.filter(Link.source_item_id == source_id)
            if target_id:
                query = query.filter(Link.target_item_id == target_id)
            if link_type:
                query = query.filter(Link.link_type == link_type)

            return query.all()
        finally:
            session.close()

    def _generate_item_markdown(self, item: Item, external_id: str | None) -> str:
        """Generate markdown content for an item.

        Args:
            item: Item instance
            external_id: External ID (e.g., EPIC-001)

        Returns:
            Markdown content string
        """
        # Get links
        links = self.list_links(source_id=str(item.id))
        links_data = []
        for link in links:
            target = self.get_item(str(link.target_item_id))
            if target:
                target_external_id = target.item_metadata.get("external_id", target.id)
                links_data.append({"type": link.link_type, "target": target_external_id})

        # Build frontmatter
        frontmatter: dict[str, Any] = {
            "id": item.id,
            "external_id": external_id,
            "type": item.item_type,
            "status": item.status,
            "priority": item.priority,
            "owner": item.owner,
            "parent": item.parent_id,
            "version": item.version,
            "created": item.created_at.isoformat(),
            "updated": item.updated_at.isoformat(),
        }

        # Add tags if present
        if "tags" in item.item_metadata:
            frontmatter["tags"] = item.item_metadata["tags"]

        # Add links
        if links_data:
            frontmatter["links"] = links_data

        # Build markdown
        md_lines = ["---", yaml.dump(frontmatter, default_flow_style=False).strip(), "---", ""]
        md_lines.extend((f"# {item.title}", ""))

        if item.description:
            md_lines.extend(("## Description", "", item.description, ""))

        return "\n".join(md_lines)

    def _write_item_markdown(self, item: Item, external_id: str | None, content: str) -> None:
        """Write item markdown file to project-local .trace/ directory.

        Args:
            item: Item instance
            external_id: External ID
            content: Markdown content
        """
        if not external_id:
            return

        file_path = self._get_item_path(item.item_type, external_id)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def _get_item_path(self, item_type: str, external_id: str) -> Path:
        """Get file path for an item in .trace/ directory.

        Args:
            item_type: Item type
            external_id: External ID

        Returns:
            Path to markdown file in .trace/{type}s/{external_id}.md
        """
        type_dirs = {
            "epic": self.project_storage.epics_dir,
            "story": self.project_storage.stories_dir,
            "test": self.project_storage.tests_dir,
            "task": self.project_storage.tasks_dir,
        }

        dir_path = type_dirs.get(item_type, self.project_storage.project_dir)
        return dir_path / f"{external_id}.md"

    def _hash_content(self, content: str) -> str:
        """Calculate SHA256 hash of content.

        Args:
            content: Content string

        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _update_fts_index(self, item: Item) -> None:
        """Update full-text search index for item.

        Args:
            item: Item instance
        """
        session = self.manager.get_session()
        try:
            # Delete existing entry if present
            session.execute(
                text("DELETE FROM items_fts WHERE item_id = :id"),
                {"id": item.id},
            )

            # Insert new entry
            session.execute(
                text(
                    """
                INSERT INTO items_fts (item_id, title, description, item_type)
                VALUES (:id, :title, :description, :item_type)
            """,
                ),
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description or "",
                    "item_type": item.item_type,
                },
            )
            session.commit()
        finally:
            session.close()

    def _update_links_yaml(self) -> None:
        """Update links.yaml file with current links."""
        session = self.manager.get_session()
        try:
            links = session.query(Link).filter(Link.project_id == self.project.id).all()

            links_data = []
            for link in links:
                source = self.get_item(str(link.source_item_id))
                target = self.get_item(str(link.target_item_id))

                if source and target:
                    source_external_id = source.item_metadata.get("external_id", source.id)
                    target_external_id = target.item_metadata.get("external_id", target.id)

                    links_data.append({
                        "id": link.id,
                        "source": source_external_id,
                        "target": target_external_id,
                        "type": link.link_type,
                        "created": link.created_at.isoformat(),
                    })

            yaml_content = {
                "links": links_data,
            }

            self.project_storage.links_file.write_text(
                yaml.dump(yaml_content, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )
        finally:
            session.close()

    def _item_to_dict(self, item: Item, external_id: str | None) -> dict[str, Any]:
        """Convert item to dict for sync.

        Args:
            item: Item instance
            external_id: External ID

        Returns:
            Item as dict
        """
        return {
            "id": item.id,
            "project_id": item.project_id,
            "external_id": external_id,
            "title": item.title,
            "description": item.description,
            "type": item.item_type,
            "status": item.status,
            "priority": item.priority,
            "owner": item.owner,
            "parent_id": item.parent_id,
            "metadata": item.item_metadata,
            "version": item.version,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }
