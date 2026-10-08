use axum::Json;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeSet;

use crate::ingest;
use crate::store::{CanonicalItem, CanonicalLink};
use crate::validation::MAX_INGEST_ISSUES;

use super::super::AppState;

// --- ingest (port of src/tracertm/services/{github,jira}_import_service.py) ---
//
// Two modes per endpoint:
//   1. Live fetch -- if GITHUB_TOKEN+GITHUB_REPO (or JIRA_*) env vars are set,
//      the handler fetches issues directly from the API and ignores `issues`.
//   2. Payload push -- caller-supplied `issues` array, ingested via the same
//      persist_issues path so records land in the store regardless of mode.
//
// Fail-loud policy: if neither source is configured AND the `issues` field
// is empty, the response contains an error entry (not a fake-success 0).
#[derive(Deserialize)]
pub(crate) struct GitHubIngestRequest {
    /// Required for project-bound payload ingest to namespace issue IDs.
    /// Unbound live ingest continues to use GITHUB_REPO from the environment.
    #[serde(default)]
    pub(crate) repo: Option<String>,
    /// Opt in to the canonical graph for an existing project. Unbound requests
    /// retain the legacy stories/evidence/trace-links ingest behavior.
    #[serde(default)]
    pub(crate) project_id: Option<String>,
    #[serde(default)]
    pub(crate) issues: Vec<Value>,
}

#[derive(Deserialize)]
pub(crate) struct JiraIngestRequest {
    #[serde(default)]
    pub(crate) issues: Vec<Value>,
}

#[derive(Deserialize)]
pub(crate) struct AgcordIngestRequest {
    /// Caller-supplied items (agents/tasks). Optional -- if AGCORD_URL is set,
    /// the handler fetches live from AgCord and ignores this field.
    #[serde(default)]
    pub(crate) items: Vec<Value>,
}

#[derive(Serialize)]
pub(crate) struct BulkIngestionResult {
    pub(crate) total_processed: usize,
    pub(crate) requirements_created: usize,
    pub(crate) trace_links_created: usize,
    pub(crate) errors: Vec<String>,
}

pub(crate) fn validate_ingest_issues(issues: &[Value]) -> Result<(), &'static str> {
    if issues.len() > MAX_INGEST_ISSUES {
        return Err("too many issues");
    }
    if issues.iter().any(|issue| {
        serde_json::to_vec(issue)
            .map(|v| v.len())
            .unwrap_or(crate::validation::MAX_LONG_TEXT_CHARS + 1)
            > crate::validation::MAX_LONG_TEXT_CHARS
    }) {
        return Err("issue payload too large");
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Ingest handlers -- real persistence via Store trait
// ---------------------------------------------------------------------------

/// POST /ingest/github
///
/// If `GITHUB_TOKEN` and `GITHUB_REPO` are set, fetches issues live from
/// GitHub and ignores the `issues` payload field.  Otherwise falls back to
/// the caller-supplied `issues` array.  Fails loud if neither source has data.
pub(crate) async fn ingest_github(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(req): Json<GitHubIngestRequest>,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    if let Err(error) = validate_ingest_issues(&req.issues) {
        return (
            axum::http::StatusCode::BAD_REQUEST,
            Json(BulkIngestionResult {
                total_processed: 0,
                requirements_created: 0,
                trace_links_created: 0,
                errors: vec![error.to_string()],
            }),
        );
    }
    if let Some(project_id) = req.project_id.as_deref() {
        return ingest_github_canonical(&state, project_id, &req).await;
    }
    // Try live GitHub fetch first
    if ingest::GitHubConfig::from_env().is_some() {
        match ingest::ingest_live(&state.store).await {
            Ok(result) => return (axum::http::StatusCode::OK, Json(result)),
            Err(ingest::IngestError::NoSourceConfigured) => {} // fall through
            Err(e) => {
                tracing::error!("GitHub live ingest failed: {e}");
                let result = BulkIngestionResult {
                    total_processed: 0,
                    requirements_created: 0,
                    trace_links_created: 0,
                    errors: vec![format!("live ingest error: {e}")],
                };
                return (axum::http::StatusCode::BAD_GATEWAY, Json(result));
            }
        }
    }

    // Fall back to payload-based ingest
    if req.issues.is_empty() {
        let result = BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![
                "no ingest source configured: set GITHUB_TOKEN+GITHUB_REPO, \
                 or supply issues[] in the request body"
                    .to_string(),
            ],
        };
        return (axum::http::StatusCode::UNPROCESSABLE_ENTITY, Json(result));
    }

    let result = ingest::ingest_from_payload(&req.issues, "number", "github", &state.store).await;
    (axum::http::StatusCode::OK, Json(result))
}

