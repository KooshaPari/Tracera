//! TRC-PHENO-009: Status / validate.
//!
//! Port of phenodag's cmdStatus + cmdValidate. Reports queue state summary
//! and validates the DAG for cycles and dangles.

use serde::Serialize;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum StatusError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Clone, Serialize)]
pub struct StatusReport {
    pub tasks_total: usize,
    pub tasks_by_status: std::collections::BTreeMap<String, usize>,
    pub agents_total: usize,
    pub agents_stale: usize,
    pub dag_valid: bool,
    pub cycles: usize,
    pub dangles: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn report_serializes() {
        let r = StatusReport {
            tasks_total: 0,
            tasks_by_status: std::collections::BTreeMap::new(),
            agents_total: 0,
            agents_stale: 0,
            dag_valid: true,
            cycles: 0,
            dangles: 0,
        };
        let j = serde_json::to_string(&r).unwrap();
        assert!(j.contains("dag_valid"));
    }
}
