//! TRC-PHENO-007: Trace export (JSON / YAML).
//!
//! Port of phenodag's cmdExport. Serialises a snapshot of the queue state.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskSnapshot {
    pub id: String,
    pub status: String,
    pub assigned_agent: Option<String>,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentSnapshot {
    pub id: String,
    pub status: String,
    pub last_heartbeat: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueueSnapshot {
    pub tasks: Vec<TaskSnapshot>,
    pub agents: Vec<AgentSnapshot>,
    pub exported_at: String,
}

pub fn to_json(snap: &QueueSnapshot) -> Result<String, serde_json::Error> {
    serde_json::to_string_pretty(snap)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn roundtrip_json() {
        let s = QueueSnapshot {
            tasks: vec![TaskSnapshot { id: "T1".into(), status: "ready".into(), assigned_agent: None, updated_at: "2026-07-05T00:00:00Z".into() }],
            agents: vec![],
            exported_at: "2026-07-05T00:00:00Z".into(),
        };
        let j = to_json(&s).unwrap();
        let back: QueueSnapshot = serde_json::from_str(&j).unwrap();
        assert_eq!(back.tasks.len(), 1);
        assert_eq!(back.tasks[0].id, "T1");
    }
}
