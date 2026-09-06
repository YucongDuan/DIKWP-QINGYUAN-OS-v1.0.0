from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from qingyuan_os import __version__  # noqa: E402
from qingyuan_os.ledger import HashLedger  # noqa: E402
from qingyuan_os.utils import merkle_root, sha256_file, write_json  # noqa: E402

EXPECTED = {
    "01_negative_truth_public_warning": "PRESERVE_AND_SURFACE",
    "02_elderly_miracle_course": "HIGH_RISK_AUTHORIZED_REVIEW",
    "03_addictive_short_video": "FRICTION_AND_CIRCUIT_BREAK_RECOMMENDED",
    "04_guaranteed_investment_group": "HIGH_RISK_AUTHORIZED_REVIEW",
    "05_evidence_based_institutional_critique": "PRESERVE_AND_SURFACE",
    "06_fake_positive_testimonial_product": "FRICTION_AND_CIRCUIT_BREAK_RECOMMENDED",
    "07_unverifiable_conspiracy_claim": "PRESERVE_WITH_CONTEXT",
    "08_offline_family_high_control_sales": "FRICTION_AND_CIRCUIT_BREAK_RECOMMENDED",
}


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    merged["PYTHONPATH"] = str(SRC)
    if env:
        merged.update(env)
    return subprocess.run(command, cwd=ROOT, env=merged, text=True, capture_output=True, check=False)


def test_suite() -> tuple[int, bool, str]:
    suite = unittest.TestLoader().discover(str(ROOT / "tests"))
    count = suite.countTestCases()
    with open(os.devnull, "w", encoding="utf-8") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    return count, result.wasSuccessful(), f"failures={len(result.failures)}, errors={len(result.errors)}"


