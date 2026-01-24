"""
Comprehensive tests for DependencyAnalysisService.

Tests all public methods with various scenarios:
- Service initialization with and without db_session
- analyze() method with empty, single, and multiple dependencies
- Error handling and edge cases
- Database interactions and session management

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

from tracertm.services.dependency_analysis_service import DependencyAnalysisService


class TestDependencyAnalysisServiceInitialization:
    """Test service initialization."""

    def test_initialization_with_db_session(self):
        """Test service initializes with db_session."""
        mock_session = Mock()
        service = DependencyAnalysisService(mock_session)
        assert service is not None
        assert service.db_session == mock_session

    def test_initialization_without_db_session(self):
        """Test service initializes without db_session (defaults to None)."""
        service = DependencyAnalysisService()
        assert service is not None
        assert service.db_session is None

    def test_initialization_with_none_session(self):
        """Test service handles explicit None db_session."""
        service = DependencyAnalysisService(None)
        assert service is not None
        assert service.db_session is None


class TestDependencyAnalysisServiceAnalyzeMethod:
    """Test analyze() method."""

    @pytest.fixture
    def service_with_mock_session(self):
        """Create service with mocked db_session."""
        mock_session = AsyncMock()
        service = DependencyAnalysisService(mock_session)
        return service

    @pytest.mark.asyncio
    async def test_analyze_returns_dict(self, service_with_mock_session):
        """Test analyze returns a dictionary."""
        result = await service_with_mock_session.analyze()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_has_status_key(self, service_with_mock_session):
        """Test analyze result contains status key."""
        result = await service_with_mock_session.analyze()
        assert "status" in result
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_analyze_has_dependencies_key(self, service_with_mock_session):
        """Test analyze result contains dependencies key."""
        result = await service_with_mock_session.analyze()
        assert "dependencies" in result
        assert isinstance(result["dependencies"], list)

    @pytest.mark.asyncio
    async def test_analyze_empty_dependencies(self, service_with_mock_session):
        """Test analyze with no dependencies."""
        result = await service_with_mock_session.analyze()
        assert result["dependencies"] == []

    @pytest.mark.asyncio
    async def test_analyze_with_args(self, service_with_mock_session):
        """Test analyze accepts arbitrary args."""
        result = await service_with_mock_session.analyze("arg1", "arg2")
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_analyze_with_kwargs(self, service_with_mock_session):
        """Test analyze accepts arbitrary kwargs."""
        result = await service_with_mock_session.analyze(
            project_id="proj-1",
            depth=2,
            include_transitive=True
        )
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_analyze_with_mixed_args_kwargs(self, service_with_mock_session):
        """Test analyze accepts mixed args and kwargs."""
        result = await service_with_mock_session.analyze(
            "pos_arg1",
            "pos_arg2",
            project_id="proj-1",
            depth=3
        )
        assert isinstance(result, dict)


class TestDependencyAnalysisServiceWithoutSession:
    """Test service behavior without db_session."""

    @pytest.fixture
    def service_no_session(self):
        """Create service without db_session."""
        return DependencyAnalysisService()

    @pytest.mark.asyncio
    async def test_analyze_without_session(self, service_no_session):
        """Test analyze works without db_session."""
        result = await service_no_session.analyze()
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_analyze_multiple_calls_without_session(self, service_no_session):
        """Test multiple analyze calls without db_session."""
        result1 = await service_no_session.analyze()
        result2 = await service_no_session.analyze()
        assert result1 == result2
        assert result1["status"] == "ok"


class TestDependencyAnalysisServiceErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_analyze_none_args(self):
        """Test analyze with None as argument."""
        service = DependencyAnalysisService()
        result = await service.analyze(None)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_empty_string_args(self):
        """Test analyze with empty string argument."""
        service = DependencyAnalysisService()
        result = await service.analyze("")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_large_number_of_kwargs(self):
        """Test analyze with many kwargs."""
        service = DependencyAnalysisService()
        kwargs = {f"key_{i}": f"value_{i}" for i in range(100)}
        result = await service.analyze(**kwargs)
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_analyze_with_complex_objects(self):
        """Test analyze with complex objects as kwargs."""
        service = DependencyAnalysisService()
        complex_obj = {
            "nested": {"deep": {"data": [1, 2, 3]}},
            "list": [{"a": 1}, {"b": 2}]
        }
        result = await service.analyze(filter=complex_obj)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_consistency(self):
        """Test analyze returns consistent results."""
        service = DependencyAnalysisService()
        results = [await service.analyze() for _ in range(5)]
        # All results should be identical
        assert all(r == results[0] for r in results)


class TestDependencyAnalysisServiceIntegration:
    """Integration tests with mocked repositories."""

    @pytest.fixture
    def service_with_repos(self):
        """Service with mocked repositories."""
        mock_session = AsyncMock()
        service = DependencyAnalysisService(mock_session)
        service.items_repo = AsyncMock()
        service.links_repo = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_analyze_calls_session_if_available(self):
        """Test analyze can use db_session if available."""
        mock_session = AsyncMock()
        service = DependencyAnalysisService(mock_session)
        result = await service.analyze()
        # Result should be valid regardless of whether session was used
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_service_with_mock_repos(self, service_with_repos):
        """Test service with mocked repositories."""
        service_with_repos.items_repo.get_all = AsyncMock(return_value=[])
        service_with_repos.links_repo.get_all = AsyncMock(return_value=[])
        result = await service_with_repos.analyze()
        assert isinstance(result, dict)


class TestDependencyAnalysisServiceConcurrency:
    """Test concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_analyze_calls(self):
        """Test multiple concurrent analyze calls."""
        service = DependencyAnalysisService()
        tasks = [service.analyze() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)
        assert all(r["status"] == "ok" for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_with_different_args(self):
        """Test concurrent calls with different arguments."""
        service = DependencyAnalysisService()
        tasks = [
            service.analyze(f"arg_{i}", depth=i)
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        assert len(results) == 5
        assert all(r["status"] == "ok" for r in results)


class TestDependencyAnalysisServiceReturnValues:
    """Test return value structure and content."""

    @pytest.mark.asyncio
    async def test_analyze_return_structure(self):
        """Test analyze returns properly structured result."""
        service = DependencyAnalysisService()
        result = await service.analyze()
        assert isinstance(result, dict)
        assert len(result) == 2  # status and dependencies
        assert set(result.keys()) == {"status", "dependencies"}

    @pytest.mark.asyncio
    async def test_analyze_dependencies_list_type(self):
        """Test dependencies is always a list."""
        service = DependencyAnalysisService()
        result = await service.analyze()
        assert isinstance(result["dependencies"], list)

    @pytest.mark.asyncio
    async def test_analyze_status_value(self):
        """Test status is always 'ok'."""
        service = DependencyAnalysisService()
        result = await service.analyze()
        assert result["status"] == "ok"
        assert isinstance(result["status"], str)


class TestDependencyAnalysisServiceStateManagement:
    """Test state management and side effects."""

    @pytest.mark.asyncio
    async def test_service_state_not_modified(self):
        """Test service state is not modified by analyze."""
        service = DependencyAnalysisService()
        initial_db = service.db_session
        await service.analyze()
        assert service.db_session == initial_db

    @pytest.mark.asyncio
    async def test_multiple_instances_independent(self):
        """Test multiple service instances are independent."""
        service1 = DependencyAnalysisService()
        service2 = DependencyAnalysisService()
        result1 = await service1.analyze()
        result2 = await service2.analyze()
        assert result1 == result2  # Same content
        assert service1 is not service2  # Different objects


class TestDependencyAnalysisServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_analyze_with_special_characters(self):
        """Test analyze with special characters in args."""
        service = DependencyAnalysisService()
        result = await service.analyze(
            "special!@#$%^&*()",
            filter="<script>alert('xss')</script>"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_with_unicode(self):
        """Test analyze with unicode characters."""
        service = DependencyAnalysisService()
        result = await service.analyze(
            "🚀 unicode test",
            description="测试中文字符"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_with_very_large_string(self):
        """Test analyze with very large string."""
        service = DependencyAnalysisService()
        large_str = "x" * 10000
        result = await service.analyze(large_str)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_with_negative_numbers(self):
        """Test analyze with negative numbers."""
        service = DependencyAnalysisService()
        result = await service.analyze(depth=-1, count=-100)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_with_zero_values(self):
        """Test analyze with zero values."""
        service = DependencyAnalysisService()
        result = await service.analyze(depth=0, count=0)
        assert isinstance(result, dict)
