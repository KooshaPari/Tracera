"""
TreeView Widget - Hierarchical data visualization.

Provides expandable tree structure for displaying hierarchical data.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    from rich.text import Text
    from textual.app import ComposeResult
    from textual.reactive import reactive
    from textual.widgets import Static
    from textual.widgets import Tree as TextualTree
    from textual.widgets.tree import TreeNode as TextualTreeNode

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    TextualTree = object
    TextualTreeNode = object
    def reactive(x):
        return x
    ComposeResult = object
    Text = object


@dataclass
class TreeNode:
    """
    Tree node data structure.
    """

    label: str
    value: Any = None
    children: list["TreeNode"] = field(default_factory=list)
    expanded: bool = False
    icon: str = "📄"
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: "TreeNode") -> "TreeNode":
        """
        Add a child node.
        """
        self.children.append(child)
        return child

    def find_node(self, label: str) -> Optional["TreeNode"]:
        """
        Find a node by label (recursive).
        """
        if self.label == label:
            return self

        for child in self.children:
            result = child.find_node(label)
            if result:
                return result

        return None

    def get_path(self, path: list[str]) -> Optional["TreeNode"]:
        """
        Get node at path.
        """
        if not path:
            return self

        if path[0] != self.label:
            return None

        if len(path) == 1:
            return self

        # Search children
        for child in self.children:
            if child.label == path[1]:
                return child.get_path(path[1:])

        return None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "label": self.label,
            "value": self.value,
            "icon": self.icon,
            "expanded": self.expanded,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TreeNode":
        """
        Create from dictionary.
        """
        node = cls(
            label=data["label"],
            value=data.get("value"),
            icon=data.get("icon", "📄"),
            expanded=data.get("expanded", False),
            metadata=data.get("metadata", {}),
        )

        for child_data in data.get("children", []):
            node.add_child(cls.from_dict(child_data))

        return node


class TreeView(Static):
    """Hierarchical tree view widget.

    Features:
    - Expandable/collapsible nodes
    - Custom icons
    - Node selection
    - Search/filter
    - Lazy loading support
    """

    selected_path = reactive("")

    def __init__(
        self,
        root: TreeNode | None = None,
        show_root: bool = True,
        auto_expand: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.root = root or TreeNode(label="Root", icon="📁")
        self.show_root = show_root
        self.auto_expand = auto_expand
        self._selection_callbacks: list[Callable[[TreeNode], None]] = []
        self._textual_tree: TextualTree | None = None

    def compose(self) -> ComposeResult:
        """
        Create tree widget.
        """
        tree = TextualTree(self.root.label if self.show_root else "")
        tree.show_root = self.show_root
        self._textual_tree = tree
        yield tree

        # Build tree structure
        self._build_tree()

    def _build_tree(self) -> None:
        """
        Build the tree structure from root node.
        """
        if not self._textual_tree:
            return

        tree = self._textual_tree

        if self.show_root:
            root_textual = tree.root
            self._add_children(root_textual, self.root)
        else:
            # Add root children as top-level nodes
            for child in self.root.children:
                child_node = tree.root.add(child.label, expand=child.expanded or self.auto_expand)
                child_node.data = child
                self._add_children(child_node, child)

    def _add_children(self, parent_textual: TextualTreeNode, parent_data: TreeNode) -> None:
        """
        Recursively add children to tree.
        """
        for child in parent_data.children:
            label = f"{child.icon} {child.label}" if child.icon else child.label
            child_node = parent_textual.add(label, expand=child.expanded or self.auto_expand)
            child_node.data = child

            if child.children:
                self._add_children(child_node, child)

    def add_node(self, path: list[str], node: TreeNode) -> bool:
        """
        Add a node at the specified path.
        """
        parent = self.root.get_path(path)

        if not parent:
            return False

        parent.add_child(node)

        # Update UI if mounted
        if self._textual_tree:
            self._build_tree()

        return True

    def remove_node(self, path: list[str]) -> bool:
        """
        Remove a node at the specified path.
        """
        if len(path) < 2:
            return False

        parent = self.root.get_path(path[:-1])
        if not parent:
            return False

        # Remove from children
        parent.children = [c for c in parent.children if c.label != path[-1]]

        # Update UI
        if self._textual_tree:
            self._build_tree()

        return True

    def update_node(self, path: list[str], **kwargs) -> bool:
        """
        Update node properties.
        """
        node = self.root.get_path(path)
        if not node:
            return False

        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)

        # Update UI
        if self._textual_tree:
            self._build_tree()

        return True

    def expand_path(self, path: list[str]) -> bool:
        """
        Expand nodes along a path.
        """
        node = self.root.get_path(path)
        if not node:
            return False

        # Mark all nodes in path as expanded
        current = self.root
        for label in path:
            if current.label == label:
                current.expanded = True
                for child in current.children:
                    if child.label in path:
                        current = child
                        break

        # Update UI
        if self._textual_tree:
            self._build_tree()

        return True

    def collapse_path(self, path: list[str]) -> bool:
        """
        Collapse a node.
        """
        node = self.root.get_path(path)
        if not node:
            return False

        node.expanded = False

        # Update UI
        if self._textual_tree:
            self._build_tree()

        return True

    def find_nodes(self, predicate: Callable[[TreeNode], bool]) -> list[TreeNode]:
        """
        Find all nodes matching a predicate.
        """
        results = []

        def search(node: TreeNode):
            if predicate(node):
                results.append(node)
            for child in node.children:
                search(child)

        search(self.root)
        return results

    def get_selected_node(self) -> TreeNode | None:
        """
        Get currently selected node.
        """
        if not self.selected_path:
            return None

        path = self.selected_path.split("/")
        return self.root.get_path(path)

    def on_tree_node_selected(self, event) -> None:
        """
        Handle node selection.
        """
        if hasattr(event.node, "data"):
            node_data = event.node.data
            if isinstance(node_data, TreeNode):
                # Update selected path
                self.selected_path = node_data.label

                # Notify callbacks
                for callback in self._selection_callbacks:
                    try:
                        callback(node_data)
                    except Exception as e:
                        print(f"Selection callback error: {e}")

    def add_selection_callback(self, callback: Callable[[TreeNode], None]) -> None:
        """
        Add callback for node selection.
        """
        self._selection_callbacks.append(callback)

    def export_to_dict(self) -> dict[str, Any]:
        """
        Export tree to dictionary.
        """
        return self.root.to_dict()

    def import_from_dict(self, data: dict[str, Any]) -> None:
        """
        Import tree from dictionary.
        """
        self.root = TreeNode.from_dict(data)

        if self._textual_tree:
            self._build_tree()
