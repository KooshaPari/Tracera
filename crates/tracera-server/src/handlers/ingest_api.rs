use axum::Json;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::ingest;
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
    /// Target repo in `owner/repo` format. Optional -- overridden by GITHUB_REPO env var.
    /// Stored for future use; currently GITHUB_REPO env var takes precedence.
    #[serde(default)]
    #[allow(dead_code)]
    pub(crate) repo: Option<String>,
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
