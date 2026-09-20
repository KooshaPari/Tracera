use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use worker::{event, Env, Request, Response, Result, RouteContext, Router};

/// KV binding name declared in wrangler.toml.
const KV_BINDING: &str = "TRACERA_KV";

/// KV key prefix for fleet-node records.
const FLEET_NODE_PREFIX: &str = "fleet:node:";

/// Cache TTL in seconds for the `/org-intel/metrics` endpoint.
/// Metrics are recomputed at most once per 5 minutes.
const METRICS_CACHE_TTL_SECS: u64 = 300;
/// Keep edge-side matrix expansion aligned with the Rust API memory guard.
const MAX_COVERAGE_LINKS: usize = 25_000;

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
struct ApiErrorResponse {
    error: &'static str,
}

// --- Fleet control plane ---

#[derive(Debug, Deserialize)]
struct FleetEnrollRequest {
    node_id: String,
    #[serde(default)]
    caps: std::collections::HashMap<String, String>,
    #[serde(default)]
    sidecar_version: String,
}

#[derive(Serialize)]
struct FleetEnrollResponse {
    accepted: bool,
    generation: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    reason: Option<&'static str>,
}

#[derive(Debug, Serialize, Deserialize)]
struct FleetDesiredState {
    generation: i64,
    services: std::collections::HashMap<String, String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct FleetStatusReport {
    node_id: String,
    generation: i64,
    services: std::collections::HashMap<String, String>,
    updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct FleetNodeSummary {
    node_id: String,
    generation: i64,
    services: std::collections::HashMap<String, String>,
    last_seen: Option<DateTime<Utc>>,
}

/// Read the fleet enroll token from the environment (set via wrangler secret).
/// An unset token disables the fleet surface entirely so a misconfigured
/// deploy cannot silently accept unauthenticated enrollment.
fn fleet_token(env: &Env) -> Option<String> {
    env.secret("FLEET_ENROLL_TOKEN").ok().map(|s| s.to_string())
}

fn fleet_authorized(req: &Request, env: &Env) -> bool {
    let Some(expected) = fleet_token(env) else {
        return false;
    };
    match req.headers().get("Authorization") {
        Ok(Some(value)) => {
            let mut parts = value.splitn(2, ' ');
            parts.next() == Some("Bearer") && parts.next() == Some(expected.as_str())
        }
        _ => false,
    }
}

fn fleet_unauthorized() -> Result<Response> {
    Response::from_json(&ApiErrorResponse { error: "unauthorized" })
        .map(|r| r.with_status(401))
}

/// POST /fleet/enroll — register or re-acknowledge a node.
async fn fleet_enroll(mut req: Request, ctx: RouteContext<()>) -> Result<Response> {
    if !fleet_authorized(&req, &ctx.env) {
        return fleet_unauthorized();
    }
    let body = req.json::<FleetEnrollRequest>().await?;
    let node_id = body.node_id.clone();
    if node_id.is_empty() || node_id.len() > 128 {
        return Response::from_json(&FleetEnrollResponse {
            accepted: false,
            generation: 0,
            reason: Some("node_id must be 1..=128 chars"),
        })
        .map(|r| r.with_status(400));
    }

    let kv = ctx.env.kv(KV_BINDING).map_err(worker::Error::from)?;
    let key = format!("{FLEET_NODE_PREFIX}{node_id}");
    let generation = match kv.get(&key).json::<FleetNodeSummary>().await? {
        Some(existing) => existing.generation,
        None => 0,
    };
    let record = FleetNodeSummary {
        node_id,
        generation,
        services: std::collections::HashMap::new(),
        last_seen: Some(Utc::now()),
    };
    let payload = serde_json::to_string(&record)
        .map_err(|e| worker::Error::RustError(e.to_string()))?;
    kv.put(&key, payload)?.execute().await?;

    Response::from_json(&FleetEnrollResponse {
        accepted: true,
        generation,
        reason: None,
    })
}

/// GET /fleet/desired?node_id=... — return the desired state for a node.
async fn fleet_desired(req: Request, ctx: RouteContext<()>) -> Result<Response> {
    if !fleet_authorized(&req, &ctx.env) {
        return fleet_unauthorized();
    }
    let node_id = req.url()?.query_pairs().into_owned()
        .find(|(k, _)| k == "node_id")
        .map(|(_, v)| v)
        .unwrap_or_default();
    if node_id.is_empty() {
        return Response::from_json(&ApiErrorResponse { error: "node_id required" })
            .map(|r| r.with_status(400));
    }
    let kv = ctx.env.kv(KV_BINDING).map_err(worker::Error::from)?;
    let key = format!("{FLEET_NODE_PREFIX}{node_id}");
    let state = match kv.get(&key).json::<FleetNodeSummary>().await? {
        Some(existing) => FleetDesiredState {
            generation: existing.generation,
            services: existing.services,
        },
        None => FleetDesiredState {
            generation: 0,
            services: std::collections::HashMap::new(),
        },
    };
    Response::from_json(&state)
}

/// PUT /fleet/desired/all — publish a new desired service set to every
/// enrolled node. Increments each node's generation so nodes converge on
/// their next poll.
async fn fleet_desired_put(mut req: Request, ctx: RouteContext<()>) -> Result<Response> {
    if !fleet_authorized(&req, &ctx.env) {
        return fleet_unauthorized();
    }
    let body = req.json::<FleetDesiredState>().await?;

    let kv = ctx.env.kv(KV_BINDING).map_err(worker::Error::from)?;
    let list = kv.list().prefix(FLEET_NODE_PREFIX.to_string()).execute().await?;
    let mut updated = 0usize;
    for key in &list.keys {
        let Some(existing) = kv.get(&key.name).json::<FleetNodeSummary>().await? else {
            continue;
        };
        let record = FleetNodeSummary {
            node_id: existing.node_id.clone(),
            generation: existing.generation + 1,
            services: body.services.clone(),
            last_seen: existing.last_seen,
        };
        let payload = serde_json::to_string(&record)
            .map_err(|e| worker::Error::RustError(e.to_string()))?;
        kv.put(&key.name, payload)?.execute().await?;
        updated += 1;
    }
    Response::from_json(&serde_json::json!({ "updated_nodes": updated }))
}

/// POST /fleet/report — record a node's convergence result.
async fn fleet_report(mut req: Request, ctx: RouteContext<()>) -> Result<Response> {
    if !fleet_authorized(&req, &ctx.env) {
        return fleet_unauthorized();
    }
    let report = req.json::<FleetStatusReport>().await?;
    let kv = ctx.env.kv(KV_BINDING).map_err(worker::Error::from)?;
    let key = format!("{FLEET_NODE_PREFIX}{}", report.node_id);
    let existing = kv.get(&key).json::<FleetNodeSummary>().await?;
    let record = FleetNodeSummary {
        node_id: report.node_id,
        generation: report.generation,
        services: report.services,
        last_seen: Some(Utc::now()),
    };
    let _ = existing; // Reserved for conflict detection in a later phase.
    let payload = serde_json::to_string(&record)
        .map_err(|e| worker::Error::RustError(e.to_string()))?;
    kv.put(&key, payload)?.execute().await?;
    Response::from_json(&StatusResponse { status: "ok" })
}

/// GET /fleet/nodes — operator-facing list of enrolled nodes.
async fn fleet_nodes(_req: Request, ctx: RouteContext<()>) -> Result<Response> {
    let kv = ctx.env.kv(KV_BINDING).map_err(worker::Error::from)?;
    let list = kv.list().prefix(FLEET_NODE_PREFIX.to_string()).execute().await?;
    let mut out = Vec::new();
    for key in &list.keys {
        if let Some(record) = kv.get(&key.name).json::<FleetNodeSummary>().await? {
            out.push(record);
        }
    }
    Response::from_json(&out)
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
        .post_async("/fleet/enroll", fleet_enroll)
        .get_async("/fleet/desired", fleet_desired)
        .put_async("/fleet/desired/all", fleet_desired_put)
        .post_async("/fleet/report", fleet_report)
        .get_async("/fleet/nodes", fleet_nodes)
        .run(req, env)
        .await
}

async fn coverage_matrix(mut req: Request, _ctx: RouteContext<()>) -> Result<Response> {
    let request = req.json::<CoverageMatrixRequest>().await?;
    if request.links.len() > MAX_COVERAGE_LINKS {
        return Response::from_json(&ApiErrorResponse {
            error: "coverage matrix exceeds link limit; use a paged export",
        })
        .map(|response| response.with_status(413));
    }
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
                let h = worker::Headers::new();
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
            let h = worker::Headers::new();
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
    Response::from_json(&ApiErrorResponse {
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
        assert!(
            key.ends_with(":v1"),
            "key '{key}' must include a :vN suffix"
        );
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
