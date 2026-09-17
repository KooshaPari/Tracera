use axum::Json;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{bad_request, ErrorResponse};
use crate::store::{Problem, ListParams};
use crate::validation::{
    validate_text, MAX_ID_CHARS, MAX_LONG_TEXT_CHARS, MAX_METADATA_BYTES, MAX_SHORT_TEXT_CHARS,
};

use super::super::AppState;

// ---------------------------------------------------------------------------
// Problem handlers (ITIL problem-management) -- recovered domain
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
pub(crate) struct ProblemCreateRequest {
    pub(crate) project_id: String,
    #[serde(default)]
    pub(crate) title: String,
    #[serde(default)]
    pub(crate) description: Option<String>,
    #[serde(default = "default_problem_status")]
    pub(crate) status: String,
    #[serde(default)]
    pub(crate) resolution_type: Option<String>,
    #[serde(default)]
    pub(crate) category: Option<String>,
    #[serde(default)]
    pub(crate) sub_category: Option<String>,
    #[serde(default)]
    pub(crate) tags: Option<serde_json::Value>,
    #[serde(default = "default_impact")]
    pub(crate) impact_level: String,
    #[serde(default = "default_impact")]
    pub(crate) urgency: String,
    #[serde(default = "default_impact")]
    pub(crate) priority: String,
    #[serde(default)]
    pub(crate) rca_performed: bool,
    #[serde(default)]
    pub(crate) root_cause_identified: bool,
    #[serde(default)]
    pub(crate) workaround_available: bool,
    #[serde(default)]
    pub(crate) permanent_fix_available: bool,
    #[serde(default)]
    pub(crate) assigned_to: Option<String>,
    #[serde(default)]
    pub(crate) assigned_team: Option<String>,
    #[serde(default)]
    pub(crate) owner: Option<String>,
    #[serde(default)]
    pub(crate) known_error_id: Option<String>,
}

pub(crate) fn default_problem_status() -> String {
    "open".to_string()
}

pub(crate) fn default_impact() -> String {
    "medium".to_string()
}

#[derive(Serialize)]
pub(crate) struct ProblemListResponse {
    pub(crate) project_id: String,
    pub(crate) count: usize,
    pub(crate) items: Vec<Problem>,
}

#[derive(Deserialize, Default)]
pub(crate) struct ProblemQuery {
    pub(crate) project_id: Option<String>,
    pub(crate) status: Option<String>,
    #[serde(flatten)]
    pub(crate) pagination: ListParams,
}

pub(crate) fn validate_problem(payload: &ProblemCreateRequest) -> Result<(), &'static str> {
    validate_text(
        &payload.project_id,
        "invalid project_id",
        MAX_ID_CHARS,
        true,
    )?;
    validate_text(&payload.title, "invalid title", MAX_SHORT_TEXT_CHARS, true)?;
    for (value, field) in [
        (payload.description.as_deref(), "invalid description"),
        (
            payload.resolution_type.as_deref(),
            "invalid resolution_type",
        ),
        (payload.category.as_deref(), "invalid category"),
        (payload.sub_category.as_deref(), "invalid sub_category"),
        (payload.assigned_to.as_deref(), "invalid assigned_to"),
        (payload.assigned_team.as_deref(), "invalid assigned_team"),
        (payload.owner.as_deref(), "invalid owner"),
        (payload.known_error_id.as_deref(), "invalid known_error_id"),
    ] {
        if let Some(value) = value {
            validate_text(value, field, MAX_LONG_TEXT_CHARS, false)?;
        }
    }
    for (value, field) in [
        (&payload.status, "invalid status"),
        (&payload.impact_level, "invalid impact_level"),
        (&payload.urgency, "invalid urgency"),
        (&payload.priority, "invalid priority"),
    ] {
        validate_text(value, field, MAX_SHORT_TEXT_CHARS, true)?;
    }
    if let Some(tags) = &payload.tags {
        if serde_json::to_vec(tags)
            .map(|v| v.len())
            .unwrap_or(MAX_METADATA_BYTES + 1)
            > MAX_METADATA_BYTES
        {
            return Err("tags too large");
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Problem handler implementations
// ---------------------------------------------------------------------------
pub(crate) async fn list_problems(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<ProblemQuery>,
) -> Result<Json<ProblemListResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let pagination = params
        .pagination
        .validated()
        .map_err(|_| bad_request("invalid pagination"))?;
    let project_id = params.project_id.unwrap_or_default();
    let status_filter = params.status;
    let items = state
        .store
        .list_problems(project_id.clone(), status_filter.clone(), pagination)
        .await
        .map_err(|e| {
            tracing::error!("list_problems store error: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "problem listing failed",
                }),
            )
        })?;
    let total = state
        .store
        .count_problems_filtered(project_id.clone(), status_filter)
        .await
        .map_err(|e| {
            tracing::error!("count_problems store error: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "problem count failed",
                }),
            )
        })?;
    Ok(Json(ProblemListResponse {
        project_id,
        count: total.max(0) as usize,
        items,
    }))
}

#[allow(clippy::too_many_arguments)]
pub(crate) async fn create_problem(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<ProblemCreateRequest>,
) -> Result<(axum::http::StatusCode, Json<Problem>), (axum::http::StatusCode, Json<ErrorResponse>)>
{
    validate_problem(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("prob-{}", Uuid::new_v4());
    // Human-readable problem number: P-YYYYMMDD-<8 hex>. Date-derived prefix
    // matches the Python implementation's `_generate_problem_number`.
    let problem_number = format!(
        "P-{}-{}",
        now.format("%Y%m%d"),
        Uuid::new_v4().simple().to_string()[..8].to_uppercase()
    );

    let problem = state
        .store
        .create_problem(
            id,
            payload.project_id,
            problem_number,
            payload.title,
            payload.description,
            payload.status,
            payload.resolution_type,
            payload.category,
            payload.sub_category,
            payload.tags,
            payload.impact_level,
            payload.urgency,
            payload.priority,
            payload.rca_performed,
            payload.root_cause_identified,
            payload.workaround_available,
            payload.permanent_fix_available,
            payload.assigned_to,
            payload.assigned_team,
            payload.owner,
            payload.known_error_id,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_problem store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "problem persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(problem)))
}
