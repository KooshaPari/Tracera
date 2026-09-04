//! In-process event bus backing the `graph_events` subscription.
//!
//! Events flow through a bounded Tokio broadcast channel. Subscribers
//! receive:
//!   - node created/updated
//!   - edge created/updated
//!   - raw events normalised by the server (`tracera_server::events`)
//!
//! The channel is process-local: in production the gateway shares the
//! server's Postgres/SQLite store, but events for live subscribers are
//! published through this in-memory bus to keep the binary standalone.

use async_graphql::{InputObject, SimpleObject, Union};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value as JsonValue;
use tokio::sync::broadcast;
use uuid::Uuid;

use crate::resolvers::edge::EdgeKind;
use crate::resolvers::node::NodeKind;

/// All event variants broadcast on `graph_events`.
#[derive(Union, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "GraphEvent")]
pub enum GraphEvent {
    NodeCreated(NodeCreatedEvent),
    NodeUpdated(NodeUpdatedEvent),
    EdgeCreated(EdgeCreatedEvent),
    EdgeUpdated(EdgeUpdatedEvent),
    DomainEvent(DomainEvent),
}

#[derive(async_graphql::SimpleObject, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "NodeCreatedEvent")]
pub struct NodeCreatedEvent {
    pub id: String,
    pub node_type: NodeKind,
    pub label: String,
    pub metadata: JsonValue,
    pub at: DateTime<Utc>,
}

#[derive(async_graphql::SimpleObject, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "NodeUpdatedEvent")]
pub struct NodeUpdatedEvent {
    pub id: String,
    pub node_type: NodeKind,
    pub label: String,
    pub metadata: JsonValue,
    pub at: DateTime<Utc>,
}

#[derive(async_graphql::SimpleObject, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "EdgeCreatedEvent")]
pub struct EdgeCreatedEvent {
    pub id: String,
    pub edge_type: EdgeKind,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    pub at: DateTime<Utc>,
}

#[derive(async_graphql::SimpleObject, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "EdgeUpdatedEvent")]
pub struct EdgeUpdatedEvent {
    pub id: String,
    pub edge_type: EdgeKind,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    pub at: DateTime<Utc>,
}

/// A domain event from the server's ingestion pipeline (`tracera_server::events`).
///
/// Mirrors the `EventType` enum from the server (CI run, test result,
/// coverage change, ADR, spec change, commit, PR, review, deployment,
/// incident). Stringified so the gateway stays decoupled from the
/// server crate.
#[derive(async_graphql::SimpleObject, Clone, Debug, Serialize, Deserialize)]
#[graphql(name = "DomainEvent")]
pub struct DomainEvent {
    pub id: String,
    /// `"ci_run" | "test_result" | "coverage_change" | "adr_created" | "spec_change" |
    ///  "commit" | "pull_request" | "review" | "deployment" | "incident"`
    pub event_type: String,
    pub source: String,
    pub payload: JsonValue,
    pub timestamp: DateTime<Utc>,
}

/// Lightweight filter accepted by the `graph_events` subscription.
///
/// All fields are optional; an empty filter streams every event.
#[derive(async_graphql::InputObject, Clone, Debug, Default)]
pub struct GraphEventFilter {
    #[graphql(default)]
    pub node_type: Option<NodeKind>,
    #[graphql(default)]
    pub edge_type: Option<EdgeKind>,
    #[graphql(default)]
    pub domain_event_type: Option<String>,
}

// ---------------------------------------------------------------------------
// Bus — process-local broadcast with bounded capacity.
// ---------------------------------------------------------------------------

const DEFAULT_CHANNEL_CAPACITY: usize = 1024;

/// In-process broadcast bus.
#[derive(Clone)]
pub struct GraphEventBus {
    sender: broadcast::Sender<GraphEvent>,
}

impl Default for GraphEventBus {
    fn default() -> Self {
        Self::new(DEFAULT_CHANNEL_CAPACITY)
    }
}

impl GraphEventBus {
    pub fn new(capacity: usize) -> Self {
        let (sender, _) = broadcast::channel(capacity.max(1));
        Self { sender }
    }

    /// Subscribe to live events. Returns a `broadcast::Receiver` that yields
    /// `RecvError::Lagged` if the subscriber falls behind.
    pub fn subscribe(&self) -> broadcast::Receiver<GraphEvent> {
        self.sender.subscribe()
    }

    pub fn publish(&self, event: GraphEvent) {
        // `send` only fails if there are no active subscribers; that's fine.
        let _ = self.sender.send(event);
    }

    /// Number of currently subscribed listeners.
    pub fn subscriber_count(&self) -> usize {
        self.sender.receiver_count()
    }

    // Convenience publishers — used by the mutation roots so the schema
    // stays readable.

    pub fn publish_node_created(
        &self,
        node_type: NodeKind,
        label: String,
        metadata: JsonValue,
    ) {
        self.publish(GraphEvent::NodeCreated(NodeCreatedEvent {
            id: format!("evt-{}", Uuid::new_v4()),
            node_type,
            label,
            metadata,
            at: Utc::now(),
        }));
    }

    pub fn publish_edge_created(
        &self,
        edge_type: EdgeKind,
        source_id: String,
        target_id: String,
        confidence: f64,
    ) {
        self.publish(GraphEvent::EdgeCreated(EdgeCreatedEvent {
            id: format!("evt-{}", Uuid::new_v4()),
            edge_type,
            source_id,
            target_id,
            confidence,
            at: Utc::now(),
        }));
    }

    pub fn publish_domain(
        &self,
        event_type: String,
        source: String,
        payload: JsonValue,
        timestamp: DateTime<Utc>,
    ) {
        self.publish(GraphEvent::DomainEvent(DomainEvent {
            id: format!("evt-{}", Uuid::new_v4()),
            event_type,
            source,
            payload,
            timestamp,
        }));
    }
}


