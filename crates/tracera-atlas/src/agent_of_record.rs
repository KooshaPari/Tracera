//! Agent-of-record: who-changed-what-who-signed-off audit log.
//!
//! Every mutation in [`crate::delegation`] can be tied back to an actor.
//! For audit and compliance purposes Atlas also records:
//!
//! - An **append-only change log** per work item, recording every
//!   state-machine transition with the actor who triggered it.
//! - A **sign-off log** capturing explicit human/peer approval of a work
//!   item, with the reviewer being *distinct* from the assignee.
//!
//! Together these answer the canonical "who-changed-what-who-signed-off"
//! question without requiring callers to scrape the underlying event bus.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::RwLock;
use thiserror::Error;
use tracing::info;
use uuid::Uuid;

use crate::delegation::{
    AgentId, DelegationError, DelegationStore, WorkItemId, WorkItemStatus,
};
use crate::observability::{SdlcEvent, SdlcEventKind};

// ---------- Identifiers ----------

/// Stable identifier for an actor (the "who" in who-changed-what).
///
/// `ActorId` is a deliberately separate type from `AgentId` to give
/// downstream callers a place to attach richer identity (e.g. a SCIM user
/// reference, a service-account URN, or a federated CI bot id) without
/// forcing every consumer of `AgentId` to know about it. Internally we
/// just wrap the same string.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct ActorId(pub String);

impl ActorId {
    /// Construct a new actor id.
    pub fn new(value: impl Into<String>) -> Self {
        Self(value.into().trim().to_string())
    }
}

impl std::fmt::Display for ActorId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

impl From<&AgentId> for ActorId {
    fn from(agent: &AgentId) -> Self {
        Self(agent.0.clone())
    }
}

/// Stable identifier for a sign-off record.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct SignOffId(pub Uuid);

impl SignOffId {
    /// Create a new sign-off id.
    #[must_use]
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for SignOffId {
    fn default() -> Self {
        Self::new()
    }
}

impl std::fmt::Display for SignOffId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

// ---------- Records ----------

/// Classification of a recorded change.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ChangeKind {
    /// A work item was created.
    Created,
    /// An agent was assigned.
    Assigned,
    /// An agent started work.
    Started,
    /// The work item moved to `Review`.
    ReviewSubmitted,
    /// The work item moved to `Done`.
    Approved,
    /// The work item was blocked.
    Blocked,
    /// The work item was unblocked (back to `Ready` or `InProgress`).
    Unblocked,
    /// The work item was cancelled.
    Cancelled,
    /// A free-form change recorded by an external actor (annotations,
    /// re-tags, etc.).
    Annotation,
}

impl ChangeKind {
    /// Stable string tag.
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Created => "created",
            Self::Assigned => "assigned",
            Self::Started => "started",
            Self::ReviewSubmitted => "review_submitted",
            Self::Approved => "approved",
            Self::Blocked => "blocked",
            Self::Unblocked => "unblocked",
            Self::Cancelled => "cancelled",
            Self::Annotation => "annotation",
        }
    }
}

impl std::fmt::Display for ChangeKind {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(self.as_str())
    }
}

/// One entry in the append-only change log for a work item.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ChangeRecord {
    /// Stable id for this change record.
    pub id: Uuid,
    /// Work item this record pertains to.
    pub work_item_id: WorkItemId,
    /// The actor that triggered or recorded the change.
    pub actor: ActorId,
    /// Classification of the change.
    pub kind: ChangeKind,
    /// Status of the work item *after* the change was applied.
    pub status_after: WorkItemStatus,
    /// Wall-clock time the change was recorded.
    pub at: DateTime<Utc>,
    /// Optional human-readable note.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
    /// Optional structured fields captured at the point of change (e.g.
    /// `{ "commit": "abc1234" }` for a CI-recorded change).
    #[serde(default)]
    pub metadata: indexmap::IndexMap<String, String>,
}

/// An explicit sign-off recorded by a distinct actor.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SignOff {
    /// Stable id.
    pub id: SignOffId,
    /// Work item being signed off.
    pub work_item_id: WorkItemId,
    /// The actor who signed off.
    pub signer: ActorId,
    /// The agent who did the original work, for cross-reference.
    pub author: ActorId,
    /// Wall-clock time the sign-off was recorded.
    pub at: DateTime<Utc>,
    /// Optional review note / comment.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
}

