//! SDLC observability: events, stage tracking, and the in-process event bus.
//!
//! This module is the "nervous system" of Atlas. Every state change anywhere
//! in the crate is funnelled through `publish` on the shared event bus, which
//! fans out to:
//!
//! 1. **Subscribers** (`EventSubscriber` implementations) — typically used to
//!    bridge into OpenTelemetry, write to a JSON log file, or push to a SIEM.
//! 2. The `tracing` macros at the call sites — so the structured fields end
//!    up in whatever subscriber chain is wired up by the host binary.
//! 3. The `RecordingSink` test helper — so unit tests can assert that the
//!    right events fired in the right order.
//!
//! The event bus is intentionally lock-free with respect to subscribers
//! (subscriber registration uses a `Mutex<Vec<…>>`; publishing only takes a
//! read-lock to clone the subscriber list). This keeps `publish` cheap enough
//! to call on every state transition without affecting hot-path performance.

use chrono::{DateTime, Utc};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use std::any::Any;
use std::sync::{Arc, Mutex};
use tracing::{debug, info};
use uuid::Uuid;

use crate::delegation::{AgentId, WorkItem, WorkItemId};

// ---------- Stages ----------

/// Higher-level SDLC stage carried alongside the operational [`WorkItemStatus`].
///
/// `SdlcStage` is intentionally redundant with `WorkItemStatus` so that
/// downstream consumers (dashboards, exports) can rely on a stable,
/// stringly-typed vocabulary without having to depend on the internal
/// `delegation` module's enum.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SdlcStage {
    /// Created but not yet claimed.
    Ready,
    /// Actively being worked on.
    InProgress,
    /// Awaiting human or peer review.
    Review,
    /// Done — signed off.
    Done,
    /// Blocked on external input.
    Blocked,
    /// Cancelled before completion.
    Cancelled,
}

impl SdlcStage {
    /// Stable string tag suitable for JSON export or metric labels.
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Ready => "ready",
            Self::InProgress => "in_progress",
            Self::Review => "review",
            Self::Done => "done",
            Self::Blocked => "blocked",
            Self::Cancelled => "cancelled",
        }
    }
}

impl std::fmt::Display for SdlcStage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(self.as_str())
    }
}

impl From<crate::delegation::WorkItemStatus> for SdlcStage {
    fn from(status: crate::delegation::WorkItemStatus) -> Self {
        status.stage()
    }
}

// ---------- Stage log ----------

/// One entry in a work item's append-only stage log.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct StageLogEntry {
    /// Stage we transitioned away from (`None` for the initial entry).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub from: Option<SdlcStage>,
    /// Stage we transitioned to.
    pub to: SdlcStage,
    /// Wall-clock timestamp of the transition.
    pub at: DateTime<Utc>,
    /// Optional human-readable note attached to the transition.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
}

/// Append-only list of stage transitions for a `WorkItem`.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct StageLog {
    /// Stage transition entries in chronological order.
    pub entries: Vec<StageLogEntry>,
}

impl StageLog {
    /// Build a new stage log seeded with the initial stage entry.
    #[must_use]
    pub fn initial(stage: SdlcStage, at: DateTime<Utc>) -> Self {
        Self {
            entries: vec![StageLogEntry {
                from: None,
                to: stage,
                at,
                note: None,
            }],
        }
    }
}

// ---------- Event kinds ----------

/// Discrete kinds of SDLC events that flow over the event bus.
///
/// Adding a new variant is an API change: downstream subscribers will
/// receive a payload they don't know how to render. The variants here are
/// intentionally narrow — every state transition in [`crate::delegation`]
/// maps to exactly one of them.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum SdlcEventKind {
    /// A work item was created (initial entry into the system).
    WorkItemCreated,
    /// A work item transitioned to `InProgress` (assignment or restart).
    WorkItemTransition {
        /// Logical transition kind, kept simple for downstream filtering.
        kind: TransitionKind,
    },
    /// An agent was assigned or reassigned to a work item.
    Assigned {
        /// The agent id, captured at event time.
        agent: AgentId,
    },
    /// The assigned agent acknowledged start of work.
    Started {
        /// The agent id.
        agent: AgentId,
    },
    /// The work item entered review.
    ReviewSubmitted,
    /// The work item was approved and reached `Done`.
    Approved {
        /// The reviewer (signer) id.
        reviewer: AgentId,
    },
    /// The work item was blocked.
    Blocked,
    /// The work item was cancelled.
    Cancelled,
    /// An out-of-band change was recorded against a work item
    /// (used by the agent-of-record audit log).
    ChangeRecorded,
    /// A sign-off was recorded by a distinct actor.
    SignOffRecorded {
        /// The signer id.
        signer: AgentId,
    },
    /// A CI run completed and was ingested by the CI bridge.
    CiRunCompleted {
        /// The provider that emitted the event (e.g. `github_actions`).
        provider: String,
        /// Stable run id, when the provider supplies one.
        run_id: Option<String>,
        /// Outcome reported by the provider (`success`, `failure`, …).
        outcome: String,
    },
    /// A new SDLC event kind was added that this consumer does not know
    /// how to interpret. Reserved for forward-compatibility — never
    /// produced by the crate itself.
    #[serde(other)]
    Unknown,
}

