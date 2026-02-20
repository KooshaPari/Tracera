"""Tests for Specification Repositories (ADR, Contract, Feature, Scenario).

Comprehensive test coverage for specification CRUD and query operations.

Functional Requirements Coverage:
    - FR-DISC-002: Specification Parsing
    - FR-APP-002: Specification Versioning

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify ADR, Contract, Feature, and Scenario repository operations including
creation, retrieval, versioning, query by project, and metadata management.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.specification_repository import (
    ADRRepository,
    ContractRepository,
    FeatureRepository,
    ScenarioRepository,
)


class TestADRRepositoryCreate:
    """Tests for ADRRepository create method."""

    @pytest_asyncio.fixture
    async def project(self, db_session: AsyncSession) -> None:
        """Create a project for ADR tests."""
        project_repo = ProjectRepository(db_session)
        return await project_repo.create(name="ADR Test Project", description="Project for testing ADRs")

    @pytest.mark.asyncio
    async def test_create_adr_success(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating an ADR successfully."""
        repo = ADRRepository(db_session)

        adr = await repo.create(
            project_id=project.id,
            title="Use PostgreSQL for Data Storage",
            context="We need a reliable database for production",
            decision="Use PostgreSQL as the primary database",
            consequences="Team needs PostgreSQL expertise",
            status="proposed",
            created_by="test_user",
        )

        assert adr is not None
        assert adr.id is not None
        assert adr.adr_number is not None
        assert adr.adr_number.startswith("ADR-")
        assert adr.project_id == project.id
        assert adr.title == "Use PostgreSQL for Data Storage"
        assert adr.context == "We need a reliable database for production"
        assert adr.decision == "Use PostgreSQL as the primary database"
        assert adr.consequences == "Team needs PostgreSQL expertise"
        assert adr.status == "proposed"
        assert adr.version == 1

    @pytest.mark.asyncio
    async def test_create_adr_with_decision_drivers(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR with decision drivers."""
        repo = ADRRepository(db_session)

        drivers = ["scalability", "reliability", "team expertise"]
        adr = await repo.create(
            project_id=project.id,
            title="Database Choice",
            context="Need database",
            decision="PostgreSQL",
            consequences="Training needed",
            decision_drivers=drivers,
        )

        assert adr.decision_drivers == drivers

    @pytest.mark.asyncio
    async def test_create_adr_with_considered_options(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR with considered options."""
        repo = ADRRepository(db_session)

        options = [
            {"option": "PostgreSQL", "pros": "Robust", "cons": "Complexity"},
            {"option": "MySQL", "pros": "Simple", "cons": "Limited JSON"},
        ]
        adr = await repo.create(
            project_id=project.id,
            title="Database Choice",
            context="Need database",
            decision="PostgreSQL",
            consequences="Training needed",
            considered_options=options,
        )

        assert adr.considered_options == options

    @pytest.mark.asyncio
    async def test_create_adr_with_related_requirements(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR with related requirements."""
        repo = ADRRepository(db_session)

        requirements = ["REQ-001", "REQ-002"]
        adr = await repo.create(
            project_id=project.id,
            title="Database Choice",
            context="Need database",
            decision="PostgreSQL",
            consequences="Training needed",
            related_requirements=requirements,
        )

        assert adr.related_requirements == requirements

    @pytest.mark.asyncio
    async def test_create_adr_with_stakeholders(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR with stakeholders."""
        repo = ADRRepository(db_session)

        stakeholders = ["architect", "dev_lead", "dba"]
        adr = await repo.create(
            project_id=project.id,
            title="Database Choice",
            context="Need database",
            decision="PostgreSQL",
            consequences="Training needed",
            stakeholders=stakeholders,
        )

        assert adr.stakeholders == stakeholders

    @pytest.mark.asyncio
    async def test_create_adr_with_tags(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR with tags."""
        repo = ADRRepository(db_session)

        tags = ["database", "infrastructure"]
        adr = await repo.create(
            project_id=project.id,
            title="Database Choice",
            context="Need database",
            decision="PostgreSQL",
            consequences="Training needed",
            tags=tags,
        )

        assert adr.tags == tags

    @pytest.mark.asyncio
    async def test_create_adr_with_supersedes(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating ADR that supersedes another."""
        repo = ADRRepository(db_session)

        # Create original ADR
        original = await repo.create(
            project_id=project.id,
            title="Original Database Choice",
            context="Context",
            decision="MySQL",
            consequences="None",
        )

        # Create superseding ADR
        new_adr = await repo.create(
            project_id=project.id,
            title="Revised Database Choice",
            context="Context",
            decision="PostgreSQL",
            consequences="None",
            supersedes=original.id,
        )

        assert new_adr.supersedes == original.id


class TestADRRepositoryGet:
    """Tests for ADRRepository get methods."""

    @pytest_asyncio.fixture
    async def adr_setup(self, db_session: AsyncSession) -> None:
        """Create project and ADR for get tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Get Test Project")

        adr_repo = ADRRepository(db_session)
        adr = await adr_repo.create(
            project_id=project.id,
            title="Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

        return {"project": project, "adr": adr}

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, adr_setup: Any) -> None:
        """Test getting ADR by ID."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_id(adr_setup["adr"].id)

        assert adr is not None
        assert adr.id == adr_setup["adr"].id

    @pytest.mark.asyncio
    async def test_get_by_id_with_project_id(self, db_session: AsyncSession, adr_setup: Any) -> None:
        """Test getting ADR by ID with project scope."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_id(adr_setup["adr"].id, project_id=adr_setup["project"].id)

        assert adr is not None
        assert adr.id == adr_setup["adr"].id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession) -> None:
        """Test getting non-existent ADR."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_id(str(uuid4()))

        assert adr is None

    @pytest.mark.asyncio
    async def test_get_by_number(self, db_session: AsyncSession, adr_setup: Any) -> None:
        """Test getting ADR by ADR number."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_number(adr_setup["adr"].adr_number)

        assert adr is not None
        assert adr.adr_number == adr_setup["adr"].adr_number

    @pytest.mark.asyncio
    async def test_get_by_number_with_project_id(self, db_session: AsyncSession, adr_setup: Any) -> None:
        """Test getting ADR by number with project scope."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_number(adr_setup["adr"].adr_number, project_id=adr_setup["project"].id)

        assert adr is not None

    @pytest.mark.asyncio
    async def test_get_by_number_not_found(self, db_session: AsyncSession) -> None:
        """Test getting ADR by non-existent number."""
        repo = ADRRepository(db_session)
        adr = await repo.get_by_number("ADR-NONEXISTENT")

        assert adr is None


class TestADRRepositoryList:
    """Tests for ADRRepository list methods."""

    @pytest_asyncio.fixture
    async def multiple_adrs(self, db_session: AsyncSession) -> None:
        """Create multiple ADRs for list tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="List Test Project")

        adr_repo = ADRRepository(db_session)
        adrs = []

        statuses = ["proposed", "accepted", "deprecated"]
        for i, status in enumerate(statuses):
            adr = await adr_repo.create(
                project_id=project.id,
                title=f"ADR {i}",
                context=f"Context {i}",
                decision=f"Decision {i}",
                consequences=f"Consequences {i}",
                status=status,
            )
            adrs.append(adr)

        return {"project": project, "adrs": adrs}

    @pytest.mark.asyncio
    async def test_list_by_project(self, db_session: AsyncSession, multiple_adrs: Any) -> None:
        """Test listing ADRs by project."""
        repo = ADRRepository(db_session)
        adrs = await repo.list_by_project(multiple_adrs["project"].id)

        assert len(adrs) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_list_by_project_with_status_filter(self, db_session: AsyncSession, multiple_adrs: Any) -> None:
        """Test listing ADRs filtered by status."""
        repo = ADRRepository(db_session)
        adrs = await repo.list_by_project(multiple_adrs["project"].id, status="proposed")

        assert len(adrs) == 1
        assert adrs[0].status == "proposed"

    @pytest.mark.asyncio
    async def test_list_by_project_with_pagination(self, db_session: AsyncSession, multiple_adrs: Any) -> None:
        """Test listing ADRs with pagination."""
        repo = ADRRepository(db_session)
        adrs = await repo.list_by_project(multiple_adrs["project"].id, limit=2, offset=0)

        assert len(adrs) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_find_by_status(self, db_session: AsyncSession, multiple_adrs: Any) -> None:
        """Test finding ADRs by status."""
        repo = ADRRepository(db_session)
        adrs = await repo.find_by_status(multiple_adrs["project"].id, status="accepted")

        assert len(adrs) == 1
        assert adrs[0].status == "accepted"


class TestADRRepositoryUpdate:
    """Tests for ADRRepository update method."""

    @pytest_asyncio.fixture
    async def adr_for_update(self, db_session: AsyncSession) -> None:
        """Create ADR for update tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Update Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Original Title",
            context="Original Context",
            decision="Original Decision",
            consequences="Original Consequences",
        )

    @pytest.mark.asyncio
    async def test_update_adr_success(self, db_session: AsyncSession, adr_for_update: Any) -> None:
        """Test updating ADR successfully."""
        repo = ADRRepository(db_session)

        updated = await repo.update(
            adr_for_update.id,
            expected_version=1,
            title="Updated Title",
            context="Updated Context",
        )

        assert updated.title == "Updated Title"
        assert updated.context == "Updated Context"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_adr_not_found(self, db_session: AsyncSession) -> None:
        """Test updating non-existent ADR."""
        repo = ADRRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update(str(uuid4()), expected_version=1, title="New Title")

    @pytest.mark.asyncio
    async def test_update_adr_concurrency_error(self, db_session: AsyncSession, adr_for_update: Any) -> None:
        """Test optimistic locking on update."""
        repo = ADRRepository(db_session)

        with pytest.raises(ConcurrencyError):
            await repo.update(
                adr_for_update.id,
                expected_version=999,  # Wrong version
                title="New Title",
            )


class TestADRRepositoryTransition:
    """Tests for ADRRepository status transitions."""

    @pytest_asyncio.fixture
    async def adr_for_transition(self, db_session: AsyncSession) -> None:
        """Create ADR for transition tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Transition Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Transition Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
            status="proposed",
        )

    @pytest.mark.asyncio
    async def test_transition_proposed_to_accepted(self, db_session: AsyncSession, adr_for_transition: Any) -> None:
        """Test transitioning from proposed to accepted."""
        repo = ADRRepository(db_session)

        updated = await repo.transition_status(adr_for_transition.id, "accepted")

        assert updated.status == "accepted"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_transition_proposed_to_rejected(self, db_session: AsyncSession, adr_for_transition: Any) -> None:
        """Test transitioning from proposed to rejected."""
        repo = ADRRepository(db_session)

        updated = await repo.transition_status(adr_for_transition.id, "rejected")

        assert updated.status == "rejected"

    @pytest.mark.asyncio
    async def test_transition_invalid(self, db_session: AsyncSession, adr_for_transition: Any) -> None:
        """Test invalid status transition."""
        repo = ADRRepository(db_session)

        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(adr_for_transition.id, "deprecated")

    @pytest.mark.asyncio
    async def test_transition_not_found(self, db_session: AsyncSession) -> None:
        """Test transition on non-existent ADR."""
        repo = ADRRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.transition_status(str(uuid4()), "accepted")


class TestADRRepositoryVerify:
    """Tests for ADRRepository verify_compliance method."""

    @pytest_asyncio.fixture
    async def adr_for_verify(self, db_session: AsyncSession) -> None:
        """Create ADR for verification tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Verify Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Verify Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

    @pytest.mark.asyncio
    async def test_verify_compliance(self, db_session: AsyncSession, adr_for_verify: Any) -> None:
        """Test verifying compliance score."""
        repo = ADRRepository(db_session)

        updated = await repo.verify_compliance(adr_for_verify.id, compliance_score=0.85)

        assert updated.compliance_score == 0.85
        assert updated.last_verified_at is not None
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_verify_compliance_not_found(self, db_session: AsyncSession) -> None:
        """Test verifying non-existent ADR."""
        repo = ADRRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.verify_compliance(str(uuid4()), compliance_score=0.5)


class TestADRRepositoryDelete:
    """Tests for ADRRepository delete method."""

    @pytest_asyncio.fixture
    async def adr_for_delete(self, db_session: AsyncSession) -> None:
        """Create ADR for delete tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Delete Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Delete Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

    @pytest.mark.asyncio
    async def test_delete_adr(self, db_session: AsyncSession, adr_for_delete: Any) -> None:
        """Test deleting ADR."""
        repo = ADRRepository(db_session)

        result = await repo.delete(adr_for_delete.id)
        assert result is True

        # Verify deleted
        deleted = await repo.get_by_id(adr_for_delete.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_adr_not_found(self, db_session: AsyncSession) -> None:
        """Test deleting non-existent ADR."""
        repo = ADRRepository(db_session)

        result = await repo.delete(str(uuid4()))
        assert result is False


class TestADRRepositoryStats:
    """Tests for ADRRepository statistics methods."""

    @pytest_asyncio.fixture
    async def adrs_for_stats(self, db_session: AsyncSession) -> None:
        """Create ADRs for statistics tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Stats Test Project")

        adr_repo = ADRRepository(db_session)

        # Create ADRs with different statuses
        for _ in range(3):
            await adr_repo.create(
                project_id=project.id,
                title="Proposed ADR",
                context="C",
                decision="D",
                consequences="Q",
                status="proposed",
            )

        for _ in range(2):
            await adr_repo.create(
                project_id=project.id,
                title="Accepted ADR",
                context="C",
                decision="D",
                consequences="Q",
                status="accepted",
            )

        return project

    @pytest.mark.asyncio
    async def test_count_by_status(self, db_session: AsyncSession, adrs_for_stats: Any) -> None:
        """Test counting ADRs by status."""
        repo = ADRRepository(db_session)

        counts = await repo.count_by_status(adrs_for_stats.id)

        assert counts.get("proposed") == COUNT_THREE
        assert counts.get("accepted") == COUNT_TWO


# ============================================================================
# Contract Repository Tests
# ============================================================================


class TestContractRepositoryCreate:
    """Tests for ContractRepository create method."""

    @pytest_asyncio.fixture
    async def setup_for_contract(self, db_session: AsyncSession) -> None:
        """Create project and item for contract tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Test Project")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Test Requirement",
            item_type="requirement",
            view="requirements",
        )

        return {"project": project, "item": item}

    @pytest.mark.asyncio
    async def test_create_contract_success(self, db_session: AsyncSession, setup_for_contract: Any) -> None:
        """Test creating a contract successfully."""
        repo = ContractRepository(db_session)

        contract = await repo.create(
            project_id=setup_for_contract["project"].id,
            item_id=setup_for_contract["item"].id,
            title="User Login Contract",
            contract_type="api",
            status="draft",
        )

        assert contract is not None
        assert contract.id is not None
        assert contract.contract_number.startswith("CTR-")
        assert contract.title == "User Login Contract"
        assert contract.contract_type == "api"
        assert contract.status == "draft"
        assert contract.version == 1

    @pytest.mark.asyncio
    async def test_create_contract_with_preconditions(self, db_session: AsyncSession, setup_for_contract: Any) -> None:
        """Test creating contract with preconditions."""
        repo = ContractRepository(db_session)

        preconditions = [
            {"condition": "User exists", "type": "state"},
            {"condition": "Session valid", "type": "auth"},
        ]
        contract = await repo.create(
            project_id=setup_for_contract["project"].id,
            item_id=setup_for_contract["item"].id,
            title="Test Contract",
            contract_type="api",
            preconditions=preconditions,
        )

        assert contract.preconditions == preconditions

    @pytest.mark.asyncio
    async def test_create_contract_with_postconditions(self, db_session: AsyncSession, setup_for_contract: Any) -> None:
        """Test creating contract with postconditions."""
        repo = ContractRepository(db_session)

        postconditions = [
            {"condition": "User logged in", "type": "state"},
        ]
        contract = await repo.create(
            project_id=setup_for_contract["project"].id,
            item_id=setup_for_contract["item"].id,
            title="Test Contract",
            contract_type="api",
            postconditions=postconditions,
        )

        assert contract.postconditions == postconditions

    @pytest.mark.asyncio
    async def test_create_contract_with_states(self, db_session: AsyncSession, setup_for_contract: Any) -> None:
        """Test creating contract with state machine."""
        repo = ContractRepository(db_session)

        states = ["idle", "loading", "success", "error"]
        transitions = [
            {"from": "idle", "to": "loading", "trigger": "submit"},
            {"from": "loading", "to": "success", "trigger": "response"},
        ]
        contract = await repo.create(
            project_id=setup_for_contract["project"].id,
            item_id=setup_for_contract["item"].id,
            title="Stateful Contract",
            contract_type="state_machine",
            states=states,
            transitions=transitions,
        )

        assert contract.states == states
        assert contract.transitions == transitions


class TestContractRepositoryGet:
    """Tests for ContractRepository get methods."""

    @pytest_asyncio.fixture
    async def contract_setup(self, db_session: AsyncSession) -> None:
        """Create contract for get tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Get Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        contract = await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Test Contract",
            contract_type="api",
        )

        return {"project": project, "item": item, "contract": contract}

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, contract_setup: Any) -> None:
        """Test getting contract by ID."""
        repo = ContractRepository(db_session)
        contract = await repo.get_by_id(contract_setup["contract"].id)

        assert contract is not None
        assert contract.id == contract_setup["contract"].id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession) -> None:
        """Test getting non-existent contract."""
        repo = ContractRepository(db_session)
        contract = await repo.get_by_id(str(uuid4()))

        assert contract is None

    @pytest.mark.asyncio
    async def test_get_by_number(self, db_session: AsyncSession, contract_setup: Any) -> None:
        """Test getting contract by number."""
        repo = ContractRepository(db_session)
        contract = await repo.get_by_number(contract_setup["contract"].contract_number)

        assert contract is not None


