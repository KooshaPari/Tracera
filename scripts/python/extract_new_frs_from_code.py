#!/usr/bin/env python3
"""Extract new functional requirements from code.

This script scans the codebase for:
- New API endpoints not in FR catalog
- New services not mapped to FRs
- New features/capabilities

It generates draft FR entries for review.

Usage:
    python scripts/python/extract_new_frs_from_code.py [options]
    python scripts/python/extract_new_frs_from_code.py --help
    python scripts/python/extract_new_frs_from_code.py --verbose
    python scripts/python/extract_new_frs_from_code.py --output docs/generated/NEW_FRS_DETECTED.md

Run weekly:
    0 0 * * 0 cd /path/to/project && python scripts/python/extract_new_frs_from_code.py
"""

import argparse
import ast
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Pattern matchers
FR_ID_PATTERN = re.compile(r'(FR-[A-Z]+-\d{3})')
FASTAPI_ROUTE_PATTERN = re.compile(r'@router\.(get|post|put|delete|patch)\(.*?["\'](.+?)["\']')


@dataclass
class APIEndpoint:
    """API endpoint detected in code."""
    method: str
    path: str
    file_path: str
    line_number: int
    function_name: str
    has_fr_reference: bool = False
    docstring: str = ""


@dataclass
class Service:
    """Service detected in code."""
    name: str
    file_path: str
    class_name: str
    has_fr_reference: bool = False
    docstring: str = ""
    methods: list[str] = field(default_factory=list)


@dataclass
class DraftFR:
    """Draft functional requirement."""
    suggested_id: str
    title: str
    description: str
    source_type: str  # "api_endpoint" or "service"
    source_file: str
    source_line: int
    confidence: str  # "high", "medium", "low"


