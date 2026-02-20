#!/usr/bin/env python3
"""populate_feature_graph_links module."""

import operator
import os
import re
import uuid
from collections import defaultdict
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.environ.get(
    "TRACERTM_DATABASE_URL",
    "postgresql://kooshapari@localhost:5432/agent_api",
)

DOMAIN_KEYWORDS = {
    "channel": "chan",
    "channels": "chan",
    "dm": "dm",
    "direct message": "dm",
    "message": "msg",
    "messages": "msg",
    "thread": "thread",
    "threads": "thread",
    "file": "file",
    "files": "file",
    "reaction": "msg",
    "emoji": "msg",
    "mention": "mention",
    "notification": "mention",
    "search": "search",
    "user": "user",
    "profile": "user",
    "presence": "user",
    "workspace": "admin",
    "admin": "admin",
    "audit": "admin",
    "invite": "chan",
    "analytics": "analytics",
    "report": "analytics",
    "workflow": "workflow",
    "security": "sec",
    "encryption": "sec",
    "sso": "sec",
    "auth": "sec",
    "performance": "perf",
    "cache": "perf",
    "rate": "perf",
    "voice": "voice",
    "video": "voice",
    "call": "voice",
    "mobile": "mobile",
    "ios": "mobile",
    "android": "mobile",
    "integration": "integ",
    "webhook": "integ",
    "bot": "integ",
}

DOMAIN_ALIASES = {
    "channel": "chan",
    "channels": "chan",
    "message": "msg",
    "messages": "msg",
    "directmessage": "dm",
    "dms": "dm",
    "dm": "dm",
    "thread": "thread",
    "threads": "thread",
    "file": "file",
    "files": "file",
    "reaction": "msg",
    "emoji": "msg",
    "mention": "mention",
    "notification": "mention",
    "user": "user",
    "users": "user",
    "workspace": "admin",
    "admin": "admin",
    "audit": "admin",
    "typing": "msg",
    "search": "search",
}

ID_PREFIXES = {
    "req",
    "feat",
    "story",
    "task",
    "test",
    "api",
    "ui",
    "schema",
}

UI_HUB_PREFERENCES = ["List", "Panel", "Input", "Header", "Viewer", "Table", "Card"]


def normalize(text: str) -> str:
    """Normalize."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def domain_from_text(text: str) -> str | None:
    """Domain from text."""
    lower = text.lower()
    for key, domain in DOMAIN_KEYWORDS.items():
        if key in lower:
            return domain
    return None


def domain_from_id(item_id: str, title: str) -> str | None:
    """Domain from id."""
    parts = item_id.split("_")
    if parts and parts[0] in ID_PREFIXES and len(parts) > 1:
        token = parts[1]
        return DOMAIN_ALIASES.get(token, token)
    return domain_from_text(title)


def choose_ui_hub(components: list[dict]) -> dict | None:
    """Choose ui hub."""
    if not components:
        return None
    for pref in UI_HUB_PREFERENCES:
        for comp in components:
            if pref.lower() in comp["title"].lower():
                return comp
    return components[0]


def base_path_from_api(title: str) -> str:
    """Base path from api."""
    # Title format: "GET /api/v1/channels/{channelId}"
    match = re.search(r"\s(/api[^\s]+)", title)
    if not match:
        return ""
    path = match.group(1)
    # Strip trailing path params and subresources
    parts = path.split("/")
    if len(parts) >= 4:
        return "/".join(parts[:4])
    return path


def fetch_all(conn: Any, query: Any, params: Any = None) -> None:
    """Fetch all."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or {})
        return cur.fetchall()


