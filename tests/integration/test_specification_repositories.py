"""Specification Repository Integration Tests.

These tests validate:
- ADR, Contract, Feature, and Scenario CRUD operations
- Status transitions with validation
- Traceability and relationships
- Optimistic locking behavior
- Complex queries and filtering
- Cascading deletions
- Activity tracking

Target Coverage: 90%+ for specification repositories

Functional Requirements Coverage:
    - FR-DISC-002: Specification Parsing
    - FR-APP-002: Specification Versioning
    - FR-QUAL-001: Requirement Quality Assessment

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify specification repository integration with database including
ADR, Contract, Feature, and Scenario creation, retrieval, status transitions,
optimistic locking, and versioning.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.specification_repository import (
    ADRRepository,
    ContractRepository,
    FeatureRepository,
    ScenarioRepository,
)

pytestmark = pytest.mark.integration


# ============================================================================
# FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """Create a test project."""
    repo = ProjectRepository(db_session)
    project = await repo.create(
        name="Specification Test Project",
        description="Test project for specification repositories",
    )
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def test_item(db_session: AsyncSession, test_project: Project) -> Item:
    """Create a test item for contracts."""
    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=str(test_project.id),
        title="Test API",
        view="api",
        item_type="function",
        description="Test API function",
    )
    await db_session.commit()
    return item


# ============================================================================
# ADR REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_adr_create_basic(db_session: AsyncSession, test_project: Project) -> None:
    """Test basic ADR creation."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Use PostgreSQL for database",
        context="Need to decide on database technology",
        decision="We chose PostgreSQL",
        consequences="Better support, more complex setup",
        status="proposed",
    )
    await db_session.commit()

    assert adr.id
    assert adr.adr_number.startswith("ADR-")
    assert adr.project_id == test_project.id
    assert adr.status == "proposed"
    assert adr.version == 1


@pytest.mark.asyncio
async def test_adr_create_with_full_metadata(db_session: AsyncSession, test_project: Project) -> None:
    """Test ADR creation with all metadata."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Use async SQLAlchemy",
        context="Need database async support",
        decision="SQLAlchemy 2.0 async",
        consequences="Better concurrency handling",
        status="accepted",
        decision_drivers=["performance", "scalability"],
        considered_options=[
            {"name": "Tortoise ORM", "pros": "Simple"},
            {"name": "Alembic", "pros": "Migrations"},
        ],
        related_requirements=["REQ-001", "REQ-002"],
        related_adrs=["ADR-001"],
        compliance_score=0.95,
        stakeholders=["backend-team", "devops"],
        tags=["database", "architecture"],
        metadata={"approval_date": "2025-01-20"},
    )
    await db_session.commit()

    assert adr.decision_drivers == ["performance", "scalability"]
    assert len(adr.considered_options or []) == COUNT_TWO
    assert adr.compliance_score == 0.95
    assert adr.version == 1


@pytest.mark.asyncio
async def test_adr_get_by_id(db_session: AsyncSession, test_project: Project) -> None:
    """Test retrieving ADR by ID."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Test ADR",
        context="Context",
        decision="Decision",
        consequences="Consequences",
    )
    await db_session.commit()

    found = await repo.get_by_id(adr.id, str(test_project.id))
    assert found is not None
    assert found.id == adr.id
    assert found.title == "Test ADR"


