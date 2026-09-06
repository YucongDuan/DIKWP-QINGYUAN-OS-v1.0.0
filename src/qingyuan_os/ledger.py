from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import canonical_json, sha256_text


class HashLedger:
    """Append-only deterministic SHA-256 evidence ledger."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def append(self, event_type: str, payload: dict[str, Any], *, stage: str) -> dict[str, Any]:
        previous = self.records[-1]["hash"] if self.records else "GENESIS"
        body = {
            "index": len(self.records),
            "stage": stage,
            "event_type": event_type,
            "previous_hash": previous,
            "payload": payload,
        }
        record = dict(body)
        record["hash"] = sha256_text(canonical_json(body))
        self.records.append(record)
        return record

    @property
    def head_hash(self) -> str | None:
        return self.records[-1]["hash"] if self.records else None

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for record in self.records:
                handle.write(canonical_json(record) + "\n")

    @staticmethod
    def verify_records(records: list[dict[str, Any]]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        previous = "GENESIS"
        for expected_index, record in enumerate(records):
            if record.get("index") != expected_index:
                errors.append(f"index mismatch at {expected_index}")
            if record.get("previous_hash") != previous:
                errors.append(f"previous_hash mismatch at {expected_index}")
            body = {
                "index": record.get("index"),
                "stage": record.get("stage"),
                "event_type": record.get("event_type"),
                "previous_hash": record.get("previous_hash"),
                "payload": record.get("payload"),
            }
            expected_hash = sha256_text(canonical_json(body))
            if record.get("hash") != expected_hash:
                errors.append(f"hash mismatch at {expected_index}")
            previous = str(record.get("hash"))
        return not errors, errors

    @classmethod
    def read_and_verify(cls, path: Path) -> tuple[bool, list[str], list[dict[str, Any]]]:
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(json.loads(stripped))
                except json.JSONDecodeError as exc:
                    return False, [f"invalid JSON at line {line_number}: {exc}"], records
        valid, errors = cls.verify_records(records)
        return valid, errors, records
