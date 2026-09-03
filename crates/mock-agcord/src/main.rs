//! Mock AgCord server.
//!
//! Exposes a tiny subset of the AgCord REST surface so Tracera's
//! `/ingest/agileplus` endpoint (which calls
//! `tracera_server::ingest::fetch_agcord_agents` and
//! `fetch_agcord_tasks`) can be exercised against deterministic seed data
//! instead of a live AgCord deployment.
//!
//! JSON field shapes mirror what `fetch_agcord_agents` /
//! `fetch_agcord_tasks` (in `crates/tracera-server/src/ingest.rs`) read:
//!
//!   agents: { id, name, type, status, capabilities[] }
//!   tasks:  { id, name, description, priority, status, assignedAgent }
//!
//! Listens on PORT (default `3001`).

use axum::{routing::get, Json, Router};
use serde::Serialize;
use std::net::SocketAddr;

// ---------------------------------------------------------------------------
// Seed types
// ---------------------------------------------------------------------------

/// Agent payload as expected by `fetch_agcord_agents`.
#[derive(Debug, Serialize)]
struct Agent {
    id: String,
    name: String,
    #[serde(rename = "type")]
    agent_type: String,
    status: String,
    capabilities: Vec<String>,
}

/// Task payload as expected by `fetch_agcord_tasks`.
#[derive(Debug, Serialize)]
struct Task {
    id: String,
    name: String,
    description: String,
    priority: String,
    status: String,
    assigned_agent: String,
}

// ---------------------------------------------------------------------------
// Seed data — two agents, three tasks. Field shapes match the AgCord
// consumer in `tracera_server::ingest` exactly (note `assignedAgent` is
// camelCase in the JSON payload, hence the `rename` below).
// ---------------------------------------------------------------------------

fn seed_agents() -> Vec<Agent> {
    vec![
        Agent {
            id: "agent-1".to_string(),
            name: "researcher".to_string(),
            agent_type: "researcher".to_string(),
            status: "active".to_string(),
            capabilities: vec![
                "search".to_string(),
                "analysis".to_string(),
                "writing".to_string(),
            ],
        },
        Agent {
            id: "agent-2".to_string(),
            name: "coder".to_string(),
            agent_type: "coder".to_string(),
            status: "active".to_string(),
            capabilities: vec![
                "rust".to_string(),
                "typescript".to_string(),
                "python".to_string(),
            ],
        },
    ]
}

fn seed_tasks() -> Vec<Task> {
    vec![
        Task {
            id: "task-1".to_string(),
            name: "Audit scorecard".to_string(),
            description: "Comprehensive 155-pillar audit".to_string(),
            priority: "high".to_string(),
            status: "completed".to_string(),
            assigned_agent: "agent-1".to_string(),
        },
        Task {
            id: "task-2".to_string(),
            name: "Build SWEE graph CRUD".to_string(),
            description: "Wire graph schema into store trait".to_string(),
            priority: "high".to_string(),
            status: "in_progress".to_string(),
            assigned_agent: "agent-2".to_string(),
        },
        Task {
            id: "task-3".to_string(),
            name: "Review PR #1001".to_string(),
            description: "Code review for audit scorecard PR".to_string(),
            priority: "medium".to_string(),
            status: "completed".to_string(),
            assigned_agent: "agent-2".to_string(),
        },
    ]
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

async fn list_agents() -> Json<Vec<Agent>> {
    Json(seed_agents())
}

async fn list_tasks() -> Json<Vec<Task>> {
    Json(seed_tasks())
}

async fn healthz() -> &'static str {
    "ok"
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    let port: u16 = std::env::var("PORT")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(3001);

    let app = Router::new()
        .route("/api/agents", get(list_agents))
        .route("/api/tasks", get(list_tasks))
        .route("/healthz", get(healthz));

    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    println!("mock-agcord listening on http://{addr}");

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap_or_else(|e| {
        eprintln!("FATAL: cannot bind mock-agcord to {addr}: {e}");
        std::process::exit(1);
    });

    if let Err(e) = axum::serve(listener, app).await {
        eprintln!("FATAL: mock-agcord stopped unexpectedly: {e}");
        std::process::exit(1);
    }
}
