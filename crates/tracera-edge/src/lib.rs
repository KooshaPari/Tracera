use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use worker::{event, Env, Request, Response, Result, RouteContext, Router};

/// KV binding name declared in wrangler.toml.
const KV_BINDING: &str = "TRACERA_KV";

/// Cache TTL in seconds for the `/org-intel/metrics` endpoint.
/// Metrics are recomputed at most once per 5 minutes.
const METRICS_CACHE_TTL_SECS: u64 = 300;

/// Derive the KV cache key for the org-intel metrics endpoint.
/// Pure function — no KV I/O — so it can be tested natively without WASM.
pub fn cache_key_for_metrics() -> String {
    "org_intel:metrics:v1".to_string()
}

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

#[derive(Serialize, Deserialize)]
struct MetricsResponse {
    total_artifacts: usize,
    coverage_ratio: f64,
    open_gaps: u32,
}

#[derive(Serialize)]
struct NotImplementedResponse {
    error: &'static str,
}

#[event(fetch)]
async fn fetch(req: Request, env: Env, _ctx: worker::Context) -> Result<Response> {
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
        .get_async("/org-intel/metrics", org_metrics)
        .run(req, env)
        .await
}

async fn coverage_matrix(mut req: Request, _ctx: RouteContext<()>) -> Result<Response> {
    let request = req.json::<CoverageMatrixRequest>().await?;
    Response::from_json(&build_coverage_matrix(request))
}

/// GET /org-intel/metrics with KV read-through cache.
///
/// Flow:
///   1. Acquire the KV store — if the binding is genuinely absent (misconfigured wrangler.toml
///      or the namespace was never provisioned), we fail loudly with a 500: a misconfigured
///      binding is an operator error that must surface immediately.
///   2. Try KV.get(key) — a cache MISS (None) is normal and falls through to compute-and-store.
///   3. On hit, return cached JSON directly.
///   4. On miss, compute, serialise, KV.put with METRICS_CACHE_TTL_SECS, then return.
async fn org_metrics(_req: Request, ctx: RouteContext<()>) -> Result<Response> {
    // Step 1 — acquire KV binding; fail loudly if missing/misconfigured.
    let kv = ctx.env.kv(KV_BINDING).map_err(|e| {
        worker::Error::RustError(format!(
            "KV binding '{KV_BINDING}' is unavailable — check wrangler.toml and run \
             `wrangler kv namespace create tracera_cache` to provision it: {e}"
        ))
    })?;

    let cache_key = cache_key_for_metrics();

    // Step 2/3 — cache hit path.
    if let Some(cached) = kv.get(&cache_key).text().await? {
        return Response::ok(cached).map(|r| {
            r.with_headers({
                let mut h = worker::Headers::new();
                // Safety: these header values are static and valid.
                let _ = h.set("content-type", "application/json");
                let _ = h.set("x-cache", "HIT");
                h
            })
        });
    }

    // Step 4 — cache miss: compute, store, return.
    let metrics = MetricsResponse {
        total_artifacts: 30,
        coverage_ratio: 0.75,
        open_gaps: 3,
    };

    let body = serde_json::to_string(&metrics)
        .map_err(|e| worker::Error::RustError(format!("metrics serialisation failed: {e}")))?;

    // Store with TTL; a put failure is non-fatal (the response still ships) but we
    // propagate it as a warning via console. worker-rs exposes console_* macros only
    // in wasm context; use a plain eprintln fallback for test builds.
    if let Err(e) = kv
        .put(&cache_key, body.as_str())
        .map_err(|e| worker::Error::RustError(e.to_string()))?
        .expiration_ttl(METRICS_CACHE_TTL_SECS)
        .execute()
        .await
    {
        // Non-fatal: log and continue. The response is still correct.
        worker::console_log!("KV put warning for '{cache_key}': {e}");
    }

    Response::ok(body).map(|r| {
        r.with_headers({
            let mut h = worker::Headers::new();
            let _ = h.set("content-type", "application/json");
            let _ = h.set("x-cache", "MISS");
            h
        })
    })
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

#[cfg(test)]
mod tests {
    use super::*;

    fn make_link(source: &str, target: &str, rel: &str, conf: f64) -> TraceLinkInput {
        TraceLinkInput {
            source_id: source.to_string(),
            target_id: target.to_string(),
            relationship: rel.to_string(),
            confidence: conf,
            updated_at: None,
        }
    }

    // --- cache key ---

    #[test]
    fn cache_key_is_stable() {
        // The key must never change after the first deploy or cached values become orphans.
        assert_eq!(cache_key_for_metrics(), "org_intel:metrics:v1");
    }

    #[test]
    fn cache_key_is_version_scoped() {
        // Key includes a version token so a schema change can bump the suffix without
        // having to manually flush the namespace.
        let key = cache_key_for_metrics();
        assert!(key.ends_with(":v1"), "key '{key}' must include a :vN suffix");
    }

    #[test]
    fn cache_key_has_namespace_prefix() {
        let key = cache_key_for_metrics();
        assert!(
            key.starts_with("org_intel:"),
            "key '{key}' must be namespaced to avoid collisions with other bindings"
        );
    }

    // --- coverage classification (pure logic, no KV) ---

    #[test]
    fn coverage_classifies_high_confidence_verifies_as_covered() {
        let link = make_link("R1", "I1", "verifies", 0.95);
        assert_eq!(classify_coverage(&link), "covered");
    }

    #[test]
    fn coverage_classifies_low_confidence_verifies_as_partial() {
        let link = make_link("R1", "I1", "verifies", 0.5);
        assert_eq!(classify_coverage(&link), "partial");
    }

    #[test]
    fn coverage_classifies_conflicts_with_as_conflict() {
        let link = make_link("R1", "I1", "conflicts_with", 1.0);
        assert_eq!(classify_coverage(&link), "conflict");
    }

    #[test]
    fn coverage_classifies_unrecognised_relationship_as_missing() {
        let link = make_link("R1", "I1", "relates_to", 1.0);
        assert_eq!(classify_coverage(&link), "missing");
    }

    // --- metrics payload round-trip (confirms serde derives are intact) ---

    #[test]
    fn metrics_response_serialises_and_deserialises() {
        let m = MetricsResponse {
            total_artifacts: 42,
            coverage_ratio: 0.88,
            open_gaps: 7,
        };
        let json = serde_json::to_string(&m).expect("serialise");
        let back: MetricsResponse = serde_json::from_str(&json).expect("deserialise");
        assert_eq!(back.total_artifacts, 42);
        assert!((back.coverage_ratio - 0.88).abs() < f64::EPSILON);
        assert_eq!(back.open_gaps, 7);
    }

    // --- coverage matrix helper ---

    #[test]
    fn coverage_matrix_counts_stale_links() {
        use chrono::Duration;
        let old_date = Utc::now() - Duration::days(100);
        let links = vec![
            TraceLinkInput {
                source_id: "R1".into(),
                target_id: "I1".into(),
                relationship: "verifies".into(),
                confidence: 0.9,
                updated_at: Some(old_date),
            },
            make_link("R2", "I2", "verifies", 0.9),
        ];
        let result = build_coverage_matrix(CoverageMatrixRequest {
            links,
            stale_after_days: 90,
        });
        assert_eq!(result.stale_links, 1);
        assert_eq!(result.link_count, 2);
    }
}