/// Sub-classification of `WorkItemTransition` events.
///
/// The full transition log lives on `WorkItem.stage_log`; this enum only
/// carries the bits subscribers most often filter on.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TransitionKind {
    /// Generic transition; no specialised handling needed.
    Generic,
    /// Back to ready after being unblocked.
    Reopened,
    /// Submitted for review.
    SubmitForReview,
    /// Move out of `Review` back to `InProgress` (review requested changes).
    ReviewToInProgress,
}

impl TransitionKind {
    /// Stable string tag.
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Generic => "generic",
            Self::Reopened => "reopened",
            Self::SubmitForReview => "submit_for_review",
            Self::ReviewToInProgress => "review_to_in_progress",
        }
    }
}

// ---------- Events ----------

/// A single SDLC event.
///
/// `SdlcEvent` is `Clone` and cheaply so — every field is either an owned
/// string, an enum, or a `chrono::DateTime` (POD).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SdlcEvent {
    /// Unique event id (UUIDv4).
    pub id: Uuid,
    /// Work item this event pertains to.
    pub work_item_id: WorkItemId,
    /// Stage of the work item at the moment the event was emitted
    /// (post-transition).
    pub stage: SdlcStage,
    /// Wall-clock timestamp of the event.
    pub at: DateTime<Utc>,
    /// Event payload.
    pub kind: SdlcEventKind,
    /// Free-form key/value tags for routing / filtering.
    #[serde(default)]
    pub tags: IndexMap<String, String>,
}

impl SdlcEvent {
    /// Construct a new event with the given kind against a work item.
    #[must_use]
    pub fn new(work_item: &WorkItem, kind: SdlcEventKind) -> Self {
        Self {
            id: Uuid::new_v4(),
            work_item_id: work_item.id.clone(),
            stage: work_item.stage,
            at: Utc::now(),
            kind,
            tags: IndexMap::new(),
        }
    }

    /// Attach a tag to this event.
    pub fn with_tag(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.tags.insert(key.into(), value.into());
        self
    }

    /// Helper: build a `WorkItemCreated` event for a freshly minted work item.
    pub fn work_item_created(work_item: &WorkItem) -> Self {
        let mut e = Self::new(work_item, SdlcEventKind::WorkItemCreated);
        e.tags.insert("title".into(), work_item.title.clone());
        e
    }

    /// Helper: build an `Assigned` event.
    pub fn work_item_assigned(work_item: &WorkItem, agent: &AgentId) -> Self {
        Self::new(
            work_item,
            SdlcEventKind::Assigned {
                agent: agent.clone(),
            },
        )
    }

    /// Helper: build a `Started` event.
    pub fn work_item_started(work_item: &WorkItem, agent: &AgentId) -> Self {
        Self::new(
            work_item,
            SdlcEventKind::Started {
                agent: agent.clone(),
            },
        )
    }

    /// Helper: build a generic transition event of the given kind.
    pub fn work_item_transition(work_item: &WorkItem, kind: SdlcEventKind) -> Self {
        Self::new(work_item, kind)
    }

    /// Helper: build an `Approved` event.
    pub fn work_item_approved(work_item: &WorkItem, reviewer: &AgentId) -> Self {
        Self::new(
            work_item,
            SdlcEventKind::Approved {
                reviewer: reviewer.clone(),
            },
        )
    }
}

// ---------- Subscriber trait + sink ----------

/// Trait implemented by anything that wants to receive SDLC events.
///
/// Subscribers are stored as `Arc<dyn EventSubscriber>` so a single
/// subscriber can be shared across multiple buses if needed.
pub trait EventSubscriber: Send + Sync + std::fmt::Debug + Any {
    /// Deliver an event to this subscriber.
    ///
    /// Implementations should not block for long — the event bus holds a
    /// read-lock while iterating subscribers, so a slow subscriber will
    /// stall every subsequent `publish` call. If you need to do real I/O,
    /// hand off to a channel and return immediately.
    fn on_event(&self, event: &SdlcEvent);

    /// Test-only hook: downcast to `&dyn Any` for inspection in tests.
    /// Default returns `None`; only `RecordingSink` overrides it.
    fn as_any(&self) -> Option<&dyn Any> {
        None
    }
}

