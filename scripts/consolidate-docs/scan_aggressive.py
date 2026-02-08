#!/usr/bin/env python3
"""Aggressive Documentation Scanner - Deep Consolidation Strategy.

Scans project markdown files (excludes dependencies) and categorizes
for aggressive consolidation targeting <2,000 files.
"""

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import frontmatter
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

console = Console()

# Aggressive exclusion patterns (dependencies, build artifacts, etc.)
EXCLUDE_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/.venv/**",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "**/dist/**",
    "**/build/**",
    "**/.next/**",
    "**/out/**",
    "**/.turbo/**",
    "**/coverage/**",
    "**/.coverage/**",
    "**/disable/**",  # Bun package store
    "**/default/**",  # Bun package store
]

# Consolidation categories
CONSOLIDATION_CATEGORIES = {
    "historical_reports": {
        "patterns": ["*REPORT*", "*COMPLETION*", "*SUMMARY*", "*STATUS*"],
        "target_count": 10,
        "strategy": "consolidate_to_index",
    },
    "planning_docs": {
        "patterns": ["*PHASE*", "*EPIC*", "*SPRINT*", "*PLAN*"],
        "target_count": 20,
        "strategy": "consolidate_by_topic",
    },
    "research_docs": {
        "patterns": ["*RESEARCH*", "*FINDINGS*", "*COMPARISON*", "*ANALYSIS*"],
        "target_count": 50,
        "strategy": "consolidate_by_topic",
    },
    "readme_files": {
        "patterns": ["README.md", "readme.md", "Readme.md"],
        "target_count": 5,
        "strategy": "keep_project_only",
    },
    "doc_planning": {
        "patterns": ["*DOCUMENTATION*", "*DOCS*"],
        "target_count": 10,
        "strategy": "consolidate_to_guide",
    },
    "feature_gap": {
        "patterns": ["*FEATURE*", "*GAP*", "*ANALYSIS*"],
        "target_count": 30,
        "strategy": "consolidate_by_interface",
    },
    "guides": {
        "patterns": ["*GUIDE*", "*TUTORIAL*", "*HOWTO*"],
        "target_count": 200,
        "strategy": "consolidate_similar",
    },
    "examples": {
        "patterns": ["*EXAMPLE*", "*USE-CASE*", "*CASE-STUDY*"],
        "target_count": 100,
        "strategy": "consolidate_similar",
    },
    "api_reference": {
        "patterns": ["*API*", "*REFERENCE*", "*ENDPOINT*"],
        "target_count": 150,
        "strategy": "keep_most",
    },
    "architecture": {
        "patterns": ["*ARCHITECTURE*", "*DESIGN*", "*PATTERN*"],
        "target_count": 100,
        "strategy": "consolidate_similar",
    },
    "testing": {
        "patterns": ["*TEST*", "*COVERAGE*", "*TESTING*"],
        "target_count": 80,
        "strategy": "consolidate_similar",
    },
    "implementation": {
        "patterns": ["*IMPLEMENTATION*", "*SETUP*", "*INSTALLATION*"],
        "target_count": 150,
        "strategy": "consolidate_similar",
    },
}


@dataclass
class DocMetadata:
    """Metadata for a single documentation file."""

    path: str
    relative_path: str
    size: int
    lines: int
    content_hash: str
    title: str | None = None
    description: str | None = None
    category: str | None = None
    consolidation_category: str | None = None
    consolidation_strategy: str | None = None
    frontmatter: dict | None = None
    headings: list[str] | None = None
    links: list[str] | None = None
    created_date: str | None = None
    updated_date: str | None = None
    is_project_file: bool = True
    is_dependency: bool = False


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        # Simple pattern matching
        pattern_clean = pattern.replace("**/", "").replace("**", "")
        if pattern_clean in path_str:
            return True
    return False


