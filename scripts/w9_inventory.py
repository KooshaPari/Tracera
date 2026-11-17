"""Inventory literal frontend API references without executing application code."""

import collections
import csv
import json
import pathlib
import re
from collections.abc import Callable, Iterator

ROOT = pathlib.Path(__file__).resolve().parents[1]
references = collections.defaultdict(set)
pattern = re.compile(r"/api/v1/(?:\$\{[^}]+\}|[^`\s\"\x27<>?)])+")


def _make_param_replacer(counter: Iterator[int]) -> Callable[[re.Match[str]], str]:
    """Return a callback that numbers each replaced match ``{param0}``, ``{param1}``.

    A factory is used instead of a ``lambda`` with a default argument so the
    callback closes over a function parameter rather than a loop variable
    (ruff B023) and carries an inferable type (mypy ``misc``).
    """

    def replace(_match: re.Match[str]) -> str:
        return "{param" + str(next(counter)) + "}"

    return replace


for source in (ROOT / "frontend/apps/web/src").rglob("*"):
    if source.suffix not in (".ts", ".tsx") or ".test." in source.name:
        continue
    for match in pattern.finditer(source.read_text(encoding="utf-8")):
        route = re.sub(r"\$\{[^}]+\}", "{id}", match.group())
        route = (
            re.sub(r"(?<=[^/])\{id\}$", "", route)
            if not route.endswith("/{id}")
            else route
        )
        if "..." in route or ":" in route:
            continue
        counter = iter(range(20))
        route = re.sub(r"\{[^}]+\}", _make_param_replacer(counter), route)
        references[route].add(source.relative_to(ROOT).as_posix())

spec_path = "frontend/apps/web/public/specs/openapi.json"
for route in json.loads((ROOT / spec_path).read_text(encoding="utf-8"))["paths"]:
    route = re.sub(r":([A-Za-z_]+)", r"{\1}", route)
    counter = iter(range(20))
    route = re.sub(r"\{[^}]+\}", _make_param_replacer(counter), route)
    references[route].add(spec_path)


def shape(route):
    return re.sub(r"\{[^}]+\}", "{}", route)


registered: dict[str, str] = {}
for source in (ROOT / "crates/tracera-server/src").rglob("*.rs"):
    if source.name.startswith("w9") or "test" in source.name:
        continue
    production = source.read_text(encoding="utf-8")
    if production.startswith("//! Unavailable "):
        continue
    production = production.split("// W9 unavailable routes (generated).")[0]
    for match in re.finditer(r'"(/[A-Za-z][^"\s]*)"', production):
        route = match[1]
        if "{{" in route or "{kind}" in route or "?" in route:
            continue
        if any(
            "{" in part and not (part.startswith("{") and part.endswith("}"))
            for part in route.split("/")
        ):
            continue
        registered.setdefault(shape(route), route)

# Specs uses format! registrations; include those actual registrations explicitly.
for kind in ("contracts", "features", "scenarios", "adrs"):
    for suffix in ("", "/{id}"):
        route = "/api/v1/" + kind + suffix
        registered[shape(route)] = route
    if kind != "scenarios":
        route = "/api/v1/projects/{project_id}/" + kind + "/stats"
        registered[shape(route)] = route


def family(route):
    parts = route.split("/")
    if not route.startswith("/api/v1/"):
        return parts[1]
    return parts[5] if parts[3] == "projects" and len(parts) > 5 else parts[3]


def canonical(route, prefixes):
    parts = route.split("/")
    for i, part in enumerate(parts):
        if part.startswith("{"):
            key = shape("/".join(parts[: i + 1]))
            parts[i] = prefixes.setdefault(
                key, "{id}" if i == 4 else "{param" + str(i) + "}"
            )
    return "/".join(parts)


