//! # Tracera Atlas — ALM engine
//!
//! Atlas is the Application Lifecycle Management layer for Tracera. It owns
//! the cross-cutting bookkeeping that the rest of the platform needs in order
//! to answer two questions:
//!
//! 1. **Who is doing what right now?** — [`delegation`] turns `WorkItem`s into
//!    agent assignments, and tracks the lifecycle (`ready → in_progress →
//!    review → done`).
//! 2. **Who did what, and who signed off on it?** — [`agent_of_record`] is an
//!    append-only log of every mutation, plus an explicit sign-off record.
//!
//! On top of those two primitives, [`observability`] publishes SDLC events
//! (state transitions, sign-offs, CI run outcomes) into the [`tracing`]
//! ecosystem, and [`ci_bridge`] normalises incoming GitHub Actions webhook
//! payloads into the same SDLC event vocabulary.
//!
//! The crate is intentionally *transport-agnostic*: persistence is optional
//! and pluggable via the `persist-sqlite` / `persist-postgres` Cargo features,
//! and the HTTP surface in [`src/bin/atlas-server.rs`] is gated behind the
//! `server` feature. This lets the same engine power embedded callers, CLI
//! tools, and daemon deployments without modification.
//!
//! ## Quick start
//!
//! ```
//! use tracera_atlas::{AtlasEngine, SdlcStage};
//!
//! let engine = AtlasEngine::in_memory();
//! let item = engine.delegation()
//!     .create_work("ship MVP", SdlcStage::Ready)
//!     .unwrap();
//! let assigned = engine.delegation()
//!     .assign(&item.id, "agent-7")
//!     .unwrap();
//! assert_eq!(assigned.assigned_agent.as_deref(), Some("agent-7"));
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]

pub mod agent_of_record;
pub mod ci_bridge;
pub mod delegation;
pub mod observability;

pub use agent_of_record::{ActorId, AgentOfRecord, AoRQuery, ChangeKind, SignOff, SignOffId};
pub use ci_bridge::{
    publish_ci_event, CiBridge, CiEventError, CiEventKind, CiProvider, CiProviderAdapter,
    GitHubActionsEvent, NormalizedCiEvent,
};
pub use delegation::{
    AgentAssignment, AgentId, AssignmentOutcome, Delegation, DelegationError, WorkItem,
    WorkItemId, WorkItemStatus, WorkItemSummary,
};
pub use observability::{
    EventBus, EventSubscriber, InMemoryEventBus, SdlcEvent, SdlcEventKind, SdlcStage, StageLog,
};

use std::sync::Arc;

/// Top-level façade over the Atlas ALM subsystems.
///
/// `AtlasEngine` is the only type most callers need to interact with. It
/// owns (and shares via interior mutability) a single [`Delegation`] store
/// and an [`EventBus`] used by [`observability`]. Persistence and HTTP
/// wiring are layered on top via the `persist-*` and `server` features.
#[derive(Clone)]
pub struct AtlasEngine {
    inner: Arc<EngineInner>,
}

struct EngineInner {
    delegation: delegation::DelegationStore,
    events: observability::InMemoryEventBus,
}

impl AtlasEngine {
    /// Create an engine backed entirely by in-memory state.
    ///
    /// This is the right choice for tests, CLI one-shot runs, or any
    /// deployment that wants Atlas as a transient coordination layer. To
    /// persist across restarts, enable one of the `persist-*` features and
    /// use the corresponding constructor (e.g. `with_sqlite`).
    #[must_use]
    pub fn in_memory() -> Self {
        let events = InMemoryEventBus::default();
        let delegation = delegation::DelegationStore::with_sink(events.clone());
        Self {
            inner: Arc::new(EngineInner {
                delegation,
                events,
            }),
        }
    }

    /// Access the delegation subsystem (work items + agent assignments).
    #[must_use]
    pub fn delegation(&self) -> Delegation<'_> {
        Delegation::new(&self.inner.delegation)
    }

    /// Access the agent-of-record subsystem (audit log + sign-offs).
    #[must_use]
    pub fn agent_of_record(&self) -> agent_of_record::AgentOfRecord<'_> {
        agent_of_record::AgentOfRecord::new(&self.inner.delegation)
    }

    /// Access the SDLC event bus.
    #[must_use]
    pub fn events(&self) -> &InMemoryEventBus {
        &self.inner.events
    }

    /// Subscribe to SDLC events (stage transitions, sign-offs, CI outcomes).
    pub fn subscribe(&self, subscriber: Arc<dyn EventSubscriber>) -> uuid::Uuid {
        self.inner.events.subscribe(subscriber)
    }

    /// Number of `WorkItem`s currently held by this engine.
    #[must_use]
    pub fn work_item_count(&self) -> usize {
        self.inner.delegation.work_item_count()
    }
}

impl std::fmt::Debug for AtlasEngine {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("AtlasEngine")
            .field("work_items", &self.inner.delegation.work_item_count())
            .finish_non_exhaustive()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn in_memory_engine_round_trip() {
        let engine = AtlasEngine::in_memory();
        let work = engine
            .delegation()
            .create_work("design auth flow", SdlcStage::Ready)
            .expect("create work");
        assert_eq!(work.stage, SdlcStage::Ready);
        assert_eq!(work.status, WorkItemStatus::Ready);

        let assigned = engine
            .delegation()
            .assign(&work.id, "agent-9")
            .expect("assign");
        assert_eq!(assigned.outcome, AssignmentOutcome::Assigned);
        assert_eq!(assigned.work_item.assigned_agent.as_deref(), Some("agent-9"));
        assert_eq!(assigned.work_item.status, WorkItemStatus::InProgress);
    }

    #[test]
    fn event_bus_records_stage_transition() {
        let engine = AtlasEngine::in_memory();
        let bag: Arc<dyn EventSubscriber> = Arc::new(observability::RecordingSink::default());
        let _id = engine.subscribe(bag.clone());

        let work = engine
            .delegation()
            .create_work("ship alpha", SdlcStage::Ready)
            .unwrap();
        engine.delegation().assign(&work.id, "agent-1").unwrap();
        engine.delegation().start(&work.id, "agent-1").unwrap();

        let events = bag
            .as_any()
            .downcast_ref::<observability::RecordingSink>()
            .unwrap()
            .snapshot();
        assert!(events
            .iter()
            .any(|e| matches!(e.kind, SdlcEventKind::Started { .. })));
    }
}
