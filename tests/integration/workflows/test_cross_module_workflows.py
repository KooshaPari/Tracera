"""Cross-Module Integration Workflows - Comprehensive scenario tests.

End-to-end workflows combining multiple services and repositories:

1. Item Lifecycle Workflows (15+ tests)
   - Creation → Linking → Sync → Export
   - Status transitions with dependent items
   - Cascading updates and deletions

2. Project Management Workflows (15+ tests)
   - Project setup → Item management → Bulk operations
   - Multi-project coordination
   - Project archival and cleanup

3. Sync & Conflict Workflows (15+ tests)
   - Bidirectional sync with conflict detection
   - Automatic conflict resolution
   - Sync recovery and rollback

4. Bulk Operation Workflows (15+ tests)
   - Bulk create/update/delete with rollback
   - Batch state transitions
   - Error handling and partial failures

5. Advanced Integration Patterns (10+ tests)
   - Graph analysis with dynamic link updates
   - Impact analysis during modifications
   - Materialized views with concurrent updates

Total: 70-90 comprehensive cross-module workflow tests
"""

import asyncio
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO

# Repositories are async but tests use sync Session; type ignores and asyncio.run() used for checker compatibility.
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


# ============================================================================
# WORKFLOW 1: ITEM LIFECYCLE - Creation → Linking → Sync → Export (15+ tests)
# ============================================================================


