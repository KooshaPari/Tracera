//! Matrix operations: build, query, diff.
use crate::CoverageMatrix;

pub fn build_empty_matrix() -> CoverageMatrix {
    CoverageMatrix::default()
}
