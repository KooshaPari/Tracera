#!/usr/bin/env python3
"""
Generate comprehensive API reference documentation for PhenoSDK.

This script extracts docstrings from Python modules and generates Fumadocs-compatible
MDX files for the API reference section.
"""

import ast
import inspect
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class APIEntity:
    """Represents a documentable API entity (class or function)."""

    name: str
    type: str  # 'class' or 'function'
    module_path: str
    docstring: str | None
    signature: str | None
    examples: list[str]
    see_also: list[str]
    source_file: str


class APIDocGenerator:
    """Generate API reference documentation from Python source files."""

    def __init__(self, src_path: Path, docs_path: Path):
        self.src_path = src_path
        self.docs_path = docs_path
        self.entities: list[APIEntity] = []

    def extract_docstring_sections(self, docstring: str | None) -> dict[str, Any]:
        """Extract structured sections from a docstring."""
        if not docstring:
            return {}

        sections = {
            "description": "",
            "attributes": [],
            "parameters": [],
            "returns": "",
            "raises": [],
            "examples": [],
            "see_also": [],
            "notes": [],
        }

        # Extract description (everything before first section)
        lines = docstring.strip().split("\n")
        description_lines = []
        current_section = None
        current_content = []

        for line in lines:
            stripped = line.strip()

            # Detect section headers
            if stripped.endswith(":") and stripped[:-1] in [
                "Args",
                "Arguments",
                "Parameters",
                "Attributes",
                "Returns",
                "Yields",
                "Raises",
                "Example",
                "Examples",
                "See Also",
                "Notes",
                "Note",
            ]:
                if current_section and current_content:
                    content_str = "\n".join(current_content)
                    if current_section in sections:
                        if isinstance(sections[current_section], list):
                            sections[current_section].append(content_str)
                        else:
                            sections[current_section] = content_str
                current_section = stripped[:-1].lower().replace(" ", "_")
                if current_section == "args" or current_section == "arguments":
                    current_section = "parameters"
                if current_section == "note":
                    current_section = "notes"
                if current_section == "example":
                    current_section = "examples"
                if current_section == "yields":
                    current_section = "returns"
                # Initialize section if not exists
                if current_section not in sections:
                    sections[current_section] = []
                current_content = []
            elif current_section:
                current_content.append(line)
            else:
                description_lines.append(line)

        if current_section and current_content:
            content_str = "\n".join(current_content)
            if current_section not in sections:
                sections[current_section] = []
            # Handle both list and string types
            if isinstance(sections[current_section], list):
                sections[current_section].append(content_str)
            else:
                sections[current_section] = content_str

        sections["description"] = "\n".join(description_lines).strip()
        return sections

    def generate_mdx_content(self, entity: APIEntity) -> str:
        """Generate MDX content for an API entity."""
        sections = self.extract_docstring_sections(entity.docstring)

        # Build MDX content
        mdx = f"""---
title: "{entity.name}"
description: "{sections.get('description', '').split('.')[0] if sections.get('description') else f'{entity.type.title()} {entity.name}'}"
---

# {entity.name}

"""

        # Add import statement
        import_path = entity.module_path.replace("/", ".").replace(".py", "")
        mdx += f"""## Import

```python
from {import_path} import {entity.name}
```

"""

        # Add description
        if sections.get("description"):
            mdx += f"""{sections['description']}

"""

        # Add signature for functions
        if entity.type == "function" and entity.signature:
            mdx += f"""## Signature

```python
{entity.signature}
```

"""

        # Add attributes for classes
        if entity.type == "class" and sections.get("attributes"):
            mdx += """## Attributes

"""
            for attr in sections["attributes"]:
                if attr.strip():
                    mdx += f"{attr.strip()}\n\n"

        # Add parameters
        if sections.get("parameters"):
            mdx += """## Parameters

"""
            for param in sections["parameters"]:
                if param.strip():
                    mdx += f"{param.strip()}\n\n"

        # Add returns
        if sections.get("returns"):
            mdx += f"""## Returns

{sections['returns']}

"""

        # Add raises
        if sections.get("raises"):
            mdx += """## Raises

"""
            for raises in sections["raises"]:
                if raises.strip():
                    mdx += f"{raises.strip()}\n\n"

        # Add examples
        if sections.get("examples") or entity.examples:
            mdx += """## Examples

"""
            for example in sections.get("examples", []) or entity.examples:
                if example.strip():
                    # Check if example has code blocks
                    if ">>>" in example or "..." in example:
                        mdx += f"```python\n{example.strip()}\n```\n\n"
                    else:
                        mdx += f"{example.strip()}\n\n"

        # Add notes
        if sections.get("notes"):
            mdx += """## Notes

"""
            for note in sections["notes"]:
                if note.strip():
                    mdx += f"{note.strip()}\n\n"

        # Add see also
        if sections.get("see_also") or entity.see_also:
            mdx += """## See Also

"""
            for see in sections.get("see_also", []) or entity.see_also:
                if see.strip():
                    mdx += f"- {see.strip()}\n"
            mdx += "\n"

        # Add source link
        mdx += f"""## Source

[View source code]({entity.source_file})
"""

        return mdx

    def extract_entities_from_file(self, py_file: Path) -> None:
        """Extract API entities from a Python file."""
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(py_file))

            rel_path = str(py_file.relative_to(self.src_path))
            module_path = rel_path.replace("/", ".").replace(".py", "")

            # Only extract top-level classes and functions
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    if docstring and len(docstring) > 50:  # Only well-documented classes
                        entity = APIEntity(
                            name=node.name,
                            type="class",
                            module_path=module_path,
                            docstring=docstring,
                            signature=None,
                            examples=[],
                            see_also=[],
                            source_file=rel_path,
                        )
                        self.entities.append(entity)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions
                    if node.name.startswith("_"):
                        continue
                    docstring = ast.get_docstring(node)
                    if docstring and len(docstring) > 50:  # Only well-documented functions
                        entity = APIEntity(
                            name=node.name,
                            type="function",
                            module_path=module_path,
                            docstring=docstring,
                            signature=f"def {node.name}(...)",
                            examples=[],
                            see_also=[],
                            source_file=rel_path,
                        )
                        self.entities.append(entity)

        except Exception as e:
            pass  # Silently skip files with syntax errors

    def scan_source_files(self) -> None:
        """Scan all Python source files."""
        for py_file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
                continue
            self.extract_entities_from_file(py_file)

    def categorize_entities(self) -> dict[str, list[APIEntity]]:
        """Categorize entities by module type."""
        categories = {
            "domain/entities": [],
            "domain/events": [],
            "domain/value-objects": [],
            "domain/exceptions": [],
            "application/use-cases": [],
            "application/services": [],
            "application/dtos": [],
            "application/ports": [],
            "adapters/database": [],
            "adapters/sst": [],
            "adapters/auth": [],
            "adapters/api": [],
            "adapters/cli": [],
            "infrastructure/observability": [],
            "infrastructure/deployment": [],
            "infrastructure/workflow": [],
            "sdk/core": [],
            "sdk/cli": [],
            "sdk/config": [],
        }

        for entity in self.entities:
            # Determine category based on module path
            if "domain/entities" in entity.module_path:
                categories["domain/entities"].append(entity)
            elif "domain/events" in entity.module_path:
                categories["domain/events"].append(entity)
            elif "domain/value_objects" in entity.module_path:
                categories["domain/value-objects"].append(entity)
            elif "domain/exceptions" in entity.module_path:
                categories["domain/exceptions"].append(entity)
            elif "application/use_cases" in entity.module_path:
                categories["application/use-cases"].append(entity)
            elif "application/services" in entity.module_path:
                categories["application/services"].append(entity)
            elif "application/dtos" in entity.module_path:
                categories["application/dtos"].append(entity)
            elif "application/ports" in entity.module_path:
                categories["application/ports"].append(entity)
            elif "adapters/database" in entity.module_path or "database" in entity.module_path:
                categories["adapters/database"].append(entity)
            elif "adapters/sst" in entity.module_path or "/sst/" in entity.module_path:
                categories["adapters/sst"].append(entity)
            elif "adapters/auth" in entity.module_path or "/auth/" in entity.module_path:
                categories["adapters/auth"].append(entity)
            elif "adapters/api" in entity.module_path or "/api/" in entity.module_path:
                categories["adapters/api"].append(entity)
            elif "adapters/cli" in entity.module_path or "/cli/" in entity.module_path:
                categories["adapters/cli"].append(entity)
            elif "observability" in entity.module_path:
                categories["infrastructure/observability"].append(entity)
            elif "deployment" in entity.module_path or "core/commands" in entity.module_path:
                categories["infrastructure/deployment"].append(entity)
            elif "workflow" in entity.module_path:
                categories["infrastructure/workflow"].append(entity)
            elif "pheno_sdk" in entity.module_path:
                if "cli" in entity.module_path:
                    categories["sdk/cli"].append(entity)
                elif "config" in entity.module_path:
                    categories["sdk/config"].append(entity)
                else:
                    categories["sdk/core"].append(entity)

        return categories

    def generate_docs(self) -> dict[str, int]:
        """Generate all API documentation files."""
        print("Scanning source files...")
        self.scan_source_files()
        print(f"Found {len(self.entities)} documentable entities")

        print("Categorizing entities...")
        categories = self.categorize_entities()

        stats = {}

        for category, entities in categories.items():
            if not entities:
                continue

            category_path = self.docs_path / category
            category_path.mkdir(parents=True, exist_ok=True)

            count = 0
            for entity in entities:
                # Generate filename (convert CamelCase to kebab-case)
                filename = re.sub(r"(?<!^)(?=[A-Z])", "-", entity.name).lower()
                file_path = category_path / f"{filename}.mdx"

                # Generate MDX content
                mdx_content = self.generate_mdx_content(entity)

                # Write file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(mdx_content)

                count += 1

            stats[category] = count
            print(f"Generated {count} pages for {category}")

        return stats

    def generate_meta_json(self, category: str, entities: list[APIEntity]) -> None:
        """Generate meta.json for a category."""
        pages = []
        for entity in sorted(entities, key=lambda x: x.name):
            filename = re.sub(r"(?<!^)(?=[A-Z])", "-", entity.name).lower()
            pages.append(filename)

        meta = {"pages": pages}

        category_path = self.docs_path / category
        meta_path = category_path / "meta.json"

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)


def main():
    """Main entry point."""
    base_path = Path(__file__).parent.parent
    src_path = base_path / "src" / "pheno"
    docs_path = base_path / "apps" / "docs" / "content" / "docs" / "api"

    generator = APIDocGenerator(src_path, docs_path)
    stats = generator.generate_docs()

    print("\n" + "=" * 60)
    print("API Documentation Generation Complete")
    print("=" * 60)

    total = sum(stats.values())
    for category, count in sorted(stats.items()):
        print(f"  {category:40s} {count:4d} pages")

    print("-" * 60)
    print(f"  {'Total':40s} {total:4d} pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
