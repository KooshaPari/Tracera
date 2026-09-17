//! Distilled memory entry type.

use std::time::{SystemTime, UNIX_EPOCH};

/// Current time as seconds since the UNIX epoch.
pub(crate) fn now_epoch() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

/// A distilled memory capturing a recurring graph pattern.
#[derive(Debug, Clone)]
pub struct MemoryEntry {
    /// Unique identifier for this entry.
    pub id: u64,
    /// Human-readable description of the pattern.
    pub pattern: String,
    /// Normalised confidence score (0.0 - 1.0).
    pub confidence: f64,
    /// Timestamp (seconds since UNIX epoch) when this pattern was last seen.
    pub last_seen: u64,
    /// IDs of source nodes that contributed to this pattern.
    pub source_nodes: Vec<u64>,
    /// Number of times the pattern has been observed.
    pub occurrence_count: usize,
    /// Edge types involved in the pattern.
    pub edge_types: Vec<String>,
}

impl MemoryEntry {
    /// Create a new entry with an initial confidence of 1.0.
    pub fn new(id: u64, pattern: String, source_nodes: Vec<u64>, edge_types: Vec<String>) -> Self {
        Self {
            id,
            pattern,
            confidence: 1.0,
            last_seen: now_epoch(),
            source_nodes,
            occurrence_count: 1,
            edge_types,
        }
    }

    /// Bump the occurrence count and refresh the last-seen timestamp.
    pub fn touch(&mut self) {
        self.occurrence_count += 1;
        self.last_seen = now_epoch();
        self.confidence = (self.confidence + 1.0).min(1.0);
    }

    /// Apply a decay factor to confidence.
    pub fn decay(&mut self, factor: f64) {
        self.confidence *= factor;
    }
}
