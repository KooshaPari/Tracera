#!/usr/bin/env python3
"""Extract cross-links from all codebase artifacts into structured database.

This script scans Python modules, test files, and documentation to extract
all cross-link metadata and build a comprehensive cross_links.json database.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_extract_cross_links.py
Docs: docs/EXTENDED_CROSS_LINKING.md
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml


PROJECT_ROOT = Path(__file__).parent.parent


class CrossLinkExtractor:
    """Extract and organize cross-links from codebase."""

    def __init__(self):
        self.links_db = {
            "modules": {},
            "tests": {},
            "docs": {},
            "specs": {},
            "stories": {},
            "adrs": {},
            "index": {
                "by_spec": {},
                "by_story": {},
                "by_state": {},
                "by_tag": {},
            },
        }

    def extract_python_module_links(self, file_path: Path) -> Dict:
        """Extract all metadata and links from Python module docstring."""
        try:
            with open(file_path) as f:
                content = f.read()

            # Parse AST to get module docstring
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if not docstring:
                return {}

            module_id = str(file_path.relative_to(PROJECT_ROOT))
            links = {
                "id": module_id,
                "type": "module",
                "path": module_id,
                "links": {},
            }

            # Extract all metadata fields using regex patterns
            patterns = {
                # Core
                "state": r"State:\s*(\w+)",
                "since": r"Since:\s*([\d.]+)",
                "version_changed": r"Version_Changed:\s*([\d.]+)\s*\((.*?)\)",
                # Specifications
                "specs": r"Specs:\s*([^\n]+)",
                "specified_by": r"Specified_By:\s*([^\n]+)",
                # User Stories
                "stories": r"Stories:\s*([^\n]+)",
                "implements": r"Implements:\s*([^\n]+)",
                # Tests
                "tests": r"Tests:\s*([^\n]+)",
                "verified_by": r"Verified_By:\s*([^\n]+)",
                "coverage": r"Coverage:\s*([\d.]+%?)",
                # Documentation
                "docs": r"Docs:\s*([^\n]+)",
                "explained_by": r"Explained_By:\s*([^\n]+)",
                "demonstrated_by": r"Demonstrated_By:\s*([^\n]+)",
                "guides": r"Guides:\s*([^\n]+)",
                "references": r"References:\s*([^\n]+)",
                # Decisions
                "decided_by": r"Decided_By:\s*([^\n]+)",
                "adr": r"ADR:\s*([^\n]+)",
                # Code Structure
                "depends_on": r"Depends_On:\s*([^\n]+)",
                "imports": r"Imports:\s*([^\n]+)",
                "exports": r"Exports:\s*([^\n]+)",
                "extends": r"Extends:\s*([^\n]+)",
                "inherits_from": r"Inherits_From:\s*([^\n]+)",
                "composed_of": r"Composed_Of:\s*([^\n]+)",
                "implements_interface": r"Implements_Interface:\s*([^\n]+)",
                # Relationships
                "supersedes": r"Supersedes:\s*([^\n]+)",
                "conflicts_with": r"Conflicts_With:\s*([^\n]+)",
                "migrates_from": r"Migrates_From:\s*([^\n]+)",
                "prerequisite_of": r"Prerequisite_Of:\s*([^\n]+)",
                "alternative_to": r"Alternative_To:\s*([^\n]+)",
                # Events & Exceptions
                "raises": r"Raises:\s*([^\n]+)",
                "handles": r"Handles:\s*([^\n]+)",
                "emits": r"Emits:\s*([^\n]+)",
                "listens_to": r"Listens_To:\s*([^\n]+)",
                # Issues & Planning
                "requested_by": r"Requested_By:\s*([^\n]+)",
                "approved_by": r"Approved_By:\s*([^\n]+)",
                "roadmap": r"Roadmap:\s*([^\n]+)",
                # Metadata
                "tags": r"Tags:\s*([^\n]+)",
                "keywords": r"Keywords:\s*([^\n]+)",
                # Performance
                "performance": r"Performance:\s*([^\n]+)",
                "benchmarks": r"Benchmarks:\s*([^\n]+)",
                # Security
                "security": r"Security:\s*([^\n]+)",
                "vulnerability_id": r"Vulnerability_ID:\s*([^\n]+)",
                # External
                "pypi": r"PyPI:\s*([^\n]+)",
                "github": r"GitHub:\s*([^\n]+)",
                "stackoverflow": r"StackOverflow:\s*([^\n]+)",
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, docstring)
                if match:
                    value = match.group(1).strip()
                    # Split comma-separated values for list fields
                    if field in ["specs", "stories", "tests", "docs", "tags", "keywords",
                                 "depends_on", "imports", "exports", "raises", "handles",
                                 "emits", "listens_to", "guides", "references"]:
                        links["links"][field] = [v.strip() for v in value.split(",")]
                    else:
                        links["links"][field] = value

            return links if links["links"] else {}

        except Exception as e:
            print(f"Error extracting from {file_path}: {e}")
            return {}

    def extract_test_file_links(self, file_path: Path) -> Dict:
        """Extract pytest markers and metadata from test files."""
        try:
            with open(file_path) as f:
                content = f.read()

            test_id = str(file_path.relative_to(PROJECT_ROOT))
            links = {
                "id": test_id,
                "type": "test",
                "path": test_id,
                "links": {},
                "functions": {},
            }

            # Extract module-level metadata
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                spec_match = re.search(r"Specs?:\s*([^\n]+)", docstring)
                story_match = re.search(r"Stories?:\s*([^\n]+)", docstring)
                if spec_match:
                    links["links"]["specs"] = [s.strip() for s in spec_match.group(1).split(",")]
                if story_match:
                    links["links"]["stories"] = [s.strip() for s in story_match.group(1).split(",")]

            # Extract pytest markers from test functions
            marker_pattern = r'@pytest\.mark\.(spec|story|feature)\(["\']([^"\']+)["\']\)\s*\n\s*(?:@pytest\.mark\.\w+.*\n\s*)*def\s+(test_\w+)'
            for match in re.finditer(marker_pattern, content):
                marker_type = match.group(1)
                marker_value = match.group(2)
                func_name = match.group(3)

                if func_name not in links["functions"]:
                    links["functions"][func_name] = {}

                if marker_type not in links["functions"][func_name]:
                    links["functions"][func_name][marker_type] = []
                links["functions"][func_name][marker_type].append(marker_value)

            return links if (links["links"] or links["functions"]) else {}

        except Exception as e:
            print(f"Error extracting from {file_path}: {e}")
            return {}

    def extract_mdx_frontmatter_links(self, file_path: Path) -> Dict:
        """Extract frontmatter metadata from MDX files."""
        try:
            with open(file_path) as f:
                content = f.read()

            if not content.startswith("---"):
                return {}

            # Find end of frontmatter
            end_idx = content.find("\n---\n", 3)
            if end_idx == -1:
                end_idx = content.find("\n---", 3)
                if end_idx == -1:
                    return {}

            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(content[3:end_idx])
            if not frontmatter:
                return {}

            doc_id = str(file_path.relative_to(PROJECT_ROOT))
            links = {
                "id": doc_id,
                "type": "doc",
                "path": doc_id,
                "links": frontmatter,
            }

            return links

        except Exception as e:
            print(f"Error extracting from {file_path}: {e}")
            return {}

    def extract_markdown_frontmatter_links(self, file_path: Path) -> Dict:
        """Extract frontmatter metadata from Markdown files."""
        # Same logic as MDX
        return self.extract_mdx_frontmatter_links(file_path)

    def build_database(self):
        """Scan entire codebase and build cross-link database."""
        print("=" * 70)
        print("Building Cross-Link Database")
        print("=" * 70)
        print()

        # Extract from Python modules
        print("Extracting from Python modules...")
        py_files = list(PROJECT_ROOT.glob("src/**/*.py"))
        py_count = 0
        for py_file in py_files:
            if py_file.name == "__init__.py" or py_file.name.startswith("_"):
                continue
            links = self.extract_python_module_links(py_file)
            if links:
                self.links_db["modules"][links["id"]] = links
                py_count += 1
        print(f"  ✓ Extracted {py_count} modules")

        # Extract from test files
        print("Extracting from test files...")
        test_files = list(PROJECT_ROOT.glob("tests/**/test_*.py"))
        test_count = 0
        for test_file in test_files:
            links = self.extract_test_file_links(test_file)
            if links:
                self.links_db["tests"][links["id"]] = links
                test_count += 1
        print(f"  ✓ Extracted {test_count} test files")

        # Extract from MDX files
        print("Extracting from MDX files...")
        mdx_files = list(PROJECT_ROOT.glob("apps/docs/content/docs/**/*.mdx"))
        mdx_count = 0
        for mdx_file in mdx_files:
            links = self.extract_mdx_frontmatter_links(mdx_file)
            if links:
                self.links_db["docs"][links["id"]] = links
                mdx_count += 1
        print(f"  ✓ Extracted {mdx_count} MDX files")

        # Extract from Markdown files
        print("Extracting from Markdown files...")
        md_files = list(PROJECT_ROOT.glob("docs/**/*.md"))
        md_count = 0
        for md_file in md_files:
            # Skip navigation/meta docs
            if md_file.name in ["NAVIGATION_HUB.md", "MASTER_INDEX.md", "STATE_MODEL.md",
                                 "TEMPORAL_VIEW.md", "CROSS_REFERENCE_GRAPH.md", "TRACEABILITY_MATRIX.md"]:
                continue
            links = self.extract_markdown_frontmatter_links(md_file)
            if links:
                self.links_db["docs"][links["id"]] = links
                md_count += 1
        print(f"  ✓ Extracted {md_count} Markdown files")

        print()
        print("Building indexes...")
        self._build_indexes()
        print("  ✓ Indexes built")
        print()

        return self.links_db

    def _build_indexes(self):
        """Build reverse indexes for fast lookups."""
        # Index by spec
        for module_id, module in self.links_db["modules"].items():
            specs = module["links"].get("specs", [])
            for spec in specs:
                if spec not in self.links_db["index"]["by_spec"]:
                    self.links_db["index"]["by_spec"][spec] = []
                self.links_db["index"]["by_spec"][spec].append({
                    "type": "module",
                    "id": module_id,
                })

        for test_id, test in self.links_db["tests"].items():
            specs = test["links"].get("specs", [])
            for spec in specs:
                if spec not in self.links_db["index"]["by_spec"]:
                    self.links_db["index"]["by_spec"][spec] = []
                self.links_db["index"]["by_spec"][spec].append({
                    "type": "test",
                    "id": test_id,
                })

        # Index by story
        for module_id, module in self.links_db["modules"].items():
            stories = module["links"].get("stories", [])
            for story in stories:
                if story not in self.links_db["index"]["by_story"]:
                    self.links_db["index"]["by_story"][story] = []
                self.links_db["index"]["by_story"][story].append({
                    "type": "module",
                    "id": module_id,
                })

        # Index by state
        for module_id, module in self.links_db["modules"].items():
            state = module["links"].get("state")
            if state:
                if state not in self.links_db["index"]["by_state"]:
                    self.links_db["index"]["by_state"][state] = []
                self.links_db["index"]["by_state"][state].append({
                    "type": "module",
                    "id": module_id,
                })

        # Index by tag
        for doc_id, doc in self.links_db["docs"].items():
            tags = doc["links"].get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if tag not in self.links_db["index"]["by_tag"]:
                        self.links_db["index"]["by_tag"][tag] = []
                    self.links_db["index"]["by_tag"][tag].append({
                        "type": "doc",
                        "id": doc_id,
                    })

    def save_database(self, output_path: Path):
        """Save cross-link database to JSON file."""
        with open(output_path, "w") as f:
            json.dump(self.links_db, f, indent=2, sort_keys=True)
        print(f"Database saved to: {output_path}")


def main():
    """Run cross-link extraction."""
    extractor = CrossLinkExtractor()
    db = extractor.build_database()

    # Save to JSON
    output_path = PROJECT_ROOT / "docs" / "cross_links.json"
    extractor.save_database(output_path)

    # Print summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Modules: {len(db['modules'])}")
    print(f"  Tests: {len(db['tests'])}")
    print(f"  Docs: {len(db['docs'])}")
    print(f"  Specs indexed: {len(db['index']['by_spec'])}")
    print(f"  Stories indexed: {len(db['index']['by_story'])}")
    print(f"  States indexed: {len(db['index']['by_state'])}")
    print(f"  Tags indexed: {len(db['index']['by_tag'])}")
    print()
    print("✅ Cross-link database extraction complete!")
    print()
    print("Next steps:")
    print("  1. Review: cat docs/cross_links.json")
    print("  2. Generate docs: python scripts/generate_spec_coverage.py")
    print("  3. Validate links: python scripts/validate_links.py")


if __name__ == "__main__":
    main()