def generate():
    prefixes = {}
    for route in registered.values():
        for i, part in enumerate(route.split("/")):
            if part.startswith("{"):
                prefixes.setdefault(shape("/".join(route.split("/")[: i + 1])), part)
    groups = collections.defaultdict(list)
    for route in sorted(references):
        if shape(route) not in registered:
            groups[family(route)].append(canonical(route, prefixes))
    out = ROOT / "crates/tracera-server/src/routes"
    modules = []
    declarations = []
    rows = []
    for group, routes in sorted(groups.items()):
        module = group.replace("-", "_")
        literal = "\n".join('    "' + r + '",' for r in routes)
        if group in ("graph", "items"):
            parent = "graph_routes" if group == "graph" else "item_routes"
            modules.append(
                ("super::" + parent + "::w9_routes", "super::" + parent + "::W9_ROUTES")
            )
            target = out / (module + ".rs")
            original = (
                target.read_text(encoding="utf-8")
                .split("// W9 unavailable routes (generated).")[0]
                .rstrip()
            )
            target.write_text(
                original + "\n\n// W9 unavailable routes (generated).\n"
                "pub(super) const W9_ROUTES: &[&str] = &[\n" + literal + "\n];\n"
                "pub(super) fn w9_routes() -> axum::Router<AppState> {\n"
                "    super::w9_routes::unavailable_routes(W9_ROUTES)\n}\n",
                encoding="utf-8",
            )
        else:
            declarations.append('#[path = "' + module + '.rs"]\nmod ' + module + ";")
            modules.append((module + "::routes", module + "::ROUTES"))
            (out / (module + ".rs")).write_text(
                "//! Unavailable "
                + group
                + " operations: no matching Store contract.\n"
                "use crate::AppState;\nuse axum::Router;\n\n"
                "pub(super) const ROUTES: &[&str] = &[\n" + literal + "\n];\n\n"
                "pub(super) fn routes() -> Router<AppState> {\n"
                "    super::unavailable_routes(ROUTES)\n}\n",
                encoding="utf-8",
            )
        rows += [
            (r, group, "501", "404 (unregistered)", "501", "THIS_PR", "ANY")
            for r in routes
        ]
    aggregate = "//! Remaining frontend route families; unavailable means unavailable, never empty.\n"
    aggregate += "use crate::AppState;\nuse axum::{routing::any, Router};\n\n"
    aggregate += "\n".join(declarations)
    aggregate += (
        "\n\npub(super) fn unavailable_routes(paths: &[&str]) -> Router<AppState> {\n"
    )
    aggregate += "    paths.iter().fold(Router::new(), |router, path| {\n"
    aggregate += "        router.route(path, any(crate::not_implemented::not_implemented))\n    })\n}\n"
    aggregate += "\npub(super) fn routes() -> Router<AppState> {\n    Router::new()\n"
    aggregate += "".join("        .merge(" + m[0] + "())\n" for m in modules) + "}\n"
    aggregate += "\n#[cfg(test)]\nfn templates() -> Vec<&'static str> {\n    [\n"
    aggregate += "".join("        " + m[1] + ",\n" for m in modules)
    aggregate += (
        '    ].concat()\n}\n\n#[cfg(test)]\n#[path = "w9_tests.rs"]\nmod tests;\n'
    )
    (out / "w9.rs").write_text(aggregate, encoding="utf-8")
    target = ROOT / "docs/operations/w9-route-decisions.csv"
    with target.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["route", "family", "decision", "before", "after", "pr", "methods"]
        )
        writer.writerows(rows)
        writer.writerows(
            [
                (
                    "/api/v1/projects",
                    "projects",
                    "501",
                    "201 (no write)",
                    "501",
                    "THIS_PR",
                    "POST",
                ),
                (
                    "/api/v1/projects/{project_id}",
                    "projects",
                    "501",
                    "200 (no write)",
                    "501",
                    "THIS_PR",
                    "PUT",
                ),
                (
                    "/api/v1/projects/{project_id}",
                    "projects",
                    "501",
                    "204 (no write)",
                    "501",
                    "THIS_PR",
                    "DELETE",
                ),
                (
                    "/org-intel/metrics",
                    "org-intel",
                    "501",
                    "200 (fabricated coverage/gaps)",
                    "501",
                    "THIS_PR",
                    "GET",
                ),
            ]
        )
    gateway = sorted(
        set(registered.values()) | {r[0] for r in rows},
        key=lambda r: (r.count("{"), -len(r), r),
    )
    (ROOT / "api/w9-route-templates.ts").write_text(
        "export default " + json.dumps(gateway, indent=2) + " as const;\n",
        encoding="utf-8",
    )
    print(f"Generated {len(rows)} routes in {len(modules)} families")


if __name__ == "__main__":
    import sys

    if "--generate" in sys.argv:
        generate()
    else:
        missing = [r for r in sorted(references) if shape(r) not in registered]
        print(json.dumps(missing, indent=2))
        print(collections.Counter(family(r) for r in missing))