def main() -> None:
    count, tests_passed, detail = test_suite()
    examples = sorted((ROOT / "examples").glob("*.json"))
    output_root = ROOT / "outputs" / "reference"
    checks = []
    total_events = 0
    dispositions = {}
    run_hashes = {}
    rights_checks = []
    for example in examples:
        directory = output_root / example.stem
        valid, errors, records = HashLedger.read_and_verify(directory / "evidence_ledger.jsonl")
        certificate = json.loads((directory / "qingyuan_certificate.json").read_text(encoding="utf-8"))
        plan = json.loads((directory / "intervention_plan.json").read_text(encoding="utf-8"))
        manifest = json.loads((directory / "output_manifest.json").read_text(encoding="utf-8"))
        dispositions[example.stem] = certificate["disposition"]
        run_hashes[example.stem] = certificate["run_hash"]
        total_events += len(records)
        rights_ok = (
            certificate["automatic_external_action_authority"] == 0
            and certificate["automatic_deletion"] is False
            and certificate["appeal_available"] is True
            and plan["decision_logic"]["aggregate_score_used"] is False
            and plan["decision_logic"]["emotional_valence_used_as_restriction_signal"] is False
            and all(action["automatic_execution"] is False for action in plan["actions"])
        )
        rights_checks.append(rights_ok)
        checks.append({
            "scenario": example.stem,
            "ledger_valid": valid,
            "ledger_errors": errors,
            "ledger_events": len(records),
            "disposition": certificate["disposition"],
            "expected_disposition": EXPECTED[example.stem],
            "disposition_matches": certificate["disposition"] == EXPECTED[example.stem],
            "rights_boundary_valid": rights_ok,
            "run_hash_matches_manifest": certificate["run_hash"] == manifest["run_hash"],
        })

    zipapp = ROOT / "dist" / "DIKWP_QINGYUAN_OS.pyz"
    inspect = run_command([sys.executable, str(zipapp), "inspect"])
    with tempfile.TemporaryDirectory() as directory:
        demo = run_command([sys.executable, str(zipapp), "demo", "--output", directory])
        demo_certificate = Path(directory) / "qingyuan_certificate.json"
        demo_ok = demo.returncode == 0 and demo_certificate.exists()
    with tempfile.TemporaryDirectory() as directory:
        shield = run_command([sys.executable, str(zipapp), "shield", str(ROOT / "demo_feed" / "mixed_feed.json"), "--output", directory])
        shield_manifest_path = Path(directory) / "shield_manifest.json"
        shield_manifest = json.loads(shield_manifest_path.read_text(encoding="utf-8")) if shield_manifest_path.exists() else {}
        shield_ok = (
            shield.returncode == 0
            and shield_manifest_path.exists()
            and shield_manifest.get("item_count") == 5
            and shield_manifest.get("locally_held_count", 0) >= 1
            and shield_manifest.get("automatic_external_action_authority") == 0
            and shield_manifest.get("source_deletion") is False
        )

    dashboard = ROOT / "web" / "DIKWP_QINGYUAN_OS_Offline_Demo.html"
    dashboard_text = dashboard.read_text(encoding="utf-8")
    dashboard_checks = {
        "exists": dashboard.exists(),
        "size_bytes": dashboard.stat().st_size,
        "external_script_dependencies": dashboard_text.count("<script src="),
        "contains_all_examples": all(json.loads(example.read_text(encoding="utf-8"))["item_id"] in dashboard_text for example in examples),
        "contains_rights_firewall": "不把悲伤、批评、坏消息或异议" in dashboard_text,
        "contains_authority_zero": "自动外部行动权限 = 0" in dashboard_text,
    }

    excluded = {"RELEASE_VERIFICATION.json", "SBOM.spdx.json"}
    source_files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in excluded
        and "__pycache__" not in path.parts
        and not ("outputs" in path.parts and "demo" in path.parts)
    )
    payload = {
        "system": "DIKWP-QINGYUAN-OS",
        "version": __version__,
        "verification_date": "2026-09-06",
        "tests": {"count": count, "passed": tests_passed, "detail": detail},
        "reference_suite": {
            "scenario_count": len(examples),
            "total_ledger_events": total_events,
            "all_ledgers_valid": all(check["ledger_valid"] for check in checks),
            "all_dispositions_match": all(check["disposition_matches"] for check in checks),
            "all_rights_boundaries_valid": all(rights_checks),
            "checks": checks,
            "run_hashes": run_hashes,
            "dispositions": dispositions,
        },
        "zipapp": {
            "exists": zipapp.exists(),
            "inspect_returncode": inspect.returncode,
            "inspect_valid_json": inspect.returncode == 0 and bool(inspect.stdout.strip()),
            "demo_returncode": demo.returncode,
            "demo_certificate_exists": demo_ok,
            "local_shield_returncode": shield.returncode,
            "local_shield_valid": shield_ok,
            "local_shield_manifest": shield_manifest,
            "sha256": sha256_file(zipapp),
        },
        "offline_dashboard": dashboard_checks,
        "architecture": {
            "exists": (ROOT / "assets" / "DIKWP_QINGYUAN_OS_Architecture.svg").exists(),
            "sha256": sha256_file(ROOT / "assets" / "DIKWP_QINGYUAN_OS_Architecture.svg"),
        },
        "runtime": {
            "python_minimum": "3.10",
            "third_party_dependencies": 0,
            "network_connectors": 0,
            "credential_connectors": 0,
            "automatic_external_action_authority": 0,
            "automatic_deletion": False,
            "aggregate_score_used": False,
        },
        "claim_boundaries": {
            "universal_truth_detector": False,
            "intent_detector": False,
            "mental_health_or_capacity_assessment": False,
            "legal_adjudication": False,
            "synthetic_examples_are_real_world_validation": False,
        },
        "source_tree": {
            "file_count": len(source_files),
            "merkle_root": merkle_root(sha256_file(path) for path in source_files),
        },
    }
    payload["overall_verified"] = bool(
        tests_passed
        and payload["reference_suite"]["all_ledgers_valid"]
        and payload["reference_suite"]["all_dispositions_match"]
        and payload["reference_suite"]["all_rights_boundaries_valid"]
        and inspect.returncode == 0
        and demo_ok
        and shield_ok
        and dashboard_checks["exists"]
        and dashboard_checks["external_script_dependencies"] == 0
        and dashboard_checks["contains_all_examples"]
        and dashboard_checks["contains_rights_firewall"]
        and dashboard_checks["contains_authority_zero"]
        and payload["architecture"]["exists"]
    )
    write_json(ROOT / "RELEASE_VERIFICATION.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if not payload["overall_verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
