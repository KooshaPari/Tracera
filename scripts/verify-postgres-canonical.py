#!/usr/bin/env python3
"""Exercise canonical HTTP behavior against the real database-backed server.

PostgreSQL is the required CI default; --backend sqlite supports local parity.

The eight-link computation input deliberately contains A4 -> DANGLING. Canonical
import must reject it atomically; the explicitly valid seven-link graph persists.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

LINKS = [
    ("A0", "A1", "implements"),
    ("A1", "A2", "depends_on"),
    ("A2", "A3", "verifies"),
    ("A3", "A4", "satisfies"),
    ("A2", "A6", "depends_on"),
    ("A4", "DANGLING", "depends_on"),
    ("A10", "A11", "implements"),
    ("A11", "A12", "verifies"),
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def request(base, path, expected, payload=None, csrf=None, method=None):
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        headers.update(
            {
                "Content-Type": "application/json",
                "Origin": "http://127.0.0.1:18000",
                "X-CSRF-Token": csrf or "",
            }
        )
    if method and method != "GET":
        headers.update({"Origin": "http://127.0.0.1:18000", "X-CSRF-Token": csrf or ""})
    req = urllib.request.Request(base + path, body, headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    if status == expected == 204 and not raw:
        return None
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as error:
        if status == expected == 404 and not raw:
            return None
        raise AssertionError(f"{path}: response was not JSON: {raw[:300]!r}") from error
    require(status == expected, f"{path}: expected HTTP {expected}, got {status}: {result}")
    return result


def project_path(project_id, suffix=""):
    return "/api/v1/projects/" + urllib.parse.quote(project_id, safe="") + suffix


def query(path, **params):
    return path + "?" + urllib.parse.urlencode(params)


def start_server(binary, database_url, bind_addr, base, log):
    env = os.environ.copy()
    env.update({"DATABASE_URL": database_url, "TRACERA_BIND_ADDR": bind_addr})
    process = subprocess.Popen([binary], env=env, stdout=log, stderr=subprocess.STDOUT)
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"server exited during startup with status {process.returncode}")
        try:
            if request(base, "/health", 200).get("status") == "ok":
                request(base, "/ready", 200)
                return process
        except (urllib.error.URLError, AssertionError):
            pass
        time.sleep(0.2)
    stop_server(process)
    raise TimeoutError("server did not become healthy within 40 seconds")


def stop_server(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def node_ids(graph):
    return {node["id"] for node in graph["nodes"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, help="built tracera-server executable")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--backend", choices=("postgres", "sqlite"), default="postgres")
    parser.add_argument("--bind-addr", default="127.0.0.1:18384")
    args = parser.parse_args()
    require(
        args.database_url
        and args.database_url.startswith(
            ("postgres://", "postgresql://") if args.backend == "postgres" else ("sqlite://",)
        ),
        "DATABASE_URL must match the selected backend",
    )
    require(args.bind_addr.startswith("127.0.0.1:"), "bind address must be loopback")
    base = "http://" + args.bind_addr
    run = uuid.uuid4().hex[:12]
    valid_id, invalid_id, other_id, cross_id = (
        f"pg-smoke-{kind}-{run}" for kind in ("valid", "invalid", "other", "cross")
    )
    items = [
        {
            "id": f"A{i}",
            "title": f"Synthetic artifact {i}",
            "view": "traceability",
            "type": "requirement",
            "status": "active",
        }
        for i in range(20)
    ]
    full_links = [
        {"source_id": source, "target_id": target, "type": kind} for source, target, kind in LINKS
    ]
    valid_links = [link for link in full_links if link["target_id"] != "DANGLING"]
    require(
        len(items) == 20 and len(full_links) == 8 and len(valid_links) == 7,
        "fixture counts changed",
    )
    fixture_bytes = json.dumps(
        {"items": items, "links": full_links}, sort_keys=True, separators=(",", ":")
    ).encode()
    fixture_sha256 = hashlib.sha256(fixture_bytes).hexdigest()

    def export(project_id, selected_items, selected_links):
        return {
            "project": {"id": project_id, "name": "Postgres smoke " + run},
            "items": selected_items,
            "links": selected_links,
        }

    with tempfile.TemporaryFile(mode="w+t") as log:
        process = None
        try:
            process = start_server(args.binary, args.database_url, args.bind_addr, base, log)
            csrf = request(base, "/api/v1/csrf-token", 200)["token"]

            rejected = request(
                base, "/api/v1/import", 400, export(invalid_id, items, full_links), csrf
            )
            require(
                rejected.get("unresolved_ids") == ["DANGLING"],
                f"wrong dangling diagnostic: {rejected}",
            )
            request(base, project_path(invalid_id), 404)

            created = request(
                base, "/api/v1/import", 201, export(valid_id, items, valid_links), csrf
            )
            require(
                created["project_id"] == valid_id
                and created["items_imported"] == 20
                and created["links_imported"] == 7,
                f"wrong import receipt: {created}",
            )
            returned_items = request(
                base, query("/api/v1/items", project_id=valid_id, limit=500), 200
            )
            require(
                returned_items["total"] == 20
                and {item["id"] for item in returned_items["items"]}
                == {item["id"] for item in items},
                "item IDs or count changed",
            )
            returned_links = request(
                base, query("/api/v1/links", project_id=valid_id, limit=500), 200
            )
            expected_links = {(x["source_id"], x["target_id"], x["type"]) for x in valid_links}
            actual_links = {
                (x["source_id"], x["target_id"], x["type"]) for x in returned_links["links"]
            }
            require(
                returned_links["total"] == 7 and actual_links == expected_links,
                "typed links changed",
            )
            forward = request(
                base,
                query(
                    "/api/v1/graph/traverse/A0",
                    project_id=valid_id,
                    direction="down",
                    depth=1,
                ),
                200,
            )
            reverse = request(
                base,
                query(
                    "/api/v1/graph/traverse/A3",
                    project_id=valid_id,
                    direction="up",
                    depth=1,
                ),
                200,
            )
            impact = request(
                base,
                query(
                    "/api/v1/graph/traverse/A0",
                    project_id=valid_id,
                    direction="down",
                    depth=32,
                ),
                200,
            )
            require(
                node_ids(forward) == {"A0", "A1"},
                f"forward traversal mismatch: {forward}",
            )
            require(
                node_ids(reverse) == {"A2", "A3"},
                f"reverse traversal mismatch: {reverse}",
            )
            require(
                node_ids(impact) == {"A0", "A1", "A2", "A3", "A4", "A6"},
                f"valid component mismatch: {impact}",
            )
            full_export = request(base, project_path(valid_id, "/export?format=full"), 200)
            require(
                len(full_export["items"]) == 20 and len(full_export["links"]) == 7,
                "export counts changed",
            )
            require(
                {(x["source_id"], x["target_id"], x["type"]) for x in full_export["links"]}
                == expected_links,
                "export links changed",
            )

            other_items = [{**items[0], "title": "Other project A0"}, items[19]]
            other_links = [{"source_id": "A19", "target_id": "A0", "type": "depends_on"}]
            request(
                base,
                "/api/v1/import",
                201,
                export(other_id, other_items, other_links),
                csrf,
            )
            other_graph = request(
                base,
                query(
                    "/api/v1/graph/traverse/A0",
                    project_id=other_id,
                    direction="down",
                    depth=32,
                ),
                200,
            )
            require(
                node_ids(other_graph) == {"A0"},
                f"cross-project graph leakage: {other_graph}",
            )
            cross = request(
                base,
                "/api/v1/import",
                400,
                export(
                    cross_id,
                    [items[0]],
                    [{"source_id": "A0", "target_id": "A1", "type": "depends_on"}],
                ),
                csrf,
            )
            require(
                cross.get("unresolved_ids") == ["A1"],
                f"cross-project target was resolved: {cross}",
            )
            request(base, project_path(cross_id), 404)

            stop_server(process)
            process = None
            process = start_server(args.binary, args.database_url, args.bind_addr, base, log)
            after_restart = request(base, project_path(valid_id, "/export?format=full"), 200)
            require(
                len(after_restart["items"]) == 20 and len(after_restart["links"]) == 7,
                "project did not survive PostgreSQL server restart",
            )
            require(
                {(x["source_id"], x["target_id"], x["type"]) for x in after_restart["links"]}
                == expected_links,
                "link data changed after restart",
            )
            restart_graph = request(
                base,
                query(
                    "/api/v1/graph/traverse/A0",
                    project_id=valid_id,
                    direction="down",
                    depth=32,
                ),
                200,
            )
            require(
                node_ids(restart_graph) == node_ids(impact),
                "graph traversal changed after restart",
            )
            # Interactive CRUD receipts use an isolated synthetic project, so
            # the original 20-item/7-link fixture remains comparable.
            csrf = request(base, "/api/v1/csrf-token", 200)["token"]
            edit_id = f"pg-smoke-edit-{run}"
            original = dict(
                items[0],
                source_url="https://github.com/KooshaPari/Tracera/issues/1",
                source_repo="KooshaPari/Tracera",
                source_kind="github_issue",
            )
            request(base, "/api/v1/import", 201, export(edit_id, [original], []), csrf)
            new_item = {
                "project_id": edit_id,
                "id": "new:node",
                "title": "Created",
                "view": "traceability",
                "type": "requirement",
                "status": "draft",
            }
            request(base, "/api/v1/items", 201, new_item, csrf)
            request(base, "/api/v1/items", 409, new_item, csrf)
            item_path = query("/api/v1/items/A0", project_id=edit_id)
            updated = request(
                base,
                item_path,
                200,
                {"title": "Edited", "description": None},
                csrf,
                "PATCH",
            )
            require(
                updated["source_url"] == original["source_url"],
                "edit lost source provenance",
            )
            request(
                base,
                item_path,
                400,
                {"source_url": "https://example.invalid/fabricated"},
                csrf,
                "PATCH",
            )
            request(base, "/api/v1/items/A0", 400, {"title": "No scope"}, csrf, "PATCH")
            require(
                request(base, query("/api/v1/items/A0", project_id=other_id), 200)["title"]
                != "Edited",
                "same-ID edit leaked across projects",
            )
            link = {
                "project_id": edit_id,
                "source_id": "A0",
                "target_id": "new:node",
                "type": "refines:typed",
            }
            created_link = request(base, "/api/v1/links", 201, link, csrf)
            replace_path = query("/api/v1/links/" + created_link["id"], project_id=edit_id)
            request(
                base,
                replace_path,
                400,
                {"source_id": "A0", "target_id": "missing", "type": "refines:typed"},
                csrf,
                "PUT",
            )
            created_link = request(
                base,
                replace_path,
                200,
                {"source_id": "new:node", "target_id": "A0", "type": "verifies:typed"},
                csrf,
                "PUT",
            )
            before = request(base, project_path(edit_id, "/export?format=full"), 200)
            request(base, "/api/v1/links", 400, dict(link, target_id="missing"), csrf)
            request(base, "/api/v1/links", 400, dict(link, project_id=other_id), csrf)
            require(
                before == request(base, project_path(edit_id, "/export?format=full"), 200),
                "rejected link changed persisted graph",
            )
            stop_server(process)
            process = None
            process = start_server(args.binary, args.database_url, args.bind_addr, base, log)
            require(
                before == request(base, project_path(edit_id, "/export?format=full"), 200),
                "interactive edits did not survive restart",
            )
            csrf = request(base, "/api/v1/csrf-token", 200)["token"]
            link_path = query("/api/v1/links/" + created_link["id"], project_id=edit_id)
            request(base, link_path, 204, csrf=csrf, method="DELETE")
            request(base, link_path, 404, csrf=csrf, method="DELETE")
            request(base, "/api/v1/links", 201, link, csrf)
            request(base, item_path, 204, csrf=csrf, method="DELETE")
            remaining = request(base, project_path(edit_id, "/export?format=full"), 200)
            require(
                len(remaining["items"]) == 1 and not remaining["links"],
                "item deletion did not cascade its incident links",
            )
            require(
                request(base, query("/api/v1/items/A0", project_id=other_id), 200)["id"] == "A0",
                "same-ID deletion leaked across projects",
            )
            request(base, project_path(invalid_id), 404)
            print(
                json.dumps(
                    {
                        "passed": True,
                        "backend": args.backend,
                        "fixture_sha256": fixture_sha256,
                        "run_id": run,
                        "valid_items": 20,
                        "valid_links": 7,
                        "dangling_link_rejected": True,
                        "cross_project_isolation": True,
                        "restart_readback": True,
                        "interactive_crud_restart": True,
                        "interactive_provenance_retained": True,
                        "interactive_delete_cascade": True,
                        "interactive_link_replace": True,
                    },
                    sort_keys=True,
                )
            )
        except Exception:
            log.flush()
            log.seek(0)
            print("tracera-server log tail:\n" + log.read()[-5000:], file=sys.stderr)
            raise
        finally:
            if process is not None:
                stop_server(process)


if __name__ == "__main__":
    main()
