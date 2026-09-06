//! WorkItem delegation: lifecycle and agent assignment.
//!
//! A `WorkItem` is the atomic unit of work in the SDLC. It moves through
//! a finite state machine — `Ready → InProgress → Review → Done` (or
//! `Blocked` / `Cancelled` terminal variants) — and at any given moment
//! may be assigned to a single `AgentId`. The state machine is intentionally
//! strict: every transition is validated against an explicit allow-list, so
//! callers cannot drive a work item into an unreachable state.
//!
//! All mutations route through the `Delegation` API on top of the
//! shared `DelegationStore`. The store publishes an SDLC event for every
//! transition via the [`EventBus`](crate::observability::EventBus) sink it
//! was constructed with, which keeps audit, observability, and CI bridge
//! subsystems consistent with the actual state.

use chrono::{DateTime, Utc};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use std::sync::RwLock;
use thiserror::Error;
use tracing::{debug, info};
use uuid::Uuid;

use crate::agent_of_record::AoRStore;
use crate::observability::{
    InMemoryEventBus, SdlcEvent, SdlcEventKind, SdlcStage, StageLog, StageLogEntry,
};

// ---------- Public identifiers ----------

/// Stable identifier for a `WorkItem`.
///
/// IDs are UUIDv4 generated at creation time. They are intentionally opaque —
/// callers should not parse them.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct WorkItemId(pub Uuid);

impl WorkItemId {
    /// Create a new work item ID.
    #[must_use]
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for WorkItemId {
    fn default() -> Self {
        Self::new()
    }
}

impl std::fmt::Display for WorkItemId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Identifier for an agent (human, bot, or CI process).
///
/// Atlas deliberately treats humans, AI agents, and CI runners uniformly —
/// each is just an `AgentId` that can claim, progress, and sign off on
/// work items. This matches the Tracera observability model where every
/// actor is recorded with equal fidelity.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct AgentId(pub String);

impl AgentId {
    /// Construct a new agent id, trimming whitespace.
    pub fn new(value: impl Into<String>) -> Self {
        Self(value.into().trim().to_string())
    }

    /// Borrow the underlying string slice.
    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl std::fmt::Display for AgentId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

// ---------- Status / stage enums ----------

/// Coarse lifecycle status of a `WorkItem`.
///
/// `Status` and `SdlcStage` carry overlapping information but serve
/// different consumers: `Status` is the operational state used by the
/// scheduler and CI integration, while `SdlcStage` is the higher-level
/// stage communicated to humans and dashboards.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WorkItemStatus {
    /// Created but not yet claimed by any agent.
    Ready,
    /// Claimed by an agent; agent is actively working on it.
    InProgress,
    /// Agent has finished work; awaiting human/peer sign-off.
    Review,
    /// Signed off and shipped.
    Done,
    /// Cannot proceed without external input.
    Blocked,
    /// Cancelled before completion.
    Cancelled,
}

impl WorkItemStatus {
    /// Whether this status is terminal (no further transitions allowed).
    #[must_use]
    pub fn is_terminal(self) -> bool {
        matches!(self, Self::Done | Self::Cancelled)
    }

    /// Map a status to the matching [`SdlcStage`].
    #[must_use]
    pub fn stage(self) -> SdlcStage {
        match self {
            Self::Ready => SdlcStage::Ready,
            Self::InProgress => SdlcStage::InProgress,
            Self::Review => SdlcStage::Review,
            Self::Done => SdlcStage::Done,
            Self::Blocked => SdlcStage::Blocked,
            Self::Cancelled => SdlcStage::Cancelled,
        }
    }
}

impl From<SdlcStage> for WorkItemStatus {
    fn from(stage: SdlcStage) -> Self {
        match stage {
            SdlcStage::Ready => Self::Ready,
            SdlcStage::InProgress => Self::InProgress,
            SdlcStage::Review => Self::Review,
            SdlcStage::Done => Self::Done,
            SdlcStage::Blocked => Self::Blocked,
            SdlcStage::Cancelled => Self::Cancelled,
        }
    }
}

/// Outcome of an `assign` call.
///
/// `assign` is idempotent for the same agent and is the only entry point
/// for moving a work item from `Ready` to `InProgress`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AssignmentOutcome {
    /// The agent was newly assigned and the work item transitioned to
    /// `InProgress`.
    Assigned,
    /// The work item was already assigned to this agent; no-op.
    AlreadyAssigned,
    /// The work item was reassigned from a different agent.
    Reassigned,
}

