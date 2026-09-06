from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from qingyuan_os.engine import QingyuanEngine, write_run_outputs
from qingyuan_os.ledger import HashLedger

ROOT = Path(__file__).resolve().parents[1]


class EngineScenarioTests(unittest.TestCase):
    def run_case(self, name: str):
        data = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
        engine = QingyuanEngine(data)
        return engine, engine.run()

    def test_negative_truth_preserved(self) -> None:
        _, result = self.run_case("01_negative_truth_public_warning.json")
        self.assertEqual(result["intervention_plan"]["disposition"], "PRESERVE_AND_SURFACE")

    def test_institutional_critique_preserved(self) -> None:
        _, result = self.run_case("05_evidence_based_institutional_critique.json")
        self.assertEqual(result["intervention_plan"]["disposition"], "PRESERVE_AND_SURFACE")

    def test_miracle_course_escalates(self) -> None:
        _, result = self.run_case("02_elderly_miracle_course.json")
        self.assertEqual(result["intervention_plan"]["disposition"], "HIGH_RISK_AUTHORIZED_REVIEW")

    def test_investment_scam_escalates(self) -> None:
        _, result = self.run_case("04_guaranteed_investment_group.json")
        self.assertEqual(result["intervention_plan"]["disposition"], "HIGH_RISK_AUTHORIZED_REVIEW")

    def test_addictive_feed_breaks_amplification(self) -> None:
        _, result = self.run_case("03_addictive_short_video.json")
        types = {a["action_type"] for a in result["intervention_plan"]["actions"]}
        self.assertIn("DEAMPLIFY_RECOMMENDATION_FEEDBACK_LOOP", types)

    def test_positive_packaging_not_trusted(self) -> None:
        _, result = self.run_case("06_fake_positive_testimonial_product.json")
        types = {a["action_type"] for a in result["intervention_plan"]["actions"]}
        self.assertIn("PAUSE_MONETIZATION_AND_REQUIRE_DISCLOSURE", types)

    def test_unverifiable_claim_contextualized_not_deleted(self) -> None:
        _, result = self.run_case("07_unverifiable_conspiracy_claim.json")
        self.assertEqual(result["intervention_plan"]["disposition"], "PRESERVE_WITH_CONTEXT")
        self.assertFalse(result["certificate"]["automatic_deletion"])

    def test_offline_support_plan_applicable(self) -> None:
        _, result = self.run_case("08_offline_family_high_control_sales.json")
        self.assertTrue(result["real_life_support_plan"]["applicable"])
        self.assertIn("WITHOUT_FORCED_BELIEF_CHANGE", result["real_life_support_plan"]["mode"])

    def test_no_person_classification(self) -> None:
        _, result = self.run_case("08_offline_family_high_control_sales.json")
        self.assertTrue(result["intervention_plan"]["rights_firewall"]["no_person_is_classified_as_a_problem"])

    def test_no_action_auto_executes(self) -> None:
        _, result = self.run_case("02_elderly_miracle_course.json")
        self.assertTrue(all(not action["automatic_execution"] for action in result["intervention_plan"]["actions"]))

    def test_all_high_impact_actions_are_appealable(self) -> None:
        _, result = self.run_case("02_elderly_miracle_course.json")
        self.assertTrue(all(action["appeal_available"] for action in result["intervention_plan"]["actions"]))

    def test_semantic_closure_vector(self) -> None:
        _, result = self.run_case("02_elderly_miracle_course.json")
        self.assertEqual(result["semantic_graph"]["closure_vector"], "11111")

    def test_twenty_five_route_types(self) -> None:
        _, result = self.run_case("02_elderly_miracle_course.json")
        self.assertEqual(len(result["semantic_graph"]["allowed_route_types"]), 25)

    def test_three_world_models_retained(self) -> None:
        _, result = self.run_case("07_unverifiable_conspiracy_claim.json")
        self.assertEqual(len(result["model_disagreement"]["non_isomorphic_models_retained"]), 3)

    def test_reality_debt_for_circuit_break(self) -> None:
        _, result = self.run_case("03_addictive_short_video.json")
        types = {r["type"] for r in result["residual_queue"]["open_items"]}
        self.assertIn("REAL_WORLD_OUTCOME_DEBT", types)

    def test_run_is_deterministic(self) -> None:
        _, first = self.run_case("06_fake_positive_testimonial_product.json")
        _, second = self.run_case("06_fake_positive_testimonial_product.json")
        self.assertEqual(first["run_hash"], second["run_hash"])
        self.assertEqual(first["ledger_head_hash"], second["ledger_head_hash"])

    def test_output_files_and_ledger(self) -> None:
        engine, result = self.run_case("02_elderly_miracle_course.json")
        with tempfile.TemporaryDirectory() as directory:
            summary = write_run_outputs(Path(directory), engine, result)
            self.assertTrue((Path(directory) / "qingyuan_certificate.json").exists())
            self.assertTrue((Path(directory) / "report.zh-CN.md").exists())
            valid, errors, records = HashLedger.read_and_verify(Path(directory) / "evidence_ledger.jsonl")
            self.assertTrue(valid, errors)
            self.assertEqual(len(records), 10)
            self.assertEqual(summary["run_hash"], result["run_hash"])


if __name__ == "__main__":
    unittest.main()
