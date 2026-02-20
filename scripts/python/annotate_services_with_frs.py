#!/usr/bin/env python3
"""Annotate service files with FR/ADR/Epic references in docstrings.

This script:
1. Reads FUNCTIONAL_REQUIREMENTS.md to extract FR → implementation mappings
2. Reads PRD.md to extract Epic hierarchy
3. Reads ADR files to build ADR list
4. Parses service files using AST
5. Matches FR implementation locations to functions/classes
6. Updates docstrings with FR/ADR/Epic references
7. Preserves existing docstring content
8. Verifies ruff/mypy compliance after changes

Usage:
    python scripts/python/annotate_services_with_frs.py [--file FILE] [--dry-run]

Arguments:
    --file FILE     Process single file (default: all services)
    --dry-run       Show changes without writing files
    --verify        Run ruff/mypy after changes
"""

from __future__ import annotations

import argparse
import ast
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class FRMapping:
    """Functional requirement to code mapping."""

    fr_id: str
    epic_ids: list[str]
    user_story_ids: list[str]
    adr_ids: list[str]
    file_path: str
    line_range: tuple[int, int] | None
    functions_classes: list[str]
    api_endpoints: list[str]


@dataclass
class AnnotationData:
    """Annotation data for a function/class."""

    frs: list[str]
    epics: list[str]
    user_stories: list[str]
    adrs: list[str]


class FRExtractor:
    """Extract FR mappings from FUNCTIONAL_REQUIREMENTS.md."""

    def __init__(self, fr_file: Path):
        """Initialize extractor."""
        self.fr_file = fr_file
        self.mappings: list[FRMapping] = []

    def extract(self) -> list[FRMapping]:
        """Extract all FR mappings."""
        if not self.fr_file.exists():
            logger.error(f"FR file not found: {self.fr_file}")
            return []

        content = self.fr_file.read_text()
        sections = self._split_fr_sections(content)

        for section in sections:
            mapping = self._parse_fr_section(section)
            if mapping:
                self.mappings.append(mapping)

        logger.info(f"Extracted {len(self.mappings)} FR mappings")
        return self.mappings

    def _split_fr_sections(self, content: str) -> list[str]:
        """Split content into FR sections."""
        # Split by FR-XXX-NNN pattern
        pattern = r"(###\s+FR-[A-Z]+-\d+:)"
        parts = re.split(pattern, content)

        sections = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                sections.append(parts[i] + parts[i + 1])

        return sections

    def _parse_fr_section(self, section: str) -> FRMapping | None:
        """Parse single FR section."""
        # Extract FR ID
        fr_match = re.search(r"FR-[A-Z]+-\d+", section)
        if not fr_match:
            return None
        fr_id = fr_match.group(0)

        # Extract Epic IDs
        epic_ids = re.findall(r"EPIC-\d+", section)

        # Extract User Story IDs
        user_story_ids = re.findall(r"US-[A-Z]+-\d+", section)

        # Extract ADR IDs from "Architecture:" or similar
        adr_ids = re.findall(r"ADR-\d+", section)

        # Extract implementation details
        impl_match = re.search(
            r"\*\*Implemented in:\*\*\s*\n\s*-\s*\*\*File\(s\):\*\*\s*`([^`]+)`",
            section,
        )
        if not impl_match:
            return None

        file_info = impl_match.group(1)
        # Parse file path and line range
        # Format: src/tracertm/services/github_import_service.py:1-350
        file_match = re.match(r"([^:]+)(?::(\d+)-(\d+))?", file_info)
        if not file_match:
            return None

        file_path = file_match.group(1)
        line_range = None
        if file_match.group(2) and file_match.group(3):
            line_range = (int(file_match.group(2)), int(file_match.group(3)))

        # Extract functions/classes
        func_match = re.search(
            r"\*\*Functions/Classes:\*\*\s*`([^`]+)`",
            section,
        )
        functions_classes = []
        if func_match:
            functions_classes = [f.strip() for f in func_match.group(1).split(",")]

        # Extract API endpoints
        api_match = re.search(
            r"\*\*API Endpoints:\*\*\s*`([^`]+)`",
            section,
        )
        api_endpoints = []
        if api_match:
            api_endpoints = [e.strip() for e in api_match.group(1).split(",")]

        return FRMapping(
            fr_id=fr_id,
            epic_ids=epic_ids,
            user_story_ids=user_story_ids,
            adr_ids=adr_ids,
            file_path=file_path,
            line_range=line_range,
            functions_classes=functions_classes,
            api_endpoints=api_endpoints,
        )