// ---------- Core records ----------

/// A unit of work in the SDLC.
///
/// `WorkItem` is `Clone` so it can be returned to callers safely without
/// handing out interior references into the store.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WorkItem {
    /// Stable id.
    pub id: WorkItemId,
    /// Human-readable title (required, non-empty).
    pub title: String,
    /// Optional longer description.
    #[serde(default)]
    pub description: Option<String>,
    /// Current operational status.
    pub status: WorkItemStatus,
    /// Current SDLC stage (kept in sync with `status`).
    pub stage: SdlcStage,
    /// Currently assigned agent, if any.
    pub assigned_agent: Option<AgentId>,
    /// Agent who created the work item, if known.
    #[serde(default)]
    pub created_by: Option<AgentId>,
    /// Wall-clock time at creation.
    pub created_at: DateTime<Utc>,
    /// Most recent update time.
    pub updated_at: DateTime<Utc>,
    /// Tags for routing / filtering.
    #[serde(default)]
    pub tags: Vec<String>,
    /// Append-only log of stage transitions.
    pub stage_log: StageLog,
}

/// Result of an assignment attempt.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AgentAssignment {
    /// The work item after assignment (always returned).
    pub work_item: WorkItem,
    /// The classification of the outcome.
    pub outcome: AssignmentOutcome,
}

/// Summary view of a work item for list endpoints.
///
/// `WorkItemSummary` strips the append-only `stage_log` to keep payload
/// sizes bounded for high-cardinality list responses. Callers that need the
/// full transition history should fetch the underlying [`WorkItem`] by id.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WorkItemSummary {
    /// Work item id.
    pub id: WorkItemId,
    /// Title.
    pub title: String,
    /// Current status.
    pub status: WorkItemStatus,
    /// Current stage.
    pub stage: SdlcStage,
    /// Current assignee, if any.
    pub assigned_agent: Option<AgentId>,
    /// Updated-at timestamp.
    pub updated_at: DateTime<Utc>,
    /// Tag list.
    #[serde(default)]
    pub tags: Vec<String>,
}

impl From<&WorkItem> for WorkItemSummary {
    fn from(item: &WorkItem) -> Self {
        Self {
            id: item.id.clone(),
            title: item.title.clone(),
            status: item.status,
            stage: item.stage,
            assigned_agent: item.assigned_agent.clone(),
            updated_at: item.updated_at,
            tags: item.tags.clone(),
        }
    }
}

// ---------- Errors ----------

/// Errors returned from delegation operations.
#[derive(Debug, Error)]
pub enum DelegationError {
    /// The work item id was not present in the store.
    #[error("work item {0} not found")]
    NotFound(WorkItemId),
    /// Caller attempted a transition that is not allowed from the current state.
    #[error("invalid transition for work item {id}: {from:?} -> {to:?}")]
    InvalidTransition {
        /// The work item id.
        id: WorkItemId,
        /// The state the item was in.
        from: WorkItemStatus,
        /// The state the caller attempted to move to.
        to: WorkItemStatus,
    },
    /// Caller attempted a transition with the wrong actor — i.e. the work
    /// item is assigned to a different agent than the one making the call.
    #[error("actor {actor} is not assigned to work item {id}")]
    WrongActor {
        /// The work item id.
        id: WorkItemId,
        /// The actor that attempted the operation.
        actor: AgentId,
    },
    /// Title was empty after trimming whitespace.
    #[error("work item title must not be empty")]
    EmptyTitle,
    /// The supplied agent id was empty.
    #[error("agent id must not be empty")]
    EmptyAgent,
    /// A conflicting write was detected under the store's interior lock.
    ///
    /// This is only seen in pathological cases (e.g. a poisoned mutex);
    /// most callers will never hit it.
    #[error("internal store lock poisoned")]
    LockPoisoned,
}

