use serde_json::Value;

use super::{IngestError, NormalisedIssue};

/// Configuration for the AgCord ingest source (agent communication platform).
///
/// AgCord provides HTTP APIs for agents, tasks, and system status.
/// Set `AGCORD_URL` to the base URL (e.g. `http://localhost:3001`).
pub struct AgcordConfig {
    pub base_url: String,
}

impl AgcordConfig {
    /// Read from environment. Returns `None` if `AGCORD_URL` is absent.
    pub fn from_env() -> Option<Self> {
        let base_url = std::env::var("AGCORD_URL").ok()?;
        Some(Self { base_url })
    }
}

/// Fetch agents from AgCord's `/api/agents` endpoint.
///
/// AgCord agents represent autonomous entities with types, capabilities,
/// and status. Each agent is normalised into a `NormalisedIssue` with
/// source="agcord" for traceability into Tracera's graph model.
///
/// // wraps: reqwest 0.13
pub async fn fetch_agcord_agents(cfg: &AgcordConfig) -> Result<Vec<NormalisedIssue>, IngestError> {
    let client = reqwest::Client::builder()
        .user_agent("tracera-ingest/0.1 (github.com/KooshaPari/Tracera)")
        .build()
        .map_err(|e| IngestError::Fetch(e.to_string()))?;

    let url = format!("{}/api/agents", cfg.base_url);
    let resp = client
        .get(&url)
        .header("Accept", "application/json")
        .send()
        .await
        .map_err(|e| IngestError::Fetch(format!("AgCord agents HTTP error: {e}")))?;

    if !resp.status().is_success() {
        let status = resp.status();
        let body = resp.text().await.unwrap_or_default();
        return Err(IngestError::Fetch(format!(
            "AgCord /api/agents returned {status}: {body}"
        )));
    }

    let items: Vec<Value> = resp
        .json()
        .await
        .map_err(|e| IngestError::Fetch(format!("AgCord agents JSON decode: {e}")))?;

    let issues = items
        .into_iter()
        .filter_map(|v| {
            let id = v.get("id")?.as_str()?.to_string();
            let name = v.get("name")?.as_str()?.to_string();
            let agent_type = v
                .get("type")
                .and_then(|t| t.as_str())
                .unwrap_or("unknown")
                .to_string();
            let status = v
                .get("status")
                .and_then(|s| s.as_str())
                .unwrap_or("unknown")
                .to_string();
            let capabilities = v
                .get("capabilities")
                .and_then(|c| c.as_array())
                .map(|arr| {
                    arr.iter()
                        .filter_map(|v| v.as_str())
                        .collect::<Vec<_>>()
                        .join(", ")
                })
                .unwrap_or_default();
            let body = format!("type={agent_type}; status={status}; capabilities={capabilities}");
            Some(NormalisedIssue {
                external_id: format!("agcord-agent-{id}"),
                title: format!("[agent] {name}"),
                body,
                url: format!("{}/api/agents", cfg.base_url),
                status,
                source: "agcord".to_string(),
            })
        })
        .collect();

    Ok(issues)
}

/// Fetch tasks from AgCord's `/api/tasks` endpoint.
///
/// AgCord tasks represent work items with priority, assignment, and status.
/// Each task is normalised into a `NormalisedIssue` with source="agcord".
///
/// // wraps: reqwest 0.13
pub async fn fetch_agcord_tasks(cfg: &AgcordConfig) -> Result<Vec<NormalisedIssue>, IngestError> {
    let client = reqwest::Client::builder()
        .user_agent("tracera-ingest/0.1 (github.com/KooshaPari/Tracera)")
        .build()
        .map_err(|e| IngestError::Fetch(e.to_string()))?;

    let url = format!("{}/api/tasks", cfg.base_url);
    let resp = client
        .get(&url)
        .header("Accept", "application/json")
        .send()
        .await
        .map_err(|e| IngestError::Fetch(format!("AgCord tasks HTTP error: {e}")))?;

    if !resp.status().is_success() {
        let status = resp.status();
        let body = resp.text().await.unwrap_or_default();
        return Err(IngestError::Fetch(format!(
            "AgCord /api/tasks returned {status}: {body}"
        )));
    }

    let items: Vec<Value> = resp
        .json()
        .await
        .map_err(|e| IngestError::Fetch(format!("AgCord tasks JSON decode: {e}")))?;

    let issues = items
        .into_iter()
        .filter_map(|v| {
            let id = v.get("id")?.as_str()?.to_string();
            let name = v.get("name")?.as_str()?.to_string();
            let _description = v
                .get("description")
                .and_then(|d| d.as_str())
                .unwrap_or("")
                .to_string();
            let priority = v
                .get("priority")
                .and_then(|p| p.as_str())
                .unwrap_or("medium")
                .to_string();
            let status = v
                .get("status")
                .and_then(|s| s.as_str())
                .unwrap_or("pending")
                .to_string();
            let assigned = v
                .get("assignedAgent")
                .and_then(|a| a.as_str())
                .unwrap_or("")
                .to_string();
            let body = format!("priority={priority}; status={status}; assigned={assigned}");
            Some(NormalisedIssue {
                external_id: format!("agcord-task-{id}"),
                title: format!("[task] {name}"),
                body,
                url: format!("{}/api/tasks", cfg.base_url),
                status,
                source: "agcord".to_string(),
            })
        })
        .collect();

    Ok(issues)
}
