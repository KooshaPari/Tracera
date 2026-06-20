#!/usr/bin/env python3
"""Verify webhook handler extraction."""

import ast
import pathlib
import sys


def analyze_file_complexity(file_path: str) -> dict[str, int]:
    """Analyze function complexity in a Python file."""
    with pathlib.Path(file_path).open(encoding="utf-8") as f:
        tree = ast.parse(f.read())

    functions = {}
    for node in tree.body:
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    complexity += 1
            functions[node.name] = complexity

    return functions


def count_lines(file_path: str) -> int:
    """Count lines in a file."""
    with pathlib.Path(file_path).open(encoding="utf-8") as f:
        return len(f.readlines())


def main() -> int:
    """Run verification checks."""
    # Check file size
    webhooks_path = "src/tracertm/api/handlers/webhooks.py"
    line_count = count_lines(webhooks_path)

    # Check complexity
    functions = analyze_file_complexity(webhooks_path)

    all_pass = True
    for _func_name, complexity in sorted(functions.items()):
        if complexity >= 7:
            all_pass = False

    max(functions.values()) if functions else 0

    # Check integration
    main_path = "src/tracertm/api/main.py"
    main_content = pathlib.Path(main_path).read_text(encoding="utf-8")

    has_import = "from tracertm.api.handlers.webhooks import github_app_webhook" in main_content
    has_endpoint = "github_app_webhook_endpoint" in main_content

    # Summary
    overall_pass = line_count < 500 and all_pass and has_import and has_endpoint

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
