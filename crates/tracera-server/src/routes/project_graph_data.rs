//! Shared projection of one canonical project's persisted items and trace links.
//!
//! The scoped graph and matrix endpoints are views over the same rows: items are
//! canonical persisted items, links are persisted artifact trace links whose two
//! endpoints both belong to the requested project. Nothing is synthesized when a
//! project has no persisted graph data, and an unregistered project is a 404.
use crate::{
    item::{Item, ItemFilter},
    store::{ProjectSummary, TraceLink},
    AppState,
};
use axum::{http::StatusCode, Json};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet},
    future::Future,
    time::Duration,
};

pub(super) const MAX_GRAPH_ITEMS: i64 = 1000;

type Failure = (StatusCode, Json<Value>);

fn error(status: StatusCode, code: &str) -> Failure {
    (status, Json(json!({"error":code})))
}

async fn bounded<T>(
    future: impl Future<Output = Result<T, crate::store::StoreError>>,
) -> Result<T, Failure> {
    tokio::time::timeout(Duration::from_secs(2), future)
        .await
        .map_err(|_| {
            error(
                StatusCode::SERVICE_UNAVAILABLE,
                "project_graph_query_over_budget",
            )
        })?
        .map_err(|_| {
            error(
                StatusCode::INTERNAL_SERVER_ERROR,
                "project_graph_store_error",
            )
        })
}

pub(super) struct ProjectGraph {
    pub(super) project: ProjectSummary,
    pub(super) items: Vec<Item>,
    pub(super) links: Vec<TraceLink>,
}

/// Load one project's complete bounded graph view from canonical storage.
pub(super) async fn load(project_id: &str, state: &AppState) -> Result<ProjectGraph, Failure> {
    let project = bounded(state.store.get_project(project_id.to_owned()))
        .await?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "project_not_found"))?;

    let page = bounded(state.store.list_items(
        ItemFilter {
            project_id: Some(project_id.to_owned()),
            ..Default::default()
        },
        MAX_GRAPH_ITEMS + 1,
        0,
    ))
    .await?;
    if page.total > MAX_GRAPH_ITEMS || page.items.len() as i64 != page.total {
        return Err(error(
            StatusCode::SERVICE_UNAVAILABLE,
            "project_graph_too_large",
        ));
    }

    let ids: BTreeSet<&str> = page.items.iter().map(|item| item.id.as_str()).collect();
    let mut links = BTreeMap::new();
    for id in &ids {
        for link in bounded(state.store.list_trace_links_for_artifact((*id).to_owned())).await? {
            if ids.contains(link.source_id.as_str()) && ids.contains(link.target_id.as_str()) {
                links.entry(link.id.clone()).or_insert(link);
            }
        }
    }

    Ok(ProjectGraph {
        project,
        items: page.items,
        links: links.into_values().collect(),
    })
}

pub(super) fn graph_summary(graph: &ProjectGraph) -> Value {
    json!({
        "id": graph.project.id,
        "name": graph.project.name,
        "graphType": "traceability",
        "description": "Canonical persisted items and trace links",
        "rootItemId": Value::Null,
        "graphRules": {},
        "metadata": {"projectId": graph.project.id},
    })
}

pub(super) fn item_json(item: &Item) -> Value {
    serde_json::to_value(item).unwrap_or_else(|_| json!({"id":item.id}))
}

pub(super) fn link_json(link: &TraceLink, project_id: &str) -> Value {
    json!({
        "id": link.id,
        "projectId": project_id,
        "sourceId": link.source_id,
        "targetId": link.target_id,
        "type": link.relationship,
        "metadata": {"confidence":link.confidence, "source":link.source},
        "createdAt": link.created_at,
        "updatedAt": link.updated_at,
        "version": 1,
    })
}

fn is_requirement(item: &Item) -> bool {
    item.item_type.eq_ignore_ascii_case("requirement")
        || item.view.eq_ignore_ascii_case("requirement")
}

/// Matrix payload matches the frontend `TraceabilityMatrix` contract exactly.
pub(super) fn matrix_json(graph: &ProjectGraph) -> Value {
    let requirement_ids: BTreeSet<&str> = graph
        .items
        .iter()
        .filter(|item| is_requirement(item))
        .map(|item| item.id.as_str())
        .collect();
    let linked: BTreeSet<&str> = graph
        .links
        .iter()
        .filter(|link| requirement_ids.contains(link.source_id.as_str()))
        .map(|link| link.source_id.as_str())
        .collect();
    let total = requirement_ids.len();
    let traced = linked.len();
    let percentage = if total == 0 {
        0.0
    } else {
        ((traced as f64 * 10_000.0) / total as f64).round() / 100.0
    };

    json!({
        "coverage": {
            "percentage": percentage,
            "total": total,
            "traced": traced,
            "untraced": total.saturating_sub(traced),
        },
        "items": graph.items.iter().map(item_json).collect::<Vec<_>>(),
        "links": graph.links.iter().map(|link| link_json(link, &graph.project.id)).collect::<Vec<_>>(),
    })
}

/// The graph projection uses the same item and link rows as the matrix.
pub(super) fn projection_json(graph: &ProjectGraph) -> Value {
    json!({
        "graph": graph_summary(graph),
        "nodes": graph.items.iter().map(item_json).collect::<Vec<_>>(),
        "links": graph.links.iter().map(|link| link_json(link, &graph.project.id)).collect::<Vec<_>>(),
    })
}

/// Viewport projection: all persisted rows are returned as one honest region
/// because canonical storage does not carry node coordinates or region cursors.
pub(super) fn viewport_json(graph: &ProjectGraph) -> Value {
    let nodes = graph
        .items
        .iter()
        .enumerate()
        .map(|(index, item)| {
            json!({
                "id": item.id,
                "position": {"x": ((index % 10) * 240) as f64, "y": ((index / 10) * 160) as f64},
                "data": item_json(item),
            })
        })
        .collect::<Vec<_>>();
    let edges = graph
        .links
        .iter()
        .map(|link| {
            json!({
                "id": link.id,
                "source": link.source_id,
                "target": link.target_id,
                "type": "default",
                "data": link_json(link, &graph.project.id),
            })
        })
        .collect::<Vec<_>>();

    json!({
        "graph": graph_summary(graph),
        "nodes": nodes,
        "edges": edges,
        "links": graph.links.iter().map(|link| link_json(link, &graph.project.id)).collect::<Vec<_>>(),
        "hasMore": {"north":false, "south":false, "east":false, "west":false},
        "totalCount": graph.items.len(),
        "metadata": {
            "regionKey": format!("project:{}", graph.project.id),
            "totalNodesInRegion": graph.items.len(),
            "totalEdgesInRegion": graph.links.len(),
        },
    })
}

pub(super) fn csv_export(graph: &ProjectGraph) -> Vec<u8> {
    let mut out = String::from("id,projectId,sourceId,targetId,type,confidence,source\n");
    for link in &graph.links {
        out.push_str(&csv_cell(&link.id));
        out.push(',');
        out.push_str(&csv_cell(&graph.project.id));
        out.push(',');
        out.push_str(&csv_cell(&link.source_id));
        out.push(',');
        out.push_str(&csv_cell(&link.target_id));
        out.push(',');
        out.push_str(&csv_cell(&link.relationship));
        out.push(',');
        out.push_str(&csv_cell(&link.confidence.to_string()));
        out.push(',');
        out.push_str(&csv_cell(&link.source));
        out.push('\n');
    }
    out.into_bytes()
}

fn csv_cell(value: &str) -> String {
    if value.contains([',', '"', '\n', '\r']) {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_owned()
    }
}
