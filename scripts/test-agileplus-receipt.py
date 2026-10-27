#!/usr/bin/env python3
"""Independent negative controls for the offline receipt boundary."""

import copy
import hashlib
import json
import runpy
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify-agileplus-receipt.py"
FIXTURES = ROOT / "tests/fixtures/agileplus"
RECEIPT = FIXTURES / "accepted-todo-receipt.json"
EXPECTED = FIXTURES / "expected-todo-work.json"
VERIFY = runpy.run_path(str(SCRIPT))["verify"]
LOAD = runpy.run_path(str(SCRIPT))["load_json"]


class ReceiptBoundary(unittest.TestCase):
    def setUp(self):
        self.raw = RECEIPT.read_bytes()
        self.receipt = json.loads(self.raw)
        self.expected = json.loads(EXPECTED.read_bytes())
        self.digest = hashlib.sha256(self.raw).hexdigest()

    def check(self, receipt=None, expected=None):
        raw = json.dumps(receipt if receipt is not None else self.receipt).encode()
        return VERIFY(
            raw,
            expected if expected is not None else self.expected,
            hashlib.sha256(raw).hexdigest(),
        )

    def test_native_fixture_does_not_accept_product(self):
        report = VERIFY(self.raw, self.expected, self.digest)
        self.assertEqual(report["status"], "receipt_preflight_only")
        self.assertFalse(report["product_reconciled"])
        self.assertIn("producer_authentication_and_authority", report["unverified"])
        self.assertIn(
            "independent_evaluation_and_evidence_contents", report["unverified"]
        )

    def test_semantic_mutations_fail_even_with_recomputed_digest(self):
        changes = {
            "feature_id": 2,
            "governance_contract_id": 2,
            "governance_version": 2,
            "event_id": True,
            "audit_ids": [],
            "committed_at": "2026-10-26T00:00:00",
            "actor": " ",
        }
        for key, value in changes.items():
            with self.subTest(field=key), self.assertRaises(ValueError):
                receipt = copy.deepcopy(self.receipt)
                receipt[key] = value
                self.check(receipt)

    def test_stale_or_wrong_candidate_identity_rejected(self):
        changes = {
            "wp_id": 2,
            "assignment_id": "different-assignment",
            "attempt_id": "earlier-attempt",
            "evaluation_id": "different-evaluation",
            "candidate_ref": "git:" + "2" * 40,
        }
        for key, value in changes.items():
            with self.subTest(field=key), self.assertRaises(ValueError):
                receipt = copy.deepcopy(self.receipt)
                receipt["accepted_candidates"][0][key] = value
                self.check(receipt)

    def test_mutated_retry_cannot_reuse_pinned_digest(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["request_id"] = "same-work-different-receipt"
        with self.assertRaisesRegex(ValueError, "receipt_digest_mismatch"):
            VERIFY(json.dumps(receipt).encode(), self.expected, self.digest)

    def test_duplicate_work_or_audit_identity_rejected(self):
        for field in ("accepted_candidates", "audit_ids"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                receipt = copy.deepcopy(self.receipt)
                receipt[field] *= 2
                self.check(receipt)

    def test_schema_drift_and_boolean_ids_rejected(self):
        for receipt in (
            {**self.receipt, "source": "agileplus"},
            {**self.receipt, "feature_id": True},
            {**self.receipt, "audit_ids": [True]},
            {**self.receipt, "accepted_candidates": []},
        ):
            with self.subTest(receipt=receipt), self.assertRaises(ValueError):
                self.check(receipt)

    def test_json_ambiguity_rejected(self):
        for raw in (b'{"event_id":1,"event_id":2}', b'{"event_id":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                LOAD(raw)

    def test_missing_producer_graph_binding_stays_unverified(self):
        expected = copy.deepcopy(self.expected)
        expected["graph_revision"] = "newer-baseline-not-in-native-receipt"
        report = self.check(expected=expected)
        self.assertFalse(report["product_reconciled"])
        self.assertIn("graph_revision_and_proposal_linkage", report["unverified"])

    def test_actor_and_chronology_do_not_establish_authority_or_freshness(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["actor"] = "untrusted-self-reported-owner"
        receipt["committed_at"] = "2999-01-01T00:00:00Z"
        report = self.check(receipt)
        self.assertFalse(report["product_reconciled"])
        self.assertIn("producer_authentication_and_authority", report["unverified"])
        self.assertIn("receipt_chronology_and_freshness", report["unverified"])

    def test_cold_process_and_retry_are_observations_only(self):
        command = [
            sys.executable,
            str(SCRIPT),
            str(RECEIPT),
            "--expected",
            str(EXPECTED),
            "--receipt-sha256",
            self.digest,
        ]
        reports = []
        for _ in range(2):
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            reports.append(json.loads(result.stdout))
        self.assertEqual(reports[0], reports[1])
        self.assertFalse(reports[1]["product_reconciled"])
        self.assertIn(
            "production_replay_and_restart_durability", reports[1]["unverified"]
        )

    def test_cli_rejects_untrusted_or_missing_input(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(RECEIPT),
                "--expected",
                str(EXPECTED),
                "--receipt-sha256",
                "0" * 64,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout),
            {"status": "rejected", "product_reconciled": False},
        )


if __name__ == "__main__":
    unittest.main()
