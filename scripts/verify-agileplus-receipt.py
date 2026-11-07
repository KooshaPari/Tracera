#!/usr/bin/env python3
"""Check a native AgilePlus acceptance receipt without accepting product state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

RECEIPT_FIELDS = {
    "request_id",
    "feature_id",
    "actor",
    "governance_contract_id",
    "governance_version",
    "accepted_candidates",
    "audit_ids",
    "event_id",
    "committed_at",
}
CANDIDATE_FIELDS = {
    "wp_id",
    "assignment_id",
    "attempt_id",
    "evaluation_id",
    "candidate_ref",
}
EXPECTED_FIELDS = {
    "product_id",
    "graph_revision",
    "proposal_id",
    "feature_id",
    "governance_contract_id",
    "governance_version",
    "accepted_candidates",
}
UNVERIFIED = [
    "producer_authentication_and_authority",
    "graph_revision_and_proposal_linkage",
    "independent_evaluation_and_evidence_contents",
    "receipt_chronology_and_freshness",
    "product_behavior_and_reconciliation",
    "production_replay_and_restart_durability",
]


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def load_json(raw: bytes) -> object:
    def invalid_constant(_: str) -> None:
        raise ValueError("non_finite_json_number")

    return json.loads(
        raw, object_pairs_hook=unique_object, parse_constant=invalid_constant
    )


def candidates(value: object, native: bool) -> list[dict]:
    require(isinstance(value, list) and bool(value), "missing_candidates")
    result = []
    for candidate in value:
        require(isinstance(candidate, dict), "invalid_candidate")
        fields = set(candidate)
        allowed = CANDIDATE_FIELDS | ({"worktree_path"} if native else set())
        require(CANDIDATE_FIELDS <= fields <= allowed, "invalid_candidate_fields")
        require(positive_int(candidate["wp_id"]), "invalid_wp_id")
        require(
            all(text(candidate[key]) for key in CANDIDATE_FIELDS - {"wp_id"}),
            "invalid_candidate_identity",
        )
        require(
            re.fullmatch(
                r"git:(?:[0-9a-f]{40}|[0-9a-f]{64})", candidate["candidate_ref"]
            )
            is not None,
            "unpinned_candidate",
        )
        if "worktree_path" in candidate:
            require(
                candidate["worktree_path"] is None or text(candidate["worktree_path"]),
                "invalid_worktree_path",
            )
        result.append({key: candidate[key] for key in CANDIDATE_FIELDS})
    require(
        len({candidate["wp_id"] for candidate in result}) == len(result),
        "duplicate_work_package",
    )
    return sorted(result, key=lambda candidate: candidate["wp_id"])


def verify(raw: bytes, expected: object, receipt_sha256: str) -> dict:
    require(re.fullmatch(r"[0-9a-f]{64}", receipt_sha256) is not None, "invalid_digest")
    require(
        hashlib.sha256(raw).hexdigest() == receipt_sha256, "receipt_digest_mismatch"
    )
    receipt = load_json(raw)
    require(
        isinstance(receipt, dict) and set(receipt) == RECEIPT_FIELDS,
        "invalid_receipt_fields",
    )
    require(
        isinstance(expected, dict) and set(expected) == EXPECTED_FIELDS,
        "invalid_expected_fields",
    )
    for key in ("request_id", "actor", "committed_at"):
        require(text(receipt[key]), f"invalid_{key}")
    for key in ("product_id", "graph_revision", "proposal_id"):
        require(text(expected[key]), f"invalid_expected_{key}")
    for key in ("feature_id", "governance_contract_id", "governance_version"):
        require(
            positive_int(receipt[key]) and positive_int(expected[key]), f"invalid_{key}"
        )
        require(receipt[key] == expected[key], f"mismatched_{key}")
    require(positive_int(receipt["event_id"]), "invalid_event_id")
    audit_ids = receipt["audit_ids"]
    require(
        isinstance(audit_ids, list)
        and bool(audit_ids)
        and all(positive_int(value) for value in audit_ids),
        "invalid_audit_ids",
    )
    require(len(set(audit_ids)) == len(audit_ids), "duplicate_audit_ids")
    try:
        committed_at = datetime.fromisoformat(
            receipt["committed_at"].replace("Z", "+00:00")
        )
    except ValueError as error:
        raise ValueError("invalid_committed_at") from error
    require(committed_at.utcoffset() == timedelta(0), "committed_at_must_be_utc")
    require(
        candidates(receipt["accepted_candidates"], True)
        == candidates(expected["accepted_candidates"], False),
        "candidate_binding_mismatch",
    )
    return {
        "status": "receipt_preflight_only",
        "request_id": receipt["request_id"],
        "receipt_sha256": receipt_sha256,
        "product_reconciled": False,
        "unverified": UNVERIFIED,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument(
        "--expected",
        required=True,
        type=Path,
        help="independently frozen expected work and graph context",
    )
    parser.add_argument(
        "--receipt-sha256",
        required=True,
        help="digest acquired independently of the supplied receipt",
    )
    args = parser.parse_args()
    try:
        report = verify(
            args.receipt.read_bytes(),
            load_json(args.expected.read_bytes()),
            args.receipt_sha256,
        )
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print(json.dumps({"status": "rejected", "product_reconciled": False}))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
