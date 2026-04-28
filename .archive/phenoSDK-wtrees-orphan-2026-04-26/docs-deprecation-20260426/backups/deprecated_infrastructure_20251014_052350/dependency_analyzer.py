"""Dependency analysis for code."""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DependencyInfo:
    """Information about dependencies in code.
    
    Attributes:
        external_packages: External package dependencies
        internal_modules: Internal module dependencies
        imports_by_file: Import statements by file
        dependency_graph: File-to-file dependency graph
        circular_dependencies: List of circular dependency chains
        unused_imports: Potentially unused imports
    """
    external_packages: set[str]
    internal_modules: dict[str, list[str]]
    imports_by_file: dict[str, list[str]]
    dependency_graph: dict[str, set[str]]
    circular_dependencies: list[list[str]]
    unused_imports: list[tuple[str, str, int]]  # (file, import, line)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "external_packages": sorted(list(self.external_packages)),
            "internal_modules": {k: v for k, v in self.internal_modules.items()},
            "imports_by_file": {k: v for k, v in self.imports_by_file.items()},
            "dependency_graph": {k: list(v) for k, v in self.dependency_graph.items()},
            "circular_dependencies": self.circular_dependencies,
            "unused_imports": [
                {"file": f, "import": i, "line": l}
                for f, i, l in self.unused_imports
            ],
        }


