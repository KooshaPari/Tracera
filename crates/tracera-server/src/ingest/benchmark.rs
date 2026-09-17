use serde_json::Value;

use super::{IngestError, NormalisedIssue};

/// Map a Helios benchmark envelope into the existing story/evidence ingest path.
/// The envelope remains content-addressed through its outcome/replay hashes.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "public ingest adapter exercised by contract and integration callers"
    )
)]
pub fn benchmark_run_to_issue(envelope: &Value) -> Result<NormalisedIssue, IngestError> {
    let run_id = envelope
        .get("run_id")
        .and_then(Value::as_str)
        .ok_or_else(|| IngestError::Fetch("benchmark envelope missing run_id".into()))?;
    let session_id = envelope
        .get("session_id")
        .and_then(Value::as_str)
        .ok_or_else(|| IngestError::Fetch("benchmark envelope missing session_id".into()))?;
    let attempt_id = envelope
        .get("attempt_id")
        .and_then(Value::as_str)
        .ok_or_else(|| IngestError::Fetch("benchmark envelope missing attempt_id".into()))?;
    let valid_id = |prefix: &str, value: &str| {
        value.strip_prefix(prefix).is_some_and(|suffix| {
            suffix.len() == 64 && suffix.chars().all(|c| c.is_ascii_hexdigit())
        })
    };
    if !valid_id("run_", run_id) || !valid_id("ses_", session_id) || !valid_id("att_", attempt_id) {
        return Err(IngestError::Fetch(
            "benchmark envelope has invalid causality IDs".into(),
        ));
    }
    let status = envelope
        .pointer("/result/status")
        .and_then(Value::as_str)
        .ok_or_else(|| IngestError::Fetch("benchmark envelope missing result status".into()))?;
    if !matches!(status, "passed" | "failed" | "timeout" | "cancelled") {
        return Err(IngestError::Fetch(
            "benchmark envelope has invalid result status".into(),
        ));
    }
    let replay_hash = envelope
        .pointer("/result/replay_hash")
        .and_then(Value::as_str)
        .ok_or_else(|| IngestError::Fetch("benchmark envelope missing replay_hash".into()))?;
    if replay_hash.len() != 64 || !replay_hash.chars().all(|c| c.is_ascii_hexdigit()) {
        return Err(IngestError::Fetch(
            "benchmark envelope has invalid replay_hash".into(),
        ));
    }
    Ok(NormalisedIssue {
        external_id: format!("helios-{run_id}"),
        title: format!("Helios benchmark {run_id}"),
        body: format!("status={status}; replay_hash={replay_hash}"),
        url: format!("urn:helios:run:{run_id}"),
        status: status.to_string(),
        source: "helios".to_string(),
    })
}

#[cfg(test)]
mod benchmark_contract_tests {
    use super::benchmark_run_to_issue;
    use serde_json::json;
    use serde_json::Value;

    #[test]
    fn valid_benchmark_envelope_maps_to_trace_issue() {
        let hex = "a".repeat(64);
        let issue = benchmark_run_to_issue(&json!({"run_id":format!("run_{hex}"), "session_id":format!("ses_{hex}"), "attempt_id":format!("att_{hex}"), "result":{"status":"passed", "replay_hash":hex}})).expect("valid envelope");
        assert_eq!(issue.source, "helios");
        assert_eq!(issue.status, "passed");
        assert_eq!(issue.url, format!("urn:helios:run:run_{hex}"));
    }

    #[test]
    fn malformed_benchmark_envelope_is_rejected() {
        let result =
            benchmark_run_to_issue(&json!({"run_id":"run_bad", "result":{"status":"passed"}}));
        assert!(result.is_err());
    }

    #[test]
    fn helios_fixture_preserves_content_addressed_fields() {
        let envelope: Value =
            serde_json::from_str(include_str!("../../testdata/helios-benchmark-run.json"))
                .expect("fixture JSON");
        let issue = benchmark_run_to_issue(&envelope).expect("valid Helios fixture");
        assert!(issue.url.starts_with("urn:helios:run:run_"));
        assert_eq!(issue.status, "passed");
        assert!(issue.body.contains("replay_hash="));
    }

    #[test]
    fn pheno_harness_fixture_replays_through_tracera_mapper() {
        let envelope: Value =
            serde_json::from_str(include_str!("../../testdata/pheno-harness-benchmark-run.json"))
                .expect("fixture JSON");
        let issue = benchmark_run_to_issue(&envelope).expect("valid pheno-harness fixture");
        assert_eq!(issue.status, "passed");
        assert_eq!(
            issue.url,
            "urn:helios:run:run_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        );
        assert!(issue
            .body
            .contains("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"));
    }
}