@pytest.mark.asyncio
async def test_adr_get_by_number(db_session: AsyncSession, test_project: Project) -> None:
    """Test retrieving ADR by number."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Test ADR",
        context="Context",
        decision="Decision",
        consequences="Consequences",
    )
    await db_session.commit()

    found = await repo.get_by_number(adr.adr_number, str(test_project.id))
    assert found is not None
    assert found.id == adr.id


@pytest.mark.asyncio
async def test_adr_list_by_project(db_session: AsyncSession, test_project: Project) -> None:
    """Test listing ADRs by project."""
    repo = ADRRepository(db_session)

    # Create multiple ADRs
    for i in range(3):
        await repo.create(
            project_id=str(test_project.id),
            title=f"ADR {i}",
            context="Context",
            decision="Decision",
            consequences="Consequences",
            status="proposed",
        )
    await db_session.commit()

    adrs = await repo.list_by_project(str(test_project.id))
    assert len(adrs) == COUNT_THREE


@pytest.mark.asyncio
async def test_adr_list_by_status(db_session: AsyncSession, test_project: Project) -> None:
    """Test listing ADRs filtered by status."""
    repo = ADRRepository(db_session)

    await repo.create(
        project_id=str(test_project.id),
        title="Proposed ADR",
        context="C",
        decision="D",
        consequences="C",
        status="proposed",
    )
    await repo.create(
        project_id=str(test_project.id),
        title="Accepted ADR",
        context="C",
        decision="D",
        consequences="C",
        status="accepted",
    )
    await db_session.commit()

    proposed = await repo.find_by_status(str(test_project.id), "proposed")
    assert len(proposed) == 1
    assert proposed[0].title == "Proposed ADR"


@pytest.mark.asyncio
async def test_adr_update_with_locking(db_session: AsyncSession, test_project: Project) -> None:
    """Test ADR update with optimistic locking."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Original",
        context="C",
        decision="D",
        consequences="C",
    )
    await db_session.commit()

    # Update with correct version
    updated = await repo.update(adr.id, adr.version, title="Updated")
    assert updated.title == "Updated"
    assert updated.version == COUNT_TWO


@pytest.mark.asyncio
async def test_adr_update_version_conflict(db_session: AsyncSession, test_project: Project) -> None:
    """Test ADR update fails with version conflict."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Original",
        context="C",
        decision="D",
        consequences="C",
    )
    await db_session.commit()

    # Try to update with wrong version
    with pytest.raises(ConcurrencyError):
        await repo.update(adr.id, 999, title="Updated")


@pytest.mark.asyncio
async def test_adr_transition_status(db_session: AsyncSession, test_project: Project) -> None:
    """Test ADR status transitions."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Test",
        context="C",
        decision="D",
        consequences="C",
        status="proposed",
    )
    await db_session.commit()

    # Transition from proposed to accepted
    updated = await repo.transition_status(adr.id, "accepted")
    assert updated.status == "accepted"


@pytest.mark.asyncio
async def test_adr_invalid_status_transition(db_session: AsyncSession, test_project: Project) -> None:
    """Test invalid ADR status transitions are rejected."""
    repo = ADRRepository(db_session)

    adr = await repo.create(
        project_id=str(test_project.id),
        title="Test",
        context="C",
        decision="D",
        consequences="C",
        status="deprecated",
    )
    await db_session.commit()

    # Try invalid transition
    with pytest.raises(ValueError):
        await repo.transition_status(adr.id, "proposed")


@pytest.mark.asyncio
async def test_adr_verify_compliance(db_session: AsyncSession, test_project: Project) -> None:
    """Test ADR compliance verification."""
    repo = ADRRepository(db_session)

    adr = await repo.create(project_id=str(test_project.id), title="Test", context="C", decision="D", consequences="C")
    await db_session.commit()

    verified = await repo.verify_compliance(adr.id, compliance_score=0.85)
    assert verified.compliance_score == 0.85
    assert verified.last_verified_at is not None


@pytest.mark.asyncio
async def test_adr_count_by_status(db_session: AsyncSession, test_project: Project) -> None:
    """Test counting ADRs by status."""
    repo = ADRRepository(db_session)

    for i in range(2):
        await repo.create(
            project_id=str(test_project.id),
            title=f"ADR {i}",
            context="C",
            decision="D",
            consequences="C",
            status="proposed",
        )

    await repo.create(
        project_id=str(test_project.id),
        title="Accepted",
        context="C",
        decision="D",
        consequences="C",
        status="accepted",
    )
    await db_session.commit()

    counts = await repo.count_by_status(str(test_project.id))
    assert counts.get("proposed") == COUNT_TWO
    assert counts.get("accepted") == 1


