use serde::{Deserialize, Serialize};

use traceability_core::{CoverageMatrix, CoverageState};

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct CoverageSummary {
    pub covered: usize,
    pub partial: usize,
    pub missing: usize,
    pub stale: usize,
    pub conflict: usize,
}

impl CoverageSummary {
    pub fn from_matrix(matrix: &CoverageMatrix) -> Self {
        let mut summary = Self::default();
        for cell in matrix.cells.values() {
            match cell.coverage {
                CoverageState::Covered => summary.covered += 1,
                CoverageState::Partial => summary.partial += 1,
                CoverageState::Missing => summary.missing += 1,
                CoverageState::Stale => summary.stale += 1,
                CoverageState::Conflict => summary.conflict += 1,
            }
        }
        summary
    }
}