// ---------- Query ----------

/// Query parameters for [`AgentOfRecord::query_changes`].
#[derive(Debug, Clone, Default)]
pub struct AoRQuery {
    /// Restrict to a single work item.
    pub work_item_id: Option<WorkItemId>,
    /// Restrict to a single actor.
    pub actor: Option<ActorId>,
    /// Restrict to a single change kind.
    pub kind: Option<ChangeKind>,
    /// Optional lower bound on `at` (inclusive).
    pub since: Option<DateTime<Utc>>,
    /// Optional upper bound on `at` (exclusive).
    pub until: Option<DateTime<Utc>>,
    /// Maximum number of records to return. `None` means no limit.
    pub limit: Option<usize>,
}

impl AoRQuery {
    /// Filter a single change record against this query.
    pub(crate) fn matches(&self, rec: &ChangeRecord) -> bool {
        if let Some(wid) = &self.work_item_id {
            if &rec.work_item_id != wid {
                return false;
            }
        }
        if let Some(actor) = &self.actor {
            if &rec.actor != actor {
                return false;
            }
        }
        if let Some(kind) = self.kind {
            if rec.kind != kind {
                return false;
            }
        }
        if let Some(since) = self.since {
            if rec.at < since {
                return false;
            }
        }
        if let Some(until) = self.until {
            if rec.at >= until {
                return false;
            }
        }
        true
    }
}

// ---------- Errors ----------

/// Errors returned from the agent-of-record API.
#[derive(Debug, Error)]
pub enum AoRError {
    /// The underlying delegation store rejected the operation.
    #[error("delegation error: {0}")]
    Delegation(#[from] DelegationError),
    /// The actor supplied for a sign-off was empty.
    #[error("signer id must not be empty")]
    EmptySigner,
    /// The work item is in a state that does not allow sign-off.
    #[error("work item {0} is not in a signable state")]
    NotSignable(WorkItemId),
    /// The sign-off was attempted by the same actor who did the work.
    #[error("signer {signer} is the same actor as the author {author} for work item {work_item}")]
    SelfSignOff {
        /// The work item id.
        work_item: WorkItemId,
        /// The signer.
        signer: ActorId,
        /// The author.
        author: ActorId,
    },
}

// ---------- Store ----------

/// Internal store backing the `AgentOfRecord` API.
#[derive(Debug)]
pub(crate) struct AoRStore {
    changes: RwLock<Vec<ChangeRecord>>,
    sign_offs: RwLock<Vec<SignOff>>,
}

impl AoRStore {
    pub(crate) fn new() -> Self {
        Self {
            changes: RwLock::new(Vec::new()),
            sign_offs: RwLock::new(Vec::new()),
        }
    }

    pub(crate) fn append(&self, rec: ChangeRecord) {
        if let Ok(mut g) = self.changes.write() {
            g.push(rec);
        }
    }

    pub(crate) fn query(&self, q: &AoRQuery) -> Vec<ChangeRecord> {
        let g = match self.changes.read() {
            Ok(g) => g,
            Err(_) => return Vec::new(),
        };
        let mut out: Vec<ChangeRecord> = g.iter().filter(|r| q.matches(r)).cloned().collect();
        if let Some(limit) = q.limit {
            out.truncate(limit);
        }
        out
    }

    pub(crate) fn append_sign_off(&self, sign_off: SignOff) {
        if let Ok(mut g) = self.sign_offs.write() {
            g.push(sign_off);
        }
    }