impl DelegationError {
    /// Convenience: build a `NotFound` error from any id-like value.
    pub fn not_found(id: &WorkItemId) -> Self {
        Self::NotFound(id.clone())
    }
}

// ---------- Store ----------

/// Internal mutable store backing the `Delegation` API.
///
/// `DelegationStore` is the only component that owns write access to the
/// work item map. It is wrapped in `Arc<RwLock<...>>` so it can be cheaply
/// shared with sibling subsystems (notably the [`agent_of_record`]
/// module, which reads from the same map to thread audit events).
#[derive(Debug)]
pub struct DelegationStore {
    items: RwLock<IndexMap<WorkItemId, WorkItem>>,
    sink: InMemoryEventBus,
    aor: AoRStore,
}

impl DelegationStore {
    /// Construct a store with a fresh empty event bus.
    #[must_use]
    pub fn new() -> Self {
        Self {
            items: RwLock::new(IndexMap::new()),
            sink: InMemoryEventBus::default(),
            aor: AoRStore::new(),
        }
    }

    /// Construct a store wired to the given event bus.
    #[must_use]
    pub fn with_sink(sink: InMemoryEventBus) -> Self {
        Self {
            items: RwLock::new(IndexMap::new()),
            sink,
            aor: AoRStore::new(),
        }
    }

    /// Replace the event sink. Existing subscribers on the previous sink
    /// are not migrated.
    pub fn set_sink(&mut self, sink: InMemoryEventBus) {
        self.sink = sink;
    }

    /// Borrow the shared event sink (cloned, cheap — it's internally
    /// reference-counted).
    #[must_use]
    pub fn sink(&self) -> InMemoryEventBus {
        self.sink.clone()
    }

    /// Borrow the shared agent-of-record store.
    #[must_use]
    pub(crate) fn aor(&self) -> &AoRStore {
        &self.aor
    }

    /// Count of work items currently held.
    pub fn work_item_count(&self) -> usize {
        self.items
            .read()
            .map(|items| items.len())
            .unwrap_or_default()
    }

    /// Fetch a clone of a work item, or `None` if absent.
    pub fn get(&self, id: &WorkItemId) -> Option<WorkItem> {
        self.items.read().ok()?.get(id).cloned()
    }

    /// Iterate summaries of every work item.
    pub fn list_summaries(&self) -> Vec<WorkItemSummary> {
        self.items
            .read()
            .map(|items| items.values().map(WorkItemSummary::from).collect())
            .unwrap_or_default()
    }

    /// Insert or replace a work item. Used by callers restoring from a
    /// persistent store; normal API users should go through
    /// [`Delegation::create_work`].
    pub(crate) fn upsert(&self, item: WorkItem) {
        if let Ok(mut items) = self.items.write() {
            items.insert(item.id.clone(), item);
        }
    }

    /// Apply a closure with mutable access to the matching work item.
    ///
    /// Returns `Ok(WorkItem)` after the closure runs. The closure decides
    /// what the new state should be; the store does *not* re-validate the
    /// transition — that responsibility belongs to the higher-level
    /// `Delegation` API which validates before calling this method.
    pub(crate) fn mutate<F>(&self, id: &WorkItemId, mut f: F) -> Result<WorkItem, DelegationError>
    where
        F: FnMut(&mut WorkItem) -> Result<WorkItem, DelegationError>,
    {
        let mut items = self
            .items
            .write()
            .map_err(|_| DelegationError::LockPoisoned)?;
        let item = items
            .get_mut(id)
            .ok_or_else(|| DelegationError::not_found(id))?;
        f(item)
    }

    /// Record an `SdlcEvent` against the shared sink. Used by `Delegation`
    /// after a successful state change.
    pub(crate) fn record_event(&self, event: SdlcEvent) {
        self.sink.publish(event);
    }
}

impl Default for DelegationStore {
    fn default() -> Self {
        Self::new()
    }
}

