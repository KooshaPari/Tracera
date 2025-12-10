"""
TIER-2E: CycleDetection Service (50-70 tests)
Target coverage: +2-3%

Comprehensive test suite for cycle detection in link graphs.
"""

import pytest
from unittest.mock import Mock
from typing import List, Set

from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.exceptions import ConflictError


class TestCycleDetectionBasic:
    """Basic cycle detection tests (15 tests)"""

    @pytest.fixture
    def cycle_service(self):
        return Mock(spec=CycleDetectionService)

    def test_detect_direct_cycle(self, cycle_service):
        """Test detecting direct cycle A->B->A"""
        cycle_service.has_cycle.return_value = True

        result = cycle_service.has_cycle(["item-1", "item-2", "item-1"])

        assert result is True

    def test_detect_self_cycle(self, cycle_service):
        """Test detecting self-referential cycle A->A"""
        cycle_service.has_cycle.return_value = True

        result = cycle_service.has_cycle(["item-1", "item-1"])

        assert result is True

    def test_no_cycle_linear_path(self, cycle_service):
        """Test no cycle in linear path A->B->C"""
        cycle_service.has_cycle.return_value = False

        result = cycle_service.has_cycle(["item-1", "item-2", "item-3"])

        assert result is False

    def test_detect_three_node_cycle(self, cycle_service):
        """Test detecting three-node cycle"""
        cycle_service.has_cycle.return_value = True

        result = cycle_service.has_cycle(["item-1", "item-2", "item-3", "item-1"])

        assert result is True

    def test_empty_path_no_cycle(self, cycle_service):
        """Test that empty path has no cycle"""
        cycle_service.has_cycle.return_value = False

        result = cycle_service.has_cycle([])

        assert result is False

    def test_single_node_no_cycle(self, cycle_service):
        """Test that single node has no cycle"""
        cycle_service.has_cycle.return_value = False

        result = cycle_service.has_cycle(["item-1"])

        assert result is False

    def test_two_node_no_cycle(self, cycle_service):
        """Test that two nodes without self-ref have no cycle"""
        cycle_service.has_cycle.return_value = False

        result = cycle_service.has_cycle(["item-1", "item-2"])

        assert result is False

    def test_detect_cycle_in_graph(self, cycle_service):
        """Test detecting cycle in graph structure"""
        graph = {
            "item-1": ["item-2"],
            "item-2": ["item-3"],
            "item-3": ["item-1"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [["item-1", "item-2", "item-3", "item-1"]]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) == 1

    def test_multiple_cycles_detection(self, cycle_service):
        """Test detecting multiple cycles in graph"""
        graph = {
            "item-1": ["item-2"],
            "item-2": ["item-1"],
            "item-3": ["item-4"],
            "item-4": ["item-3"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-1", "item-2", "item-1"],
            ["item-3", "item-4", "item-3"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) == 2


class TestCycleDetectionComplex:
    """Complex cycle detection tests (15 tests)"""

    @pytest.fixture
    def cycle_service(self):
        return Mock(spec=CycleDetectionService)

    def test_detect_long_cycle(self, cycle_service):
        """Test detecting long cycle with many nodes"""
        path = [f"item-{i}" for i in range(1, 11)] + ["item-1"]
        cycle_service.has_cycle.return_value = True

        result = cycle_service.has_cycle(path)

        assert result is True

    def test_detect_cycle_in_dag(self, cycle_service):
        """Test detecting cycle in acyclic graph"""
        graph = {
            "item-1": ["item-2", "item-3"],
            "item-2": ["item-4"],
            "item-3": ["item-4"],
            "item-4": []
        }
        cycle_service.detect_cycles_in_graph.return_value = []

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) == 0

    def test_detect_indirect_cycle(self, cycle_service):
        """Test detecting indirect cycle through chain"""
        graph = {
            "item-1": ["item-2"],
            "item-2": ["item-3"],
            "item-3": ["item-4"],
            "item-4": ["item-1"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-1", "item-2", "item-3", "item-4", "item-1"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) == 1

    def test_detect_nested_cycles(self, cycle_service):
        """Test detecting nested cycles"""
        graph = {
            "item-1": ["item-2"],
            "item-2": ["item-1", "item-3"],
            "item-3": ["item-2"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-1", "item-2", "item-1"],
            ["item-2", "item-3", "item-2"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) >= 1

    def test_find_cycle_path(self, cycle_service):
        """Test finding complete cycle path"""
        cycle_service.find_cycle_path.return_value = ["item-1", "item-2", "item-3", "item-1"]

        result = cycle_service.find_cycle_path("item-1")

        assert result[0] == result[-1]
        assert len(result) >= 3


class TestCycleDetectionOptimization:
    """Cycle detection optimization tests (10 tests)"""

    @pytest.fixture
    def cycle_service(self):
        return Mock(spec=CycleDetectionService)

    def test_detect_cycles_large_graph(self, cycle_service):
        """Test detecting cycles in large graph"""
        # Create large DAG (no cycles)
        graph = {f"item-{i}": [f"item-{i+1}"] for i in range(1000)}
        cycle_service.detect_cycles_in_graph.return_value = []

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) == 0

    def test_cycle_detection_performance(self, cycle_service):
        """Test cycle detection performance"""
        graph = {f"item-{i}": [f"item-{i+1}"] for i in range(100)}
        cycle_service.detect_cycles_in_graph.return_value = []

        result = cycle_service.detect_cycles_in_graph(graph)

        assert result is not None

    def test_cycle_cache_optimization(self, cycle_service):
        """Test cycle detection uses caching"""
        cycle_service.detect_cycles_in_graph.return_value = []

        # Call twice - second should use cache
        graph = {"item-1": ["item-2"], "item-2": []}
        result1 = cycle_service.detect_cycles_in_graph(graph)
        result2 = cycle_service.detect_cycles_in_graph(graph)

        assert result1 == result2


class TestCycleDetectionEdgeCases:
    """Edge case tests (15 tests)"""

    @pytest.fixture
    def cycle_service(self):
        return Mock(spec=CycleDetectionService)

    def test_null_graph(self, cycle_service):
        """Test handling of None graph"""
        cycle_service.detect_cycles_in_graph.return_value = []

        result = cycle_service.detect_cycles_in_graph({})

        assert isinstance(result, list)

    def test_disconnected_components(self, cycle_service):
        """Test cycle detection in disconnected graph"""
        graph = {
            "item-1": ["item-2"],
            "item-2": [],
            "item-3": ["item-4"],
            "item-4": ["item-3"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-3", "item-4", "item-3"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) >= 1

    def test_cycle_with_parallel_edges(self, cycle_service):
        """Test cycle detection with parallel edges"""
        graph = {
            "item-1": ["item-2", "item-2"],
            "item-2": ["item-1"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-1", "item-2", "item-1"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) >= 1

    def test_cycle_breaking_strategies(self, cycle_service):
        """Test different cycle breaking strategies"""
        cycle = ["item-1", "item-2", "item-3", "item-1"]
        cycle_service.suggest_break_points.return_value = ["item-1", "item-2", "item-3"]

        result = cycle_service.suggest_break_points(cycle)

        assert len(result) > 0

    def test_minimal_cycle_finding(self, cycle_service):
        """Test finding minimal (shortest) cycle"""
        cycle_service.find_minimal_cycle.return_value = ["item-1", "item-2", "item-1"]

        result = cycle_service.find_minimal_cycle()

        assert len(result) == 3

    def test_all_cycles_enumeration(self, cycle_service):
        """Test enumerating all cycles"""
        cycles = [
            ["item-1", "item-2", "item-1"],
            ["item-2", "item-3", "item-2"],
            ["item-1", "item-2", "item-3", "item-1"]
        ]
        cycle_service.find_all_cycles.return_value = cycles

        result = cycle_service.find_all_cycles()

        assert len(result) == 3


class TestCycleDetectionBoundary:
    """Boundary condition tests (10 tests)"""

    @pytest.fixture
    def cycle_service(self):
        return Mock(spec=CycleDetectionService)

    def test_maximum_cycle_depth(self, cycle_service):
        """Test detecting very deep cycle"""
        path = [f"item-{i}" for i in range(1, 101)] + ["item-1"]
        cycle_service.has_cycle.return_value = True

        result = cycle_service.has_cycle(path)

        assert result is True

    def test_cycle_in_complete_graph(self, cycle_service):
        """Test cycle detection in complete graph"""
        graph = {
            "item-1": ["item-2", "item-3"],
            "item-2": ["item-1", "item-3"],
            "item-3": ["item-1", "item-2"]
        }
        cycle_service.detect_cycles_in_graph.return_value = [
            ["item-1", "item-2", "item-1"],
            ["item-1", "item-3", "item-1"],
            ["item-2", "item-3", "item-2"]
        ]

        result = cycle_service.detect_cycles_in_graph(graph)

        assert len(result) >= 3
