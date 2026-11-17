//! Durable product observation contract. Batches are atomic and append-only.
use super::{AcceptedIntent, BaselineRevision, Observation, ProductId};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProductObservationBatch {
    pub product_id: ProductId,
    pub baseline: BaselineRevision,
    pub idempotency_key: String,
    pub intents: Vec<AcceptedIntent>,
    pub observations: Vec<Observation>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProductObservationModel {
    pub product_id: ProductId,
    pub baseline: BaselineRevision,
    pub intents: Vec<AcceptedIntent>,
    pub observations: Vec<Observation>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProductIngestReceipt {
    pub accepted: usize,
    pub replayed: bool,
}

impl ProductObservationBatch {
    pub fn validate(&self) -> Result<(), String> {
        fn identity(value: &str) -> bool {
            !value.is_empty()
                && value.len() <= 256
                && value.trim() == value
                && value.chars().all(|c| !c.is_control())
        }
        if !identity(self.product_id.as_str()) || !identity(&self.idempotency_key) {
            return Err(
                "product_id and idempotency_key must be nonempty bounded identities".into(),
            );
        }
        if self.baseline.number() > i64::MAX as u64
            || self.intents.len() > 1000
            || self.observations.is_empty()
            || self.observations.len() > 500
        {
            return Err(
                "invalid baseline or batch size (1..500 observations, <=1000 intents)".into(),
            );
        }
        let mut ids = std::collections::HashSet::new();
        for intent in &self.intents {
            if !identity(&intent.id) || intent.baseline != self.baseline || !ids.insert(&intent.id)
            {
                return Err("intent identities must be unique and match the baseline".into());
            }
        }
        let mut observations = std::collections::HashSet::new();
        for obs in &self.observations {
            if !identity(&obs.id)
                || !observations.insert(&obs.id)
                || obs.product_id != self.product_id
                || obs.baseline != self.baseline
                || !identity(&obs.source.collector)
                || !identity(&obs.source.version)
                || obs.recorded_at > chrono::Utc::now() + chrono::Duration::minutes(5)
            {
                return Err("observation identity, scope, source, or timestamp invalid".into());
            }
            if let Some(capability) = &obs.capability_id {
                if !self.intents.iter().any(|intent| {
                    intent.id == *capability
                        && intent.kind == super::IntentKind::Capability
                        && intent.status == super::IntentStatus::Accepted
                }) {
                    return Err("observation capability must be accepted in this baseline".into());
                }
            }
        }
        Ok(())
    }
}
