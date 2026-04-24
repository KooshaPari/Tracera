"""Stateless ingestion service for MD/MDX/YAML/OpenSpec/BMad formats."""

import re
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import yaml
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

# Lazy imports for optional dependencies
try:
    import frontmatter
except ImportError:
    frontmatter = cast("Any", None)

try:
    from markdown import Markdown
    from markdown_it import MarkdownIt
except ImportError:
    Markdown = cast("Any", None)  # type: ignore[misc]
    MarkdownIt = cast("Any", None)

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class StatelessIngestionService:
    """Service for stateless ingestion of MD/MDX/YAML/OpenSpec/BMad files."""

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session
        if MarkdownIt is not None:
            self.md_parser: object = MarkdownIt()
        else:
            self.md_parser = None
        if Markdown is not None:
            self.markdown: object = Markdown()
        else:
            self.markdown = None

    def _validate_file_extension(self, path: Path, allowed: tuple[str, ...], label: str) -> None:
        if path.suffix.lower() not in allowed:
            msg = f"Invalid file extension: {path.suffix}. Expected {label}"
            raise ValueError(msg)

    def _ensure_file_exists(self, path: Path, file_path: str) -> None:
        if not path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def _markdown_dry_run(self, content: str) -> dict[str, Any]:
        header_count = len(re.findall(r"^(#{1,6})\s+", content, re.MULTILINE))
        link_count = len(re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content))
        return {
            "dry_run": True,
            "headers_found": header_count,
            "links_found": link_count,
            "would_create_items": header_count,
            "would_create_links": link_count,
        }

    def _ingest_markdown_content(
        self,
        *,
        body: str,
        metadata: dict[str, Any],
        path: Path,
        project_id: str,
        view: str,
    ) -> tuple[list[str], list[tuple[str, str]]]:
        items_created, headers = self._collect_markdown_headers(
            body=body,
            project_id=project_id,
            view=view,
            metadata=metadata,
            path=path,
        )
        links_created = self._create_markdown_links(
            body=body,
            project_id=project_id,
            headers=headers,
            items_created=items_created,
        )
        return items_created, links_created

    def _parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        if frontmatter:
            try:
                post = frontmatter.loads(content)
            except (ValueError, KeyError, OperationalError):
                return {}, content
            else:
                return post.metadata, post.content
        return {}, content

    def _get_or_create_project(
        self,
        *,
        project_id: str | None,
        name: str,
        description: str,
        validate_existing: bool,
    ) -> str:
        if project_id:
            if validate_existing:
                project = self.session.query(Project).filter(Project.id == project_id).first()
                if not project:
                    msg = f"Project not found: {project_id}"
                    raise ValueError(msg)
            return project_id

        project = self.session.query(Project).filter(Project.name == name).first()
        if not project:
            project = Project(
                id=str(uuid4()),
                name=name,
                description=description,
            )
            self.session.add(project)
            self.session.flush()
        return str(project.id)

    def _create_item(self, item: Item) -> str:
        self.session.add(item)
        self.session.flush()
        return str(item.id)

    def _collect_markdown_headers(
        self,
        body: str,
        project_id: str,
        view: str,
        metadata: dict[str, Any],
        path: Path,
    ) -> tuple[list[str], list[tuple[int, str, str]]]:
        items_created: list[str] = []
        headers: list[tuple[int, str, str]] = []
        header_pattern = r"^(#{1,6})\s+(.+)$"
        parent_stack: list[str | None] = [None]

        for line in body.split("\n"):
            match = re.match(header_pattern, line)
            if not match:
                continue
            level = len(match.group(1))
            title = match.group(2).strip()
            parent_stack = self._adjust_parent_stack(parent_stack, level)
            parent_id = parent_stack[-1] if parent_stack else None
            item_type = self._determine_item_type(level, metadata)
            item = Item(
                id=str(uuid4()),
                project_id=project_id,
                title=title,
                view=view,
                item_type=item_type,
                status=metadata.get("status", "todo"),
                description=self._extract_section_content(body, line),
                item_metadata={
                    "header_level": level,
                    "source_file": str(path),
                    **metadata,
                },
                parent_id=parent_id,
                version=1,
            )
            item_id = self._create_item(item)
            items_created.append(item_id)
            headers.append((level, item_id, title))
            parent_stack = self._update_parent_stack(parent_stack, level, item_id)

        return items_created, headers

    def _adjust_parent_stack(self, parent_stack: list[str | None], level: int) -> list[str | None]:
        while len(parent_stack) > level:
            parent_stack.pop()
        while len(parent_stack) < level:
            parent_stack.append(None)
        return parent_stack

    def _update_parent_stack(
        self,
        parent_stack: list[str | None],
        level: int,
        item_id: str,
    ) -> list[str | None]:
        if len(parent_stack) <= level:
            parent_stack.append(item_id)
        else:
            parent_stack[level - 1] = item_id
        return parent_stack

    def _create_markdown_links(
        self,
        body: str,
        project_id: str,
        headers: list[tuple[int, str, str]],
        items_created: list[str],
    ) -> list[tuple[str, str]]:
        links_created: list[tuple[str, str]] = []
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        for match in re.finditer(link_pattern, body):
            link_url = match.group(2)
            if not items_created:
                continue
            source_id = items_created[-1]
            if not link_url.startswith("#"):
                continue
            target_title = link_url[1:].replace("-", " ").title()
            target_id = self._find_header_target(headers, target_title)
            if not target_id:
                continue
            link = Link(
                id=str(uuid4()),
                project_id=project_id,
                source_item_id=source_id,
                target_item_id=target_id,
                link_type="relates_to",
            )
            self.session.add(link)
            links_created.append((source_id, target_id))
        return links_created

    def _find_header_target(
        self,
        headers: list[tuple[int, str, str]],
        target_title: str,
    ) -> str | None:
        for _level, item_id, title in headers:
            if title.lower() == target_title.lower():
                return item_id
        return None

    def _count_yaml_items(self, data: object) -> int:
        if isinstance(data, dict):
            return sum(self._count_yaml_items(value) for value in data.values()) + len(data)
        if isinstance(data, list):
            return sum(self._count_yaml_items(value) for value in data) + len(data)
        return 0

    def _detect_yaml_format(self, data: dict[str, Any], path: Path) -> str:
        if "openapi" in data or "swagger" in data:
            return "openapi"
        if (
            "bmad" in str(path).lower()
            or "bmad" in data
            or "requirements" in data
            or ("spec" in data and "requirements" in data.get("spec", {}))
        ):
            return "bmad"
        return "yaml"

    def _schema_name_from_ref(self, schema_ref: str) -> str | None:
        return schema_ref.rsplit("/", maxsplit=1)[-1] if schema_ref else None

    def _iter_schema_names_from_content(
        self,
        content: dict[str, Any],
    ) -> Iterable[str]:
        for content_schema in content.values():
            schema_ref = content_schema.get("schema", {}).get("$ref", "")
            schema_name = self._schema_name_from_ref(schema_ref)
            if schema_name:
                yield schema_name

    def _link_schema_names(
        self,
        *,
        project_id: str,
        source_item_id: str,
        schema_items: dict[str, str],
        schema_names: Iterable[str],
        link_type: str,
        links_created: list[tuple[str, str]],
    ) -> None:
        for schema_name in schema_names:
            target_item_id = schema_items.get(schema_name)
            if not target_item_id:
                continue
            link = Link(
                id=str(uuid4()),
                project_id=project_id,
                source_item_id=source_item_id,
                target_item_id=target_item_id,
                link_type=link_type,
            )
            self.session.add(link)
            links_created.append((source_item_id, target_item_id))

    def _ensure_openapi_project_id(
        self,
        data: dict[str, Any],
        file_path: str,
        project_id: str | None,
    ) -> str:
        if project_id:
            return project_id
        project_name = data.get("info", {}).get("title", Path(file_path).stem)
        description = data.get("info", {}).get("description", "")
        return self._get_or_create_project(
            project_id=None,
            name=project_name,
            description=description,
            validate_existing=False,
        )

    def _create_openapi_schema_items(
        self,
        schemas: dict[str, Any],
        *,
        project_id: str,
        file_path: str,
        items_created: list[str],
    ) -> dict[str, str]:
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
                    "format": "openapi",
                    "openapi_schema": schema_def,
                    "schema_name": schema_name,
                    "schema_type": schema_def.get("type", "object"),
                    "source_file": file_path,
                },
                version=1,
            )
            item_id = self._create_item(item)
            schema_items[schema_name] = item_id
            items_created.append(item_id)
        return schema_items

    def _iter_openapi_operations(
        self,
        paths: dict[str, Any],
    ) -> Iterable[tuple[str, str, dict[str, Any]]]:
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.startswith("x-"):
                    continue
                if isinstance(operation, dict):
                    yield path, method, operation

    def _create_openapi_endpoint_item(
        self,
        *,
        project_id: str,
        file_path: str,
        method: str,
        path: str,
        operation: dict[str, Any],
    ) -> str:
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
                "format": "openapi",
                "method": method.upper(),
                "openapi_spec": operation,
                "operation_id": operation_id,
                "path": path,
                "source_file": file_path,
            },
            version=1,
        )
        return self._create_item(item)

    def _link_openapi_operation_schemas(
        self,
        *,
        project_id: str,
        operation: dict[str, Any],
        source_item_id: str,
        schema_items: dict[str, str],
        links_created: list[tuple[str, str]],
    ) -> None:
        request_body = operation.get("requestBody", {})
        if request_body:
            content = request_body.get("content", {})
            schema_names = self._iter_schema_names_from_content(content)
            self._link_schema_names(
                project_id=project_id,
                source_item_id=source_item_id,
                schema_items=schema_items,
                schema_names=schema_names,
                link_type="uses",
                links_created=links_created,
            )

        responses_op = operation.get("responses", {})
        for response_def in responses_op.values():
            if not isinstance(response_def, dict):
                continue
            content = response_def.get("content", {})
            schema_names = self._iter_schema_names_from_content(content)
            self._link_schema_names(
                project_id=project_id,
                source_item_id=source_item_id,
                schema_items=schema_items,
                schema_names=schema_names,
                link_type="returns",
                links_created=links_created,
            )

    def _link_related_endpoints(
        self,
        *,
        project_id: str,
        path_item_map: dict[str, dict[str, str]],
        links_created: list[tuple[str, str]],
    ) -> None:
        for methods in path_item_map.values():
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

    def _ensure_bmad_project_id(
        self,
        data: dict[str, Any],
        file_path: str,
        project_id: str | None,
    ) -> str:
        if project_id:
            return project_id
        project_name = data.get("project", {}).get("name", Path(file_path).stem)
        description = data.get("project", {}).get("description", "")
        return self._get_or_create_project(
            project_id=None,
            name=project_name,
            description=description,
            validate_existing=False,
        )

    def _extract_bmad_requirements(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        requirements = data.get("requirements", [])
        if requirements:
            return requirements
        return data.get("spec", {}).get("requirements", [])

    def _resolve_bmad_view(self, req_type: str) -> str:
        if req_type in {"test", "test_case", "test_spec"}:
            return "TEST"
        if req_type in {"code", "implementation", "component"}:
            return "CODE"
        if req_type in {"api", "endpoint", "service"}:
            return "API"
        return "FEATURE"

    def _build_bmad_metadata(self, req: dict[str, Any], file_path: str, req_id: str) -> dict[str, Any]:
        base_fields = {"id", "title", "description", "text", "type", "status", "parent_id"}
        extra_fields = {key: value for key, value in req.items() if key not in base_fields}
        return {
            "format": "bmad",
            "owner": req.get("owner"),
            "priority": req.get("priority", "medium"),
            "requirement_id": req_id,
            "source_file": file_path,
            "tags": req.get("tags", []),
            **extra_fields,
        }

    def _create_bmad_requirement_items(
        self,
        requirements: list[dict[str, Any]],
        *,
        project_id: str,
        file_path: str,
    ) -> tuple[list[str], dict[str, str]]:
        items_created: list[str] = []
        req_id_map: dict[str, str] = {}
        for req in requirements:
            req_id = req.get("id", req.get("requirement_id", str(uuid4())))
            title = req.get("title", req.get("name", req_id))
            req_type = req.get("type", "requirement")
            view = self._resolve_bmad_view(req_type)
            parent_key = req.get("parent_id")
            parent_id = req_id_map.get(parent_key) if parent_key else None
            item = Item(
                id=str(uuid4()),
                project_id=project_id,
                title=title,
                view=view,
                item_type=req_type,
                status=req.get("status", "todo"),
                description=req.get("description", req.get("text", "")),
                parent_id=parent_id,
                item_metadata=self._build_bmad_metadata(req, file_path, req_id),
                version=1,
            )
            item_id = self._create_item(item)
            req_id_map[req_id] = item_id
            items_created.append(item_id)
        return items_created, req_id_map

    def _create_bmad_traceability_links(
        self,
        traceability: list[dict[str, Any]],
        *,
        project_id: str,
        req_id_map: dict[str, str],
        links_created: list[tuple[str, str]],
    ) -> None:
        for trace in traceability:
            source_id = trace.get("source")
            target_id = trace.get("target")
            link_type = trace.get("type", "traces_to")
            source_item = req_id_map.get(str(source_id) if source_id else "")
            target_item = req_id_map.get(str(target_id) if target_id else "")
            if not source_item or not target_item:
                continue
            link = Link(
                id=str(uuid4()),
                project_id=project_id,
                source_item_id=source_item,
                target_item_id=target_item,
                link_type=link_type,
                metadata={
                    "format": "bmad",
                    "traceability_rule": trace.get("rule"),
                },
            )
            self.session.add(link)
            links_created.append((source_item, target_item))

    def _create_bmad_dependency_links(
        self,
        requirements: list[dict[str, Any]],
        *,
        project_id: str,
        req_id_map: dict[str, str],
        links_created: list[tuple[str, str]],
    ) -> None:
        for req in requirements:
            req_id = req.get("id", req.get("requirement_id"))
            if req_id not in req_id_map:
                continue
            source_item = req_id_map[req_id]

            parent_id = req.get("parent_id")
            if parent_id and parent_id in req_id_map:
                link = Link(
                    id=str(uuid4()),
                    project_id=project_id,
                    source_item_id=source_item,
                    target_item_id=req_id_map[parent_id],
                    link_type="child_of",
                )
                self.session.add(link)
                links_created.append((source_item, req_id_map[parent_id]))

            depends_on = req.get("depends_on", [])
            depends_list = [depends_on] if isinstance(depends_on, str) else depends_on
            for dep_id in depends_list:
                if dep_id not in req_id_map:
                    continue
                link = Link(
                    id=str(uuid4()),
                    project_id=project_id,
                    source_item_id=source_item,
                    target_item_id=req_id_map[dep_id],
                    link_type="depends_on",
                )
                self.session.add(link)
                links_created.append((source_item, req_id_map[dep_id]))

    def _create_yaml_item(
        self,
        *,
        project_id: str,
        file_path: str,
        title: str,
        view: str,
        item_type: str,
        description: str,
        item_metadata: dict[str, Any],
        parent_id: str | None,
    ) -> str:
        item = Item(
            id=str(uuid4()),
            project_id=project_id,
            title=title,
            view=view,
            item_type=item_type,
            status="todo",
            description=description,
            item_metadata={
                "format": "yaml",
                "source_file": file_path,
                **item_metadata,
            },
            parent_id=parent_id,
            version=1,
        )
        return self._create_item(item)

    def _ingest_yaml_dict(
        self,
        data: dict[str, Any],
        *,
        project_id: str,
        file_path: str,
        view: str,
        items_created: list[str],
        parent_id: str | None,
    ) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                item_id = self._create_yaml_item(
                    project_id=project_id,
                    file_path=file_path,
                    title=str(key),
                    view=view,
                    item_type="section",
                    description=str(value.get("description", "")),
                    item_metadata={"yaml_data": value},
                    parent_id=parent_id,
                )
                items_created.append(item_id)
                self._ingest_yaml_dict(
                    value,
                    project_id=project_id,
                    file_path=file_path,
                    view=view,
                    items_created=items_created,
                    parent_id=item_id,
                )
            elif isinstance(value, list):
                self._ingest_yaml_list(
                    value,
                    key=key,
                    project_id=project_id,
                    file_path=file_path,
                    view=view,
                    items_created=items_created,
                    parent_id=parent_id,
                )

    def _ingest_yaml_list(
        self,
        items: list[object],
        *,
        key: str,
        project_id: str,
        file_path: str,
        view: str,
        items_created: list[str],
        parent_id: str | None,
    ) -> None:
        for index, item_data in enumerate(items):
            if not isinstance(item_data, dict):
                continue
            title = item_data.get("title", item_data.get("name", f"{key}_{index}"))
            item_id = self._create_yaml_item(
                project_id=project_id,
                file_path=file_path,
                title=str(title),
                view=view,
                item_type="item",
                description=str(item_data.get("description", "")),
                item_metadata={"yaml_data": item_data},
                parent_id=parent_id,
            )
            items_created.append(item_id)

    def ingest_markdown(
        self,
        file_path: str,
        project_id: str | uuid.UUID | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Ingest a Markdown file (with optional frontmatter).

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
        pid = str(project_id) if project_id is not None else None
        path = Path(file_path)
        self._ensure_file_exists(path, file_path)

        if validate:
            self._validate_file_extension(
                path,
                (".md", ".markdown", ".mdx"),
                ".md, .markdown, or .mdx",
            )

        content = self._read_text(path)
        if dry_run:
            return self._markdown_dry_run(content)

        metadata, body = self._parse_frontmatter(content)
        project_id = self._get_or_create_project(
            project_id=pid,
            name=metadata.get("project", path.stem),
            description=metadata.get("description", ""),
            validate_existing=True,
        )
        items_created, links_created = self._ingest_markdown_content(
            body=body,
            metadata=metadata,
            path=path,
            project_id=project_id,
            view=view,
        )

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": len(links_created),
            "file_path": str(path),
        }

    def ingest_mdx(
        self,
        file_path: str,
        project_id: str | uuid.UUID | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Ingest an MDX file (Markdown with JSX components).

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
        path = Path(file_path)
        if not path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        if validate:
            self._validate_file_extension(path, (".mdx",), ".mdx")

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

        metadata, body = self._parse_frontmatter(content)
        jsx_pattern = r"<(\w+)([^>]*)>([^<]*)</\1>"
        jsx_components = re.findall(jsx_pattern, body)

        pid: str | None = str(project_id) if project_id is not None else None
        pid = self._get_or_create_project(
            project_id=pid,
            name=metadata.get("project", path.stem),
            description=metadata.get("description", ""),
            validate_existing=False,
        )

        result = self.ingest_markdown(file_path, pid, view)

        # Add JSX components as CODE view items
        items_created = []
        for component_name, attrs, content in jsx_components:
            item = Item(
                id=str(uuid4()),
                project_id=pid,
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
            items_created.append(str(item.id))

        result["jsx_components_created"] = len(items_created)
        return result

    def ingest_yaml(
        self,
        file_path: str,
        project_id: str | uuid.UUID | None = None,
        view: str = "FEATURE",
        dry_run: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Ingest a YAML file.

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
        pid: str | None = str(project_id) if project_id is not None else None
        path = Path(file_path)
        if not path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        if validate:
            self._validate_file_extension(path, (".yaml", ".yml"), ".yaml or .yml")

        content = path.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML: {e}"
            raise ValueError(msg) from e

        if not isinstance(data, dict):
            msg = "YAML root must be a dictionary"
            raise ValueError(msg)

        format_type = self._detect_yaml_format(data, path)

        if dry_run:
            if format_type == "openapi":
                paths = data.get("paths", {})
                schemas = data.get("components", {}).get("schemas", {})
                endpoint_count = sum(len([m for m in methods if not m.startswith("x-")]) for methods in paths.values())
                return {
                    "dry_run": True,
                    "format": "openapi",
                    "endpoints_found": endpoint_count,
                    "schemas_found": len(schemas),
                    "would_create_items": endpoint_count + len(schemas),
                }
            if format_type == "bmad":
                requirements = data.get("requirements", []) or data.get("spec", {}).get("requirements", [])
                return {
                    "dry_run": True,
                    "format": "bmad",
                    "requirements_found": len(requirements),
                    "would_create_items": len(requirements),
                }

            item_count = self._count_yaml_items(data)
            return {
                "dry_run": True,
                "format": "yaml",
                "items_found": item_count,
                "would_create_items": item_count,
            }

        if format_type == "openapi":
            return self._ingest_openapi_spec(data, file_path, pid)
        if format_type == "bmad":
            return self._ingest_bmad_format(data, file_path, pid)
        return self._ingest_generic_yaml(data, file_path, pid, view)

    def _ingest_openapi_spec(self, data: dict[str, Any], file_path: str, project_id: str | None) -> dict[str, Any]:
        """Ingest OpenAPI/Swagger specification with enhanced component extraction."""
        project_id = self._ensure_openapi_project_id(data, file_path, project_id)
        items_created: list[str] = []
        links_created: list[tuple[str, str]] = []
        path_item_map: dict[str, dict[str, str]] = {}  # path -> method -> item_id

        # Extract components (schemas, responses, parameters)
        components = data.get("components", {})
        schemas = components.get("schemas", {})
        schema_items = self._create_openapi_schema_items(
            schemas,
            project_id=project_id,
            file_path=file_path,
            items_created=items_created,
        )

        paths = data.get("paths", {})
        for path, method, operation in self._iter_openapi_operations(paths):
            path_item_map.setdefault(path, {})
            item_id = self._create_openapi_endpoint_item(
                project_id=project_id,
                file_path=file_path,
                method=method,
                path=path,
                operation=operation,
            )
            path_item_map[path][method] = item_id
            items_created.append(item_id)
            self._link_openapi_operation_schemas(
                project_id=project_id,
                operation=operation,
                source_item_id=item_id,
                schema_items=schema_items,
                links_created=links_created,
            )

        self._link_related_endpoints(
            project_id=project_id,
            path_item_map=path_item_map,
            links_created=links_created,
        )

        return {
            "project_id": project_id,
            "items_created": len(items_created),
            "links_created": len(links_created),
            "file_path": file_path,
            "format": "openapi",
            "schemas_created": len(schema_items),
            "endpoints_created": len(items_created) - len(schema_items),
        }

    def _ingest_bmad_format(self, data: dict[str, Any], file_path: str, project_id: str | None) -> dict[str, Any]:
        """Ingest BMad format with enhanced requirement linking and traceability."""
        project_id = self._ensure_bmad_project_id(data, file_path, project_id)
        links_created: list[tuple[str, str]] = []

        requirements = self._extract_bmad_requirements(data)
        items_created, req_id_map = self._create_bmad_requirement_items(
            requirements,
            project_id=project_id,
            file_path=file_path,
        )

        traceability = data.get("traceability", []) or data.get("spec", {}).get("traceability", [])
        self._create_bmad_traceability_links(
            traceability,
            project_id=project_id,
            req_id_map=req_id_map,
            links_created=links_created,
        )
        self._create_bmad_dependency_links(
            requirements,
            project_id=project_id,
            req_id_map=req_id_map,
            links_created=links_created,
        )

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
        project_id = self._get_or_create_project(
            project_id=project_id,
            name=data.get("name", Path(file_path).stem),
            description=data.get("description", ""),
            validate_existing=False,
        )
        items_created: list[str] = []
        self._ingest_yaml_dict(
            data,
            project_id=project_id,
            file_path=file_path,
            view=view,
            items_created=items_created,
            parent_id=None,
        )

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
            return str(type_mapping[str(level)])

        # Default mapping
        default_mapping = {1: "epic", 2: "feature", 3: "story"}
        return default_mapping.get(level, "task")

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

        return "\n".join(lines[start_idx:end_idx]).strip()
