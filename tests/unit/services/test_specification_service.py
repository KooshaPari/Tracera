"""Unit tests for specification services.

Functional Requirements Coverage:
    - FR-DISC-002: Specification Parsing

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify ADR, Contract, Feature, Scenario, and Step Definition services
for parsing and managing structured specifications in TraceRTM.
"""

from typing import Any

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.adr import ADR
from tracertm.models.contract import Contract
from tracertm.models.feature import Feature
from tracertm.models.scenario import Scenario
from tracertm.services.specification_service import (
    ADRService,
    ContractService,
    FeatureService,
    ScenarioService,
    StepDefinitionService,
)


class TestADRService:
    """Test ADRService."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create ADRService instance."""
        return ADRService(mock_session)

    @pytest.mark.asyncio
    async def test_create_adr(self, service: Any, mock_session: Any) -> None:
        """Test creating an ADR.

        Tests: FR-DISC-002
        """
        # Setup
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        adr = await service.create(
            project_id="proj-1",
            title="Use async/await for async operations",
            context="Need async handling for IO operations",
            decision="Use Python async/await pattern",
            consequences="Requires asyncio knowledge from team",
            status="proposed",
            decision_drivers=["Performance", "Code clarity"],
            stakeholders=["Backend team"],
        )

        # Assert
        assert adr.project_id == "proj-1"
        assert adr.title == "Use async/await for async operations"
        assert adr.adr_number == "ADR-0001"
        assert adr.status == "proposed"
        assert adr.version == 1
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_adr(self, service: Any, mock_session: Any) -> None:
        """Test getting an ADR by ID."""
        # Setup
        mock_adr = ADR(
            id="adr-1",
            project_id="proj-1",
            title="Test ADR",
            adr_number="ADR-0001",
            status="proposed",
            context="Test context",
            decision="Test decision",
            consequences="Test consequences",
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_adr

        # Execute
        result = await service.get("adr-1")

        # Assert
        assert result == mock_adr
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_adr_by_project(self, service: Any, mock_session: Any) -> None:
        """Test listing ADRs for a project."""
        # Setup
        mock_adr1 = ADR(
            id="adr-1",
            project_id="proj-1",
            title="ADR 1",
            adr_number="ADR-0001",
            status="proposed",
            context="ctx",
            decision="dec",
            consequences="cons",
        )
        mock_adr2 = ADR(
            id="adr-2",
            project_id="proj-1",
            title="ADR 2",
            adr_number="ADR-0002",
            status="accepted",
            context="ctx",
            decision="dec",
            consequences="cons",
        )

        # Mock count query
        mock_session.execute.side_effect = [
            MagicMock(scalar=MagicMock(return_value=2)),  # count query
            MagicMock(
                scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_adr1, mock_adr2]))),
            ),  # list query
        ]

        # Execute
        results, total = await service.list_by_project("proj-1", status="proposed")

        # Assert
        assert total == COUNT_TWO
        assert len(results) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_adr(self, service: Any, mock_session: Any) -> None:
        """Test updating an ADR."""
        # Setup
        mock_adr = ADR(
            id="adr-1",
            project_id="proj-1",
            title="Old title",
            adr_number="ADR-0001",
            status="proposed",
            context="ctx",
            decision="dec",
            consequences="cons",
            version=1,
        )
        service.get = AsyncMock(return_value=mock_adr)

        # Execute
        updated = await service.update("adr-1", title="New title", status="accepted")

        # Assert
        assert updated.title == "New title"
        assert updated.status == "accepted"
        assert updated.version == COUNT_TWO
        mock_session.add.assert_called()

    @pytest.mark.asyncio
    async def test_delete_adr(self, service: Any, mock_session: Any) -> None:
        """Test deleting an ADR."""
        # Setup
        mock_session.execute.return_value.rowcount = 1

        # Execute
        result = await service.delete("adr-1")

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_compliance(self, service: Any, _mock_session: Any) -> None:
        """Test verifying ADR compliance."""
        # Setup
        mock_adr = ADR(
            id="adr-1",
            project_id="proj-1",
            title="Test ADR",
            adr_number="ADR-0001",
            status="proposed",
            context="ctx",
            decision="dec",
            consequences="cons",
            compliance_score=0.0,
            version=1,
        )
        service.get = AsyncMock(return_value=mock_adr)

        # Execute
        result = await service.verify_compliance("adr-1", 0.85)

        # Assert
        assert result.compliance_score == 0.85
        assert result.version == COUNT_TWO
        assert result.last_verified_at is not None

    @pytest.mark.asyncio
    async def test_link_requirements(self, service: Any, _mock_session: Any) -> None:
        """Test linking requirements to ADR."""
        # Setup
        mock_adr = ADR(
            id="adr-1",
            project_id="proj-1",
            title="Test ADR",
            adr_number="ADR-0001",
            status="proposed",
            context="ctx",
            decision="dec",
            consequences="cons",
            related_requirements=["REQ-001"],
            version=1,
        )
        service.get = AsyncMock(return_value=mock_adr)

        # Execute
        result = await service.link_requirements("adr-1", ["REQ-002", "REQ-003"])

        # Assert
        assert "REQ-001" in result.related_requirements
        assert "REQ-002" in result.related_requirements
        assert "REQ-003" in result.related_requirements

    @pytest.mark.asyncio
    async def test_supersede(self, service: Any, _mock_session: Any) -> None:
        """Test marking ADR as superseded."""
        # Setup
        mock_adr = ADR(
            id="adr-1",
            project_id="proj-1",
            title="Old ADR",
            adr_number="ADR-0001",
            status="proposed",
            context="ctx",
            decision="dec",
            consequences="cons",
            version=1,
        )
        service.get = AsyncMock(return_value=mock_adr)

        # Execute
        result = await service.supersede("adr-1", "ADR-0005")

        # Assert
        assert result.superseded_by == "ADR-0005"
        assert result.status == "superseded"


