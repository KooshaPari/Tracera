import ast
import os
from collections import defaultdict
from pathlib import Path


def get_module_name(file_path, src_root):
    try:
        rel_path = file_path.relative_to(src_root)
        module_parts = list(rel_path.parts)
        module_parts[-1] = module_parts[-1].replace(".py", "")
        if module_parts[-1] == "__init__":
            module_parts.pop()
        return ".".join(module_parts)
    except ValueError:
        return None


def get_imports(file_path):
    with Path(file_path).open(encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
            elif node.level:  # Relative import
                imports.append("." * node.level + (node.module or ""))
    return imports


def build_dependency_graph(root_dirs):
    graph = defaultdict(set)
    file_map = {}

    cwd = Path.cwd()

    # First pass: map files to modules
    for root_dir in root_dirs:
        root_path = Path(root_dir).resolve()
        for path in root_path.rglob("*.py"):
            if "site-packages" in path.parts or ".venv" in path.parts or "__pycache__" in path.parts:
                continue

            # Determine module name
            # For src/tracertm/..., we want tracertm...
            # For backend/tests/..., we want backend.tests...

            try:
                if "src" in root_path.parts:
                    # src is usually a root for imports
                    module_name = get_module_name(path, root_path)
                else:
                    # backend logic
                    rel = path.relative_to(cwd)
                    module_name = ".".join(rel.parts).replace(".py", "").replace(os.sep, ".")
                    module_name = module_name.removesuffix(".__init__")

                if module_name:
                    file_map[module_name] = path
            except Exception:
                pass

    # Second pass: analyze imports
    for module, path in file_map.items():
        raw_imports = get_imports(path)
        for imp in raw_imports:
            # Check if import matches a known module

            # Direct match
            if imp in file_map:
                graph[module].add(imp)
                continue

            # Submodule match (import tracertm.core.foo -> dependency on tracertm.core.foo)
            # OR Parent match (import tracertm.core -> dependency on tracertm.core package (init))

            # Check if 'imp' is a prefix of any known module (meaning importing a package)
            # or if any known module is a prefix of 'imp' (meaning importing a specific submodule not fully mapped or mapped exact)

            # 1. Exact match in file_map keys (Already checked)

            # 2. Check if the import corresponds to a package (folder) that contains modules
            # E.g. import tracertm.core -> matches tracertm.core if tracertm/core/__init__.py exists
            # This is covered by file_map if __init__.py exists.

            # 3. Check if we import a class/function from a module
            # from tracertm.core.config import Config
            # imp is tracertm.core.config.Config? No, AST gives 'tracertm.core.config' for module.
            # So typically we just check if the module path exists.

            # Let's try to match the import string against keys
            best_match = None
            for known_mod in file_map:
                if imp == known_mod:
                    best_match = known_mod
                    break
                # If imp is 'tracertm.core.config' and known is 'tracertm.core', we might not match if config.py exists but isn't scanned?
                # But we scanned everything.

                # If we import 'tracertm.utils', and we have 'tracertm.utils', match.

            if best_match:
                graph[module].add(best_match)
            else:
                # Try to find if 'imp' starts with a known internal package
                # e.g. imp = 'tracertm.core.something_external' (unlikely if strictly internal)
                # or imp = 'tracertm.core' and we have 'tracertm.core.submodule'

                parts = imp.split(".")
                # Iteratively check prefixes
                for i in range(len(parts), 0, -1):
                    prefix = ".".join(parts[:i])
                    if prefix in file_map:
                        graph[module].add(prefix)
                        break

    return graph


def main() -> None:
    dirs = ["src", "backend"]
    dirs = [d for d in dirs if Path(d).exists()]

    graph = build_dependency_graph(dirs)

    sorted_modules = sorted(graph.keys())
    for mod in sorted_modules:
        deps = sorted(graph[mod])
        if deps:
            for _dep in deps:
                pass


if __name__ == "__main__":
    main()
