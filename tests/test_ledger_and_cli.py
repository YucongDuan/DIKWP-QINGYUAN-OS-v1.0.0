from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from qingyuan_os.ledger import HashLedger

ROOT = Path(__file__).resolve().parents[1]


class LedgerTests(unittest.TestCase):
    def test_empty_ledger_valid(self) -> None:
        valid, errors = HashLedger.verify_records([])
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_ledger_tamper_detected(self) -> None:
        ledger = HashLedger()
        ledger.append("one", {"x": 1}, stage="S1")
        ledger.append("two", {"y": 2}, stage="S2")
        ledger.records[0]["payload"]["x"] = 9
        valid, errors = HashLedger.verify_records(ledger.records)
        self.assertFalse(valid)
        self.assertTrue(any("hash mismatch" in error for error in errors))

    def test_ledger_order_tamper_detected(self) -> None:
        ledger = HashLedger()
        ledger.append("one", {}, stage="S1")
        ledger.append("two", {}, stage="S2")
        ledger.records.reverse()
        valid, _ = HashLedger.verify_records(ledger.records)
        self.assertFalse(valid)


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "qingyuan_os", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_inspect(self) -> None:
        result = self.run_cli("inspect")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["automatic_external_action_authority"], 0)
        self.assertFalse(payload["automatic_deletion"])

    def test_assess(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                "assess", str(ROOT / "examples" / "01_negative_truth_public_warning.json"),
                "--output", directory,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(directory) / "qingyuan_certificate.json").exists())

    def test_demo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("demo", "--output", directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["item_id"], "QY-EX-02")

    def test_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("suite", "--examples", str(ROOT / "examples"), "--output", directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload["runs"]), 8)

    def test_verify(self) -> None:
        ledger = ROOT / "outputs" / "reference" / "01_negative_truth_public_warning" / "evidence_ledger.jsonl"
        result = self.run_cli("verify", str(ledger))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