// ---------- Public façade ----------

/// Public façade for work-item operations.
///
/// `Delegation` is a thin handle around [`DelegationStore`]; it exists so
/// the public API is owned by `AtlasEngine` while the underlying store can
/// be shared with other subsystems without lifetime gymnastics.
pub struct Delegation<'a> {
    store: &'a DelegationStore,
}

impl<'a> Delegation<'a> {
    /// Create a new `Delegation` view over the store.
    pub(crate) fn new(store: &'a DelegationStore) -> Self {
        Self { store }
    }

    /// Create a new work item in the [`Ready`](WorkItemStatus::Ready) stage.
    pub fn create_work(
        &self,
        title: &str,
        stage: SdlcStage,
    ) -> Result<WorkItem, DelegationError> {
        self.create_work_with(title, stage, None, None)
    }

    /// Create a work item with optional description and creator.
    pub fn create_work_with(
        &self,
        title: &str,
        stage: SdlcStage,
        description: Option<String>,
        created_by: Option<AgentId>,
    ) -> Result<WorkItem, DelegationError> {
        let title = title.trim();
        if title.is_empty() {
            return Err(DelegationError::EmptyTitle);
        }

        let now = Utc::now();
        let status: WorkItemStatus = stage.into();
        let item = WorkItem {
            id: WorkItemId::new(),
            title: title.to_string(),
            description,
            status,
            stage,
            assigned_agent: None,
            created_by,
            created_at: now,
            updated_at: now,
            tags: Vec::new(),
            stage_log: StageLog::initial(stage, now),
        };

        debug!(id = %item.id, title = %item.title, "creating work item");
        self.store.upsert(item.clone());
        self.store.record_event(SdlcEvent::work_item_created(&item));
        Ok(item)
    }

    /// Assign an agent to a work item.
    ///
    /// - If the work item is `Ready`, it transitions to `InProgress` and
    ///   [`AssignmentOutcome::Assigned`] is returned.
    /// - If it is already `InProgress` *and* the same agent is assigned, the
    ///   state is unchanged and [`AssignmentOutcome::AlreadyAssigned`] is
    ///   returned. No event is emitted for the no-op.
    /// - If it is `InProgress` with a *different* agent, the assignment is
    ///   replaced and [`AssignmentOutcome::Reassigned`] is returned. The
    ///   assigned-agent event is emitted but the status stays `InProgress`.
    /// - All other states return [`DelegationError::InvalidTransition`].
    pub fn assign(
        &self,
        id: &WorkItemId,
        agent: &str,
    ) -> Result<AgentAssignment, DelegationError> {
        let agent_id = AgentId::new(agent);
        if agent_id.as_str().is_empty() {
            return Err(DelegationError::EmptyAgent);
        }

        let mut outcome_slot: Option<AssignmentOutcome> = None;
        let item = self.store.mutate(id, |item| {
            match item.status {
                WorkItemStatus::Ready => {
                    transition(item, WorkItemStatus::InProgress)?;
                    item.assigned_agent = Some(agent_id.clone());
                    outcome_slot = Some(AssignmentOutcome::Assigned);
                }
                WorkItemStatus::InProgress => {
                    if item.assigned_agent.as_ref() == Some(&agent_id) {
                        outcome_slot = Some(AssignmentOutcome::AlreadyAssigned);
                    } else {
                        item.assigned_agent = Some(agent_id.clone());
                        outcome_slot = Some(AssignmentOutcome::Reassigned);
                    }
                }
                other => {
                    return Err(DelegationError::InvalidTransition {
                        id: item.id.clone(),
                        from: other,
                        to: WorkItemStatus::InProgress,
                    });
                }
            }
            Ok(item.clone())
        })?;

        let outcome = outcome_slot.unwrap_or(AssignmentOutcome::AlreadyAssigned);
        match outcome {
            AssignmentOutcome::AlreadyAssigned => {
                debug!(%id, agent = %agent_id, "agent already assigned; no-op");
            }
            AssignmentOutcome::Assigned => {
                info!(%id, agent = %agent_id, "work item assigned");
                self.store.record_event(SdlcEvent::work_item_assigned(&item, &agent_id));
            }
            AssignmentOutcome::Reassigned => {
                info!(%id, agent = %agent_id, "work item reassigned");
                self.store.record_event(SdlcEvent::work_item_assigned(&item, &agent_id));
            }
        }

        Ok(AgentAssignment {
            work_item: item,
            outcome,
        })
    }

