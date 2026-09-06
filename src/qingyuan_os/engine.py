from __future__ import annotations

from pathlib import Path
from typing import Any

from . import __version__
from .interventions import choose_interventions
from .ledger import HashLedger
from .models import ContentItem
from .semantics import build_semantic_graph
from .signals import scan_text
from .support import build_incentive_circuit_map, build_real_life_support_plan
from .utils import canonical_json, merkle_root, sha256_file, sha256_text, write_json, write_text
from .world_models import (
    build_non_aggregated_profile,
    evidence_world_model,
    harm_and_rights_world_model,
    manipulation_world_model,
)


class QingyuanEngine:
    def __init__(self, data: dict[str, Any]):
        self.item = ContentItem.from_dict(data)
        self.ledger = HashLedger()

    def run(self) -> dict[str, Any]:
        item = self.item
        self.ledger.append(
            "assessment_contract_registered",
            {
                "item_id": item.item_id,
                "channel": item.channel,
                "purpose_owner": item.purpose.get("owner"),
                "automatic_external_action_authority": 0,
                "emotional_valence_is_not_truth": True,
            },
            stage="01_CONTRACT",
        )

        signals = scan_text(item.text, item.context)
        self.ledger.append(
            "screening_signals_registered",
            {
                "categories_with_matches": sorted(k for k, v in signals["matches"].items() if v),
                "context_discount": signals["context_discount"],
                "screening_is_not_verdict": True,
            },
            stage="02_SIGNAL_SCREEN",
        )

        evidence = evidence_world_model(item, signals)
        self.ledger.append(
            "evidence_world_model_evaluated",
            {
                "model_id": evidence["model_id"],
                "mean_evidence_quality": evidence["mean_evidence_quality"],
                "max_evidence_deficit": evidence["max_evidence_deficit"],
                "provenance_deficit": evidence["provenance_deficit"],
            },
            stage="03_EVIDENCE_WORLD_MODEL",
        )

        manipulation = manipulation_world_model(item, signals, evidence)
        self.ledger.append(
            "manipulation_world_model_evaluated",
            {
                "model_id": manipulation["model_id"],
                "pressure": manipulation["manipulation_pressure"],
                "addictive_design": manipulation["addictive_design"],
                "commercial_conflict": manipulation["commercial_conflict"],
                "vulnerable_targeting": manipulation["vulnerable_targeting"],
            },
            stage="04_MANIPULATION_WORLD_MODEL",
        )

        harm = harm_and_rights_world_model(item, signals, evidence, manipulation)
        self.ledger.append(
            "harm_and_rights_world_model_evaluated",
            {
                "model_id": harm["model_id"],
                "potential_harm": harm["potential_harm"],
                "autonomy_risk": harm["autonomy_risk"],
                "suppression_protection": harm["suppression_protection"],
                "negative_truth_preservation": harm["negative_truth_preservation"],
            },
            stage="05_HARM_RIGHTS_WORLD_MODEL",
        )

        profile = build_non_aggregated_profile(evidence, manipulation, harm)
        model_disagreement = _model_disagreement(evidence, manipulation, harm)
        intervention = choose_interventions(item, signals, evidence, manipulation, harm, profile)
        self.ledger.append(
            "rights_preserving_intervention_planned",
            {
                "disposition": intervention["disposition"],
                "action_types": [action["action_type"] for action in intervention["actions"]],
                "aggregate_score_used": False,
                "automatic_execution": False,
            },
            stage="06_INTERVENTION_PLANNING",
        )

        circuit = build_incentive_circuit_map(item, manipulation)
        support = build_real_life_support_plan(item, profile, intervention)
        self.ledger.append(
            "incentive_and_real_life_paths_registered",
            {
                "circuit_breakpoints": len(circuit["breakpoints"]),
                "real_life_support_applicable": support["applicable"],
                "coercive_belief_change": False,
            },
            stage="07_INCENTIVE_AND_SUPPORT",
        )

        semantic_graph = build_semantic_graph(item, signals, evidence, manipulation, harm, intervention)
        self.ledger.append(
            "dikwp_semantic_graph_generated",
            {
                "closure_vector": semantic_graph["closure_vector"],
                "record_count": len(semantic_graph["records"]),
                "route_count": len(semantic_graph["routes"]),
                "allowed_route_types": 25,
            },
            stage="08_DIKWP_REGENERATION",
        )

        residuals = _build_residual_queue(item, evidence, manipulation, harm, intervention)
        appeal = _build_appeal_packet(item, evidence, intervention)
        truth_return = _build_truth_return_card(item, evidence, manipulation, harm)
        self.ledger.append(
            "residuals_and_appeal_registered",
            {
                "open_residuals": len(residuals["open_items"]),
                "appeal_available": appeal["appeal_available"],
                "temporary_actions_expire": all(
                    action["expiry_hours"] >= 0 for action in intervention["actions"]
                ),
            },
            stage="09_RESIDUAL_AND_APPEAL",
        )

        core = {
            "system": "DIKWP-QINGYUAN-OS",
            "version": __version__,
            "item": item.as_dict(),
            "signals": signals,
            "world_models": {
                "evidence": evidence,
                "manipulation": manipulation,
                "harm_and_rights": harm,
            },
            "model_disagreement": model_disagreement,
            "non_aggregated_profile": profile,
            "intervention_plan": intervention,
            "truth_return_card": truth_return,
            "incentive_circuit_map": circuit,
            "real_life_support_plan": support,
            "semantic_graph": semantic_graph,
            "residual_queue": residuals,
            "appeal_packet": appeal,
        }
        run_hash = sha256_text(canonical_json(core))
        certificate = _build_certificate(core, run_hash)
        self.ledger.append(
            "bounded_assessment_certificate_issued",
            {
                "certificate_id": certificate["certificate_id"],
                "disposition": certificate["disposition"],
                "run_hash": run_hash,
                "not_a_person_or_ideology_verdict": True,
                "automatic_external_action_authority": 0,
            },
            stage="10_CERTIFICATE",
        )
        result = dict(core)
        result["run_hash"] = run_hash
        result["certificate"] = certificate
        result["ledger_head_hash"] = self.ledger.head_hash
        return result