class DependencyAnalyzer:
    """Analyze code dependencies and imports."""

    def __init__(self):
        """Initialize the dependency analyzer."""
        self.stdlib_modules = self._get_stdlib_modules()

    def analyze_project(self, root_path: str, file_patterns: list[str] = None) -> DependencyInfo:
        """Analyze dependencies for entire project.
        
        Args:
            root_path: Root directory of project
            file_patterns: File patterns to analyze (default: ["*.py"])
            
        Returns:
            DependencyInfo with complete dependency analysis
        """
        file_patterns = file_patterns or ["*.py"]

        external_packages = set()
        internal_modules = {}
        imports_by_file = {}
        dependency_graph = {}

        root = Path(root_path)

        # Collect all Python files
        python_files = []
        for pattern in file_patterns:
            python_files.extend(root.rglob(pattern))

        # Analyze each file
        for file_path in python_files:
            if not file_path.is_file():
                continue

            file_str = str(file_path)

            try:
                imports = self._extract_imports(file_str)
                imports_by_file[file_str] = imports

                # Categorize imports
                for imp in imports:
                    if self._is_external_package(imp):
                        external_packages.add(imp.split(".")[0])
                    else:
                        if file_str not in internal_modules:
                            internal_modules[file_str] = []
                        internal_modules[file_str].append(imp)

                # Build dependency graph
                deps = self._resolve_dependencies(file_str, imports, root_path)
                if deps:
                    dependency_graph[file_str] = set(deps)

            except Exception:
                continue

        # Find circular dependencies
        circular = self._find_circular_dependencies(dependency_graph)

        # Find unused imports (simplified)
        unused = self._find_unused_imports(imports_by_file)

        return DependencyInfo(
            external_packages=external_packages,
            internal_modules=internal_modules,
            imports_by_file=imports_by_file,
            dependency_graph=dependency_graph,
            circular_dependencies=circular,
            unused_imports=unused,
        )

    def _extract_imports(self, file_path: str) -> list[str]:
        """Extract import statements from Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of imported module names
        """
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception:
            pass

        return imports

    def _is_external_package(self, module_name: str) -> bool:
        """Check if module is an external package.
        
        Args:
            module_name: Module name to check
            
        Returns:
            True if external package, False if stdlib or internal
        """
        base_module = module_name.split(".")[0]

        # Check if it's a standard library module
        if base_module in self.stdlib_modules:
            return False

        # Check if it's a relative import or internal module
        if base_module.startswith("."):
            return False

        # Assume it's external
        return True

    def _resolve_dependencies(
        self,
        file_path: str,
        imports: list[str],
        root_path: str,
    ) -> list[str]:
        """Resolve import statements to actual file paths.
        
        Args:
            file_path: Path to file being analyzed
            imports: List of import statements
            root_path: Project root path
            
        Returns:
            List of resolved file paths
        """
        dependencies = []
        root = Path(root_path)

        for imp in imports:
            # Skip external packages
            if self._is_external_package(imp):
                continue

            # Try to resolve to file
            module_path = imp.replace(".", "/")

            # Try as .py file
            potential_file = root / f"{module_path}.py"
            if potential_file.exists():
                dependencies.append(str(potential_file))
                continue

            # Try as __init__.py in directory
            potential_init = root / module_path / "__init__.py"
            if potential_init.exists():
                dependencies.append(str(potential_init))

        return dependencies

    def _find_circular_dependencies(
        self,
        dependency_graph: dict[str, set[str]],
    ) -> list[list[str]]:
        """Find circular dependencies in dependency graph.
        
        Args:
            dependency_graph: File-to-file dependency graph
            
        Returns:
            List of circular dependency chains
        """
        circular = []
        visited = set()

        def dfs(node: str, path: list[str]) -> None:
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in circular:
                    circular.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in dependency_graph.get(node, set()):
                dfs(neighbor, path.copy())

        for node in dependency_graph:
            dfs(node, [])

        return circular

    def _find_unused_imports(
        self,
        imports_by_file: dict[str, list[str]],
    ) -> list[tuple[str, str, int]]:
        """Find potentially unused imports (simplified).
        
        This is a simplified version. A full implementation would
        analyze actual usage in the code.
        
        Args:
            imports_by_file: Import statements by file
            
        Returns:
            List of (file, import, line) tuples for unused imports
        """
        # Simplified: just return empty list
        # Full implementation would check if imported names are used
        return []

    def _get_stdlib_modules(self) -> set[str]:
        """Get set of Python standard library module names.
        
        Returns:
            Set of stdlib module names
        """
        # Common Python standard library modules
        return {
            "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
            "asyncore", "atexit", "audioop", "base64", "bdb", "binascii",
            "binhex", "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb",
            "chunk", "cmath", "cmd", "code", "codecs", "codeop", "collections",
            "colorsys", "compileall", "concurrent", "configparser", "contextlib",
            "contextvars", "copy", "copyreg", "cProfile", "crypt", "csv",
            "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal",
            "difflib", "dis", "distutils", "doctest", "email", "encodings",
            "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput",
            "fnmatch", "formatter", "fractions", "ftplib", "functools", "gc",
            "getopt", "getpass", "gettext", "glob", "graphlib", "grp", "gzip",
            "hashlib", "heapq", "hmac", "html", "http", "imaplib", "imghdr",
            "imp", "importlib", "inspect", "io", "ipaddress", "itertools",
            "json", "keyword", "lib2to3", "linecache", "locale", "logging",
            "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes",
            "mmap", "modulefinder", "msilib", "msvcrt", "multiprocessing",
            "netrc", "nis", "nntplib", "numbers", "operator", "optparse", "os",
            "ossaudiodev", "parser", "pathlib", "pdb", "pickle", "pickletools",
            "pipes", "pkgutil", "platform", "plistlib", "poplib", "posix",
            "posixpath", "pprint", "profile", "pstats", "pty", "pwd", "py_compile",
            "pyclbr", "pydoc", "queue", "quopri", "random", "re", "readline",
            "reprlib", "resource", "rlcompleter", "runpy", "sched", "secrets",
            "select", "selectors", "shelve", "shlex", "shutil", "signal",
            "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
            "spwd", "sqlite3", "ssl", "stat", "statistics", "string", "stringprep",
            "struct", "subprocess", "sunau", "symbol", "symtable", "sys",
            "sysconfig", "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile",
            "termios", "test", "textwrap", "threading", "time", "timeit", "tkinter",
            "token", "tokenize", "trace", "traceback", "tracemalloc", "tty",
            "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
            "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
            "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml",
            "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
        }