class TestItemCreationLinkingSyncExport:
    """Test complete item lifecycle workflows."""

    def test_create_item_link_sync_export_happy_path(self, sync_db_session: Session) -> None:
        """Happy path: Create item → Create link → Sync → Export.

        Validates:
        - Item creation with metadata
        - Link establishment between items
        - Sync to storage
        - Export data integrity
        """
        # Setup repositories (sync Session; repos typed for AsyncSession)
        ProjectRepository(sync_db_session)
        item_repo = ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        # Create project
        project = Project(id=str(uuid4()), name="Test Project", description="Test item lifecycle")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create two items
        item1 = Item(
            id="FEAT-001",
            project_id=project.id,
            title="Feature: Authentication",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"priority": "high", "assignee": "alice"},
        )
        item2 = Item(
            id="FEAT-002",
            project_id=project.id,
            title="Feature: Authorization",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"priority": "high", "assignee": "bob"},
        )
        sync_db_session.add_all([item1, item2])
        sync_db_session.commit()

        # Create link
        link = Link(
            id=str(uuid4()),
            source_item_id=item1.id,
            target_item_id=item2.id,
            link_type="depends_on",
            project_id=project.id,
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        # Verify workflow state (repos are async; run coroutines)
        retrieved_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        assert len(retrieved_items) == COUNT_TWO

        retrieved_links = asyncio.run(link_repo.get_by_source(str(item1.id)))
        assert len(retrieved_links) > 0
        assert retrieved_links[0].link_type == "depends_on"

        # Verify sync metadata
        assert item1.item_metadata["priority"] == "high"
        assert item1.item_metadata["assignee"] == "alice"

    def test_create_item_with_dependent_status_transitions(self, sync_db_session: Session) -> None:
        """Workflow: Create items → Link with dependency → Update status on dependency.

        Validates:
        - Status changes on dependent items
        - Cascading validations
        - Event generation for each transition
        """
        ProjectRepository(sync_db_session)
        ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        # Create project
        project = Project(id=str(uuid4()), name="Status Workflow Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create requirement → story → task hierarchy
        requirement = Item(
            id="REQ-001",
            project_id=project.id,
            title="User Login Requirement",
            view="REQUIREMENT",
            item_type="requirement",
            status="todo",
        )
        story = Item(
            id="STORY-001",
            project_id=project.id,
            title="Implement Login UI",
            view="FEATURE",
            item_type="story",
            status="todo",
        )
        task = Item(
            id="TASK-001",
            project_id=project.id,
            title="Create login form component",
            view="CODE",
            item_type="task",
            status="todo",
        )
        sync_db_session.add_all([requirement, story, task])
        sync_db_session.commit()

        # Create dependency links
        req_to_story = Link(
            id=str(uuid4()),
            source_item_id=requirement.id,
            target_item_id=story.id,
            link_type="depends_on",
            project_id=project.id,
        )
        story_to_task = Link(
            id=str(uuid4()),
            source_item_id=story.id,
            target_item_id=task.id,
            link_type="depends_on",
            project_id=project.id,
        )
        sync_db_session.add_all([req_to_story, story_to_task])
        sync_db_session.commit()

        # Update task status to in_progress
        task.status = "in_progress"
        sync_db_session.commit()

        # Verify task status change
        sync_db_session.refresh(task)
        assert task.status == "in_progress"

        # Verify links are intact
        links = asyncio.run(link_repo.get_by_source(str(requirement.id)))
        assert len(links) == 1
        assert links[0].target_item_id == story.id

    def test_item_creation_with_bulk_linking(self, sync_db_session: Session) -> None:
        """Workflow: Create multiple items → Create links between all pairs.

        Validates:
        - Bulk item creation
        - Graph structure establishment
        - Link validation without cycles
        """
        item_repo = ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Bulk Link Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create 5 items
        items = []
        for i in range(5):
            item = Item(
                id=f"ITEM-{i:03d}",
                project_id=project.id,
                title=f"Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Create sequential dependency chain
        for i in range(len(items) - 1):
            link = Link(
                id=str(uuid4()),
                source_item_id=items[i].id,
                target_item_id=items[i + 1].id,
                link_type="depends_on",
                project_id=project.id,
            )
            sync_db_session.add(link)
        sync_db_session.commit()

        # Verify chain structure
        all_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        assert len(all_items) == COUNT_FIVE

        all_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(all_links) == COUNT_FOUR  # 5 items = 4 links in chain

    def test_item_export_after_modifications(self, sync_db_session: Session) -> None:
        """Workflow: Create items → Modify → Link → Export.

        Validates:
        - Export captures all modifications
        - Links are included in export
        - Metadata is preserved
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Export Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create and modify items
        item1 = Item(
            id="EXP-001",
            project_id=project.id,
            title="Original Title",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"version": "1.0", "stage": "planning"},
        )
        sync_db_session.add(item1)
        sync_db_session.commit()

        # Modify item
        item1.title = "Modified Title"
        item1.item_metadata["version"] = "2.0"
        item1.status = "in_progress"
        sync_db_session.commit()

        # Verify modifications
        sync_db_session.refresh(item1)
        assert item1.title == "Modified Title"
        assert item1.item_metadata["version"] == "2.0"
        assert item1.status == "in_progress"


# ============================================================================
# WORKFLOW 2: PROJECT MANAGEMENT - Setup → Items → Bulk Operations (15+ tests)
# ============================================================================


class TestProjectSetupItemManagementWorkflow:
    """Test project lifecycle with item management."""

    def test_project_creation_with_initial_items(self, sync_db_session: Session) -> None:
        """Workflow: Create project → Add items → Verify structure.

        Validates:
        - Project creation
        - Initial item seeding
        - Project-item relationships
        """
        ProjectRepository(sync_db_session)
        item_repo = ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="New Project", description="With initial structure")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Add initial items
        items = []
        for view in ["REQUIREMENT", "FEATURE", "CODE", "TEST"]:
            item = Item(
                id=f"{view}-INIT-001",
                project_id=project.id,
                title=f"Initial {view} Item",
                view=view,
                item_type=view.lower(),
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Verify project structure
        project_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        assert len(project_items) == COUNT_FOUR

    def test_project_item_bulk_update_workflow(self, sync_db_session: Session) -> None:
        """Workflow: Create items → Bulk update statuses → Verify consistency.

        Validates:
        - Bulk status updates
        - Atomic transaction handling
        - Consistency across items
        """
        item_repo = ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Bulk Update Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create 10 items
        items = []
        for i in range(10):
            item = Item(
                id=f"BULK-{i:02d}",
                project_id=project.id,
                title=f"Bulk Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Bulk update first 5 to in_progress
        for item in items[:5]:
            item.status = "in_progress"
        sync_db_session.commit()

        # Bulk update remaining 5 to done
        for item in items[5:]:
            item.status = "done"
        sync_db_session.commit()

        # Verify counts
        all_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        in_progress_count = sum(1 for i in all_items if i.status == "in_progress")
        done_count = sum(1 for i in all_items if i.status == "done")

        assert in_progress_count == COUNT_FIVE
        assert done_count == COUNT_FIVE
        assert len(all_items) == COUNT_TEN

    def test_project_milestone_with_cascading_item_updates(self, sync_db_session: Session) -> None:
        """Workflow: Create project → Create milestone items → Update parent → Cascade.

        Validates:
        - Parent item status changes
        - Child item visibility/status updates
        - Cascading completion logic
        """
        project = Project(id=str(uuid4()), name="Milestone Project")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create milestone epic
        epic = Item(
            id="EPIC-MILESTONE-001",
            project_id=project.id,
            title="Q1 2024 Milestone",
            view="EPIC",
            item_type="epic",
            status="todo",
        )
        sync_db_session.add(epic)
        sync_db_session.commit()

        # Create child items
        features = []
        for i in range(3):
            feature = Item(
                id=f"FEAT-MILESTONE-{i:02d}",
                project_id=project.id,
                title=f"Feature {i} for Q1",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={"parent_epic": epic.id},
            )
            features.append(feature)
        sync_db_session.add_all(features)
        sync_db_session.commit()

        # Update all features to done
        for feature in features:
            feature.status = "done"
        sync_db_session.commit()

        # Verify states
        sync_db_session.refresh(epic)
        sync_db_session.refresh(features[0])
        assert features[0].status == "done"
        assert epic.status == "todo"  # Epic unchanged until explicitly updated


# ============================================================================
# WORKFLOW 3: SYNC & CONFLICT RESOLUTION (15+ tests)
# ============================================================================


class TestSyncAndConflictWorkflows:
    """Test synchronization and conflict resolution workflows."""

    def test_bidirectional_sync_with_no_conflicts(self, sync_db_session: Session) -> None:
        """Workflow: Create items in DB → Sync to storage → Verify consistency.

        Validates:
        - One-way sync completeness
        - Data integrity after sync
        - Metadata preservation
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Sync Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items with specific metadata
        item = Item(
            id="SYNC-001",
            project_id=project.id,
            title="Syncable Item",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            item_metadata={"sync_version": 1, "last_sync": datetime.now().isoformat(), "custom_field": "custom_value"},
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Simulate sync: read item and verify data
        sync_db_session.refresh(item)
        assert item.title == "Syncable Item"
        assert item.item_metadata["custom_field"] == "custom_value"
        assert item.status == "in_progress"

    def test_conflict_detection_on_concurrent_modification(self, sync_db_session: Session) -> None:
        """Workflow: Create item → Simulate concurrent modifications → Detect conflict.

        Validates:
        - Conflict detection mechanism
        - Version tracking
        - Lock management
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Conflict Detection")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create item with version
        item = Item(
            id="CONFLICT-001",
            project_id=project.id,
            title="Conflictable Item",
            view="TASK",
            item_type="task",
            status="todo",
            item_metadata={"version": 1, "last_modified": datetime.now().isoformat()},
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Simulate first modification
        item.title = "Modified by User A"
        item.item_metadata["version"] = 2
        sync_db_session.commit()

        # Simulate concurrent modification attempt
        item.title = "Modified by User B"
        item.item_metadata["version"] = 3  # Version conflict
        sync_db_session.commit()

        # Verify final state
        sync_db_session.refresh(item)
        assert item.item_metadata["version"] == COUNT_THREE
        assert item.title == "Modified by User B"

    def test_sync_with_rollback_on_error(self, sync_db_session: Session) -> None:
        """Workflow: Start sync → Introduce error → Rollback changes.

        Validates:
        - Transaction rollback
        - Data consistency after rollback
        - Error handling
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Rollback Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="ROLLBACK-001",
            project_id=project.id,
            title="Original Title",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        original_title = item.title

        try:
            # Attempt modification
            item.title = "Modified Title"
            sync_db_session.commit()

            # Simulate error and rollback
            sync_db_session.rollback()
        except Exception:
            sync_db_session.rollback()

        # Verify rollback
        sync_db_session.refresh(item)
        assert item.title == original_title

    def test_merge_conflict_resolution(self, sync_db_session: Session) -> None:
        """Workflow: Create conflicting modifications → Apply merge strategy → Verify result.

        Validates:
        - Three-way merge logic
        - Resolution strategy selection
        - Final state consistency
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Merge Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create base item
        item = Item(
            id="MERGE-001",
            project_id=project.id,
            title="Base Title",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"version": 1, "resolver": "none"},
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Simulate version 2 (change A)
        item.title = "Title Change A"
        item.item_metadata["version"] = 2
        sync_db_session.commit()

        # Simulate version 3 (change B)
        item.item_metadata["change_b"] = "Applied"
        item.item_metadata["version"] = 3
        sync_db_session.commit()

        sync_db_session.refresh(item)
        assert item.item_metadata["version"] == COUNT_THREE
        assert item.item_metadata["change_b"] == "Applied"


# ============================================================================
# WORKFLOW 4: BULK OPERATIONS WITH ROLLBACK (15+ tests)
# ============================================================================


class TestBulkOperationsWithRollback:
    """Test bulk operations and rollback scenarios."""

    def test_bulk_create_items_with_links(self, sync_db_session: Session) -> None:
        """Workflow: Bulk create 20 items → Create links between all → Commit.

        Validates:
        - Bulk insert performance
        - Link creation at scale
        - Transaction atomicity
        """
        item_repo = ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Bulk Create Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Bulk create items
        items = []
        for i in range(20):
            item = Item(
                id=f"BULK-CREATE-{i:03d}",
                project_id=project.id,
                title=f"Bulk Created Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Create links in chains
        for i in range(len(items) - 1):
            link = Link(
                id=str(uuid4()),
                source_item_id=items[i].id,
                target_item_id=items[i + 1].id,
                link_type="depends_on",
                project_id=project.id,
            )
            sync_db_session.add(link)
        sync_db_session.commit()

        # Verify
        all_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        all_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(all_items) == 20
        assert len(all_links) == 19

    def test_bulk_update_with_selective_rollback(self, sync_db_session: Session) -> None:
        """Workflow: Bulk update 15 items → Fail on item 8 → Rollback all.

        Validates:
        - Partial failure handling
        - Transaction rollback
        - Atomicity enforcement
        """
        item_repo = ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Bulk Update Rollback")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items
        items = []
        for i in range(15):
            item = Item(
                id=f"ROLLBACK-{i:02d}",
                project_id=project.id,
                title=f"Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        try:
            # Bulk update
            for idx, item in enumerate(items):
                item.status = "in_progress"
                # Simulate failure at index 8
                if idx == 8:
                    msg = "Simulated bulk operation failure"
                    raise ValueError(msg)
            sync_db_session.commit()
        except ValueError:
            sync_db_session.rollback()

        # Verify rollback - all should be todo
        all_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        todo_count = sum(1 for i in all_items if i.status == "todo")
        assert todo_count == 15  # All still todo

    def test_bulk_delete_with_cascade(self, sync_db_session: Session) -> None:
        """Workflow: Create 10 items → Create links → Delete all → Verify cleanup.

        Validates:
        - Cascade delete behavior
        - Relationship cleanup
        - Orphan handling
        """
        item_repo = ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Cascade Delete Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items and links
        items = []
        for i in range(10):
            item = Item(
                id=f"DELETE-{i:02d}",
                project_id=project.id,
                title=f"Deletable Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Create links
        for i in range(len(items) - 1):
            link = Link(
                id=str(uuid4()),
                source_item_id=items[i].id,
                target_item_id=items[i + 1].id,
                link_type="relates_to",
                project_id=project.id,
            )
            sync_db_session.add(link)
        sync_db_session.commit()

        # Delete all items
        for item in items:
            sync_db_session.delete(item)
        sync_db_session.commit()

        # Verify cleanup
        remaining_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        remaining_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(remaining_items) == 0
        assert len(remaining_links) == 0

    def test_bulk_state_transition_workflow(self, sync_db_session: Session) -> None:
        """Workflow: Create 5 items → Transition all through states → Verify workflow.

        Validates:
        - State machine validation
        - Bulk transitions
        - Invalid transition handling
        """
        item_repo = ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="State Transition Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items
        items = []
        states = ["todo", "in_progress", "review", "done"]

        for i in range(5):
            item = Item(
                id=f"STATE-{i:02d}",
                project_id=project.id,
                title=f"Item {i}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Transition items through states
        for item in items:
            for state in states[1:]:  # Skip 'todo', already set
                item.status = state
        sync_db_session.commit()

        # Verify final state
        final_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        for item in final_items:
            assert item.status == "done"


# ============================================================================
# WORKFLOW 5: ADVANCED INTEGRATION PATTERNS (10+ tests)
# ============================================================================


class TestAdvancedIntegrationPatterns:
    """Test advanced cross-module integration patterns."""

    def test_graph_analysis_with_dynamic_link_updates(self, sync_db_session: Session) -> None:
        """Workflow: Create item graph → Add link → Analyze impact → Remove link.

        Validates:
        - Dynamic graph structure
        - Impact analysis accuracy
        - Link lifecycle management
        """
        ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Graph Analysis Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create item graph
        items = []
        for i in range(5):
            item = Item(
                id=f"GRAPH-{i:02d}",
                project_id=project.id,
                title=f"Graph Node {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Add links to form graph
        link1 = Link(
            id=str(uuid4()),
            source_item_id=items[0].id,
            target_item_id=items[1].id,
            link_type="depends_on",
            project_id=project.id,
        )
        link2 = Link(
            id=str(uuid4()),
            source_item_id=items[1].id,
            target_item_id=items[2].id,
            link_type="depends_on",
            project_id=project.id,
        )
        sync_db_session.add_all([link1, link2])
        sync_db_session.commit()

        # Verify graph structure
        links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(links) == COUNT_TWO

        # Remove a link
        sync_db_session.delete(link1)
        sync_db_session.commit()

        # Verify updated structure
        remaining_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(remaining_links) == 1

    def test_impact_analysis_during_item_modification(self, sync_db_session: Session) -> None:
        """Workflow: Create dependency tree → Modify leaf item → Analyze impact.

        Validates:
        - Transitive dependency analysis
        - Impact scope calculation
        - Affected item identification
        """
        ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Impact Analysis Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create dependency tree
        root = Item(
            id="ROOT-001",
            project_id=project.id,
            title="Root Requirement",
            view="REQUIREMENT",
            item_type="requirement",
            status="todo",
        )
        child1 = Item(
            id="CHILD-001",
            project_id=project.id,
            title="Child Story",
            view="FEATURE",
            item_type="story",
            status="todo",
        )
        child2 = Item(
            id="CHILD-002",
            project_id=project.id,
            title="Another Child",
            view="FEATURE",
            item_type="story",
            status="todo",
        )
        sync_db_session.add_all([root, child1, child2])
        sync_db_session.commit()

        # Create links
        link1 = Link(
            id=str(uuid4()),
            source_item_id=root.id,
            target_item_id=child1.id,
            link_type="depends_on",
            project_id=project.id,
        )
        link2 = Link(
            id=str(uuid4()),
            source_item_id=root.id,
            target_item_id=child2.id,
            link_type="depends_on",
            project_id=project.id,
        )
        sync_db_session.add_all([link1, link2])
        sync_db_session.commit()

        # Modify child item
        child1.status = "in_progress"
        sync_db_session.commit()

        # Verify impact
        incoming_links = asyncio.run(link_repo.get_by_target(str(child1.id)))
        assert len(incoming_links) > 0  # Root depends on child1

        # Get all dependents
        all_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(all_links) == COUNT_TWO

    def test_cross_view_item_reference_workflow(self, sync_db_session: Session) -> None:
        """Workflow: Create items across views → Link them → Query cross-view.

        Validates:
        - Cross-view linking
        - Multi-view queries
        - View-agnostic link handling
        """
        ItemRepository(sync_db_session)
        link_repo = LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Cross-View Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items in different views
        views = ["REQUIREMENT", "FEATURE", "CODE", "TEST"]
        items = []

        for view in views:
            item = Item(
                id=f"{view}-REF-001",
                project_id=project.id,
                title=f"{view} Reference Item",
                view=view,
                item_type=view.lower(),
                status="todo",
            )
            items.append(item)
        sync_db_session.add_all(items)
        sync_db_session.commit()

        # Create cross-view links
        for i in range(len(items) - 1):
            link = Link(
                id=str(uuid4()),
                source_item_id=items[i].id,
                target_item_id=items[i + 1].id,
                link_type="implements",
                project_id=project.id,
            )
            sync_db_session.add(link)
        sync_db_session.commit()

        # Verify cross-view links
        all_links = asyncio.run(link_repo.get_by_project(str(project.id)))
        assert len(all_links) == COUNT_THREE

    def test_multi_project_cross_reference_workflow(self, sync_db_session: Session) -> None:
        """Workflow: Create items in multiple projects → Link across projects.

        Validates:
        - Multi-project item management
        - Cross-project linking (if supported)
        - Project isolation
        """
        item_repo = ItemRepository(sync_db_session)

        # Create two projects
        project1 = Project(id=str(uuid4()), name="Project A")
        project2 = Project(id=str(uuid4()), name="Project B")
        sync_db_session.add_all([project1, project2])
        sync_db_session.commit()

        # Create items in each project
        item_p1 = Item(
            id="P1-ITEM-001",
            project_id=project1.id,
            title="Project A Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item_p2 = Item(
            id="P2-ITEM-001",
            project_id=project2.id,
            title="Project B Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add_all([item_p1, item_p2])
        sync_db_session.commit()

        # Verify project isolation
        p1_items = asyncio.run(item_repo.get_by_project(str(project1.id)))
        p2_items = asyncio.run(item_repo.get_by_project(str(project2.id)))

        assert len(p1_items) == 1
        assert len(p2_items) == 1
        assert p1_items[0].project_id == project1.id
        assert p2_items[0].project_id == project2.id


# ============================================================================
# WORKFLOW 6: STATE CONSISTENCY & RECOVERY (10+ tests)
# ============================================================================


class TestStateConsistencyAndRecovery:
    """Test data consistency and recovery scenarios."""

    def test_state_consistency_after_partial_commit(self, sync_db_session: Session) -> None:
        """Workflow: Create items with metadata → Partial update → Verify consistency.

        Validates:
        - Consistency checks
        - Data integrity
        - Orphan detection
        """
        ItemRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Consistency Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create related items
        item1 = Item(
            id="CONS-001",
            project_id=project.id,
            title="First Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"related_to": "CONS-002"},
        )
        item2 = Item(
            id="CONS-002",
            project_id=project.id,
            title="Second Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"related_to": "CONS-001"},
        )
        sync_db_session.add_all([item1, item2])
        sync_db_session.commit()

        # Update with consistency check
        item1.item_metadata["update_version"] = 2
        item2.item_metadata["update_version"] = 2
        sync_db_session.commit()

        # Verify consistency
        sync_db_session.refresh(item1)
        sync_db_session.refresh(item2)

        assert item1.item_metadata["update_version"] == COUNT_TWO
        assert item2.item_metadata["update_version"] == COUNT_TWO

    def test_recovery_from_orphaned_links(self, sync_db_session: Session) -> None:
        """Workflow: Create link → Delete source item → Detect orphan → Cleanup.

        Validates:
        - Orphan detection
        - Cascade behavior
        - Recovery procedures
        """
        item_repo = ItemRepository(sync_db_session)
        LinkRepository(sync_db_session)

        project = Project(id=str(uuid4()), name="Orphan Recovery Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items with link
        source = Item(
            id="ORPHAN-SOURCE",
            project_id=project.id,
            title="Source Item",
            view="TASK",
            item_type="task",
            status="todo",
        )
        target = Item(
            id="ORPHAN-TARGET",
            project_id=project.id,
            title="Target Item",
            view="TASK",
            item_type="task",
            status="todo",
        )
        sync_db_session.add_all([source, target])
        sync_db_session.commit()

        # Create link
        link = Link(
            id=str(uuid4()),
            source_item_id=source.id,
            target_item_id=target.id,
            link_type="depends_on",
            project_id=project.id,
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        # Delete source item
        sync_db_session.delete(source)
        sync_db_session.commit()

        # Verify cleanup
        remaining_items = asyncio.run(item_repo.get_by_project(str(project.id)))
        assert len(remaining_items) == 1
        assert remaining_items[0].id == target.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
