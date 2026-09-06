from __future__ import annotations

from pathlib import Path
from typing import Any

from .engine import QingyuanEngine
from .utils import canonical_json, merkle_root, sha256_text, write_json


def apply_local_shield(feed: dict[str, Any]) -> dict[str, Any]:
    """Apply a user-controlled local feed shield.

    This transforms only the supplied local feed representation. It neither
    deletes source material nor performs a platform/network action. Items held
    from the local view are preserved in a hashed quarantine archive.
    """
    feed_id = str(feed.get("feed_id", "local-feed"))
    items = feed.get("items", [])
    if not isinstance(items, list):
        raise ValueError("feed.items must be a list")

    safe_items: list[dict[str, Any]] = []
    archive: list[dict[str, Any]] = []
    assessments: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        engine = QingyuanEngine(raw)
        result = engine.run()
        plan = result["intervention_plan"]
        disposition = plan["disposition"]
        action_types = {a["action_type"] for a in plan["actions"]}
        original_hash = sha256_text(canonical_json(raw))
        common = {
            "item_id": raw.get("item_id"),
            "title": raw.get("title"),
            "disposition": disposition,
            "content_sha256": sha256_text(str(raw.get("text", ""))),
            "assessment_run_hash": result["run_hash"],
            "truth_return_card": result["truth_return_card"],
            "appeal_available": True,
        }
        if disposition in {"HIGH_RISK_AUTHORIZED_REVIEW", "TEMPORARY_QUARANTINE_PENDING_REVIEW", "URGENT_HUMAN_SAFETY_ESCALATION"}:
            safe_items.append({
                **common,
                "local_state": "HELD_FROM_DEFAULT_VIEW_PENDING_REVIEW",
                "display_text": "该条目因高风险主张、证据缺口或操纵信号被本地用户控制临时收起。原文未删除，可查看证据卡并申诉。",
                "autoplay": False,
                "recommendation_boost": 0,
                "monetization_eligible_in_local_view": False,
                "source_deleted": False,
            })
            archive.append({
                "item_id": raw.get("item_id"),
                "original_record_sha256": original_hash,
                "original_record": raw,
                "reason": disposition,
                "review_required": True,
                "appeal_available": True,
            })
        elif disposition == "FRICTION_AND_CIRCUIT_BREAK_RECOMMENDED":
            safe_items.append({
                **common,
                "local_state": "VISIBLE_WITH_FRICTION_AND_NO_BOOST",
                "display_text": raw.get("text", ""),
                "autoplay": False,
                "recommendation_boost": 0,
                "monetization_eligible_in_local_view": "PAUSE_MONETIZATION_AND_REQUIRE_DISCLOSURE" not in action_types,
                "share_or_purchase_confirmation": True,
                "source_deleted": False,
            })
        elif disposition == "PRESERVE_WITH_CONTEXT":
            safe_items.append({
                **common,
                "local_state": "VISIBLE_WITH_CONTEXT",
                "display_text": raw.get("text", ""),
                "autoplay": False,
                "recommendation_boost": 0,
                "context_card_attached": True,
                "source_deleted": False,
            })
        else:
            safe_items.append({
                **common,
                "local_state": "PRESERVED_AND_SURFACED",
                "display_text": raw.get("text", ""),
                "autoplay": bool(raw.get("design", {}).get("autoplay", False)),
                "recommendation_boost": 1,
                "source_deleted": False,
            })
        assessments.append({
            "item_id": raw.get("item_id"),
            "disposition": disposition,
            "certificate": result["certificate"],
        })

    output = {
        "system": "DIKWP-QINGYUAN-OS",
        "mode": "USER_CONTROLLED_LOCAL_SHIELD",
        "feed_id": feed_id,
        "safe_feed": safe_items,
        "quarantine_archive": archive,
        "assessments": assessments,
        "invariants": {
            "source_deletion": False,
            "external_platform_action": False,
            "automatic_external_action_authority": 0,
            "local_user_controlled_transformation": True,
            "appeal_available": True,
        },
    }
    output["shield_run_hash"] = sha256_text(canonical_json(output))
    return output


def write_shield_outputs(output_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "safe_feed.json", {
        "feed_id": result["feed_id"],
        "items": result["safe_feed"],
        "invariants": result["invariants"],
        "shield_run_hash": result["shield_run_hash"],
    })
    write_json(output_dir / "quarantine_archive.json", {
        "feed_id": result["feed_id"],
        "items": result["quarantine_archive"],
        "source_deletion": False,
    })
    write_json(output_dir / "shield_assessments.json", result["assessments"])
    hashes = [
        sha256_text(canonical_json(result["safe_feed"])),
        sha256_text(canonical_json(result["quarantine_archive"])),
        sha256_text(canonical_json(result["assessments"])),
    ]
    manifest = {
        "feed_id": result["feed_id"],
        "shield_run_hash": result["shield_run_hash"],
        "item_count": len(result["safe_feed"]),
        "locally_held_count": len(result["quarantine_archive"]),
        "merkle_root": merkle_root(hashes),
        "automatic_external_action_authority": 0,
        "source_deletion": False,
    }
    write_json(output_dir / "shield_manifest.json", manifest)
    return manifest