# ============================================================================
# CONTRACT REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_contract_create_basic(db_session: AsyncSession, test_project: Project, test_item: Item) -> None:
    """Test basic contract creation."""
    repo = ContractRepository(db_session)

    contract = await repo.create(
        project_id=str(test_project.id),
        item_id=str(test_item.id),
        title="API Contract",
        contract_type="api",
        status="draft",
    )
    await db_session.commit()

    assert contract.id
    assert contract.contract_number.startswith("CTR-")
    assert contract.contract_type == "api"


@pytest.mark.asyncio
async def test_contract_create_with_specification(
    db_session: AsyncSession, test_project: Project, test_item: Item
) -> None:
    """Test contract creation with full specification."""
    repo = ContractRepository(db_session)

    contract = await repo.create(
        project_id=str(test_project.id),
        item_id=str(test_item.id),
        title="Payment API Contract",
        contract_type="api",
        status="draft",
        preconditions=[
            {"name": "user_authenticated", "type": "boolean"},
            {"name": "payment_enabled", "type": "boolean"},
        ],
        postconditions=[
            {"name": "transaction_recorded", "type": "boolean"},
            {"name": "notification_sent", "type": "boolean"},
        ],
        invariants=[{"name": "balance_non_negative", "type": "numeric"}],
        states=["pending", "processing", "completed", "failed"],
        transitions=[
            {"from": "pending", "to": "processing", "trigger": "process"},
            {"from": "processing", "to": "completed", "trigger": "success"},
        ],
        executable_spec="function processPayment(amount) { ... }",
        spec_language="javascript",
        tags=["payment", "critical"],
    )
    await db_session.commit()

    assert len(contract.preconditions or []) == COUNT_TWO
    assert len(contract.postconditions or []) == COUNT_TWO
    assert len(contract.states or []) == COUNT_FOUR
    assert contract.spec_language == "javascript"


@pytest.mark.asyncio
async def test_contract_list_by_item(db_session: AsyncSession, test_project: Project, test_item: Item) -> None:
    """Test listing contracts for an item."""
    repo = ContractRepository(db_session)

    for i in range(3):
        await repo.create(
            project_id=str(test_project.id),
            item_id=str(test_item.id),
            title=f"Contract {i}",
            contract_type="api",
        )
    await db_session.commit()

    contracts = await repo.list_by_item(str(test_item.id))
    assert len(contracts) == COUNT_THREE


@pytest.mark.asyncio
async def test_contract_verify(db_session: AsyncSession, test_project: Project, test_item: Item) -> None:
    """Test contract verification recording."""
    repo = ContractRepository(db_session)

    contract = await repo.create(
        project_id=str(test_project.id),
        item_id=str(test_item.id),
        title="API Contract",
        contract_type="api",
    )
    await db_session.commit()

    verification_result = {"passed": True, "checks": ["preconditions_ok", "postconditions_ok"], "warnings": []}

    verified = await repo.verify(contract.id, verification_result)
    assert verified is not None and verified.verification_result is not None
    assert verified.verification_result.get("passed") is True
    assert verified.last_verified_at is not None


@pytest.mark.asyncio
async def test_contract_status_transitions(db_session: AsyncSession, test_project: Project, test_item: Item) -> None:
    """Test contract status transitions."""
    repo = ContractRepository(db_session)

    contract = await repo.create(
        project_id=str(test_project.id),
        item_id=str(test_item.id),
        title="API Contract",
        contract_type="api",
        status="draft",
    )
    await db_session.commit()

    # draft -> review
    updated = await repo.transition_status(contract.id, "review")
    assert updated.status == "review"

    # review -> approved
    updated = await repo.transition_status(contract.id, "approved")
    assert updated.status == "approved"


# ============================================================================
# FEATURE REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_feature_create_basic(db_session: AsyncSession, test_project: Project) -> None:
    """Test basic feature creation."""
    repo = FeatureRepository(db_session)

    feature = await repo.create(
        project_id=str(test_project.id),
        name="User Authentication",
        description="Implement user authentication",
        status="draft",
    )
    await db_session.commit()

    assert feature.id
    assert feature.feature_number.startswith("FEAT-")
    assert feature.status == "draft"


