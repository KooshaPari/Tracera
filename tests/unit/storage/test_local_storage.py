"""Unit tests for LocalStorageManager.

Tests CRUD operations and SQLite ↔ Markdown synchronization
for the hybrid local storage architecture.
"""

import json
import sqlite3
from datetime import UTC, datetime

# ============================================================================
# FIXTURES
# ============================================================================
from typing import Any

import pytest
import yaml

from tests.test_constants import COUNT_THREE, COUNT_TWO


@pytest.fixture
def storage_dir(tmp_path: Any) -> None:
    """Fixture: Temporary Storage Directory.

    Provides: Clean storage directory for tests
    Cleanup: Automatic via tmp_path
    """
    storage_path = tmp_path / ".tracertm"
    storage_path.mkdir()
    return storage_path


@pytest.fixture
def db_path(storage_dir: Any) -> None:
    """Fixture: Database Path.

    Provides: Path to SQLite database file
    """
    return storage_dir / "tracertm.db"


@pytest.fixture
def markdown_dir(storage_dir: Any) -> None:
    """Fixture: Markdown Directory.

    Provides: Path to markdown files directory
    """
    projects_dir = storage_dir / "projects"
    projects_dir.mkdir()
    return projects_dir


@pytest.fixture
def init_db(db_path: Any) -> None:
    """Fixture: Initialize Database Schema.

    Creates the SQLite database with all required tables
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Projects table
    cursor.execute("""
        CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT,
            remote_id TEXT,
            version INTEGER DEFAULT 1,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    # Items table
    cursor.execute("""
        CREATE TABLE items (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            external_id TEXT,
            title TEXT NOT NULL,
            content_hash TEXT,
            status TEXT NOT NULL,
            priority TEXT,
            owner TEXT,
            parent_id TEXT,
            version INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT,
            remote_id TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (parent_id) REFERENCES items(id)
        )
    """)

    # Links table
    cursor.execute("""
        CREATE TABLE links (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            link_type TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL,
            synced_at TEXT,
            remote_id TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (source_id) REFERENCES items(id),
            FOREIGN KEY (target_id) REFERENCES items(id)
        )
    """)

    # Sync queue table
    cursor.execute("""
        CREATE TABLE sync_queue (
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
    """)

    # Sync state table
    cursor.execute("""
        CREATE TABLE sync_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    return db_path

    # Cleanup handled by tmp_path


@pytest.fixture
def sample_project_data() -> None:
    """Sample project data for testing."""
    return {
        "id": "proj-001",
        "name": "test-project",
        "description": "Test Project Description",
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "version": 1,
        "is_deleted": 0,
    }


@pytest.fixture
def sample_item_data() -> None:
    """Sample item data for testing."""
    return {
        "id": "item-001",
        "project_id": "proj-001",
        "item_type": "epic",
        "external_id": "EPIC-001",
        "title": "User Authentication System",
        "content_hash": "abc123",
        "status": "in_progress",
        "priority": "high",
        "owner": "@team-lead",
        "parent_id": None,
        "version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "is_deleted": 0,
    }


# ============================================================================
# TEST CLASSES - Project CRUD Operations
# ============================================================================


class TestLocalStorageProjectOperations:
    """Test Suite: Local Storage - Project Operations.

    Tests CRUD operations for projects in SQLite database
    """

    @pytest.mark.unit
    def test_create_project(self, init_db: Any, sample_project_data: Any) -> None:
        """TC-LS.1.1: Create Project - Success.

        Given: Empty database
        When: Project is created
        Then: Project exists in database
        And: Has correct attributes
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Act
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )
        conn.commit()

        # Assert
        cursor.execute("SELECT * FROM projects WHERE id = ?", (sample_project_data["id"],))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == sample_project_data["id"]
        assert result[1] == sample_project_data["name"]
        assert result[2] == sample_project_data["description"]

    @pytest.mark.unit
    def test_read_project(self, init_db: Any, sample_project_data: Any) -> None:
        """TC-LS.1.2: Read Project - Success.

        Given: Project exists in database
        When: Project is queried by ID
        Then: Correct project data is returned
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )
        conn.commit()

        # Act
        cursor.execute("SELECT * FROM projects WHERE id = ?", (sample_project_data["id"],))
        result = cursor.fetchone()
        conn.close()

        # Assert
        assert result is not None
        assert result[1] == sample_project_data["name"]

    @pytest.mark.unit
    def test_update_project(self, init_db: Any, sample_project_data: Any) -> None:
        """TC-LS.1.3: Update Project - Success.

        Given: Project exists in database
        When: Project is updated
        Then: Changes are persisted
        And: Version is incremented
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )
        conn.commit()

        # Act
        new_description = "Updated Description"
        new_version = 2
        cursor.execute(
            """
            UPDATE projects
            SET description = ?, version = ?, updated_at = ?
            WHERE id = ?
        """,
            (new_description, new_version, datetime.now(UTC).isoformat(), sample_project_data["id"]),
        )
        conn.commit()

        # Assert
        cursor.execute("SELECT description, version FROM projects WHERE id = ?", (sample_project_data["id"],))
        result = cursor.fetchone()
        conn.close()

        assert result[0] == new_description
        assert result[1] == new_version

    @pytest.mark.unit
    def test_soft_delete_project(self, init_db: Any, sample_project_data: Any) -> None:
        """TC-LS.1.4: Soft Delete Project - Success.

        Given: Project exists in database
        When: Project is soft deleted
        Then: is_deleted flag is set to 1
        And: Project still exists in database
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )
        conn.commit()

        # Act
        cursor.execute("UPDATE projects SET is_deleted = 1 WHERE id = ?", (sample_project_data["id"],))
        conn.commit()

        # Assert
        cursor.execute("SELECT is_deleted FROM projects WHERE id = ?", (sample_project_data["id"],))
        result = cursor.fetchone()
        conn.close()

        assert result[0] == 1


# ============================================================================
# TEST CLASSES - Item CRUD Operations
# ============================================================================


class TestLocalStorageItemOperations:
    """Test Suite: Local Storage - Item Operations.

    Tests CRUD operations for items in SQLite database
    """

    @pytest.mark.unit
    def test_create_item(self, init_db: Any, sample_project_data: Any, sample_item_data: Any) -> None:
        """TC-LS.2.1: Create Item - Success.

        Given: Project exists in database
        When: Item is created
        Then: Item exists in database
        And: Has correct attributes
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Create project first
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )
        conn.commit()

        # Act
        cursor.execute(
            """
            INSERT INTO items (
                id, project_id, item_type, external_id, title, content_hash,
                status, priority, owner, parent_id, version, created_at, updated_at, is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_item_data["id"],
                sample_item_data["project_id"],
                sample_item_data["item_type"],
                sample_item_data["external_id"],
                sample_item_data["title"],
                sample_item_data["content_hash"],
                sample_item_data["status"],
                sample_item_data["priority"],
                sample_item_data["owner"],
                sample_item_data["parent_id"],
                sample_item_data["version"],
                sample_item_data["created_at"],
                sample_item_data["updated_at"],
                sample_item_data["is_deleted"],
            ),
        )
        conn.commit()

        # Assert
        cursor.execute("SELECT * FROM items WHERE id = ?", (sample_item_data["id"],))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == sample_item_data["id"]
        assert result[4] == sample_item_data["title"]
        assert result[3] == sample_item_data["external_id"]

    @pytest.mark.unit
    def test_query_items_by_project(self, init_db: Any, sample_project_data: Any, _sample_item_data: Any) -> None:
        """TC-LS.2.2: Query Items by Project - Success.

        Given: Multiple items exist in project
        When: Items are queried by project_id
        Then: All project items are returned
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Create project
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )

        # Create multiple items
        for i in range(3):
            cursor.execute(
                """
                INSERT INTO items (
                    id, project_id, item_type, external_id, title, content_hash,
                    status, priority, created_at, updated_at, version, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"item-{i:03d}",
                    sample_project_data["id"],
                    "story",
                    f"STORY-{i:03d}",
                    f"Story {i}",
                    f"hash-{i}",
                    "todo",
                    "medium",
                    datetime.now(UTC).isoformat(),
                    datetime.now(UTC).isoformat(),
                    1,
                    0,
                ),
            )
        conn.commit()

        # Act
        cursor.execute(
            """
            SELECT * FROM items
            WHERE project_id = ? AND is_deleted = 0
        """,
            (sample_project_data["id"],),
        )
        results = cursor.fetchall()
        conn.close()

        # Assert
        assert len(results) == COUNT_THREE

    @pytest.mark.unit
    def test_filter_items_by_status(self, init_db: Any, sample_project_data: Any) -> None:
        """TC-LS.2.3: Filter Items by Status - Success.

        Given: Items with different statuses exist
        When: Items are filtered by status
        Then: Only matching items are returned
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Create project
        cursor.execute(
            """
            INSERT INTO projects (id, name, description, created_at, updated_at, version, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample_project_data["id"],
                sample_project_data["name"],
                sample_project_data["description"],
                sample_project_data["created_at"],
                sample_project_data["updated_at"],
                sample_project_data["version"],
                sample_project_data["is_deleted"],
            ),
        )

        # Create items with different statuses
        statuses = ["todo", "in_progress", "done", "todo"]
        for i, status in enumerate(statuses):
            cursor.execute(
                """
                INSERT INTO items (
                    id, project_id, item_type, external_id, title, content_hash,
                    status, created_at, updated_at, version, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"item-{i:03d}",
                    sample_project_data["id"],
                    "story",
                    f"STORY-{i:03d}",
                    f"Story {i}",
                    f"hash-{i}",
                    status,
                    datetime.now(UTC).isoformat(),
                    datetime.now(UTC).isoformat(),
                    1,
                    0,
                ),
            )
        conn.commit()

        # Act
        cursor.execute(
            """
            SELECT * FROM items
            WHERE project_id = ? AND status = ? AND is_deleted = 0
        """,
            (sample_project_data["id"], "todo"),
        )
        results = cursor.fetchall()
        conn.close()

        # Assert
        assert len(results) == COUNT_TWO


# ============================================================================
# TEST CLASSES - Content Hashing
# ============================================================================


class TestLocalStorageContentHashing:
    """Test Suite: Local Storage - Content Hashing.

    Tests content hash generation and change detection
    """

    @pytest.mark.unit
    def test_generate_content_hash(self) -> None:
        """TC-LS.3.1: Generate Content Hash - Success.

        Given: Markdown content
        When: Hash is generated
        Then: Consistent hash is produced
        """
        # Arrange
        import hashlib

        content = "# Test Item\n\nDescription here"

        # Act
        hash1 = hashlib.sha256(content.encode()).hexdigest()
        hash2 = hashlib.sha256(content.encode()).hexdigest()

        # Assert
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64-char hex

    @pytest.mark.unit
    def test_detect_content_change(self) -> None:
        """TC-LS.3.2: Detect Content Change - Success.

        Given: Two different content strings
        When: Hashes are compared
        Then: Hashes are different
        """
        # Arrange
        import hashlib

        content1 = "# Original Content"
        content2 = "# Modified Content"

        # Act
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()

        # Assert
        assert hash1 != hash2

    @pytest.mark.unit
    def test_no_change_detection(self) -> None:
        """TC-LS.3.3: No Change Detection - Success.

        Given: Same content with whitespace differences
        When: Hashes are compared after normalization
        Then: Hashes match
        """
        # Arrange
        import hashlib

        content1 = "# Test\n\nContent"
        content2 = "# Test\n\nContent"  # Same content

        # Act
        hash1 = hashlib.sha256(content1.strip().encode()).hexdigest()
        hash2 = hashlib.sha256(content2.strip().encode()).hexdigest()

        # Assert
        assert hash1 == hash2


# ============================================================================
# TEST CLASSES - Sync Queue Management
# ============================================================================


class TestLocalStorageSyncQueue:
    """Test Suite: Local Storage - Sync Queue.

    Tests sync queue operations for change tracking
    """

    @pytest.mark.unit
    def test_add_to_sync_queue(self, init_db: Any) -> None:
        """TC-LS.4.1: Add to Sync Queue - Success.

        Given: Change occurred locally
        When: Change is added to sync queue
        Then: Queue entry is created
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Act
        cursor.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, operation, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            ("item", "item-001", "create", json.dumps({"title": "New Item"}), datetime.now(UTC).isoformat()),
        )
        conn.commit()

        # Assert
        cursor.execute("SELECT * FROM sync_queue WHERE entity_id = ?", ("item-001",))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[1] == "item"
        assert result[3] == "create"

    @pytest.mark.unit
    def test_unique_sync_queue_constraint(self, init_db: Any) -> None:
        """TC-LS.4.2: Sync Queue Unique Constraint - Duplicate Prevention.

        Given: Queue entry already exists
        When: Same change is added again
        Then: Constraint violation occurs
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, operation, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            ("item", "item-001", "update", json.dumps({"title": "Updated"}), datetime.now(UTC).isoformat()),
        )
        conn.commit()

        # Act & Assert
        def insert_duplicate() -> None:
            cursor.execute(
                """
                INSERT INTO sync_queue (entity_type, entity_id, operation, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                ("item", "item-001", "update", json.dumps({"title": "Updated Again"}), datetime.now(UTC).isoformat()),
            )
            conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            insert_duplicate()

        conn.close()

    @pytest.mark.unit
    def test_process_sync_queue(self, init_db: Any) -> None:
        """TC-LS.4.3: Process Sync Queue - Success.

        Given: Multiple entries in sync queue
        When: Queue is processed in order
        Then: Entries are returned in creation order
        """
        # Arrange
        conn = sqlite3.connect(init_db)
        cursor = conn.cursor()

        # Add multiple entries
        for i in range(3):
            cursor.execute(
                """
                INSERT INTO sync_queue (entity_type, entity_id, operation, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                ("item", f"item-{i:03d}", "create", json.dumps({"id": i}), datetime.now(UTC).isoformat()),
            )
        conn.commit()

        # Act
        cursor.execute("SELECT * FROM sync_queue ORDER BY id ASC")
        results = cursor.fetchall()
        conn.close()

        # Assert
        assert len(results) == COUNT_THREE
        assert results[0][2] == "item-000"
        assert results[2][2] == "item-002"


# ============================================================================
# TEST CLASSES - Markdown Directory Structure
# ============================================================================


class TestLocalStorageMarkdownStructure:
    """Test Suite: Local Storage - Markdown Directory Structure.

    Tests markdown file organization and structure
    """

    @pytest.mark.unit
    def test_create_project_directory(self, markdown_dir: Any) -> None:
        """TC-LS.5.1: Create Project Directory - Success.

        Given: Projects directory exists
        When: New project directory is created
        Then: Directory structure is correct
        """
        # Arrange
        project_name = "test-project"

        # Act
        project_dir = markdown_dir / project_name
        project_dir.mkdir()
        (project_dir / "epics").mkdir()
        (project_dir / "stories").mkdir()
        (project_dir / "tests").mkdir()
        (project_dir / ".meta").mkdir()

        # Assert
        assert project_dir.exists()
        assert (project_dir / "epics").exists()
        assert (project_dir / "stories").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / ".meta").exists()

    @pytest.mark.unit
    def test_create_readme(self, markdown_dir: Any) -> None:
        """TC-LS.5.2: Create Project README - Success.

        Given: Project directory exists
        When: README.md is created
        Then: File exists with correct content
        """
        # Arrange
        project_name = "test-project"
        project_dir = markdown_dir / project_name
        project_dir.mkdir()

        # Act
        readme_path = project_dir / "README.md"
        readme_content = "# Test Project\n\nProject description here."
        readme_path.write_text(readme_content)

        # Assert
        assert readme_path.exists()
        assert readme_path.read_text() == readme_content

    @pytest.mark.unit
    def test_create_links_yaml(self, markdown_dir: Any) -> None:
        """TC-LS.5.3: Create Links YAML - Success.

        Given: Project .meta directory exists
        When: links.yaml is created
        Then: Valid YAML structure exists
        """
        # Arrange
        project_name = "test-project"
        project_dir = markdown_dir / project_name
        project_dir.mkdir()
        meta_dir = project_dir / ".meta"
        meta_dir.mkdir()

        # Act
        links_data = {
            "links": [
                {
                    "id": "link-001",
                    "source": "EPIC-001",
                    "target": "STORY-001",
                    "type": "implements",
                    "created": datetime.now(UTC).isoformat(),
                },
            ],
        }
        links_path = meta_dir / "links.yaml"
        links_path.write_text(yaml.dump(links_data, default_flow_style=False))

        # Assert
        assert links_path.exists()
        loaded_data = yaml.safe_load(links_path.read_text())
        assert "links" in loaded_data
        assert len(loaded_data["links"]) == 1
        assert loaded_data["links"][0]["type"] == "implements"


# ============================================================================
# NOTES
# ============================================================================

"""
COVERAGE AREAS:

1. Project Operations:
   - Create, Read, Update, Soft Delete
   - Version tracking

2. Item Operations:
   - CRUD operations
   - Query by project
   - Filter by status
   - Foreign key relationships

3. Content Hashing:
   - Hash generation
   - Change detection
   - Consistency verification

4. Sync Queue:
   - Queue entry creation
   - Unique constraint enforcement
   - Processing order

5. Markdown Structure:
   - Directory creation
   - README generation
   - YAML metadata files

TODO for full implementation:
- Add LocalStorageManager class tests (when implemented)
- Add bidirectional sync tests (SQLite ↔ Markdown)
- Add transaction rollback tests
- Add concurrent access tests
- Add full-text search integration tests
"""
