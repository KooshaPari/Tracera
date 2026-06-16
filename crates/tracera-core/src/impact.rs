//! Re-export impact analysis from the shared core.

pub use traceability_core::{
    compute_impact, conflicts_only, top_affected, BlastNode, ImpactConfig, ImpactReport,
};