/// The internal event-sink seam shared between `DelegationStore` and
/// `AtlasEngine`. The `EventBus` trait abstracts over the implementation
/// (in-memory now, pluggable to other backends later).
pub trait EventBus: Send + Sync + std::fmt::Debug {
    /// Publish an event to all current subscribers.
    fn publish(&self, event: SdlcEvent);

    /// Register a new subscriber; returns a token that can be used to
    /// identify the subscription.
    fn subscribe(&self, subscriber: Arc<dyn EventSubscriber>) -> Uuid;

    /// Number of currently registered subscribers.
    fn subscriber_count(&self) -> usize;
}

/// In-memory `EventBus` implementation. Cheap to clone (internal `Arc`).
#[derive(Clone, Debug)]
pub struct InMemoryEventBus {
    inner: Arc<Mutex<BusInner>>,
}

#[derive(Debug)]
struct BusInner {
    subscribers: IndexMap<Uuid, Arc<dyn EventSubscriber>>,
}

impl Default for InMemoryEventBus {
    fn default() -> Self {
        Self {
            inner: Arc::new(Mutex::new(BusInner {
                subscribers: IndexMap::new(),
            })),
        }
    }
}

impl InMemoryEventBus {
    /// Construct a new empty bus.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Register a subscriber. Returns the subscription id.
    pub fn subscribe(&self, subscriber: Arc<dyn EventSubscriber>) -> Uuid {
        let id = Uuid::new_v4();
        let mut guard = self.inner.lock().expect("event bus poisoned");
        guard.subscribers.insert(id, subscriber);
        id
    }

    /// Remove a subscriber by id. No-op if the id is unknown.
    pub fn unsubscribe(&self, id: Uuid) -> bool {
        let mut guard = self.inner.lock().expect("event bus poisoned");
        guard.subscribers.shift_remove(&id).is_some()
    }

    /// Current subscriber count.
    pub fn subscriber_count(&self) -> usize {
        self.inner
            .lock()
            .map(|g| g.subscribers.len())
            .unwrap_or_default()
    }

    /// Publish an event to every current subscriber. Locks the subscriber
    /// list briefly to clone, then drops the lock before dispatching — so a
    /// subscriber that panics or blocks does not stall other subscribers.
    pub fn publish(&self, event: SdlcEvent) {
        let subscribers: Vec<Arc<dyn EventSubscriber>> = self
            .inner
            .lock()
            .map(|g| g.subscribers.values().cloned().collect())
            .unwrap_or_default();
        for s in &subscribers {
            // Swallow panics: a misbehaving subscriber must not bring down
            // the entire engine. The `tracing` layer below still records
            // the event regardless.
            let res = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                s.on_event(&event);
            }));
            if res.is_err() {
                tracing::error!(subscriber = ?s, "event subscriber panicked");
            }
        }
        // Always emit a tracing event so the host's log subscriber sees it.
        match &event.kind {
            SdlcEventKind::CiRunCompleted { provider, outcome, .. } => {
                info!(
                    event_id = %event.id,
                    work_item_id = %event.work_item_id,
                    stage = %event.stage,
                    provider = %provider,
                    outcome = %outcome,
                    "sdlc_event"
                );
            }
            SdlcEventKind::Assigned { agent }
            | SdlcEventKind::Started { agent }
            | SdlcEventKind::SignOffRecorded { signer: agent } => {
                info!(
                    event_id = %event.id,
                    work_item_id = %event.work_item_id,
                    stage = %event.stage,
                    agent = %agent,
                    kind = ?event.kind,
                    "sdlc_event"
                );
            }
            SdlcEventKind::Approved { reviewer } => {
                info!(
                    event_id = %event.id,
                    work_item_id = %event.work_item_id,
                    stage = %event.stage,
                    reviewer = %reviewer,
                    "sdlc_event"
                );
            }
            _ => {
                debug!(
                    event_id = %event.id,
                    work_item_id = %event.work_item_id,
                    stage = %event.stage,
                    kind = ?event.kind,
                    "sdlc_event"
                );
            }
        }
    }
}

impl EventBus for InMemoryEventBus {
    fn publish(&self, event: SdlcEvent) {
        // Use UFCS to disambiguate from the trait method we're implementing.
        InMemoryEventBus::publish(self, event);
    }

    fn subscribe(&self, subscriber: Arc<dyn EventSubscriber>) -> Uuid {
        InMemoryEventBus::subscribe(self, subscriber)
    }

    fn subscriber_count(&self) -> usize {
        InMemoryEventBus::subscriber_count(self)
    }
}

// ---------- Test sink ----------

/// `EventSubscriber` that records every event it receives, for use in tests.
///
/// `RecordingSink` is exported because both `lib.rs` and the integration
/// tests want to assert against the recorded events.
#[derive(Debug, Default)]
pub struct RecordingSink {
    events: Mutex<Vec<SdlcEvent>>,
}