class TestContractRepositoryList:
    """Tests for ContractRepository list methods."""

    @pytest_asyncio.fixture
    async def multiple_contracts(self, db_session: AsyncSession) -> None:
        """Create multiple contracts for list tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract List Test")

        item_repo = ItemRepository(db_session)
        items = []
        for i in range(3):
            item = await item_repo.create(
                project_id=project.id,
                title=f"Requirement {i}",
                item_type="requirement",
                view="requirements",
            )
            items.append(item)

        contract_repo = ContractRepository(db_session)
        contracts = []
        types = ["api", "state_machine", "api"]
        for i, (item, ctype) in enumerate(zip(items, types, strict=False)):
            contract = await contract_repo.create(
                project_id=project.id,
                item_id=item.id,
                title=f"Contract {i}",
                contract_type=ctype,
            )
            contracts.append(contract)

        return {"project": project, "items": items, "contracts": contracts}

    @pytest.mark.asyncio
    async def test_list_by_project(self, db_session: AsyncSession, multiple_contracts: Any) -> None:
        """Test listing contracts by project."""
        repo = ContractRepository(db_session)
        contracts = await repo.list_by_project(multiple_contracts["project"].id)

        assert len(contracts) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_type(self, db_session: AsyncSession, multiple_contracts: Any) -> None:
        """Test listing contracts filtered by type."""
        repo = ContractRepository(db_session)
        contracts = await repo.list_by_project(multiple_contracts["project"].id, contract_type="api")

        assert len(contracts) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_item(self, db_session: AsyncSession, multiple_contracts: Any) -> None:
        """Test listing contracts by item."""
        repo = ContractRepository(db_session)
        contracts = await repo.list_by_item(multiple_contracts["items"][0].id)

        assert len(contracts) == 1


# ============================================================================
# Feature Repository Tests
# ============================================================================


class TestFeatureRepositoryCreate:
    """Tests for FeatureRepository create method."""

    @pytest_asyncio.fixture
    async def project(self, db_session: AsyncSession) -> None:
        """Create project for feature tests."""
        project_repo = ProjectRepository(db_session)
        return await project_repo.create(name="Feature Test Project")

    @pytest.mark.asyncio
    async def test_create_feature_success(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating a feature successfully."""
        repo = FeatureRepository(db_session)

        feature = await repo.create(
            project_id=project.id,
            name="User Authentication",
            description="Users can log in and out",
            tags=["auth", "security"],
        )

        assert feature is not None
        assert feature.id is not None
        assert feature.feature_number.startswith("FEAT-")
        assert feature.name == "User Authentication"
        assert feature.status == "draft"
        assert feature.version == 1

    @pytest.mark.asyncio
    async def test_create_feature_with_user_story(self, db_session: AsyncSession, project: Any) -> None:
        """Test creating feature with user story format."""
        repo = FeatureRepository(db_session)

        feature = await repo.create(
            project_id=project.id,
            name="Feature with User Story",
            as_a="user",
            i_want="to log in",
            so_that="I can access my account",
        )

        assert feature.as_a == "user"
        assert feature.i_want == "to log in"
        assert feature.so_that == "I can access my account"


