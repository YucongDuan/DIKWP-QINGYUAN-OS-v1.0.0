from __future__ import annotations

from typing import Any

from .models import ContentItem
from .utils import sha256_text, stable_id


POSITIONS = ["D", "I", "K", "W", "P"]
ALL_ROUTE_TYPES = [f"{source}->{target}" for source in POSITIONS for target in POSITIONS]


def build_semantic_graph(
    item: ContentItem,
    signals: dict[str, Any],
    evidence: dict[str, Any],
    manipulation: dict[str, Any],
    harm: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []

    def add(position: str, record_id: str, content: Any, provenance: str) -> str:
        records.append({
            "record_id": record_id,
            "position": position,
            "content": content,
            "provenance": provenance,
            "immutable": True,
        })
        return record_id

    d_content = add("D", f"D-{item.item_id}-SOURCE", {
        "content_sha256": sha256_text(item.text),
        "source": item.source,
        "claims_submitted": len(item.claims),
    }, "submitted_item")
    d_evidence = add("D", f"D-{item.item_id}-EVIDENCE", evidence["claim_results"], "WM-EVIDENCE")
    i_signals = add("I", f"I-{item.item_id}-SIGNALS", {
        "detected": {k: v for k, v in signals["matches"].items() if v},
        "note": signals["note"],
    }, "lexical_and_design_screen")
    i_conflict = add("I", f"I-{item.item_id}-CONFLICT", {
        "evidence_deficit": evidence["max_evidence_deficit"],
        "commercial_conflict": manipulation["commercial_conflict"],
        "suppression_protection": harm["suppression_protection"],
    }, "plural_world_model_comparison")
    k_assessment = add("K", f"K-{item.item_id}-ASSESSMENT", {
        "disposition": intervention["disposition"],
        "scope": "submitted item and declared context only",
        "not_a_truth_or_intent_or_personhood_verdict": True,
    }, "bounded_runtime_assessment")
    w_rights = add("W", f"W-{item.item_id}-RIGHTS", {
        "protect_autonomy": True,
        "protect_vulnerable_people": True,
        "protect_negative_truth_and_dissent": True,
        "avoid_secret_blacklists": True,
        "avoid_coercive_belief_change": True,
        "potential_harm": harm["potential_harm"],
    }, "rights_and_harm_configuration")
    p_plan = add("P", f"P-{item.item_id}-PLAN", {
        "input_records": [d_content, d_evidence, i_signals, i_conflict, k_assessment, w_rights],
        "output": "reversible_intervention_plan",
        "actions": [action["action_type"] for action in intervention["actions"]],
        "automatic_external_action_authority": 0,
    }, "intervention_contract")
    p_request = add("P", f"P-{item.item_id}-EVIDENCE-REQUEST", {
        "input": "open evidence and provenance positions",
        "output": "specific evidence that would update the assessment",
    }, "evidence_return_contract")

    def route(source: str, target: str, content: str) -> None:
        routes.append({
            "route_id": stable_id("R", source, target, content),
            "route_type": f"{source[0]}->{target[0]}",
            "source_record_id": source,
            "target_record_id": target,
            "generated_content": content,
        })

    route(d_content, i_signals, "Submitted traces are screened for consequential differences without declaring them false.")
    route(d_evidence, k_assessment, "Claim evidence constrains the bounded assessment.")
    route(i_signals, k_assessment, "Manipulation and uncertainty signals reopen simple accept/reject classification.")
    route(i_conflict, w_rights, "Model disagreement activates autonomy and expression-rights review.")
    route(k_assessment, w_rights, "Assessment consequences are checked before action.")
    route(w_rights, p_plan, "Configured values alter the selected intervention and cap censorship risk.")
    route(p_plan, p_request, "The intervention emits a reversible request for missing evidence.")
    route(p_request, d_evidence, "New evidence may be appended as a successor D record; prior records remain addressable.")
    if harm["negative_truth_preservation"] >= 0.50:
        route(d_evidence, p_plan, "Strong evidence and public-interest status directly generate preservation and surfacing.")
    if intervention["disposition"].startswith("TEMPORARY"):
        route(p_plan, k_assessment, "Review outcome must regenerate or revise the temporary assessment before expiry.")

    closure = {position: any(record["position"] == position for record in records) for position in POSITIONS}
    return {
        "positions": POSITIONS,
        "allowed_route_types": ALL_ROUTE_TYPES,
        "records": records,
        "routes": routes,
        "closure_vector": "".join("1" if closure[position] else "0" for position in POSITIONS),
        "append_only": True,
        "concept_aliases_have_zero_native_authority": True,
        "note": "D/I/K/W/P are open roles, not a moral ranking and not labels for good or bad people.",
    }
