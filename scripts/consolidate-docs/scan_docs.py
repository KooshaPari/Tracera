#!/usr/bin/env python3
"""Documentation Scanner - Phase 1 of Consolidation.

Scans all markdown files and creates comprehensive inventory.
Outputs: docs_inventory.json with metadata, content hashes, categorization.
"""

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import frontmatter
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

console = Console()

# Exclude patterns
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
]


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
    audience: str | None = None
    doc_type: str | None = None
    frontmatter: dict | None = None
    first_line: str | None = None
    headings: list[str] | None = None
    links: list[str] | None = None
    created_date: str | None = None
    updated_date: str | None = None


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    return any(pattern.replace("**/", "").replace("**", "") in path_str for pattern in EXCLUDE_PATTERNS)


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
    for line in lines[:20]:  # Check first 20 lines
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
    # Match [text](path) and [text][ref] patterns
    patterns = [
        r"\[([^\]]+)\]\(([^)]+)\)",  # [text](path)
        r"\[([^\]]+)\]\[([^\]]+)\]",  # [text][ref]
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                links.append(match[1] if len(match) > 1 else match[0])
            else:
                links.append(match)
    return links


def determine_audience(path_str: str, frontmatter_data: dict) -> str:
    """Determine document audience from path and frontmatter."""
    audience = frontmatter_data.get("audience")
    if audience:
        return audience

    if "user" in path_str or "getting-started" in path_str or "guide" in path_str:
        return "user"
    if "developer" in path_str or "api" in path_str or "architecture" in path_str:
        return "developer"
    if "api" in path_str or "reference" in path_str:
        return "api"
    return "unknown"


def determine_doc_type(path_str: str, frontmatter_data: dict) -> str:
    """Determine document type from path and frontmatter."""
    doc_type = frontmatter_data.get("type")
    if doc_type:
        return doc_type

    # Mapping of keywords to doc types
    type_patterns = {
        "research": ["research"],
        "planning": ["plan", "planning"],
        "report": ["report", "completion"],
        "guide": ["guide", "tutorial"],
        "reference": ["reference", "api"],
        "example": ["example", "use-case"],
        "faq": ["faq", "troubleshooting"],
    }

    for doc_type, keywords in type_patterns.items():
        if any(keyword in path_str for keyword in keywords):
            return doc_type

    return "general"


def determine_category(path_str: str, frontmatter_data: dict) -> str:
    """Determine document category from path and frontmatter."""
    category = frontmatter_data.get("category")
    if category:
        return category

    # Mapping of keywords to categories
    category_patterns = {
        "cli": ["cli"],
        "tui": ["tui"],
        "frontend": ["frontend", "web"],
        "backend": ["backend"],
        "testing": ["test", "testing"],
        "architecture": ["architecture"],
    }

    for category, keywords in category_patterns.items():
        if any(keyword in path_str for keyword in keywords):
            return category

    return "general"


def categorize_doc(path: Path, _content: str, frontmatter_data: dict) -> dict[str, str]:
    """Categorize document by audience, type, and topic."""
    path_str = str(path).lower()

    return {
        "audience": determine_audience(path_str, frontmatter_data),
        "type": determine_doc_type(path_str, frontmatter_data),
        "category": determine_category(path_str, frontmatter_data),
    }


def scan_documentation(root_dir: Path = Path.cwd()) -> list[DocMetadata]:
    """Scan all markdown files and create inventory."""
    console.print("[bold blue]Scanning documentation files...[/bold blue]")

    all_docs = []
    md_files = list(root_dir.rglob("*.md"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning files...", total=len(md_files))

        for md_file in md_files:
            if should_exclude(md_file):
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

                # Categorize
                categorization = categorize_doc(md_file, content_body, frontmatter_data)

                # Extract additional info
                headings = extract_headings(content_body)
                links = extract_links(content_body)
                first_line = content_body.split("\n")[0] if content_body else None

                doc = DocMetadata(
                    path=str(md_file),
                    relative_path=str(md_file.relative_to(root_dir)),
                    size=len(content.encode()),
                    lines=len(content.split("\n")),
                    content_hash=content_hash,
                    title=title,
                    description=description,
                    category=categorization["category"],
                    audience=categorization["audience"],
                    doc_type=categorization["type"],
                    frontmatter=frontmatter_data,
                    first_line=first_line,
                    headings=headings,
                    links=links,
                    created_date=frontmatter_data.get("date") or frontmatter_data.get("created"),
                    updated_date=frontmatter_data.get("updated") or frontmatter_data.get("lastUpdated"),
                )

                all_docs.append(doc)
                progress.update(task, advance=1)

            except Exception as e:
                console.print(f"[yellow]Warning: Could not process {md_file}: {e}[/yellow]")
                progress.update(task, advance=1)

    return all_docs


def generate_statistics(docs: list[DocMetadata]) -> dict:
    """Generate statistics about documentation."""
    stats = {
        "total_files": len(docs),
        "total_size": sum(d.size for d in docs),
        "total_lines": sum(d.lines for d in docs),
        "by_audience": defaultdict(int),
        "by_type": defaultdict(int),
        "by_category": defaultdict(int),
        "with_frontmatter": sum(1 for d in docs if d.frontmatter),
        "with_title": sum(1 for d in docs if d.title),
    }

    for doc in docs:
        stats["by_audience"][doc.audience] += 1
        stats["by_type"][doc.doc_type] += 1
        stats["by_category"][doc.category] += 1

    return stats


def main() -> None:
    """Main entry point."""
    root_dir = Path.cwd()
    output_dir = root_dir / "consolidation-output"
    output_dir.mkdir(exist_ok=True)

    # Scan all documentation
    docs = scan_documentation(root_dir)

    # Generate statistics
    stats = generate_statistics(docs)

    # Save inventory
    inventory = {
        "metadata": {
            "version": "1.0.0",
            "scanned_at": str(Path.cwd()),
            "total_files": len(docs),
        },
        "statistics": stats,
        "docs": [asdict(doc) for doc in docs],
    }

    inventory_path = output_dir / "docs_inventory.json"
    with Path(inventory_path).open("w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    console.print(f"\n[green]✓[/green] Scanned {len(docs)} documentation files")
    console.print(f"[green]✓[/green] Inventory saved to: {inventory_path}")
    console.print("\n[bold]Statistics:[/bold]")
    console.print(f"  Total files: {stats['total_files']}")
    console.print(f"  Total size: {stats['total_size']:,} bytes")
    console.print(f"  Total lines: {stats['total_lines']:,}")
    console.print("\n  By Audience:")
    for audience, count in sorted(stats["by_audience"].items()):
        console.print(f"    {audience}: {count}")
    console.print("\n  By Type:")
    for doc_type, count in sorted(stats["by_type"].items()):
        console.print(f"    {doc_type}: {count}")
    console.print("\n  By Category:")
    for category, count in sorted(stats["by_category"].items()):
        console.print(f"    {category}: {count}")


if __name__ == "__main__":
    main()
