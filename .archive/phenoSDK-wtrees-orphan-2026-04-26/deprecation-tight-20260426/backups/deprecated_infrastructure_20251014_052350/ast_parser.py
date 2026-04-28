"""AST parsing for code entity extraction."""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, method, etc.).
    
    Attributes:
        type: Entity type ('function', 'class', 'method', 'variable')
        name: Entity name
        file_path: Path to file containing entity
        line_number: Line number where entity is defined
        docstring: Docstring if available
        code: Full code of the entity
        parent: Parent entity name (for methods, the class name)
        signature: Function/method signature
    """
    type: str
    name: str
    file_path: str
    line_number: int
    docstring: str | None
    code: str
    parent: str | None = None
    signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "docstring": self.docstring,
            "code": self.code[:500],  # Limit code length
            "parent": self.parent,
            "signature": self.signature,
        }


class PythonASTParser:
    """Parse Python code using AST to extract entities."""

    def parse_file(self, file_path: str) -> list[CodeEntity]:
        """Extract code entities from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of extracted code entities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)
            entities = []

            # Extract top-level entities
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a top-level function
                    if self._is_top_level(node, tree):
                        entities.append(self._extract_function(node, file_path, source))

                elif isinstance(node, ast.ClassDef):
                    entities.append(self._extract_class(node, file_path, source))

                    # Extract methods from class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            entities.append(
                                self._extract_method(item, node.name, file_path, source),
                            )

            return entities

        except Exception:
            # Return empty list if parsing fails
            return []

    def _is_top_level(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if function is top-level (not a method)."""
        for item in tree.body:
            if item == node:
                return True
        return False

    def _extract_function(
        self,
        node: ast.FunctionDef,
        file_path: str,
        source: str,
    ) -> CodeEntity:
        """Extract function information."""
        signature = self._get_signature(node)

        return CodeEntity(
            type="function",
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            code=self._get_node_source(node, source),
            signature=signature,
        )

    def _extract_class(
        self,
        node: ast.ClassDef,
        file_path: str,
        source: str,
    ) -> CodeEntity:
        """Extract class information."""
        # Get base classes
        bases = [self._get_name(base) for base in node.bases]
        signature = f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"

        return CodeEntity(
            type="class",
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            code=self._get_node_source(node, source),
            signature=signature,
        )

    def _extract_method(
        self,
        node: ast.FunctionDef,
        class_name: str,
        file_path: str,
        source: str,
    ) -> CodeEntity:
        """Extract method information."""
        signature = self._get_signature(node)

        return CodeEntity(
            type="method",
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            code=self._get_node_source(node, source),
            parent=class_name,
            signature=signature,
        )

    def _get_signature(self, node: ast.FunctionDef) -> str:
        """Get function/method signature."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            args.append(arg.arg)

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        return f"{node.name}({', '.join(args)})"

    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _get_node_source(self, node, source: str) -> str:
        """Get source code for a node."""
        try:
            return ast.get_source_segment(source, node) or ""
        except Exception:
            # Fallback: extract by line numbers
            lines = source.split("\n")
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                start = node.lineno - 1
                end = node.end_lineno if node.end_lineno else start + 1
                return "\n".join(lines[start:end])
            return ""


class JavaScriptParser:
    """Parse JavaScript/TypeScript code (simplified regex-based).
    
    Note: This is a simplified parser. For production, consider using
    a proper JS/TS parser like esprima or tree-sitter.
    """

    def parse_file(self, file_path: str) -> list[CodeEntity]:
        """Extract code entities from JS/TS file.
        
        Args:
            file_path: Path to JavaScript/TypeScript file
            
        Returns:
            List of extracted code entities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            entities = []

            # Find functions
            entities.extend(self._extract_functions(source, file_path))

            # Find classes
            entities.extend(self._extract_classes(source, file_path))

            # Find arrow functions assigned to variables
            entities.extend(self._extract_arrow_functions(source, file_path))

            return entities

        except Exception:
            return []

    def _extract_functions(self, source: str, file_path: str) -> list[CodeEntity]:
        """Extract function declarations."""
        entities = []

        # Pattern for function declarations
        pattern = r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"

        for match in re.finditer(pattern, source):
            line_num = source[:match.start()].count("\n") + 1
            name = match.group(1)
            params = match.group(2)

            # Extract function body
            code = self._extract_function_body(source, match.start())

            entities.append(CodeEntity(
                type="function",
                name=name,
                file_path=file_path,
                line_number=line_num,
                docstring=self._extract_jsdoc(source, match.start()),
                code=code,
                signature=f"{name}({params})",
            ))

        return entities

    def _extract_classes(self, source: str, file_path: str) -> list[CodeEntity]:
        """Extract class declarations."""
        entities = []

        # Pattern for class declarations
        pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?"

        for match in re.finditer(pattern, source):
            line_num = source[:match.start()].count("\n") + 1
            name = match.group(1)
            extends = match.group(2)

            # Extract class body
            code = self._extract_class_body(source, match.start())

            signature = f"class {name}"
            if extends:
                signature += f" extends {extends}"

            entities.append(CodeEntity(
                type="class",
                name=name,
                file_path=file_path,
                line_number=line_num,
                docstring=self._extract_jsdoc(source, match.start()),
                code=code,
                signature=signature,
            ))

        return entities

    def _extract_arrow_functions(self, source: str, file_path: str) -> list[CodeEntity]:
        """Extract arrow function assignments."""
        entities = []

        # Pattern for arrow functions
        pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>"

        for match in re.finditer(pattern, source):
            line_num = source[:match.start()].count("\n") + 1
            name = match.group(1)
            params = match.group(2)

            entities.append(CodeEntity(
                type="function",
                name=name,
                file_path=file_path,
                line_number=line_num,
                docstring=self._extract_jsdoc(source, match.start()),
                code=source[match.start():match.end() + 100],  # Approximate
                signature=f"{name}({params})",
            ))

        return entities

    def _extract_function_body(self, source: str, start: int) -> str:
        """Extract function body by matching braces."""
        brace_count = 0
        in_function = False
        end = start

        for i in range(start, len(source)):
            if source[i] == "{":
                brace_count += 1
                in_function = True
            elif source[i] == "}":
                brace_count -= 1
                if in_function and brace_count == 0:
                    end = i + 1
                    break

        return source[start:end]

    def _extract_class_body(self, source: str, start: int) -> str:
        """Extract class body by matching braces."""
        return self._extract_function_body(source, start)

    def _extract_jsdoc(self, source: str, pos: int) -> str | None:
        """Extract JSDoc comment before position."""
        # Look backwards for /** ... */
        before = source[:pos]
        match = re.search(r"/\*\*(.*?)\*/", before[::-1], re.DOTALL)
        if match:
            return match.group(1)[::-1].strip()
        return None


def get_parser_for_file(file_path: str):
    """Get appropriate parser for file type.
    
    Args:
        file_path: Path to file
        
    Returns:
        Parser instance or None if unsupported
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".py":
        return PythonASTParser()
    if ext in [".js", ".ts", ".jsx", ".tsx"]:
        return JavaScriptParser()
    return None