class FRExtractor:
    """Extract new functional requirements from code."""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose

        # Paths
        self.fr_status_path = project_root / "docs" / "FUNCTIONAL_REQUIREMENTS_STATUS.json"

        # Known entities
        self.known_fr_ids: set[str] = set()
        self.known_endpoints: set[str] = set()
        self.known_services: set[str] = set()

        # Discovered entities
        self.api_endpoints: list[APIEndpoint] = []
        self.services: list[Service] = []
        self.draft_frs: list[DraftFR] = []

    def log(self, msg: str, level: str = "INFO") -> None:
        """Log message if verbose enabled."""
        if self.verbose:
            prefix = "🔍" if level == "INFO" else "✅" if level == "SUCCESS" else "⚠️"
            print(f"{prefix} {msg}")

    def load_known_entities(self) -> None:
        """Load known FR IDs from FR status file."""
        self.log("Loading known entities...")

        with self.fr_status_path.open("r") as f:
            fr_status = json.load(f)

        # Load known FR IDs
        self.known_fr_ids = set(fr_status["functional_requirements"].keys())

        # Extract known endpoints from code_locations
        for fr in fr_status["functional_requirements"].values():
            for location in fr.get("code_locations", []):
                # Extract file path
                file_path = location.split(":")[0]

                # Track endpoints (routers/)
                if "api/v1/routers" in file_path or "handlers" in file_path:
                    self.known_endpoints.add(file_path)

                # Track services
                if "services/" in file_path and file_path.endswith("_service.py"):
                    service_name = Path(file_path).stem
                    self.known_services.add(service_name)

        self.log(f"Loaded {len(self.known_fr_ids)} known FRs")
        self.log(f"Tracked {len(self.known_endpoints)} known endpoint files")
        self.log(f"Tracked {len(self.known_services)} known services")

    def scan_api_endpoints(self) -> None:
        """Scan API routers for endpoints."""
        self.log("Scanning API endpoints...")

        # Scan Python API routers
        for router_file in self.project_root.glob("src/tracertm/api/v1/routers/**/*.py"):
            self._scan_python_router(router_file)

        # Scan Go handlers
        for handler_file in self.project_root.glob("backend/internal/handlers/**/*.go"):
            self._scan_go_handler(handler_file)

        self.log(f"Found {len(self.api_endpoints)} API endpoints")

        # Count endpoints without FR references
        no_fr_count = sum(1 for ep in self.api_endpoints if not ep.has_fr_reference)
        self.log(f"  {no_fr_count} endpoints have no FR reference")

    def _scan_python_router(self, file_path: Path) -> None:
        """Scan Python router file for endpoints."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for FR references
            has_fr_ref = bool(FR_ID_PATTERN.search(content))

            # Parse AST to find route decorators
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for @router.method decorators
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                method = decorator.func.attr
                                if method in ["get", "post", "put", "delete", "patch"]:
                                    # Extract path from first argument
                                    if decorator.args:
                                        path_arg = decorator.args[0]
                                        if isinstance(path_arg, ast.Constant):
                                            path = path_arg.value

                                            # Get docstring
                                            docstring = ast.get_docstring(node) or ""

                                            endpoint = APIEndpoint(
                                                method=method.upper(),
                                                path=path,
                                                file_path=str(file_path.relative_to(self.project_root)),
                                                line_number=node.lineno,
                                                function_name=node.name,
                                                has_fr_reference=has_fr_ref,
                                                docstring=docstring
                                            )
                                            self.api_endpoints.append(endpoint)

        except Exception as e:
            self.log(f"Error scanning {file_path}: {e}", "WARNING")

    def _scan_go_handler(self, file_path: Path) -> None:
        """Scan Go handler file for endpoints (simplified)."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for FR references
            has_fr_ref = bool(FR_ID_PATTERN.search(content))

            # Simple pattern matching for Go routes
            # r.GET("/path", handler)
            route_pattern = re.compile(r'r\.(GET|POST|PUT|DELETE|PATCH)\("(.+?)",\s*(\w+)\)')

            for match in route_pattern.finditer(content):
                method = match.group(1)
                path = match.group(2)
                handler_name = match.group(3)

                # Find line number
                line_number = content[:match.start()].count("\n") + 1

                endpoint = APIEndpoint(
                    method=method,
                    path=path,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_number,
                    function_name=handler_name,
                    has_fr_reference=has_fr_ref,
                    docstring=""
                )
                self.api_endpoints.append(endpoint)

        except Exception as e:
            self.log(f"Error scanning {file_path}: {e}", "WARNING")

    def scan_services(self) -> None:
        """Scan service files."""
        self.log("Scanning services...")

        # Scan Python services
        for service_file in self.project_root.glob("src/tracertm/services/*_service.py"):
            self._scan_python_service(service_file)

        self.log(f"Found {len(self.services)} services")

        # Count services without FR references
        no_fr_count = sum(1 for svc in self.services if not svc.has_fr_reference)
        self.log(f"  {no_fr_count} services have no FR reference")

    def _scan_python_service(self, file_path: Path) -> None:
        """Scan Python service file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for FR references
            has_fr_ref = bool(FR_ID_PATTERN.search(content))

            # Parse AST to find service class
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.endswith("Service"):
                        # Get docstring
                        docstring = ast.get_docstring(node) or ""

                        # Get method names
                        methods = [
                            m.name for m in node.body
                            if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
                        ]

                        service = Service(
                            name=node.name,
                            file_path=str(file_path.relative_to(self.project_root)),
                            class_name=node.name,
                            has_fr_reference=has_fr_ref,
                            docstring=docstring,
                            methods=methods
                        )
                        self.services.append(service)

        except Exception as e:
            self.log(f"Error scanning {file_path}: {e}", "WARNING")

    def generate_draft_frs(self) -> None:
        """Generate draft FR entries for unmapped code."""
        self.log("Generating draft FRs...")

        # Generate FRs for endpoints without references
        for endpoint in self.api_endpoints:
            if not endpoint.has_fr_reference:
                self._generate_fr_for_endpoint(endpoint)

        # Generate FRs for services without references
        for service in self.services:
            if not service.has_fr_reference:
                self._generate_fr_for_service(service)

        self.log(f"Generated {len(self.draft_frs)} draft FRs")

    def _generate_fr_for_endpoint(self, endpoint: APIEndpoint) -> None:
        """Generate draft FR for API endpoint."""
        # Suggest FR ID based on path
        path_parts = endpoint.path.strip("/").split("/")

        # Determine category from path
        if any(p in ["items", "requirements"] for p in path_parts):
            category = "APP"
        elif any(p in ["graph", "analysis"] for p in path_parts):
            category = "QUAL"
        elif any(p in ["reports", "export"] for p in path_parts):
            category = "RPT"
        elif any(p in ["sync", "webhooks", "integrations"] for p in path_parts):
            category = "COLLAB"
        else:
            category = "APP"

        # Generate title from path and method
        title = self._path_to_title(endpoint.path, endpoint.method)

        # Generate description
        description = endpoint.docstring if endpoint.docstring else f"{endpoint.method} {endpoint.path} endpoint"

        # Determine confidence
        confidence = "medium" if endpoint.docstring else "low"

        draft_fr = DraftFR(
            suggested_id=f"FR-{category}-NEW",
            title=title,
            description=description,
            source_type="api_endpoint",
            source_file=endpoint.file_path,
            source_line=endpoint.line_number,
            confidence=confidence
        )

        self.draft_frs.append(draft_fr)

    def _generate_fr_for_service(self, service: Service) -> None:
        """Generate draft FR for service."""
        # Suggest FR ID based on service name
        service_name = service.name.replace("Service", "").replace("_", " ")

        # Determine category
        if "analysis" in service_name.lower() or "graph" in service_name.lower():
            category = "QUAL"
        elif "report" in service_name.lower() or "export" in service_name.lower():
            category = "RPT"
        elif "sync" in service_name.lower() or "integration" in service_name.lower():
            category = "COLLAB"
        elif "import" in service_name.lower() or "webhook" in service_name.lower():
            category = "DISC"
        else:
            category = "APP"

        # Generate title
        title = service_name.title()

        # Generate description
        description = service.docstring if service.docstring else f"{service.name} provides {service_name.lower()} functionality"

        # Add methods to description
        if service.methods:
            description += f"\n\nKey operations: {', '.join(service.methods[:5])}"

        # Determine confidence
        confidence = "high" if service.docstring else "medium"

        draft_fr = DraftFR(
            suggested_id=f"FR-{category}-NEW",
            title=title,
            description=description,
            source_type="service",
            source_file=service.file_path,
            source_line=1,
            confidence=confidence
        )

        self.draft_frs.append(draft_fr)

    def _path_to_title(self, path: str, method: str) -> str:
        """Convert path to readable title."""
        # Remove leading slash and version
        path = path.strip("/")
        parts = [p for p in path.split("/") if not p.startswith("v")]

        # Remove placeholders
        parts = [p for p in parts if not p.startswith("{") and not p.startswith(":")]

        # Capitalize and join
        title_parts = [p.replace("_", " ").replace("-", " ").title() for p in parts]

        # Add method verb
        method_verb = {
            "GET": "Retrieve",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Modify",
            "DELETE": "Delete"
        }.get(method, method)

        if title_parts:
            return f"{method_verb} {' '.join(title_parts)}"
        else:
            return f"{method_verb} Resource"

    def write_report(self, output_path: Path) -> None:
        """Write NEW_FRS_DETECTED.md report."""
        self.log(f"Writing report to {output_path}...")

        # Group by category
        by_category: dict[str, list[DraftFR]] = {}
        for fr in self.draft_frs:
            category = fr.suggested_id.split("-")[1]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(fr)

        # Generate report
        report = f"""# New Functional Requirements Detected

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Draft FRs:** {len(self.draft_frs)}