    /// Mark the assigned agent as having started (status remains `InProgress`,
    /// `updated_at` is bumped). This is a no-op for the state machine itself
    /// but emits a heartbeat event useful for downstream consumers.
    pub fn start(&self, id: &WorkItemId, agent: &str) -> Result<WorkItem, DelegationError> {
        let agent_id = AgentId::new(agent);
        if agent_id.as_str().is_empty() {
            return Err(DelegationError::EmptyAgent);
        }
        let item = self.store.mutate(id, |item| {
            require_status(item, WorkItemStatus::InProgress)?;
            require_assigned_to(item, &agent_id)?;
            item.updated_at = Utc::now();
            Ok(item.clone())
        })?;
        self.store.record_event(SdlcEvent::work_item_started(&item, &agent_id));
        Ok(item)
    }

    /// Move a work item from `InProgress` to `Review`.
    pub fn submit_for_review(
        &self,
        id: &WorkItemId,
        agent: &str,
    ) -> Result<WorkItem, DelegationError> {
        let agent_id = AgentId::new(agent);
        let item = self.store.mutate(id, |item| {
            require_status(item, WorkItemStatus::InProgress)?;
            require_assigned_to(item, &agent_id)?;
            transition(item, WorkItemStatus::Review)?;
            Ok(item.clone())
        })?;
        self.store
            .record_event(SdlcEvent::work_item_transition(&item, SdlcEventKind::ReviewSubmitted));
        Ok(item)
    }

    /// Sign off on a work item in `Review`, moving it to `Done`.
    ///
    /// `reviewer` does NOT need to be the assigned agent — sign-off must be
    /// performed by a distinct actor to enforce two-person integrity. The
    /// detailed audit record (reviewer, sign-off time, optional note) is
    /// written by [`AgentOfRecord::sign_off`](crate::agent_of_record::AgentOfRecord::sign_off);
    /// this method only drives the state machine.
    pub fn approve(
        &self,
        id: &WorkItemId,
        reviewer: &str,
    ) -> Result<WorkItem, DelegationError> {
        let reviewer = AgentId::new(reviewer);
        if reviewer.as_str().is_empty() {
            return Err(DelegationError::EmptyAgent);
        }

        let item = self.store.mutate(id, |item| {
            require_status(item, WorkItemStatus::Review)?;
            transition(item, WorkItemStatus::Done)?;
            Ok(item.clone())
        })?;
        self.store
            .record_event(SdlcEvent::work_item_approved(&item, &reviewer));
        Ok(item)
    }

    /// Mark a work item as blocked (only valid from `InProgress` or `Ready`).
    pub fn block(&self, id: &WorkItemId, reason: &str) -> Result<WorkItem, DelegationError> {
        let item = self.store.mutate(id, |item| {
            match item.status {
                WorkItemStatus::Ready | WorkItemStatus::InProgress | WorkItemStatus::Review => {
                    transition(item, WorkItemStatus::Blocked)?;
                }
                other => {
                    return Err(DelegationError::InvalidTransition {
                        id: item.id.clone(),
                        from: other,
                        to: WorkItemStatus::Blocked,
                    });
                }
            }
            if !reason.is_empty() {
                let note = format!("blocked: {reason}");
                if let Some(last) = item.stage_log.entries.last_mut() {
                    last.note = Some(note);
                }
            }
            Ok(item.clone())
        })?;
        self.store
            .record_event(SdlcEvent::work_item_transition(&item, SdlcEventKind::Blocked));
        Ok(item)
    }

