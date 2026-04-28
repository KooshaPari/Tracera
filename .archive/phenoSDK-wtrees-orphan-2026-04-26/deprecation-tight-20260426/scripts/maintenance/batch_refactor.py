#!/usr/bin/env python3
"""Batch refactoring for parameter consolidation."""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParameterGroup:
    """Group of related parameters."""

    names: list[str]
    types: list[str]
    defaults: list[str]


def extract_parameter_dataclass(
    func_name: str, params: ParameterGroup, config_name: str
) -> str:
    """Generate a dataclass for function parameters."""
    lines = [f"@dataclass", f"class {config_name}:"]

    for name, type_hint, default in zip(params.names, params.types, params.defaults):
        if default:
            lines.append(f"    {name}: {type_hint} = {default}")
        else:
            lines.append(f"    {name}: {type_hint}")

    return "\n".join(lines)


def refactor_high_param_function(filepath: Path, function_name: str, target_params: int = 5):
    """Refactor a function with too many parameters."""
    print(f"Refactoring {filepath}::{function_name}")

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=str(filepath))

        # Find the function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                param_count = len(node.args.args) + len(node.args.kwonlyargs)

                if param_count > target_params:
                    print(f"  Found {param_count} parameters - needs refactoring")

                    # Extract parameter info
                    params = ParameterGroup(
                        names=[arg.arg for arg in node.args.args[1:]],  # Skip 'self'
                        types=["Any"] * (param_count - 1),
                        defaults=["None"] * (param_count - 1),
                    )

                    config_class = extract_parameter_dataclass(
                        function_name,
                        params,
                        f"{function_name.title().replace('_', '')}Config",
                    )

                    print("  Generated config class:")
                    print("  " + config_class.replace("\n", "\n  "))
                    return config_class

    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)

    return None


def main():
    """Main batch refactoring."""
    # Priority refactorings
    targets = [
        ("src/pheno/core/shared/scheduler/decorators.py", "cron_job"),
        ("src/pheno/observability/runtime_metrics/collector.py", "record_model_performance"),
        ("src/pheno/exceptions/base.py", "__init__"),
        ("src/pheno/cli/audit.py", "log_command"),
    ]

    print("=" * 80)
    print("BATCH PARAMETER CONSOLIDATION REFACTORING")
    print("=" * 80)
    print()

    for filepath, func_name in targets:
        path = Path(filepath)
        if path.exists():
            refactor_high_param_function(path, func_name)
            print()
        else:
            print(f"File not found: {filepath}")
            print()


if __name__ == "__main__":
    main()
