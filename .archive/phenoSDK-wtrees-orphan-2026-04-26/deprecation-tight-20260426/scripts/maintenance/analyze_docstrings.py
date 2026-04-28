#!/usr/bin/env python3
"""Analyze docstring coverage across the codebase."""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class DocstringStats:
    """Statistics for a single file."""

    file_path: str
    total_functions: int = 0
    total_classes: int = 0
    total_methods: int = 0
    total_modules: int = 0
    missing_functions: List[str] = field(default_factory=list)
    missing_classes: List[str] = field(default_factory=list)
    missing_methods: List[str] = field(default_factory=list)
    missing_module: bool = False
    incomplete_docstrings: List[Tuple[str, str, List[str]]] = field(default_factory=list)
    oneliner_docstrings: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total items to document."""
        return (self.total_functions + self.total_classes +
                self.total_methods + self.total_modules)

    @property
    def missing(self) -> int:
        """Total missing docstrings."""
        return (len(self.missing_functions) + len(self.missing_classes) +
                len(self.missing_methods) + (1 if self.missing_module else 0))

    @property
    def coverage(self) -> float:
        """Coverage percentage."""
        if self.total == 0:
            return 100.0
        return ((self.total - self.missing) / self.total) * 100


class DocstringAnalyzer(ast.NodeVisitor):
    """Analyzes AST for docstring coverage."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.stats = DocstringStats(file_path=file_path)
        self.current_class = None

    def has_docstring(self, node) -> bool:
        """Check if node has a docstring."""
        return (ast.get_docstring(node) is not None and
                ast.get_docstring(node).strip() != "")

    def get_docstring(self, node) -> str:
        """Get docstring from node."""
        return ast.get_docstring(node) or ""

    def is_oneliner(self, docstring: str) -> bool:
        """Check if docstring is a single line (should be Google-style)."""
        if not docstring:
            return False
        lines = [line for line in docstring.split('\n') if line.strip()]
        # One-liner if only one line and doesn't have sections
        if len(lines) == 1:
            return True
        # Check if it has Google-style sections
        has_sections = any(
            keyword in docstring
            for keyword in ['Args:', 'Returns:', 'Raises:', 'Yields:', 'Example:', 'Note:']
        )
        return len(lines) <= 3 and not has_sections

    def is_incomplete(self, node, docstring: str) -> List[str]:
        """Check if docstring is missing expected sections."""
        missing_sections = []

        # Check for Args section if function has parameters
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Count non-self/cls parameters
            params = [arg.arg for arg in node.args.args
                     if arg.arg not in ('self', 'cls')]
            if params and 'Args:' not in docstring:
                missing_sections.append('Args')

            # Check for Returns section if function returns something
            has_return = any(
                isinstance(n, ast.Return) and n.value is not None
                for n in ast.walk(node)
            )
            if has_return and 'Returns:' not in docstring and node.name != '__init__':
                missing_sections.append('Returns')

            # Check for Raises section if function raises exceptions
            has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(node))
            if has_raise and 'Raises:' not in docstring:
                missing_sections.append('Raises')

        return missing_sections

    def visit_Module(self, node):
        """Visit module."""
        self.stats.total_modules = 1
        if not self.has_docstring(node):
            self.stats.missing_module = True
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definition."""
        self.stats.total_classes += 1

        if not self.has_docstring(node):
            self.stats.missing_classes.append(node.name)
        else:
            docstring = self.get_docstring(node)
            if self.is_oneliner(docstring):
                self.stats.oneliner_docstrings.append((f"class {node.name}", docstring))

            missing_sections = self.is_incomplete(node, docstring)
            if missing_sections:
                self.stats.incomplete_docstrings.append(
                    (f"class {node.name}", "class", missing_sections)
                )

        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self._visit_function(node)

    def _visit_function(self, node):
        """Common logic for function/async function."""
        # Skip private functions starting with _
        if node.name.startswith('_') and not node.name.startswith('__'):
            self.generic_visit(node)
            return

        if self.current_class:
            # It's a method
            self.stats.total_methods += 1
            if not self.has_docstring(node):
                self.stats.missing_methods.append(f"{self.current_class}.{node.name}")
            else:
                docstring = self.get_docstring(node)
                if self.is_oneliner(docstring) and node.name != '__init__':
                    self.stats.oneliner_docstrings.append(
                        (f"{self.current_class}.{node.name}", docstring)
                    )

                missing_sections = self.is_incomplete(node, docstring)
                if missing_sections:
                    self.stats.incomplete_docstrings.append(
                        (f"{self.current_class}.{node.name}", "method", missing_sections)
                    )
        else:
            # It's a function
            self.stats.total_functions += 1
            if not self.has_docstring(node):
                self.stats.missing_functions.append(node.name)
            else:
                docstring = self.get_docstring(node)
                if self.is_oneliner(docstring):
                    self.stats.oneliner_docstrings.append((node.name, docstring))

                missing_sections = self.is_incomplete(node, docstring)
                if missing_sections:
                    self.stats.incomplete_docstrings.append(
                        (node.name, "function", missing_sections)
                    )

        self.generic_visit(node)


def analyze_file(file_path: Path) -> DocstringStats:
    """Analyze a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        analyzer = DocstringAnalyzer(str(file_path))
        analyzer.visit(tree)
        return analyzer.stats
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return DocstringStats(file_path=str(file_path))