class TestContractService:
    """Test ContractService."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create ContractService instance."""
        return ContractService(mock_session)

    @pytest.mark.asyncio
    async def test_create_contract(self, service: Any, mock_session: Any) -> None:
        """Test creating a Contract."""
        # Setup
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        contract = await service.create(
            project_id="proj-1",
            item_id="item-1",
            title="API Contract",
            contract_type="api",
            preconditions=[{"name": "auth_token", "type": "string"}],
            postconditions=[{"name": "response", "type": "json"}],
        )

        # Assert
        assert contract.project_id == "proj-1"
        assert contract.item_id == "item-1"
        assert contract.contract_type == "api"
        assert contract.contract_number == "CONTRACT-0001"
        assert contract.status == "draft"
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_contract(self, service: Any, _mock_session: Any) -> None:
        """Test verifying a contract."""
        # Setup
        mock_contract = Contract(
            id="contract-1",
            project_id="proj-1",
            item_id="item-1",
            title="API Contract",
            contract_type="api",
            contract_number="CONTRACT-0001",
            status="draft",
            version=1,
        )
        service.get = AsyncMock(return_value=mock_contract)

        # Execute
        verification_result = {"status": "passed", "checks": 10, "passed": 10}
        result = await service.verify("contract-1", verification_result)

        # Assert
        assert result.verification_result == verification_result
        assert result.last_verified_at is not None
        assert result.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_execute_transition(self, service: Any, _mock_session: Any) -> None:
        """Test executing state transition."""
        # Setup
        mock_contract = Contract(
            id="contract-1",
            project_id="proj-1",
            item_id="item-1",
            title="State Machine",
            contract_type="state_machine",
            contract_number="CONTRACT-0001",
            status="draft",
            states=["INIT", "READY", "RUNNING", "DONE"],
            transitions=[
                {"from": "INIT", "to": "READY"},
                {"from": "READY", "to": "RUNNING"},
                {"from": "RUNNING", "to": "DONE"},
            ],
            version=1,
        )
        service.get = AsyncMock(return_value=mock_contract)

        # Execute
        result = await service.execute_transition("contract-1", "INIT", "READY")

        # Assert
        assert result is not None
        assert result.metadata_.get("current_state") == "READY"


