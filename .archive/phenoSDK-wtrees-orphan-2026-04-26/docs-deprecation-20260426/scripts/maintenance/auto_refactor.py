#!/usr/bin/env python3
"""Automated code complexity reduction tool."""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RefactoringAction:
    """A single refactoring action."""

    file: Path
    line: int
    action_type: str
    description: str
    suggestion: str


class ComplexityReducer(ast.NodeTransformer):
    """AST transformer for reducing complexity."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.actions: list[RefactoringAction] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Visit function definition and suggest refactorings."""
        # Count parameters
        param_count = (
            len(node.args.args)
            + len(node.args.kwonlyargs)
            + (1 if node.args.vararg else 0)
            + (1 if node.args.kwarg else 0)
        )

        if param_count > 5:
            self.actions.append(
                RefactoringAction(
                    file=self.filepath,
                    line=node.lineno,
                    action_type="extract_parameter_object",
                    description=f"Function '{node.name}' has {param_count} parameters",
                    suggestion=f"Create a dataclass/TypedDict for {node.name}Config",
                )
            )

        # Count return statements
        return_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
        if return_count > 10:
            self.actions.append(
                RefactoringAction(
                    file=self.filepath,
                    line=node.lineno,
                    action_type="extract_return_object",
                    description=f"Function '{node.name}' has {return_count} return statements",
                    suggestion="Use named tuple or dataclass for return value",
                )
            )

        # Estimate complexity
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        if complexity > 10:
            self.actions.append(
                RefactoringAction(
                    file=self.filepath,
                    line=node.lineno,
                    action_type="extract_helper_methods",
                    description=f"Function '{node.name}' has complexity {complexity}",
                    suggestion="Extract helper methods for each logical section",
                )
            )

        # Check LOC
        loc = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
        if loc > 100:
            self.actions.append(
                RefactoringAction(
                    file=self.filepath,
                    line=node.lineno,
                    action_type="split_function",
                    description=f"Function '{node.name}' has {loc} lines",
                    suggestion="Split into smaller functions (target <50 LOC each)",
                )
            )

        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Check for magic numbers and strings."""
        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, (int, float)):
                if node.value.value not in (0, 1, -1, 2):  # Allow common values
                    self.actions.append(
                        RefactoringAction(
                            file=self.filepath,
                            line=node.lineno,
                            action_type="extract_constant",
                            description=f"Magic number: {node.value.value}",
                            suggestion="Extract to named constant",
                        )
                    )
            elif isinstance(node.value.value, str) and len(node.value.value) > 20:
                self.actions.append(
                    RefactoringAction(
                        file=self.filepath,
                        line=node.lineno,
                        action_type="extract_constant",
                        description=f"Magic string: {node.value.value[:50]}...",
                        suggestion="Extract to named constant",
                    )
                )

        return self.generic_visit(node)


def analyze_file_for_refactoring(filepath: Path) -> list[RefactoringAction]:
    """Analyze file and suggest refactorings."""
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        reducer = ComplexityReducer(filepath)
        reducer.visit(tree)
        return reducer.actions
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return []


def main():
    """Main refactoring analysis."""
    src_path = Path("src")
    all_actions: list[RefactoringAction] = []

    # Analyze all Python files
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        actions = analyze_file_for_refactoring(py_file)
        all_actions.extend(actions)

    # Group actions by type
    actions_by_type: dict[str, list[RefactoringAction]] = {}
    for action in all_actions:
        if action.action_type not in actions_by_type:
            actions_by_type[action.action_type] = []
        actions_by_type[action.action_type].append(action)

    print("=" * 80)
    print("AUTOMATED REFACTORING SUGGESTIONS")
    print("=" * 80)
    print()

    for action_type, actions in sorted(actions_by_type.items()):
        print(f"{action_type.upper().replace('_', ' ')}: {len(actions)} instances")
        print("-" * 80)
        for action in actions[:10]:  # Show top 10
            print(f"  {action.file}:{action.line}")
            print(f"    {action.description}")
            print(f"    → {action.suggestion}")
            print()

    print("=" * 80)
    print(f"TOTAL REFACTORING ACTIONS: {len(all_actions)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
