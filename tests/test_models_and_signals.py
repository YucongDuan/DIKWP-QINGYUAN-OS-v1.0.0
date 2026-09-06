from __future__ import annotations

import json
import unittest
from pathlib import Path

from qingyuan_os.models import ContentItem, ScenarioError
from qingyuan_os.signals import scan_text

ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_valid_item(self) -> None:
        item = ContentItem.from_dict(self.load("01_negative_truth_public_warning.json"))
        self.assertEqual(item.item_id, "QY-EX-01")
        self.assertEqual(item.channel, "online")

    def test_missing_item_id_rejected(self) -> None:
        data = self.load("01_negative_truth_public_warning.json")
        data.pop("item_id")
        with self.assertRaises(ScenarioError):
            ContentItem.from_dict(data)

    def test_empty_text_rejected(self) -> None:
        data = self.load("01_negative_truth_public_warning.json")
        data["text"] = ""
        with self.assertRaises(ScenarioError):
            ContentItem.from_dict(data)

    def test_external_action_authority_must_be_zero(self) -> None:
        data = self.load("01_negative_truth_public_warning.json")
        data["purpose"]["automatic_external_action_authority"] = 1
        with self.assertRaises(ScenarioError):
            ContentItem.from_dict(data)

    def test_claim_evidence_parsed(self) -> None:
        item = ContentItem.from_dict(self.load("01_negative_truth_public_warning.json"))
        self.assertEqual(len(item.claims), 1)
        self.assertEqual(len(item.claims[0].evidence), 2)

    def test_unknown_claim_type_becomes_other(self) -> None:
        data = self.load("01_negative_truth_public_warning.json")
        data["claims"][0]["type"] = "mystical"
        item = ContentItem.from_dict(data)
        self.assertEqual(item.claims[0].claim_type, "other")

    def test_unsupported_channel_rejected(self) -> None:
        data = self.load("01_negative_truth_public_warning.json")
        data["channel"] = "telepathy"
        with self.assertRaises(ScenarioError):
            ContentItem.from_dict(data)

    def test_as_dict_round_trip_core(self) -> None:
        item = ContentItem.from_dict(self.load("04_guaranteed_investment_group.json"))
        clone = ContentItem.from_dict(item.as_dict())
        self.assertEqual(clone.item_id, item.item_id)
        self.assertEqual(clone.text, item.text)


class SignalTests(unittest.TestCase):
    def test_medical_displacement(self) -> None:
        result = scan_text("三天逆转糖尿病，不用看医生，立即停药")
        self.assertGreater(result["category_scores"]["medical_displacement"], 0)

    def test_financial_guarantee(self) -> None:
        result = scan_text("稳赚不赔，养老钱翻倍，内部投资渠道")
        self.assertGreater(result["category_scores"]["financial_guarantee"], 0)

    def test_secrecy(self) -> None:
        result = scan_text("不要告诉家人，他们不想让你知道")
        self.assertGreater(result["category_scores"]["secrecy_isolation"], 0)

    def test_urgency(self) -> None:
        result = scan_text("最后机会，仅限今天，立即购买")
        self.assertGreater(result["category_scores"]["urgency_scarcity"], 0)

    def test_positive_pseudo_knowledge(self) -> None:
        result = scan_text("量子能量可以改写人生，绝对有效")
        self.assertGreater(result["category_scores"]["pseudo_knowledge_packaging"], 0)
        self.assertGreater(result["category_scores"]["absolute_certainty"], 0)

    def test_quoted_context_discount(self) -> None:
        raw = scan_text("报道引用骗子的话：稳赚不赔，不要告诉家人")
        quoted = scan_text("报道引用骗子的话：稳赚不赔，不要告诉家人", {"quoted_or_reported": True})
        self.assertLess(quoted["category_scores"]["secrecy_isolation"], raw["category_scores"]["secrecy_isolation"])

    def test_satire_context_discount(self) -> None:
        raw = scan_text("绝对有效，稳赚不赔")
        satire = scan_text("绝对有效，稳赚不赔", {"satire": True})
        self.assertLess(satire["category_scores"]["absolute_certainty"], raw["category_scores"]["absolute_certainty"])

    def test_screening_not_verdict_note(self) -> None:
        result = scan_text("最后机会")
        self.assertIn("not proof", result["note"])


if __name__ == "__main__":
    unittest.main()