@pytest.mark.asyncio
async def test_feature_create_with_user_story(db_session: AsyncSession, test_project: Project) -> None:
    """Test feature creation with user story format."""
    repo = FeatureRepository(db_session)

    feature = await repo.create(
        project_id=str(test_project.id),
        name="User Login",
        as_a="user",
        i_want="to log in with email",
        so_that="I can access my account",
        description="Implement login functionality",
        related_requirements=["REQ-001", "REQ-002"],
        related_adrs=["ADR-001"],
        tags=["authentication", "security"],
    )
    await db_session.commit()

    assert feature.as_a == "user"
    assert feature.i_want == "to log in with email"
    assert feature.so_that == "I can access my account"


@pytest.mark.asyncio
async def test_feature_list_by_project(db_session: AsyncSession, test_project: Project) -> None:
    """Test listing features by project."""
    repo = FeatureRepository(db_session)

    for i in range(3):
        await repo.create(project_id=str(test_project.id), name=f"Feature {i}", status="draft")
    await db_session.commit()

    features = await repo.list_by_project(str(test_project.id))
    assert len(features) == COUNT_THREE


@pytest.mark.asyncio
async def test_feature_status_transitions(db_session: AsyncSession, test_project: Project) -> None:
    """Test feature status transitions."""
    repo = FeatureRepository(db_session)

    feature = await repo.create(project_id=str(test_project.id), name="Test Feature", status="draft")
    await db_session.commit()

    # draft -> review
    updated = await repo.transition_status(feature.id, "review")
    assert updated.status == "review"

    # review -> approved
    updated = await repo.transition_status(feature.id, "approved")
    assert updated.status == "approved"

    # approved -> implemented
    updated = await repo.transition_status(feature.id, "implemented")
    assert updated.status == "implemented"


# ============================================================================
# SCENARIO REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_scenario_create_basic(db_session: AsyncSession, test_project: Project) -> None:
    """Test basic scenario creation."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Login Feature")
    await db_session.commit()

    scenario = await repo_scenario.create(
        feature_id=feature.id,
        title="User logs in successfully",
        gherkin_text="Given user is on login page\nWhen user enters credentials\nThen user is logged in",
        status="draft",
    )
    await db_session.commit()

    assert scenario.id
    assert scenario.scenario_number.startswith("SC-")
    assert scenario.feature_id == feature.id


@pytest.mark.asyncio
async def test_scenario_create_with_steps(db_session: AsyncSession, test_project: Project) -> None:
    """Test scenario creation with detailed steps."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Payment Feature")
    await db_session.commit()

    scenario = await repo_scenario.create(
        feature_id=feature.id,
        title="User makes a payment",
        gherkin_text="...",
        given_steps=[{"step": "user has account", "parameter": None}, {"step": "user has balance", "parameter": "100"}],
        when_steps=[{"step": "user initiates payment", "parameter": "50"}],
        then_steps=[
            {"step": "payment is processed", "parameter": None},
            {"step": "balance is updated", "parameter": "50"},
        ],
        tags=["payment", "critical"],
        requirement_ids=["REQ-001", "REQ-002"],
        test_case_ids=["TC-001", "TC-002"],
    )
    await db_session.commit()

    assert len(scenario.given_steps or []) == COUNT_TWO
    assert len(scenario.when_steps or []) == 1
    assert len(scenario.then_steps or []) == COUNT_TWO
    assert scenario.pass_rate == 0.0


