# AgilePlus receipt preflight

This offline checker validates the native AgilePlus `FeatureAcceptanceReceipt`
shape and exact work/candidate binding before a future authenticated Tracera
consumer considers it. It does not ingest, persist, reconcile or accept product
state. A successful exit means `receipt_preflight_only`; `product_reconciled`
is always false. No production route or existing receipt schema is changed.

Run the independent fixture controls:

```text
python scripts/test-agileplus-receipt.py
```

Check a real receipt using a separately acquired digest and independently frozen
expected context:

```text
python scripts/verify-agileplus-receipt.py receipt.json --expected expected-work.json --receipt-sha256 <trusted-raw-file-sha256>
```

The digest covers the exact receipt bytes, not reserialized JSON. Acquire it
through the trusted producer/source retrieval path; computing it from a supplied
untrusted bundle does not establish integrity or authority. Actor strings and
matching IDs do not authenticate a producer, evaluator or owner. The expected
context must also come from a trusted invocation, not the receipt sender.
Timestamps are checked for UTC syntax only; chronology and freshness remain
unverified, including a syntactically valid future timestamp.

`expected-work.json` contains `product_id`, `graph_revision`, `proposal_id`,
`feature_id`, `governance_contract_id`, `governance_version`, and the complete
`accepted_candidates` set. Candidate expectations contain native `wp_id`,
`assignment_id`, `attempt_id`, `evaluation_id` and immutable `candidate_ref`.
Optional native `worktree_path` is validated but never opened or echoed.
Graph/proposal context is required as an explicit future linkage obligation;
the native receipt does not contain those fields, so this checker cannot prove
that linkage or determine graph freshness.

The hand-authored `tests/fixtures/agileplus` ToDo pair uses native field types;
it was not emitted by a running AgilePlus instance. Its commit IDs are synthetic.
The checker deliberately rejects unknown fields, duplicate JSON keys, nonfinite
numbers, boolean numeric IDs, ambiguous duplicate WPs, unpinned candidates,
changed receipt bytes, mismatched governance/work/candidate identities and naive
timestamps. Native receipt changes require an explicit compatibility update.

Semantic negative controls recompute the digest, proving rejection is not only
a checksum comparison. Cold-process/retry tests exercise the stateless checker;
they do not test server restart durability or production idempotency.

## Remaining executable-twin integration

The next runtime path is tracked in
[issue1164](https://github.com/KooshaPari/Tracera/issues/1164). Current
`handlers/ingest_api.rs::ingest_agileplus` accepts AgCord items and source
`agcord`. Preserve legacy callers; do not reinterpret their data as a governance
receipt. Add a distinct authenticated, versioned receipt ingestion contract
after explicit product/proposal/work linkage is defined. Reuse AgilePlus
`domain/acceptance.rs` receipts and acceptance tests instead of another backend.

That consumer must bind the independently retrieved receipt to the current
product/graph revision and authorized proposal, resolve exact candidate and
independent evaluation evidence, and persist an observation transactionally.
Replayed request IDs must return the original outcome; conflicting content must
fail closed, including after server restart. Receipt acceptance must not itself
mark a capability satisfied. Tracera product observations currently include an
in-memory `ObservationStore`; the existing
[PR1157](https://github.com/KooshaPari/Tracera/pull/1157) persistence lane must be
reviewed/converged rather than duplicated.

Canonical graph convergence remains in
[PR1099](https://github.com/KooshaPari/Tracera/pull/1099) and
[PR1126](https://github.com/KooshaPari/Tracera/pull/1126); product-graph witness
[issue1119](https://github.com/KooshaPari/Tracera/issues/1119) and assessment
isolation [issue1098](https://github.com/KooshaPari/Tracera/issues/1098) remain
separate gates. No current maintainer ownership or merge readiness is inferred
from those open lanes.

The original user requirement (August21,2025) is diagram edit -> real product
change, programmatically or through agents. This preflight closes a small
input-checking gap only. Authenticated receipt transport, graph linkage, causal
execution, real artifact/evaluation retrieval, persistent reconciliation and
deployed product behavior remain unverified.
