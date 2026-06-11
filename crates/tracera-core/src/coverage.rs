//! Coverage analysis: which requirements are covered, partial, missing, stale, conflict.

use serde::{Deserialize, Serialize};

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct CoverageSummary {
    pub total: usize,
    pub covered: usize,
    pub partial: usize,
    pub missing: usize,
    pub stale: usize,
    pub conflict: usize,
}

pub fn summarize(states: &[crate::CoverageState]) -> CoverageSummary {
    let mut s = CoverageSummary::default();
    for &st in states {
        match st {
            crate::CoverageState::Covered => s.covered += 1,
            crate::CoverageState::Partial => s.partial += 1,
            crate::CoverageState::Missing => s.missing += 1,
            crate::CoverageState::Stale => s.stale += 1,
            crate::CoverageState::Conflict => s.conflict += 1,
        }
    }
    s.total = states.len();
    s
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::CoverageState;

    #[test]
    fn empty_summary() {
        let s = summarize(&[]);
        assert_eq!(s.total, 0);
        assert_eq!(s.covered, 0);
    }

    #[test]
    fn mixed_summary() {
        let s = summarize(&[
            CoverageState::Covered,
            CoverageState::Missing,
            CoverageState::Partial,
        ]);
        assert_eq!(s.total, 3);
        assert_eq!(s.covered, 1);
        assert_eq!(s.missing, 1);
        assert_eq!(s.partial, 1);
    }
}