class TestFeatureService:
    """Test FeatureService."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create FeatureService instance."""
        return FeatureService(mock_session)

    @pytest.mark.asyncio
    async def test_create_feature(self, service: Any, mock_session: Any) -> None:
        """Test creating a Feature."""
        # Setup
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Execute
        feature = await service.create(
            project_id="proj-1",
            name="User authentication",
            as_a="User",
            i_want="to login with email",
            so_that="I can access the application",
            tags=["auth", "security"],
        )

        # Assert
        assert feature.project_id == "proj-1"
        assert feature.name == "User authentication"
        assert feature.feature_number == "FEAT-0001"
        assert feature.status == "draft"
        assert feature.as_a == "User"

    @pytest.mark.asyncio
    async def test_get_feature(self, service: Any, mock_session: Any) -> None:
        """Test getting a Feature by ID."""
        # Setup
        mock_feature = Feature(
            id="feat-1",
            project_id="proj-1",
            name="Test Feature",
            feature_number="FEAT-0001",
            status="draft",
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_feature

        # Execute
        result = await service.get("feat-1")

        # Assert
        assert result == mock_feature

    @pytest.mark.asyncio
    async def test_calculate_pass_rate(self, service: Any, mock_session: Any) -> None:
        """Test calculating feature pass rate from scenarios."""
        # Setup
        mock_session.execute.return_value.scalar.return_value = 0.75

        # Execute
        pass_rate = await service.calculate_pass_rate("feat-1")

        # Assert
        assert pass_rate == 0.75


class TestScenarioService:
    """Test ScenarioService."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create ScenarioService instance."""
        return ScenarioService(mock_session)

    @pytest.mark.asyncio
    async def test_create_scenario(self, service: Any, mock_session: Any) -> None:
        """Test creating a Scenario."""
        # Setup
        mock_feature = Feature(
            id="feat-1",
            project_id="proj-1",
            name="Test Feature",
            feature_number="FEAT-0001",
            status="draft",
        )
        mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=mock_feature)),  # Feature lookup
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # Last scenario lookup
        ]

        # Execute
        scenario = await service.create(
            feature_id="feat-1",
            title="User login with valid credentials",
            gherkin_text="Given user is on login page\nWhen user enters credentials\nThen user is logged in",
            given_steps=[{"text": "user is on login page", "status": "pending"}],
            when_steps=[{"text": "user enters credentials", "status": "pending"}],
            then_steps=[{"text": "user is logged in", "status": "pending"}],
        )

        # Assert
        assert scenario.feature_id == "feat-1"
        assert scenario.title == "User login with valid credentials"
        assert scenario.scenario_number == "FEAT-0001-SC-001"
        assert scenario.status == "draft"
        assert scenario.pass_rate == 0.0

    @pytest.mark.asyncio
    async def test_run_scenario(self, service: Any, _mock_session: Any) -> None:
        """Test running a scenario."""
        # Setup
        mock_scenario = Scenario(
            id="scenario-1",
            feature_id="feat-1",
            title="Test Scenario",
            scenario_number="FEAT-0001-SC-001",
            gherkin_text="Given ... When ... Then ...",
            given_steps=[{"text": "step1"}],
            when_steps=[{"text": "step2"}],
            then_steps=[{"text": "step3"}],
            status="draft",
            pass_rate=0.0,
            version=1,
        )
        service.get = AsyncMock(return_value=mock_scenario)

        # Execute
        results = {"passed_steps": 3, "failed_steps": 0}
        result = await service.run("scenario-1", results)

        # Assert
        assert result.pass_rate == 1.0
        assert result.status == "executed"
        assert result.metadata_.get("last_run") == results

    @pytest.mark.asyncio
    async def test_update_pass_rate(self, service: Any, _mock_session: Any) -> None:
        """Test updating scenario pass rate."""
        # Setup
        mock_scenario = Scenario(
            id="scenario-1",
            feature_id="feat-1",
            title="Test Scenario",
            scenario_number="FEAT-0001-SC-001",
            gherkin_text="Given ... When ... Then ...",
            pass_rate=0.5,
            version=1,
        )
        service.get = AsyncMock(return_value=mock_scenario)

        # Execute
        result = await service.update_pass_rate("scenario-1", 0.85)

        # Assert
        assert result.pass_rate == 0.85
        assert result.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_link_test_cases(self, service: Any, _mock_session: Any) -> None:
        """Test linking test cases to scenario."""
        # Setup
        mock_scenario = Scenario(
            id="scenario-1",
            feature_id="feat-1",
            title="Test Scenario",
            scenario_number="FEAT-0001-SC-001",
            gherkin_text="Given ... When ... Then ...",
            test_case_ids=["TC-001"],
            version=1,
        )
        service.get = AsyncMock(return_value=mock_scenario)

        # Execute
        result = await service.link_test_cases("scenario-1", ["TC-002", "TC-003"])

        # Assert
        assert "TC-001" in result.test_case_ids
        assert "TC-002" in result.test_case_ids
        assert "TC-003" in result.test_case_ids


class TestStepDefinitionService:
    """Test StepDefinitionService."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create StepDefinitionService instance."""
        return StepDefinitionService(mock_session)

    @pytest.mark.asyncio
    async def test_create_step_definition(self, service: Any, _mock_session: Any) -> None:
        """Test creating a Step Definition."""
        # Execute
        step = await service.create(
            project_id="proj-1",
            step_pattern=r"^user is on (.+) page$",
            step_type="given",
            implementation_code="def step_user_on_page(context, page): pass",
            language="python",
            description="User navigates to a page",
            parameters=[{"name": "page", "type": "string"}],
        )

        # Assert
        assert step["project_id"] == "proj-1"
        assert step["step_pattern"] == r"^user is on (.+) page$"
        assert step["step_type"] == "given"
        assert step["language"] == "python"
        assert step["usage_count"] == 0
        assert step["version"] == 1

    @pytest.mark.asyncio
    async def test_find_matching_steps(self, service: Any, _mock_session: Any) -> None:
        """Test finding matching step definitions."""
        # Execute
        results = await service.find_matching(
            project_id="proj-1",
            step_text="user is on login page",
            step_type="given",
        )

        # Assert
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_step(self, service: Any, _mock_session: Any) -> None:
        """Test getting a Step Definition."""
        # Execute
        result = await service.get("step-1")

        # Assert
        assert result is None  # Placeholder implementation

    @pytest.mark.asyncio
    async def test_list_steps_by_project(self, service: Any, _mock_session: Any) -> None:
        """Test listing step definitions for a project."""
        # Execute
        steps, total = await service.list_by_project("proj-1")

        # Assert
        assert steps == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_increment_usage(self, service: Any, _mock_session: Any) -> None:
        """Test incrementing step usage count."""
        # Execute
        result = await service.increment_usage("step-1")

        # Assert
        assert result is None  # Placeholder implementation
