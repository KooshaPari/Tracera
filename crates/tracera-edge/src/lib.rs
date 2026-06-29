use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use worker::{event, Request, Response, Result, RouteContext, Router};

#[derive(Serialize)]
struct StatusResponse {
    status: &'static str,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(rename_all = "snake_case")]
struct TraceLinkInput {
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
    updated_at: Option<DateTime<Utc>>,
}

#[derive(Serialize)]
struct MatrixCellResponse {
    source_id: String,
    target_id: String,
    coverage: String,
    links: Vec<TraceLinkInput>,
}

#[derive(Deserialize)]
struct CoverageMatrixRequest {
    #[serde(default)]
    links: Vec<TraceLinkInput>,
    #[serde(default = "default_stale_after_days")]
    stale_after_days: u32,
}

#[derive(Serialize)]
struct CoverageMatrixResponse {
    generated_at: DateTime<Utc>,
    link_count: usize,
    cell_count: usize,
    stale_links: usize,
    cells: Vec<MatrixCellResponse>,
}

#[derive(Serialize)]
struct NotImplementedResponse {
    error: &'static str,
}

#[event(fetch)]
async fn fetch(req: Request, _env: worker::Env, _ctx: worker::Context) -> Result<Response> {
    Router::new()
        .get("/health", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ok" })
        })
        .get("/healthz", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ok" })
        })
        .get("/ready", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ready" })
        })
        .get("/readyz", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ready" })
        })
        .post_async("/api/v1/coverage-matrix", coverage_matrix)
        .post("/api/v1/impact", not_implemented)
        .post("/api/v1/confidence", not_implemented)
        .post("/api/v1/blast-radius", not_implemented)
        .post("/api/v1/governance/spec-check", not_implemented)
        .post("/api/v1/trace/forward/:artifact_id", not_implemented)
        .post("/api/v1/trace/reverse/:artifact_id", not_implemented)
        .get("/evidence", not_implemented)
        .post("/evidence", not_implemented)
        .get("/evidence/health", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ok" })
        })
        .post("/ingest/github", not_implemented)
        .post("/ingest/jira", not_implemented)
        .get("/sdlc-pm/health", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ok" })
        })
        .get("/sdlc-pm/sprints", not_implemented)
        .post("/sdlc-pm/sprints", not_implemented)
        .get("/sdlc-pm/stories", not_implemented)
        .get("/org-intel/health", |_req, _ctx| {
            Response::from_json(&StatusResponse { status: "ok" })
        })
        .get("/org-intel/teams", not_implemented)
        .get("/org-intel/metrics", not_implemented)
        .run(req, _env)
        .await
}

async fn coverage_matrix(mut req: Request, _ctx: RouteContext<()>) -> Result<Response> {
    let request = req.json::<CoverageMatrixRequest>().await?;
    Response::from_json(&build_coverage_matrix(request))
}

fn build_coverage_matrix(request: CoverageMatrixRequest) -> CoverageMatrixResponse {
    let now = Utc::now();
    let mut cells = Vec::new();
    let mut stale_links = 0usize;
    for link in &request.links {
        if let Some(updated_at) = link.updated_at {
            if (now - updated_at).num_days() as u32 > request.stale_after_days {
                stale_links += 1;
            }
        }
        cells.push(MatrixCellResponse {
            source_id: link.source_id.clone(),
            target_id: link.target_id.clone(),
            coverage: classify_coverage(link),
            links: vec![link.clone()],
        });
    }

    CoverageMatrixResponse {
        generated_at: now,
        link_count: request.links.len(),
        cell_count: cells.len(),
        stale_links,
        cells,
    }
}

fn classify_coverage(link: &TraceLinkInput) -> String {
    if link.relationship == "conflicts_with" {
        "conflict".to_string()
    } else if matches!(link.relationship.as_str(), "verifies" | "satisfies")
        && link.confidence >= 0.9
    {
        "covered".to_string()
    } else if matches!(link.relationship.as_str(), "verifies" | "satisfies") {
        "partial".to_string()
    } else {
        "missing".to_string()
    }
}

fn default_stale_after_days() -> u32 {
    90
}

fn not_implemented(_req: Request, _ctx: RouteContext<()>) -> Result<Response> {
    Response::from_json(&NotImplementedResponse {
        error: "not implemented",
    })
    .map(|resp| resp.with_status(501))
}
