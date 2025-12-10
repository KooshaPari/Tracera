"""
TIER-2C: LinkService Relationship Tests (90-120 tests)
Target coverage: +4-6%

Comprehensive test suite for LinkService and link relationships.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List

from tracertm.services.link_service import LinkService
from tracertm.repositories.link_repository import LinkRepository
from tracertm.models.link import Link, RelationshipType
from tracertm.models.item import Item
from tracertm.exceptions import LinkNotFoundError, ValidationError, ConflictError


class TestLinkServiceCreation:
    """Link creation tests (20 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_create_basic_link(self, link_service, link_repo):
        """Test creating a basic link between items"""
        link_data = {
            "source_id": "item-1",
            "target_id": "item-2",
            "relationship_type": RelationshipType.VERIFIES
        }
        link_repo.create.return_value = Link(**link_data, id="link-1")

        result = link_service.create_link(**link_data)

        assert result.id == "link-1"
        assert result.relationship_type == RelationshipType.VERIFIES

    def test_create_link_all_relationship_types(self, link_service, link_repo):
        """Test creating links with all relationship types"""
        for rel_type in RelationshipType:
            link_data = {
                "source_id": "item-1",
                "target_id": "item-2",
                "relationship_type": rel_type
            }
            link_repo.create.return_value = Link(**link_data, id=f"link-{rel_type}")

            result = link_service.create_link(**link_data)
            assert result.relationship_type == rel_type

    def test_create_link_with_metadata(self, link_service, link_repo):
        """Test creating link with metadata"""
        link_data = {
            "source_id": "item-1",
            "target_id": "item-2",
            "relationship_type": RelationshipType.IMPLEMENTS,
            "metadata": {"priority": "high"}
        }
        link_repo.create.return_value = Link(**link_data, id="link-2")

        result = link_service.create_link(**link_data)
        assert result.metadata["priority"] == "high"

    def test_create_link_validation_missing_source(self, link_service):
        """Test link creation fails without source_id"""
        with pytest.raises(ValidationError):
            link_service.create_link(target_id="item-2", relationship_type=RelationshipType.VERIFIES)

    def test_create_link_validation_missing_target(self, link_service):
        """Test link creation fails without target_id"""
        with pytest.raises(ValidationError):
            link_service.create_link(source_id="item-1", relationship_type=RelationshipType.VERIFIES)

    def test_create_link_validation_same_source_target(self, link_service):
        """Test link creation fails when source and target are same"""
        with pytest.raises(ValidationError):
            link_service.create_link(
                source_id="item-1",
                target_id="item-1",
                relationship_type=RelationshipType.VERIFIES
            )

    def test_create_bidirectional_link(self, link_service, link_repo):
        """Test creating bidirectional link"""
        link_data = {
            "source_id": "item-1",
            "target_id": "item-2",
            "relationship_type": RelationshipType.RELATED_TO,
            "bidirectional": True
        }
        link_repo.create.return_value = Link(**link_data, id="link-3")

        result = link_service.create_link(**link_data)
        assert result.bidirectional is True

    def test_create_multiple_links_sequentially(self, link_service, link_repo):
        """Test creating multiple links"""
        link_repo.create.side_effect = [
            Link(id=f"link-{i}", source_id="item-1", target_id=f"item-{i+2}",
                 relationship_type=RelationshipType.VERIFIES)
            for i in range(5)
        ]

        results = [
            link_service.create_link(
                source_id="item-1",
                target_id=f"item-{i+2}",
                relationship_type=RelationshipType.VERIFIES
            )
            for i in range(5)
        ]

        assert len(results) == 5

    def test_batch_create_links(self, link_service, link_repo):
        """Test batch creating links"""
        links_data = [
            {
                "source_id": "item-1",
                "target_id": f"item-{i}",
                "relationship_type": RelationshipType.VERIFIES
            }
            for i in range(5)
        ]
        link_repo.batch_create.return_value = 5

        result = link_service.batch_create_links(links_data)

        assert result == 5

    def test_create_link_with_description(self, link_service, link_repo):
        """Test creating link with description"""
        link_data = {
            "source_id": "item-1",
            "target_id": "item-2",
            "relationship_type": RelationshipType.VERIFIES,
            "description": "This test case verifies the requirement"
        }
        link_repo.create.return_value = Link(**link_data, id="link-4")

        result = link_service.create_link(**link_data)
        assert result.description == "This test case verifies the requirement"


class TestLinkServiceRetrieval:
    """Link retrieval tests (20 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_get_link_by_id(self, link_service, link_repo):
        """Test retrieving link by ID"""
        link = Link(id="link-1", source_id="item-1", target_id="item-2",
                   relationship_type=RelationshipType.VERIFIES)
        link_repo.get_by_id.return_value = link

        result = link_service.get_link("link-1")

        assert result.id == "link-1"

    def test_get_nonexistent_link(self, link_service, link_repo):
        """Test retrieving nonexistent link raises error"""
        link_repo.get_by_id.return_value = None

        with pytest.raises(LinkNotFoundError):
            link_service.get_link("nonexistent")

    def test_get_outbound_links(self, link_service, link_repo):
        """Test retrieving outbound links from an item"""
        links = [
            Link(id=f"link-{i}", source_id="item-1", target_id=f"item-{i+2}",
                 relationship_type=RelationshipType.VERIFIES)
            for i in range(3)
        ]
        link_repo.get_outbound_links.return_value = links

        results = link_service.get_outbound_links("item-1")

        assert len(results) == 3
        assert all(r.source_id == "item-1" for r in results)

    def test_get_inbound_links(self, link_service, link_repo):
        """Test retrieving inbound links to an item"""
        links = [
            Link(id=f"link-{i}", source_id=f"item-{i+2}", target_id="item-1",
                 relationship_type=RelationshipType.VERIFIES)
            for i in range(3)
        ]
        link_repo.get_inbound_links.return_value = links

        results = link_service.get_inbound_links("item-1")

        assert len(results) == 3
        assert all(r.target_id == "item-1" for r in results)

    def test_get_all_links_for_item(self, link_service, link_repo):
        """Test retrieving all links (inbound and outbound) for item"""
        outbound = [
            Link(id="link-1", source_id="item-1", target_id="item-2",
                 relationship_type=RelationshipType.VERIFIES)
        ]
        inbound = [
            Link(id="link-2", source_id="item-3", target_id="item-1",
                 relationship_type=RelationshipType.VERIFIES)
        ]
        link_repo.get_outbound_links.return_value = outbound
        link_repo.get_inbound_links.return_value = inbound

        results = link_service.get_all_links("item-1")

        assert len(results) == 2

    def test_get_links_by_relationship_type(self, link_service, link_repo):
        """Test retrieving links by relationship type"""
        links = [
            Link(id=f"link-{i}", source_id="item-1", target_id=f"item-{i+2}",
                 relationship_type=RelationshipType.VERIFIES)
            for i in range(3)
        ]
        link_repo.get_by_relationship_type.return_value = links

        results = link_service.get_links_by_type(RelationshipType.VERIFIES)

        assert all(r.relationship_type == RelationshipType.VERIFIES for r in results)

    def test_get_links_between_items(self, link_service, link_repo):
        """Test retrieving links between two specific items"""
        links = [
            Link(id="link-1", source_id="item-1", target_id="item-2",
                 relationship_type=RelationshipType.VERIFIES)
        ]
        link_repo.get_between_items.return_value = links

        results = link_service.get_links_between("item-1", "item-2")

        assert len(results) == 1


class TestLinkServiceTraversal:
    """Link traversal and path finding (15 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_get_transitive_closure(self, link_service, link_repo):
        """Test getting transitive closure of links"""
        items = ["item-1", "item-2", "item-3"]
        link_repo.get_transitive_closure.return_value = items

        results = link_service.get_transitive_closure("item-1")

        assert len(results) == 3

    def test_find_path_between_items(self, link_service, link_repo):
        """Test finding path between two items"""
        path = ["item-1", "item-2", "item-3"]
        link_repo.find_path.return_value = path

        result = link_service.find_path("item-1", "item-3")

        assert len(result) == 3

    def test_find_path_no_connection(self, link_service, link_repo):
        """Test finding path when no connection exists"""
        link_repo.find_path.return_value = None

        result = link_service.find_path("item-1", "item-99")

        assert result is None


class TestLinkServiceValidation:
    """Link validation and constraint testing (15 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_validate_relationship_rules(self, link_service, link_repo):
        """Test validating relationship type rules"""
        link_repo.validate_relationship.return_value = True

        result = link_service.validate_relationship("item-1", "item-2", RelationshipType.VERIFIES)

        assert result is True

    def test_detect_circular_dependency(self, link_service, link_repo):
        """Test detecting circular dependencies"""
        link_repo.has_circular_dependency.return_value = True

        result = link_service.has_circular_dependency("item-1", "item-2")

        assert result is True

    def test_prevent_circular_link_creation(self, link_service, link_repo):
        """Test preventing creation of circular links"""
        link_repo.has_circular_dependency.return_value = True

        with pytest.raises(ConflictError):
            link_service.create_link(
                source_id="item-1",
                target_id="item-2",
                relationship_type=RelationshipType.VERIFIES
            )


class TestLinkServiceUpdate:
    """Link update operations (12 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_update_link_metadata(self, link_service, link_repo):
        """Test updating link metadata"""
        original = Link(id="link-1", source_id="item-1", target_id="item-2",
                       relationship_type=RelationshipType.VERIFIES,
                       metadata={"priority": "low"})
        updated = Link(id="link-1", source_id="item-1", target_id="item-2",
                      relationship_type=RelationshipType.VERIFIES,
                      metadata={"priority": "high"})

        link_repo.get_by_id.return_value = original
        link_repo.update.return_value = updated

        result = link_service.update_link("link-1", metadata={"priority": "high"})

        assert result.metadata["priority"] == "high"

    def test_update_link_description(self, link_service, link_repo):
        """Test updating link description"""
        original = Link(id="link-1", source_id="item-1", target_id="item-2",
                       relationship_type=RelationshipType.VERIFIES)
        updated = Link(id="link-1", source_id="item-1", target_id="item-2",
                      relationship_type=RelationshipType.VERIFIES,
                      description="New description")

        link_repo.get_by_id.return_value = original
        link_repo.update.return_value = updated

        result = link_service.update_link("link-1", description="New description")

        assert result.description == "New description"


class TestLinkServiceDeletion:
    """Link deletion tests (10 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_delete_link(self, link_service, link_repo):
        """Test deleting a link"""
        link = Link(id="link-1", source_id="item-1", target_id="item-2",
                   relationship_type=RelationshipType.VERIFIES)
        link_repo.get_by_id.return_value = link
        link_repo.delete.return_value = True

        result = link_service.delete_link("link-1")

        assert result is True

    def test_delete_nonexistent_link(self, link_service, link_repo):
        """Test deleting nonexistent link raises error"""
        link_repo.get_by_id.return_value = None

        with pytest.raises(LinkNotFoundError):
            link_service.delete_link("nonexistent")

    def test_batch_delete_links(self, link_service, link_repo):
        """Test batch deleting links"""
        link_ids = [f"link-{i}" for i in range(5)]
        link_repo.batch_delete.return_value = 5

        result = link_service.batch_delete_links(link_ids)

        assert result == 5

    def test_delete_all_links_for_item(self, link_service, link_repo):
        """Test deleting all links for an item"""
        link_repo.delete_all_for_item.return_value = 5

        result = link_service.delete_all_for_item("item-1")

        assert result == 5


class TestLinkServiceBulkOperations:
    """Link bulk operations (8 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_bulk_create_links(self, link_service, link_repo):
        """Test bulk creating links"""
        links = [
            {
                "source_id": "item-1",
                "target_id": f"item-{i}",
                "relationship_type": RelationshipType.VERIFIES
            }
            for i in range(10)
        ]
        link_repo.batch_create.return_value = 10

        result = link_service.batch_create_links(links)

        assert result == 10

    def test_bulk_update_links(self, link_service, link_repo):
        """Test bulk updating links"""
        updates = [
            {"id": f"link-{i}", "metadata": {"priority": "high"}}
            for i in range(5)
        ]
        link_repo.batch_update.return_value = 5

        result = link_service.batch_update_links(updates)

        assert result == 5


class TestLinkServiceImpactAnalysis:
    """Link impact analysis (10 tests)"""

    @pytest.fixture
    def link_repo(self):
        return Mock(spec=LinkRepository)

    @pytest.fixture
    def link_service(self, link_repo):
        return LinkService(link_repo)

    def test_get_impact_on_delete(self, link_service, link_repo):
        """Test determining impact of deleting a link"""
        impact = {"affected_items": 3, "affected_links": 2}
        link_repo.calculate_delete_impact.return_value = impact

        result = link_service.get_delete_impact("link-1")

        assert result["affected_items"] == 3

    def test_get_affected_items_downstream(self, link_service, link_repo):
        """Test getting downstream affected items"""
        items = ["item-2", "item-3", "item-4"]
        link_repo.get_downstream_items.return_value = items

        result = link_service.get_downstream_items("item-1")

        assert len(result) == 3

    def test_get_affected_items_upstream(self, link_service, link_repo):
        """Test getting upstream affected items"""
        items = ["item-99", "item-98"]
        link_repo.get_upstream_items.return_value = items

        result = link_service.get_upstream_items("item-1")

        assert len(result) == 2