class TestFeatureRepositoryGet:
    """Tests for FeatureRepository get methods."""

    @pytest_asyncio.fixture
    async def feature_setup(self, db_session: AsyncSession) -> None:
        """Create feature for get tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Get Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        return {"project": project, "feature": feature}

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, feature_setup: Any) -> None:
        """Test getting feature by ID."""
        repo = FeatureRepository(db_session)
        feature = await repo.get_by_id(feature_setup["feature"].id)

        assert feature is not None
        assert feature.id == feature_setup["feature"].id

    @pytest.mark.asyncio
    async def test_get_by_number(self, db_session: AsyncSession, feature_setup: Any) -> None:
        """Test getting feature by number."""
        repo = FeatureRepository(db_session)
        feature = await repo.get_by_number(feature_setup["feature"].feature_number)

        assert feature is not None


class TestFeatureRepositoryList:
    """Tests for FeatureRepository list methods."""

    @pytest_asyncio.fixture
    async def multiple_features(self, db_session: AsyncSession) -> None:
        """Create multiple features for list tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature List Test")

        feature_repo = FeatureRepository(db_session)
        features = []
        for i in range(3):
            feature = await feature_repo.create(
                project_id=project.id,
                name=f"Feature {i}",
            )
            features.append(feature)

        return {"project": project, "features": features}

    @pytest.mark.asyncio
    async def test_list_by_project(self, db_session: AsyncSession, multiple_features: Any) -> None:
        """Test listing features by project."""
        repo = FeatureRepository(db_session)
        features = await repo.list_by_project(multiple_features["project"].id)

        assert len(features) == COUNT_THREE


# ============================================================================
# Scenario Repository Tests
# ============================================================================


class TestScenarioRepositoryCreate:
    """Tests for ScenarioRepository create method."""

    @pytest_asyncio.fixture
    async def feature_setup(self, db_session: AsyncSession) -> None:
        """Create project and feature for scenario tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Test Project")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        return {"project": project, "feature": feature}

    @pytest.mark.asyncio
    async def test_create_scenario_success(self, db_session: AsyncSession, feature_setup: Any) -> None:
        """Test creating a scenario successfully."""
        repo = ScenarioRepository(db_session)

        given_steps = [{"text": "a user exists"}]
        when_steps = [{"text": "the user logs in"}]
        then_steps = [{"text": "the user is authenticated"}]

        scenario = await repo.create(
            feature_id=feature_setup["feature"].id,
            title="User Login Scenario",
            gherkin_text="Given a user exists\nWhen the user logs in\nThen the user is authenticated",
            given_steps=given_steps,
            when_steps=when_steps,
            then_steps=then_steps,
        )

        assert scenario is not None
        assert scenario.id is not None
        assert scenario.scenario_number.startswith("SC-")
        assert scenario.title == "User Login Scenario"
        assert scenario.given_steps == given_steps
        assert scenario.version == 1

    @pytest.mark.asyncio
    async def test_create_scenario_outline(self, db_session: AsyncSession, feature_setup: Any) -> None:
        """Test creating a scenario outline with examples."""
        repo = ScenarioRepository(db_session)

        examples = {"headers": ["role", "action"], "rows": [["admin", "delete"], ["user", "read"]]}
        scenario = await repo.create(
            feature_id=feature_setup["feature"].id,
            title="Role Permissions",
            gherkin_text="Given a user with role <role>\nThen the user can <action>",
            is_outline=True,
            examples=examples,
        )

        assert scenario.is_outline is True
        assert scenario.examples == examples


class TestScenarioRepositoryGet:
    """Tests for ScenarioRepository get methods."""

    @pytest_asyncio.fixture
    async def scenario_setup(self, db_session: AsyncSession) -> None:
        """Create scenario for get tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Get Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        scenario = await scenario_repo.create(
            feature_id=feature.id,
            title="Test Scenario",
            gherkin_text="Given something\nWhen action\nThen result",
        )

        return {"project": project, "feature": feature, "scenario": scenario}

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, scenario_setup: Any) -> None:
        """Test getting scenario by ID."""
        repo = ScenarioRepository(db_session)
        scenario = await repo.get_by_id(scenario_setup["scenario"].id)

        assert scenario is not None
        assert scenario.id == scenario_setup["scenario"].id

    @pytest.mark.asyncio
    async def test_get_by_number(self, db_session: AsyncSession, scenario_setup: Any) -> None:
        """Test getting scenario by number."""
        repo = ScenarioRepository(db_session)
        scenario = await repo.get_by_number(scenario_setup["scenario"].scenario_number)

        assert scenario is not None


class TestScenarioRepositoryList:
    """Tests for ScenarioRepository list methods."""

    @pytest_asyncio.fixture
    async def multiple_scenarios(self, db_session: AsyncSession) -> None:
        """Create multiple scenarios for list tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario List Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        scenarios = []
        for i in range(3):
            scenario = await scenario_repo.create(
                feature_id=feature.id,
                title=f"Scenario {i}",
                gherkin_text=f"Given scenario {i}",
            )
            scenarios.append(scenario)

        return {"project": project, "feature": feature, "scenarios": scenarios}

    @pytest.mark.asyncio
    async def test_list_by_feature(self, db_session: AsyncSession, multiple_scenarios: Any) -> None:
        """Test listing scenarios by feature."""
        repo = ScenarioRepository(db_session)
        scenarios = await repo.list_by_feature(multiple_scenarios["feature"].id)

        assert len(scenarios) == COUNT_THREE


# ============================================================================
# Additional ADR Repository Tests - Status Transitions
# ============================================================================


class TestADRRepositoryAdditionalTransitions:
    """Additional tests for ADR status transitions."""

    @pytest_asyncio.fixture
    async def project(self, db_session: AsyncSession) -> None:
        """Create project for tests."""
        project_repo = ProjectRepository(db_session)
        return await project_repo.create(name="ADR Transition Test Project")

    @pytest.mark.asyncio
    async def test_transition_accepted_to_deprecated(self, db_session: AsyncSession, project: Any) -> None:
        """Test transitioning from accepted to deprecated."""
        adr_repo = ADRRepository(db_session)

        # Create ADR and transition to accepted first
        adr = await adr_repo.create(
            project_id=project.id,
            title="ADR to Deprecate",
            context="Context",
            decision="Decision",
            consequences="Consequences",
            status="proposed",
        )
        await adr_repo.transition_status(adr.id, "accepted")

        # Now transition to deprecated
        updated = await adr_repo.transition_status(adr.id, "deprecated")

        assert updated.status == "deprecated"
        assert updated.version == COUNT_THREE  # created=1, accepted=2, deprecated=3

    @pytest.mark.asyncio
    async def test_transition_rejected_to_proposed(self, db_session: AsyncSession, project: Any) -> None:
        """Test transitioning from rejected back to proposed."""
        adr_repo = ADRRepository(db_session)

        # Create ADR and transition to rejected
        adr = await adr_repo.create(
            project_id=project.id,
            title="ADR to Reconsider",
            context="Context",
            decision="Decision",
            consequences="Consequences",
            status="proposed",
        )
        await adr_repo.transition_status(adr.id, "rejected")

        # Now transition back to proposed
        updated = await adr_repo.transition_status(adr.id, "proposed")

        assert updated.status == "proposed"
        assert updated.version == COUNT_THREE

    @pytest.mark.asyncio
    async def test_transition_deprecated_is_terminal(self, db_session: AsyncSession, project: Any) -> None:
        """Test that deprecated is a terminal state."""
        adr_repo = ADRRepository(db_session)

        adr = await adr_repo.create(
            project_id=project.id,
            title="Terminal ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
            status="proposed",
        )
        await adr_repo.transition_status(adr.id, "accepted")
        await adr_repo.transition_status(adr.id, "deprecated")

        # Try to transition from deprecated (should fail)
        with pytest.raises(ValueError, match="Invalid status transition"):
            await adr_repo.transition_status(adr.id, "proposed")


class TestADRNumberFormat:
    """Tests for ADR number format validation."""

    @pytest_asyncio.fixture
    async def project(self, db_session: AsyncSession) -> None:
        """Create project for tests."""
        project_repo = ProjectRepository(db_session)
        return await project_repo.create(name="ADR Number Test Project")

    @pytest.mark.asyncio
    async def test_adr_number_format(self, db_session: AsyncSession, project: Any) -> None:
        """Test ADR number format is ADR-YYYYMMDD-XXXXXXXX."""
        import re

        adr_repo = ADRRepository(db_session)
        adr = await adr_repo.create(
            project_id=project.id,
            title="Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

        # Pattern: ADR-YYYYMMDD-8HEXCHARS
        pattern = r"^ADR-\d{8}-[A-F0-9]{8}$"
        assert re.match(pattern, adr.adr_number), f"ADR number '{adr.adr_number}' doesn't match expected format"


class TestADRRepositoryFindRelated:
    """Tests for ADR find_related method."""

    @pytest_asyncio.fixture
    async def related_adrs(self, db_session: AsyncSession) -> None:
        """Create related ADRs for tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Related ADR Test Project")

        adr_repo = ADRRepository(db_session)

        # Create original ADR
        original = await adr_repo.create(
            project_id=project.id,
            title="Original ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

        # Create superseding ADR
        superseding = await adr_repo.create(
            project_id=project.id,
            title="Superseding ADR",
            context="New Context",
            decision="New Decision",
            consequences="New Consequences",
            supersedes=original.id,
        )

        return {"project": project, "original": original, "superseding": superseding}

    @pytest.mark.asyncio
    async def test_find_related_adrs(self, db_session: AsyncSession, related_adrs: Any) -> None:
        """Test finding related ADRs."""
        repo = ADRRepository(db_session)
        related = await repo.find_related(related_adrs["original"].id)

        # Should find the original and the superseding ADR
        assert len(related) >= 1
        ids = [adr.id for adr in related]
        assert related_adrs["original"].id in ids


# ============================================================================
# Contract Repository Additional Tests
# ============================================================================


class TestContractRepositoryUpdate:
    """Tests for ContractRepository update method."""

    @pytest_asyncio.fixture
    async def contract_for_update(self, db_session: AsyncSession) -> None:
        """Create contract for update tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Update Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        contract = await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Original Contract",
            contract_type="api",
        )

        return {"project": project, "item": item, "contract": contract}

    @pytest.mark.asyncio
    async def test_update_contract_success(self, db_session: AsyncSession, contract_for_update: Any) -> None:
        """Test updating contract successfully."""
        repo = ContractRepository(db_session)

        updated = await repo.update(
            contract_for_update["contract"].id,
            expected_version=1,
            title="Updated Contract",
        )

        assert updated.title == "Updated Contract"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_contract_not_found(self, db_session: AsyncSession) -> None:
        """Test updating non-existent contract."""
        repo = ContractRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update(
                str(uuid4()),
                expected_version=1,
                title="New Title",
            )

    @pytest.mark.asyncio
    async def test_update_contract_concurrency_error(self, db_session: AsyncSession, contract_for_update: Any) -> None:
        """Test optimistic locking on contract update."""
        repo = ContractRepository(db_session)

        with pytest.raises(ConcurrencyError):
            await repo.update(
                contract_for_update["contract"].id,
                expected_version=999,  # Wrong version
                title="New Title",
            )


class TestContractRepositoryTransition:
    """Tests for ContractRepository status transitions."""

    @pytest_asyncio.fixture
    async def contract_for_transition(self, db_session: AsyncSession) -> None:
        """Create contract for transition tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Transition Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        return await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Transition Contract",
            contract_type="api",
            status="draft",
        )

    @pytest.mark.asyncio
    async def test_transition_draft_to_review(self, db_session: AsyncSession, contract_for_transition: Any) -> None:
        """Test transitioning contract from draft to review."""
        repo = ContractRepository(db_session)

        updated = await repo.transition_status(contract_for_transition.id, "review")

        assert updated.status == "review"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_transition_review_to_approved(self, db_session: AsyncSession, contract_for_transition: Any) -> None:
        """Test transitioning contract from review to approved."""
        repo = ContractRepository(db_session)

        # First transition to review
        await repo.transition_status(contract_for_transition.id, "review")

        # Then to approved
        updated = await repo.transition_status(contract_for_transition.id, "approved")

        assert updated.status == "approved"
        assert updated.version == COUNT_THREE

    @pytest.mark.asyncio
    async def test_transition_approved_to_archived(
        self, db_session: AsyncSession, contract_for_transition: Any
    ) -> None:
        """Test transitioning contract from approved to archived."""
        repo = ContractRepository(db_session)

        # Transition through states
        await repo.transition_status(contract_for_transition.id, "review")
        await repo.transition_status(contract_for_transition.id, "approved")

        # Then to archived
        updated = await repo.transition_status(contract_for_transition.id, "archived")

        assert updated.status == "archived"

    @pytest.mark.asyncio
    async def test_transition_invalid(self, db_session: AsyncSession, contract_for_transition: Any) -> None:
        """Test invalid status transition."""
        repo = ContractRepository(db_session)

        # Can't go directly from draft to approved
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(contract_for_transition.id, "approved")

    @pytest.mark.asyncio
    async def test_transition_archived_is_terminal(
        self, db_session: AsyncSession, contract_for_transition: Any
    ) -> None:
        """Test that archived is a terminal state."""
        repo = ContractRepository(db_session)

        # Transition to archived
        await repo.transition_status(contract_for_transition.id, "review")
        await repo.transition_status(contract_for_transition.id, "approved")
        await repo.transition_status(contract_for_transition.id, "archived")

        # Try to transition from archived (should fail)
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(contract_for_transition.id, "draft")

    @pytest.mark.asyncio
    async def test_transition_not_found(self, db_session: AsyncSession) -> None:
        """Test transition on non-existent contract."""
        repo = ContractRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.transition_status(str(uuid4()), "review")