---

## Summary

This report identifies code entities (API endpoints and services) that are not currently
mapped to any functional requirement in FUNCTIONAL_REQUIREMENTS_STATUS.json.

| Category | Count | Confidence Distribution |
|----------|-------|------------------------|
"""

        # Summary table
        for category in sorted(by_category.keys()):
            frs = by_category[category]
            high = sum(1 for fr in frs if fr.confidence == "high")
            medium = sum(1 for fr in frs if fr.confidence == "medium")
            low = sum(1 for fr in frs if fr.confidence == "low")
            report += f"| **{category}** | {len(frs)} | High: {high}, Medium: {medium}, Low: {low} |\n"

        report += """
---

## Draft Functional Requirements

Review these drafts and add valid ones to FUNCTIONAL_REQUIREMENTS.md and
FUNCTIONAL_REQUIREMENTS_STATUS.json.

"""

        # Category sections
        category_names = {
            "DISC": "Discovery & Capture",
            "QUAL": "Qualification & Analysis",
            "APP": "Application & Tracking",
            "VERIF": "Verification & Validation",
            "RPT": "Reporting & Analytics",
            "COLLAB": "Collaboration & Integration",
            "AI": "AI & Automation",
            "MCP": "MCP Server"
        }

        for category in sorted(by_category.keys()):
            frs = by_category[category]
            category_name = category_names.get(category, category)

            report += f"""
