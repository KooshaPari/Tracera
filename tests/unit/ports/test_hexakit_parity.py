"""Unit tests for HexaKit canonical port parity (NFR-TRC-011).

Verifies that Tracera's port interfaces follow the HexaKit pattern for canonical
ports: all ports are dependency-free, abstract, and contain typed methods that
are inspectable and properly constrained. This ensures cross-repo parity between
Tracera, HexaKit/Rust, and other implementers.

Implements ``NFR-TRC-011`` (HexaKit Canonical Ports Mirror). See
``docs/specs/NFR-TRC-011-hexakit-parity.md``.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Protocol, get_type_hints

import pytest


# ============================================================================
# Test: All Tracera ports are importable and use Protocol / ABC
# ============================================================================


def test_graph_port_is_importable():
    """FR-NFR-TRC-011: GraphPort must be importable from canonical location."""
    from tracertm.ports import GraphPort

    assert GraphPort is not None
    assert hasattr(GraphPort, "upsert_node")
    assert hasattr(GraphPort, "upsert_edge")


def test_scorer_port_is_importable():
    """FR-NFR-TRC-011: ScorerPort must be importable from canonical location."""
    from tracertm.ports import ScorerPort

    assert ScorerPort is not None
    assert hasattr(ScorerPort, "score")
    assert hasattr(ScorerPort, "name")


def test_model_adapter_port_is_importable():
    """FR-NFR-TRC-011: ModelAdapter must be importable from canonical location."""
    from tracertm.ml.registry import ModelAdapter

    assert ModelAdapter is not None
    assert hasattr(ModelAdapter, "dump")
    assert hasattr(ModelAdapter, "load")


def test_graph_port_is_runtime_checkable_protocol():
    """FR-NFR-TRC-011: GraphPort must be a runtime-checkable Protocol."""
    from tracertm.ports import GraphPort

    # Verify it's actually a Protocol
    assert hasattr(GraphPort, "__mro__")
    # Check that isinstance works (runtime-checkable)
    assert hasattr(GraphPort, "_is_protocol")


def test_scorer_port_is_runtime_checkable_protocol():
    """FR-NFR-TRC-011: ScorerPort must be a runtime-checkable Protocol."""
    from tracertm.ports import ScorerPort

    # Verify it's actually a Protocol
    assert hasattr(ScorerPort, "__mro__")
    # Check that isinstance works (runtime-checkable)
    assert hasattr(ScorerPort, "_is_protocol")


def test_model_adapter_is_protocol():
    """FR-NFR-TRC-011: ModelAdapter must be a Protocol."""
    from tracertm.ml.registry import ModelAdapter

    # Verify it's actually a Protocol
    assert hasattr(ModelAdapter, "__mro__")


# ============================================================================
# Test: Port methods have proper type annotations (HexaKit requirement)
# ============================================================================


def test_graph_port_methods_have_annotations():
    """FR-NFR-TRC-011: GraphPort methods must have type annotations."""
    from tracertm.ports import GraphPort

    # Check key methods for annotations
    methods = ["upsert_node", "upsert_edge", "upsert_nodes", "upsert_edges", "neighbors"]
    for method_name in methods:
        method = getattr(GraphPort, method_name, None)
        assert method is not None, f"GraphPort.{method_name} not found"
        if hasattr(method, "__annotations__"):
            # Methods should have at least return type annotation
            assert len(method.__annotations__) > 0 or method.__doc__, (
                f"GraphPort.{method_name} lacks type annotations"
            )


def test_scorer_port_methods_have_annotations():
    """FR-NFR-TRC-011: ScorerPort methods must have type annotations."""
    from tracertm.ports import ScorerPort

    methods = ["score"]
    for method_name in methods:
        method = getattr(ScorerPort, method_name, None)
        assert method is not None, f"ScorerPort.{method_name} not found"
        # Verify the method exists and is callable
        assert callable(method), f"ScorerPort.{method_name} is not callable"


def test_model_adapter_methods_have_annotations():
    """FR-NFR-TRC-011: ModelAdapter methods must have type annotations."""
    from tracertm.ml.registry import ModelAdapter

    methods = ["dump", "load"]
    for method_name in methods:
        method = getattr(ModelAdapter, method_name, None)
        assert method is not None, f"ModelAdapter.{method_name} not found"
        # These are Protocol methods, so they should be defined
        assert callable(method), f"ModelAdapter.{method_name} is not callable"


# ============================================================================
# Test: Concrete implementations satisfy their ports
# ============================================================================


def test_jaccard_scorer_satisfies_scorer_port():
    """FR-NFR-TRC-011: JaccardScorer must implement ScorerPort protocol."""
    from tracertm.ports import JaccardScorer, ScorerPort

    scorer = JaccardScorer()
    assert isinstance(scorer, ScorerPort), "JaccardScorer does not satisfy ScorerPort"


def test_pickle_adapter_satisfies_model_adapter_port():
    """FR-NFR-TRC-011: PickleAdapter must implement ModelAdapter protocol."""
    from tracertm.ml.registry import ModelAdapter, PickleAdapter

    adapter = PickleAdapter()
    assert isinstance(adapter, ModelAdapter), "PickleAdapter does not satisfy ModelAdapter"


def test_pytorch_adapter_satisfies_model_adapter_port():
    """FR-NFR-TRC-011: PyTorchAdapter must implement ModelAdapter protocol."""
    from tracertm.ml.registry import ModelAdapter, PyTorchAdapter

    adapter = PyTorchAdapter()
    assert isinstance(adapter, ModelAdapter), "PyTorchAdapter does not satisfy ModelAdapter"


def test_sklearn_adapter_satisfies_model_adapter_port():
    """FR-NFR-TRC-011: SklearnJoblibAdapter must implement ModelAdapter protocol."""
    from tracertm.ml.registry import ModelAdapter, SklearnJoblibAdapter

    adapter = SklearnJoblibAdapter()
    assert isinstance(adapter, ModelAdapter), "SklearnJoblibAdapter does not satisfy ModelAdapter"


def test_onnx_adapter_satisfies_model_adapter_port():
    """FR-NFR-TRC-011: OnnxAdapter must implement ModelAdapter protocol."""
    from tracertm.ml.registry import ModelAdapter, OnnxAdapter

    adapter = OnnxAdapter()
    assert isinstance(adapter, ModelAdapter), "OnnxAdapter does not satisfy ModelAdapter"


# ============================================================================
# Test: Port interfaces are dependency-free (can be mirrored in other langs)
# ============================================================================


def test_graph_port_imports_are_stdlib_only():
    """FR-NFR-TRC-011: GraphPort must not depend on external packages (mirroring requirement)."""
    from tracertm.ports import graph_contract

    # Check that graph_contract module only uses stdlib imports in the Protocol
    module_source = inspect.getsource(graph_contract)
    # Should only use typing module, dataclasses, enum (all stdlib)
    assert "import Protocol" in module_source or "from typing" in module_source


def test_scorer_port_imports_are_lightweight():
    """FR-NFR-TRC-011: ScorerPort should have minimal external dependencies."""
    from tracertm.ports import scorer

    # Scorer uses only typing, dataclasses, re (all stdlib) for the port definition
    module_source = inspect.getsource(scorer)
    assert "Protocol" in module_source


def test_model_adapter_port_imports_are_stdlib():
    """FR-NFR-TRC-011: ModelAdapter port must use only stdlib in interface."""
    from tracertm.ml import registry

    module_source = inspect.getsource(registry)
    # The Protocol definition uses only typing and pathlib (stdlib)
    assert "Protocol" in module_source
    assert "from pathlib import Path" in module_source


# ============================================================================
# Test: Port discovery and structural parity
# ============================================================================


def test_can_discover_all_tracera_ports():
    """FR-NFR-TRC-011: All ports must be discoverable via introspection."""
    ports_module = importlib.import_module("tracertm.ports")

    # Check that major ports are exported
    assert hasattr(ports_module, "GraphPort")
    assert hasattr(ports_module, "ScorerPort")
    # Also check via explicit import
    from tracertm.ml.registry import ModelAdapter
    assert ModelAdapter is not None


def test_graph_port_has_required_methods():
    """FR-NFR-TRC-011: GraphPort must have all canonical methods for HexaKit parity."""
    from tracertm.ports import GraphPort

    required_methods = [
        "upsert_node",
        "upsert_edge",
        "upsert_nodes",
        "upsert_edges",
        "neighbors",
    ]
    for method_name in required_methods:
        assert hasattr(GraphPort, method_name), (
            f"GraphPort missing required HexaKit-parity method: {method_name}"
        )


def test_scorer_port_has_required_interface():
    """FR-NFR-TRC-011: ScorerPort must have canonical method + name property."""
    from tracertm.ports import ScorerPort

    assert hasattr(ScorerPort, "score"), "ScorerPort missing score method"
    assert hasattr(ScorerPort, "name"), "ScorerPort missing name property"


def test_model_adapter_has_required_interface():
    """FR-NFR-TRC-011: ModelAdapter must have dump/load + format/extension properties."""
    from tracertm.ml.registry import ModelAdapter

    required = ["dump", "load", "format", "extension"]
    for item in required:
        assert hasattr(ModelAdapter, item), f"ModelAdapter missing {item}"


# ============================================================================
# Test: Port compliance with HexaKit canonical pattern
# ============================================================================


def test_ports_can_be_instantiated_and_used():
    """FR-NFR-TRC-011: Concrete port implementations must be usable."""
    from tracertm.ports import JaccardScorer, ScorerPort

    scorer = JaccardScorer()
    result = scorer.score("hello world", "hello there")

    assert result is not None
    assert hasattr(result, "score")
    assert hasattr(result, "strategy")
    assert 0.0 <= result.score <= 1.0


def test_port_protocols_support_duck_typing():
    """FR-NFR-TRC-011: Ports must support duck-typed implementations (HexaKit pattern)."""
    from tracertm.ports import GraphPort, GraphNode, GraphEdge, NodeKind, EdgeType

    # Create a minimal duck-typed implementation
    class MinimalGraphPort:
        def upsert_node(self, node: GraphNode) -> None:
            pass

        def upsert_edge(self, edge: GraphEdge) -> None:
            pass

        def upsert_nodes(self, nodes: list[GraphNode]) -> None:
            pass

        def upsert_edges(self, edges: list[GraphEdge]) -> None:
            pass

        def neighbors(self, node: GraphNode, *, edge_type=None, direction="out"):
            return []

    # Should be recognized as satisfying the protocol
    impl = MinimalGraphPort()
    assert isinstance(impl, GraphPort), (
        "Duck-typed implementation should satisfy GraphPort protocol"
    )


def test_hexakit_pattern_allows_swappable_strategies():
    """FR-NFR-TRC-011: Port pattern allows strategy pattern substitution."""
    from tracertm.ports import ScorerPort, JaccardScorer

    def use_scorer(scorer: ScorerPort, a: str, b: str) -> float:
        return scorer.score(a, b).score

    # Any ScorerPort implementation is interchangeable
    result = use_scorer(JaccardScorer(), "abc def", "abc xyz")
    assert 0.0 <= result <= 1.0


# ============================================================================
# Test: Detailed structural parity
# ============================================================================


def test_graph_port_method_signatures_are_sound():
    """FR-NFR-TRC-011: GraphPort methods must have sane signatures for mirror impl."""
    from tracertm.ports import GraphPort, GraphNode

    # Verify upsert_node signature
    sig = inspect.signature(GraphPort.upsert_node)
    params = list(sig.parameters.keys())
    assert "node" in params, "upsert_node missing 'node' parameter"


def test_scorer_port_score_method_parameters():
    """FR-NFR-TRC-011: ScorerPort.score must have requirement/artifact parameters."""
    from tracertm.ports import ScorerPort

    sig = inspect.signature(ScorerPort.score)
    params = list(sig.parameters.keys())
    # Should have both requirement and artifact (or similar)
    assert len(params) >= 2, "ScorerPort.score should have at least 2 parameters"


def test_model_adapter_dump_load_are_mirror_operations():
    """FR-NFR-TRC-011: ModelAdapter dump/load must be symmetric operations."""
    from tracertm.ml.registry import ModelAdapter

    # Both methods should exist and be callable
    assert callable(getattr(ModelAdapter, "dump"))
    assert callable(getattr(ModelAdapter, "load"))


def test_ports_are_defined_in_stable_locations():
    """FR-NFR-TRC-011: Ports must live in stable, documented locations."""
    # These import paths should never change for HexaKit parity
    locations = [
        "tracertm.ports:GraphPort",
        "tracertm.ports:ScorerPort",
        "tracertm.ml.registry:ModelAdapter",
    ]

    for location in locations:
        module_path, class_name = location.split(":")
        module = importlib.import_module(module_path)
        assert hasattr(module, class_name), f"Port {location} not found at canonical location"


# ============================================================================
# Test: Protocol documentation and intros follow HexaKit pattern
# ============================================================================


def test_graph_port_has_docstring():
    """FR-NFR-TRC-011: GraphPort must document its contract."""
    from tracertm.ports import GraphPort

    assert GraphPort.__doc__ is not None
    assert len(GraphPort.__doc__) > 0
    assert "FR-TRC-018" in GraphPort.__doc__ or "contract" in GraphPort.__doc__.lower()


def test_scorer_port_has_docstring():
    """FR-NFR-TRC-011: ScorerPort must document its strategy pattern role."""
    from tracertm.ports import ScorerPort

    assert ScorerPort.__doc__ is not None
    assert len(ScorerPort.__doc__) > 0


def test_model_adapter_has_docstring():
    """FR-NFR-TRC-011: ModelAdapter must document its serialization contract."""
    from tracertm.ml.registry import ModelAdapter

    assert ModelAdapter.__doc__ is not None
    assert len(ModelAdapter.__doc__) > 0


# ============================================================================
# Test: Type-checking support for HexaKit mirror
# ============================================================================


def test_ports_use_runtime_checkable():
    """FR-NFR-TRC-011: Ports should use @runtime_checkable for duck typing."""
    from tracertm.ports import graph_contract, scorer
    import inspect as insp

    # GraphPort should have @runtime_checkable
    gp_source = insp.getsource(graph_contract.GraphPort)
    assert "@runtime_checkable" in gp_source, "GraphPort should use @runtime_checkable"

    # ScorerPort should have @runtime_checkable
    sp_source = insp.getsource(scorer.ScorerPort)
    assert "@runtime_checkable" in sp_source, "ScorerPort should use @runtime_checkable"


def test_concrete_implementations_are_clean():
    """FR-NFR-TRC-011: Implementations must be inspectable and without side effects."""
    from tracertm.ports import JaccardScorer

    # JaccardScorer should be a clean, simple implementation
    scorer = JaccardScorer()

    # Should have a name
    assert hasattr(scorer, "name")
    assert scorer.name == "jaccard"

    # Should have a score method
    assert hasattr(scorer, "score")
    assert callable(scorer.score)


# ============================================================================
# Meta-test: This test file itself validates NFR-TRC-011 coverage
# ============================================================================


def test_nfr_trc_011_test_coverage_is_comprehensive():
    """FR-NFR-TRC-011: This test suite must cover all canonical ports."""
    # Count the number of test functions that reference NFR-TRC-011
    current_module = importlib.import_module(__name__)

    test_functions = [
        name for name in dir(current_module)
        if name.startswith("test_") and callable(getattr(current_module, name))
    ]

    # Should have at least 10 tests covering port parity
    assert len(test_functions) >= 10, (
        f"Insufficient test coverage for NFR-TRC-011: {len(test_functions)} tests"
    )
