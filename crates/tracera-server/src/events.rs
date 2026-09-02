//! Event ingestion pipeline for memory distillation.
//!
//! Receives CI events, governance events, and code events,
//! normalises them into graph nodes/edges, and feeds them
//! into the distillation pipeline.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Types of events that can be ingested.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    CiRun,
    TestResult,
    CoverageChange,
    AdrCreated,
    SpecChange,
    Commit,
    PullRequest,
    Review,
    Deployment,
    Incident,
}

/// A raw event from any source.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RawEvent {
    pub event_type: EventType,
    pub source: String,
    pub payload: Value,
    pub timestamp: DateTime<Utc>,
}

/// Normalised event ready for graph ingestion.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NormalisedEvent {
    pub id: String,
    pub event_type: EventType,
    pub node_type: String,
    pub label: String,
    pub metadata: Value,
    pub source_refs: Vec<String>,
    pub timestamp: DateTime<Utc>,
}

/// Normalize a raw event into graph-ready form.
pub fn normalize_event(event: &RawEvent) -> NormalisedEvent {
    let id = format!("evt-{}", uuid::Uuid::new_v4());
    let (node_type, label) = match &event.event_type {
        EventType::CiRun => ("build".to_string(), event.payload["name"].as_str().unwrap_or("CI run").to_string()),
        EventType::TestResult => ("test".to_string(), event.payload["test_name"].as_str().unwrap_or("test").to_string()),
        EventType::CoverageChange => ("metric".to_string(), format!("coverage {}%", event.payload["coverage"].as_f64().unwrap_or(0.0))),
        EventType::AdrCreated => ("specification".to_string(), event.payload["title"].as_str().unwrap_or("ADR").to_string()),
        EventType::SpecChange => ("specification".to_string(), event.payload["title"].as_str().unwrap_or("spec").to_string()),
        EventType::Commit => ("commit".to_string(), event.payload["message"].as_str().unwrap_or("commit").to_string()),
        EventType::PullRequest => ("pull_request".to_string(), event.payload["title"].as_str().unwrap_or("PR").to_string()),
        EventType::Review => ("evidence".to_string(), format!("review by {}", event.payload["reviewer"].as_str().unwrap_or("unknown"))),
        EventType::Deployment => ("deployment".to_string(), event.payload["environment"].as_str().unwrap_or("prod").to_string()),
        EventType::Incident => ("incident".to_string(), event.payload["title"].as_str().unwrap_or("incident").to_string()),
    };
    
    let source_refs = event.payload["refs"].as_array()
        .map(|a| a.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_default();
    
    NormalisedEvent {
        id,
        event_type: event.event_type.clone(),
        node_type,
        label,
        metadata: event.payload.clone(),
        source_refs,
        timestamp: event.timestamp,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn normalize_ci_run_event() {
        let event = RawEvent {
            event_type: EventType::CiRun,
            source: "github-actions".to_string(),
            payload: serde_json::json!({"name": "build-and-test"}),
            timestamp: Utc::now(),
        };
        let normalised = normalize_event(&event);
        assert_eq!(normalised.node_type, "build");
        assert_eq!(normalised.label, "build-and-test");
    }
    
    #[test]
    fn normalize_commit_event() {
        let event = RawEvent {
            event_type: EventType::Commit,
            source: "git".to_string(),
            payload: serde_json::json!({"message": "feat: add SWEE graph"}),
            timestamp: Utc::now(),
        };
        let normalised = normalize_event(&event);
        assert_eq!(normalised.node_type, "commit");
        assert!(normalised.label.contains("SWEE"));
    }
}
