//! Distillation configuration.

use std::time::Duration;

/// Controls how the distiller selects and retains patterns.
#[derive(Debug, Clone)]
pub struct DistillationConfig {
    /// Minimum elapsed time between distillation passes.
    pub interval: Duration,
    /// A pattern must appear at least this many times before it qualifies.
    pub min_pattern_occurrences: usize,
    /// Maximum number of memory entries the distiller will retain.
    pub max_memory_size: usize,
    /// Confidence threshold below which entries are pruned (0.0 - 1.0).
    pub confidence_threshold: f64,
    /// Decay factor applied to confidence on each prune cycle.
    pub decay_factor: f64,
}

impl Default for DistillationConfig {
    fn default() -> Self {
        Self {
            interval: Duration::from_secs(300),
            min_pattern_occurrences: 3,
            max_memory_size: 10_000,
            confidence_threshold: 0.3,
            decay_factor: 0.9,
        }
    }
}
