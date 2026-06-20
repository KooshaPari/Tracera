#!/usr/bin/env python3
"""augment_graph_semantics module."""

import json
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

GEN_TAG = "augment_graph_semantics_v1"

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
    "user": "user",
    "users": "user",
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
    "typing": "msg",
    "search": "search",
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

ID_PREFIXES = {"req", "feat", "story", "task", "test", "api", "ui", "schema"}

UI_HUB_PREFERENCES = ["List", "Panel", "Input", "Header", "Viewer", "Table", "Card"]


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
    match = re.search(r"\s(/api[^\s]+)", title)
    if not match:
        return ""
    path = match.group(1)
    parts = path.split("/")
    if len(parts) >= 4:
        return "/".join(parts[:4])
    return path


def tokenize(text: str) -> set[str]:
    """Tokenize."""
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def score_api_for_ui(ui_title: str, api_title: str) -> int:
    """Score api for ui."""
    ui_tokens = tokenize(ui_title)
    api_tokens = tokenize(api_title)
    if not ui_tokens or not api_tokens:
        return 0
    overlap = ui_tokens.intersection(api_tokens)
    return len(overlap)


def fetch_all(conn: Any, query: Any, params: Any = None) -> None:
    """Fetch all."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or {})
        return cur.fetchall()


def ensure_view(conn: Any, project_id: str, name: str) -> None:
    """Ensure view."""
    row = fetch_all(
        conn,
        "select id from views where project_id=%(pid)s and name=%(name)s",
        {"pid": project_id, "name": name},
    )
    if row:
        return row[0]["id"]
    view_id = str(uuid.uuid4())
    conn.cursor().execute(
        """
        insert into views (id, project_id, name, description, view_metadata)
        values (%s, %s, %s, %s, %s::jsonb)
        """,
        (view_id, project_id, name, None, "{}"),
    )
    return view_id


def ensure_node_kind(conn: Any, project_id: str, name: str) -> None:
    """Ensure node kind."""
    row = fetch_all(
        conn,
        "select id from node_kinds where project_id=%(pid)s and name=%(name)s",
        {"pid": project_id, "name": name},
    )
    if row:
        return row[0]["id"]
    kind_id = str(uuid.uuid4())
    conn.cursor().execute(
        """
        insert into node_kinds (id, project_id, name, description, kind_metadata)
        values (%s, %s, %s, %s, %s::jsonb)
        """,
        (kind_id, project_id, name, None, "{}"),
    )
    return kind_id


def ensure_item_view(conn: Any, item_id: str, project_id: str, view_id: str) -> None:
    """Ensure item view."""
    conn.cursor().execute(
        """
        insert into item_views (item_id, view_id, project_id, is_primary)
        values (%s, %s, %s, %s)
        on conflict do nothing
        """,
        (item_id, view_id, project_id, True),
    )


def ensure_graph_node(conn: Any, graph_id: str | None, item_id: str, project_id: str) -> None:
    """Ensure graph node."""
    if not graph_id:
        return
    conn.cursor().execute(
        """
        insert into graph_nodes (graph_id, item_id, project_id, is_primary)
        values (%s, %s, %s, %s)
        on conflict do nothing
        """,
        (graph_id, item_id, project_id, False),
    )


def insert_link(
    conn: Any,
    project_id: str,
    graph_id: str | None,
    source_id: str,
    target_id: str,
    link_type: str,
    ensure_nodes: bool = False,
) -> None:
    """Insert link."""
    if not graph_id or source_id == target_id:
        return
    if ensure_nodes:
        ensure_graph_node(conn, graph_id, source_id, project_id)
        ensure_graph_node(conn, graph_id, target_id, project_id)
    conn.cursor().execute(
        """
        insert into links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, graph_id)
        values (%s, %s, %s, %s, %s, %s::jsonb, %s)
        on conflict do nothing
        """,
        (str(uuid.uuid4()), project_id, source_id, target_id, link_type, "{}", graph_id),
    )


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
            journey_graph_id = graph_by_type.get("journey")
            tasks_graph_id = graph_by_type.get("tasks")
            api_graph_id = graph_by_type.get("api_endpoints")

            journey_view_id = ensure_view(conn, project_id, "journey")
            screen_kind_id = ensure_node_kind(conn, project_id, "screen")
            interaction_kind_id = ensure_node_kind(conn, project_id, "interaction")
            state_kind_id = ensure_node_kind(conn, project_id, "state")
            task_kind_id = ensure_node_kind(conn, project_id, "task")

            items = fetch_all(
                conn,
                "select id, view, item_type, title, item_metadata from items where project_id = %(pid)s and deleted_at is null",
                {"pid": project_id},
            )
            if not items:
                continue

            by_view_domain: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
            for item in items:
                domain = domain_from_id(item["id"], item["title"]) or "misc"
                by_view_domain[item["view"]][domain].append(item)

            # Journey primitives per domain
            for domain in sorted(
                set(by_view_domain.get("features", {}).keys()) | set(by_view_domain.get("ui_components", {}).keys()),
            ):
                meta_filter = json.dumps({"generated_by": GEN_TAG, "domain": domain})
                existing = fetch_all(
                    conn,
                    """
                    select id, item_type from items where project_id=%(pid)s and view='journey' and item_metadata @> %(meta)s::jsonb
                    """,
                    {"pid": project_id, "meta": meta_filter},
                )
                existing_by_type = {row["item_type"]: row["id"] for row in existing}

                screen_id = existing_by_type.get("screen")
                if not screen_id:
                    screen_id = f"journey_screen_{domain}_{uuid.uuid4().hex[:8]}"
                    conn.cursor().execute(
                        """
                        insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        """,
                        (
                            screen_id,
                            project_id,
                            f"{domain.title()} Screen",
                            None,
                            "journey",
                            "screen",
                            screen_kind_id,
                            "todo",
                            "medium",
                            None,
                            None,
                            json.dumps({"generated_by": GEN_TAG, "domain": domain}),
                            1,
                        ),
                    )
                    ensure_item_view(conn, screen_id, project_id, journey_view_id)

                interaction_id = existing_by_type.get("interaction")
                if not interaction_id:
                    interaction_id = f"journey_interaction_{domain}_{uuid.uuid4().hex[:8]}"
                    conn.cursor().execute(
                        """
                        insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        """,
                        (
                            interaction_id,
                            project_id,
                            f"{domain.title()} Interaction",
                            None,
                            "journey",
                            "interaction",
                            interaction_kind_id,
                            "todo",
                            "medium",
                            None,
                            screen_id,
                            json.dumps({"generated_by": GEN_TAG, "domain": domain}),
                            1,
                        ),
                    )
                    ensure_item_view(conn, interaction_id, project_id, journey_view_id)

                state_id = existing_by_type.get("state")
                if not state_id:
                    state_id = f"journey_state_{domain}_{uuid.uuid4().hex[:8]}"
                    conn.cursor().execute(
                        """
                        insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        """,
                        (
                            state_id,
                            project_id,
                            f"{domain.title()} State",
                            None,
                            "journey",
                            "state",
                            state_kind_id,
                            "todo",
                            "medium",
                            None,
                            interaction_id,
                            json.dumps({"generated_by": GEN_TAG, "domain": domain}),
                            1,
                        ),
                    )
                    ensure_item_view(conn, state_id, project_id, journey_view_id)

                if journey_graph_id:
                    ensure_graph_node(conn, journey_graph_id, screen_id, project_id)
                    ensure_graph_node(conn, journey_graph_id, interaction_id, project_id)
                    ensure_graph_node(conn, journey_graph_id, state_id, project_id)
                    insert_link(conn, project_id, journey_graph_id, screen_id, interaction_id, "related_to")
                    insert_link(conn, project_id, journey_graph_id, interaction_id, state_id, "related_to")

                ui_components = by_view_domain.get("ui_components", {}).get(domain, [])
                apis = by_view_domain.get("api_endpoints", {}).get(domain, [])
                for ui in ui_components:
                    insert_link(conn, project_id, journey_graph_id, ui["id"], interaction_id, "implements", True)
                    insert_link(conn, project_id, default_graph_id, ui["id"], interaction_id, "implements", True)
                    if mapping_graph_id:
                        insert_link(conn, project_id, mapping_graph_id, ui["id"], interaction_id, "implements", True)
                for api in apis:
                    insert_link(conn, project_id, journey_graph_id, interaction_id, api["id"], "depends_on", True)
                    insert_link(conn, project_id, default_graph_id, interaction_id, api["id"], "depends_on", True)
                    if mapping_graph_id:
                        insert_link(conn, project_id, mapping_graph_id, interaction_id, api["id"], "depends_on", True)

                # Per-screen interactions: one per UI component (granular)
                for ui in ui_components:
                    ui_meta = json.dumps({"generated_by": GEN_TAG, "ui_id": ui["id"]})
                    existing_ui_interaction = fetch_all(
                        conn,
                        """
                        select id from items
                        where project_id=%(pid)s
                          and view='journey'
                          and item_type='interaction'
                          and item_metadata @> %(meta)s::jsonb
                        """,
                        {"pid": project_id, "meta": ui_meta},
                    )
                    if existing_ui_interaction:
                        interaction_node_id = existing_ui_interaction[0]["id"]
                    else:
                        interaction_node_id = f"interaction_{ui['id']}_{uuid.uuid4().hex[:6]}"
                        conn.cursor().execute(
                            """
                            insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                            """,
                            (
                                interaction_node_id,
                                project_id,
                                f"Click {ui['title']}",
                                None,
                                "journey",
                                "interaction",
                                interaction_kind_id,
                                "todo",
                                "medium",
                                None,
                                screen_id,
                                json.dumps({"generated_by": GEN_TAG, "ui_id": ui["id"], "domain": domain}),
                                1,
                            ),
                        )
                        ensure_item_view(conn, interaction_node_id, project_id, journey_view_id)

                    insert_link(conn, project_id, journey_graph_id, ui["id"], interaction_node_id, "implements", True)
                    insert_link(conn, project_id, default_graph_id, ui["id"], interaction_node_id, "implements", True)
                    if mapping_graph_id:
                        insert_link(
                            conn,
                            project_id,
                            mapping_graph_id,
                            ui["id"],
                            interaction_node_id,
                            "implements",
                            True,
                        )

                    scored = []
                    for api in apis:
                        score = score_api_for_ui(ui["title"], api["title"])
                        scored.append((score, api))
                    scored.sort(key=operator.itemgetter(0), reverse=True)
                    candidates = [api for score, api in scored if score > 0] or apis[:1]
                    for api in candidates[:2]:
                        insert_link(
                            conn,
                            project_id,
                            journey_graph_id,
                            interaction_node_id,
                            api["id"],
                            "depends_on",
                            True,
                        )
                        insert_link(
                            conn,
                            project_id,
                            default_graph_id,
                            interaction_node_id,
                            api["id"],
                            "depends_on",
                            True,
                        )
                        if mapping_graph_id:
                            insert_link(
                                conn,
                                project_id,
                                mapping_graph_id,
                                interaction_node_id,
                                api["id"],
                                "depends_on",
                                True,
                            )

            # Feature WBS atomic tasks + state machines
            features = by_view_domain.get("features", {})
            for domain, feats in features.items():
                for feat in feats:
                    existing_tasks = fetch_all(
                        conn,
                        """
                        select id from items
                        where project_id=%(pid)s
                          and view='tasks'
                          and item_metadata->>'generated_by' = %(tag)s
                          and item_metadata->>'feature_id' = %(fid)s
                        """,
                        {"pid": project_id, "tag": GEN_TAG, "fid": feat["id"]},
                    )
                    if not existing_tasks:
                        task_specs = [
                            ("UI", "Design and implement UI"),
                            ("API", "Implement API and contracts"),
                            ("DB", "Add storage schema and migrations"),
                        ]
                        for suffix, desc in task_specs:
                            task_id = f"task_{domain}_{uuid.uuid4().hex[:8]}"
                            title = f"{feat['title']} - {suffix}"
                            meta = {"generated_by": GEN_TAG, "feature_id": feat["id"], "task_type": suffix}
                            conn.cursor().execute(
                                """
                                insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                                """,
                                (
                                    task_id,
                                    project_id,
                                    title,
                                    desc,
                                    "tasks",
                                    "task",
                                    task_kind_id,
                                    "todo",
                                    "medium",
                                    None,
                                    feat["id"],
                                    json.dumps(meta),
                                    1,
                                ),
                            )
                            tasks_view_id = ensure_view(conn, project_id, "tasks")
                            ensure_item_view(conn, task_id, project_id, tasks_view_id)
                            ensure_graph_node(conn, tasks_graph_id, task_id, project_id)
                            ensure_graph_node(conn, tasks_graph_id, feat["id"], project_id)
                            insert_link(conn, project_id, tasks_graph_id, task_id, feat["id"], "implements", True)
                            if mapping_graph_id:
                                insert_link(conn, project_id, mapping_graph_id, task_id, feat["id"], "implements", True)

                    state_meta = json.dumps({"generated_by": GEN_TAG, "feature_id": feat["id"]})
                    existing_states = fetch_all(
                        conn,
                        """
                        select id, title from items
                        where project_id=%(pid)s
                          and view='journey'
                          and item_type='state'
                          and item_metadata @> %(meta)s::jsonb
                        """,
                        {"pid": project_id, "meta": state_meta},
                    )
                    if not existing_states:
                        state_ids = {}
                        for state_name in ["Idle", "Loading", "Error"]:
                            state_id = f"state_{feat['id']}_{state_name.lower()}_{uuid.uuid4().hex[:6]}"
                            conn.cursor().execute(
                                """
                                insert into items (id, project_id, title, description, view, item_type, node_kind_id, status, priority, owner, parent_id, item_metadata, version)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                                """,
                                (
                                    state_id,
                                    project_id,
                                    f"{feat['title']} - {state_name}",
                                    None,
                                    "journey",
                                    "state",
                                    state_kind_id,
                                    "todo",
                                    "medium",
                                    None,
                                    None,
                                    json.dumps({
                                        "generated_by": GEN_TAG,
                                        "feature_id": feat["id"],
                                        "state": state_name.lower(),
                                    }),
                                    1,
                                ),
                            )
                            ensure_item_view(conn, state_id, project_id, journey_view_id)
                            state_ids[state_name.lower()] = state_id

                        idle_id = state_ids["idle"]
                        loading_id = state_ids["loading"]
                        error_id = state_ids["error"]
                        if journey_graph_id:
                            insert_link(conn, project_id, journey_graph_id, idle_id, loading_id, "related_to", True)
                            insert_link(conn, project_id, journey_graph_id, loading_id, error_id, "related_to", True)
                            insert_link(conn, project_id, journey_graph_id, loading_id, idle_id, "related_to", True)
                        if mapping_graph_id:
                            insert_link(conn, project_id, mapping_graph_id, feat["id"], idle_id, "implements", True)
                            insert_link(conn, project_id, mapping_graph_id, feat["id"], loading_id, "implements", True)
                            insert_link(conn, project_id, mapping_graph_id, feat["id"], error_id, "implements", True)

            if api_graph_id:
                for domain, apis in by_view_domain.get("api_endpoints", {}).items():
                    base_groups = defaultdict(list)
                    for api in apis:
                        base = base_path_from_api(api["title"]) or domain
                        base_groups[base].append(api)
                    for group in base_groups.values():
                        hub = group[0]
                        for api in group[1:]:
                            insert_link(conn, project_id, api_graph_id, api["id"], hub["id"], "related_to")

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
