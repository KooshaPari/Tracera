"""Command-line Interface for Hexagonal Refactoring Tools.

This module provides a CLI for analyzing, extracting, and validating hexagonal
architecture patterns in Python codebases.
"""

import asyncio
import json
import logging
from pathlib import Path

import click

from .analyzer import (
    CodeAnalyzer,
    detect_large_files,
    detect_violations,
)
from .extractor import (
    ClassExtractor,
    ConcernExtractor,
    LayerExtractor,
    PatternExtractor,
)
from .validator import (
    validate_dependencies,
    validate_layers,
    validate_port_adapter,
)

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
def cli(verbose: bool, quiet: bool) -> None:
    """
    Hexagonal Architecture Refactoring Tools.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.group()
def analyze() -> None:
    """
    Analyze code for refactoring opportunities.
    """


@analyze.command("file")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "html"]),
    default="text",
    help="Output format",
)
@click.option(
    "--threshold", "-t", type=int, default=500, help="Lines of code threshold for large files",
)
def analyze_file(file_path: str, output: str, threshold: int) -> None:
    """
    Analyze a single file for metrics and violations.
    """
    file = Path(file_path)
    analyzer = CodeAnalyzer(size_threshold=threshold)

    async def run_analysis() -> None:
        result = await analyzer.analyze_file(file)

        if output == "json":
            data = {
                "file": result.file_path,
                "metrics": {
                    "lines_of_code": result.metrics.lines_of_code,
                    "cyclomatic_complexity": result.metrics.cyclomatic_complexity,
                    "cognitive_complexity": result.metrics.cognitive_complexity,
                    "class_count": result.metrics.class_count,
                    "function_count": result.metrics.function_count,
                    "needs_refactoring": result.metrics.needs_refactoring,
                },
                "violations": [
                    {
                        "type": v.violation_type,
                        "severity": v.severity,
                        "line": v.line_number,
                        "message": v.message,
                        "fix": v.suggested_fix,
                    }
                    for v in result.violations
                ],
                "suggestions": result.refactoring_suggestions,
                "priority": result.priority,
            }
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Analysis: {result.file_path}")
            click.echo(f"{'=' * 80}\n")

            click.echo("Metrics:")
            click.echo(f"  Lines of Code: {result.metrics.lines_of_code}")
            click.echo(f"  Cyclomatic Complexity: {result.metrics.cyclomatic_complexity}")
            click.echo(f"  Cognitive Complexity: {result.metrics.cognitive_complexity}")
            click.echo(f"  Classes: {result.metrics.class_count}")
            click.echo(f"  Functions: {result.metrics.function_count}")
            click.echo(f"  Needs Refactoring: {result.metrics.needs_refactoring}")

            if result.violations:
                click.echo(f"\nViolations ({len(result.violations)}):")
                for v in result.violations:
                    click.echo(f"  [{v.severity.upper()}] Line {v.line_number}: {v.message}")
                    if v.suggested_fix:
                        click.echo(f"    → {v.suggested_fix}")

            if result.refactoring_suggestions:
                click.echo("\nSuggestions:")
                for s in result.refactoring_suggestions:
                    click.echo(f"  • {s}")

            click.echo(f"\nPriority: {result.priority.upper()}")

    asyncio.run(run_analysis())


@analyze.command("directory")
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "html"]),
    default="text",
    help="Output format",
)
@click.option("--exclude", "-e", multiple=True, help="Patterns to exclude from analysis")
@click.option("--threshold", "-t", type=int, default=500, help="Lines of code threshold")
def analyze_directory(directory: str, output: str, exclude: tuple, threshold: int) -> None:
    """
    Analyze all Python files in a directory.
    """
    dir_path = Path(directory)
    exclude_patterns = list(exclude) or ["test_", "__pycache__", ".git"]

    async def run_analysis() -> None:
        # Detect large files
        large_files = await detect_large_files(dir_path, threshold, exclude_patterns)

        # Detect violations
        violations = await detect_violations(dir_path, exclude_patterns)

        if output == "json":
            data = {
                "directory": str(dir_path),
                "large_files": [{"file": str(f), "lines": loc} for f, loc in large_files],
                "violations": [
                    {
                        "file": v.file_path,
                        "line": v.line_number,
                        "type": v.violation_type,
                        "severity": v.severity,
                        "message": v.message,
                    }
                    for v in violations
                ],
            }
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Directory Analysis: {dir_path}")
            click.echo(f"{'=' * 80}\n")

            if large_files:
                click.echo(f"Large Files (>{threshold} LOC):")
                for file, loc in large_files[:10]:
                    click.echo(f"  {loc:5d} LOC: {file.relative_to(dir_path)}")
                if len(large_files) > 10:
                    click.echo(f"  ... and {len(large_files) - 10} more")

            if violations:
                click.echo("\nViolations by Severity:")
                by_severity = {}
                for v in violations:
                    by_severity.setdefault(v.severity, []).append(v)

                for severity in ["critical", "high", "medium", "low"]:
                    if severity in by_severity:
                        click.echo(f"  {severity.upper()}: {len(by_severity[severity])}")

                click.echo("\nTop 10 Critical Issues:")
                for v in violations[:10]:
                    rel_path = (
                        Path(v.file_path).relative_to(dir_path)
                        if dir_path in Path(v.file_path).parents
                        else v.file_path
                    )
                    click.echo(f"  [{v.severity.upper()}] {rel_path}:{v.line_number}")
                    click.echo(f"    {v.message}")

    asyncio.run(run_analysis())


@cli.group()
def extract() -> None:
    """
    Extract code components for refactoring.
    """


@extract.command("class")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("class_name")
@click.option("--target", "-t", type=click.Path(), help="Target file path for extracted class")
@click.option("--dry-run", is_flag=True, help="Show what would be extracted without writing files")
def extract_class(file_path: str, class_name: str, target: str | None, dry_run: bool) -> None:
    """
    Extract a class to a separate file.
    """
    file = Path(file_path)
    target_file = Path(target) if target else None

    async def run_extraction() -> None:
        extractor = ClassExtractor()
        result = await extractor.extract_class(file, class_name, target_file)

        if not result.success:
            click.echo(f"Error: {result.error}", err=True)
            return

        click.echo("\nExtraction Result:")
        click.echo(f"  Source: {result.source_file}")
        click.echo(f"  Target: {result.target_file}")
        click.echo(f"  Dependencies: {len(result.dependencies)}")

        if dry_run:
            click.echo("\n--- Extracted Code Preview ---")
            click.echo(result.extracted_code[:500])
            if len(result.extracted_code) > 500:
                click.echo("... (truncated)")
        else:
            # Write extracted code
            Path(result.target_file).write_text(result.extracted_code)
            # Update source file
            Path(result.source_file).write_text(result.remaining_code)
            click.echo("\n✓ Extraction completed successfully")

    asyncio.run(run_extraction())


@extract.command("concern")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("concern")
@click.option(
    "--target-dir", "-d", type=click.Path(), help="Target directory for extracted concern",
)
@click.option("--dry-run", is_flag=True, help="Show what would be extracted without writing files")
def extract_concern(file_path: str, concern: str, target_dir: str | None, dry_run: bool) -> None:
    """
    Extract code by functional concern.
    """
    file = Path(file_path)
    target = Path(target_dir) if target_dir else None

    async def run_extraction() -> None:
        extractor = ConcernExtractor()
        result = await extractor.extract_concern(file, concern, target)

        if not result.success:
            click.echo(f"Error: {result.error}", err=True)
            return

        click.echo("\nConcern Extraction Result:")
        click.echo(f"  Source: {result.source_file}")
        click.echo(f"  Target: {result.target_file}")
        click.echo(f"  Concern: {concern}")

        if dry_run:
            click.echo("\n--- Extracted Code Preview ---")
            click.echo(result.extracted_code[:500])
            if len(result.extracted_code) > 500:
                click.echo("... (truncated)")
        else:
            Path(result.target_file).write_text(result.extracted_code)
            Path(result.source_file).write_text(result.remaining_code)
            click.echo("\n✓ Extraction completed successfully")

    asyncio.run(run_extraction())


@extract.command("pattern")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("pattern_type", type=click.Choice(["factory", "singleton", "strategy", "observer"]))
@click.option(
    "--target-dir", "-d", type=click.Path(), help="Target directory for extracted pattern",
)
@click.option("--dry-run", is_flag=True, help="Show what would be extracted without writing files")
def extract_pattern(
    file_path: str, pattern_type: str, target_dir: str | None, dry_run: bool,
) -> None:
    """
    Extract a design pattern to a separate file.
    """
    file = Path(file_path)
    target = Path(target_dir) if target_dir else None

    async def run_extraction() -> None:
        extractor = PatternExtractor()
        result = await extractor.extract_pattern(file, pattern_type, target)

        if not result.success:
            click.echo(f"Error: {result.error}", err=True)
            return

        click.echo("\nPattern Extraction Result:")
        click.echo(f"  Source: {result.source_file}")
        click.echo(f"  Target: {result.target_file}")
        click.echo(f"  Pattern: {pattern_type}")

        if dry_run:
            click.echo("\n--- Extracted Code Preview ---")
            click.echo(result.extracted_code[:500])
        else:
            Path(result.target_file).write_text(result.extracted_code)
            click.echo("\n✓ Extraction completed successfully")

    asyncio.run(run_extraction())


@extract.command("layer")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument(
    "layer", type=click.Choice(["domain", "application", "adapters", "infrastructure", "ports"]),
)
@click.option("--target-dir", "-d", type=click.Path(), help="Target directory for extracted layer")
@click.option("--dry-run", is_flag=True, help="Show what would be extracted without writing files")
def extract_layer(file_path: str, layer: str, target_dir: str | None, dry_run: bool) -> None:
    """
    Extract code by architectural layer.
    """
    file = Path(file_path)
    target = Path(target_dir) if target_dir else None

    async def run_extraction() -> None:
        extractor = LayerExtractor()
        result = await extractor.extract_layer(file, layer, target)

        if not result.success:
            click.echo(f"Error: {result.error}", err=True)
            return

        click.echo("\nLayer Extraction Result:")
        click.echo(f"  Source: {result.source_file}")
        click.echo(f"  Target: {result.target_file}")
        click.echo(f"  Layer: {layer}")

        if dry_run:
            click.echo("\n--- Extracted Code Preview ---")
            click.echo(result.extracted_code[:500])
        else:
            # Create target directory if needed
            Path(result.target_file).parent.mkdir(parents=True, exist_ok=True)
            Path(result.target_file).write_text(result.extracted_code)
            click.echo("\n✓ Extraction completed successfully")

    asyncio.run(run_extraction())


@cli.group()
def validate() -> None:
    """
    Validate hexagonal architecture compliance.
    """


@validate.command("port-adapter")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--is-port", is_flag=True, help="Validate as port interface")
@click.option(
    "--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format",
)
def validate_port_adapter_cmd(file_path: str, is_port: bool, output: str) -> None:
    """
    Validate port/adapter pattern compliance.
    """
    file = Path(file_path)

    async def run_validation() -> None:
        result = await validate_port_adapter(file, is_port)

        if output == "json":
            data = {
                "file": result.file_path,
                "valid": result.is_valid,
                "errors": result.error_count,
                "warnings": result.warning_count,
                "issues": [
                    {
                        "rule": i.rule_name,
                        "line": i.line_number,
                        "severity": i.severity,
                        "message": i.message,
                        "suggestion": i.suggestion,
                    }
                    for i in result.issues
                ],
            }
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Port/Adapter Validation: {result.file_path}")
            click.echo(f"{'=' * 80}\n")

            status = "✓ PASS" if result.is_valid else "✗ FAIL"
            click.echo(f"Status: {status}")
            click.echo(f"Errors: {result.error_count}")
            click.echo(f"Warnings: {result.warning_count}")

            if result.issues:
                click.echo("\nIssues:")
                for issue in result.issues:
                    click.echo(f"\n  [{issue.severity.upper()}] {issue.rule_name}")
                    click.echo(f"  Line {issue.line_number}: {issue.message}")
                    if issue.suggestion:
                        click.echo(f"  → {issue.suggestion}")

    asyncio.run(run_validation())


@validate.command("layers")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format",
)
def validate_layers_cmd(file_path: str, output: str) -> None:
    """
    Validate layer separation and dependencies.
    """
    file = Path(file_path)

    async def run_validation() -> None:
        result = await validate_layers(file)

        if output == "json":
            data = {
                "file": result.file_path,
                "valid": result.is_valid,
                "errors": result.error_count,
                "warnings": result.warning_count,
                "issues": [
                    {
                        "rule": i.rule_name,
                        "line": i.line_number,
                        "severity": i.severity,
                        "message": i.message,
                    }
                    for i in result.issues
                ],
            }
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Layer Validation: {result.file_path}")
            click.echo(f"{'=' * 80}\n")

            status = "✓ PASS" if result.is_valid else "✗ FAIL"
            click.echo(f"Status: {status}")
            click.echo(f"Errors: {result.error_count}")
            click.echo(f"Warnings: {result.warning_count}")

            if result.issues:
                click.echo("\nIssues:")
                for issue in result.issues:
                    click.echo(f"\n  [{issue.severity.upper()}] {issue.rule_name}")
                    click.echo(f"  Line {issue.line_number}: {issue.message}")

    asyncio.run(run_validation())


@validate.command("dependencies")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format",
)
def validate_dependencies_cmd(file_path: str, output: str) -> None:
    """
    Validate dependency rules.
    """
    file = Path(file_path)

    async def run_validation() -> None:
        result = await validate_dependencies(file)

        if output == "json":
            data = {
                "file": result.file_path,
                "valid": result.is_valid,
                "errors": result.error_count,
                "warnings": result.warning_count,
                "issues": [
                    {
                        "rule": i.rule_name,
                        "line": i.line_number,
                        "severity": i.severity,
                        "message": i.message,
                    }
                    for i in result.issues
                ],
            }
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Dependency Validation: {result.file_path}")
            click.echo(f"{'=' * 80}\n")

            status = "✓ PASS" if result.is_valid else "✗ FAIL"
            click.echo(f"Status: {status}")
            click.echo(f"Errors: {result.error_count}")
            click.echo(f"Warnings: {result.warning_count}")

            if result.issues:
                click.echo("\nIssues:")
                for issue in result.issues:
                    click.echo(f"\n  [{issue.severity.upper()}] {issue.rule_name}")
                    click.echo(f"  Line {issue.line_number}: {issue.message}")

    asyncio.run(run_validation())


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path for report")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "html", "markdown"]),
    default="text",
    help="Report format",
)
def report(directory: str, output: str | None, format: str) -> None:
    """
    Generate comprehensive refactoring report.
    """
    dir_path = Path(directory)

    async def generate_report() -> None:
        # Run all analyses
        large_files = await detect_large_files(dir_path)
        violations = await detect_violations(dir_path)

        # Generate report
        if format == "json":
            report_data = {
                "directory": str(dir_path),
                "summary": {
                    "large_files": len(large_files),
                    "violations": len(violations),
                },
                "large_files": [{"file": str(f), "lines": loc} for f, loc in large_files],
                "violations": [
                    {
                        "file": v.file_path,
                        "type": v.violation_type,
                        "severity": v.severity,
                        "message": v.message,
                    }
                    for v in violations
                ],
            }
            report_text = json.dumps(report_data, indent=2)

        elif format == "markdown":
            lines = [
                "# Refactoring Report",
                "",
                f"**Directory:** `{dir_path}`",
                "",
                "## Summary",
                "",
                f"- Large Files: {len(large_files)}",
                f"- Violations: {len(violations)}",
                "",
                "## Large Files",
                "",
            ]

            for file, loc in large_files[:20]:
                lines.append(f"- `{file}`: {loc} LOC")

            lines.extend(
                [
                    "",
                    "## Violations",
                    "",
                ],
            )

            for v in violations[:50]:
                lines.append(f"### {v.violation_type}")
                lines.append("")
                lines.append(f"- **File:** `{v.file_path}:{v.line_number}`")
                lines.append(f"- **Severity:** {v.severity}")
                lines.append(f"- **Message:** {v.message}")
                lines.append("")

            report_text = "\n".join(lines)

        else:  # text
            lines = [
                "",
                f"{'=' * 80}",
                f"Refactoring Report: {dir_path}",
                f"{'=' * 80}",
                "",
                "Summary:",
                f"  Large Files: {len(large_files)}",
                f"  Violations: {len(violations)}",
                "",
            ]

            if large_files:
                lines.append("Large Files:")
                for file, loc in large_files[:20]:
                    lines.append(f"  {loc:5d} LOC: {file}")

            if violations:
                lines.append("")
                lines.append("Violations:")
                for v in violations[:50]:
                    lines.append(f"  [{v.severity.upper()}] {v.file_path}:{v.line_number}")
                    lines.append(f"    {v.message}")

            report_text = "\n".join(lines)

        # Output report
        if output:
            Path(output).write_text(report_text)
            click.echo(f"Report written to: {output}")
        else:
            click.echo(report_text)

    asyncio.run(generate_report())


if __name__ == "__main__":
    cli()
