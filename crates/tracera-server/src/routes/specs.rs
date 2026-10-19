//! Specification reads are projections of canonical persisted items, never synthetic records.
//! Specialized execution/activity/health semantics remain explicitly unavailable.
use crate::{
    item::{Item, ItemFilter},
    AppState,
};
use axum::{
    extract::{MatchedPath, Path, Query, State},
    http::StatusCode,
    routing::{any, get},
    Json, Router,
};
use serde::Deserialize;
use serde_json::{json, Map, Value};
use std::{collections::BTreeMap, time::Duration};

type Failure = (StatusCode, Json<Value>);
type Reply = Result<Json<Value>, Failure>;
fn failure(status: StatusCode, error: &str) -> Failure {
    (status, Json(json!({"error":error})))
}
pub(super) async fn unavailable(path: MatchedPath) -> Failure {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error":"not_implemented", "route":path.as_str()})),
    )
}
#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    project_id: Option<String>,
    status: Option<String>,
    search: Option<String>,
    tags: Option<String>,
    contract_type: Option<String>,
    feature_id: Option<String>,
    limit: Option<usize>,
    offset: Option<usize>,
}
fn family(path: &str) -> &'static str {
    if path.contains("/adrs") {
        "adr"
    } else if path.contains("/contracts") {
        "contract"
    } else if path.contains("/features") {
        "feature"
    } else {
        "scenario"
    }
}
fn is_family(item: &Item, kind: &str) -> bool {
    item.item_type.eq_ignore_ascii_case(kind)
}
// Keep every original field, and supply snake_case aliases expected by existing specs clients.
fn document(item: &Item) -> Value {
    let mut value = serde_json::to_value(item).expect("Item serializes");
    let map = value.as_object_mut().expect("Item is an object");
    for (key, value) in map.clone() {
        let mut snake = String::new();
        for c in key.chars() {
            if c.is_ascii_uppercase() {
                snake.push('_');
                snake.push(c.to_ascii_lowercase());
            } else {
                snake.push(c);
            }
        }
        map.entry(snake).or_insert(value);
    }
    // Canonical identity/timestamps take precedence over conflicting extension aliases.
    map.insert("project_id".into(), json!(item.project_id));
    map.insert("created_at".into(), json!(item.created_at));
    map.insert("updated_at".into(), json!(item.updated_at));
    value
}
async fn load(state: &AppState, project: Option<String>) -> Result<Vec<Item>, Failure> {
    let work = async {
        let mut all = Vec::new();
        let filter = ItemFilter {
            project_id: project.clone(),
            ..Default::default()
        };
        loop {
            let page = state
                .store
                .list_items(filter.clone(), 100, all.len() as i64)
                .await
                .map_err(|_| failure(StatusCode::INTERNAL_SERVER_ERROR, "specs_store_error"))?;
            if page.total > 100_000 {
                return Err(failure(
                    StatusCode::SERVICE_UNAVAILABLE,
                    "specs_query_over_budget",
                ));
            }
            let empty = page.items.is_empty();
            all.extend(page.items);
            if all.len() as i64 >= page.total {
                if all.is_empty() {
                    if let Some(id) = project.clone() {
                        let exists = state.store.get_project(id).await.map_err(|_| {
                            failure(StatusCode::INTERNAL_SERVER_ERROR, "specs_store_error")
                        })?;
                        if exists.is_none() {
                            return Err(failure(StatusCode::NOT_FOUND, "project_not_found"));
                        }
                    }
                }
                return Ok(all);
            }
            if empty {
                return Err(failure(
                    StatusCode::SERVICE_UNAVAILABLE,
                    "specs_incomplete_read",
                ));
            }
        }
    };
    tokio::time::timeout(Duration::from_secs(2), work)
        .await
        .map_err(|_| failure(StatusCode::SERVICE_UNAVAILABLE, "specs_query_over_budget"))?
}
fn matches(item: &Item, p: &Params) -> bool {
    let d = document(item);
    p.status.as_ref().is_none_or(|s| &item.status == s)
        && p.search.as_ref().is_none_or(|s| {
            let needle = s.to_lowercase();
            item.title.to_lowercase().contains(&needle)
                || d.get("description")
                    .and_then(Value::as_str)
                    .is_some_and(|v| v.to_lowercase().contains(&needle))
        })
        && p.contract_type
            .as_ref()
            .is_none_or(|s| d.get("contract_type").and_then(Value::as_str) == Some(s.as_str()))
        && p.feature_id
            .as_ref()
            .is_none_or(|s| d.get("feature_id").and_then(Value::as_str) == Some(s.as_str()))
        && p.tags.as_ref().is_none_or(|tags| {
            tags.split(',').all(|tag| {
                d.get("tags")
                    .and_then(Value::as_array)
                    .is_some_and(|values| values.iter().any(|v| v.as_str() == Some(tag)))
            })
        })
}
async fn list(State(state): State<AppState>, path: MatchedPath, Query(p): Query<Params>) -> Reply {
    listing(state, family(path.as_str()), p).await
}
async fn listing(state: AppState, kind: &str, p: Params) -> Reply {
    if p.limit.is_some_and(|v| v == 0 || v > 1000) || p.offset.is_some_and(|v| v > 100_000) {
        return Err(failure(StatusCode::BAD_REQUEST, "invalid_pagination"));
    }
    let items: Vec<_> = load(&state, p.project_id.clone())
        .await?
        .into_iter()
        .filter(|i| is_family(i, kind) && matches(i, &p))
        .collect();
    let total = items.len();
    let offset = p.offset.unwrap_or(0);
    let limit = p.limit.unwrap_or(total);
    let docs: Vec<_> = items
        .iter()
        .skip(offset)
        .take(limit)
        .map(document)
        .collect();
    let mut response = Map::new();
    response.insert(format!("{kind}s"), json!(docs));
    response.insert("total".into(), json!(total));
    response.insert(
        "has_more".into(),
        json!(offset.saturating_add(docs.len()) < total),
    );
    Ok(Json(Value::Object(response)))
}
async fn project_scenarios(
    State(state): State<AppState>,
    Path(project): Path<String>,
    Query(mut p): Query<Params>,
) -> Reply {
    if p.project_id.as_ref().is_some_and(|v| v != &project) {
        return Err(failure(StatusCode::BAD_REQUEST, "project_id_mismatch"));
    }
    p.project_id = Some(project);
    listing(state, "scenario", p).await
}
async fn detail(State(state): State<AppState>, path: MatchedPath, Path(id): Path<String>) -> Reply {
    let item = tokio::time::timeout(Duration::from_secs(2), state.store.get_item(id))
        .await
        .map_err(|_| failure(StatusCode::SERVICE_UNAVAILABLE, "specs_query_over_budget"))?
        .map_err(|_| failure(StatusCode::INTERNAL_SERVER_ERROR, "specs_store_error"))?
        .filter(|i| is_family(i, family(path.as_str())))
        .ok_or_else(|| failure(StatusCode::NOT_FOUND, "specification_not_found"))?;
    Ok(Json(document(&item)))
}
async fn stats(
    State(state): State<AppState>,
    path: MatchedPath,
    Path(project): Path<String>,
) -> Reply {
    let kind = family(path.as_str());
    let all = load(&state, Some(project.clone())).await?;
    let items: Vec<_> = all.iter().filter(|i| is_family(i, kind)).collect();
    let mut by_status = BTreeMap::new();
    for item in &items {
        *by_status.entry(item.status.clone()).or_insert(0usize) += 1;
    }
    // Only metrics backed by stored fields are emitted. Missing observations are null.
    let mut result = json!({"project_id":project, "total":items.len(), "by_status":by_status});
    if kind == "adr" {
        let scores: Vec<_> = items
            .iter()
            .filter_map(|i| document(i)["compliance_score"].as_f64())
            .collect();
        result["average_compliance_score"] = if scores.len() == items.len() && !scores.is_empty() {
            json!(scores.iter().sum::<f64>() / scores.len() as f64)
        } else {
            Value::Null
        };
        result["pending_verification"] = json!(items
            .iter()
            .filter(|i| document(i)["last_verified_at"].is_null())
            .count());
        let linked: std::collections::BTreeSet<_> = items
            .iter()
            .flat_map(|i| {
                document(i)["related_requirements"]
                    .as_array()
                    .cloned()
                    .unwrap_or_default()
            })
            .filter_map(|v| v.as_str().map(str::to_owned))
            .collect();
        result["requirements_linked"] = json!(linked.len());
    }
    if kind == "feature" {
        result["total_features"] = json!(items.len());
        result["total_scenarios"] = json!(all.iter().filter(|i| is_family(i, "scenario")).count());
        result["pass_rate"] = Value::Null;
        result["coverage"] =
            json!({"percentage":null,"requirements_covered":null,"total_requirements":null});
    }
    if kind == "contract" {
        let mut by_type = BTreeMap::new();
        for item in &items {
            if let Some(t) = document(item)["contract_type"].as_str() {
                *by_type.entry(t.to_owned()).or_insert(0usize) += 1;
            }
        }
        result["by_type"] = json!(by_type);
        result["verification_rate"] = Value::Null;
        result["violation_count"] = Value::Null;
    }
    Ok(Json(result))
}
pub(super) fn routes() -> Router<AppState> {
    let mut router = Router::new();
    for kind in ["contracts", "features", "scenarios", "adrs"] {
        router = router
            .route(&format!("/api/v1/{kind}"), get(list).fallback(unavailable))
            .route(
                &format!("/api/v1/{kind}/{{id}}"),
                get(detail).fallback(unavailable),
            );
    }
    for kind in ["contracts", "features", "adrs"] {
        router = router.route(
            &format!("/api/v1/projects/{{project_id}}/{kind}/stats"),
            get(stats).fallback(unavailable),
        );
    }
    for route in [
        "/api/v1/contracts/{id}/verify",
        "/api/v1/contracts/{id}/activities",
        "/api/v1/features/{id}/activities",
        "/api/v1/scenarios/{id}/run",
        "/api/v1/specifications/scenarios/{id}/activities",
        "/api/v1/specifications/projects/{project_id}/scenarios/activities",
        "/api/v1/adrs/{id}/verify",
        "/api/v1/adrs/{id}/activities",
        "/api/v1/projects/{project_id}/specifications/summary",
        "/api/v1/projects/{project_id}/specifications/stats",
    ] {
        router = router.route(route, any(unavailable));
    }
    router.route(
        "/api/v1/specifications/projects/{project_id}/scenarios",
        get(project_scenarios).fallback(unavailable),
    )
}
#[cfg(test)]
#[path = "specs_tests.rs"]
mod tests;
