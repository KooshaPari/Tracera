#!/usr/bin/env python3
"""Verify webhook handler extraction."""

import ast


def analyze_file_complexity(file_path: str) -> dict[str, int]:
    """Analyze function complexity in a Python file."""
    with open(file_path) as f:
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
    with open(file_path) as f:
        return len(f.readlines())


def main():
    """Run verification checks."""
    print("=" * 70)
    print("Webhook Handler Extraction Verification")
    print("=" * 70)
    print()

    # Check file size
    webhooks_path = "src/tracertm/api/handlers/webhooks.py"
    line_count = count_lines(webhooks_path)
    print(f"File Size Check:")
    print(f"  Lines: {line_count}")
    print(f"  Target: < 500 lines")
    print(f"  Status: {'✓ PASS' if line_count < 500 else '✗ FAIL'}")
    print()

    # Check complexity
    functions = analyze_file_complexity(webhooks_path)
    print(f"Complexity Analysis:")
    print(f"  Functions analyzed: {len(functions)}")
    print()

    all_pass = True
    for func_name, complexity in sorted(functions.items()):
        status = "✓" if complexity < 7 else "✗"
        if complexity >= 7:
            all_pass = False
        print(f"    {status} {func_name}: {complexity}")

    print()
    max_complexity = max(functions.values()) if functions else 0
    print(f"  Maximum complexity: {max_complexity}")
    print(f"  Target: < 7")
    print(f"  Status: {'✓ PASS' if all_pass else '✗ FAIL'}")
    print()

    # Check integration
    print(f"Integration Check:")
    main_path = "src/tracertm/api/main.py"
    with open(main_path) as f:
        main_content = f.read()

    has_import = "from tracertm.api.handlers.webhooks import github_app_webhook" in main_content
    has_endpoint = "github_app_webhook_endpoint" in main_content

    print(f"  Import in main.py: {'✓ PASS' if has_import else '✗ FAIL'}")
    print(f"  Endpoint wrapper: {'✓ PASS' if has_endpoint else '✗ FAIL'}")
    print()

    # Summary
    print("=" * 70)
    overall_pass = line_count < 500 and all_pass and has_import and has_endpoint
    print(f"Overall Status: {'✓ ALL CHECKS PASSED' if overall_pass else '✗ SOME CHECKS FAILED'}")
    print("=" * 70)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    exit(main())