def main() -> None:
    """Main."""
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = False
    try:
        projects = fetch_all(conn, "select id from projects")

        for project in projects:
            project_id = project["id"]
            graphs = fetch_all(
                conn,
                "select id, graph_type from graphs where project_id = %(pid)s",
                {"pid": project_id},
            )
            graph_by_type = {g["graph_type"]: g["id"] for g in graphs}
            default_graph_id = graph_by_type.get("default")
            mapping_graph_id = graph_by_type.get("mapping")

            items = fetch_all(
                conn,
                "select id, view, item_type, title from items where project_id = %(pid)s and deleted_at is null",
                {"pid": project_id},
            )
            if not items:
                continue

            if not mapping_graph_id:
                mapping_graph_id = str(uuid.uuid4())
                conn.cursor().execute(
                    """
                    insert into graphs (id, project_id, name, graph_type, description, graph_metadata, graph_version, graph_rules)
                    values (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)
                    """,
                    (
                        mapping_graph_id,
                        project_id,
                        "mapping graph",
                        "mapping",
                        "Cross-view mapping graph",
                        "{}",
                        1,
                        "{}",
                    ),
                )

            by_view_domain: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
            for item in items:
                domain = domain_from_id(item["id"], item["title"]) or "misc"
                by_view_domain[item["view"]][domain].append(item)

            existing_links = fetch_all(
                conn,
                "select graph_id, source_item_id, target_item_id, link_type from links where project_id = %(pid)s",
                {"pid": project_id},
            )
            link_set = {
                (row["graph_id"], row["source_item_id"], row["target_item_id"], row["link_type"])
                for row in existing_links
            }

            graph_node_set = {
                (row["graph_id"], row["item_id"])
                for row in fetch_all(
                    conn,
                    "select graph_id, item_id from graph_nodes where project_id = %(pid)s",
                    {"pid": project_id},
                )
            }

            def ensure_graph_node(
                graph_id: str | None,
                item_id: str,
                _graph_node_set: set = graph_node_set,
                _project_id: str = project_id,
            ) -> None:
                if not graph_id:
                    return
                key = (graph_id, item_id)
                if key in _graph_node_set:
                    return
                _graph_node_set.add(key)
                conn.cursor().execute(
                    """
                    insert into graph_nodes (graph_id, item_id, project_id, is_primary)
                    values (%s, %s, %s, %s)
                    on conflict do nothing
                    """,
                    (graph_id, item_id, _project_id, False),
                )

            def insert_link(
                graph_id: str | None,
                source_id: str,
                target_id: str,
                link_type: str,
                _link_set: set = link_set,
                _project_id: str = project_id,
            ) -> None:
                if not graph_id or source_id == target_id:
                    return
                key = (graph_id, source_id, target_id, link_type)
                if key in _link_set:
                    return
                _link_set.add(key)
                conn.cursor().execute(
                    """
                    insert into links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, graph_id)
                    values (%s, %s, %s, %s, %s, %s::jsonb, %s)
                    """,
                    (str(uuid.uuid4()), _project_id, source_id, target_id, link_type, "{}", graph_id),
                )

            # Cross-view mapping in default graph
            if default_graph_id:
                for domain, reqs in by_view_domain.get("requirements", {}).items():
                    feats = by_view_domain.get("features", {}).get(domain, [])
                    for req in reqs:
                        for feat in feats:
                            insert_link(default_graph_id, req["id"], feat["id"], "traces_to")

                for domain, stories in by_view_domain.get("user_stories", {}).items():
                    feats = by_view_domain.get("features", {}).get(domain, [])
                    for story in stories:
                        for feat in feats:
                            insert_link(default_graph_id, story["id"], feat["id"], "implements")

                for domain, feats in by_view_domain.get("features", {}).items():
                    apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                    uis = by_view_domain.get("ui_components", {}).get(domain, [])
                    tasks = by_view_domain.get("tasks", {}).get(domain, [])
                    tests = by_view_domain.get("tests", {}).get(domain, [])
                    dbs = by_view_domain.get("database", {}).get(domain, [])
                    for feat in feats:
                        for api in apis:
                            insert_link(default_graph_id, feat["id"], api["id"], "implements")
                        for ui in uis:
                            insert_link(default_graph_id, feat["id"], ui["id"], "implements")
                        for task in tasks:
                            insert_link(default_graph_id, task["id"], feat["id"], "implements")
                        for test in tests:
                            insert_link(default_graph_id, test["id"], feat["id"], "tests")
                        for db in dbs:
                            insert_link(default_graph_id, feat["id"], db["id"], "implements")

                # API -> DB dependencies
                for domain, apis in by_view_domain.get("api_endpoints", {}).items():
                    dbs = by_view_domain.get("database", {}).get(domain, [])
                    for api in apis:
                        for db in dbs:
                            insert_link(default_graph_id, api["id"], db["id"], "depends_on")

                # UI -> API triggers
                for domain, uis in by_view_domain.get("ui_components", {}).items():
                    apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                    for ui in uis:
                        for api in apis:
                            insert_link(default_graph_id, ui["id"], api["id"], "depends_on")

            # UI components graph: link components by domain to a hub
            ui_graph_id = graph_by_type.get("ui_components")
            if ui_graph_id:
                for domain, components in by_view_domain.get("ui_components", {}).items():
                    hub = choose_ui_hub(components)
                    if not hub:
                        continue
                    for feat in by_view_domain.get("features", {}).get(domain, []):
                        ensure_graph_node(ui_graph_id, feat["id"])
                        for comp in components:
                            insert_link(ui_graph_id, comp["id"], feat["id"], "implements")
                    for comp in components:
                        if comp["id"] != hub["id"]:
                            insert_link(ui_graph_id, comp["id"], hub["id"], "related_to")

            # API endpoints graph: group by base path
            api_graph_id = graph_by_type.get("api_endpoints")
            if api_graph_id:
                api_items = by_view_domain.get("api_endpoints", {})
                for domain, apis in api_items.items():
                    groups: dict[str, list[dict]] = defaultdict(list)
                    for api in apis:
                        base = base_path_from_api(api["title"]) or domain
                        groups[base].append(api)
                    for group in groups.values():
                        hub = group[0]
                        for api in group[1:]:
                            insert_link(api_graph_id, api["id"], hub["id"], "related_to")

            # Database graph: link tables in same domain
            db_graph_id = graph_by_type.get("database")
            if db_graph_id:
                for tables in by_view_domain.get("database", {}).values():
                    hub = tables[0] if tables else None
                    if not hub:
                        continue
                    for table in tables[1:]:
                        insert_link(db_graph_id, table["id"], hub["id"], "related_to")

            # Mapping graph: isolate cross-view mappings here
            if mapping_graph_id:
                for domain, reqs in by_view_domain.get("requirements", {}).items():
                    feats = by_view_domain.get("features", {}).get(domain, [])
                    for req in reqs:
                        for feat in feats:
                            insert_link(mapping_graph_id, req["id"], feat["id"], "traces_to")

                for domain, stories in by_view_domain.get("user_stories", {}).items():
                    feats = by_view_domain.get("features", {}).get(domain, [])
                    for story in stories:
                        for feat in feats:
                            insert_link(mapping_graph_id, story["id"], feat["id"], "implements")

                for domain, feats in by_view_domain.get("features", {}).items():
                    apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                    uis = by_view_domain.get("ui_components", {}).get(domain, [])
                    tasks = by_view_domain.get("tasks", {}).get(domain, [])
                    tests = by_view_domain.get("tests", {}).get(domain, [])
                    dbs = by_view_domain.get("database", {}).get(domain, [])
                    for feat in feats:
                        for api in apis:
                            insert_link(mapping_graph_id, feat["id"], api["id"], "implements")
                        for ui in uis:
                            insert_link(mapping_graph_id, feat["id"], ui["id"], "implements")
                        for task in tasks:
                            insert_link(mapping_graph_id, task["id"], feat["id"], "implements")
                        for test in tests:
                            insert_link(mapping_graph_id, test["id"], feat["id"], "tests")
                        for db in dbs:
                            insert_link(mapping_graph_id, feat["id"], db["id"], "implements")

                for domain, uis in by_view_domain.get("ui_components", {}).items():
                    apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                    for ui in uis:
                        for api in apis:
                            insert_link(mapping_graph_id, ui["id"], api["id"], "depends_on")

            # Journey graph: simple ordered flow + UI/API mapping
            journey_graph_id = graph_by_type.get("journey")
            if journey_graph_id:
                for domain, journeys in by_view_domain.get("journey", {}).items():
                    ordered = sorted(journeys, key=operator.itemgetter("title"))
                    for idx in range(len(ordered) - 1):
                        insert_link(journey_graph_id, ordered[idx]["id"], ordered[idx + 1]["id"], "related_to")
                    uis = by_view_domain.get("ui_components", {}).get(domain, [])
                    apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                    for journey in ordered:
                        for ui in uis:
                            insert_link(journey_graph_id, journey["id"], ui["id"], "related_to")
                        for api in apis:
                            insert_link(journey_graph_id, journey["id"], api["id"], "depends_on")

            # Tasks graph: include features and link tasks -> feature
            tasks_graph_id = graph_by_type.get("tasks")
            if tasks_graph_id:
                for domain, tasks in by_view_domain.get("tasks", {}).items():
                    feats = by_view_domain.get("features", {}).get(domain, [])
                    for feat in feats:
                        ensure_graph_node(tasks_graph_id, feat["id"])
                    for task in tasks:
                        for feat in feats:
                            insert_link(tasks_graph_id, task["id"], feat["id"], "implements")

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