    pub(crate) fn sign_offs_for(&self, id: &WorkItemId) -> Vec<SignOff> {
        self.sign_offs
            .read()
            .map(|g| {
                g.iter()
                    .filter(|s| &s.work_item_id == id)
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

// ---------- Public façade ----------

/// Public façade for the agent-of-record subsystem.
pub struct AgentOfRecord<'a> {
    aor: &'a AoRStore,
    delegation: &'a DelegationStore,
}

impl<'a> AgentOfRecord<'a> {
    /// Construct a new view over the agent-of-record stores.
    pub(crate) fn new(delegation: &'a DelegationStore) -> Self {
        Self {
            aor: delegation.aor(),
            delegation,
        }
    }

    /// Record a custom annotation against a work item.
    ///
    /// Annotations are the escape hatch for callers that need to record
    /// out-of-band context (a Jira ticket link, a design-doc URL, etc.)
    /// without driving the state machine.
    pub fn annotate(
        &self,
        work_item_id: &WorkItemId,
        actor: &str,
        note: &str,
    ) -> Result<ChangeRecord, AoRError> {
        let actor_id = ActorId::new(actor);
        if actor_id.0.is_empty() {
            return Err(AoRError::EmptySigner);
        }
        let item = self
            .delegation
            .get(work_item_id)
            .ok_or_else(|| AoRError::Delegation(DelegationError::not_found(work_item_id)))?;
        let rec = ChangeRecord {
            id: Uuid::new_v4(),
            work_item_id: item.id.clone(),
            actor: actor_id,
            kind: ChangeKind::Annotation,
            status_after: item.status,
            at: Utc::now(),
            note: if note.is_empty() {
                None
            } else {
                Some(note.to_string())
            },
            metadata: indexmap::IndexMap::new(),
        };
        self.aor.append(rec.clone());
        self.delegation
            .record_event(SdlcEvent::work_item_transition(&item, SdlcEventKind::ChangeRecorded));
        Ok(rec)
    }

    /// Query the change log.
    #[must_use]
    pub fn query_changes(&self, query: &AoRQuery) -> Vec<ChangeRecord> {
        self.aor.query(query)
    }

    /// Record a sign-off against a work item.
    ///
    /// - The work item must currently be in `Review` (otherwise
    ///   [`AoRError::NotSignable`] is returned).
    /// - The signer must NOT be the same actor as the assigned agent
    ///   (otherwise [`AoRError::SelfSignOff`] is returned) — this is the
    ///   two-person integrity rule.
    pub fn sign_off(
        &self,
        work_item_id: &WorkItemId,
        signer: &str,
        note: Option<&str>,
    ) -> Result<SignOff, AoRError> {
        let signer_id = ActorId::new(signer);
        if signer_id.0.is_empty() {
            return Err(AoRError::EmptySigner);
        }
        let item = self
            .delegation
            .get(work_item_id)
            .ok_or_else(|| AoRError::Delegation(DelegationError::not_found(work_item_id)))?;
        if item.status != WorkItemStatus::Review {
            return Err(AoRError::NotSignable(item.id.clone()));
        }
        let author = item
            .assigned_agent
            .as_ref()
            .map(ActorId::from)
            .unwrap_or_else(|| ActorId::new(""));
        if !author.0.is_empty() && signer_id == author {
            return Err(AoRError::SelfSignOff {
                work_item: item.id.clone(),
                signer: signer_id,
                author,
            });
        }

        let now = Utc::now();
        let sign_off = SignOff {
            id: SignOffId::new(),
            work_item_id: item.id.clone(),
            signer: signer_id.clone(),
            author,
            at: now,
            note: note.map(|s| s.to_string()).filter(|s| !s.is_empty()),
        };
        self.aor.append_sign_off(sign_off.clone());

        // Mirror the sign-off into the change log for unified queries.
        let rec = ChangeRecord {
            id: Uuid::new_v4(),
            work_item_id: item.id.clone(),
            actor: signer_id.clone(),
            kind: ChangeKind::Approved,
            status_after: item.status,
            at: now,
            note: sign_off.note.clone(),
            metadata: indexmap::IndexMap::new(),
        };
        self.aor.append(rec);

        self.delegation.record_event(SdlcEvent::work_item_transition(
            &item,
            SdlcEventKind::SignOffRecorded {
                signer: signer_id.0.clone(),
            },
        ));

        info!(
            work_item_id = %item.id,
            signer = %signer_id,
            "sign-off recorded"
        );
        Ok(sign_off)
    }

    /// All sign-offs recorded against the given work item, oldest first.
    #[must_use]
    pub fn sign_offs_for(&self, work_item_id: &WorkItemId) -> Vec<SignOff> {
        self.aor.sign_offs_for(work_item_id)
    }
}

// ---------- Tests ----------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::observability::SdlcStage;
    use crate::AtlasEngine;

    /// Build a small in-memory engine, drive a work item through to `Review`,
    /// and return the engine + the work item id.
    fn engine_with_review_item() -> (AtlasEngine, WorkItemId, AgentId) {
        let engine = AtlasEngine::in_memory();
        let item = engine
            .delegation()
            .create_work("ship MVP", SdlcStage::Ready)
            .unwrap();
        let author = AgentId::new("author-1");
        engine.delegation().assign(&item.id, author.as_str()).unwrap();
        engine.delegation().start(&item.id, author.as_str()).unwrap();
        engine.delegation().submit_for_review(&item.id, author.as_str()).unwrap();
        (engine, item.id, author)
    }

    #[test]
    fn annotate_records_change_log_entry() {
        let engine = AtlasEngine::in_memory();
        let item = engine
            .delegation()
            .create_work("x", SdlcStage::Ready)
            .unwrap();
        let rec = engine
            .agent_of_record()
            .annotate(&item.id, "ops-bot", "linked ticket ABC-123")
            .unwrap();
        assert_eq!(rec.kind, ChangeKind::Annotation);
        assert_eq!(rec.actor, ActorId::new("ops-bot"));
        let q = AoRQuery {
            work_item_id: Some(item.id.clone()),
            ..Default::default()
        };
        let out = engine.agent_of_record().query_changes(&q);
        assert_eq!(out.len(), 1);
        assert_eq!(out[0].id, rec.id);
    }

    #[test]
    fn sign_off_requires_review_state() {
        let engine = AtlasEngine::in_memory();
        let item = engine
            .delegation()
            .create_work("x", SdlcStage::Ready)
            .unwrap();
        let err = engine
            .agent_of_record()
            .sign_off(&item.id, "reviewer-1", None)
            .unwrap_err();
        assert!(matches!(err, AoRError::NotSignable(_)));
    }

    #[test]
    fn sign_off_rejects_self_review() {
        let (engine, item_id, author) = engine_with_review_item();
        let err = engine
            .agent_of_record()
            .sign_off(&item_id, author.as_str(), None)
            .unwrap_err();
        assert!(matches!(err, AoRError::SelfSignOff { .. }));
    }

    #[test]
    fn sign_off_records_audit_trail() {
        let (engine, item_id, _author) = engine_with_review_item();
        let sign_off = engine
            .agent_of_record()
            .sign_off(&item_id, "reviewer-1", Some("LGTM"))
            .unwrap();
        assert_eq!(sign_off.signer, ActorId::new("reviewer-1"));
        assert_eq!(sign_off.note.as_deref(), Some("LGTM"));
        let history = engine.agent_of_record().sign_offs_for(&item_id);
        assert_eq!(history.len(), 1);
        assert_eq!(history[0].id, sign_off.id);
    }

    #[test]
    fn query_filters_by_actor_and_kind() {
        let engine = AtlasEngine::in_memory();
        let item = engine
            .delegation()
            .create_work("x", SdlcStage::Ready)
            .unwrap();
        let _a = engine.agent_of_record().annotate(&item.id, "alice", "n1").unwrap();
        let b = engine.agent_of_record().annotate(&item.id, "bob", "n2").unwrap();
        let q = AoRQuery {
            actor: Some(ActorId::new("bob")),
            ..Default::default()
        };
        let out = engine.agent_of_record().query_changes(&q);
        assert_eq!(out.len(), 1);
        assert_eq!(out[0].id, b.id);
        assert_ne!(out[0].id, _a.id);
    }

    #[test]
    fn empty_signer_is_rejected() {
        let engine = AtlasEngine::in_memory();
        let item = engine
            .delegation()
            .create_work("x", SdlcStage::Ready)
            .unwrap();
        let err = engine
            .agent_of_record()
            .annotate(&item.id, "   ", "x")
            .unwrap_err();
        assert!(matches!(err, AoRError::EmptySigner));
    }
}