def _model_disagreement(evidence: dict[str, Any], manipulation: dict[str, Any], harm: dict[str, Any]) -> dict[str, Any]:
    observations: list[str] = []
    if evidence["mean_evidence_quality"] >= 0.68 and manipulation["manipulation_pressure"] >= 0.45:
        observations.append("Evidence may be strong while presentation remains manipulative; preserve the claim record but add autonomy protections.")
    if evidence["mean_evidence_quality"] < 0.35 and manipulation["manipulation_pressure"] < 0.25:
        observations.append("Weak evidence does not by itself establish malicious manipulation; request evidence without punitive suppression.")
    if harm["suppression_protection"] >= 0.55:
        observations.append("Public-interest, critical, minority, or whistleblowing context raises the cost of false-positive suppression.")
    if not observations:
        observations.append("No decisive cross-model conflict; model dimensions remain separately visible.")
    return {
        "non_isomorphic_models_retained": ["WM-EVIDENCE", "WM-MANIPULATION", "WM-HARM-RIGHTS"],
        "observations": observations,
        "forced_single_truth_score": False,
    }


def _build_residual_queue(
    item: ContentItem,
    evidence: dict[str, Any],
    manipulation: dict[str, Any],
    harm: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    residuals: list[dict[str, Any]] = []
    if evidence["max_evidence_deficit"] > 0.25:
        residuals.append({
            "residual_id": f"R-{item.item_id}-EVIDENCE",
            "type": "EVIDENCE_GAP",
            "description": "One or more factual claims lack independently verifiable support in the submitted record.",
            "reopen_condition": "Append primary, peer-reviewed, official, or independently reproducible evidence with a stable locator.",
            "owner": item.purpose.get("owner"),
        })
    if evidence["provenance_deficit"] > 0.25:
        residuals.append({
            "residual_id": f"R-{item.item_id}-PROVENANCE",
            "type": "SOURCE_PROVENANCE_GAP",
            "description": "Authorship, origin, sponsorship, or chain of custody is incomplete.",
            "reopen_condition": "Supply identity, origin, edit history, sponsorship, and source document references.",
            "owner": item.purpose.get("owner"),
        })
    if manipulation["commercial_conflict"] > 0.30:
        residuals.append({
            "residual_id": f"R-{item.item_id}-INTEREST",
            "type": "INCENTIVE_CONFLICT",
            "description": "The commercial or recommendation incentive may affect presentation or targeting.",
            "reopen_condition": "Disclose sponsor/affiliate terms, outcome-claim basis, refund policy, and recommendation incentives.",
            "owner": item.purpose.get("owner"),
        })
    if intervention["highest_level_rank"] >= 4:
        residuals.append({
            "residual_id": f"R-{item.item_id}-OUTCOME",
            "type": "REAL_WORLD_OUTCOME_DEBT",
            "description": "The effect of friction, de-amplification, or review has not yet been observed.",
            "reopen_condition": "Measure harmful exposure, false positives, appeal reversals, user autonomy, and displacement to other channels.",
            "owner": item.purpose.get("owner"),
        })
    if harm["suppression_protection"] >= 0.45:
        residuals.append({
            "residual_id": f"R-{item.item_id}-RIGHTS",
            "type": "EXPRESSION_RIGHTS_RISK",
            "description": "Restrictive action may suppress criticism, dissent, satire, minority evidence, or public-interest warning.",
            "reopen_condition": "Independent rights review must confirm claim-specific necessity and least-restrictive means.",
            "owner": item.purpose.get("owner"),
        })
    return {
        "open_items": residuals,
        "not_one_uncertainty_score": True,
        "actual_outcomes_must_update_models": True,
        "unobserved_outcomes_are_reality_debt": True,
    }


def _build_appeal_packet(item: ContentItem, evidence: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    return {
        "appeal_available": True,
        "item_id": item.item_id,
        "current_disposition": intervention["disposition"],
        "grounds": [
            "source identity or provenance was misread",
            "evidence was omitted or incorrectly weighted",
            "quotation, satire, criticism, or public-interest context was missed",
            "audience vulnerability or commercial relationship was inferred incorrectly",
            "the proposed action is disproportionate or not the least restrictive option",
        ],
        "required_review": {
            "independent_reviewer": True,
            "claim_level_reasons": True,
            "access_to_submitted_record": True,
            "response_due_hours": 72,
            "temporary_action_expiry": True,
        },
        "update_inputs": [
            {
                "claim_id": result["claim_id"],
                "current_status": result["status"],
                "evidence_needed": "stable independent evidence or a correction to the claim scope",
            }
            for result in evidence["claim_results"]
        ],
        "no_retaliation_for_appeal": True,
        "no_secret_permanent_blacklist": True,
    }


def _build_truth_return_card(
    item: ContentItem,
    evidence: dict[str, Any],
    manipulation: dict[str, Any],
    harm: dict[str, Any],
) -> dict[str, Any]:
    return {
        "item_id": item.item_id,
        "headline": item.title,
        "claim_statuses": [
            {
                "claim_id": result["claim_id"],
                "status": result["status"],
                "evidence_quality": result["evidence_quality"],
                "certainty_mismatch": result["certainty_mismatch"],
            }
            for result in evidence["claim_results"]
        ],
        "source_status": {
            "provenance_quality": evidence["provenance_quality"],
            "provenance_deficit": evidence["provenance_deficit"],
        },
        "interest_status": manipulation["interest_map"],
        "rights_notice": {
            "negative_or_unpopular_does_not_mean_false": True,
            "positive_or_inspirational_does_not_mean_true": True,
            "uncertainty_is_explicit": True,
            "person_is_not_equated_with_claim": True,
        },
        "harm_context": {
            "potential_harm": harm["potential_harm"],
            "autonomy_risk": harm["autonomy_risk"],
        },
    }


def _build_certificate(core: dict[str, Any], run_hash: str) -> dict[str, Any]:
    item = core["item"]
    intervention = core["intervention_plan"]
    return {
        "certificate_id": f"QY-CERT-{item['item_id']}-{run_hash[:16]}",
        "system": "DIKWP-QINGYUAN-OS",
        "version": __version__,
        "item_id": item["item_id"],
        "content_sha256": sha256_text(item["text"]),
        "run_hash": run_hash,
        "disposition": intervention["disposition"],
        "non_aggregated_profile": core["non_aggregated_profile"],
        "actions": intervention["actions"],
        "world_models_retained": core["model_disagreement"]["non_isomorphic_models_retained"],
        "semantic_closure_vector": core["semantic_graph"]["closure_vector"],
        "claim_boundaries": {
            "truth_of_all_claims": "NOT_ESTABLISHED_BY_RUNTIME_ALONE",
            "malicious_intent": "NOT_ESTABLISHED_BY_SIGNAL_SCREENING",
            "mental_health_or_capacity_of_person": "NOT_ASSESSED",
            "legality": "NOT_ADJUDICATED",
            "real_world_effectiveness": "NOT_ESTABLISHED_UNTIL_OUTCOMES_ARE_MEASURED",
        },
        "rights_and_safety": intervention["rights_firewall"],
        "automatic_external_action_authority": 0,
        "automatic_deletion": False,
        "appeal_available": True,
        "causal_handoff": {
            "owner": item["purpose"].get("owner"),
            "next_action": _next_action(intervention),
            "required_artifact": "claim-level evidence packet and post-intervention outcome report",
            "kill_condition": "stop or reverse intervention if evidence, appeal, or measured outcome no longer supports it",
        },
    }


def _next_action(intervention: dict[str, Any]) -> str:
    if intervention["highest_level_rank"] >= 6:
        return "authorized human domain and rights review before any high-impact external action"
    if intervention["highest_level_rank"] >= 4:
        return "apply only reversible circuit-breaking measures under named authority, then measure outcomes and appeals"
    if intervention["highest_level_rank"] >= 2:
        return "publish provenance, uncertainty, and counterevidence context; invite a bounded correction"
    return "preserve the content and continue ordinary provenance monitoring"


def write_run_outputs(output_dir: Path, engine: QingyuanEngine, result: dict[str, Any]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "assessment.json", {
        "item_id": result["item"]["item_id"],
        "signals": result["signals"],
        "world_models": result["world_models"],
        "model_disagreement": result["model_disagreement"],
        "non_aggregated_profile": result["non_aggregated_profile"],
    })
    write_json(output_dir / "intervention_plan.json", result["intervention_plan"])
    write_json(output_dir / "truth_return_card.json", result["truth_return_card"])
    write_json(output_dir / "incentive_circuit_map.json", result["incentive_circuit_map"])
    write_json(output_dir / "real_life_support_plan.json", result["real_life_support_plan"])
    write_json(output_dir / "semantic_graph.json", result["semantic_graph"])
    write_json(output_dir / "residual_queue.json", result["residual_queue"])
    write_json(output_dir / "appeal_packet.json", result["appeal_packet"])
    write_json(output_dir / "qingyuan_certificate.json", result["certificate"])
    engine.ledger.write(output_dir / "evidence_ledger.jsonl")
    write_text(output_dir / "report.zh-CN.md", _report_zh(result))
    write_text(output_dir / "report.en.md", _report_en(result))

    artifact_names = [
        "assessment.json", "intervention_plan.json", "truth_return_card.json",
        "incentive_circuit_map.json", "real_life_support_plan.json", "semantic_graph.json",
        "residual_queue.json", "appeal_packet.json", "qingyuan_certificate.json",
        "evidence_ledger.jsonl", "report.zh-CN.md", "report.en.md",
    ]
    hashes = {name: sha256_file(output_dir / name) for name in artifact_names}
    manifest = {
        "system": "DIKWP-QINGYUAN-OS",
        "version": __version__,
        "item_id": result["item"]["item_id"],
        "run_hash": result["run_hash"],
        "ledger_head_hash": result["ledger_head_hash"],
        "files": hashes,
        "merkle_root": merkle_root(hashes.values()),
    }
    write_json(output_dir / "output_manifest.json", manifest)
    return {
        "item_id": result["item"]["item_id"],
        "disposition": result["intervention_plan"]["disposition"],
        "run_hash": result["run_hash"],
        "ledger_head_hash": result["ledger_head_hash"],
        "output_dir": str(output_dir),
        "manifest_merkle_root": manifest["merkle_root"],
    }


def _report_zh(result: dict[str, Any]) -> str:
    item = result["item"]
    profile = result["non_aggregated_profile"]
    plan = result["intervention_plan"]
    lines = [
        f"# {item['title']}",
        "",
        "## 有界结论",
        "",
        f"- 条目：`{item['item_id']}`",
        f"- 处置建议：**{plan['disposition']}**",
        f"- 运行哈希：`{result['run_hash']}`",
        "- 自动外部行动权限：`0`",
        "- 自动删除：`否`",
        "- 情绪正负作为限制依据：`否`",
        "",
        "本系统不把‘让人不舒服’等同于虚假，也不把‘正能量包装’等同于真实。判断围绕证据、来源、操纵、上瘾设计、脆弱人群利用、商业利益、现实伤害和表达权分别展开。",
        "",
        "## 非聚合风险与保护向量",
        "",
        "| 维度 | 数值 |",
        "|---|---:|",
    ]
    for key, value in profile.items():
        lines.append(f"| {key} | {value:.3f} |")
    lines.extend(["", "## 主张证据状态", "", "| 主张 | 类型 | 状态 | 证据质量 |", "|---|---|---|---:|"])
    for claim in result["world_models"]["evidence"]["claim_results"]:
        quality = "—" if claim["evidence_quality"] is None else f"{claim['evidence_quality']:.3f}"
        lines.append(f"| {claim['claim_id']} | {claim['claim_type']} | {claim['status']} | {quality} |")
    lines.extend(["", "## 建议行动", ""])
    for action in plan["actions"]:
        lines.append(f"- **{action['action_type']}**（{action['level']}）：{action['detail']}")
    lines.extend([
        "",
        "## 权利防火墙",
        "",
        "- 保留有证据的坏消息、警示、批评、异议与揭弊；不得因其‘负面’而降权。",
        "- 对正面、励志、疗愈或知识包装同样进行证据和利益审计。",
        "- 不建立秘密永久黑名单，不把人等同于其当前相信或传播的主张。",
        "- 高影响措施必须具名授权、限时、可撤回，并提供独立申诉。",
        "",
        "## 现实接触与后续",
        "",
        f"- 下一行动：{result['certificate']['causal_handoff']['next_action']}",
        f"- 停止/回滚条件：{result['certificate']['causal_handoff']['kill_condition']}",
        "- 未观测的实际效果保持为现实债务，必须用暴露减少、误伤率、申诉改判率、用户自主性和渠道迁移等结果重新校准。",
    ])
    return "\n".join(lines) + "\n"


def _report_en(result: dict[str, Any]) -> str:
    item = result["item"]
    profile = result["non_aggregated_profile"]
    plan = result["intervention_plan"]
    lines = [
        f"# {item['title']}",
        "",
        "## Bounded result",
        "",
        f"- Item: `{item['item_id']}`",
        f"- Recommended disposition: **{plan['disposition']}**",
        f"- Run hash: `{result['run_hash']}`",
        "- Automatic external action authority: `0`",
        "- Automatic deletion: `no`",
        "- Emotional valence used as a restriction signal: `no`",
        "",
        "The runtime separates evidence, provenance, manipulation, addiction design, vulnerable targeting, commercial incentive, harm, autonomy, and expression rights. Negative tone is not falsity; positive packaging is not truth.",
        "",
        "## Non-aggregated profile",
        "",
        "| Dimension | Value |",
        "|---|---:|",
    ]
    for key, value in profile.items():
        lines.append(f"| {key} | {value:.3f} |")
    lines.extend(["", "## Recommended actions", ""])
    for action in plan["actions"]:
        lines.append(f"- **{action['action_type']}** ({action['level']}): {action['detail']}")
    lines.extend([
        "",
        "## Rights firewall",
        "",
        "- Preserve evidenced warnings, criticism, dissent, minority evidence, and whistleblowing.",
        "- Audit inspirational and positive claims under the same evidence and incentive standards.",
        "- Do not create a secret permanent person blacklist or equate a person with a claim.",
        "- High-impact measures require named authority, expiry, reversibility, and independent appeal.",
        "",
        "## Causal handoff",
        "",
        f"- Next action: {result['certificate']['causal_handoff']['next_action']}",
        f"- Kill/reversal condition: {result['certificate']['causal_handoff']['kill_condition']}",
        "- Unobserved real-world outcomes remain a reality debt and must recalibrate the models.",
    ])
    return "\n".join(lines) + "\n"