class TestContractRepositoryDelete:
    """Tests for ContractRepository delete method."""

    @pytest_asyncio.fixture
    async def contract_for_delete(self, db_session: AsyncSession) -> None:
        """Create contract for delete tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Delete Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        return await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Delete Contract",
            contract_type="api",
        )

    @pytest.mark.asyncio
    async def test_delete_contract(self, db_session: AsyncSession, contract_for_delete: Any) -> None:
        """Test deleting contract."""
        repo = ContractRepository(db_session)

        result = await repo.delete(contract_for_delete.id)
        assert result is True

        # Verify deleted
        deleted = await repo.get_by_id(contract_for_delete.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_contract_not_found(self, db_session: AsyncSession) -> None:
        """Test deleting non-existent contract."""
        repo = ContractRepository(db_session)

        result = await repo.delete(str(uuid4()))
        assert result is False


class TestContractRepositoryStats:
    """Tests for ContractRepository statistics methods."""

    @pytest_asyncio.fixture
    async def contracts_for_stats(self, db_session: AsyncSession) -> None:
        """Create contracts for statistics tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Stats Test")

        item_repo = ItemRepository(db_session)
        items = []
        for i in range(5):
            item = await item_repo.create(
                project_id=project.id,
                title=f"Requirement {i}",
                item_type="requirement",
                view="requirements",
            )
            items.append(item)

        contract_repo = ContractRepository(db_session)

        # Create 3 API contracts and 2 state machine contracts
        types = ["api", "api", "api", "state_machine", "state_machine"]
        for i, (item, ctype) in enumerate(zip(items, types, strict=False)):
            await contract_repo.create(
                project_id=project.id,
                item_id=item.id,
                title=f"Contract {i}",
                contract_type=ctype,
            )

        return project

    @pytest.mark.asyncio
    async def test_count_by_type(self, db_session: AsyncSession, contracts_for_stats: Any) -> None:
        """Test counting contracts by type."""
        repo = ContractRepository(db_session)

        counts = await repo.count_by_type(contracts_for_stats.id)

        assert counts.get("api") == COUNT_THREE
        assert counts.get("state_machine") == COUNT_TWO


class TestContractRepositoryVerify:
    """Tests for ContractRepository verify method."""

    @pytest_asyncio.fixture
    async def contract_for_verify(self, db_session: AsyncSession) -> None:
        """Create contract for verification tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Verify Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        return await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Verify Contract",
            contract_type="api",
        )

    @pytest.mark.asyncio
    async def test_verify_contract(self, db_session: AsyncSession, contract_for_verify: Any) -> None:
        """Test verifying contract."""
        repo = ContractRepository(db_session)

        verification_result = {"passed": True, "violations": []}
        updated = await repo.verify(contract_for_verify.id, verification_result)

        assert updated.verification_result == verification_result
        assert updated.last_verified_at is not None
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_verify_contract_not_found(self, db_session: AsyncSession) -> None:
        """Test verifying non-existent contract."""
        repo = ContractRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.verify(str(uuid4()), {"passed": False})


class TestContractNumberFormat:
    """Tests for contract number format validation."""

    @pytest_asyncio.fixture
    async def setup(self, db_session: AsyncSession) -> None:
        """Create project and item for tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Number Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        return {"project": project, "item": item}

    @pytest.mark.asyncio
    async def test_contract_number_format(self, db_session: AsyncSession, setup: Any) -> None:
        """Test contract number format is CTR-YYYYMMDD-XXXXXXXX."""
        import re

        contract_repo = ContractRepository(db_session)
        contract = await contract_repo.create(
            project_id=setup["project"].id,
            item_id=setup["item"].id,
            title="Test Contract",
            contract_type="api",
        )

        # Pattern: CTR-YYYYMMDD-8HEXCHARS
        pattern = r"^CTR-\d{8}-[A-F0-9]{8}$"
        assert re.match(pattern, contract.contract_number), (
            f"Contract number '{contract.contract_number}' doesn't match expected format"
        )


# ============================================================================
# Feature Repository Additional Tests
# ============================================================================


