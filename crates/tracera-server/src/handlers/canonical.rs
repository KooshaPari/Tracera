use crate::{
    store::{CanonicalExport, CanonicalItem},
    AppState,
};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeSet, HashMap, HashSet, VecDeque};

type ApiError = (StatusCode, Json<Value>);
fn error(code: StatusCode, message: &'static str) -> ApiError {
    (code, Json(json!({"error":message})))
}
fn db_error(e: impl std::fmt::Display) -> ApiError {
    tracing::error!("canonical graph store error: {e}");
    error(
        StatusCode::INTERNAL_SERVER_ERROR,
        "canonical graph store failure",
    )
}

fn validate(export: &CanonicalExport) -> Result<(), ApiError> {
    if export.project.id.trim().is_empty()
        || export.project.name.trim().is_empty()
        || export.project.id.len() > 256
        || export.project.name.len() > 1024
    {
        return Err(error(StatusCode::BAD_REQUEST, "invalid project identity"));
    }
    let mut ids = HashSet::new();
    for item in &export.items {
        if item.id.trim().is_empty()
            || item.title.trim().is_empty()
            || item.view.trim().is_empty()
            || item.item_type.trim().is_empty()
            || item.status.trim().is_empty()
            || item.id.len() > 256
            || !ids.insert(item.id.as_str())
        {
            return Err(error(StatusCode::BAD_REQUEST, "invalid or duplicate item"));
        }
    }
    let mut links = HashSet::new();
    let mut unresolved = BTreeSet::new();
    for link in &export.links {
        if link.link_type.trim().is_empty()
            || link.link_type.len() > 256
            || !links.insert((&link.source_id, &link.target_id, &link.link_type))
        {
            return Err(error(StatusCode::BAD_REQUEST, "invalid or duplicate link"));
        }
        if !ids.contains(link.source_id.as_str()) {
            unresolved.insert(link.source_id.as_str());
        }
        if !ids.contains(link.target_id.as_str()) {
            unresolved.insert(link.target_id.as_str());
        }
    }
    if !unresolved.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(json!({
                "error": "dangling link endpoints",
                "unresolved_ids": unresolved,
            })),
        ));
    }
    Ok(())
}

#[derive(Serialize)]
pub(crate) struct ImportResult {
    project_id: String,
    items_imported: usize,
    links_imported: usize,
}
pub(crate) async fn import(
    State(state): State<AppState>,
    Json(export): Json<CanonicalExport>,
) -> Result<(StatusCode, Json<ImportResult>), ApiError> {
    validate(&export)?;
    if state
        .store
        .canonical_project(export.project.id.clone())
        .await
        .map_err(db_error)?
        .is_some()
        || state
            .store
            .get_project(export.project.id.clone())
            .await
            .map_err(db_error)?
            .is_some()
    {
        return Err(error(StatusCode::CONFLICT, "project already exists"));
    }
    let response = ImportResult {
        project_id: export.project.id.clone(),
        items_imported: export.items.len(),
        links_imported: export.links.len(),
    };
    state.store.import_canonical(export).await.map_err(|e| {
        tracing::warn!("canonical import rejected: {e}");
        error(StatusCode::CONFLICT, "canonical import conflict")
    })?;
    Ok((StatusCode::CREATED, Json(response)))
}

#[derive(Deserialize)]
pub(crate) struct PageQuery {
    project_id: Option<String>,
    limit: Option<i64>,
    skip: Option<i64>,
}
fn page(query: &PageQuery) -> Result<(String, i64, i64), ApiError> {
    let project_id = query
        .project_id
        .as_ref()
        .filter(|s| !s.trim().is_empty())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "project_id required"))?;
    let limit = query.limit.unwrap_or(50);
    let skip = query.skip.unwrap_or(0);
    if !(1..=500).contains(&limit) || skip < 0 {
        return Err(error(StatusCode::BAD_REQUEST, "invalid pagination"));
    }
    Ok((project_id.clone(), limit, skip))
}
async fn require_project(state: &AppState, id: &str) -> Result<(), ApiError> {
    if state
        .store
        .canonical_project(id.to_owned())
        .await
        .map_err(db_error)?
        .is_none()
    {
        return Err(error(StatusCode::NOT_FOUND, "project not found"));
    }
    Ok(())
}

pub(crate) async fn list_items(
    State(state): State<AppState>,
    Query(query): Query<PageQuery>,
) -> Result<Json<Value>, ApiError> {
    let (id, limit, skip) = page(&query)?;
    require_project(&state, &id).await?;
    let (items, total) = state
        .store
        .canonical_items(id, limit, skip)
        .await
        .map_err(db_error)?;
    Ok(Json(json!({"items": items, "total": total})))
}

