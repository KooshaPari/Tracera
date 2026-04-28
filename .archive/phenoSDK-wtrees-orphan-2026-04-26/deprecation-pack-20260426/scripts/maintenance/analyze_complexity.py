#!/usr/bin/env python3
"""Analyze code complexity and identify refactoring targets."""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class FunctionInfo:
    """Function analysis information."""

    name: str
    file: str
    line: int
    params: int
    returns: int
    complexity: int
    loc: int


@dataclass
class CodeDuplicate:
    """Duplicate code block information."""

    pattern: str
    locations: List[str]
    lines: int


class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyze Python code for complexity metrics."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.functions: List[FunctionInfo] = []
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        params = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            params += 1
        if node.args.kwarg:
            params += 1

        # Count return statements
        returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))

        # Estimate cyclomatic complexity
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        # Count lines of code
        loc = node.end_lineno - node.lineno + 1 if node.end_lineno else 1

        func_info = FunctionInfo(
            name=node.name,
            file=self.filepath,
            line=node.lineno,
            params=params,
            returns=returns,
            complexity=complexity,
            loc=loc
        )
        self.functions.append(func_info)

        self.generic_visit(node)


def analyze_file(filepath: Path) -> List[FunctionInfo]:
    """Analyze a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        analyzer = ComplexityAnalyzer(str(filepath))
        analyzer.visit(tree)
        return analyzer.functions
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return []


def main():
    """Main analysis function."""
    src_path = Path("src")
    all_functions: List[FunctionInfo] = []

    # Analyze all Python files
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        functions = analyze_file(py_file)
        all_functions.extend(functions)

    # Find high-parameter functions (>5 params)
    high_param_funcs = [f for f in all_functions if f.params > 5]

    # Find high-return functions (>10 returns)
    high_return_funcs = [f for f in all_functions if f.returns > 10]

    # Find high-complexity functions (complexity > 10)
    high_complexity_funcs = [f for f in all_functions if f.complexity > 10]

    # Find long functions (>100 LOC)
    long_funcs = [f for f in all_functions if f.loc > 100]

    print("=" * 80)
    print("COMPLEXITY ANALYSIS REPORT")
    print("=" * 80)
    print()

    print(f"Total functions analyzed: {len(all_functions)}")
    print()

    print(f"HIGH PARAMETER COUNT (>5 parameters): {len(high_param_funcs)}")
    print("-" * 80)
    for func in sorted(high_param_funcs, key=lambda x: x.params, reverse=True)[:20]:
        print(f"  {func.params:2d} params | {func.file}:{func.line} | {func.name}")
    print()

    print(f"HIGH RETURN COUNT (>10 returns): {len(high_return_funcs)}")
    print("-" * 80)
    for func in sorted(high_return_funcs, key=lambda x: x.returns, reverse=True)[:20]:
        print(f"  {func.returns:2d} returns | {func.file}:{func.line} | {func.name}")
    print()

    print(f"HIGH COMPLEXITY (>10): {len(high_complexity_funcs)}")
    print("-" * 80)
    for func in sorted(high_complexity_funcs, key=lambda x: x.complexity, reverse=True)[:30]:
        print(f"  CC={func.complexity:2d} | {func.file}:{func.line} | {func.name}")
    print()

    print(f"LONG FUNCTIONS (>100 LOC): {len(long_funcs)}")
    print("-" * 80)
    for func in sorted(long_funcs, key=lambda x: x.loc, reverse=True)[:20]:
        print(f"  {func.loc:3d} LOC | {func.file}:{func.line} | {func.name}")
    print()

    # Summary statistics
    total_issues = len(set(
        [f.name for f in high_param_funcs] +
        [f.name for f in high_return_funcs] +
        [f.name for f in high_complexity_funcs] +
        [f.name for f in long_funcs]
    ))

    print("=" * 80)
    print(f"TOTAL FUNCTIONS NEEDING REFACTORING: {total_issues}")
    print("=" * 80)


if __name__ == "__main__":
    main()
