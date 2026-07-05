//! TRC-PHENO-004: Fuzzy duplicate detection.
//!
//! Port of phenodag v0.3.0 `cmdDupes` (Go). Uses Levenshtein distance to find
//! near-duplicate task titles within the queue.

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum DedupError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DupGroup {
    pub root_id: String,
    pub root_title: String,
    pub similar: Vec<(String, String, f32)>, // (id, title, similarity 0..=1)
}

/// Levenshtein distance (iterative, O(n*m) time, O(min(n,m)) space).
pub fn levenshtein(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    if a.is_empty() { return b.len(); }
    if b.is_empty() { return a.len(); }
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    let mut curr = vec![0; b.len() + 1];
    for i in 1..=a.len() {
        curr[0] = i;
        for j in 1..=b.len() {
            let cost = if a[i-1] == b[j-1] { 0 } else { 1 };
            curr[j] = (prev[j] + 1).min(curr[j-1] + 1).min(prev[j-1] + cost);
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[b.len()]
}

/// Similarity in [0.0, 1.0]: 1.0 = identical, 0.0 = completely different.
pub fn similarity(a: &str, b: &str) -> f32 {
    let max_len = a.chars().count().max(b.chars().count()) as f32;
    if max_len == 0.0 { return 1.0; }
    1.0 - (levenshtein(a, b) as f32 / max_len)
}

/// Find near-duplicate groups in a list of (id, title) pairs.
/// `threshold` is the minimum similarity to consider two items duplicates.
pub fn find_dupes(items: &[(String, String)], threshold: f32) -> Vec<DupGroup> {
    let mut groups: Vec<DupGroup> = Vec::new();
    for (id, title) in items {
        let mut placed = false;
        for g in groups.iter_mut() {
            if similarity(&g.root_title, title) >= threshold {
                g.similar.push((id.clone(), title.clone(), similarity(&g.root_title, title)));
                placed = true;
                break;
            }
        }
        if !placed {
            groups.push(DupGroup {
                root_id: id.clone(),
                root_title: title.clone(),
                similar: vec![],
            });
        }
    }
    groups.retain(|g| !g.similar.is_empty()); // keep only groups with at least one similar
    groups
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn lev_basic() { assert_eq!(levenshtein("kitten", "sitting"), 3); }
    #[test] fn sim_identical() { assert!((similarity("foo", "foo") - 1.0).abs() < 1e-6); }
    #[test] fn sim_different() { assert!(similarity("abc", "xyz") < 0.5); }
    #[test] fn find_dupes_groups() {
        let items = vec![
            ("1".into(), "Implement PKCE state binding".into()),
            ("2".into(), "Implement PKCE states binding".into()),
            ("3".into(), "Write README".into()),
        ];
        let groups = find_dupes(&items, 0.7);
        assert_eq!(groups.len(), 1);
        assert_eq!(groups[0].root_id, "1");
        assert_eq!(groups[0].similar.len(), 1);
        assert_eq!(groups[0].similar[0].0, "2");
    }
}