def is_project_readme(path: Path, root_dir: Path) -> bool:
    """Check if README is a project file (not dependency)."""
    # Project READMEs are typically in root, docs/, src/, or top-level dirs
    relative = path.relative_to(root_dir)
    parts = relative.parts

    # Exclude if in node_modules, .venv, or deep in dependencies
    if "node_modules" in parts or ".venv" in parts:
        return False

    # Include if in root or common project directories
    if len(parts) <= 2:  # Root level or one level deep
        return True

    # Include if in docs/, src/, tests/, etc.
    return parts[0] in {"docs", "src", "tests", "frontend", "backend", "scripts"}


def classify_consolidation_category(path: Path, content: str) -> str | None:
    """Classify file into consolidation category."""
    path_str = str(path).upper()
    content_upper = content.upper()
    combined = f"{path_str} {content_upper}"

    for category, config in CONSOLIDATION_CATEGORIES.items():
        for pattern in config["patterns"]:
            pattern_clean = pattern.replace("*", "").upper()
            if pattern_clean in combined:
                return category

    return None


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract frontmatter from markdown content."""
    try:
        post = frontmatter.loads(content)
        return post.metadata, post.content
    except Exception:
        return {}, content


def extract_title(content: str) -> str | None:
    """Extract title from first H1 heading or frontmatter."""
    lines = content.split("\n")
    for line in lines[:20]:
        if line.startswith("# "):
            return line[2:].strip()
    return None


def extract_headings(content: str) -> list[str]:
    """Extract all headings from markdown."""
    headings = []
    for line in content.split("\n"):
        if line.startswith("#"):
            text = line.lstrip("#").strip()
            if text:
                headings.append(text)
    return headings


def extract_links(content: str) -> list[str]:
    """Extract all internal markdown links."""
    links = []
    patterns = [
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"\[([^\]]+)\]\[([^\]]+)\]",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple) and len(match) > 1:
                links.append(match[1])
            elif isinstance(match, str):
                links.append(match)
    return links


def scan_documentation_aggressive(root_dir: Path = Path.cwd()) -> list[DocMetadata]:
    """Scan project markdown files (excludes dependencies)."""
    console.print("[bold blue]Scanning project documentation files (excluding dependencies)...[/bold blue]")

    all_docs = []
    md_files = list(root_dir.rglob("*.md"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning files...", total=len(md_files))

        for md_file in md_files:
            # Exclude dependencies
            if should_exclude(md_file):
                progress.update(task, advance=1)
                continue

            # Special handling for README files
            if md_file.name.lower() in {"readme.md", "readme"} and not is_project_readme(md_file, root_dir):
                progress.update(task, advance=1)
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                # Extract frontmatter
                frontmatter_data, content_body = extract_frontmatter(content)

                # Extract metadata
                title = frontmatter_data.get("title") or extract_title(content_body)
                description = frontmatter_data.get("description")

                # Classify consolidation category
                consolidation_category = classify_consolidation_category(md_file, content_body)
                consolidation_strategy = None
                if consolidation_category:
                    consolidation_strategy = CONSOLIDATION_CATEGORIES[consolidation_category]["strategy"]

                # Extract additional info
                headings = extract_headings(content_body)
                links = extract_links(content_body)

                doc = DocMetadata(
                    path=str(md_file),
                    relative_path=str(md_file.relative_to(root_dir)),
                    size=len(content.encode()),
                    lines=len(content.split("\n")),
                    content_hash=content_hash,
                    title=title,
                    description=description,
                    consolidation_category=consolidation_category,
                    consolidation_strategy=consolidation_strategy,
                    frontmatter=frontmatter_data,
                    headings=headings,
                    links=links,
                    created_date=frontmatter_data.get("date") or frontmatter_data.get("created"),
                    updated_date=frontmatter_data.get("updated") or frontmatter_data.get("lastUpdated"),
                    is_project_file=True,
                    is_dependency=False,
                )

                all_docs.append(doc)
                progress.update(task, advance=1)

            except Exception as e:
                console.print(f"[yellow]Warning: Could not process {md_file}: {e}[/yellow]")
                progress.update(task, advance=1)

    return all_docs


def generate_consolidation_statistics(docs: list[DocMetadata]) -> dict:
    """Generate statistics for consolidation planning."""
    stats = {
        "total_files": len(docs),
        "total_size": sum(d.size for d in docs),
        "total_lines": sum(d.lines for d in docs),
        "by_consolidation_category": defaultdict(int),
        "by_strategy": defaultdict(int),
        "readme_files": 0,
        "with_frontmatter": sum(1 for d in docs if d.frontmatter),
        "with_title": sum(1 for d in docs if d.title),
        "consolidation_plan": {},
    }

    for doc in docs:
        if doc.consolidation_category:
            stats["by_consolidation_category"][doc.consolidation_category] += 1
        if doc.consolidation_strategy:
            stats["by_strategy"][doc.consolidation_strategy] += 1
        if doc.path.lower().endswith("readme.md"):
            stats["readme_files"] += 1

    # Generate consolidation plan
    for category, config in CONSOLIDATION_CATEGORIES.items():
        current_count = stats["by_consolidation_category"][category]
        target_count = config["target_count"]
        reduction = ((current_count - target_count) / current_count * 100) if current_count > 0 else 0

        stats["consolidation_plan"][category] = {
            "current": current_count,
            "target": target_count,
            "reduction_percent": round(reduction, 1),
            "strategy": config["strategy"],
        }

    return stats


def print_consolidation_plan(stats: dict) -> None:
    """Print consolidation plan table."""
    table = Table(title="Consolidation Plan", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Current", justify="right", style="yellow")
    table.add_column("Target", justify="right", style="green")
    table.add_column("Reduction %", justify="right", style="red")
    table.add_column("Strategy", style="blue")

    for category, plan in stats["consolidation_plan"].items():
        if plan["current"] > 0:
            table.add_row(
                category.replace("_", " ").title(),
                str(plan["current"]),
                str(plan["target"]),
                f"{plan['reduction_percent']:.1f}%",
                plan["strategy"],
            )

    console.print("\n")
    console.print(table)

    # Calculate totals
    total_current = sum(p["current"] for p in stats["consolidation_plan"].values())
    total_target = sum(p["target"] for p in stats["consolidation_plan"].values())
    total_reduction = ((total_current - total_target) / total_current * 100) if total_current > 0 else 0

    console.print(
        f"\n[bold]Total:[/bold] {total_current:,} → {total_target:,} files ({total_reduction:.1f}% reduction)",
    )


def main() -> None:
    """Main entry point."""
    root_dir = Path.cwd()
    output_dir = root_dir / "consolidation-output"
    output_dir.mkdir(exist_ok=True)

    # Scan project documentation
    docs = scan_documentation_aggressive(root_dir)

    # Generate statistics
    stats = generate_consolidation_statistics(docs)

    # Save inventory
    inventory = {
        "metadata": {
            "version": "2.0.0",
            "scanned_at": str(Path.cwd()),
            "total_files": len(docs),
            "excludes_dependencies": True,
        },
        "statistics": stats,
        "docs": [asdict(doc) for doc in docs],
    }

    inventory_path = output_dir / "docs_inventory_aggressive.json"
    with Path(inventory_path).open("w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    # Print results
    console.print(f"\n[green]✓[/green] Scanned {len(docs):,} project documentation files")
    console.print(f"[green]✓[/green] Inventory saved to: {inventory_path}")
    console.print("\n[bold]Statistics:[/bold]")
    console.print(f"  Total files: {stats['total_files']:,}")
    console.print(f"  Total size: {stats['total_size']:,} bytes ({stats['total_size'] / 1024 / 1024:.1f} MB)")
    console.print(f"  Total lines: {stats['total_lines']:,}")
    console.print(f"  README files: {stats['readme_files']}")
    console.print(f"  With frontmatter: {stats['with_frontmatter']}")
    console.print(f"  With title: {stats['with_title']}")

    # Print consolidation plan
    print_consolidation_plan(stats)

    # Print by strategy
    console.print("\n[bold]By Consolidation Strategy:[/bold]")
    for strategy, count in sorted(stats["by_strategy"].items(), key=lambda x: -x[1]):
        console.print(f"  {strategy}: {count}")


if __name__ == "__main__":
    main()
