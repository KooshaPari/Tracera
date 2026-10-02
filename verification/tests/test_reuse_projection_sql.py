"""Execute the production reuse SELECT against the real additive SQLite DDL.

This is SQL-layer evidence only. It is not a Rust, HTTP, or Postgres test.
Run: python3 -m unittest discover -s verification/tests -p test_reuse_projection_sql.py -v
"""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "crates/tracera-server"
SQL_DIR = SERVER / "src/product/sql"
STAMP = "2026-10-02T10:00:00+00:00"


class ReuseProjectionSqlTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.row_factory = sqlite3.Row
        for filename in ("010_product_persistence_v1.sql", "011_product_invalidation_v1.sql"):
            self.db.executescript((SERVER / "migrations-sqlite" / filename).read_text())
        self.query = (SQL_DIR / "reuse_for_target.sqlite.sql").read_text()
        for product, baseline in (("p-a", "b-a"), ("p-b", "b-b")):
            self.db.execute(
                "INSERT INTO product_baselines_v1 "
                "(baseline_id,product_id,revision_number,accepted_at) VALUES (?,?,1,?)",
                (baseline, product, STAMP),
            )
        self.observation("o-a", "p-a", "b-a")
        self.observation("o-b", "p-b", "b-b")
        # A historical/raw row can claim product A while its source baseline is B.
        self.observation("o-bad", "p-a", "b-b")
        self.decision("r-a2", "o-a", "b-a", "git:target")
        self.decision("r-a1", "o-a", "b-a", "git:target")
        self.decision("r-other", "o-a", "b-a", "git:other")
        self.decision("r-b", "o-b", "b-b", "git:target")
        self.decision("r-cross", "o-b", "b-a", "git:target")
        self.decision("r-bad-source", "o-bad", "b-a", "git:target")

    def observation(self, identity, product, baseline):
        self.db.execute(
            "INSERT INTO product_observations_v1 "
            "(observation_id,product_id,baseline_id,candidate_ref,result,"
            "verifier_id,verifier_version,recorded_at) VALUES (?,?,?,'git:observed',"
            "'passed','suite','1',?)",
            (identity, product, baseline, STAMP),
        )

    def decision(self, identity, observation, baseline, candidate):
        self.db.execute(
            "INSERT INTO evidence_reuse_decisions_v1 "
            "(reuse_decision_id,observation_id,target_baseline_id,target_candidate_ref,"
            "criterion_ref,applicability_state,policy_version,reason,decided_at) "
            "VALUES (?,?,?,?,'criterion','current_valid','v1','fixture',?)",
            (identity, observation, baseline, candidate, STAMP),
        )

    def ids(self, product="p-a", baseline="b-a", candidate="git:target", limit=100):
        rows = self.db.execute(self.query, (product, baseline, candidate, limit))
        return [row["reuse_decision_id"] for row in rows]

    def test_exact_product_baseline_and_candidate(self):
        self.assertEqual(self.ids(), ["r-a1", "r-a2"])
        self.assertEqual(self.ids("p-b", "b-b"), ["r-b"])
        self.assertEqual(self.ids(candidate="git:other"), ["r-other"])

    def test_foreign_target_baseline_returns_no_rows(self):
        self.assertEqual(self.ids("p-a", "b-b"), [])
        self.assertEqual(self.ids("p-b", "b-a"), [])

    def test_foreign_observation_cannot_be_projected(self):
        self.assertNotIn("r-cross", self.ids())

    def test_forged_source_baseline_cannot_be_projected(self):
        self.assertNotIn("r-bad-source", self.ids())

    def test_missing_product_baseline_or_candidate_has_no_rows(self):
        self.assertEqual(self.ids(product="missing"), [])
        self.assertEqual(self.ids(baseline="missing"), [])
        self.assertEqual(self.ids(candidate="missing"), [])

    def test_bound_and_deterministic_tie_break(self):
        self.assertEqual(self.ids(limit=1), ["r-a1"])
        self.assertEqual(self.ids(limit=2), ["r-a1", "r-a2"])
        self.assertEqual(self.ids(), self.ids())

    def test_reference_text_is_bound_not_interpolated(self):
        self.assertEqual(self.ids(candidate="' OR 1=1 --"), [])
        candidate = "git:branch/a?mode=+&tag=one"
        self.decision("r-special", "o-a", "b-a", candidate)
        self.assertEqual(self.ids(candidate=candidate), ["r-special"])

    def test_queries_do_not_rewrite_observation_history(self):
        before = [
            tuple(row)
            for row in self.db.execute(
                "SELECT * FROM product_observations_v1 ORDER BY observation_id"
            )
        ]
        self.ids()
        after = [
            tuple(row)
            for row in self.db.execute(
                "SELECT * FROM product_observations_v1 ORDER BY observation_id"
            )
        ]
        self.assertEqual(before, after)

    def test_previous_empty_membership_probe_was_not_an_ownership_check(self):
        members = self.db.execute(
            "SELECT r.entity_revision_id FROM baseline_entity_membership_v1 m "
            "JOIN product_entities_v1 e ON e.entity_id=m.entity_id "
            "JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id "
            "WHERE m.baseline_id=? AND e.product_id=? LIMIT 1",
            ("b-b", "p-a"),
        ).fetchall()
        self.assertEqual(members, [])
        unscoped = self.db.execute(
            "SELECT reuse_decision_id FROM evidence_reuse_decisions_v1 "
            "WHERE target_baseline_id=? AND target_candidate_ref=?",
            ("b-b", "git:target"),
        ).fetchall()
        self.assertEqual([row[0] for row in unscoped], ["r-b"])
        self.assertEqual(self.ids("p-a", "b-b"), [])

    def test_postgres_select_has_same_predicates_and_parameter_order(self):
        pg = (SQL_DIR / "reuse_for_target.postgres.sql").read_text()
        self.assertEqual(re.sub(r"\$(\d+)", r"?\1", pg), self.query)


if __name__ == "__main__":
    unittest.main()
