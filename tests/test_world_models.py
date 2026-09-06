from __future__ import annotations

import json
import unittest
from pathlib import Path

from qingyuan_os.models import ContentItem
from qingyuan_os.signals import scan_text
from qingyuan_os.world_models import evidence_world_model, harm_and_rights_world_model, manipulation_world_model

ROOT = Path(__file__).resolve().parents[1]


class WorldModelTests(unittest.TestCase):
    def build(self, name: str):
        data = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
        item = ContentItem.from_dict(data)
        signals = scan_text(item.text, item.context)
        evidence = evidence_world_model(item, signals)
        manipulation = manipulation_world_model(item, signals, evidence)
        harm = harm_and_rights_world_model(item, signals, evidence, manipulation)
        return item, signals, evidence, manipulation, harm

    def test_primary_evidence_scores_high(self) -> None:
        _, _, evidence, _, _ = self.build("01_negative_truth_public_warning.json")
        self.assertGreaterEqual(evidence["mean_evidence_quality"], 0.8)

    def test_testimonial_not_treated_as_strong_proof(self) -> None:
        _, _, evidence, _, _ = self.build("02_elderly_miracle_course.json")
        self.assertLess(evidence["mean_evidence_quality"], 0.4)

    def test_opinion_not_forced_into_factual_verdict(self) -> None:
        data = json.loads((ROOT / "examples" / "07_unverifiable_conspiracy_claim.json").read_text(encoding="utf-8"))
        data["claims"][0]["type"] = "opinion"
        item = ContentItem.from_dict(data)
        evidence = evidence_world_model(item, scan_text(item.text, item.context))
        self.assertEqual(evidence["claim_results"][0]["status"], "VALUE_OR_EXPRESSIVE_CLAIM")

    def test_miracle_course_high_pressure(self) -> None:
        _, _, _, manipulation, _ = self.build("02_elderly_miracle_course.json")
        self.assertGreater(manipulation["manipulation_pressure"], 0.5)

    def test_addictive_feed_detected_from_design(self) -> None:
        _, _, _, manipulation, _ = self.build("03_addictive_short_video.json")
        self.assertGreater(manipulation["addictive_design"], 0.8)

    def test_vulnerable_targeting_detected(self) -> None:
        _, _, _, manipulation, _ = self.build("04_guaranteed_investment_group.json")
        self.assertGreater(manipulation["vulnerable_targeting"], 0.6)

    def test_public_interest_critique_has_suppression_protection(self) -> None:
        _, _, _, _, harm = self.build("05_evidence_based_institutional_critique.json")
        self.assertGreaterEqual(harm["suppression_protection"], 0.8)

    def test_negative_warning_preservation(self) -> None:
        _, _, _, _, harm = self.build("01_negative_truth_public_warning.json")
        self.assertGreater(harm["negative_truth_preservation"], 0.6)

    def test_emotional_valence_not_truth(self) -> None:
        _, _, _, _, harm = self.build("01_negative_truth_public_warning.json")
        self.assertTrue(harm["emotional_valence_is_not_truth"])

    def test_commercial_conflict_high_in_affiliate_course(self) -> None:
        _, _, _, manipulation, _ = self.build("06_fake_positive_testimonial_product.json")
        self.assertGreater(manipulation["commercial_conflict"], 0.7)


if __name__ == "__main__":
    unittest.main()