class EpicExtractor:
    """Extract Epic hierarchy from PRD.md."""

    def __init__(self, prd_file: Path):
        """Initialize extractor."""
        self.prd_file = prd_file
        self.epics: dict[str, str] = {}

    def extract(self) -> dict[str, str]:
        """Extract epic ID to name mapping."""
        if not self.prd_file.exists():
            logger.error(f"PRD file not found: {self.prd_file}")
            return {}

        content = self.prd_file.read_text()

        # Extract epic hierarchy section
        hierarchy_match = re.search(
            r"##\s+\d+\.\s+Epic Hierarchy\s*\n```\s*\n(.*?)\n```",
            content,
            re.DOTALL,
        )
        if not hierarchy_match:
            logger.warning("Epic hierarchy not found in PRD")
            return {}

        hierarchy = hierarchy_match.group(1)
        # Parse lines like "E1.1: Multi-Source Import"
        for line in hierarchy.split("\n"):
            epic_match = re.match(r"\s*(E[\d.]+):\s*(.+)", line)
            if epic_match:
                epic_id = epic_match.group(1)
                epic_name = epic_match.group(2).strip()
                self.epics[epic_id] = epic_name

        logger.info(f"Extracted {len(self.epics)} epics")
        return self.epics


class ADRExtractor:
    """Extract ADR list from docs/adr/*.md."""

    def __init__(self, adr_dir: Path):
        """Initialize extractor."""
        self.adr_dir = adr_dir
        self.adrs: dict[str, str] = {}

    def extract(self) -> dict[str, str]:
        """Extract ADR ID to title mapping."""
        if not self.adr_dir.exists():
            logger.error(f"ADR directory not found: {self.adr_dir}")
            return {}

        for adr_file in self.adr_dir.glob("ADR-*.md"):
            # Extract ADR ID from filename
            adr_match = re.match(r"ADR-(\d+)", adr_file.stem)
            if not adr_match:
                continue

            adr_id = f"ADR-{adr_match.group(1)}"

            # Extract title from first # heading
            content = adr_file.read_text()
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                # Remove ADR-NNNN prefix from title if present
                title = re.sub(r"^ADR-\d+:\s*", "", title)
                self.adrs[adr_id] = title

        logger.info(f"Extracted {len(self.adrs)} ADRs")
        return self.adrs


