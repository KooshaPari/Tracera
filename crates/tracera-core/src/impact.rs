// SPDX-License-Identifier: MIT OR Apache-2.0
// Copyright 2026 Koosha Pari

//! Re-export impact analysis from the shared core.

pub use traceability_core::{
    compute_impact, conflicts_only, top_affected, BlastNode, ImpactConfig, ImpactReport,
};
