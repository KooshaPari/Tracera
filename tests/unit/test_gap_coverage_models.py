"""Gap coverage tests for low-coverage model modules.

Targets: models/agent.py, models/agent_event.py, models/types.py.
"""

from unittest.mock import MagicMock


class TestAgentModel:
    """Tests for Agent model to increase coverage."""

    def test_agent_import(self) -> None:
        """Test Agent model can be imported."""
        from tracertm.models.agent import Agent, generate_agent_uuid

        assert Agent is not None
        assert generate_agent_uuid is not None

    def test_generate_agent_uuid(self) -> None:
        """Test UUID generation for agents."""
        from tracertm.models.agent import generate_agent_uuid

        uuid1 = generate_agent_uuid()
        uuid2 = generate_agent_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert len(uuid1) == 36  # Standard UUID format
        assert uuid1 != uuid2  # Should be unique

    def test_agent_repr(self) -> None:
        """Test Agent __repr__ method."""
        from tracertm.models.agent import Agent

        agent = Agent()
        agent.id = "test-id"
        agent.name = "Test Agent"

        repr_str = repr(agent)
        assert "Agent" in repr_str
        assert "test-id" in repr_str
        assert "Test Agent" in repr_str

    def test_agent_table_name(self) -> None:
        """Test Agent table name is set."""
        from tracertm.models.agent import Agent

        assert Agent.__tablename__ == "agents"


class TestAgentEventModel:
    """Tests for AgentEvent model."""

    def test_agent_event_import(self) -> None:
        """Test AgentEvent model can be imported."""
        from tracertm.models.agent_event import AgentEvent, generate_event_uuid

        assert AgentEvent is not None
        assert generate_event_uuid is not None

    def test_generate_event_uuid(self) -> None:
        """Test UUID generation for events."""
        from tracertm.models.agent_event import generate_event_uuid

        uuid1 = generate_event_uuid()
        uuid2 = generate_event_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert len(uuid1) == 36
        assert uuid1 != uuid2

    def test_agent_event_table_name(self) -> None:
        """Test AgentEvent table name is set."""
        from tracertm.models.agent_event import AgentEvent

        assert AgentEvent.__tablename__ == "agent_events"

    def test_agent_event_repr(self) -> None:
        """Test AgentEvent __repr__ method."""
        from tracertm.models.agent_event import AgentEvent

        event = AgentEvent()
        event.id = "event-123"
        event.event_type = "item_created"
        event.agent_id = "agent-456"

        repr_str = repr(event)
        assert "AgentEvent" in repr_str
        assert "event-123" in repr_str
        assert "item_created" in repr_str
        assert "agent-456" in repr_str


class TestJSONType:
    """Tests for custom JSONType."""

    def test_json_type_import(self) -> None:
        """Test JSONType can be imported."""
        from tracertm.models.types import JSONType

        assert JSONType is not None

    def test_json_type_cache_ok(self) -> None:
        """Test JSONType has cache_ok set."""
        from tracertm.models.types import JSONType

        assert JSONType.cache_ok is True

    def test_json_type_load_dialect_impl_postgresql(self) -> None:
        """Test JSONType uses JSONB for PostgreSQL."""
        from tracertm.models.types import JSONType

        json_type = JSONType()

        # Mock PostgreSQL dialect
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"
        mock_dialect.type_descriptor = MagicMock(return_value="jsonb_type")

        result = json_type.load_dialect_impl(mock_dialect)

        assert result == "jsonb_type"
        mock_dialect.type_descriptor.assert_called_once()

    def test_json_type_load_dialect_impl_sqlite(self) -> None:
        """Test JSONType uses JSON for SQLite."""
        from tracertm.models.types import JSONType

        json_type = JSONType()

        # Mock SQLite dialect
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"
        mock_dialect.type_descriptor = MagicMock(return_value="json_type")

        result = json_type.load_dialect_impl(mock_dialect)

        assert result == "json_type"
        mock_dialect.type_descriptor.assert_called_once()

    def test_json_type_load_dialect_impl_mysql(self) -> None:
        """Test JSONType uses JSON for MySQL."""
        from tracertm.models.types import JSONType

        json_type = JSONType()

        # Mock MySQL dialect
        mock_dialect = MagicMock()
        mock_dialect.name = "mysql"
        mock_dialect.type_descriptor = MagicMock(return_value="json_type")

        result = json_type.load_dialect_impl(mock_dialect)

        assert result == "json_type"


class TestAgentLockModel:
    """Tests for AgentLock model."""

    def test_agent_lock_import(self) -> None:
        """Test AgentLock model can be imported."""
        from tracertm.models.agent_lock import AgentLock

        assert AgentLock is not None

    def test_agent_lock_table_name(self) -> None:
        """Test AgentLock table name is set."""
        from tracertm.models.agent_lock import AgentLock

        assert AgentLock.__tablename__ == "agent_locks"