    /// Cancel a work item (allowed from any non-terminal state).
    pub fn cancel(&self, id: &WorkItemId) -> Result<WorkItem, DelegationError> {
        let item = self.store.mutate(id, |item| {
            if item.status.is_terminal() {
                return Err(DelegationError::InvalidTransition {
                    id: item.id.clone(),
                    from: item.status,
                    to: WorkItemStatus::Cancelled,
                });
            }
            transition(item, WorkItemStatus::Cancelled)?;
            Ok(item.clone())
        })?;
        self.store
            .record_event(SdlcEvent::work_item_transition(&item, SdlcEventKind::Cancelled));
        Ok(item)
    }

    /// Read a work item by id.
    pub fn get(&self, id: &WorkItemId) -> Option<WorkItem> {
        self.store.get(id)
    }

    /// List summaries for every work item.
    pub fn list(&self) -> Vec<WorkItemSummary> {
        self.store.list_summaries()
    }

    /// List work items whose `assigned_agent` matches `agent`.
    pub fn list_for_agent(&self, agent: &str) -> Vec<WorkItemSummary> {
        let target = AgentId::new(agent);
        self.store
            .list_summaries()
            .into_iter()
            .filter(|s| s.assigned_agent.as_ref() == Some(&target))
            .collect()
    }
}

// ---------- Helpers ----------

fn transition(item: &mut WorkItem, to: WorkItemStatus) -> Result<(), DelegationError> {
    if !is_valid_transition(item.status, to) {
        return Err(DelegationError::InvalidTransition {
            id: item.id.clone(),
            from: item.status,
            to,
        });
    }
    let now = Utc::now();
    let from = item.status;
    item.status = to;
    item.stage = to.stage();
    item.updated_at = now;
    item.stage_log.entries.push(StageLogEntry {
        from: Some(from.stage()),
        to: to.stage(),
        at: now,
        note: None,
    });
    Ok(())
}

fn require_status(item: &WorkItem, expected: WorkItemStatus) -> Result<(), DelegationError> {
    if item.status != expected {
        return Err(DelegationError::InvalidTransition {
            id: item.id.clone(),
            from: item.status,
            to: expected,
        });
    }
    Ok(())
}

fn require_assigned_to(item: &WorkItem, agent: &AgentId) -> Result<(), DelegationError> {
    match &item.assigned_agent {
        Some(current) if current == agent => Ok(()),
        _ => Err(DelegationError::WrongActor {
            id: item.id.clone(),
            actor: agent.clone(),
        }),
    }
}

/// Pure transition validation, exposed for tests and external callers.
#[must_use]
pub fn is_valid_transition(from: WorkItemStatus, to: WorkItemStatus) -> bool {
    use WorkItemStatus::*;
    matches!(
        (from, to),
        (Ready, InProgress)
            | (Ready, Cancelled)
            | (Ready, Blocked)
            | (InProgress, Review)
            | (InProgress, Blocked)
            | (InProgress, Cancelled)
            | (Review, InProgress)
            | (Review, Done)
            | (Review, Blocked)
            | (Review, Cancelled)
            | (Blocked, Ready)
            | (Blocked, InProgress)
            | (Blocked, Cancelled)
    )
}

