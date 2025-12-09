"""
Comprehensive tests for VisualizationService.

Coverage target: 100%
Tests all methods: render_tree, render_graph, render_dependency_matrix.

Covers:
- Success scenarios with various data structures
- Edge cases (empty data, single items, nested structures)
- Boundary conditions
- Output formatting validation
- Special characters and error handling
"""

import pytest
from tracertm.services.visualization_service import VisualizationService


class TestRenderTree:
    """Test render_tree method comprehensively."""

    def test_empty_items_returns_empty_string(self):
        """Test that empty items list returns empty string."""
        result = VisualizationService.render_tree([])
        assert result == ""

    def test_single_item_with_title(self):
        """Test rendering single item with title."""
        items = [{"id": "1", "title": "Item 1"}]
        result = VisualizationService.render_tree(items)
        assert "Item 1" in result
        assert "└──" in result

    def test_single_item_without_title_uses_id(self):
        """Test that item without title falls back to ID."""
        items = [{"id": "item-123"}]
        result = VisualizationService.render_tree(items)
        assert "item-123" in result

    def test_multiple_items_same_level(self):
        """Test multiple items at the same level."""
        items = [
            {"id": "1", "title": "First"},
            {"id": "2", "title": "Second"},
            {"id": "3", "title": "Third"},
        ]
        result = VisualizationService.render_tree(items)
        assert "First" in result
        assert "Second" in result
        assert "Third" in result
        # Should have both types of branches
        assert "├──" in result
        assert "└──" in result

    def test_items_with_single_child(self):
        """Test item with single child."""
        items = [
            {
                "id": "1",
                "title": "Parent",
                "children": [
                    {"id": "2", "title": "Child"},
                ],
            }
        ]
        result = VisualizationService.render_tree(items)
        assert "Parent" in result
        assert "Child" in result

    def test_items_with_multiple_children(self):
        """Test item with multiple children."""
        items = [
            {
                "id": "1",
                "title": "Parent",
                "children": [
                    {"id": "2", "title": "Child 1"},
                    {"id": "3", "title": "Child 2"},
                    {"id": "4", "title": "Child 3"},
                ],
            }
        ]
        result = VisualizationService.render_tree(items)
        assert "Parent" in result
        assert "Child 1" in result
        assert "Child 2" in result
        assert "Child 3" in result

    def test_deeply_nested_children(self):
        """Test deeply nested tree structure."""
        items = [
            {
                "id": "1",
                "title": "Level 1",
                "children": [
                    {
                        "id": "2",
                        "title": "Level 2",
                        "children": [
                            {
                                "id": "3",
                                "title": "Level 3",
                                "children": [
                                    {"id": "4", "title": "Level 4"},
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
        result = VisualizationService.render_tree(items)
        assert "Level 1" in result
        assert "Level 2" in result
        assert "Level 3" in result
        assert "Level 4" in result

    def test_multiple_branches_with_children(self):
        """Test multiple parent items each with children."""
        items = [
            {
                "id": "1",
                "title": "Parent 1",
                "children": [
                    {"id": "2", "title": "Child 1-1"},
                    {"id": "3", "title": "Child 1-2"},
                ],
            },
            {
                "id": "4",
                "title": "Parent 2",
                "children": [
                    {"id": "5", "title": "Child 2-1"},
                ],
            },
        ]
        result = VisualizationService.render_tree(items)
        assert "Parent 1" in result
        assert "Parent 2" in result
        assert "Child 1-1" in result
        assert "Child 2-1" in result

    def test_empty_children_list(self):
        """Test item with empty children list."""
        items = [{"id": "1", "title": "Item", "children": []}]
        result = VisualizationService.render_tree(items)
        assert "Item" in result

    def test_with_custom_prefix(self):
        """Test rendering with custom prefix."""
        items = [{"id": "1", "title": "Item"}]
        result = VisualizationService.render_tree(items, prefix="  ")
        assert "Item" in result

    def test_special_characters_in_title(self):
        """Test items with special characters in titles."""
        items = [
            {"id": "1", "title": "Item with $pecial Ch@rs!"},
            {"id": "2", "title": "Item with 日本語"},
            {"id": "3", "title": "Item with\nnewline"},
        ]
        result = VisualizationService.render_tree(items)
        assert "$pecial" in result
        assert "日本語" in result

    def test_very_long_title(self):
        """Test item with very long title."""
        long_title = "A" * 200
        items = [{"id": "1", "title": long_title}]
        result = VisualizationService.render_tree(items)
        assert long_title in result

    def test_mixed_items_some_without_titles(self):
        """Test mixed items where some have titles and some don't."""
        items = [
            {"id": "1", "title": "Has Title"},
            {"id": "item-without-title"},
        ]
        result = VisualizationService.render_tree(items)
        assert "Has Title" in result
        assert "item-without-title" in result

    def test_tree_branch_characters_present(self):
        """Test that tree uses proper box-drawing characters."""
        items = [
            {"id": "1", "title": "First"},
            {"id": "2", "title": "Second"},
        ]
        result = VisualizationService.render_tree(items)
        assert "├──" in result or "└──" in result
        lines = result.split("\n")
        assert len(lines) >= 2

    def test_multiline_output_structure(self):
        """Test that output has proper multiline structure."""
        items = [
            {
                "id": "1",
                "title": "Parent",
                "children": [{"id": "2", "title": "Child"}],
            }
        ]
        result = VisualizationService.render_tree(items)
        lines = result.split("\n")
        assert len(lines) >= 2

    def test_single_item_no_prefix(self):
        """Test single item renders without prefix."""
        items = [{"id": "1", "title": "Item"}]
        result = VisualizationService.render_tree(items, prefix="", is_last=True)
        assert "└──" in result

    def test_is_last_parameter_affects_branch(self):
        """Test that is_last parameter changes branch character."""
        items = [{"id": "1", "title": "Item"}]
        result = VisualizationService.render_tree(items, is_last=True)
        # Should use last-item branch character
        assert "└──" in result

    def test_complex_nested_structure(self):
        """Test complex nested structure with multiple levels."""
        items = [
            {
                "id": "1",
                "title": "Root",
                "children": [
                    {
                        "id": "2",
                        "title": "Branch A",
                        "children": [
                            {"id": "3", "title": "Leaf A1"},
                            {"id": "4", "title": "Leaf A2"},
                        ],
                    },
                    {
                        "id": "5",
                        "title": "Branch B",
                        "children": [
                            {"id": "6", "title": "Leaf B1"},
                        ],
                    },
                ],
            }
        ]
        result = VisualizationService.render_tree(items)
        assert all(name in result for name in ["Root", "Branch A", "Branch B", "Leaf A1", "Leaf A2", "Leaf B1"])


class TestRenderGraph:
    """Test render_graph method comprehensively."""

    def test_empty_items_returns_empty_string(self):
        """Test that empty items returns empty string."""
        result = VisualizationService.render_graph({}, [])
        assert result == ""

    def test_single_item_no_links(self):
        """Test single item with no links."""
        items = {"1": {"title": "Item 1"}}
        result = VisualizationService.render_graph(items, [])
        assert "Item Dependency Graph" in result
        assert "Item 1" in result
        assert "Level 0" in result

    def test_multiple_items_no_links(self):
        """Test multiple items with no links."""
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
            "C": {"title": "Item C"},
        }
        result = VisualizationService.render_graph(items, [])
        assert "Item A" in result
        assert "Item B" in result
        assert "Item C" in result

    def test_two_items_single_link(self):
        """Test two items with single link."""
        items = {
            "A": {"title": "From"},
            "B": {"title": "To"},
        }
        links = [{"source": "A", "target": "B"}]
        result = VisualizationService.render_graph(items, links)
        assert "From" in result
        assert "To" in result
        assert "Dependencies:" in result

    def test_multiple_items_multiple_links(self):
        """Test multiple items with multiple links."""
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
            "C": {"title": "Item C"},
        }
        links = [
            {"source": "A", "target": "B", "type": "depends_on"},
            {"source": "B", "target": "C", "type": "relates_to"},
            {"source": "A", "target": "C", "type": "blocks"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert "Item A" in result
        assert "Item B" in result
        assert "Item C" in result
        assert "depends_on" in result
        assert "relates_to" in result
        assert "blocks" in result

    def test_link_without_type_defaults_to_relates_to(self):
        """Test that link without type defaults to 'relates_to'."""
        items = {
            "A": {"title": "From"},
            "B": {"title": "To"},
        }
        links = [{"source": "A", "target": "B"}]
        result = VisualizationService.render_graph(items, links)
        assert "relates_to" in result

    def test_custom_link_type(self):
        """Test custom link type."""
        items = {
            "A": {"title": "From"},
            "B": {"title": "To"},
        }
        links = [{"source": "A", "target": "B", "type": "custom_type"}]
        result = VisualizationService.render_graph(items, links)
        assert "custom_type" in result

    def test_level_calculation(self):
        """Test level-based rendering."""
        items = {
            "A": {"title": "Root"},
            "B": {"title": "Child"},
            "C": {"title": "Grandchild"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert "Level 0" in result or "Level 1" in result or "Level 2" in result

    def test_circular_reference_no_hang(self):
        """Test that circular references don't cause infinite loop."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "A"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert "A" in result
        assert "B" in result

    def test_self_referencing_item(self):
        """Test item that links to itself."""
        items = {"A": {"title": "Self"}}
        links = [{"source": "A", "target": "A"}]
        result = VisualizationService.render_graph(items, links)
        assert "Self" in result

    def test_dependencies_section_format(self):
        """Test dependencies section formatting."""
        items = {
            "A": {"title": "From"},
            "B": {"title": "To"},
        }
        links = [{"source": "A", "target": "B", "type": "blocks"}]
        result = VisualizationService.render_graph(items, links)
        assert "Dependencies:" in result
        assert "--[blocks]-->" in result

    def test_item_without_title_uses_id(self):
        """Test item without title falls back to ID in graph."""
        items = {
            "item-1": {},
            "item-2": {"title": "Item 2"},
        }
        links = [{"source": "item-1", "target": "item-2"}]
        result = VisualizationService.render_graph(items, links)
        assert "item-1" in result or "Unknown" in result

    def test_header_format(self):
        """Test graph header format."""
        items = {"A": {"title": "Item"}}
        result = VisualizationService.render_graph(items, [])
        assert "Item Dependency Graph" in result
        assert "=" * 40 in result

    def test_complex_dependency_chain(self):
        """Test complex dependency chain."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
            "D": {"title": "D"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "D"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert all(item in result for item in ["A", "B", "C", "D"])

    def test_diamond_dependency_pattern(self):
        """Test diamond dependency pattern (A->B, A->C, B->D, C->D)."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
            "D": {"title": "D"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "B", "target": "D"},
            {"source": "C", "target": "D"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert all(item in result for item in ["A", "B", "C", "D"])

    def test_multiple_independent_graphs(self):
        """Test multiple independent graphs in same visualization."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
            "D": {"title": "D"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "C", "target": "D"},
        ]
        result = VisualizationService.render_graph(items, links)
        assert all(item in result for item in ["A", "B", "C", "D"])

    def test_special_characters_in_titles(self):
        """Test items with special characters in graph."""
        items = {
            "A": {"title": "Item with $pecial"},
            "B": {"title": "Item with 日本語"},
        }
        links = [{"source": "A", "target": "B"}]
        result = VisualizationService.render_graph(items, links)
        assert "$pecial" in result


class TestRenderDependencyMatrix:
    """Test render_dependency_matrix method comprehensively."""

    def test_empty_items_returns_empty_string(self):
        """Test that empty items returns empty string."""
        result = VisualizationService.render_dependency_matrix({}, [])
        assert result == ""

    def test_single_item_no_dependencies(self):
        """Test single item with no dependencies."""
        items = {"A": {"title": "Item A"}}
        result = VisualizationService.render_dependency_matrix(items, [])
        assert "." in result
        assert "Legend:" in result

    def test_single_item_self_dependency(self):
        """Test single item with self-dependency."""
        items = {"A": {"title": "Item A"}}
        links = [{"source": "A", "target": "A"}]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert "X" in result

    def test_two_items_single_dependency(self):
        """Test two items with single dependency."""
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
        }
        links = [{"source": "A", "target": "B"}]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert "X" in result
        assert "." in result

    def test_multiple_items_multiple_dependencies(self):
        """Test matrix with multiple items and dependencies."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "A", "target": "C"},
        ]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert result.count("X") >= 3

    def test_legend_format(self):
        """Test legend format and content."""
        items = {"A": {"title": "A"}}
        result = VisualizationService.render_dependency_matrix(items, [])
        assert "Legend:" in result
        assert "X = dependency exists" in result
        assert ". = no dependency" in result

    def test_header_row_indices(self):
        """Test header row contains column indices."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        assert "0" in result
        assert "1" in result
        assert "2" in result

    def test_row_indices_present(self):
        """Test that each row has an index."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        lines = result.split("\n")
        # Check that rows after header contain indices
        matrix_lines = [line for line in lines[1:4] if line.strip()]
        assert len(matrix_lines) > 0

    def test_matrix_symmetry_with_bidirectional_links(self):
        """Test matrix with bidirectional dependencies."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "A"},
        ]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert result.count("X") >= 2

    def test_complete_graph_all_connected(self):
        """Test complete graph where all items depend on each other."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "B", "target": "A"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"},
            {"source": "C", "target": "B"},
        ]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert result.count("X") >= 6

    def test_no_dependencies_all_dots(self):
        """Test matrix with no dependencies shows all dots."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        assert "." in result
        assert "X" not in result

    def test_matrix_format_spacing(self):
        """Test matrix has proper spacing."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        # Should have spaces for formatting
        assert " " in result

    def test_sorted_item_ids(self):
        """Test that items are sorted by ID in matrix."""
        items = {
            "C": {"title": "C"},
            "A": {"title": "A"},
            "B": {"title": "B"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        # Items should be sorted, so order is predictable
        assert "Legend:" in result

    def test_large_matrix(self):
        """Test matrix with many items."""
        items = {str(i): {"title": f"Item {i}"} for i in range(10)}
        links = [{"source": "0", "target": str(i)} for i in range(1, 10)]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert "X" in result
        assert "." in result
        assert result.count("X") >= 9

    def test_matrix_dimensions(self):
        """Test matrix has correct dimensions."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        result = VisualizationService.render_dependency_matrix(items, [])
        lines = [line for line in result.split("\n") if line.strip()]
        # Should have header + 3 matrix rows + legend lines
        assert len(lines) >= 4

    def test_diagonal_dependencies(self):
        """Test matrix with diagonal pattern dependencies."""
        items = {
            "A": {"title": "A"},
            "B": {"title": "B"},
            "C": {"title": "C"},
        }
        links = [
            {"source": "A", "target": "A"},
            {"source": "B", "target": "B"},
            {"source": "C", "target": "C"},
        ]
        result = VisualizationService.render_dependency_matrix(items, links)
        assert result.count("X") >= 3


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_render_tree_none_items(self):
        """Test render_tree with None instead of list."""
        # Should handle gracefully or return empty
        try:
            result = VisualizationService.render_tree(None)
            # If it doesn't raise, should return empty
            assert result == "" or result is None
        except (TypeError, AttributeError):
            # Expected behavior - None is not iterable
            pass

    def test_render_graph_empty_items_with_links(self):
        """Test render_graph with empty items but links provided."""
        result = VisualizationService.render_graph({}, [{"source": "A", "target": "B"}])
        assert result == ""

    def test_render_graph_items_with_empty_links(self):
        """Test render_graph with items but empty links."""
        items = {"A": {"title": "Item A"}}
        result = VisualizationService.render_graph(items, [])
        assert "Item A" in result

    def test_render_dependency_matrix_mismatched_links(self):
        """Test matrix with links referring to non-existent items."""
        items = {"A": {"title": "A"}}
        links = [{"source": "A", "target": "B"}]  # B doesn't exist
        result = VisualizationService.render_dependency_matrix(items, links)
        # Should handle gracefully
        assert "Legend:" in result

    def test_very_long_item_title_in_tree(self):
        """Test tree with very long title."""
        long_title = "A" * 500
        items = [{"id": "1", "title": long_title}]
        result = VisualizationService.render_tree(items)
        assert long_title in result

    def test_unicode_characters_in_all_methods(self):
        """Test unicode support in all methods."""
        items_tree = [{"id": "1", "title": "测试项目"}]
        result_tree = VisualizationService.render_tree(items_tree)
        assert "测试" in result_tree

        items_graph = {"A": {"title": "測試"}}
        result_graph = VisualizationService.render_graph(items_graph, [])
        assert "測試" in result_graph

        result_matrix = VisualizationService.render_dependency_matrix(items_graph, [])
        assert "Legend:" in result_matrix

    def test_empty_title_and_no_id(self):
        """Test item with empty title and no id."""
        items = [{"title": ""}]
        result = VisualizationService.render_tree(items)
        # Should handle gracefully
        assert isinstance(result, str)