def analyze_directory(directory: Path) -> Dict[str, DocstringStats]:
    """Analyze all Python files in directory."""
    results = {}

    for py_file in directory.rglob('*.py'):
        # Skip __pycache__ and .venv
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue

        stats = analyze_file(py_file)
        if stats.total > 0:  # Only include files with documentable items
            results[str(py_file)] = stats

    return results


def main():
    """Run analysis."""
    src_path = Path('src')

    print("Analyzing docstring coverage...")
    results = analyze_directory(src_path)

    # Aggregate statistics
    total_items = sum(stats.total for stats in results.values())
    total_missing = sum(stats.missing for stats in results.values())
    total_functions = sum(stats.total_functions for stats in results.values())
    total_classes = sum(stats.total_classes for stats in results.values())
    total_methods = sum(stats.total_methods for stats in results.values())
    total_modules = sum(stats.total_modules for stats in results.values())
    missing_functions = sum(len(stats.missing_functions) for stats in results.values())
    missing_classes = sum(len(stats.missing_classes) for stats in results.values())
    missing_methods = sum(len(stats.missing_methods) for stats in results.values())
    missing_modules = sum(1 if stats.missing_module else 0 for stats in results.values())
    total_incomplete = sum(len(stats.incomplete_docstrings) for stats in results.values())
    total_oneliners = sum(len(stats.oneliner_docstrings) for stats in results.values())

    coverage = ((total_items - total_missing) / total_items * 100) if total_items > 0 else 0

    print(f"\n{'='*80}")
    print(f"DOCSTRING COVERAGE SUMMARY")
    print(f"{'='*80}")
    print(f"Total items:      {total_items:,}")
    print(f"Missing:          {total_missing:,} ({100-coverage:.1f}%)")
    print(f"Coverage:         {coverage:.1f}%")
    print(f"\nBreakdown:")
    print(f"  Modules:        {total_modules - missing_modules}/{total_modules} " +
          f"({missing_modules} missing)")
    print(f"  Functions:      {total_functions - missing_functions}/{total_functions} " +
          f"({missing_functions} missing)")
    print(f"  Classes:        {total_classes - missing_classes}/{total_classes} " +
          f"({missing_classes} missing)")
    print(f"  Methods:        {total_methods - missing_methods}/{total_methods} " +
          f"({missing_methods} missing)")
    print(f"\nQuality Issues:")
    print(f"  Incomplete:     {total_incomplete} (missing Args/Returns/Raises)")
    print(f"  One-liners:     {total_oneliners} (should be Google-style)")

    # Sort files by coverage (worst first)
    sorted_files = sorted(results.items(), key=lambda x: (x[1].coverage, x[0]))

    print(f"\n{'='*80}")
    print(f"WORST COVERAGE (Bottom 30 files)")
    print(f"{'='*80}")
    print(f"{'File':<60} {'Coverage':>10} {'Missing':>8}")
    print(f"{'-'*80}")

    for file_path, stats in sorted_files[:30]:
        rel_path = file_path.replace('/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/', '')
        if len(rel_path) > 58:
            rel_path = '...' + rel_path[-55:]
        print(f"{rel_path:<60} {stats.coverage:>9.1f}% {stats.missing:>8}")

    # Group by layer
    print(f"\n{'='*80}")
    print(f"COVERAGE BY LAYER")
    print(f"{'='*80}")

    layers = {
        'Domain': [],
        'Application': [],
        'Adapters': [],
        'Infrastructure': [],
        'SDK Interface': [],
        'Tests': []
    }

    for file_path, stats in results.items():
        if '/pheno/domain/' in file_path:
            layers['Domain'].append(stats)
        elif '/pheno/application/' in file_path:
            layers['Application'].append(stats)
        elif '/pheno/adapters/' in file_path:
            layers['Adapters'].append(stats)
        elif '/pheno/infrastructure/' in file_path or '/pheno/infra/' in file_path:
            layers['Infrastructure'].append(stats)
        elif '/pheno_sdk/' in file_path:
            layers['SDK Interface'].append(stats)
        elif '/tests/' in file_path:
            layers['Tests'].append(stats)

    for layer_name, layer_stats in layers.items():
        if not layer_stats:
            continue

        layer_total = sum(s.total for s in layer_stats)
        layer_missing = sum(s.missing for s in layer_stats)
        layer_coverage = ((layer_total - layer_missing) / layer_total * 100) if layer_total > 0 else 0

        print(f"\n{layer_name}:")
        print(f"  Files:          {len(layer_stats)}")
        print(f"  Items:          {layer_total:,}")
        print(f"  Missing:        {layer_missing} ({100-layer_coverage:.1f}%)")
        print(f"  Coverage:       {layer_coverage:.1f}%")

    # Generate detailed file list
    print(f"\n{'='*80}")
    print(f"DETAILED BREAKDOWN")
    print(f"{'='*80}")

    output_file = Path('DOCSTRING_ANALYSIS_DETAILS.txt')
    with open(output_file, 'w') as f:
        f.write("DETAILED DOCSTRING COVERAGE ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        for file_path, stats in sorted_files:
            rel_path = file_path.replace('/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/', '')

            f.write(f"\nFile: {rel_path}\n")
            f.write(f"Coverage: {stats.coverage:.1f}% ({stats.total - stats.missing}/{stats.total})\n")

            if stats.missing_module:
                f.write(f"  - Missing module docstring\n")

            if stats.missing_functions:
                f.write(f"  Missing functions ({len(stats.missing_functions)}):\n")
                for func in stats.missing_functions:
                    f.write(f"    - {func}\n")

            if stats.missing_classes:
                f.write(f"  Missing classes ({len(stats.missing_classes)}):\n")
                for cls in stats.missing_classes:
                    f.write(f"    - {cls}\n")

            if stats.missing_methods:
                f.write(f"  Missing methods ({len(stats.missing_methods)}):\n")
                for method in stats.missing_methods:
                    f.write(f"    - {method}\n")

            if stats.incomplete_docstrings:
                f.write(f"  Incomplete docstrings ({len(stats.incomplete_docstrings)}):\n")
                for name, item_type, missing_sections in stats.incomplete_docstrings:
                    f.write(f"    - {name} (missing: {', '.join(missing_sections)})\n")

            if stats.oneliner_docstrings:
                f.write(f"  One-liner docstrings ({len(stats.oneliner_docstrings)}):\n")
                for name, docstring in stats.oneliner_docstrings[:3]:  # Show first 3
                    f.write(f"    - {name}: \"{docstring[:60]}...\"\n")
                if len(stats.oneliner_docstrings) > 3:
                    f.write(f"    ... and {len(stats.oneliner_docstrings) - 3} more\n")

    print(f"\nDetailed analysis written to: {output_file}")

    # Estimate effort
    print(f"\n{'='*80}")
    print(f"EFFORT ESTIMATION")
    print(f"{'='*80}")

    # Rough estimates:
    # - Module docstring: 15 min
    # - Function docstring: 10 min
    # - Class docstring: 15 min
    # - Method docstring: 10 min
    # - Enhance incomplete: 5 min
    # - Convert one-liner: 10 min

    effort_hours = (
        (missing_modules * 15) +
        (missing_functions * 10) +
        (missing_classes * 15) +
        (missing_methods * 10) +
        (total_incomplete * 5) +
        (total_oneliners * 10)
    ) / 60

    print(f"Add missing docstrings:     {missing_modules + missing_functions + missing_classes + missing_methods:,} items")
    print(f"Enhance incomplete:         {total_incomplete:,} items")
    print(f"Convert one-liners:         {total_oneliners:,} items")
    print(f"\nEstimated effort:           {effort_hours:.1f} hours ({effort_hours/8:.1f} days)")
    print(f"With 2 people:              {effort_hours/16:.1f} days")
    print(f"With automation:            {effort_hours/4:.1f} hours (75% reduction)")


if __name__ == '__main__':
    main()
