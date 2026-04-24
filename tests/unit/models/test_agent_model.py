"""Unit tests for Agent model."""

from uuid import uuid4

import pytest

from tracertm.models import Agent

pytestmark = pytest.mark.unit


class TestAgentModelCreation:
    """Test Agent model creation."""

    def test_agent_creation_with_name(self) -> None:
        """Agent creates with name."""
        agent = Agent(name="Test Agent")
        assert agent.name == "Test Agent"

    def test_agent_creation_with_project_id(self) -> None:
        """Agent can include project_id."""
        project_id = str(uuid4())
        agent = Agent(name="Test Agent", project_id=project_id)
        assert agent.project_id == project_id

    def test_agent_creation_with_type(self) -> None:
        """Agent can specify agent_type."""
        agent = Agent(name="Test Agent", agent_type="coordinator")
        assert agent.agent_type == "coordinator"

    def test_agent_creation_with_config(self) -> None:
        """Agent can include config."""
        config = {"timeout": 30, "retry_count": 3}
        agent = Agent(name="Test Agent", config=config)
        assert agent.config == config

    def test_agent_creation_with_capabilities(self) -> None:
        """Agent can list capabilities."""
        capabilities = ["read", "write", "analyze"]
        agent = Agent(name="Test Agent", capabilities=capabilities)
        assert agent.capabilities == capabilities

    def test_agent_defaults_agent_type(self) -> None:
        """Agent defaults agent_type to 'generic'."""
        agent = Agent(name="Test")
        assert agent.agent_type == "generic"

    def test_agent_defaults_status(self) -> None:
        """Agent has status field (defaults to active)."""
        agent = Agent(name="Test")
        assert hasattr(agent, "status")


class TestAgentModelTypes:
    """Test Agent with different agent types."""

    def test_agent_type_generic(self) -> None:
        """Agent supports generic type."""
        agent = Agent(name="Test", agent_type="generic")
        assert agent.agent_type == "generic"

    def test_agent_type_analyzer(self) -> None:
        """Agent supports analyzer type."""
        agent = Agent(name="Test", agent_type="analyzer")
        assert agent.agent_type == "analyzer"

    def test_agent_type_coordinator(self) -> None:
        """Agent supports coordinator type."""
        agent = Agent(name="Test", agent_type="coordinator")
        assert agent.agent_type == "coordinator"

    def test_agent_type_executor(self) -> None:
        """Agent supports executor type."""
        agent = Agent(name="Test", agent_type="executor")
        assert agent.agent_type == "executor"


class TestAgentModelMetadata:
    """Test Agent metadata fields."""

    def test_agent_metadata_storage(self) -> None:
        """Agent can store metadata."""
        metadata = {"version": "1.0", "author": "test"}
        agent = Agent(name="Test", agent_metadata=metadata)
        assert agent.agent_metadata == metadata

    def test_agent_config_and_metadata(self) -> None:
        """Agent can have both config and metadata."""
        config = {"key": "value"}
        metadata = {"type": "test"}
        agent = Agent(name="Test", config=config, agent_metadata=metadata)
        assert agent.config == config
        assert agent.agent_metadata == metadata


class TestAgentModelAttributes:
    """Test Agent model attributes."""

    def test_agent_has_timestamps(self) -> None:
        """Agent has timestamp attributes."""
        agent = Agent(name="Test")
        assert hasattr(agent, "created_at")
        assert hasattr(agent, "updated_at")

    def test_agent_has_last_activity(self) -> None:
        """Agent has last_activity_at field."""
        agent = Agent(name="Test")
        assert hasattr(agent, "last_activity_at")

    def test_agent_last_activity_optional(self) -> None:
        """Agent last_activity_at is optional."""
        agent = Agent(name="Test")
        assert agent.last_activity_at is None


class TestAgentModelRepresentation:
    """Test Agent model representation."""

    def test_agent_repr(self) -> None:
        """Agent has string representation."""
        agent = Agent(name="Test Agent")
        repr_str = repr(agent)
        assert "Agent" in repr_str
        assert "Test Agent" in repr_str
