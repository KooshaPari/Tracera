"""Stateless ingestion service for MD/MDX/YAML/OpenSpec/BMad formats."""

import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from sqlalchemy.orm import Session

# Lazy imports for optional dependencies
try:
    import frontmatter
except ImportError:
    frontmatter = None

try:
    from markdown import Markdown
    from markdown_it import MarkdownIt
except ImportError:
    Markdown = None
    MarkdownIt = None

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class StatelessIngestionService:
    """Service for stateless ingestion of MD/MDX/YAML/OpenSpec/BMad files."""

    def __init__(self, session: Session):
        self.session = session
        if MarkdownIt:
            self.md_parser = MarkdownIt()
        else:
            self.md_parser = None
        if Markdown:
            self.markdown = Markdown()
        else:
            self.markdown = None

    def ingest_markdown(
        self,
        file_path: str,
        project_id: str | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Ingest a Markdown file (with optional frontmatter).

        Supports:
        - Frontmatter metadata (YAML)
        - Headers as hierarchical items
        - Links in markdown format
        - Code blocks

        Args:
            file_path: Path to markdown file
            project_id: Optional project ID (creates project if not provided)
            view: Target view for items
            dry_run: If True, validate but don't create items
            validate: If True, validate file before ingestion

        Returns:
            Dictionary with ingestion results
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file
        if validate and path.suffix.lower() not in [".md", ".markdown", ".mdx"]:
            raise ValueError(f"Invalid file extension: {path.suffix}. Expected .md, .markdown, or .mdx")

        content = path.read_text(encoding="utf-8")

        if dry_run:
            # Just validate and return what would be created
            header_count = len(re.findall(r"^(#{1,6})\s+", content, re.MULTILINE))
            link_count = len(re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content))
            return {
                "dry_run": True,
                "headers_found": header_count,
                "links_found": link_count,
                "would_create_items": header_count,
                "would_create_links": link_count,
            }

        # Parse frontmatter if present
        if frontmatter:
            try:
                post = frontmatter.loads(content)
                metadata = post.metadata
                body = post.content
            except Exception:
                # No frontmatter, treat entire file as body
                metadata = {}
                body = content
        else:
            # No frontmatter library, treat entire file as body
            metadata = {}
            body = content

        # Get or create project
        if not project_id:
            project_name = metadata.get("project", path.stem)
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                project = Project(
                    id=str(uuid4()),
                    name=project_name,
                    description=metadata.get("description", ""),
                )
                self.session.add(project)
                self.session.flush()
            project_id = project.id
        else:
            project = self.session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project not found: {project_id}")

        # Parse markdown structure
        items_created = []
        links_created = []

        # Extract headers as items
        header_pattern = r"^(#{1,6})\s+(.+)$"
        headers = []
        parent_stack: list[str | None] = [None]

        for line in body.split("\n"):
            match = re.match(header_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                # Adjust parent stack based on level
                while len(parent_stack) > level:
                    parent_stack.pop()
                if len(parent_stack) < level:
                    parent_stack.extend([None] * (level - len(parent_stack)))

                parent_id = parent_stack[-1] if parent_stack else None

                # Determine item type based on level
                item_type = self._determine_item_type(level, metadata)

                # Create item
                item = Item(
                    id=str(uuid4()),
                    project_id=project_id,
                    title=title,
                    view=view,
                    item_type=item_type,
                    status=metadata.get("status", "todo"),
                    description=self._extract_section_content(body, line),
                    item_metadata={
                        "source_file": str(path),
                        "header_level": level,
                        **metadata,
                    },
                    parent_id=parent_id,
                    version=1,
                )
                self.session.add(item)
                self.session.flush()

                items_created.append(item.id)
                headers.append((level, item.id, title))

                # Update parent stack
                if len(parent_stack) <= level:
                    parent_stack.append(item.id)
                else:
                    parent_stack[level - 1] = item.id

        # Extract markdown links
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        for match in re.finditer(link_pattern, body):
            match.group(1)
            link_url = match.group(2)

            # Try to find source item (item containing this link)
            # For simplicity, link to the last created item
            if items_created:
                source_id = items_created[-1]

                # If link_url is an internal reference (starts with #), try to find target
                if link_url.startswith("#"):
                    target_title = link_url[1:].replace("-", " ").title()
                    # Try to find matching header
                    for level, item_id, title in headers:
                        if title.lower() == target_title.lower():
                            link = Link(
                                id=str(uuid4()),
                                project_id=project_id,
                                source_item_id=source_id,
                                target_item_id=item_id,
                                link_type="relates_to",
                            )
                            self.session.add(link)
                            links_created.append((source_id, item_id))

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": len(links_created),
            "file_path": str(path),
        }

    def ingest_mdx(
        self,
        file_path: str,
        project_id: str | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Ingest an MDX file (Markdown with JSX components).

        Similar to markdown but handles JSX components in code blocks.

        Args:
            file_path: Path to MDX file
            project_id: Optional project ID
            view: Target view for items
            dry_run: If True, validate but don't create items
            validate: If True, validate file before ingestion

        Returns:
            Dictionary with ingestion results
        """
        # MDX is similar to Markdown, but we need to handle JSX
        # For MVP, treat as markdown and extract JSX components separately
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file
        if validate and path.suffix.lower() not in [".mdx"]:
            raise ValueError(f"Invalid file extension: {path.suffix}. Expected .mdx")

        content = path.read_text(encoding="utf-8")

        if dry_run:
            # Count what would be created
            header_count = len(re.findall(r"^(#{1,6})\s+", content, re.MULTILINE))
            jsx_count = len(re.findall(r"<(\w+)([^>]*)>", content))
            return {
                "dry_run": True,
                "headers_found": header_count,
                "jsx_components_found": jsx_count,
                "would_create_items": header_count + jsx_count,
            }

        # Parse frontmatter
        if frontmatter:
            try:
                post = frontmatter.loads(content)
                metadata = post.metadata
                body = post.content
            except Exception:
                metadata = {}
                body = content
        else:
            metadata = {}
            body = content

        # Extract JSX components (basic pattern matching)
        jsx_pattern = r"<(\w+)([^>]*)>([^<]*)</\1>"
        jsx_components = re.findall(jsx_pattern, body)

        # Get or create project
        if not project_id:
            project_name = metadata.get("project", path.stem)
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                project = Project(
                    id=str(uuid4()),
                    name=project_name,
                    description=metadata.get("description", ""),
                )
                self.session.add(project)
                self.session.flush()
            project_id = project.id

        # Process as markdown first
        result = self.ingest_markdown(file_path, project_id, view)

        # Add JSX components as CODE view items
        items_created = []
        for component_name, attrs, content in jsx_components:
            item = Item(
                id=str(uuid4()),
                project_id=project_id,
                title=f"{component_name} Component",
                view="CODE",
                item_type="component",
                status="todo",
                description=content.strip(),
                item_metadata={
                    "source_file": str(path),
                    "component_name": component_name,
                    "attributes": attrs,
                    "format": "mdx",
                },
                version=1,
            )
            self.session.add(item)
            self.session.flush()
            items_created.append(item.id)

        result["jsx_components_created"] = len(items_created)
        return result

    def ingest_yaml(
        self,
        file_path: str,
        project_id: str | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Ingest a YAML file.

        Supports:
        - OpenAPI/Swagger specs
        - Generic YAML structures
        - BMad format (if detected)

        Args:
            file_path: Path to YAML file
            project_id: Optional project ID
            view: Target view for items
            dry_run: If True, validate but don't create items
            validate: If True, validate file before ingestion

        Returns:
            Dictionary with ingestion results
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file
        if validate and path.suffix.lower() not in [".yaml", ".yml"]:
            raise ValueError(f"Invalid file extension: {path.suffix}. Expected .yaml or .yml")

        content = path.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        if not isinstance(data, dict):
            raise ValueError("YAML root must be a dictionary")

        # Detect format
        format_type = "yaml"
        if "openapi" in data or "swagger" in data:
            format_type = "openapi"
        elif "bmad" in str(path).lower() or "bmad" in data or "requirements" in data or ("spec" in data and "requirements" in data.get("spec", {})):
            format_type = "bmad"

        if dry_run:
            # Estimate what would be created
            if format_type == "openapi":
                paths = data.get("paths", {})
                schemas = data.get("components", {}).get("schemas", {})
                return {
                    "dry_run": True,
                    "format": "openapi",
                    "endpoints_found": sum(len([m for m in methods if not m.startswith("x-")]) for methods in paths.values()),
                    "schemas_found": len(schemas),
                    "would_create_items": sum(len([m for m in methods if not m.startswith("x-")]) for methods in paths.values()) + len(schemas),
                }
            elif format_type == "bmad":
                requirements = data.get("requirements", []) or data.get("spec", {}).get("requirements", [])
                return {
                    "dry_run": True,
                    "format": "bmad",
                    "requirements_found": len(requirements),
                    "would_create_items": len(requirements),
                }
            else:
                # Generic YAML - estimate from structure
                def count_items(d):
                    count = 0
                    if isinstance(d, dict):
                        count += len(d)
                        for v in d.values():
                            count += count_items(v)
                    elif isinstance(d, list):
                        count += len(d)
                        for item in d:
                            count += count_items(item)
                    return count
                item_count = count_items(data)
                return {
                    "dry_run": True,
                    "format": "yaml",
                    "items_found": item_count,
                    "would_create_items": item_count,
                }

        # Actual ingestion
        if format_type == "openapi":
            return self._ingest_openapi_spec(data, file_path, project_id)
        elif format_type == "bmad":
            return self._ingest_bmad_format(data, file_path, project_id)
        else:
            return self._ingest_generic_yaml(data, file_path, project_id, view)

    def _ingest_openapi_spec(
        self, data: dict[str, Any], file_path: str, project_id: str | None
    ) -> dict[str, Any]:
        """Ingest OpenAPI/Swagger specification with enhanced component extraction."""
        # Get or create project
        if not project_id:
            project_name = data.get("info", {}).get("title", Path(file_path).stem)
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                project = Project(
                    id=str(uuid4()),
                    name=project_name,
                    description=data.get("info", {}).get("description", ""),
                )
                self.session.add(project)
                self.session.flush()
            project_id = project.id

        items_created = []
        links_created = []
        path_item_map: dict[str, dict[str, str]] = {}  # path -> method -> item_id

        # Extract components (schemas, responses, parameters)
        components = data.get("components", {})
        schemas = components.get("schemas", {})
        components.get("responses", {})
        components.get("parameters", {})

        # Create items for schemas
        schema_items: dict[str, str] = {}
        for schema_name, schema_def in schemas.items():
            item = Item(
                id=str(uuid4()),
                project_id=project_id,
                title=f"Schema: {schema_name}",
                view="API",
                item_type="schema",
                status="todo",
                description=schema_def.get("description", ""),
                item_metadata={
                    "source_file": file_path,
                    "schema_name": schema_name,
                    "schema_type": schema_def.get("type", "object"),
                    "format": "openapi",
                    "openapi_schema": schema_def,
                },
                version=1,
            )
            self.session.add(item)
            self.session.flush()
            schema_items[schema_name] = item.id
            items_created.append(item.id)

        # Create API view items for paths
        paths = data.get("paths", {})
        for path, methods in paths.items():
            path_item_map[path] = {}
            for method, operation in methods.items():
                if not isinstance(operation, dict) or method.startswith("x-"):
                    continue

                operation_id = operation.get("operationId", f"{method}_{path}")
                summary = operation.get("summary", operation_id)

                item = Item(
                    id=str(uuid4()),
                    project_id=project_id,
                    title=f"{method.upper()} {path}",
                    view="API",
                    item_type="endpoint",
                    status="todo",
                    description=operation.get("description", summary),
                    item_metadata={
                        "source_file": file_path,
                        "method": method.upper(),
                        "path": path,
                        "operation_id": operation_id,
                        "openapi_spec": operation,
                        "format": "openapi",
                    },
                    version=1,
                )
                self.session.add(item)
                self.session.flush()
                path_item_map[path][method] = item.id
                items_created.append(item.id)

                # Link to request/response schemas
                request_body = operation.get("requestBody", {})
                if request_body:
                    content = request_body.get("content", {})
                    for _content_type, content_schema in content.items():
                        schema_ref = content_schema.get("schema", {}).get("$ref", "")
                        if schema_ref:
                            schema_name = schema_ref.split("/")[-1]
                            if schema_name in schema_items:
                                link = Link(
                                    id=str(uuid4()),
                                    project_id=project_id,
                                    source_item_id=item.id,
                                    target_item_id=schema_items[schema_name],
                                    link_type="uses",
                                )
                                self.session.add(link)
                                links_created.append((item.id, schema_items[schema_name]))

                # Link to response schemas
                responses_op = operation.get("responses", {})
                for _status_code, response_def in responses_op.items():
                    if isinstance(response_def, dict):
                        content = response_def.get("content", {})
                        for _content_type, content_schema in content.items():
                            schema_ref = content_schema.get("schema", {}).get("$ref", "")
                            if schema_ref:
                                schema_name = schema_ref.split("/")[-1]
                                if schema_name in schema_items:
                                    link = Link(
                                        id=str(uuid4()),
                                        project_id=project_id,
                                        source_item_id=item.id,
                                        target_item_id=schema_items[schema_name],
                                        link_type="returns",
                                    )
                                    self.session.add(link)
                                    links_created.append((item.id, schema_items[schema_name]))

        # Create links between related endpoints (same path, different methods)
        for path, methods in path_item_map.items():
            method_items = list(methods.values())
            for i in range(len(method_items)):
                for j in range(i + 1, len(method_items)):
                    link = Link(
                        id=str(uuid4()),
                        project_id=project_id,
                        source_item_id=method_items[i],
                        target_item_id=method_items[j],
                        link_type="related_to",
                    )
                    self.session.add(link)
                    links_created.append((method_items[i], method_items[j]))

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": len(links_created),
            "file_path": file_path,
            "format": "openapi",
            "schemas_created": len(schema_items),
            "endpoints_created": len(items_created) - len(schema_items),
        }

    def _ingest_bmad_format(
        self, data: dict[str, Any], file_path: str, project_id: str | None
    ) -> dict[str, Any]:
        """Ingest BMad format with enhanced requirement linking and traceability."""
        # Get or create project
        if not project_id:
            project_name = data.get("project", {}).get("name", Path(file_path).stem)
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                project = Project(
                    id=str(uuid4()),
                    name=project_name,
                    description=data.get("project", {}).get("description", ""),
                )
                self.session.add(project)
                self.session.flush()
            project_id = project.id

        items_created = []
        links_created = []
        req_id_map: dict[str, str] = {}  # requirement_id -> item_id

        # BMad format structure - support multiple requirement types
        requirements = data.get("requirements", [])
        if not requirements:
            # Try alternative structure
            requirements = data.get("spec", {}).get("requirements", [])

        # Create items for requirements
        for req in requirements:
            req_id = req.get("id", req.get("requirement_id", str(uuid4())))
            title = req.get("title", req.get("name", req_id))

            # Determine view based on requirement type
            req_type = req.get("type", "requirement")
            view = "FEATURE"
            if req_type in ["test", "test_case", "test_spec"]:
                view = "TEST"
            elif req_type in ["code", "implementation", "component"]:
                view = "CODE"
            elif req_type in ["api", "endpoint", "service"]:
                view = "API"

            item = Item(
                id=str(uuid4()),
                project_id=project_id,
                title=title,
                view=view,
                item_type=req_type,
                status=req.get("status", "todo"),
                description=req.get("description", req.get("text", "")),
                parent_id=req_id_map.get(req.get("parent_id")) if req.get("parent_id") else None,
                item_metadata={
                    "source_file": file_path,
                    "format": "bmad",
                    "requirement_id": req_id,
                    "priority": req.get("priority", "medium"),
                    "owner": req.get("owner"),
                    "tags": req.get("tags", []),
                    **{k: v for k, v in req.items() if k not in ["id", "title", "description", "text", "type", "status", "parent_id"]},
                },
                version=1,
            )
            self.session.add(item)
            self.session.flush()
            req_id_map[req_id] = item.id
            items_created.append(item.id)

        # Create traceability links
        traceability = data.get("traceability", [])
        if not traceability:
            traceability = data.get("spec", {}).get("traceability", [])

        for trace in traceability:
            source_id = trace.get("source")
            target_id = trace.get("target")
            link_type = trace.get("type", "traces_to")

            if source_id in req_id_map and target_id in req_id_map:
                link = Link(
                    id=str(uuid4()),
                    project_id=project_id,
                    source_item_id=req_id_map[source_id],
                    target_item_id=req_id_map[target_id],
                    link_type=link_type,
                    metadata={
                        "format": "bmad",
                        "traceability_rule": trace.get("rule"),
                    },
                )
                self.session.add(link)
                links_created.append((req_id_map[source_id], req_id_map[target_id]))

        # Also create links from requirement dependencies
        for req in requirements:
            req_id = req.get("id", req.get("requirement_id"))
            if req_id not in req_id_map:
                continue

            # Link to parent
            parent_id = req.get("parent_id")
            if parent_id and parent_id in req_id_map:
                link = Link(
                    id=str(uuid4()),
                    project_id=project_id,
                    source_item_id=req_id_map[req_id],
                    target_item_id=req_id_map[parent_id],
                    link_type="child_of",
                )
                self.session.add(link)
                links_created.append((req_id_map[req_id], req_id_map[parent_id]))

            # Link to dependencies
            depends_on = req.get("depends_on", [])
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            for dep_id in depends_on:
                if dep_id in req_id_map:
                    link = Link(
                        id=str(uuid4()),
                        project_id=project_id,
                        source_item_id=req_id_map[req_id],
                        target_item_id=req_id_map[dep_id],
                        link_type="depends_on",
                    )
                    self.session.add(link)
                    links_created.append((req_id_map[req_id], req_id_map[dep_id]))

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": len(links_created),
            "file_path": file_path,
            "format": "bmad",
            "requirements_created": len(items_created),
            "traceability_links": len([link for link in links_created if link]),
        }

    def _ingest_generic_yaml(
        self,
        data: dict[str, Any],
        file_path: str,
        project_id: str | None,
        view: str,
    ) -> dict[str, Any]:
        """Ingest generic YAML structure."""
        # Get or create project
        if not project_id:
            project_name = data.get("name", Path(file_path).stem)
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                project = Project(
                    id=str(uuid4()),
                    name=project_name,
                    description=data.get("description", ""),
                )
                self.session.add(project)
                self.session.flush()
            project_id = project.id

        items_created = []

        # Recursively process YAML structure
        def process_dict(d: dict[str, Any], parent_id: str | None = None):
            for key, value in d.items():
                if isinstance(value, dict):
                    # Create item for this key
                    item = Item(
                        id=str(uuid4()),
                        project_id=project_id,
                        title=str(key),
                        view=view,
                        item_type="section",
                        status="todo",
                        description=str(value.get("description", "")),
                        item_metadata={
                            "source_file": file_path,
                            "format": "yaml",
                            "yaml_data": value,
                        },
                        parent_id=parent_id,
                        version=1,
                    )
                    self.session.add(item)
                    self.session.flush()
                    items_created.append(item.id)
                    # Recursively process nested dict
                    process_dict(value, item.id)
                elif isinstance(value, list):
                    for i, item_data in enumerate(value):
                        if isinstance(item_data, dict):
                            item = Item(
                                id=str(uuid4()),
                                project_id=project_id,
                                title=item_data.get("title", item_data.get("name", f"{key}_{i}")),
                                view=view,
                                item_type="item",
                                status="todo",
                                description=str(item_data.get("description", "")),
                                item_metadata={
                                    "source_file": file_path,
                                    "format": "yaml",
                                    "yaml_data": item_data,
                                },
                                parent_id=parent_id,
                                version=1,
                            )
                            self.session.add(item)
                            self.session.flush()
                            items_created.append(item.id)

        process_dict(data)

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": 0,
            "file_path": file_path,
            "format": "yaml",
        }

    def _determine_item_type(self, level: int, metadata: dict[str, Any]) -> str:
        """Determine item type based on header level."""
        type_mapping = metadata.get("type_mapping", {})
        if str(level) in type_mapping:
            return type_mapping[str(level)]

        # Default mapping
        if level == 1:
            return "epic"
        elif level == 2:
            return "feature"
        elif level == 3:
            return "story"
        else:
            return "task"

    def _extract_section_content(self, body: str, header_line: str) -> str:
        """Extract content between current header and next header."""
        lines = body.split("\n")
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip() == header_line.strip():
                start_idx = i + 1
                break

        if start_idx is None:
            return ""

        # Find next header
        end_idx = len(lines)
        header_pattern = r"^#{1,6}\s+"
        for i in range(start_idx, len(lines)):
            if re.match(header_pattern, lines[i]):
                end_idx = i
                break

        content = "\n".join(lines[start_idx:end_idx]).strip()
        return content