class TestFeatureRepositoryUpdate:
    """Tests for FeatureRepository update method."""

    @pytest_asyncio.fixture
    async def feature_for_update(self, db_session: AsyncSession) -> None:
        """Create feature for update tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Update Test")

        feature_repo = FeatureRepository(db_session)
        return await feature_repo.create(
            project_id=project.id,
            name="Original Feature",
        )

    @pytest.mark.asyncio
    async def test_update_feature_success(self, db_session: AsyncSession, feature_for_update: Any) -> None:
        """Test updating feature successfully."""
        repo = FeatureRepository(db_session)

        updated = await repo.update(
            feature_for_update.id,
            expected_version=1,
            name="Updated Feature",
            description="New description",
        )

        assert updated.name == "Updated Feature"
        assert updated.description == "New description"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_feature_not_found(self, db_session: AsyncSession) -> None:
        """Test updating non-existent feature."""
        repo = FeatureRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update(
                str(uuid4()),
                expected_version=1,
                name="New Name",
            )

    @pytest.mark.asyncio
    async def test_update_feature_concurrency_error(self, db_session: AsyncSession, feature_for_update: Any) -> None:
        """Test optimistic locking on feature update."""
        repo = FeatureRepository(db_session)

        with pytest.raises(ConcurrencyError):
            await repo.update(
                feature_for_update.id,
                expected_version=999,  # Wrong version
                name="New Name",
            )


class TestFeatureRepositoryTransition:
    """Tests for FeatureRepository status transitions."""

    @pytest_asyncio.fixture
    async def feature_for_transition(self, db_session: AsyncSession) -> None:
        """Create feature for transition tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Transition Test")

        feature_repo = FeatureRepository(db_session)
        return await feature_repo.create(
            project_id=project.id,
            name="Transition Feature",
            status="draft",
        )

    @pytest.mark.asyncio
    async def test_transition_draft_to_review(self, db_session: AsyncSession, feature_for_transition: Any) -> None:
        """Test transitioning feature from draft to review."""
        repo = FeatureRepository(db_session)

        updated = await repo.transition_status(feature_for_transition.id, "review")

        assert updated.status == "review"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_transition_review_to_approved(self, db_session: AsyncSession, feature_for_transition: Any) -> None:
        """Test transitioning feature from review to approved."""
        repo = FeatureRepository(db_session)

        await repo.transition_status(feature_for_transition.id, "review")
        updated = await repo.transition_status(feature_for_transition.id, "approved")

        assert updated.status == "approved"

    @pytest.mark.asyncio
    async def test_transition_approved_to_implemented(
        self, db_session: AsyncSession, feature_for_transition: Any
    ) -> None:
        """Test transitioning feature from approved to implemented."""
        repo = FeatureRepository(db_session)

        await repo.transition_status(feature_for_transition.id, "review")
        await repo.transition_status(feature_for_transition.id, "approved")
        updated = await repo.transition_status(feature_for_transition.id, "implemented")

        assert updated.status == "implemented"

    @pytest.mark.asyncio
    async def test_transition_invalid(self, db_session: AsyncSession, feature_for_transition: Any) -> None:
        """Test invalid status transition."""
        repo = FeatureRepository(db_session)

        # Can't go directly from draft to implemented
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(feature_for_transition.id, "implemented")

    @pytest.mark.asyncio
    async def test_transition_not_found(self, db_session: AsyncSession) -> None:
        """Test transition on non-existent feature."""
        repo = FeatureRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.transition_status(str(uuid4()), "review")


class TestFeatureRepositoryDelete:
    """Tests for FeatureRepository delete method with cascade."""

    @pytest_asyncio.fixture
    async def feature_with_scenarios(self, db_session: AsyncSession) -> None:
        """Create feature with scenarios for cascade delete tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Delete Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Feature to Delete",
        )

        scenario_repo = ScenarioRepository(db_session)
        scenarios = []
        for i in range(3):
            scenario = await scenario_repo.create(
                feature_id=feature.id,
                title=f"Scenario {i}",
                gherkin_text=f"Given scenario {i}",
            )
            scenarios.append(scenario)

        return {"project": project, "feature": feature, "scenarios": scenarios}

    @pytest.mark.asyncio
    async def test_delete_feature_cascades_to_scenarios(
        self, db_session: AsyncSession, feature_with_scenarios: Any
    ) -> None:
        """Test that deleting a feature also deletes its scenarios."""
        feature_repo = FeatureRepository(db_session)
        scenario_repo = ScenarioRepository(db_session)

        # Verify scenarios exist
        scenarios_before = await scenario_repo.list_by_feature(feature_with_scenarios["feature"].id)
        assert len(scenarios_before) == COUNT_THREE

        # Delete feature
        result = await feature_repo.delete(feature_with_scenarios["feature"].id)
        assert result is True

        # Verify feature is deleted
        deleted_feature = await feature_repo.get_by_id(feature_with_scenarios["feature"].id)
        assert deleted_feature is None

        # Verify scenarios are also deleted
        scenarios_after = await scenario_repo.list_by_feature(feature_with_scenarios["feature"].id)
        assert len(scenarios_after) == 0

    @pytest.mark.asyncio
    async def test_delete_feature_not_found(self, db_session: AsyncSession) -> None:
        """Test deleting non-existent feature."""
        repo = FeatureRepository(db_session)

        result = await repo.delete(str(uuid4()))
        assert result is False


class TestFeatureRepositoryListWithScenarios:
    """Tests for FeatureRepository list_with_scenarios method."""

    @pytest_asyncio.fixture
    async def features_with_scenarios(self, db_session: AsyncSession) -> None:
        """Create features with scenarios for tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature List With Scenarios Test")

        feature_repo = FeatureRepository(db_session)
        scenario_repo = ScenarioRepository(db_session)

        features = []
        for i in range(2):
            feature = await feature_repo.create(
                project_id=project.id,
                name=f"Feature {i}",
            )
            features.append(feature)

            # Add scenarios to each feature
            for j in range(2):
                await scenario_repo.create(
                    feature_id=feature.id,
                    title=f"Scenario {i}-{j}",
                    gherkin_text=f"Given feature {i} scenario {j}",
                )

        return {"project": project, "features": features}

    @pytest.mark.asyncio
    async def test_list_with_scenarios(self, db_session: AsyncSession, features_with_scenarios: Any) -> None:
        """Test listing features with their scenarios."""
        repo = FeatureRepository(db_session)

        results = await repo.list_with_scenarios(features_with_scenarios["project"].id)

        assert len(results) == COUNT_TWO
        for _, scenarios in results:
            assert len(scenarios) == COUNT_TWO


class TestFeatureNumberFormat:
    """Tests for feature number format validation."""

    @pytest_asyncio.fixture
    async def project(self, db_session: AsyncSession) -> None:
        """Create project for tests."""
        project_repo = ProjectRepository(db_session)
        return await project_repo.create(name="Feature Number Test")

    @pytest.mark.asyncio
    async def test_feature_number_format(self, db_session: AsyncSession, project: Any) -> None:
        """Test feature number format is FEAT-YYYYMMDD-XXXXXXXX."""
        import re

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        # Pattern: FEAT-YYYYMMDD-8HEXCHARS
        pattern = r"^FEAT-\d{8}-[A-F0-9]{8}$"
        assert re.match(pattern, feature.feature_number), (
            f"Feature number '{feature.feature_number}' doesn't match expected format"
        )


# ============================================================================
# Scenario Repository Additional Tests
# ============================================================================