#[derive(Deserialize)]
pub(crate) struct ItemQuery {
    project_id: Option<String>,
}
pub(crate) async fn get_item(
    State(state): State<AppState>,
    Path(item_id): Path<String>,
    Query(query): Query<ItemQuery>,
) -> Result<Json<Value>, ApiError> {
    let project_id = query
        .project_id
        .filter(|id| !id.trim().is_empty())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "project_id required"))?;
    let project = state
        .store
        .canonical_project(project_id.clone())
        .await
        .map_err(db_error)?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "project not found"))?;
    let item = state
        .store
        .canonical_item(project_id.clone(), item_id)
        .await
        .map_err(db_error)?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "item not found"))?;
    // Canonical export carries no item timestamps. The persisted project's
    // import timestamp is the baseline available to the legacy detail view.
    Ok(Json(json!({
        "id": item.id,
        "project_id": project_id,
        "title": item.title,
        "view": item.view,
        "type": item.item_type,
        "status": item.status,
        "description": item.description,
        "version": item.version,
        "source_url": item.source_url,
        "source_repo": item.source_repo,
        "source_kind": item.source_kind,
        "created_at": project.created_at,
        "updated_at": project.created_at,
    })))
}
pub(crate) async fn list_links(
    State(state): State<AppState>,
    Query(query): Query<PageQuery>,
) -> Result<Json<Value>, ApiError> {
    let (id, limit, skip) = page(&query)?;
    require_project(&state, &id).await?;
    let (links, total) = state
        .store
        .canonical_links(id, limit, skip)
        .await
        .map_err(db_error)?;
    Ok(Json(json!({"links": links, "total": total})))
}

#[derive(Deserialize)]
pub(crate) struct ExportQuery {
    format: Option<String>,
}
pub(crate) async fn export(
    State(state): State<AppState>,
    Path(project_id): Path<String>,
    Query(query): Query<ExportQuery>,
) -> Result<Json<CanonicalExport>, ApiError> {
    if query.format.as_deref() != Some("full") {
        return Err(error(StatusCode::BAD_REQUEST, "format=full required"));
    }
    state
        .store
        .canonical_export(project_id)
        .await
        .map_err(db_error)?
        .map(Json)
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "project not found"))
}

#[derive(Deserialize)]
pub(crate) struct TraverseQuery {
    project_id: Option<String>,
    direction: Option<String>,
    depth: Option<u32>,
}
pub(crate) async fn traverse(
    State(state): State<AppState>,
    Path(root): Path<String>,
    Query(query): Query<TraverseQuery>,
) -> Result<Json<Value>, ApiError> {
    let project_id = query
        .project_id
        .filter(|s| !s.trim().is_empty())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "project_id required"))?;
    let direction = query.direction.unwrap_or_else(|| "both".to_owned());
    if !matches!(direction.as_str(), "up" | "down" | "both") {
        return Err(error(StatusCode::BAD_REQUEST, "invalid direction"));
    }
    let depth = query.depth.unwrap_or(3);
    if depth > 32 {
        return Err(error(StatusCode::BAD_REQUEST, "depth exceeds 32"));
    }
    let export = state
        .store
        .canonical_export(project_id)
        .await
        .map_err(db_error)?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "project not found"))?;
    let by_id: HashMap<&str, &CanonicalItem> = export
        .items
        .iter()
        .map(|item| (item.id.as_str(), item))
        .collect();
    if !by_id.contains_key(root.as_str()) {
        return Err(error(StatusCode::NOT_FOUND, "item not found"));
    }
    let mut seen = BTreeSet::new();
    let mut frontier = VecDeque::from([(root.clone(), 0u32)]);
    seen.insert(root);
    while let Some((current, distance)) = frontier.pop_front() {
        if distance >= depth {
            continue;
        }
        for link in &export.links {
            let next = match direction.as_str() {
                "down" if link.source_id == current => Some(&link.target_id),
                "up" if link.target_id == current => Some(&link.source_id),
                "both" if link.source_id == current => Some(&link.target_id),
                "both" if link.target_id == current => Some(&link.source_id),
                _ => None,
            };
            if let Some(next) = next {
                if seen.insert(next.clone()) {
                    frontier.push_back((next.clone(), distance + 1));
                }
            }
        }
    }
    let nodes: Vec<Value> = seen.iter().filter_map(|id| by_id.get(id.as_str())).map(|item| json!({
        "id": item.id, "title": item.title, "type": item.item_type, "view": item.view, "status": item.status,
    })).collect();
    let edges: Vec<Value> = export
        .links
        .iter()
        .filter(|link| seen.contains(&link.source_id) && seen.contains(&link.target_id))
        .map(|link| {
            json!({"id": format!("{}:{}:{}",link.source_id,link.target_id,link.link_type),
            "source":link.source_id,"target":link.target_id,"type":link.link_type})
        })
        .collect();
    Ok(Json(json!({"nodes":nodes,"edges":edges})))
}