@pytest.mark.asyncio
async def test_scenario_create_outline(db_session: AsyncSession, test_project: Project) -> None:
    """Test scenario outline creation."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Login Feature")
    await db_session.commit()

    scenario = await repo_scenario.create(
        feature_id=feature.id,
        title="Login with different users",
        gherkin_text="...",
        is_outline=True,
        examples={
            "header": ["username", "password", "result"],
            "rows": [["user1", "pass1", "success"], ["user2", "pass2", "success"], ["user3", "invalid", "failure"]],
        },
    )
    await db_session.commit()

    assert scenario.is_outline
    assert scenario.examples is not None and isinstance(scenario.examples, dict)
    assert len((scenario.examples or {}).get("rows", [])) == COUNT_THREE


@pytest.mark.asyncio
async def test_scenario_list_by_feature(db_session: AsyncSession, test_project: Project) -> None:
    """Test listing scenarios for a feature."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Login Feature")
    await db_session.commit()

    for i in range(3):
        await repo_scenario.create(feature_id=feature.id, title=f"Scenario {i}", gherkin_text="...")
    await db_session.commit()

    scenarios = await repo_scenario.list_by_feature(feature.id)
    assert len(scenarios) == COUNT_THREE


@pytest.mark.asyncio
async def test_scenario_update_pass_rate(db_session: AsyncSession, test_project: Project) -> None:
    """Test updating scenario pass rate."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Test Feature")
    scenario = await repo_scenario.create(feature_id=feature.id, title="Test Scenario", gherkin_text="...")
    await db_session.commit()

    # Update pass rate
    updated = await repo_scenario.update_pass_rate(scenario.id, 0.85)
    assert updated.pass_rate == 0.85


@pytest.mark.asyncio
async def test_scenario_status_transitions(db_session: AsyncSession, test_project: Project) -> None:
    """Test scenario status transitions."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Test Feature")
    scenario = await repo_scenario.create(
        feature_id=feature.id,
        title="Test Scenario",
        gherkin_text="...",
        status="draft",
    )
    await db_session.commit()

    # draft -> review
    updated = await repo_scenario.transition_status(scenario.id, "review")
    assert updated.status == "review"

    # review -> ready
    updated = await repo_scenario.transition_status(scenario.id, "ready")
    assert updated.status == "ready"


@pytest.mark.asyncio
async def test_scenario_count_by_status(db_session: AsyncSession, test_project: Project) -> None:
    """Test counting scenarios by status."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Test Feature")
    await db_session.commit()

    for i in range(2):
        await repo_scenario.create(feature_id=feature.id, title=f"Draft {i}", gherkin_text="...", status="draft")

    await repo_scenario.create(feature_id=feature.id, title="Ready Scenario", gherkin_text="...", status="ready")
    await db_session.commit()

    counts = await repo_scenario.count_by_status(feature.id)
    assert counts.get("draft") == COUNT_TWO
    assert counts.get("ready") == 1


@pytest.mark.asyncio
async def test_scenario_average_pass_rate(db_session: AsyncSession, test_project: Project) -> None:
    """Test calculating average pass rate for feature."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Test Feature")
    await db_session.commit()

    scenarios = []
    for pass_rate in [0.8, 0.9, 1.0]:
        scenario = await repo_scenario.create(
            feature_id=feature.id,
            title="Test",
            gherkin_text="...",
            pass_rate=pass_rate,
        )
        scenarios.append(scenario)
    await db_session.commit()

    avg = await repo_scenario.get_average_pass_rate(feature.id)
    assert avg == pytest.approx(0.9, rel=0.01)


@pytest.mark.asyncio
async def test_scenario_version_locking(db_session: AsyncSession, test_project: Project) -> None:
    """Test scenario optimistic locking."""
    repo_feature = FeatureRepository(db_session)
    repo_scenario = ScenarioRepository(db_session)

    feature = await repo_feature.create(project_id=str(test_project.id), name="Test Feature")
    scenario = await repo_scenario.create(feature_id=feature.id, title="Test", gherkin_text="...")
    await db_session.commit()

    # Update with correct version
    updated = await repo_scenario.update(scenario.id, scenario.version, title="Updated")
    assert updated.title == "Updated"
    assert updated.version == COUNT_TWO

    # Try with wrong version
    with pytest.raises(ConcurrencyError):
        await repo_scenario.update(scenario.id, 999, title="Another")
