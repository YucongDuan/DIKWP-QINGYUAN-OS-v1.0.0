from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from qingyuan_os.shield import apply_local_shield, write_shield_outputs

ROOT = Path(__file__).resolve().parents[1]


class LocalShieldTests(unittest.TestCase):
    def feed(self):
        return json.loads((ROOT / "demo_feed" / "mixed_feed.json").read_text(encoding="utf-8"))

    def test_mixed_feed_item_count(self) -> None:
        result = apply_local_shield(self.feed())
        self.assertEqual(len(result["safe_feed"]), 5)

    def test_negative_truth_is_surfaced(self) -> None:
        result = apply_local_shield(self.feed())
        item = next(x for x in result["safe_feed"] if x["item_id"] == "QY-EX-01")
        self.assertEqual(item["local_state"], "PRESERVED_AND_SURFACED")

    def test_institutional_critique_is_surfaced(self) -> None:
        result = apply_local_shield(self.feed())
        item = next(x for x in result["safe_feed"] if x["item_id"] == "QY-EX-05")
        self.assertEqual(item["local_state"], "PRESERVED_AND_SURFACED")

    def test_high_risk_item_is_locally_held_not_deleted(self) -> None:
        result = apply_local_shield(self.feed())
        item = next(x for x in result["safe_feed"] if x["item_id"] == "QY-EX-02")
        self.assertEqual(item["local_state"], "HELD_FROM_DEFAULT_VIEW_PENDING_REVIEW")
        self.assertFalse(item["source_deleted"])

    def test_high_risk_original_is_archived(self) -> None:
        result = apply_local_shield(self.feed())
        archived = {x["item_id"] for x in result["quarantine_archive"]}
        self.assertIn("QY-EX-02", archived)

    def test_addictive_feed_autoplay_disabled(self) -> None:
        result = apply_local_shield(self.feed())
        item = next(x for x in result["safe_feed"] if x["item_id"] == "QY-EX-03")
        self.assertFalse(item["autoplay"])
        self.assertEqual(item["recommendation_boost"], 0)

    def test_uncertain_claim_kept_with_context(self) -> None:
        result = apply_local_shield(self.feed())
        item = next(x for x in result["safe_feed"] if x["item_id"] == "QY-EX-07")
        self.assertEqual(item["local_state"], "VISIBLE_WITH_CONTEXT")

    def test_shield_invariants(self) -> None:
        result = apply_local_shield(self.feed())
        self.assertEqual(result["invariants"]["automatic_external_action_authority"], 0)
        self.assertFalse(result["invariants"]["source_deletion"])
        self.assertTrue(result["invariants"]["local_user_controlled_transformation"])

    def test_write_outputs(self) -> None:
        result = apply_local_shield(self.feed())
        with tempfile.TemporaryDirectory() as directory:
            manifest = write_shield_outputs(Path(directory), result)
            self.assertTrue((Path(directory) / "safe_feed.json").exists())
            self.assertTrue((Path(directory) / "quarantine_archive.json").exists())
            self.assertGreaterEqual(manifest["locally_held_count"], 1)


if __name__ == "__main__":
    unittest.main()