// ---------- Tests ----------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::observability::RecordingSink;

    fn fresh_store_with_sink() -> (DelegationStore, std::sync::Arc<RecordingSink>) {
        let sink = std::sync::Arc::new(RecordingSink::default());
        let bus = InMemoryEventBus::default();
        bus.subscribe(sink.clone());
        let store = DelegationStore::with_sink(bus);
        (store, sink)
    }

    #[test]
    fn create_then_get_round_trip() {
        let (store, _sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view
            .create_work("ship MVP", SdlcStage::Ready)
            .expect("create");
        assert_eq!(work.status, WorkItemStatus::Ready);
        let fetched = view.get(&work.id).expect("get");
        assert_eq!(fetched.id, work.id);
    }

    #[test]
    fn empty_title_is_rejected() {
        let (store, _) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let err = view.create_work("   ", SdlcStage::Ready).unwrap_err();
        assert!(matches!(err, DelegationError::EmptyTitle));
    }

    #[test]
    fn assign_transitions_ready_to_in_progress() {
        let (store, sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        let out = view.assign(&work.id, "agent-1").unwrap();
        assert_eq!(out.outcome, AssignmentOutcome::Assigned);
        assert_eq!(out.work_item.status, WorkItemStatus::InProgress);
        assert_eq!(
            out.work_item.assigned_agent.as_ref().unwrap().0,
            "agent-1"
        );

        let events = sink.snapshot();
        assert!(events
            .iter()
            .any(|e| matches!(e.kind, SdlcEventKind::Assigned { .. })));
    }

    #[test]
    fn assign_is_idempotent_for_same_agent() {
        let (store, _sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        let _ = view.assign(&work.id, "agent-1").unwrap();
        let second = view.assign(&work.id, "agent-1").unwrap();
        assert_eq!(second.outcome, AssignmentOutcome::AlreadyAssigned);
    }

    #[test]
    fn assign_reassigns_to_different_agent() {
        let (store, _sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        let _ = view.assign(&work.id, "agent-1").unwrap();
        let second = view.assign(&work.id, "agent-2").unwrap();
        assert_eq!(second.outcome, AssignmentOutcome::Reassigned);
        assert_eq!(
            second.work_item.assigned_agent.as_ref().unwrap().0,
            "agent-2"
        );
    }

    #[test]
    fn full_lifecycle() {
        let (store, sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        view.assign(&work.id, "agent-1").unwrap();
        view.start(&work.id, "agent-1").unwrap();
        view.submit_for_review(&work.id, "agent-1").unwrap();
        let done = view.approve(&work.id, "reviewer-1").unwrap();
        assert_eq!(done.status, WorkItemStatus::Done);
        assert!(done.stage_log.entries.len() >= 4);
        let events = sink.snapshot();
        assert!(events
            .iter()
            .any(|e| matches!(e.kind, SdlcEventKind::Approved { .. })));
    }

    #[test]
    fn wrong_actor_is_rejected() {
        let (store, _sink) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        view.assign(&work.id, "agent-1").unwrap();
        let err = view.start(&work.id, "agent-2").unwrap_err();
        assert!(matches!(err, DelegationError::WrongActor { .. }));
    }

    #[test]
    fn invalid_transition_blocked_terminal() {
        let (store, _) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let work = view.create_work("ship", SdlcStage::Ready).unwrap();
        let _ = view.cancel(&work.id).unwrap();
        let err = view.approve(&work.id, "reviewer-1").unwrap_err();
        assert!(matches!(err, DelegationError::InvalidTransition { .. }));
    }

    #[test]
    fn list_for_agent_filters_correctly() {
        let (store, _) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let a = view.create_work("a", SdlcStage::Ready).unwrap();
        let b = view.create_work("b", SdlcStage::Ready).unwrap();
        view.assign(&a.id, "agent-1").unwrap();
        view.assign(&b.id, "agent-2").unwrap();
        assert_eq!(view.list_for_agent("agent-1").len(), 1);
        assert_eq!(view.list_for_agent("agent-2").len(), 1);
        assert_eq!(view.list_for_agent("agent-3").len(), 0);
    }

    #[test]
    fn transition_table_is_total() {
        use WorkItemStatus::*;
        assert!(is_valid_transition(Ready, InProgress));
        assert!(is_valid_transition(InProgress, Review));
        assert!(is_valid_transition(Review, Done));
        assert!(!is_valid_transition(Done, Ready));
        assert!(!is_valid_transition(Cancelled, InProgress));
    }

    #[test]
    fn tag_list_round_trips_via_serde() {
        let (store, _) = fresh_store_with_sink();
        let view = Delegation::new(&store);
        let mut item = view.create_work("typed", SdlcStage::Ready).unwrap();
        item.tags = vec!["alpha".into(), "beta".into()];
        store.upsert(item.clone());
        let json = serde_json::to_string(&item).unwrap();
        let back: WorkItem = serde_json::from_str(&json).unwrap();
        assert_eq!(back.tags, vec!["alpha", "beta"]);
    }
}