### {category} - {category_name}

**Count:** {len(frs)} draft FRs

"""

            for i, fr in enumerate(frs, 1):
                confidence_emoji = {
                    "high": "🟢",
                    "medium": "🟡",
                    "low": "🔴"
                }.get(fr.confidence, "⚪")

                report += f"""
#### {i}. {fr.title} {confidence_emoji}

**Suggested ID:** `{fr.suggested_id}-{i:03d}`
**Confidence:** {fr.confidence.upper()}
**Source:** {fr.source_type}
**Location:** `{fr.source_file}:{fr.source_line}`

**Description:**
{fr.description}

**Draft FR Entry:**

```markdown
## {fr.suggested_id}-{i:03d}: {fr.title}

**Status:** Draft
**Epic:** TBD
**User Stories:** []

### Description

{fr.description}

### Implementation

- **Location:** `{fr.source_file}:{fr.source_line}`
- **Type:** {fr.source_type}

### Acceptance Criteria

- [ ] TBD

### Dependencies

- TBD
```

---
"""

        # Footer
        report += """
## Next Steps

1. **Review** each draft FR for accuracy and relevance
2. **Assign** appropriate FR IDs (update numbering)
3. **Link** to Epic IDs and User Stories
4. **Add** to FUNCTIONAL_REQUIREMENTS.md
5. **Update** FUNCTIONAL_REQUIREMENTS_STATUS.json
6. **Annotate** source code with FR references

## Notes

- High confidence FRs have good docstrings and clear purpose
- Medium confidence FRs have minimal documentation
- Low confidence FRs may need investigation before adding

---

*Auto-generated by extract_new_frs_from_code.py*
"""

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write report
        output_path.write_text(report, encoding="utf-8")

        print(f"\n✅ Report written to {output_path}")
        print(f"   {len(self.draft_frs)} draft FRs generated")

        # Print category summary
        print("\n📊 Draft FRs by Category:")
        for category in sorted(by_category.keys()):
            print(f"   {category}: {len(by_category[category])} FRs")

    def extract(self, output_path: Path) -> None:
        """Run extraction process."""
        self.log("=" * 60)
        self.log("Starting FR Extraction from Code")
        self.log("=" * 60)

        # Load known entities
        self.load_known_entities()

        # Scan code
        self.scan_api_endpoints()
        self.scan_services()

        # Generate draft FRs
        self.generate_draft_frs()

        # Write report
        self.write_report(output_path)

        self.log("=" * 60)
        self.log("Extraction Complete", "SUCCESS")
        self.log("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract new functional requirements from code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/extract_new_frs_from_code.py
  python scripts/python/extract_new_frs_from_code.py --verbose
  python scripts/python/extract_new_frs_from_code.py --output docs/NEW_FRS.md

Weekly cron:
  0 0 * * 0 cd /path/to/project && python scripts/python/extract_new_frs_from_code.py
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file path (default: docs/generated/NEW_FRS_DETECTED.md)"
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = project_root / "docs" / "generated" / "NEW_FRS_DETECTED.md"

    # Run extraction
    extractor = FRExtractor(project_root, verbose=args.verbose)
    extractor.extract(output_path)


if __name__ == "__main__":
    main()
