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
        .canonical_links(id.clone(), limit, skip)
        .await
        .map_err(db_error)?;
    let links: Vec<Value> = links.iter().map(|link| link_value(&id, link)).collect();
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

fn scoped(query: ItemQuery) -> Result<String, ApiError> {
    query
        .project_id
        .filter(|id| !id.trim().is_empty() && id.len() <= 256)
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "project_id required"))
}
async fn edit(
    state: &AppState,
    project_id: &str,
    mutation: crate::store::CanonicalMutation,
) -> Result<(), ApiError> {
    require_project(state, project_id).await?;
    match state
        .store
        .mutate_canonical(project_id.to_owned(), mutation)
        .await
    {
        Ok(true) => Ok(()),
        Ok(false) => Err(error(StatusCode::NOT_FOUND, "item or link not found")),
        Err(e) => {
            tracing::warn!("canonical edit rejected: {e}");
            Err(error(StatusCode::CONFLICT, "canonical edit conflict"))
        }
    }
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct CreateItem {
    project_id: String,
    #[serde(default)]
    id: Option<String>,
    title: String,
    view: String,
    #[serde(rename = "type")]
    item_type: String,
    status: String,
    #[serde(default)]
    description: Option<String>,
}
pub(crate) async fn create_item(
    State(state): State<AppState>,
    Json(body): Json<CreateItem>,
) -> Result<(StatusCode, Json<Value>), ApiError> {
    let project_id = scoped(ItemQuery {
        project_id: Some(body.project_id),
    })?;
    let item = CanonicalItem {
        id: body.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string()),
        title: body.title,
        view: body.view,
        item_type: body.item_type,
        status: body.status,
        description: body.description,
        version: None,
        source_url: None,
        source_repo: None,
        source_kind: None,
    };
    if [
        &item.id,
        &item.title,
        &item.view,
        &item.item_type,
        &item.status,
    ]
    .iter()
    .any(|s| s.trim().is_empty())
        || item.id.len() > 256
    {
        return Err(error(StatusCode::BAD_REQUEST, "invalid item"));
    }
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::CreateItem(item.clone()),
    )
    .await?;
    let mut value = serde_json::to_value(item).map_err(db_error)?;
    value["project_id"] = json!(project_id);
    Ok((StatusCode::CREATED, Json(value)))
}
pub(crate) async fn update_item(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(query): Query<ItemQuery>,
    Json(patch): Json<Value>,
) -> Result<Json<Value>, ApiError> {
    let project_id = scoped(query)?;
    let fields = patch
        .as_object()
        .filter(|o| !o.is_empty())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "nonempty item patch required"))?;
    // Interactive edits cannot rewrite identity or source evidence. Omitted
    // fields retain their current values inside the storage transaction.
    for (key, value) in fields {
        match key.as_str() {
            "title" | "view" | "type" | "status"
                if value.as_str().is_some_and(|s| !s.trim().is_empty()) => {}
            "description" if value.is_null() || value.is_string() => {}
            _ => {
                return Err(error(
                    StatusCode::BAD_REQUEST,
                    "unsupported item field or value",
                ))
            }
        }
    }
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::UpdateItem {
            id: id.clone(),
            patch,
        },
    )
    .await?;
    get_item(
        State(state),
        Path(id),
        Query(ItemQuery {
            project_id: Some(project_id),
        }),
    )
    .await
}
pub(crate) async fn delete_item(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(query): Query<ItemQuery>,
) -> Result<StatusCode, ApiError> {
    let project_id = scoped(query)?;
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::DeleteItem(id),
    )
    .await?;
    Ok(StatusCode::NO_CONTENT)
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct CreateLink {
    project_id: String,
    source_id: String,
    target_id: String,
    #[serde(rename = "type")]
    link_type: String,
}
fn link_id(link: &crate::store::CanonicalLink) -> String {
    use base64::Engine;
    // Encode the tuple rather than ambiguous colon-separated identifiers.
    base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(
        serde_json::to_vec(&(&link.source_id, &link.target_id, &link.link_type))
            .expect("string tuple"),
    )
}
fn link_value(project_id: &str, link: &crate::store::CanonicalLink) -> Value {
    json!({"id": link_id(link), "project_id": project_id, "source_id": link.source_id, "target_id": link.target_id, "type": link.link_type})
}
pub(crate) async fn create_link(
    State(state): State<AppState>,
    Json(body): Json<CreateLink>,
) -> Result<(StatusCode, Json<Value>), ApiError> {
    let project_id = scoped(ItemQuery {
        project_id: Some(body.project_id),
    })?;
    let link = crate::store::CanonicalLink {
        source_id: body.source_id,
        target_id: body.target_id,
        link_type: body.link_type,
    };
    if [&link.source_id, &link.target_id, &link.link_type]
        .iter()
        .any(|s| s.trim().is_empty() || s.len() > 256)
    {
        return Err(error(StatusCode::BAD_REQUEST, "invalid link"));
    }
    require_project(&state, &project_id).await?;
    for endpoint in [&link.source_id, &link.target_id] {
        if state
            .store
            .canonical_item(project_id.clone(), endpoint.clone())
            .await
            .map_err(db_error)?
            .is_none()
        {
            return Err(error(StatusCode::BAD_REQUEST, "dangling link endpoint"));
        }
    }
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::CreateLink(link.clone()),
    )
    .await?;
    Ok((StatusCode::CREATED, Json(link_value(&project_id, &link))))
}
pub(crate) async fn delete_link(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(query): Query<ItemQuery>,
) -> Result<StatusCode, ApiError> {
    use base64::Engine;
    let project_id = scoped(query)?;
    let tuple: (String, String, String) = base64::engine::general_purpose::URL_SAFE_NO_PAD
        .decode(id)
        .ok()
        .and_then(|bytes| serde_json::from_slice(&bytes).ok())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "invalid link identifier"))?;
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::DeleteLink(crate::store::CanonicalLink {
            source_id: tuple.0,
            target_id: tuple.1,
            link_type: tuple.2,
        }),
    )
    .await?;
    Ok(StatusCode::NO_CONTENT)
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct ReplaceLink {
    source_id: String,
    target_id: String,
    #[serde(rename = "type")]
    link_type: String,
}
pub(crate) async fn update_link(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(query): Query<ItemQuery>,
    Json(body): Json<ReplaceLink>,
) -> Result<Json<Value>, ApiError> {
    use base64::Engine;
    let project_id = scoped(query)?;
    let tuple: (String, String, String) = base64::engine::general_purpose::URL_SAFE_NO_PAD
        .decode(id)
        .ok()
        .and_then(|bytes| serde_json::from_slice(&bytes).ok())
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "invalid link identifier"))?;
    let old = crate::store::CanonicalLink {
        source_id: tuple.0,
        target_id: tuple.1,
        link_type: tuple.2,
    };
    let new = crate::store::CanonicalLink {
        source_id: body.source_id,
        target_id: body.target_id,
        link_type: body.link_type,
    };
    if [&new.source_id, &new.target_id, &new.link_type]
        .iter()
        .any(|s| s.trim().is_empty() || s.len() > 256)
    {
        return Err(error(StatusCode::BAD_REQUEST, "invalid link"));
    }
    require_project(&state, &project_id).await?;
    for endpoint in [&new.source_id, &new.target_id] {
        if state
            .store
            .canonical_item(project_id.clone(), endpoint.clone())
            .await
            .map_err(db_error)?
            .is_none()
        {
            return Err(error(StatusCode::BAD_REQUEST, "dangling link endpoint"));
        }
    }
    edit(
        &state,
        &project_id,
        crate::store::CanonicalMutation::ReplaceLink {
            old,
            new: new.clone(),
        },
    )
    .await?;
    Ok(Json(link_value(&project_id, &new)))
}