impl RecordingSink {
    /// Create an empty recording sink.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Snapshot the events received so far.
    #[must_use]
    pub fn snapshot(&self) -> Vec<SdlcEvent> {
        self.events
            .lock()
            .map(|g| g.clone())
            .unwrap_or_default()
    }

    /// Number of events received.
    #[must_use]
    pub fn len(&self) -> usize {
        self.events.lock().map(|g| g.len()).unwrap_or_default()
    }

    /// Whether the sink has received zero events.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Drop all recorded events.
    pub fn clear(&self) {
        if let Ok(mut g) = self.events.lock() {
            g.clear();
        }
    }
}

impl EventSubscriber for RecordingSink {
    fn on_event(&self, event: &SdlcEvent) {
        if let Ok(mut g) = self.events.lock() {
            g.push(event.clone());
        }
    }

    fn as_any(&self) -> Option<&dyn Any> {
        Some(self)
    }
}

// ---------- Tests ----------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stage_string_round_trip() {
        for stage in [
            SdlcStage::Ready,
            SdlcStage::InProgress,
            SdlcStage::Review,
            SdlcStage::Done,
            SdlcStage::Blocked,
            SdlcStage::Cancelled,
        ] {
            let json = serde_json::to_string(&stage).unwrap();
            let back: SdlcStage = serde_json::from_str(&json).unwrap();
            assert_eq!(back, stage);
        }
    }

    #[test]
    fn stage_log_records_initial_entry() {
        let now = Utc::now();
        let log = StageLog::initial(SdlcStage::Ready, now);
        assert_eq!(log.entries.len(), 1);
        assert_eq!(log.entries[0].to, SdlcStage::Ready);
        assert!(log.entries[0].from.is_none());
    }

    #[test]
    fn subscribers_receive_published_events() {
        let bus = InMemoryEventBus::default();
        let sink = Arc::new(RecordingSink::default());
        let _id = bus.subscribe(sink.clone());
        let work = WorkItem {
            id: WorkItemId::new(),
            title: "x".into(),
            description: None,
            status: crate::delegation::WorkItemStatus::Ready,
            stage: SdlcStage::Ready,
            assigned_agent: None,
            created_by: None,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            tags: vec![],
            stage_log: StageLog::initial(SdlcStage::Ready, Utc::now()),
        };
        let event = SdlcEvent::work_item_created(&work);
        bus.publish(event.clone());
        let recorded = sink.snapshot();
        assert_eq!(recorded.len(), 1);
        assert_eq!(recorded[0].id, event.id);
    }

    #[test]
    fn unsubscribe_stops_delivery() {
        let bus = InMemoryEventBus::default();
        let sink = Arc::new(RecordingSink::default());
        let id = bus.subscribe(sink.clone());
        assert_eq!(bus.subscriber_count(), 1);
        assert!(bus.unsubscribe(id));
        assert_eq!(bus.subscriber_count(), 0);
        // Publishing after unsubscribe must not panic.
        let event = SdlcEvent {
            id: Uuid::new_v4(),
            work_item_id: WorkItemId::new(),
            stage: SdlcStage::Ready,
            at: Utc::now(),
            kind: SdlcEventKind::WorkItemCreated,
            tags: IndexMap::new(),
        };
        bus.publish(event);
        assert!(sink.is_empty());
    }

    #[test]
    fn panicking_subscriber_does_not_break_publish() {
        let bus = InMemoryEventBus::default();

        #[derive(Debug)]
        struct Panic;
        impl EventSubscriber for Panic {
            fn on_event(&self, _: &SdlcEvent) {
                panic!("nope");
            }
        }

        let good = Arc::new(RecordingSink::default());
        bus.subscribe(Arc::new(Panic));
        bus.subscribe(good.clone());

        let event = SdlcEvent {
            id: Uuid::new_v4(),
            work_item_id: WorkItemId::new(),
            stage: SdlcStage::Ready,
            at: Utc::now(),
            kind: SdlcEventKind::WorkItemCreated,
            tags: IndexMap::new(),
        };
        // Should not panic — the bad subscriber is isolated.
        bus.publish(event);
        // The good subscriber still received the event.
        assert_eq!(good.len(), 1);
    }

    #[test]
    fn sdlc_event_with_tags_serializes() {
        let event = SdlcEvent {
            id: Uuid::new_v4(),
            work_item_id: WorkItemId::new(),
            stage: SdlcStage::Ready,
            at: Utc::now(),
            kind: SdlcEventKind::Approved {
                reviewer: AgentId::new("koosh"),
            },
            tags: IndexMap::from([("env".into(), "test".into())]),
        };
        let json = serde_json::to_string(&event).unwrap();
        let back: SdlcEvent = serde_json::from_str(&json).unwrap();
        assert_eq!(back.tags.get("env").map(String::as_str), Some("test"));
    }
}
