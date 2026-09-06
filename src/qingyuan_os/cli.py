from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

from . import __version__
from .engine import QingyuanEngine, write_run_outputs
from .ledger import HashLedger
from .models import ScenarioError
from .shield import apply_local_shield, write_shield_outputs
from .utils import read_json


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "examples").exists() and (parent / "src").exists():
            return parent
    return Path.cwd()


def _packaged_names() -> list[str]:
    root = resources.files("qingyuan_os").joinpath("data", "examples")
    return sorted(item.name for item in root.iterdir() if item.name.endswith(".json"))


def _packaged(name: str) -> dict[str, Any]:
    text = resources.files("qingyuan_os").joinpath("data", "examples", name).read_text(encoding="utf-8")
    return json.loads(text)


def _run_data(data: dict[str, Any], output: Path, source: str) -> dict[str, Any]:
    engine = QingyuanEngine(data)
    result = engine.run()
    summary = write_run_outputs(output, engine, result)
    summary["source"] = source
    return summary


def command_assess(args: argparse.Namespace) -> int:
    try:
        summary = _run_data(read_json(Path(args.input)), Path(args.output), str(args.input))
    except (OSError, ValueError, ScenarioError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_demo(args: argparse.Namespace) -> int:
    root = _project_root()
    name = "02_elderly_miracle_course.json"
    local = root / "examples" / name
    try:
        data = read_json(local) if local.exists() else _packaged(name)
        summary = _run_data(data, Path(args.output), str(local) if local.exists() else f"package:{name}")
    except (OSError, ValueError, ScenarioError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_suite(args: argparse.Namespace) -> int:
    directory = Path(args.examples)
    if directory.exists():
        items = [(path.name, read_json(path), str(path)) for path in sorted(directory.glob("*.json"))]
    elif args.examples == "examples":
        items = [(name, _packaged(name), f"package:{name}") for name in _packaged_names()]
    else:
        print(f"ERROR: examples directory not found: {directory}", file=sys.stderr)
        return 2
    runs: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for name, data, source in items:
        try:
            runs.append(_run_data(data, Path(args.output) / Path(name).stem, source))
        except Exception as exc:  # isolate individual scenarios at CLI boundary
            failures.append({"source": source, "error": str(exc)})
    print(json.dumps({"system": "DIKWP-QINGYUAN-OS", "version": __version__, "runs": runs, "failures": failures}, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failures else 0



def command_shield(args: argparse.Namespace) -> int:
    try:
        result = apply_local_shield(read_json(Path(args.feed)))
        manifest = write_shield_outputs(Path(args.output), result)
    except (OSError, ValueError, ScenarioError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    try:
        valid, errors, records = HashLedger.read_and_verify(Path(args.ledger))
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = {
        "valid": valid,
        "record_count": len(records),
        "head_hash": records[-1]["hash"] if records else None,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if valid else 1


def command_inspect(args: argparse.Namespace) -> int:
    payload = {
        "system": "DIKWP-QINGYUAN-OS",
        "version": __version__,
        "chinese_name": "清源：主动认知环境免疫、操纵断链与证据回流系统",
        "mission": "reduce harmful manipulation, addictive amplification, pseudo-knowledge monetization, and high-stakes misinformation while preserving negative truth, dissent, autonomy, and appeal",
        "world_models": ["provenance-and-verifiability", "pressure-addiction-and-incentive", "harm-autonomy-and-expression-rights"],
        "intervention_ladder": list(range(8)),
        "aggregate_score_used": False,
        "automatic_deletion": False,
        "automatic_external_action_authority": 0,
        "person_classification": "not supported",
        "examples": _packaged_names(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dikwp-qingyuan",
        description="Evidence-return and manipulation-circuit-breaking runtime with a rights-preserving intervention ladder",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    assess = sub.add_parser("assess", help="assess one online/offline content item")
    assess.add_argument("input")
    assess.add_argument("--output", required=True)
    assess.set_defaults(func=command_assess)

    demo = sub.add_parser("demo", help="run the packaged monetized pseudo-knowledge example")
    demo.add_argument("--output", default="outputs/demo")
    demo.set_defaults(func=command_demo)

    suite = sub.add_parser("suite", help="run all packaged or local examples")
    suite.add_argument("--examples", default="examples")
    suite.add_argument("--output", default="outputs/reference")
    suite.set_defaults(func=command_suite)


    shield = sub.add_parser("shield", help="apply a user-controlled local feed transformation without deleting source records")
    shield.add_argument("feed")
    shield.add_argument("--output", required=True)
    shield.set_defaults(func=command_shield)

    verify = sub.add_parser("verify", help="verify an append-only evidence ledger")
    verify.add_argument("ledger")
    verify.set_defaults(func=command_verify)

    inspect = sub.add_parser("inspect", help="show the runtime contract and boundaries")
    inspect.set_defaults(func=command_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