class TestScenarioRepositoryUpdate:
    """Tests for ScenarioRepository update method."""

    @pytest_asyncio.fixture
    async def scenario_for_update(self, db_session: AsyncSession) -> None:
        """Create scenario for update tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Update Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Original Scenario",
            gherkin_text="Given original",
        )

    @pytest.mark.asyncio
    async def test_update_scenario_success(self, db_session: AsyncSession, scenario_for_update: Any) -> None:
        """Test updating scenario successfully."""
        repo = ScenarioRepository(db_session)

        updated = await repo.update(
            scenario_for_update.id,
            expected_version=1,
            title="Updated Scenario",
            gherkin_text="Given updated",
        )

        assert updated.title == "Updated Scenario"
        assert updated.gherkin_text == "Given updated"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_scenario_not_found(self, db_session: AsyncSession) -> None:
        """Test updating non-existent scenario."""
        repo = ScenarioRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update(
                str(uuid4()),
                expected_version=1,
                title="New Title",
            )

    @pytest.mark.asyncio
    async def test_update_scenario_concurrency_error(self, db_session: AsyncSession, scenario_for_update: Any) -> None:
        """Test optimistic locking on scenario update."""
        repo = ScenarioRepository(db_session)

        with pytest.raises(ConcurrencyError):
            await repo.update(
                scenario_for_update.id,
                expected_version=999,  # Wrong version
                title="New Title",
            )


class TestScenarioRepositoryTransition:
    """Tests for ScenarioRepository status transitions."""

    @pytest_asyncio.fixture
    async def scenario_for_transition(self, db_session: AsyncSession) -> None:
        """Create scenario for transition tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Transition Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Transition Scenario",
            gherkin_text="Given transition test",
            status="draft",
        )

    @pytest.mark.asyncio
    async def test_transition_draft_to_ready(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from draft to ready."""
        repo = ScenarioRepository(db_session)

        updated = await repo.transition_status(scenario_for_transition.id, "ready")

        assert updated.status == "ready"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_transition_ready_to_executing(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from ready to executing."""
        repo = ScenarioRepository(db_session)

        await repo.transition_status(scenario_for_transition.id, "ready")
        updated = await repo.transition_status(scenario_for_transition.id, "executing")

        assert updated.status == "executing"

    @pytest.mark.asyncio
    async def test_transition_executing_to_passed(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from executing to passed."""
        repo = ScenarioRepository(db_session)

        await repo.transition_status(scenario_for_transition.id, "ready")
        await repo.transition_status(scenario_for_transition.id, "executing")
        updated = await repo.transition_status(scenario_for_transition.id, "passed")

        assert updated.status == "passed"

    @pytest.mark.asyncio
    async def test_transition_executing_to_failed(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from executing to failed."""
        repo = ScenarioRepository(db_session)

        await repo.transition_status(scenario_for_transition.id, "ready")
        await repo.transition_status(scenario_for_transition.id, "executing")
        updated = await repo.transition_status(scenario_for_transition.id, "failed")

        assert updated.status == "failed"

    @pytest.mark.asyncio
    async def test_transition_failed_to_executing_retry(
        self, db_session: AsyncSession, scenario_for_transition: Any
    ) -> None:
        """Test transitioning scenario from failed back to executing (retry)."""
        repo = ScenarioRepository(db_session)

        await repo.transition_status(scenario_for_transition.id, "ready")
        await repo.transition_status(scenario_for_transition.id, "executing")
        await repo.transition_status(scenario_for_transition.id, "failed")

        # Retry execution
        updated = await repo.transition_status(scenario_for_transition.id, "executing")

        assert updated.status == "executing"

    @pytest.mark.asyncio
    async def test_transition_invalid(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test invalid status transition."""
        repo = ScenarioRepository(db_session)

        # Can't go directly from draft to passed
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(scenario_for_transition.id, "passed")

    @pytest.mark.asyncio
    async def test_transition_not_found(self, db_session: AsyncSession) -> None:
        """Test transition on non-existent scenario."""
        repo = ScenarioRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.transition_status(str(uuid4()), "ready")


class TestScenarioRepositoryDelete:
    """Tests for ScenarioRepository delete method."""

    @pytest_asyncio.fixture
    async def scenario_for_delete(self, db_session: AsyncSession) -> None:
        """Create scenario for delete tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Delete Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Delete Scenario",
            gherkin_text="Given delete test",
        )

    @pytest.mark.asyncio
    async def test_delete_scenario(self, db_session: AsyncSession, scenario_for_delete: Any) -> None:
        """Test deleting scenario."""
        repo = ScenarioRepository(db_session)

        result = await repo.delete(scenario_for_delete.id)
        assert result is True

        # Verify deleted
        deleted = await repo.get_by_id(scenario_for_delete.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_scenario_not_found(self, db_session: AsyncSession) -> None:
        """Test deleting non-existent scenario."""
        repo = ScenarioRepository(db_session)

        result = await repo.delete(str(uuid4()))
        assert result is False


class TestScenarioRepositoryStats:
    """Tests for ScenarioRepository statistics methods."""

    @pytest_asyncio.fixture
    async def scenarios_for_stats(self, db_session: AsyncSession) -> None:
        """Create scenarios for statistics tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Stats Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Stats Feature",
        )

        scenario_repo = ScenarioRepository(db_session)

        # Create scenarios with different statuses and pass rates
        statuses = ["draft", "draft", "ready", "passed", "failed"]
        pass_rates = [0.0, 0.0, 0.5, 1.0, 0.0]

        for i, (status, pass_rate) in enumerate(zip(statuses, pass_rates, strict=False)):
            await scenario_repo.create(
                feature_id=feature.id,
                title=f"Scenario {i}",
                gherkin_text=f"Given scenario {i}",
                status=status,
                pass_rate=pass_rate,
            )

        return feature

    @pytest.mark.asyncio
    async def test_count_by_status(self, db_session: AsyncSession, scenarios_for_stats: Any) -> None:
        """Test counting scenarios by status."""
        repo = ScenarioRepository(db_session)

        counts = await repo.count_by_status(scenarios_for_stats.id)

        assert counts.get("draft") == COUNT_TWO
        assert counts.get("ready") == 1
        assert counts.get("passed") == 1
        assert counts.get("failed") == 1

    @pytest.mark.asyncio
    async def test_get_average_pass_rate(self, db_session: AsyncSession, scenarios_for_stats: Any) -> None:
        """Test getting average pass rate for scenarios."""
        repo = ScenarioRepository(db_session)

        avg_pass_rate = await repo.get_average_pass_rate(scenarios_for_stats.id)

        # Average of [0.0, 0.0, 0.5, 1.0, 0.0] = 0.3
        assert abs(avg_pass_rate - 0.3) < 0.01

    @pytest.mark.asyncio
    async def test_get_average_pass_rate_no_scenarios(self, db_session: AsyncSession) -> None:
        """Test getting average pass rate when no scenarios exist."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Empty Feature Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Empty Feature",
        )

        repo = ScenarioRepository(db_session)
        avg_pass_rate = await repo.get_average_pass_rate(feature.id)

        assert avg_pass_rate == 0.0


class TestScenarioRepositoryUpdatePassRate:
    """Tests for ScenarioRepository update_pass_rate method."""

    @pytest_asyncio.fixture
    async def scenario_for_pass_rate(self, db_session: AsyncSession) -> None:
        """Create scenario for pass rate tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Pass Rate Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Pass Rate Scenario",
            gherkin_text="Given pass rate test",
            pass_rate=0.0,
        )

    @pytest.mark.asyncio
    async def test_update_pass_rate(self, db_session: AsyncSession, scenario_for_pass_rate: Any) -> None:
        """Test updating scenario pass rate."""
        repo = ScenarioRepository(db_session)

        updated = await repo.update_pass_rate(scenario_for_pass_rate.id, 0.85)

        assert updated.pass_rate == 0.85
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_pass_rate_not_found(self, db_session: AsyncSession) -> None:
        """Test updating pass rate for non-existent scenario."""
        repo = ScenarioRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update_pass_rate(str(uuid4()), 0.5)


class TestScenarioRepositoryFindByStatus:
    """Tests for ScenarioRepository find_by_status method."""

    @pytest_asyncio.fixture
    async def scenarios_with_statuses(self, db_session: AsyncSession) -> None:
        """Create scenarios with different statuses for tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Find By Status Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        statuses = ["draft", "draft", "ready", "ready", "passed"]

        for i, status in enumerate(statuses):
            await scenario_repo.create(
                feature_id=feature.id,
                title=f"Scenario {i}",
                gherkin_text=f"Given scenario {i}",
                status=status,
            )

        return feature

    @pytest.mark.asyncio
    async def test_find_by_status_draft(self, db_session: AsyncSession, scenarios_with_statuses: Any) -> None:
        """Test finding scenarios by draft status."""
        repo = ScenarioRepository(db_session)

        scenarios = await repo.find_by_status(scenarios_with_statuses.id, "draft")

        assert len(scenarios) == COUNT_TWO
        for s in scenarios:
            assert s.status == "draft"

    @pytest.mark.asyncio
    async def test_find_by_status_ready(self, db_session: AsyncSession, scenarios_with_statuses: Any) -> None:
        """Test finding scenarios by ready status."""
        repo = ScenarioRepository(db_session)

        scenarios = await repo.find_by_status(scenarios_with_statuses.id, "ready")

        assert len(scenarios) == COUNT_TWO
        for s in scenarios:
            assert s.status == "ready"

    @pytest.mark.asyncio
    async def test_find_by_status_passed(self, db_session: AsyncSession, scenarios_with_statuses: Any) -> None:
        """Test finding scenarios by passed status."""
        repo = ScenarioRepository(db_session)

        scenarios = await repo.find_by_status(scenarios_with_statuses.id, "passed")

        assert len(scenarios) == 1
        assert scenarios[0].status == "passed"


class TestScenarioNumberFormat:
    """Tests for scenario number format validation."""

    @pytest_asyncio.fixture
    async def feature(self, db_session: AsyncSession) -> None:
        """Create feature for tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Number Test")

        feature_repo = FeatureRepository(db_session)
        return await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

    @pytest.mark.asyncio
    async def test_scenario_number_format(self, db_session: AsyncSession, feature: Any) -> None:
        """Test scenario number format is SC-YYYYMMDD-XXXXXXXX."""
        import re

        scenario_repo = ScenarioRepository(db_session)
        scenario = await scenario_repo.create(
            feature_id=feature.id,
            title="Test Scenario",
            gherkin_text="Given test",
        )

        # Pattern: SC-YYYYMMDD-8HEXCHARS
        pattern = r"^SC-\d{8}-[A-F0-9]{8}$"
        assert re.match(pattern, scenario.scenario_number), (
            f"Scenario number '{scenario.scenario_number}' doesn't match expected format"
        )


# ============================================================================
# Additional Coverage Tests - Edge Cases and Filters
# ============================================================================


class TestADRRepositoryUpdateEdgeCases:
    """Tests for ADRRepository update edge cases."""

    @pytest_asyncio.fixture
    async def adr_for_edge_cases(self, db_session: AsyncSession) -> None:
        """Create ADR for edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Edge Case Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Edge Case ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

    @pytest.mark.asyncio
    async def test_update_with_invalid_attribute(self, db_session: AsyncSession, adr_for_edge_cases: Any) -> None:
        """Test update ignores invalid attributes that don't exist on model."""
        repo = ADRRepository(db_session)

        # Update with a mix of valid and invalid keys
        updated = await repo.update(
            adr_for_edge_cases.id,
            expected_version=1,
            title="Updated Title",
            nonexistent_field="should be ignored",
            another_invalid_key=12345,
        )

        # Valid update should work
        assert updated.title == "Updated Title"
        assert updated.version == COUNT_TWO
        # Invalid attributes should be silently ignored
        assert not hasattr(updated, "nonexistent_field")

    @pytest.mark.asyncio
    async def test_update_with_only_invalid_attributes(self, db_session: AsyncSession, adr_for_edge_cases: Any) -> None:
        """Test update with only invalid attributes still increments version."""
        repo = ADRRepository(db_session)

        updated = await repo.update(
            adr_for_edge_cases.id,
            expected_version=1,
            fake_attribute="ignored",
        )

        # Version should still increment even if no actual changes
        assert updated.version == COUNT_TWO
        assert updated.title == "Edge Case ADR"  # Unchanged


class TestContractRepositoryListFilters:
    """Tests for ContractRepository list filters."""

    @pytest_asyncio.fixture
    async def contracts_with_statuses(self, db_session: AsyncSession) -> None:
        """Create contracts with different statuses for filter tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Filter Test")

        item_repo = ItemRepository(db_session)
        items = []
        for i in range(5):
            item = await item_repo.create(
                project_id=project.id,
                title=f"Requirement {i}",
                item_type="requirement",
                view="requirements",
            )
            items.append(item)

        contract_repo = ContractRepository(db_session)
        contracts = []
        statuses = ["draft", "draft", "review", "approved", "archived"]
        for i, (item, status) in enumerate(zip(items, statuses, strict=False)):
            contract = await contract_repo.create(
                project_id=project.id,
                item_id=item.id,
                title=f"Contract {i}",
                contract_type="api",
                status=status,
            )
            contracts.append(contract)

        return {"project": project, "contracts": contracts}

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_status(
        self, db_session: AsyncSession, contracts_with_statuses: Any
    ) -> None:
        """Test listing contracts filtered by status."""
        repo = ContractRepository(db_session)

        # Filter by draft status
        draft_contracts = await repo.list_by_project(contracts_with_statuses["project"].id, status="draft")
        assert len(draft_contracts) == COUNT_TWO

        # Filter by review status
        review_contracts = await repo.list_by_project(contracts_with_statuses["project"].id, status="review")
        assert len(review_contracts) == 1

        # Filter by approved status
        approved_contracts = await repo.list_by_project(contracts_with_statuses["project"].id, status="approved")
        assert len(approved_contracts) == 1

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_type_and_status(
        self, db_session: AsyncSession, contracts_with_statuses: Any
    ) -> None:
        """Test listing contracts with both type and status filters."""
        repo = ContractRepository(db_session)

        # Filter by both type and status
        filtered = await repo.list_by_project(
            contracts_with_statuses["project"].id,
            contract_type="api",
            status="draft",
        )
        assert len(filtered) == COUNT_TWO


class TestContractRepositoryUpdateEdgeCases:
    """Tests for ContractRepository update edge cases."""

    @pytest_asyncio.fixture
    async def contract_for_edge_cases(self, db_session: AsyncSession) -> None:
        """Create contract for edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Edge Case Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        return await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Edge Case Contract",
            contract_type="api",
        )

    @pytest.mark.asyncio
    async def test_update_with_invalid_attribute(self, db_session: AsyncSession, contract_for_edge_cases: Any) -> None:
        """Test update ignores invalid attributes that don't exist on model."""
        repo = ContractRepository(db_session)

        updated = await repo.update(
            contract_for_edge_cases.id,
            expected_version=1,
            title="Updated Contract",
            nonexistent_field="should be ignored",
        )

        assert updated.title == "Updated Contract"
        assert updated.version == COUNT_TWO
        assert not hasattr(updated, "nonexistent_field")


class TestContractRepositoryTransitionEdgeCases:
    """Tests for ContractRepository status transition edge cases."""

    @pytest_asyncio.fixture
    async def contracts_for_transition(self, db_session: AsyncSession) -> None:
        """Create contracts in various states for transition tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Contract Transition Edge Case Test")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Requirement",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)

        # Create a draft contract
        draft = await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Draft Contract",
            contract_type="api",
            status="draft",
        )

        return {"project": project, "item": item, "draft": draft}

    @pytest.mark.asyncio
    async def test_transition_draft_to_deprecated(
        self, db_session: AsyncSession, contracts_for_transition: Any
    ) -> None:
        """Test transitioning from draft directly to deprecated."""
        repo = ContractRepository(db_session)

        updated = await repo.transition_status(contracts_for_transition["draft"].id, "deprecated")

        assert updated.status == "deprecated"

    @pytest.mark.asyncio
    async def test_transition_review_to_draft(self, db_session: AsyncSession, contracts_for_transition: Any) -> None:
        """Test transitioning from review back to draft."""
        repo = ContractRepository(db_session)

        # First transition to review
        await repo.transition_status(contracts_for_transition["draft"].id, "review")

        # Then back to draft
        updated = await repo.transition_status(contracts_for_transition["draft"].id, "draft")

        assert updated.status == "draft"

    @pytest.mark.asyncio
    async def test_transition_deprecated_to_draft(
        self, db_session: AsyncSession, contracts_for_transition: Any
    ) -> None:
        """Test transitioning from deprecated back to draft (revival)."""
        repo = ContractRepository(db_session)

        # First deprecate
        await repo.transition_status(contracts_for_transition["draft"].id, "deprecated")

        # Then revive to draft
        updated = await repo.transition_status(contracts_for_transition["draft"].id, "draft")

        assert updated.status == "draft"


class TestFeatureRepositoryFilters:
    """Tests for FeatureRepository filter edge cases."""

    @pytest_asyncio.fixture
    async def features_setup(self, db_session: AsyncSession) -> None:
        """Create features for filter tests."""
        project_repo = ProjectRepository(db_session)
        project1 = await project_repo.create(name="Feature Filter Project 1")
        project2 = await project_repo.create(name="Feature Filter Project 2")

        feature_repo = FeatureRepository(db_session)

        # Features in project 1 with various statuses
        feature1 = await feature_repo.create(
            project_id=project1.id,
            name="Feature 1",
            status="draft",
        )
        feature2 = await feature_repo.create(
            project_id=project1.id,
            name="Feature 2",
            status="review",
        )
        feature3 = await feature_repo.create(
            project_id=project1.id,
            name="Feature 3",
            status="draft",
        )

        # Feature in project 2
        feature4 = await feature_repo.create(
            project_id=project2.id,
            name="Feature 4",
            status="draft",
        )

        return {
            "project1": project1,
            "project2": project2,
            "features": [feature1, feature2, feature3, feature4],
        }

    @pytest.mark.asyncio
    async def test_get_by_id_with_project_scope(self, db_session: AsyncSession, features_setup: Any) -> None:
        """Test getting feature by ID with project scope."""
        repo = FeatureRepository(db_session)

        # Get feature1 with correct project scope
        feature = await repo.get_by_id(features_setup["features"][0].id, project_id=features_setup["project1"].id)
        assert feature is not None
        assert feature.name == "Feature 1"

        # Try to get feature1 with wrong project scope
        feature_wrong_project = await repo.get_by_id(
            features_setup["features"][0].id,
            project_id=features_setup["project2"].id,
        )
        assert feature_wrong_project is None

    @pytest.mark.asyncio
    async def test_get_by_number_with_project_scope(self, db_session: AsyncSession, features_setup: Any) -> None:
        """Test getting feature by number with project scope."""
        repo = FeatureRepository(db_session)

        feature_number = features_setup["features"][0].feature_number

        # Get with correct project scope
        feature = await repo.get_by_number(feature_number, project_id=features_setup["project1"].id)
        assert feature is not None

        # Get with wrong project scope
        feature_wrong_project = await repo.get_by_number(feature_number, project_id=features_setup["project2"].id)
        assert feature_wrong_project is None

    @pytest.mark.asyncio
    async def test_list_by_project_with_status_filter(self, db_session: AsyncSession, features_setup: Any) -> None:
        """Test listing features filtered by status."""
        repo = FeatureRepository(db_session)

        # Filter by draft status
        draft_features = await repo.list_by_project(features_setup["project1"].id, status="draft")
        assert len(draft_features) == COUNT_TWO

        # Filter by review status
        review_features = await repo.list_by_project(features_setup["project1"].id, status="review")
        assert len(review_features) == 1


class TestFeatureRepositoryUpdateEdgeCases:
    """Tests for FeatureRepository update edge cases."""

    @pytest_asyncio.fixture
    async def feature_for_edge_cases(self, db_session: AsyncSession) -> None:
        """Create feature for edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Edge Case Test")

        feature_repo = FeatureRepository(db_session)
        return await feature_repo.create(
            project_id=project.id,
            name="Edge Case Feature",
        )

    @pytest.mark.asyncio
    async def test_update_with_invalid_attribute(self, db_session: AsyncSession, feature_for_edge_cases: Any) -> None:
        """Test update ignores invalid attributes that don't exist on model."""
        repo = FeatureRepository(db_session)

        updated = await repo.update(
            feature_for_edge_cases.id,
            expected_version=1,
            name="Updated Feature",
            nonexistent_field="should be ignored",
        )

        assert updated.name == "Updated Feature"
        assert updated.version == COUNT_TWO
        assert not hasattr(updated, "nonexistent_field")


class TestScenarioRepositoryFilters:
    """Tests for ScenarioRepository filter edge cases."""

    @pytest_asyncio.fixture
    async def scenarios_for_filters(self, db_session: AsyncSession) -> None:
        """Create scenarios for filter tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Filter Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)

        # Create scenarios with different statuses
        scenarios = []
        for i, status in enumerate(["draft", "draft", "ready", "executing", "passed"]):
            scenario = await scenario_repo.create(
                feature_id=feature.id,
                title=f"Scenario {i}",
                gherkin_text=f"Given scenario {i}",
                status=status,
            )
            scenarios.append(scenario)

        return {"feature": feature, "scenarios": scenarios}

    @pytest.mark.asyncio
    async def test_list_by_feature_with_status_filter(
        self, db_session: AsyncSession, scenarios_for_filters: Any
    ) -> None:
        """Test listing scenarios filtered by status."""
        repo = ScenarioRepository(db_session)

        # Filter by draft status
        draft_scenarios = await repo.list_by_feature(scenarios_for_filters["feature"].id, status="draft")
        assert len(draft_scenarios) == COUNT_TWO

        # Filter by ready status
        ready_scenarios = await repo.list_by_feature(scenarios_for_filters["feature"].id, status="ready")
        assert len(ready_scenarios) == 1

        # Filter by executing status
        executing_scenarios = await repo.list_by_feature(scenarios_for_filters["feature"].id, status="executing")
        assert len(executing_scenarios) == 1


class TestScenarioRepositoryUpdateEdgeCases:
    """Tests for ScenarioRepository update edge cases."""

    @pytest_asyncio.fixture
    async def scenario_for_edge_cases(self, db_session: AsyncSession) -> None:
        """Create scenario for edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Edge Case Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Edge Case Scenario",
            gherkin_text="Given edge case",
        )

    @pytest.mark.asyncio
    async def test_update_with_invalid_attribute(self, db_session: AsyncSession, scenario_for_edge_cases: Any) -> None:
        """Test update ignores invalid attributes that don't exist on model."""
        repo = ScenarioRepository(db_session)

        updated = await repo.update(
            scenario_for_edge_cases.id,
            expected_version=1,
            title="Updated Scenario",
            nonexistent_field="should be ignored",
        )

        assert updated.title == "Updated Scenario"
        assert updated.version == COUNT_TWO
        assert not hasattr(updated, "nonexistent_field")

    @pytest.mark.asyncio
    async def test_update_gherkin_steps(self, db_session: AsyncSession, scenario_for_edge_cases: Any) -> None:
        """Test updating scenario with new Gherkin steps."""
        repo = ScenarioRepository(db_session)

        new_given = [{"text": "a new precondition", "keyword": "Given"}]
        new_when = [{"text": "an action occurs", "keyword": "When"}]
        new_then = [{"text": "a result happens", "keyword": "Then"}]

        updated = await repo.update(
            scenario_for_edge_cases.id,
            expected_version=1,
            given_steps=new_given,
            when_steps=new_when,
            then_steps=new_then,
        )

        assert updated.given_steps == new_given
        assert updated.when_steps == new_when
        assert updated.then_steps == new_then
        assert updated.version == COUNT_TWO