fn github_repo_name(repo: Option<&str>) -> Option<&str> {
    let repo = repo?;
    let (owner, name) = repo.split_once('/')?;
    if owner.is_empty()
        || name.is_empty()
        || repo.len() > 256
        || !owner
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
        || !name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_' || c == '.')
    {
        return None;
    }
    Some(repo)
}

fn github_canonical_error(
    status: axum::http::StatusCode,
    message: String,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    (
        status,
        Json(BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![message],
        }),
    )
}

/// Explicit payload push into an existing canonical project. References must
/// resolve to imported requirement items; no target is synthesized from text.
async fn ingest_github_canonical(
    state: &AppState,
    project_id: &str,
    req: &GitHubIngestRequest,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    use axum::http::StatusCode;
    if project_id.trim().is_empty() {
        return github_canonical_error(StatusCode::BAD_REQUEST, "project_id required".into());
    }
    let Some(repo) = github_repo_name(req.repo.as_deref()) else {
        return github_canonical_error(
            StatusCode::BAD_REQUEST,
            "repo must be owner/repo for a canonical ingest".into(),
        );
    };
    let (owner, repository) = repo.split_once('/').expect("validated repository");
    if req.issues.is_empty() {
        return github_canonical_error(
            StatusCode::UNPROCESSABLE_ENTITY,
            "issues[] required for a canonical ingest".into(),
        );
    }
    match state.store.canonical_project(project_id.to_owned()).await {
        Ok(Some(_)) => {}
        Ok(None) => {
            return github_canonical_error(
                StatusCode::NOT_FOUND,
                "canonical project not found".into(),
            )
        }
        Err(e) => {
            return github_canonical_error(
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("project lookup failed: {e}"),
            )
        }
    }

    let mut items = Vec::new();
    let mut links = Vec::new();
    let mut story_ids = BTreeSet::new();
    let mut requirement_ids = BTreeSet::new();
    for issue in &req.issues {
        let Some(number) = issue
            .get("number")
            .and_then(Value::as_u64)
            .filter(|n| *n > 0)
        else {
            return github_canonical_error(
                StatusCode::BAD_REQUEST,
                "each issue needs a positive numeric number".into(),
            );
        };
        let Some(title) = issue
            .get("title")
            .and_then(Value::as_str)
            .filter(|s| !s.trim().is_empty())
        else {
            return github_canonical_error(
                StatusCode::BAD_REQUEST,
                "each issue needs a title".into(),
            );
        };
        let story_id = format!("github:{owner}:{repository}:{number}");
        if !story_ids.insert(story_id.clone()) {
            return github_canonical_error(
                StatusCode::BAD_REQUEST,
                format!("duplicate GitHub issue: {number}"),
            );
        }
        let body = issue.get("body").and_then(Value::as_str).unwrap_or("");
        let Some(source_url) = issue.get("html_url").and_then(Value::as_str).filter(|s| {
            s.len() <= 2048
                && reqwest::Url::parse(s).is_ok_and(|url| {
                    matches!(url.scheme(), "http" | "https") && url.host_str().is_some()
                })
        }) else {
            return github_canonical_error(
                StatusCode::BAD_REQUEST,
                "each bound issue needs an absolute http(s) html_url".into(),
            );
        };
        let status = match issue.get("state").and_then(Value::as_str).unwrap_or("open") {
            "open" => "todo",
            "closed" => "done",
            _ => {
                return github_canonical_error(
                    StatusCode::BAD_REQUEST,
                    "GitHub issue state must be open or closed".into(),
                )
            }
        };
        items.push(CanonicalItem {
            id: story_id.clone(),
            title: title.to_owned(),
            view: "feature".into(),
            item_type: "story".into(),
            status: status.to_owned(),
            description: Some(body.to_owned()),
            version: Some(1),
            source_url: Some(source_url.to_owned()),
            source_repo: Some(repo.to_owned()),
            source_kind: Some("github_issue".into()),
        });
        for requirement_id in ingest::extract_req_refs(body) {
            requirement_ids.insert(requirement_id.clone());
            links.push(CanonicalLink {
                source_id: story_id.clone(),
                target_id: requirement_id,
                link_type: "satisfies".into(),
            });
        }
    }
    let mut unresolved = Vec::new();
    for requirement_id in requirement_ids {
        match state
            .store
            .canonical_item(project_id.to_owned(), requirement_id.clone())
            .await
        {
            Ok(Some(item)) if item.item_type == "requirement" => {}
            Ok(_) => unresolved.push(requirement_id),
            Err(e) => {
                return github_canonical_error(
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("requirement lookup failed: {e}"),
                )
            }
        }
    }
    if !unresolved.is_empty() {
        return github_canonical_error(
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("unresolved requirement IDs: {}", unresolved.join(", ")),
        );
    }
    let total_processed = items.len();
    let trace_links_created = links.len();
    if let Err(e) = state
        .store
        .append_canonical(project_id.to_owned(), items, links)
        .await
    {
        tracing::warn!("canonical GitHub ingest rejected: {e}");
        return github_canonical_error(
            StatusCode::CONFLICT,
            "canonical GitHub issue conflict".into(),
        );
    }
    (
        StatusCode::OK,
        Json(BulkIngestionResult {
            total_processed,
            requirements_created: total_processed,
            trace_links_created,
            errors: Vec::new(),
        }),
    )
}

