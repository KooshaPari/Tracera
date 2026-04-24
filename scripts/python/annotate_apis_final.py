#!/usr/bin/env python3
"""Final API annotation script with hardcoded prefix mappings.

This script uses a configuration map to handle routers that are mounted
with additional prefixes in main.py.

Usage:
    python scripts/python/annotate_apis_final.py [--dry-run]
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

# Mapping of router file names to their full API prefix
# (combining main.py mounting prefix + router prefix)
ROUTER_PREFIX_MAP = {
    "items.py": "/api/v1/items",
    "features.py": "/api/v1/features",
    "specifications.py": "/api/v1/specifications",  # adrs router
    "integrations.py": "/api/v1/integrations",
    "github.py": "/api/v1/integrations/github",
    "quality.py": "/api/v1/quality",
    "contracts.py": "/api/v1/contracts",
    "adrs.py": "/api/v1/adrs",  # Note: specifications use adrs router
    "item_specs.py": "/api/v1/item-specs",
}


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


class FinalAPIEndpointExtractor:
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
        fr_match = re.search(r"FR-[A-Z]+-\d+", section)
        if not fr_match:
            return []
        fr_id = fr_match.group(0)

        epic_ids = re.findall(r"EPIC-\d+", section)
        user_story_ids = re.findall(r"US-[A-Z]+-\d+", section)

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


class FinalEndpointAnnotator:
    """Annotate API endpoints with FR references using prefix map."""

    def __init__(self, endpoint_mappings: list[EndpointMapping]):
        """Initialize annotator."""
        self.endpoint_mappings = endpoint_mappings
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

        for data in annotation_map.values():
            data.frs = sorted(set(data.frs))
            data.epics = sorted(set(data.epics))
            data.user_stories = sorted(set(data.user_stories))

        return annotation_map

    def annotate_file(self, file_path: Path, dry_run: bool = False) -> int:
        """Annotate single router file. Returns number of endpoints annotated."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 0

        logger.info(f"Processing {file_path.name}")

        original_content = file_path.read_text()

        try:
            tree = ast.parse(original_content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return 0

        # Get full prefix from map
        full_prefix = ROUTER_PREFIX_MAP.get(file_path.name, "")
        if not full_prefix:
            logger.debug(f"No prefix mapping for {file_path.name}")
            return 0

        logger.debug(f"Using full prefix: {full_prefix}")

        modified_content, count = self._annotate_endpoints(original_content, tree, full_prefix)

        if modified_content == original_content:
            logger.debug(f"No changes needed for {file_path.name}")
            return 0

        if dry_run:
            logger.info(f"[DRY RUN] Would update {file_path.name} ({count} endpoints)")
            return count

        file_path.write_text(modified_content)
        logger.info(f"✓ Updated {file_path.name} ({count} endpoints)")
        return count

    def _annotate_endpoints(
        self,
        content: str,
        tree: ast.AST,
        full_prefix: str,
    ) -> tuple[str, int]:
        """Annotate endpoint functions. Returns (modified_content, count)."""
        lines = content.splitlines(keepends=True)
        modified = False
        annotated_count = 0

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue

            endpoint_info = self._extract_endpoint_decorator(node)
            if not endpoint_info:
                continue

            method, decorator_path = endpoint_info

            # Combine full prefix + decorator path
            # Handle "/" decorator path specially
            if decorator_path == "/":
                full_path = full_prefix
            else:
                full_path = full_prefix + decorator_path

            # Normalize {parameter_name} to {id}
            normalized_path = re.sub(r"\{[^}]+\}", "{id}", full_path)

            # Try exact match first, then normalized
            key = (method, full_path)
            normalized_key = (method, normalized_path)

            if key in self.annotation_map:
                annotation = self.annotation_map[key]
            elif normalized_key in self.annotation_map:
                annotation = self.annotation_map[normalized_key]
            else:
                logger.debug(f"No FR mapping for {method} {full_path}")
                continue

            docstring = ast.get_docstring(node)
            if docstring is None:
                logger.warning(f"No docstring for {node.name}, skipping")
                continue

            if "Functional Requirements:" in docstring:
                logger.debug(f"{node.name} already annotated, skipping")
                continue

            # Build annotation
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

            new_docstring = docstring.rstrip() + "\n\n" + "\n".join(sections)

            if not node.body or not isinstance(node.body[0], ast.Expr):
                continue

            docstring_node = node.body[0].value
            if not isinstance(docstring_node, ast.Constant):
                continue

            start_line = docstring_node.lineno - 1
            end_line = docstring_node.end_lineno - 1

            quote_style = '"""'
            if lines[start_line].strip().startswith("'''"):
                quote_style = "'''"

            indent = self._get_indent(lines[start_line])

            new_lines = [f"{indent}{quote_style}{new_docstring}\n{indent}{quote_style}\n"]

            lines[start_line : end_line + 1] = new_lines
            modified = True
            annotated_count += 1

            logger.debug(
                f"Annotated {node.name} ({method} {full_path}) with {len(annotation.frs)} FRs",
            )

        if not modified:
            return content, 0

        return "".join(lines), annotated_count

    def _extract_endpoint_decorator(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> tuple[str, str] | None:
        """Extract HTTP method and path from router decorator."""
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            if not isinstance(decorator.func, ast.Attribute):
                continue

            if not isinstance(decorator.func.value, ast.Name):
                continue

            if decorator.func.value.id != "router":
                continue

            method = decorator.func.attr.upper()

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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing files",
    )
    args = parser.parse_args()

    root = Path.cwd()
    if not (root / "pyproject.toml").exists():
        logger.error("Not in project root (pyproject.toml not found)")
        return 1

    fr_file = root / "docs/reference/FUNCTIONAL_REQUIREMENTS.md"
    extractor = FinalAPIEndpointExtractor(fr_file)
    endpoint_mappings = extractor.extract()

    if not endpoint_mappings:
        logger.error("No API endpoint mappings found")
        return 1

    annotator = FinalEndpointAnnotator(endpoint_mappings)

    routers_dir = root / "src/tracertm/api/routers"
    if not routers_dir.exists():
        logger.error(f"Routers directory not found: {routers_dir}")
        return 1

    # Only process routers in our prefix map
    total_annotated = 0
    for router_name in ROUTER_PREFIX_MAP:
        file_path = routers_dir / router_name
        if file_path.exists():
            count = annotator.annotate_file(file_path, dry_run=args.dry_run)
            total_annotated += count

    logger.info(f"\nTotal endpoints annotated: {total_annotated}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