class DocstringAnnotator:
    """Annotate Python AST nodes with FR/ADR/Epic references."""

    def __init__(
        self,
        fr_mappings: list[FRMapping],
        epics: dict[str, str],
        adrs: dict[str, str],
    ):
        """Initialize annotator."""
        self.fr_mappings = fr_mappings
        self.epics = epics
        self.adrs = adrs

    def annotate_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Annotate single file."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        # Find mappings for this file
        # Handle both absolute and relative paths
        abs_path = file_path.resolve()
        try:
            rel_path = str(abs_path.relative_to(Path.cwd()))
        except ValueError:
            # File is not under cwd, try relative to file_path itself
            rel_path = str(file_path)

        mappings = [m for m in self.fr_mappings if m.file_path == rel_path]

        if not mappings:
            logger.debug(f"No FR mappings for {file_path}")
            return False

        logger.info(f"Processing {file_path} ({len(mappings)} mappings)")

        # Read file
        original_content = file_path.read_text()

        # Parse AST
        try:
            tree = ast.parse(original_content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return False

        # Build annotation map: function/class name -> AnnotationData
        annotation_map = self._build_annotation_map(mappings)

        # Annotate nodes
        modified_content = self._annotate_nodes(
            original_content,
            tree,
            annotation_map,
        )

        if modified_content == original_content:
            logger.debug(f"No changes needed for {file_path}")
            return False

        if dry_run:
            logger.info(f"[DRY RUN] Would update {file_path}")
            return True

        # Write changes
        file_path.write_text(modified_content)
        logger.info(f"✓ Updated {file_path}")
        return True

    def _build_annotation_map(
        self,
        mappings: list[FRMapping],
    ) -> dict[str, AnnotationData]:
        """Build function/class name to annotation data map."""
        annotation_map: dict[str, AnnotationData] = {}

        for mapping in mappings:
            for func_or_class in mapping.functions_classes:
                # Parse format like "GitHubImportService.import_from_github()"
                # or just "GitHubImportService"
                name = func_or_class.split("(")[0].strip()

                # Get base name (last part after .)
                parts = name.split(".")
                if len(parts) == 2:
                    # Class.method format
                    class_name, method_name = parts
                    # Add both the class and method keys
                    keys = [class_name, method_name]
                elif len(parts) == 1:
                    # Just class or function name
                    keys = [name]
                else:
                    # More complex format, use last part
                    keys = [parts[-1]]

                for key in keys:
                    if key not in annotation_map:
                        annotation_map[key] = AnnotationData(
                            frs=[],
                            epics=[],
                            user_stories=[],
                            adrs=[],
                        )

                    annotation_map[key].frs.append(mapping.fr_id)
                    annotation_map[key].epics.extend(mapping.epic_ids)
                    annotation_map[key].user_stories.extend(mapping.user_story_ids)
                    annotation_map[key].adrs.extend(mapping.adr_ids)

        # Deduplicate lists
        for data in annotation_map.values():
            data.frs = sorted(set(data.frs))
            data.epics = sorted(set(data.epics))
            data.user_stories = sorted(set(data.user_stories))
            data.adrs = sorted(set(data.adrs))

        return annotation_map

    def _annotate_nodes(
        self,
        content: str,
        tree: ast.AST,
        annotation_map: dict[str, AnnotationData],
    ) -> str:
        """Annotate function/class nodes with FR references."""
        lines = content.splitlines(keepends=True)
        modified = False

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue

            name = node.name
            if name not in annotation_map:
                continue

            annotation = annotation_map[name]

            # Get existing docstring
            docstring = ast.get_docstring(node)
            if docstring is None:
                # No docstring, skip (could add one but risky)
                logger.warning(f"No docstring for {name}, skipping")
                continue

            # Check if already annotated
            if "Functional Requirements:" in docstring:
                logger.debug(f"{name} already annotated, skipping")
                continue

            # Build annotation sections with proper indentation
            # Docstrings need 4-space indent for content
            base_indent = "    "
            sections = []

            if annotation.frs:
                sections.append(f"{base_indent}Functional Requirements:")
                for fr in annotation.frs:
                    sections.append(f"{base_indent}- {fr}")

            if annotation.user_stories:
                sections.append(f"\n{base_indent}User Stories:")
                for us in annotation.user_stories:
                    sections.append(f"{base_indent}- {us}")

            if annotation.epics:
                sections.append(f"\n{base_indent}Epics:")
                for epic in annotation.epics:
                    epic_name = self.epics.get(epic, "")
                    if epic_name:
                        sections.append(f"{base_indent}- {epic}: {epic_name}")
                    else:
                        sections.append(f"{base_indent}- {epic}")

            if annotation.adrs:
                sections.append(f"\n{base_indent}Architecture:")
                for adr in annotation.adrs:
                    adr_title = self.adrs.get(adr, "")
                    if adr_title:
                        sections.append(f"{base_indent}- {adr}: {adr_title}")
                    else:
                        sections.append(f"{base_indent}- {adr}")

            if not sections:
                continue

            # Insert annotation at end of docstring
            new_docstring = docstring.rstrip() + "\n\n" + "\n".join(sections)

            # Find docstring location in source
            # Docstring is the first statement in the node body
            if not node.body or not isinstance(
                node.body[0],
                ast.Expr,
            ):
                continue

            docstring_node = node.body[0].value
            if not isinstance(docstring_node, ast.Constant):
                continue

            # Get line numbers (1-indexed)
            start_line = docstring_node.lineno - 1  # Convert to 0-indexed
            end_line = docstring_node.end_lineno - 1

            # Replace docstring
            # Handle both """ and ''' quotes
            quote_style = '"""'
            if lines[start_line].strip().startswith("'''"):
                quote_style = "'''"

            indent = self._get_indent(lines[start_line])

            # Build new docstring lines
            new_lines = [f"{indent}{quote_style}{new_docstring}\n"]
            if not new_docstring.endswith("\n"):
                new_lines = [f"{indent}{quote_style}{new_docstring}\n{indent}{quote_style}\n"]
            else:
                new_lines = [f"{indent}{quote_style}{new_docstring}{indent}{quote_style}\n"]

            # Replace in lines
            lines[start_line : end_line + 1] = new_lines
            modified = True

            logger.debug(f"Annotated {name} with {len(annotation.frs)} FRs")

        if not modified:
            return content

        return "".join(lines)

    def _get_indent(self, line: str) -> str:
        """Extract indentation from line."""
        return line[: len(line) - len(line.lstrip())]


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        help="Process single file (default: all services)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing files",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run ruff/mypy after changes",
    )
    args = parser.parse_args()

    # Locate project root
    root = Path.cwd()
    if not (root / "pyproject.toml").exists():
        logger.error("Not in project root (pyproject.toml not found)")
        return 1

    # Extract FR mappings
    fr_file = root / "docs/reference/FUNCTIONAL_REQUIREMENTS.md"
    fr_extractor = FRExtractor(fr_file)
    fr_mappings = fr_extractor.extract()

    if not fr_mappings:
        logger.error("No FR mappings found")
        return 1

    # Extract epics
    prd_file = root / "docs/reference/PRD.md"
    epic_extractor = EpicExtractor(prd_file)
    epics = epic_extractor.extract()

    # Extract ADRs
    adr_dir = root / "docs/adr"
    adr_extractor = ADRExtractor(adr_dir)
    adrs = adr_extractor.extract()

    # Initialize annotator
    annotator = DocstringAnnotator(fr_mappings, epics, adrs)

    # Determine files to process
    if args.file:
        files = [args.file]
    else:
        # Process all service files
        files = list((root / "src/tracertm/services").glob("**/*.py"))

    # Annotate files
    updated_count = 0
    for file_path in files:
        if annotator.annotate_file(file_path, dry_run=args.dry_run):
            updated_count += 1

    logger.info(f"Updated {updated_count} files")

    # Verify with ruff/mypy
    if args.verify and not args.dry_run and updated_count > 0:
        import subprocess

        logger.info("Running ruff check...")
        result = subprocess.run(
            ["ruff", "check", "src/tracertm/services/"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(f"Ruff errors:\n{result.stdout}")
            return 1

        logger.info("Running mypy...")
        result = subprocess.run(
            ["mypy", "src/tracertm/services/"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.warning(f"Mypy errors (informational):\n{result.stdout}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
