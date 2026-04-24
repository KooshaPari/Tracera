#!/usr/bin/env python3
"""
TraceRTM Traceability Link Auto-Discovery Script

This script automatically discovers traceability links between documentation
and code by:
1. Scanning markdown files for FR/Epic/ADR IDs
2. Scanning code for docstring references to requirements
3. Using AST parsing to map definitions to line numbers
4. Matching test file names to source files
5. Building bidirectional link database with confidence scores

Usage:
    python scripts/python/discover_traceability_links.py
    python scripts/python/discover_traceability_links.py --output custom_links.json
    python scripts/python/discover_traceability_links.py --verbose
"""

import ast
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DocReference:
    """Reference to a documentation artifact."""

    type: str  # Epic, FR, ADR, etc.
    id: str  # EPIC-001, FR-DISC-001, ADR-0001
    file: str  # Relative path
    line: int  # Line number
    title: str = ""
    status: str = "Active"


@dataclass
class CodeReference:
    """Reference to a code artifact."""

    type: str  # Model, Service, API, etc.
    name: str  # Fully qualified name
    file: str  # Relative path
    line_start: int
    line_end: int | None = None
    language: str = "python"
    module: str = ""


@dataclass
class TraceLink:
    """A bidirectional traceability link."""

    id: str
    from_ref: DocReference | CodeReference
    to_ref: DocReference | CodeReference
    link_type: str  # traces_to, implements, tested_by, etc.
    confidence: str  # high, medium, low
    auto_discovered: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class TraceLinkDiscoverer:
    """Discovers traceability links between docs and code."""

    # Regex patterns for document IDs
    PATTERNS = {
        "epic": re.compile(r"\b(E\d+(?:\.\d+)?|EPIC-\d+)\b"),
        "fr": re.compile(r"\b(FR-[A-Z]+-\d+)\b"),
        "adr": re.compile(r"\b(ADR-\d{4})\b"),
        "user_story": re.compile(r"\b(US-[A-Z]+-\d+)\b"),
        "req": re.compile(r"\b(REQ-[A-Z]+-\d+)\b"),
    }

    # File path patterns
    CODE_PATTERNS = {
        "python_service": re.compile(r"src/tracertm/services/([a-z_]+)\.py$"),
        "python_model": re.compile(r"src/tracertm/models/([a-z_]+)\.py$"),
        "python_api": re.compile(r"src/tracertm/api/([a-z_]+)\.py$"),
        "go_handler": re.compile(r"backend/internal/handlers/([a-z_]+)\.go$"),
        "test": re.compile(r"tests?/.*/test_([a-z_]+)\.py$"),
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.links: list[TraceLink] = []
        self.doc_refs: dict[str, DocReference] = {}
        self.code_refs: dict[str, CodeReference] = {}

    def discover_all(self) -> list[TraceLink]:
        """Run all discovery phases."""
        print("🔍 Phase 1: Scanning documentation files...")
        self._scan_documentation()

        print(f"📚 Found {len(self.doc_refs)} documentation references")

        print("\n🔍 Phase 2: Scanning code files...")
        self._scan_python_code()

        print(f"💾 Found {len(self.code_refs)} code references")

        print("\n🔍 Phase 3: Extracting explicit links from docs...")
        self._extract_doc_links()

        print("\n🔍 Phase 4: Scanning code for docstring references...")
        self._scan_code_references()

        print("\n🔍 Phase 5: Matching test files to source files...")
        self._match_test_files()

        print(f"\n✅ Total links discovered: {len(self.links)}")
        return self.links

    def _scan_documentation(self) -> None:
        """Scan markdown files for FR/Epic/ADR IDs."""
        doc_dirs = [
            self.project_root / "docs",
        ]

        for doc_dir in doc_dirs:
            if not doc_dir.exists():
                continue

            for md_file in doc_dir.rglob("*.md"):
                self._scan_markdown_file(md_file)

    def _scan_markdown_file(self, file_path: Path) -> None:
        """Scan a single markdown file for IDs."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, start=1):
                # Scan for all ID patterns
                for doc_type, pattern in self.PATTERNS.items():
                    for match in pattern.finditer(line):
                        doc_id = match.group(1)

                        # Extract title from heading
                        title = ""
                        if line.startswith("#"):
                            title = re.sub(r"^#+\s*", "", line).strip()
                            title = re.sub(r"\bFR-[A-Z]+-\d+:\s*", "", title)
                            title = re.sub(r"\bADR-\d{4}:\s*", "", title)

                        ref = DocReference(
                            type=doc_type.replace("_", " ").title(),
                            id=doc_id,
                            file=str(file_path.relative_to(self.project_root)),
                            line=line_num,
                            title=title,
                        )

                        # Store unique references
                        key = f"{ref.type}:{ref.id}:{ref.file}:{ref.line}"
                        if key not in self.doc_refs:
                            self.doc_refs[key] = ref
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def _scan_python_code(self) -> None:
        """Scan Python source files and extract code references."""
        src_dirs = [
            self.project_root / "src" / "tracertm",
        ]

        for src_dir in src_dirs:
            if not src_dir.exists():
                continue

            for py_file in src_dir.rglob("*.py"):
                # Skip test files and __pycache__
                if "__pycache__" in str(py_file) or "test_" in py_file.name:
                    continue

                self._scan_python_file(py_file)

    def _scan_python_file(self, file_path: Path) -> None:
        """Scan a Python file using AST to extract definitions."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            rel_path = str(file_path.relative_to(self.project_root))

            # Determine code type from path
            code_type = "Function"
            if "/services/" in rel_path:
                code_type = "Service"
            elif "/models/" in rel_path:
                code_type = "Model"
            elif "/api/" in rel_path:
                code_type = "API"

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    ref = CodeReference(
                        type="Class" if code_type == "Function" else code_type,
                        name=node.name,
                        file=rel_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        language="python",
                        module=self._get_module_name(file_path),
                    )
                    key = f"{ref.name}:{ref.file}:{ref.line_start}"
                    self.code_refs[key] = ref

                elif isinstance(node, ast.FunctionDef):
                    ref = CodeReference(
                        type="Function",
                        name=node.name,
                        file=rel_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        language="python",
                        module=self._get_module_name(file_path),
                    )
                    key = f"{ref.name}:{ref.file}:{ref.line_start}"
                    self.code_refs[key] = ref

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Extract module name from file path."""
        rel_path = file_path.relative_to(self.project_root)
        parts = list(rel_path.parts)

        # Remove src/ prefix if present
        if parts and parts[0] == "src":
            parts = parts[1:]

        # Remove .py extension
        if parts:
            parts[-1] = parts[-1].replace(".py", "")

        return ".".join(parts)

    def _extract_doc_links(self) -> None:
        """Extract explicit links from documentation (Traces to:, Implemented in:, etc.)."""
        for md_file in self.project_root.glob("docs/**/*.md"):
            self._extract_links_from_doc(md_file)

    def _extract_links_from_doc(self, file_path: Path) -> None:
        """Extract links from a single documentation file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            current_fr: str | None = None

            for line_num, line in enumerate(lines, start=1):
                # Check if this is an FR heading
                fr_match = self.PATTERNS["fr"].search(line)
                if fr_match and line.startswith("#"):
                    current_fr = fr_match.group(0)
                    continue

                if not current_fr:
                    continue

                # Look for "Traces to:" section
                if line.startswith("**Traces to:**"):
                    # Read next few lines for Epic/User Story references
                    for i in range(1, min(10, len(lines) - line_num)):
                        next_line = lines[line_num + i]

                        # Stop if we hit another section
                        if next_line.startswith("**") and "**Traces to:**" not in next_line:
                            break

                        # Extract Epic references (EPIC-NNN format)
                        epic_match = re.search(r'\b(EPIC-\d+)\b', next_line)
                        if epic_match:
                            self._create_link(
                                from_id=current_fr,
                                from_type="FR",
                                to_id=epic_match.group(1),
                                to_type="Epic",
                                link_type="traces_to",
                                confidence="high",
                                source_file=str(
                                    file_path.relative_to(self.project_root)
                                ),
                                source_line=line_num + i,
                            )

                        # Extract User Story references
                        us_match = re.search(r'\b(US-[A-Z]+-\d+)\b', next_line)
                        if us_match:
                            self._create_link(
                                from_id=current_fr,
                                from_type="FR",
                                to_id=us_match.group(1),
                                to_type="User Story",
                                link_type="traces_to",
                                confidence="high",
                                source_file=str(
                                    file_path.relative_to(self.project_root)
                                ),
                                source_line=line_num + i,
                            )

                # Look for "Implemented in:" section
                if line.startswith("**Implemented in:**"):
                    for i in range(1, min(5, len(lines) - line_num)):
                        next_line = lines[line_num + i]

                        # Extract file references like `src/tracertm/services/github_import_service.py:1-350`
                        file_match = re.search(
                            r"`(src/tracertm/[^:]+\.py):(\d+)-(\d+)`", next_line
                        )
                        if file_match:
                            file_ref, start_line, end_line = file_match.groups()
                            self._create_code_link(
                                from_id=current_fr,
                                from_type="FR",
                                to_file=file_ref,
                                to_line_start=int(start_line),
                                to_line_end=int(end_line),
                                link_type="implements",
                                confidence="high",
                                source_file=str(
                                    file_path.relative_to(self.project_root)
                                ),
                                source_line=line_num + i,
                            )

                # Look for "Tested in:" section
                if line.startswith("**Tested in:**"):
                    for i in range(1, min(5, len(lines) - line_num)):
                        next_line = lines[line_num + i]

                        # Extract test references
                        test_match = re.search(
                            r"`(tests/[^:]+\.py)::(test_\w+)`", next_line
                        )
                        if test_match:
                            test_file, test_name = test_match.groups()
                            self._create_test_link(
                                from_id=current_fr,
                                from_type="FR",
                                to_file=test_file,
                                to_test=test_name,
                                link_type="tested_by",
                                confidence="high",
                                source_file=str(
                                    file_path.relative_to(self.project_root)
                                ),
                                source_line=line_num + i,
                            )

        except Exception as e:
            print(f"⚠️  Error extracting links from {file_path}: {e}")

    def _scan_code_references(self) -> None:
        """Scan code docstrings for references to documentation IDs."""
        for py_file in (self.project_root / "src" / "tracertm").rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            self._scan_code_for_doc_refs(py_file)

    def _scan_code_for_doc_refs(self, file_path: Path) -> None:
        """Scan a Python file for docstring references to FR/ADR/Epic."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, start=1):
                # Skip non-comment/docstring lines
                if not ("\"\"\"" in line or "#" in line):
                    continue

                # Check for FR/ADR/Epic references in comments
                for doc_type, pattern in self.PATTERNS.items():
                    for match in pattern.finditer(line):
                        doc_id = match.group(1)

                        # Find the code element this belongs to
                        code_ref = self._find_code_ref_at_line(file_path, line_num)
                        if code_ref:
                            self._create_doc_to_code_link(
                                from_id=doc_id,
                                from_type=doc_type.replace("_", " ").title(),
                                to_code_ref=code_ref,
                                link_type="implements",
                                confidence="medium",
                                source_file=str(
                                    file_path.relative_to(self.project_root)
                                ),
                                source_line=line_num,
                            )

        except Exception as e:
            print(f"⚠️  Error scanning {file_path} for doc refs: {e}")

    def _find_code_ref_at_line(
        self, file_path: Path, line_num: int
    ) -> CodeReference | None:
        """Find the code reference that contains the given line number."""
        rel_path = str(file_path.relative_to(self.project_root))

        for key, ref in self.code_refs.items():
            if ref.file == rel_path and ref.line_start <= line_num <= (
                ref.line_end or ref.line_start
            ):
                return ref

        return None

    def _match_test_files(self) -> None:
        """Match test files to source files based on naming conventions."""
        test_dir = self.project_root / "tests"
        if not test_dir.exists():
            return

        for test_file in test_dir.rglob("test_*.py"):
            # Extract module name from test file
            test_name = test_file.stem.replace("test_", "")

            # Find corresponding source file
            for code_key, code_ref in self.code_refs.items():
                if test_name in code_ref.file:
                    # Create tested_by link
                    link = TraceLink(
                        id=str(uuid.uuid4()),
                        from_ref=code_ref,
                        to_ref=CodeReference(
                            type="Test",
                            name=test_file.stem,
                            file=str(test_file.relative_to(self.project_root)),
                            line_start=1,
                            language="python",
                        ),
                        link_type="tested_by",
                        confidence="medium",
                        auto_discovered=True,
                        metadata={
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "created_by": "auto_discovery",
                            "match_pattern": "file_name_match",
                        },
                    )
                    self.links.append(link)

    def _create_link(
        self,
        from_id: str,
        from_type: str,
        to_id: str,
        to_type: str,
        link_type: str,
        confidence: str,
        source_file: str,
        source_line: int,
    ) -> None:
        """Create a link between two documentation references."""
        # Find from_ref
        from_ref = None
        for ref in self.doc_refs.values():
            if ref.id == from_id:
                from_ref = ref
                break

        # Find to_ref
        to_ref = None
        for ref in self.doc_refs.values():
            if ref.id == to_id:
                to_ref = ref
                break

        if from_ref and to_ref:
            link = TraceLink(
                id=str(uuid.uuid4()),
                from_ref=from_ref,
                to_ref=to_ref,
                link_type=link_type,
                confidence=confidence,
                auto_discovered=True,
                metadata={
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "auto_discovery",
                    "source_line": source_line,
                    "source_file": source_file,
                },
            )
            self.links.append(link)

    def _create_code_link(
        self,
        from_id: str,
        from_type: str,
        to_file: str,
        to_line_start: int,
        to_line_end: int,
        link_type: str,
        confidence: str,
        source_file: str,
        source_line: int,
    ) -> None:
        """Create a link from documentation to code."""
        # Find from_ref
        from_ref = None
        for ref in self.doc_refs.values():
            if ref.id == from_id:
                from_ref = ref
                break

        if from_ref:
            to_ref = CodeReference(
                type="Service",
                name=Path(to_file).stem,
                file=to_file,
                line_start=to_line_start,
                line_end=to_line_end,
                language="python",
            )

            link = TraceLink(
                id=str(uuid.uuid4()),
                from_ref=from_ref,
                to_ref=to_ref,
                link_type=link_type,
                confidence=confidence,
                auto_discovered=True,
                metadata={
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "auto_discovery",
                    "source_line": source_line,
                    "source_file": source_file,
                },
            )
            self.links.append(link)

    def _create_test_link(
        self,
        from_id: str,
        from_type: str,
        to_file: str,
        to_test: str,
        link_type: str,
        confidence: str,
        source_file: str,
        source_line: int,
    ) -> None:
        """Create a link from documentation to test."""
        # Find from_ref
        from_ref = None
        for ref in self.doc_refs.values():
            if ref.id == from_id:
                from_ref = ref
                break

        if from_ref:
            to_ref = CodeReference(
                type="Test",
                name=to_test,
                file=to_file,
                line_start=1,
                language="python",
            )

            link = TraceLink(
                id=str(uuid.uuid4()),
                from_ref=from_ref,
                to_ref=to_ref,
                link_type=link_type,
                confidence=confidence,
                auto_discovered=True,
                metadata={
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "auto_discovery",
                    "source_line": source_line,
                    "source_file": source_file,
                },
            )
            self.links.append(link)

    def _create_doc_to_code_link(
        self,
        from_id: str,
        from_type: str,
        to_code_ref: CodeReference,
        link_type: str,
        confidence: str,
        source_file: str,
        source_line: int,
    ) -> None:
        """Create a link from documentation to code reference."""
        # Find from_ref
        from_ref = None
        for ref in self.doc_refs.values():
            if ref.id == from_id:
                from_ref = ref
                break

        if from_ref:
            link = TraceLink(
                id=str(uuid.uuid4()),
                from_ref=from_ref,
                to_ref=to_code_ref,
                link_type=link_type,
                confidence=confidence,
                auto_discovered=True,
                metadata={
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "auto_discovery",
                    "source_line": source_line,
                    "source_file": source_file,
                },
            )
            self.links.append(link)

    def to_json(self) -> dict[str, Any]:
        """Convert link database to JSON format."""

        def ref_to_dict(ref: DocReference | CodeReference) -> dict[str, Any]:
            if isinstance(ref, DocReference):
                return {
                    "type": ref.type,
                    "id": ref.id,
                    "file": ref.file,
                    "line": ref.line,
                    "title": ref.title,
                    "status": ref.status,
                }
            else:
                result: dict[str, Any] = {
                    "type": ref.type,
                    "name": ref.name,
                    "file": ref.file,
                    "line_start": ref.line_start,
                    "language": ref.language,
                }
                if ref.line_end:
                    result["line_end"] = ref.line_end
                if ref.module:
                    result["module"] = ref.module
                return result

        links_json = []
        for link in self.links:
            links_json.append(
                {
                    "id": link.id,
                    "from": ref_to_dict(link.from_ref),
                    "to": ref_to_dict(link.to_ref),
                    "linkType": link.link_type,
                    "confidence": link.confidence,
                    "auto_discovered": link.auto_discovered,
                    "metadata": link.metadata,
                }
            )

        # Calculate statistics
        link_types = {}
        confidence_levels = {"high": 0, "medium": 0, "low": 0}
        auto_count = 0

        for link in self.links:
            link_types[link.link_type] = link_types.get(link.link_type, 0) + 1
            confidence_levels[link.confidence] += 1
            if link.auto_discovered:
                auto_count += 1

        return {
            "version": "1.0.0",
            "project": {
                "name": "TraceRTM",
                "id": "tracertm",
                "description": "Requirements Traceability Matrix System",
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "links": links_json,
            "statistics": {
                "total_links": len(self.links),
                "by_type": link_types,
                "by_confidence": confidence_levels,
                "auto_discovered_count": auto_count,
                "manual_count": len(self.links) - auto_count,
            },
        }


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-discover traceability links between docs and code"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs/generated/traceability_links.json",
        help="Output file path (default: docs/generated/traceability_links.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    args = parser.parse_args()

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent

    print(f"📂 Project root: {project_root}")

    # Run discovery
    discoverer = TraceLinkDiscoverer(project_root)
    links = discoverer.discover_all()

    # Save to JSON
    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    link_db = discoverer.to_json()

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(link_db, f, indent=2)

    print(f"\n💾 Saved {len(links)} links to {output_path}")
    print("\n📊 Statistics:")
    print(f"  Total links: {link_db['statistics']['total_links']}")
    print(f"  By type: {link_db['statistics']['by_type']}")
    print(f"  By confidence: {link_db['statistics']['by_confidence']}")
    print(
        f"  Auto-discovered: {link_db['statistics']['auto_discovered_count']} ({link_db['statistics']['auto_discovered_count'] / max(1, link_db['statistics']['total_links']) * 100:.1f}%)"
    )


if __name__ == "__main__":
    main()
