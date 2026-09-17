use regex::Regex;

/// Extract requirement/spec references from free-form issue body text.
///
/// Matches `REQ-NNN`, `SPEC-NNN`, `FR-NNN`, and `NFR-NNN` (case-insensitive).
/// Returns a list of referenced IDs (e.g. `["REQ-001", "SPEC-042"]`).
pub fn extract_req_refs(body: &str) -> Vec<String> {
    // Lazily compiled; in production this would be a `once_cell::sync::Lazy`.
    let re = Regex::new(r"(?i)\b(REQ|SPEC|FR|NFR)-\d+\b").expect("valid regex");
    re.find_iter(body)
        .map(|m| m.as_str().to_uppercase())
        .collect::<std::collections::BTreeSet<_>>() // deduplicate
        .into_iter()
        .collect()
}