class TestScenarioRepositoryTransitionEdgeCases:
    """Tests for ScenarioRepository status transition edge cases."""

    @pytest_asyncio.fixture
    async def scenario_for_transition(self, db_session: AsyncSession) -> None:
        """Create scenario for transition edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Scenario Transition Edge Case Test")

        feature_repo = FeatureRepository(db_session)
        feature = await feature_repo.create(
            project_id=project.id,
            name="Test Feature",
        )

        scenario_repo = ScenarioRepository(db_session)
        return await scenario_repo.create(
            feature_id=feature.id,
            title="Transition Edge Case Scenario",
            gherkin_text="Given transition test",
            status="draft",
        )

    @pytest.mark.asyncio
    async def test_transition_draft_to_review(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from draft to review."""
        repo = ScenarioRepository(db_session)

        updated = await repo.transition_status(scenario_for_transition.id, "review")

        assert updated.status == "review"

    @pytest.mark.asyncio
    async def test_transition_review_to_draft(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from review back to draft."""
        repo = ScenarioRepository(db_session)

        # First transition to review
        await repo.transition_status(scenario_for_transition.id, "review")

        # Then back to draft
        updated = await repo.transition_status(scenario_for_transition.id, "draft")

        assert updated.status == "draft"

    @pytest.mark.asyncio
    async def test_transition_review_to_ready(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from review to ready."""
        repo = ScenarioRepository(db_session)

        # First transition to review
        await repo.transition_status(scenario_for_transition.id, "review")

        # Then to ready
        updated = await repo.transition_status(scenario_for_transition.id, "ready")

        assert updated.status == "ready"

    @pytest.mark.asyncio
    async def test_transition_passed_to_executing_retest(
        self, db_session: AsyncSession, scenario_for_transition: Any
    ) -> None:
        """Test transitioning scenario from passed back to executing (retest)."""
        repo = ScenarioRepository(db_session)

        # Go through full lifecycle
        await repo.transition_status(scenario_for_transition.id, "ready")
        await repo.transition_status(scenario_for_transition.id, "executing")
        await repo.transition_status(scenario_for_transition.id, "passed")

        # Retest: back to executing
        updated = await repo.transition_status(scenario_for_transition.id, "executing")

        assert updated.status == "executing"

    @pytest.mark.asyncio
    async def test_transition_ready_to_executing(self, db_session: AsyncSession, scenario_for_transition: Any) -> None:
        """Test transitioning scenario from ready to executing."""
        repo = ScenarioRepository(db_session)

        await repo.transition_status(scenario_for_transition.id, "ready")
        updated = await repo.transition_status(scenario_for_transition.id, "executing")

        assert updated.status == "executing"

    @pytest.mark.asyncio
    async def test_transition_deprecated_is_terminal(
        self, db_session: AsyncSession, scenario_for_transition: Any
    ) -> None:
        """Test that deprecated is a terminal state."""
        repo = ScenarioRepository(db_session)

        # Deprecate from draft
        await repo.transition_status(scenario_for_transition.id, "deprecated")

        # Try to transition from deprecated (should fail)
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(scenario_for_transition.id, "draft")


class TestFeatureRepositoryTransitionEdgeCases:
    """Tests for FeatureRepository status transition edge cases."""

    @pytest_asyncio.fixture
    async def feature_for_transition(self, db_session: AsyncSession) -> None:
        """Create feature for transition edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Feature Transition Edge Case Test")

        feature_repo = FeatureRepository(db_session)
        return await feature_repo.create(
            project_id=project.id,
            name="Transition Edge Case Feature",
            status="draft",
        )

    @pytest.mark.asyncio
    async def test_transition_draft_to_deprecated(self, db_session: AsyncSession, feature_for_transition: Any) -> None:
        """Test transitioning feature from draft directly to deprecated."""
        repo = FeatureRepository(db_session)

        updated = await repo.transition_status(feature_for_transition.id, "deprecated")

        assert updated.status == "deprecated"

    @pytest.mark.asyncio
    async def test_transition_review_to_draft(self, db_session: AsyncSession, feature_for_transition: Any) -> None:
        """Test transitioning feature from review back to draft."""
        repo = FeatureRepository(db_session)

        await repo.transition_status(feature_for_transition.id, "review")
        updated = await repo.transition_status(feature_for_transition.id, "draft")

        assert updated.status == "draft"

    @pytest.mark.asyncio
    async def test_transition_implemented_to_deprecated(
        self, db_session: AsyncSession, feature_for_transition: Any
    ) -> None:
        """Test transitioning feature from implemented to deprecated."""
        repo = FeatureRepository(db_session)

        # Go through lifecycle
        await repo.transition_status(feature_for_transition.id, "review")
        await repo.transition_status(feature_for_transition.id, "approved")
        await repo.transition_status(feature_for_transition.id, "implemented")

        # Deprecate
        updated = await repo.transition_status(feature_for_transition.id, "deprecated")

        assert updated.status == "deprecated"

    @pytest.mark.asyncio
    async def test_transition_deprecated_is_terminal(
        self, db_session: AsyncSession, feature_for_transition: Any
    ) -> None:
        """Test that deprecated is a terminal state for features."""
        repo = FeatureRepository(db_session)

        await repo.transition_status(feature_for_transition.id, "deprecated")

        # Try to transition from deprecated (should fail)
        with pytest.raises(ValueError, match="Invalid status transition"):
            await repo.transition_status(feature_for_transition.id, "draft")


class TestContractRepositoryProjectScope:
    """Tests for ContractRepository project scope filters."""

    @pytest_asyncio.fixture
    async def contracts_multi_project(self, db_session: AsyncSession) -> None:
        """Create contracts in multiple projects for scope tests."""
        project_repo = ProjectRepository(db_session)
        project1 = await project_repo.create(name="Contract Scope Project 1")
        project2 = await project_repo.create(name="Contract Scope Project 2")

        item_repo = ItemRepository(db_session)
        item1 = await item_repo.create(
            project_id=project1.id,
            title="Requirement 1",
            item_type="requirement",
            view="requirements",
        )
        item2 = await item_repo.create(
            project_id=project2.id,
            title="Requirement 2",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        contract1 = await contract_repo.create(
            project_id=project1.id,
            item_id=item1.id,
            title="Contract in Project 1",
            contract_type="api",
        )
        contract2 = await contract_repo.create(
            project_id=project2.id,
            item_id=item2.id,
            title="Contract in Project 2",
            contract_type="api",
        )

        return {
            "project1": project1,
            "project2": project2,
            "contract1": contract1,
            "contract2": contract2,
        }

    @pytest.mark.asyncio
    async def test_get_by_id_with_project_scope(self, db_session: AsyncSession, contracts_multi_project: Any) -> None:
        """Test getting contract by ID with project scope."""
        repo = ContractRepository(db_session)

        # Get contract1 with correct project scope
        contract = await repo.get_by_id(
            contracts_multi_project["contract1"].id,
            project_id=contracts_multi_project["project1"].id,
        )
        assert contract is not None
        assert contract.title == "Contract in Project 1"

        # Try to get contract1 with wrong project scope
        contract_wrong = await repo.get_by_id(
            contracts_multi_project["contract1"].id,
            project_id=contracts_multi_project["project2"].id,
        )
        assert contract_wrong is None

    @pytest.mark.asyncio
    async def test_get_by_number_with_project_scope(
        self, db_session: AsyncSession, contracts_multi_project: Any
    ) -> None:
        """Test getting contract by number with project scope."""
        repo = ContractRepository(db_session)

        contract_number = contracts_multi_project["contract1"].contract_number

        # Get with correct project scope
        contract = await repo.get_by_number(contract_number, project_id=contracts_multi_project["project1"].id)
        assert contract is not None
        assert contract.title == "Contract in Project 1"

        # Get with wrong project scope
        contract_wrong = await repo.get_by_number(contract_number, project_id=contracts_multi_project["project2"].id)
        assert contract_wrong is None


# ============================================================================
# ADDITIONAL TESTS FOR 100% COVERAGE
# ============================================================================


class TestADRVerifyComplianceExplicitTime:
    """Additional tests for ADRRepository.verify_compliance with explicit verified_at."""

    @pytest_asyncio.fixture
    async def adr_for_verify(self, db_session: AsyncSession) -> None:
        """Create ADR for verification tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Verify Time Test Project")

        adr_repo = ADRRepository(db_session)
        return await adr_repo.create(
            project_id=project.id,
            title="Verify Test ADR",
            context="Context",
            decision="Decision",
            consequences="Consequences",
        )

    @pytest.mark.asyncio
    async def test_verify_compliance_with_explicit_verified_at(
        self, db_session: AsyncSession, adr_for_verify: Any
    ) -> None:
        """Test verify_compliance with explicit verified_at to cover lines 220-225."""
        repo = ADRRepository(db_session)

        # Use explicit verified_at timestamp
        explicit_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        updated = await repo.verify_compliance(adr_for_verify.id, compliance_score=0.92, verified_at=explicit_time)

        # Lines 220-225 should be covered
        assert updated.compliance_score == 0.92
        assert updated.last_verified_at == explicit_time
        assert updated.version == COUNT_TWO


class TestContractVerifyMethod:
    """Additional tests for ContractRepository.verify method."""

    @pytest_asyncio.fixture
    async def contract_for_verify(self, db_session: AsyncSession) -> None:
        """Create contract for verification tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Verify Contract Project")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=project.id,
            title="Test Item",
            item_type="requirement",
            view="requirements",
        )

        contract_repo = ContractRepository(db_session)
        return await contract_repo.create(
            project_id=project.id,
            item_id=item.id,
            title="Test Contract",
            contract_type="api",
        )

    @pytest.mark.asyncio
    async def test_verify_contract_success(self, db_session: AsyncSession, contract_for_verify: Any) -> None:
        """Test contract verification to cover lines 398-401."""
        repo = ContractRepository(db_session)

        verification_result = {"verified": True, "proofs": ["proof1", "proof2"], "coverage": 95.5}

        # This covers lines 398-401
        updated = await repo.verify(contract_for_verify.id, verification_result=verification_result)

        assert updated.last_verified_at is not None
        assert updated.verification_result == verification_result
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_verify_contract_not_found(self, db_session: AsyncSession) -> None:
        """Test contract verification with non-existent contract to cover line 396."""
        repo = ContractRepository(db_session)

        # This covers lines 395-396
        with pytest.raises(ValueError, match=r"Contract .* not found"):
            await repo.verify(str(uuid4()), verification_result={"verified": False})
