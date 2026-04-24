#!/usr/bin/env python3
"""Annotate API endpoint functions with FR references in docstrings.

This script:
1. Scans API router files in src/tracertm/api/routers/
2. Finds endpoint decorators (@router.get, @router.post, etc.)
3. Extracts endpoint paths and functions
4. Matches to FRs from FUNCTIONAL_REQUIREMENTS.md
5. Adds FR references to endpoint docstrings
6. Preserves FastAPI doc metadata

Usage:
    python scripts/python/annotate_apis_with_frs.py [--file FILE] [--dry-run]

Arguments:
    --file FILE     Process single file (default: all routers)
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class EndpointMapping:
    """API endpoint to FR mapping."""

    fr_id: str
    epic_ids: list[str]
    user_story_ids: list[str]
    endpoint_path: str
    http_method: str


@dataclass
class AnnotationData:
    """Annotation data for an endpoint."""

    frs: list[str]
    epics: list[str]
    user_stories: list[str]


class APIEndpointExtractor:
    """Extract API endpoint to FR mappings."""

    def __init__(self, fr_file: Path):
        """Initialize extractor."""
        self.fr_file = fr_file
        self.mappings: list[EndpointMapping] = []

    def extract(self) -> list[EndpointMapping]:
        """Extract all endpoint mappings."""
        if not self.fr_file.exists():
            logger.error(f"FR file not found: {self.fr_file}")
            return []

        content = self.fr_file.read_text()
        sections = self._split_fr_sections(content)

        for section in sections:
            mappings = self._parse_api_endpoints(section)
            self.mappings.extend(mappings)

        logger.info(f"Extracted {len(self.mappings)} API endpoint mappings")
        return self.mappings

    def _split_fr_sections(self, content: str) -> list[str]:
        """Split content into FR sections."""
        pattern = r"(###\s+FR-[A-Z]+-\d+:)"
        parts = re.split(pattern, content)

        sections = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                sections.append(parts[i] + parts[i + 1])

        return sections

    def _parse_api_endpoints(self, section: str) -> list[EndpointMapping]:
        """Parse API endpoints from FR section."""
        # Extract FR ID
        fr_match = re.search(r"FR-[A-Z]+-\d+", section)
        if not fr_match:
            return []
        fr_id = fr_match.group(0)

        # Extract Epic IDs
        epic_ids = re.findall(r"EPIC-\d+", section)

        # Extract User Story IDs
        user_story_ids = re.findall(r"US-[A-Z]+-\d+", section)

        # Extract API endpoints
        # Format: POST /api/v1/integrations/github/app/installations/{id}/link
        endpoint_match = re.search(
            r"\*\*API Endpoints:\*\*\s*`([^`]+)`",
            section,
        )
        if not endpoint_match:
            return []

        endpoints_str = endpoint_match.group(1)
        endpoints = [e.strip() for e in endpoints_str.split(",")]

        mappings = []
        for endpoint in endpoints:
            # Parse "METHOD /path" format
            parts = endpoint.split(None, 1)
            if len(parts) != 2:
                logger.warning(f"Invalid endpoint format: {endpoint}")
                continue

            http_method = parts[0].upper()
            endpoint_path = parts[1]

            mappings.append(
                EndpointMapping(
                    fr_id=fr_id,
                    epic_ids=epic_ids,
                    user_story_ids=user_story_ids,
                    endpoint_path=endpoint_path,
                    http_method=http_method,
                ),
            )

        return mappings


class EndpointAnnotator:
    """Annotate API endpoint functions with FR references."""

    def __init__(self, endpoint_mappings: list[EndpointMapping]):
        """Initialize annotator."""
        self.endpoint_mappings = endpoint_mappings
        # Build lookup: (method, path) -> AnnotationData
        self.annotation_map = self._build_annotation_map()

    def _build_annotation_map(self) -> dict[tuple[str, str], AnnotationData]:
        """Build (method, path) to annotation data map."""
        annotation_map: dict[tuple[str, str], AnnotationData] = {}

        for mapping in self.endpoint_mappings:
            key = (mapping.http_method, mapping.endpoint_path)

            if key not in annotation_map:
                annotation_map[key] = AnnotationData(
                    frs=[],
                    epics=[],
                    user_stories=[],
                )

            annotation_map[key].frs.append(mapping.fr_id)
            annotation_map[key].epics.extend(mapping.epic_ids)
            annotation_map[key].user_stories.extend(mapping.user_story_ids)

        # Deduplicate lists
        for data in annotation_map.values():
            data.frs = sorted(set(data.frs))
            data.epics = sorted(set(data.epics))
            data.user_stories = sorted(set(data.user_stories))

        return annotation_map

    def annotate_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Annotate single router file."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        logger.info(f"Processing {file_path}")

        # Read file
        original_content = file_path.read_text()

        # Parse AST
        try:
            tree = ast.parse(original_content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return False

        # Annotate endpoints
        modified_content = self._annotate_endpoints(original_content, tree)

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

    def _annotate_endpoints(self, content: str, tree: ast.AST) -> str:
        """Annotate endpoint functions."""
        lines = content.splitlines(keepends=True)
        modified = False

        # Extract router prefix from content
        router_prefix = self._extract_router_prefix(content)

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue

            # Check for router decorator
            endpoint_info = self._extract_endpoint_decorator(node)
            if not endpoint_info:
                continue

            method, relative_path = endpoint_info

            # Construct full path from router prefix + relative path
            full_path = router_prefix + relative_path

            # Try multiple path variations to match FR document
            # Some routers have /api/v1/ prefix, some are mounted under it
            path_variations = [full_path]
            if not full_path.startswith("/api/v1/"):
                path_variations.append("/api/v1" + full_path)

            # Also try without trailing slash
            if full_path.endswith("/"):
                path_variations.append(full_path.rstrip("/"))
                if not full_path.startswith("/api/v1/"):
                    path_variations.append("/api/v1" + full_path.rstrip("/"))

            # Check if we have annotations for this endpoint
            annotation = None
            for path_attempt in path_variations:
                key = (method, path_attempt)
                logger.debug(f"Checking endpoint: {method} {path_attempt}")
                if key in self.annotation_map:
                    logger.debug(f"  Found exact match")
                    annotation = self.annotation_map[key]
                    break

                # Try normalizing path (replace {id} with {.*})
                normalized_path = re.sub(r"\{[^}]+\}", "{id}", path_attempt)
                normalized_key = (method, normalized_path)
                logger.debug(f"  Normalized: {method} {normalized_path}")
                if normalized_key in self.annotation_map:
                    logger.debug(f"  Found via normalization")
                    annotation = self.annotation_map[normalized_key]
                    break

            if annotation is None:
                logger.debug(f"  No FR mapping found for any variation")
                continue

            # Get existing docstring
            docstring = ast.get_docstring(node)
            if docstring is None:
                logger.warning(f"No docstring for {node.name}, skipping")
                continue

            # Check if already annotated
            if "Functional Requirements:" in docstring:
                logger.debug(f"{node.name} already annotated, skipping")
                continue

            # Build annotation sections (without indentation - will be added later)
            sections = []

            if annotation.frs:
                sections.append("Functional Requirements:")
                for fr in annotation.frs:
                    sections.append(f"- {fr}")

            if annotation.user_stories:
                sections.append("\nUser Stories:")
                for us in annotation.user_stories:
                    sections.append(f"- {us}")

            if annotation.epics:
                sections.append("\nEpics:")
                for epic in annotation.epics:
                    sections.append(f"- {epic}")

            if not sections:
                continue

            # Get docstring indentation
            docstring_indent = "    "  # Standard 4-space indent for docstring content

            # Indent each section line
            indented_sections = [docstring_indent + line if line and not line.startswith("\n") else line
                                 for line in sections]

            # Insert annotation at end of docstring
            new_docstring = docstring.rstrip() + "\n\n" + "\n".join(indented_sections)

            # Find docstring location in source
            if not node.body or not isinstance(node.body[0], ast.Expr):
                continue

            docstring_node = node.body[0].value
            if not isinstance(docstring_node, ast.Constant):
                continue

            # Get line numbers (1-indexed)
            start_line = docstring_node.lineno - 1  # Convert to 0-indexed
            end_line = docstring_node.end_lineno - 1

            # Replace docstring
            quote_style = '"""'
            if lines[start_line].strip().startswith("'''"):
                quote_style = "'''"

            indent = self._get_indent(lines[start_line])

            # Build new docstring lines
            new_lines = [f"{indent}{quote_style}{new_docstring}\n{indent}{quote_style}\n"]

            # Replace in lines
            lines[start_line : end_line + 1] = new_lines
            modified = True

            logger.debug(
                f"Annotated {node.name} ({method} {full_path}) with {len(annotation.frs)} FRs",
            )

        if not modified:
            return content

        return "".join(lines)

    def _extract_endpoint_decorator(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> tuple[str, str] | None:
        """Extract HTTP method and path from router decorator."""
        for decorator in node.decorator_list:
            # Handle @router.get("/path") or @router.post("/path", ...)
            if not isinstance(decorator, ast.Call):
                continue

            if not isinstance(decorator.func, ast.Attribute):
                continue

            # Check if it's router.METHOD or app.METHOD
            if not isinstance(decorator.func.value, ast.Name):
                continue

            if decorator.func.value.id not in ("router", "app"):
                continue

            method = decorator.func.attr.upper()

            # Extract path from first argument
            if not decorator.args:
                continue

            path_arg = decorator.args[0]
            if isinstance(path_arg, ast.Constant):
                path = path_arg.value
                return (method, path)

        return None

    def _get_indent(self, line: str) -> str:
        """Extract indentation from line."""
        return line[: len(line) - len(line.lstrip())]

    def _extract_router_prefix(self, content: str) -> str:
        """Extract router prefix from file content."""
        # Look for: router = APIRouter(prefix="/api/v1/items", ...)
        match = re.search(r'router\s*=\s*APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return ""


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        help="Process single file (default: all routers)",
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

    # Extract endpoint mappings
    fr_file = root / "docs/reference/FUNCTIONAL_REQUIREMENTS.md"
    extractor = APIEndpointExtractor(fr_file)
    endpoint_mappings = extractor.extract()

    if not endpoint_mappings:
        logger.error("No API endpoint mappings found")
        return 1

    # Initialize annotator
    annotator = EndpointAnnotator(endpoint_mappings)

    # Determine files to process
    if args.file:
        files = [args.file]
    else:
        # Process all router files
        routers_dir = root / "src/tracertm/api/routers"
        if not routers_dir.exists():
            logger.error(f"Routers directory not found: {routers_dir}")
            return 1
        files = list(routers_dir.glob("**/*.py"))

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
            ["ruff", "check", "src/tracertm/api/routers/"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(f"Ruff errors:\n{result.stdout}")
            return 1

        logger.info("✓ Ruff check passed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
