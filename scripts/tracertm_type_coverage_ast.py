from __future__ import annotations

import argparse
import ast
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Missing:
    file: str
    line: int
    func: str
    kind: str  # 'param' | 'return'
    detail: str


def iter_py_files(root: str) -> list[str]:
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in {
                "__pycache__",
                ".venv",
                "venv",
                ".mypy_cache",
                ".pytest_cache",
            }
            # Generated protobuf/grpc stubs live under src/tracertm/proto.
            and d != "proto"
        ]
        for fn in filenames:
            if fn.endswith(".py"):
                if fn.endswith("_pb2.py") or fn.endswith("_pb2_grpc.py"):
                    continue
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def is_selfish(name: str) -> bool:
    return name in {"self", "cls"}


class CoverageVisitor(ast.NodeVisitor):
    def __init__(self, file: str, *, include_methods: bool):
        self.file = file
        self.include_methods = include_methods
        self._class_depth = 0
        self.missing: list[Missing] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    def _eligible(self) -> bool:
        if self.include_methods:
            return True
        return self._class_depth == 0

    def _check_func(self, node: ast.AST, name: str, args: ast.arguments, returns: ast.expr | None):
        if not self._eligible():
            return

        if returns is None:
            self.missing.append(Missing(self.file, getattr(node, "lineno", 1), name, "return", "missing"))

        def check_arg(a: ast.arg, *, kind: str):
            if is_selfish(a.arg):
                return
            if a.annotation is None:
                self.missing.append(
                    Missing(
                        self.file,
                        getattr(a, "lineno", getattr(node, "lineno", 1)),
                        name,
                        "param",
                        f"{kind}:{a.arg}",
                    )
                )

        for a in args.posonlyargs:
            check_arg(a, kind="posonly")
        for a in args.args:
            check_arg(a, kind="pos")
        if args.vararg is not None:
            check_arg(args.vararg, kind="vararg")
        for a in args.kwonlyargs:
            check_arg(a, kind="kwonly")
        if args.kwarg is not None:
            check_arg(args.kwarg, kind="kwarg")

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_func(node, node.name, node.args, node.returns)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_func(node, node.name, node.args, node.returns)
        self.generic_visit(node)


def _missing_by_function(all_missing: list[Missing], kind: str) -> set[tuple[str, str]]:
    return {(m.file, m.func) for m in all_missing if m.kind == kind}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="src/tracertm")
    ap.add_argument("--include-methods", action="store_true")
    ap.add_argument("--sample", type=int, default=30)
    args = ap.parse_args()

    files = iter_py_files(args.root)
    all_missing: list[Missing] = []

    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            src = fh.read()
        try:
            tree = ast.parse(src, filename=f)
        except SyntaxError:
            continue

        v = CoverageVisitor(f, include_methods=args.include_methods)
        v.visit(tree)
        all_missing.extend(v.missing)

    miss_params = _missing_by_function(all_missing, "param")
    miss_returns = _missing_by_function(all_missing, "return")

    print(
        " ".join(
            [
                f"files={len(files)}",
                f"functions_missing_param_types={len(miss_params)}",
                f"functions_missing_return_types={len(miss_returns)}",
                f"total_missing_items={len(all_missing)}",
            ]
        )
    )

    for m in all_missing[: args.sample]:
        print(f"{m.file}:{m.line} {m.func} {m.kind} {m.detail}")

    return 0 if not all_missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
