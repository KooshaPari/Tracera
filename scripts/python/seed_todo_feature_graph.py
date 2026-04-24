#!/usr/bin/env python3
"""Seed a ToDo CRUD feature graph project with multi-view graphs."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from tracertm.models.external_link import ExternalLink
from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.item_view import ItemView
from tracertm.models.link import Link
from tracertm.models.link_type import LinkType
from tracertm.models.node_kind import NodeKind
from tracertm.models.project import Project
from tracertm.models.view import View

PROJECT_ID = "proj_todo_graph_001"
PROJECT_NAME = "ToDo CRUD Feature Graph"


def get_database_url() -> str:
    """Get database url."""
    return os.getenv("TRACERTM_DATABASE_URL") or os.getenv("DATABASE_URL") or "postgresql://localhost/tracertm"


def ensure_project(session: Session) -> Project:
    """Ensure project."""
    existing = session.execute(select(Project).where(Project.id == PROJECT_ID)).scalar_one_or_none()
    if existing:
        return existing
    project = Project(
        id=PROJECT_ID,
        name=PROJECT_NAME,
        description="Multi-view ToDo CRUD feature graph (user/tech/journey/mapping).",
        project_metadata={
            "domain": "Product Feature Graph",
            "schema_version": "2026-01",
            "example": True,
        },
    )
    session.add(project)
    session.flush()
    return project


def ensure_views(session: Session, project_id: str) -> dict[str, View]:
    """Ensure views."""
    views = {}
    for name, description in [
        ("user_requirements", "User-facing capabilities and expectations"),
        ("technical_requirements", "Implementation details and system design"),
        ("journey", "User journeys and flows"),
        ("mapping", "Cross-view mapping between nodes"),
        ("ui_components", "UI components and containment"),
        ("data_model", "Data model entities and relations"),
        ("qa", "Quality assurance and coverage"),
        ("infra", "Infra, observability, alerts"),
        ("security", "Authz, policies, roles"),
        ("performance", "Performance budgets and optimizations"),
        ("analytics", "Analytics events and dashboards"),
        ("compliance", "Compliance and retention rules"),
        ("localization", "Localization and i18n"),
        ("accessibility", "Accessibility checks"),
        ("ops", "Ops runbooks and incident hooks"),
    ]:
        view = session.execute(
            select(View).where(View.project_id == project_id, View.name == name),
        ).scalar_one_or_none()
        if not view:
            view = View(project_id=project_id, name=name, description=description, view_metadata={})
            session.add(view)
            session.flush()
        views[name] = view
    return views


def ensure_node_kinds(session: Session, project_id: str, kind_names: list[str]) -> dict[str, NodeKind]:
    """Ensure node kinds."""
    kinds: dict[str, NodeKind] = {}
    for name in kind_names:
        kind = session.execute(
            select(NodeKind).where(NodeKind.project_id == project_id, NodeKind.name == name),
        ).scalar_one_or_none()
        if not kind:
            kind = NodeKind(project_id=project_id, name=name, description=None, kind_metadata={})
            session.add(kind)
            session.flush()
        kinds[name] = kind
    return kinds


def ensure_link_types(session: Session, project_id: str, link_types: list[str]) -> None:
    """Ensure link types."""
    for name in link_types:
        existing = session.execute(
            select(LinkType).where(LinkType.project_id == project_id, LinkType.name == name),
        ).scalar_one_or_none()
        if not existing:
            session.add(LinkType(project_id=project_id, name=name, description=None, link_metadata={}))
    session.flush()


def ensure_graphs(session: Session, project_id: str) -> dict[str, Graph]:
    """Ensure graphs."""
    graphs: dict[str, Graph] = {}
    graph_specs = [
        ("user_requirements", "User Requirements Graph"),
        ("technical_requirements", "Technical Requirements Graph"),
        ("journey", "Journey: Create Task"),
        ("mapping", "Mapping Graph"),
        ("ui_components", "UI Component Graph"),
        ("data_model", "Data Model Graph"),
        ("qa", "QA Graph"),
        ("infra", "Infra Graph"),
        ("security", "Security Graph"),
        ("performance", "Performance Graph"),
        ("analytics", "Analytics Graph"),
        ("compliance", "Compliance Graph"),
        ("localization", "Localization Graph"),
        ("accessibility", "Accessibility Graph"),
        ("ops", "Ops Graph"),
    ]
    for graph_type, name in graph_specs:
        graph = session.execute(
            select(Graph).where(Graph.project_id == project_id, Graph.graph_type == graph_type, Graph.name == name),
        ).scalar_one_or_none()
        if not graph:
            graph = Graph(
                project_id=project_id,
                graph_type=graph_type,
                name=name,
                description=None,
                root_item_id=None,
                graph_metadata={},
            )
            session.add(graph)
            session.flush()
        graphs[graph_type] = graph
    return graphs


def seed_items(
    session: Session,
    project_id: str,
    views: dict[str, View],
    kinds: dict[str, NodeKind],
) -> dict[str, Item]:
    """Seed items."""
    items: dict[str, Item] = {}

    def add_item(
        item_id: str,
        title: str,
        view_name: str,
        kind: str,
        status: str = "planned",
        metadata: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        item = session.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
        if item:
            items[item_id] = item
            return
        item = Item(
            id=item_id,
            project_id=project_id,
            title=title,
            description=description,
            view=view_name,
            item_type=kind,
            node_kind_id=kinds[kind].id,
            status=status,
            priority="medium",
            owner=None,
            item_metadata=metadata or {},
        )
        session.add(item)
        session.flush()
        items[item_id] = item

        session.add(
            ItemView(
                item_id=item.id,
                view_id=views[view_name].id,
                project_id=project_id,
                is_primary=True,
            ),
        )

    # User requirements
    add_item(
        "U_CAP_TODO_CRUD",
        "Manage tasks (Create/Read/Update/Delete)",
        "user_requirements",
        "capability",
        metadata={"priority": "P0"},
    )
    add_item(
        "U_EXP_CREATE_TASK",
        "Create a new task",
        "user_requirements",
        "expectation",
        metadata={"user_language": "I can add a task and see it in my list."},
    )
    add_item(
        "U_EXP_VIEW_TASKS",
        "View task list",
        "user_requirements",
        "expectation",
        metadata={"user_language": "I can see all my tasks in a list."},
    )
    add_item(
        "U_EXP_UPDATE_TASK",
        "Update a task",
        "user_requirements",
        "expectation",
        metadata={"user_language": "I can edit a task title or status."},
    )
    add_item(
        "U_EXP_DELETE_TASK",
        "Delete a task",
        "user_requirements",
        "expectation",
        metadata={"user_language": "I can remove a task from my list."},
    )
    add_item(
        "U_ACC_CREATE_TASK",
        "New task appears in list",
        "user_requirements",
        "acceptance_check",
        metadata={"given": "Task list is open", "when": "User adds a task", "then": "Task appears"},
    )
    add_item(
        "U_ACC_UPDATE_TASK",
        "Edited task persists",
        "user_requirements",
        "acceptance_check",
        metadata={"given": "Task exists", "when": "User edits", "then": "Task shows updated fields"},
    )
    add_item(
        "U_ACC_DELETE_TASK",
        "Deleted task is removed",
        "user_requirements",
        "acceptance_check",
        metadata={"given": "Task exists", "when": "User deletes", "then": "Task no longer listed"},
    )

    # UI / Journey nodes
    add_item("UI_S_TASK_LIST", "Task List Screen", "journey", "screen", metadata={"route": "/tasks"})
    add_item("UI_C_NEW_TASK_INPUT", "New Task Input", "journey", "component", metadata={"type": "text"})
    add_item("UI_C_ADD_TASK_BUTTON", "Add Task Button", "journey", "component", metadata={"label": "Add"})
    add_item("UI_I_ADD_TASK_CLICK", "Click Add Task", "journey", "interaction", metadata={"trigger": "onClick"})
    add_item("UI_C_TASK_ROW", "Task Row", "journey", "component", metadata={"type": "row"})
    add_item("UI_I_EDIT_TASK", "Edit Task", "journey", "interaction", metadata={"trigger": "onBlur"})
    add_item("UI_I_DELETE_TASK", "Delete Task", "journey", "interaction", metadata={"trigger": "onClick"})
    add_item("J_CREATE_TASK", "Journey: Create Task", "journey", "journey", metadata={"intent": "Add a new task"})
    add_item("UI_C_TASK_TITLE_CELL", "Task Title Cell", "journey", "component", metadata={"type": "cell"})
    add_item("UI_C_TASK_STATUS_TOGGLE", "Task Status Toggle", "journey", "component", metadata={"type": "toggle"})
    add_item(
        "UI_C_TASK_DELETE_BUTTON",
        "Task Delete Button",
        "journey",
        "component",
        metadata={"type": "button", "label": "Delete"},
    )
    add_item("UI_I_TOGGLE_TASK", "Toggle Task Status", "journey", "interaction", metadata={"trigger": "onChange"})
    add_item(
        "UI_I_INLINE_EDIT_TITLE",
        "Inline Edit Task Title",
        "journey",
        "interaction",
        metadata={"trigger": "onBlur"},
    )
    add_item("UI_C_FILTER_STATUS", "Status Filter Dropdown", "journey", "component", metadata={"type": "select"})
    add_item("UI_I_FILTER_CHANGE", "Change Status Filter", "journey", "interaction", metadata={"trigger": "onChange"})

    # Technical requirements
    add_item("T_SVC_TASK", "task-service", "technical_requirements", "service", metadata={"protocol": "HTTP"})
    add_item("T_API_TASK_CREATE", "POST /api/tasks", "technical_requirements", "api_endpoint")
    add_item("T_API_TASK_LIST", "GET /api/tasks", "technical_requirements", "api_endpoint")
    add_item("T_API_TASK_UPDATE", "PATCH /api/tasks/:id", "technical_requirements", "api_endpoint")
    add_item("T_API_TASK_DELETE", "DELETE /api/tasks/:id", "technical_requirements", "api_endpoint")
    add_item("T_FN_CREATE_TASK", "CreateTaskHandler", "technical_requirements", "function")
    add_item("T_FN_UPDATE_TASK", "UpdateTaskHandler", "technical_requirements", "function")
    add_item("T_FN_DELETE_TASK", "DeleteTaskHandler", "technical_requirements", "function")
    add_item("T_FN_LIST_TASKS", "ListTasksHandler", "technical_requirements", "function")
    add_item("T_FN_VALIDATE_TASK", "ValidateTaskInput", "technical_requirements", "function")
    add_item("T_FN_BUILD_QUERY", "BuildTaskQuery", "technical_requirements", "function")
    add_item("T_FN_APPLY_FILTERS", "ApplyTaskFilters", "technical_requirements", "function")
    add_item("T_ENTITY_TASK", "Task", "technical_requirements", "data_entity")
    add_item("T_TABLE_TASKS", "tasks", "technical_requirements", "table")
    add_item("T_INDEX_TASKS_STATUS", "tasks(status) index", "technical_requirements", "index")
    add_item(
        "T_FIELD_TASK_ID",
        "tasks.id",
        "technical_requirements",
        "data_entity",
        metadata={"field": "id", "type": "uuid"},
    )
    add_item(
        "T_FIELD_TASK_TITLE",
        "tasks.title",
        "technical_requirements",
        "data_entity",
        metadata={"field": "title", "type": "text"},
    )
    add_item(
        "T_FIELD_TASK_STATUS",
        "tasks.status",
        "technical_requirements",
        "data_entity",
        metadata={"field": "status", "type": "text"},
    )
    add_item(
        "T_FIELD_TASK_CREATED",
        "tasks.created_at",
        "technical_requirements",
        "data_entity",
        metadata={"field": "created_at", "type": "timestamptz"},
    )
    add_item("T_EVENT_TASK_CREATED", "TaskCreated event", "technical_requirements", "event")
    add_item("T_EVENT_TASK_UPDATED", "TaskUpdated event", "technical_requirements", "event")
    add_item("T_EVENT_TASK_DELETED", "TaskDeleted event", "technical_requirements", "event")
    add_item("T_JOB_REINDEX_TASKS", "Reindex Tasks Job", "technical_requirements", "job")

    # Tests
    add_item("QA_TST_CREATE_TASK", "Create task API test", "technical_requirements", "test")
    add_item("QA_TST_UPDATE_TASK", "Update task API test", "technical_requirements", "test")
    add_item("QA_TST_DELETE_TASK", "Delete task API test", "technical_requirements", "test")
    add_item("QA_TST_LIST_TASKS", "List tasks API test", "technical_requirements", "test")
    add_item("QA_TST_FILTER_TASKS", "Filter tasks by status", "technical_requirements", "test")
    add_item("QA_TST_TOGGLE_TASK", "Toggle task status", "technical_requirements", "test")

    # UI component graph extras
    add_item("UI_C_TASK_LIST_CONTAINER", "Task List Container", "ui_components", "component")
    add_item("UI_C_TASK_ROW_ACTIONS", "Task Row Actions", "ui_components", "component")
    add_item("UI_C_TASK_EMPTY_STATE", "Empty State Panel", "ui_components", "component")
    add_item("UI_C_ERROR_BANNER", "Error Banner", "ui_components", "component")

    # Data model graph extras
    add_item("D_ENTITY_TASK", "Task Entity", "data_model", "data_entity")
    add_item("D_TABLE_TASKS", "tasks table", "data_model", "table")
    add_item("D_INDEX_TASKS_STATUS", "tasks(status) index", "data_model", "index")

    # QA graph extras
    add_item("QA_SUITE_TASKS", "Task CRUD Suite", "qa", "test")
    add_item("QA_TST_EMPTY_STATE", "Empty state UI test", "qa", "test")
    add_item("QA_TST_ERROR_BANNER", "Error banner UI test", "qa", "test")

    # Infra graph extras
    add_item("INF_METRIC_TASK_CREATE_RATE", "metric.tasks.create_rate", "infra", "metric")
    add_item("INF_ALERT_TASK_CREATE_SPIKE", "Alert: task create spike", "infra", "alert")
    add_item("INF_LOG_TASK_MUTATION", "Log: task mutation audit", "infra", "log")
    add_item("INF_DASH_TASKS", "Dashboard: task health", "infra", "dashboard")
    add_item("INF_SLI_TASK_CREATE_LAT", "SLI: task create latency", "infra", "sli")
    add_item("INF_SLO_TASK_CREATE_LAT", "SLO: task create latency p95", "infra", "slo")

    # Security graph extras
    add_item("SEC_POLICY_TASK_AUTHZ", "Policy: task authz", "security", "policy")
    add_item("SEC_ROLE_USER", "Role: user", "security", "role")
    add_item("SEC_PERMISSION_TASK_WRITE", "Permission: task.write", "security", "permission")
    add_item("SEC_FEATURE_FLAG_BULK", "Feature flag: bulk edit", "security", "feature_flag")

    # Performance graph extras
    add_item("PERF_BUDGET_TASK_LIST", "Budget: task list p95 < 150ms", "performance", "metric")
    add_item("PERF_QUERY_PLAN", "Task list query plan", "performance", "log")

    # Analytics graph extras
    add_item("AN_EVENT_TASK_CREATED", "Event: task_created", "analytics", "event")
    add_item("AN_METRIC_TASK_COMPLETED", "Metric: task_completed_count", "analytics", "metric")
    add_item("AN_DASH_PRODUCTIVITY", "Dashboard: productivity", "analytics", "dashboard")

    # Compliance graph extras
    add_item("COMP_POLICY_RETENTION", "Policy: task retention 365d", "compliance", "policy")

    # Localization graph extras
    add_item("LOC_STRING_EMPTY", "i18n.empty_state", "localization", "locale_string")
    add_item("LOC_STRING_ERROR", "i18n.error_banner", "localization", "locale_string")

    # Accessibility graph extras
    add_item("A11Y_CHECK_CONTRAST", "Check: contrast ratio", "accessibility", "a11y_check")
    add_item("A11Y_CHECK_KEYBOARD", "Check: keyboard navigation", "accessibility", "a11y_check")

    # Ops graph extras
    add_item("OPS_RUNBOOK_TASK_SPIKE", "Runbook: task spike", "ops", "runbook")

    session.flush()

    # Add mapping view memberships (non-primary)
    mapping_view_id = views["mapping"].id
    for item_id in items:
        session.merge(
            ItemView(
                item_id=item_id,
                view_id=mapping_view_id,
                project_id=project_id,
                is_primary=False,
            ),
        )

    return items


def seed_graph_nodes(session: Session, project_id: str, graphs: dict[str, Graph], items: dict[str, Item]) -> None:
    """Seed graph nodes."""
    graph_nodes: dict[str, list[str]] = {
        "user_requirements": [
            "U_CAP_TODO_CRUD",
            "U_EXP_CREATE_TASK",
            "U_EXP_VIEW_TASKS",
            "U_EXP_UPDATE_TASK",
            "U_EXP_DELETE_TASK",
            "U_ACC_CREATE_TASK",
            "U_ACC_UPDATE_TASK",
            "U_ACC_DELETE_TASK",
        ],
        "technical_requirements": [
            "T_SVC_TASK",
            "T_API_TASK_CREATE",
            "T_API_TASK_LIST",
            "T_API_TASK_UPDATE",
            "T_API_TASK_DELETE",
            "T_FN_CREATE_TASK",
            "T_FN_UPDATE_TASK",
            "T_FN_DELETE_TASK",
            "T_FN_LIST_TASKS",
            "T_FN_VALIDATE_TASK",
            "T_FN_BUILD_QUERY",
            "T_FN_APPLY_FILTERS",
            "T_ENTITY_TASK",
            "T_TABLE_TASKS",
            "T_INDEX_TASKS_STATUS",
            "T_FIELD_TASK_ID",
            "T_FIELD_TASK_TITLE",
            "T_FIELD_TASK_STATUS",
            "T_FIELD_TASK_CREATED",
            "T_EVENT_TASK_CREATED",
            "T_EVENT_TASK_UPDATED",
            "T_EVENT_TASK_DELETED",
            "T_JOB_REINDEX_TASKS",
            "QA_TST_CREATE_TASK",
            "QA_TST_UPDATE_TASK",
            "QA_TST_DELETE_TASK",
            "QA_TST_LIST_TASKS",
            "QA_TST_FILTER_TASKS",
            "QA_TST_TOGGLE_TASK",
        ],
        "journey": [
            "J_CREATE_TASK",
            "UI_S_TASK_LIST",
            "UI_C_NEW_TASK_INPUT",
            "UI_C_ADD_TASK_BUTTON",
            "UI_I_ADD_TASK_CLICK",
            "UI_C_TASK_ROW",
            "UI_I_EDIT_TASK",
            "UI_I_DELETE_TASK",
            "UI_C_TASK_TITLE_CELL",
            "UI_C_TASK_STATUS_TOGGLE",
            "UI_C_TASK_DELETE_BUTTON",
            "UI_I_TOGGLE_TASK",
            "UI_I_INLINE_EDIT_TITLE",
            "UI_C_FILTER_STATUS",
            "UI_I_FILTER_CHANGE",
            "T_API_TASK_CREATE",
            "T_API_TASK_LIST",
            "T_API_TASK_UPDATE",
            "T_API_TASK_DELETE",
        ],
        "ui_components": [
            "UI_S_TASK_LIST",
            "UI_C_TASK_LIST_CONTAINER",
            "UI_C_NEW_TASK_INPUT",
            "UI_C_ADD_TASK_BUTTON",
            "UI_C_TASK_ROW",
            "UI_C_TASK_TITLE_CELL",
            "UI_C_TASK_STATUS_TOGGLE",
            "UI_C_TASK_DELETE_BUTTON",
            "UI_C_TASK_ROW_ACTIONS",
            "UI_C_TASK_EMPTY_STATE",
            "UI_C_ERROR_BANNER",
            "UI_C_FILTER_STATUS",
        ],
        "data_model": [
            "D_ENTITY_TASK",
            "D_TABLE_TASKS",
            "D_INDEX_TASKS_STATUS",
            "T_FIELD_TASK_ID",
            "T_FIELD_TASK_TITLE",
            "T_FIELD_TASK_STATUS",
            "T_FIELD_TASK_CREATED",
        ],
        "qa": [
            "QA_SUITE_TASKS",
            "QA_TST_CREATE_TASK",
            "QA_TST_UPDATE_TASK",
            "QA_TST_DELETE_TASK",
            "QA_TST_LIST_TASKS",
            "QA_TST_FILTER_TASKS",
            "QA_TST_TOGGLE_TASK",
            "QA_TST_EMPTY_STATE",
            "QA_TST_ERROR_BANNER",
        ],
        "infra": [
            "INF_METRIC_TASK_CREATE_RATE",
            "INF_ALERT_TASK_CREATE_SPIKE",
            "INF_LOG_TASK_MUTATION",
            "INF_DASH_TASKS",
            "INF_SLI_TASK_CREATE_LAT",
            "INF_SLO_TASK_CREATE_LAT",
        ],
        "security": [
            "SEC_POLICY_TASK_AUTHZ",
            "SEC_ROLE_USER",
            "SEC_PERMISSION_TASK_WRITE",
            "SEC_FEATURE_FLAG_BULK",
        ],
        "performance": [
            "PERF_BUDGET_TASK_LIST",
            "PERF_QUERY_PLAN",
            "T_INDEX_TASKS_STATUS",
        ],
        "analytics": [
            "AN_EVENT_TASK_CREATED",
            "AN_METRIC_TASK_COMPLETED",
            "AN_DASH_PRODUCTIVITY",
            "T_EVENT_TASK_CREATED",
        ],
        "compliance": [
            "COMP_POLICY_RETENTION",
            "T_ENTITY_TASK",
            "T_TABLE_TASKS",
        ],
        "localization": [
            "LOC_STRING_EMPTY",
            "LOC_STRING_ERROR",
            "UI_C_TASK_EMPTY_STATE",
            "UI_C_ERROR_BANNER",
        ],
        "accessibility": [
            "A11Y_CHECK_CONTRAST",
            "A11Y_CHECK_KEYBOARD",
            "UI_C_TASK_LIST_CONTAINER",
            "UI_C_TASK_ROW",
        ],
        "ops": [
            "OPS_RUNBOOK_TASK_SPIKE",
            "INF_ALERT_TASK_CREATE_SPIKE",
            "INF_DASH_TASKS",
        ],
        "mapping": list(items.keys()),
    }

    for graph_type, node_ids in graph_nodes.items():
        graph = graphs[graph_type]
        for node_id in node_ids:
            session.merge(
                GraphNode(
                    graph_id=graph.id,
                    item_id=node_id,
                    project_id=project_id,
                    is_primary=False,
                ),
            )


def seed_links(session: Session, project_id: str, graphs: dict[str, Graph]) -> None:
    """Seed links."""

    def add_link(
        link_id: str,
        src: str,
        dst: str,
        link_type: str,
        graph_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        existing = session.execute(select(Link).where(Link.id == link_id)).scalar_one_or_none()
        if existing:
            return
        session.add(
            Link(
                id=link_id,
                project_id=project_id,
                graph_id=graphs[graph_type].id,
                source_item_id=src,
                target_item_id=dst,
                link_type=link_type,
                link_metadata=metadata or {},
            ),
        )

    # User graph
    add_link("L_U1", "U_CAP_TODO_CRUD", "U_EXP_CREATE_TASK", "decomposes", "user_requirements")
    add_link("L_U2", "U_CAP_TODO_CRUD", "U_EXP_VIEW_TASKS", "decomposes", "user_requirements")
    add_link("L_U3", "U_CAP_TODO_CRUD", "U_EXP_UPDATE_TASK", "decomposes", "user_requirements")
    add_link("L_U4", "U_CAP_TODO_CRUD", "U_EXP_DELETE_TASK", "decomposes", "user_requirements")
    add_link("L_U5", "U_EXP_CREATE_TASK", "U_ACC_CREATE_TASK", "verified_by", "user_requirements")
    add_link("L_U6", "U_EXP_UPDATE_TASK", "U_ACC_UPDATE_TASK", "verified_by", "user_requirements")
    add_link("L_U7", "U_EXP_DELETE_TASK", "U_ACC_DELETE_TASK", "verified_by", "user_requirements")

    # Technical graph
    add_link("L_T1", "T_SVC_TASK", "T_API_TASK_CREATE", "contains", "technical_requirements")
    add_link("L_T2", "T_SVC_TASK", "T_API_TASK_LIST", "contains", "technical_requirements")
    add_link("L_T3", "T_SVC_TASK", "T_API_TASK_UPDATE", "contains", "technical_requirements")
    add_link("L_T4", "T_SVC_TASK", "T_API_TASK_DELETE", "contains", "technical_requirements")
    add_link("L_T5", "T_API_TASK_CREATE", "T_FN_CREATE_TASK", "calls", "technical_requirements")
    add_link("L_T6", "T_API_TASK_UPDATE", "T_FN_UPDATE_TASK", "calls", "technical_requirements")
    add_link("L_T7", "T_API_TASK_DELETE", "T_FN_DELETE_TASK", "calls", "technical_requirements")
    add_link("L_T7A", "T_API_TASK_LIST", "T_FN_LIST_TASKS", "calls", "technical_requirements")
    add_link("L_T7B", "T_FN_CREATE_TASK", "T_FN_VALIDATE_TASK", "calls", "technical_requirements")
    add_link("L_T7C", "T_FN_UPDATE_TASK", "T_FN_VALIDATE_TASK", "calls", "technical_requirements")
    add_link("L_T7D", "T_FN_LIST_TASKS", "T_FN_BUILD_QUERY", "calls", "technical_requirements")
    add_link("L_T7E", "T_FN_BUILD_QUERY", "T_FN_APPLY_FILTERS", "calls", "technical_requirements")
    add_link("L_T8", "T_FN_CREATE_TASK", "T_TABLE_TASKS", "writes", "technical_requirements")
    add_link("L_T9", "T_API_TASK_LIST", "T_TABLE_TASKS", "reads", "technical_requirements")
    add_link("L_T10", "T_TABLE_TASKS", "T_INDEX_TASKS_STATUS", "uses", "technical_requirements")
    add_link("L_T10A", "T_TABLE_TASKS", "T_FIELD_TASK_ID", "contains", "technical_requirements")
    add_link("L_T10B", "T_TABLE_TASKS", "T_FIELD_TASK_TITLE", "contains", "technical_requirements")
    add_link("L_T10C", "T_TABLE_TASKS", "T_FIELD_TASK_STATUS", "contains", "technical_requirements")
    add_link("L_T10D", "T_TABLE_TASKS", "T_FIELD_TASK_CREATED", "contains", "technical_requirements")
    add_link("L_T10E", "T_FN_CREATE_TASK", "T_EVENT_TASK_CREATED", "publishes", "technical_requirements")
    add_link("L_T10F", "T_FN_UPDATE_TASK", "T_EVENT_TASK_UPDATED", "publishes", "technical_requirements")
    add_link("L_T10G", "T_FN_DELETE_TASK", "T_EVENT_TASK_DELETED", "publishes", "technical_requirements")
    add_link("L_T10H", "T_EVENT_TASK_CREATED", "T_JOB_REINDEX_TASKS", "triggers", "technical_requirements")
    add_link("L_T11", "QA_TST_CREATE_TASK", "T_API_TASK_CREATE", "tests", "technical_requirements")
    add_link("L_T12", "QA_TST_UPDATE_TASK", "T_API_TASK_UPDATE", "tests", "technical_requirements")
    add_link("L_T13", "QA_TST_DELETE_TASK", "T_API_TASK_DELETE", "tests", "technical_requirements")
    add_link("L_T14", "QA_TST_LIST_TASKS", "T_API_TASK_LIST", "tests", "technical_requirements")
    add_link("L_T15", "QA_TST_FILTER_TASKS", "T_API_TASK_LIST", "tests", "technical_requirements")
    add_link("L_T16", "QA_TST_TOGGLE_TASK", "T_API_TASK_UPDATE", "tests", "technical_requirements")

    # Journey graph
    add_link("L_J1", "J_CREATE_TASK", "UI_S_TASK_LIST", "includes_step", "journey")
    add_link("L_J2", "UI_S_TASK_LIST", "UI_C_NEW_TASK_INPUT", "contains", "journey")
    add_link("L_J3", "UI_S_TASK_LIST", "UI_C_ADD_TASK_BUTTON", "contains", "journey")
    add_link("L_J4", "UI_C_ADD_TASK_BUTTON", "UI_I_ADD_TASK_CLICK", "triggers", "journey")
    add_link("L_J5", "UI_I_ADD_TASK_CLICK", "T_API_TASK_CREATE", "calls", "journey")
    add_link("L_J6", "UI_S_TASK_LIST", "UI_C_TASK_ROW", "contains", "journey")
    add_link("L_J7", "UI_C_TASK_ROW", "UI_I_EDIT_TASK", "triggers", "journey")
    add_link("L_J8", "UI_C_TASK_ROW", "UI_I_DELETE_TASK", "triggers", "journey")
    add_link("L_J9", "UI_I_EDIT_TASK", "T_API_TASK_UPDATE", "calls", "journey")
    add_link("L_J10", "UI_I_DELETE_TASK", "T_API_TASK_DELETE", "calls", "journey")
    add_link("L_J11", "UI_C_TASK_ROW", "UI_C_TASK_TITLE_CELL", "contains", "journey")
    add_link("L_J12", "UI_C_TASK_ROW", "UI_C_TASK_STATUS_TOGGLE", "contains", "journey")
    add_link("L_J13", "UI_C_TASK_ROW", "UI_C_TASK_DELETE_BUTTON", "contains", "journey")
    add_link("L_J14", "UI_C_TASK_STATUS_TOGGLE", "UI_I_TOGGLE_TASK", "triggers", "journey")
    add_link("L_J15", "UI_I_TOGGLE_TASK", "T_API_TASK_UPDATE", "calls", "journey")
    add_link("L_J16", "UI_C_TASK_TITLE_CELL", "UI_I_INLINE_EDIT_TITLE", "triggers", "journey")
    add_link("L_J17", "UI_I_INLINE_EDIT_TITLE", "T_API_TASK_UPDATE", "calls", "journey")
    add_link("L_J18", "UI_S_TASK_LIST", "UI_C_FILTER_STATUS", "contains", "journey")
    add_link("L_J19", "UI_C_FILTER_STATUS", "UI_I_FILTER_CHANGE", "triggers", "journey")
    add_link("L_J20", "UI_I_FILTER_CHANGE", "T_API_TASK_LIST", "calls", "journey")

    # Mapping graph (cross-view glue)
    add_link("L_M1", "U_EXP_CREATE_TASK", "UI_I_ADD_TASK_CLICK", "represented_by", "mapping")
    add_link("L_M2", "U_EXP_CREATE_TASK", "T_API_TASK_CREATE", "realized_by", "mapping")
    add_link("L_M3", "U_ACC_CREATE_TASK", "QA_TST_CREATE_TASK", "verified_by", "mapping")
    add_link("L_M4", "U_EXP_UPDATE_TASK", "T_API_TASK_UPDATE", "realized_by", "mapping")
    add_link("L_M5", "U_ACC_UPDATE_TASK", "QA_TST_UPDATE_TASK", "verified_by", "mapping")
    add_link("L_M6", "U_EXP_DELETE_TASK", "T_API_TASK_DELETE", "realized_by", "mapping")
    add_link("L_M7", "U_ACC_DELETE_TASK", "QA_TST_DELETE_TASK", "verified_by", "mapping")
    add_link("L_M8", "U_EXP_VIEW_TASKS", "T_API_TASK_LIST", "realized_by", "mapping")
    add_link("L_M9", "U_EXP_VIEW_TASKS", "UI_S_TASK_LIST", "represented_by", "mapping")
    add_link("L_M10", "U_ACC_CREATE_TASK", "UI_C_TASK_ROW", "represented_by", "mapping")
    add_link("L_M11", "U_ACC_UPDATE_TASK", "UI_I_INLINE_EDIT_TITLE", "represented_by", "mapping")
    add_link("L_M12", "U_ACC_UPDATE_TASK", "QA_TST_TOGGLE_TASK", "verified_by", "mapping")
    add_link("L_M13", "U_EXP_VIEW_TASKS", "QA_TST_LIST_TASKS", "verified_by", "mapping")
    add_link("L_M14", "U_EXP_VIEW_TASKS", "QA_TST_FILTER_TASKS", "verified_by", "mapping")

    # UI component graph links
    add_link("L_UI1", "UI_S_TASK_LIST", "UI_C_TASK_LIST_CONTAINER", "contains", "ui_components")
    add_link("L_UI2", "UI_C_TASK_LIST_CONTAINER", "UI_C_NEW_TASK_INPUT", "contains", "ui_components")
    add_link("L_UI3", "UI_C_TASK_LIST_CONTAINER", "UI_C_ADD_TASK_BUTTON", "contains", "ui_components")
    add_link("L_UI4", "UI_C_TASK_LIST_CONTAINER", "UI_C_TASK_ROW", "contains", "ui_components")
    add_link("L_UI5", "UI_C_TASK_ROW", "UI_C_TASK_TITLE_CELL", "contains", "ui_components")
    add_link("L_UI6", "UI_C_TASK_ROW", "UI_C_TASK_STATUS_TOGGLE", "contains", "ui_components")
    add_link("L_UI7", "UI_C_TASK_ROW", "UI_C_TASK_ROW_ACTIONS", "contains", "ui_components")
    add_link("L_UI8", "UI_C_TASK_ROW_ACTIONS", "UI_C_TASK_DELETE_BUTTON", "contains", "ui_components")
    add_link("L_UI9", "UI_S_TASK_LIST", "UI_C_TASK_EMPTY_STATE", "contains", "ui_components")
    add_link("L_UI10", "UI_S_TASK_LIST", "UI_C_ERROR_BANNER", "contains", "ui_components")
    add_link("L_UI11", "UI_S_TASK_LIST", "UI_C_FILTER_STATUS", "contains", "ui_components")

    # Data model graph links
    add_link("L_D1", "D_ENTITY_TASK", "D_TABLE_TASKS", "realized_by", "data_model")
    add_link("L_D2", "D_TABLE_TASKS", "D_INDEX_TASKS_STATUS", "uses", "data_model")
    add_link("L_D3", "D_TABLE_TASKS", "T_FIELD_TASK_ID", "contains", "data_model")
    add_link("L_D4", "D_TABLE_TASKS", "T_FIELD_TASK_TITLE", "contains", "data_model")
    add_link("L_D5", "D_TABLE_TASKS", "T_FIELD_TASK_STATUS", "contains", "data_model")
    add_link("L_D6", "D_TABLE_TASKS", "T_FIELD_TASK_CREATED", "contains", "data_model")

    # QA graph links
    add_link("L_Q1", "QA_SUITE_TASKS", "QA_TST_CREATE_TASK", "contains", "qa")
    add_link("L_Q2", "QA_SUITE_TASKS", "QA_TST_UPDATE_TASK", "contains", "qa")
    add_link("L_Q3", "QA_SUITE_TASKS", "QA_TST_DELETE_TASK", "contains", "qa")
    add_link("L_Q4", "QA_SUITE_TASKS", "QA_TST_LIST_TASKS", "contains", "qa")
    add_link("L_Q5", "QA_SUITE_TASKS", "QA_TST_FILTER_TASKS", "contains", "qa")
    add_link("L_Q6", "QA_SUITE_TASKS", "QA_TST_TOGGLE_TASK", "contains", "qa")
    add_link("L_Q7", "QA_SUITE_TASKS", "QA_TST_EMPTY_STATE", "contains", "qa")
    add_link("L_Q8", "QA_SUITE_TASKS", "QA_TST_ERROR_BANNER", "contains", "qa")

    # Infra graph links
    add_link("L_INF1", "T_API_TASK_CREATE", "INF_METRIC_TASK_CREATE_RATE", "instrumented_by", "infra")
    add_link("L_INF2", "INF_METRIC_TASK_CREATE_RATE", "INF_ALERT_TASK_CREATE_SPIKE", "alerts_on", "infra")
    add_link("L_INF3", "T_API_TASK_UPDATE", "INF_LOG_TASK_MUTATION", "logs", "infra")
    add_link("L_INF4", "INF_METRIC_TASK_CREATE_RATE", "INF_DASH_TASKS", "monitored_by", "infra")
    add_link("L_INF5", "INF_SLI_TASK_CREATE_LAT", "INF_SLO_TASK_CREATE_LAT", "conforms_to", "infra")

    # Security graph links
    add_link("L_SEC1", "SEC_POLICY_TASK_AUTHZ", "SEC_ROLE_USER", "contains", "security")
    add_link("L_SEC2", "SEC_ROLE_USER", "SEC_PERMISSION_TASK_WRITE", "contains", "security")
    add_link("L_SEC3", "T_API_TASK_CREATE", "SEC_POLICY_TASK_AUTHZ", "authz_checks", "security")
    add_link("L_SEC4", "SEC_FEATURE_FLAG_BULK", "T_API_TASK_UPDATE", "guarded_by", "security")

    # Performance graph links
    add_link("L_PERF1", "T_API_TASK_LIST", "PERF_BUDGET_TASK_LIST", "instrumented_by", "performance")
    add_link("L_PERF2", "T_API_TASK_LIST", "PERF_QUERY_PLAN", "logs", "performance")

    # Analytics graph links
    add_link("L_AN1", "T_EVENT_TASK_CREATED", "AN_EVENT_TASK_CREATED", "emits", "analytics")
    add_link("L_AN2", "AN_EVENT_TASK_CREATED", "AN_METRIC_TASK_COMPLETED", "instrumented_by", "analytics")
    add_link("L_AN3", "AN_METRIC_TASK_COMPLETED", "AN_DASH_PRODUCTIVITY", "monitored_by", "analytics")

    # Compliance graph links
    add_link("L_COMP1", "COMP_POLICY_RETENTION", "D_TABLE_TASKS", "conforms_to", "compliance")

    # Localization graph links
    add_link("L_LOC1", "UI_C_TASK_EMPTY_STATE", "LOC_STRING_EMPTY", "localizes", "localization")
    add_link("L_LOC2", "UI_C_ERROR_BANNER", "LOC_STRING_ERROR", "localizes", "localization")

    # Accessibility graph links
    add_link("L_A11Y1", "UI_C_TASK_LIST_CONTAINER", "A11Y_CHECK_KEYBOARD", "a11y_validated_by", "accessibility")
    add_link("L_A11Y2", "UI_C_TASK_LIST_CONTAINER", "A11Y_CHECK_CONTRAST", "a11y_validated_by", "accessibility")

    # Ops graph links
    add_link("L_OPS1", "INF_ALERT_TASK_CREATE_SPIKE", "OPS_RUNBOOK_TASK_SPIKE", "triggers", "ops")


def seed_external_links(session: Session, project_id: str) -> None:
    """Seed external links."""
    existing = session.execute(select(ExternalLink).where(ExternalLink.project_id == project_id)).scalar_one_or_none()
    if existing:
        return
    session.add(
        ExternalLink(
            project_id=project_id,
            item_id="UI_S_TASK_LIST",
            provider="figma",
            target="figma://FILE_TODO?nodeId=1",
            label="Task List Wireframe",
            link_metadata={},
        ),
    )


def main() -> None:
    """Main."""
    database_url = get_database_url()
    engine = create_engine(database_url)

    with Session(engine) as session:
        project = ensure_project(session)
        project_id = str(project.id)
        views = ensure_views(session, project_id)
        kinds = ensure_node_kinds(
            session,
            project_id,
            [
                "capability",
                "expectation",
                "acceptance_check",
                "variant",
                "screen",
                "component",
                "interaction",
                "journey",
                "service",
                "function",
                "api_endpoint",
                "data_entity",
                "table",
                "index",
                "test",
                "event",
                "job",
                "metric",
                "alert",
                "log",
                "dashboard",
                "policy",
                "role",
                "permission",
                "feature_flag",
                "sli",
                "slo",
                "locale_string",
                "a11y_check",
                "runbook",
            ],
        )
        ensure_link_types(
            session,
            project_id,
            [
                "decomposes",
                "verified_by",
                "contains",
                "calls",
                "reads",
                "writes",
                "uses",
                "tests",
                "includes_step",
                "triggers",
                "represented_by",
                "realized_by",
                "instrumented_by",
                "guarded_by",
                "authz_checks",
                "emits",
                "logs",
                "alerts_on",
                "monitored_by",
                "localizes",
                "a11y_validated_by",
                "conforms_to",
            ],
        )
        graphs = ensure_graphs(session, project_id)
        items = seed_items(session, project_id, views, kinds)
        seed_graph_nodes(session, project_id, graphs, items)
        seed_links(session, project_id, graphs)
        seed_external_links(session, project_id)
        session.commit()


if __name__ == "__main__":
    main()