/// POST /ingest/jira
///
/// If `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` are
/// all set, fetches issues live from Jira.  Otherwise uses the `issues` payload.
/// Fails loud if neither source has data.
pub(crate) async fn ingest_jira(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(req): Json<JiraIngestRequest>,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    if let Err(error) = validate_ingest_issues(&req.issues) {
        return (
            axum::http::StatusCode::BAD_REQUEST,
            Json(BulkIngestionResult {
                total_processed: 0,
                requirements_created: 0,
                trace_links_created: 0,
                errors: vec![error.to_string()],
            }),
        );
    }
    // Try live Jira fetch first
    if ingest::JiraConfig::from_env().is_some() {
        match ingest::ingest_live(&state.store).await {
            Ok(result) => return (axum::http::StatusCode::OK, Json(result)),
            Err(ingest::IngestError::NoSourceConfigured) => {}
            Err(e) => {
                tracing::error!("Jira live ingest failed: {e}");
                let result = BulkIngestionResult {
                    total_processed: 0,
                    requirements_created: 0,
                    trace_links_created: 0,
                    errors: vec![format!("live ingest error: {e}")],
                };
                return (axum::http::StatusCode::BAD_GATEWAY, Json(result));
            }
        }
    }

    // Fall back to payload-based ingest
    if req.issues.is_empty() {
        let result = BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![
                "no ingest source configured: set JIRA_URL+JIRA_EMAIL+JIRA_API_TOKEN+JIRA_PROJECT_KEY, \
                 or supply issues[] in the request body"
                    .to_string(),
            ],
        };
        return (axum::http::StatusCode::UNPROCESSABLE_ENTITY, Json(result));
    }

    let result = ingest::ingest_from_payload(&req.issues, "key", "jira", &state.store).await;
    (axum::http::StatusCode::OK, Json(result))
}

/// POST /ingest/agileplus
///
/// Ingests agent and task data from AgCord (autonomous agent communication
/// platform) into Tracera's traceability graph.
///
/// Two modes:
///   1. Live fetch -- if `AGCORD_URL` is set, fetches agents and tasks from
///      AgCord's HTTP API (`/api/agents`, `/api/tasks`).
///   2. Payload push -- caller-supplied `items` array (agents/tasks).
///
/// AgCord provides the governance and work-management layer that Tracera
/// expands into full graph-based traceability for agentic product engineering.
pub(crate) async fn ingest_agileplus(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(req): Json<AgcordIngestRequest>,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    // Try live AgCord fetch first
    if ingest::AgcordConfig::from_env().is_some() {
        match ingest::ingest_live(&state.store).await {
            Ok(result) => return (axum::http::StatusCode::OK, Json(result)),
            Err(ingest::IngestError::NoSourceConfigured) => {}
            Err(e) => {
                tracing::error!("AgCord live ingest failed: {e}");
                let result = BulkIngestionResult {
                    total_processed: 0,
                    requirements_created: 0,
                    trace_links_created: 0,
                    errors: vec![format!("live ingest error: {e}")],
                };
                return (axum::http::StatusCode::BAD_GATEWAY, Json(result));
            }
        }
    }

    // Fall back to payload-based ingest
    if req.items.is_empty() {
        let result = BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec!["no ingest source configured: set AGCORD_URL, \
                 or supply items[] in the request body"
                .to_string()],
        };
        return (axum::http::StatusCode::UNPROCESSABLE_ENTITY, Json(result));
    }

    let result = ingest::ingest_from_payload(&req.items, "id", "agcord", &state.store).await;
    (axum::http::StatusCode::OK, Json(result))
}
