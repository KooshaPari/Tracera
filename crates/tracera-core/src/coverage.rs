//! Coverage analysis: which requirements are covered, partial, missing, stale, conflict.
use crate::CoverageState;

pub fn summarize(states: &[CoverageState]) -> CoverageSummary {
    let mut s = CoverageSummary::default();
    for &st in states {
        match st {
            CoverageState::Covered => s.covered += 1,
            CoverageState::Partial => s.partial += 1,
            CoverageState::Missing => s.missing += 1,
            CoverageState::Stale => s.stale += 1,
            CoverageState::Conflict => s.conflict += 1,
        }
    }
    s.total = states.len();
    s
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct CoverageSummary {
    pub total: usize,
    pub covered: usize,
    pub partial: usize,
    pub missing: usize,
    pub stale: usize,
    pub conflict: usize,
}
