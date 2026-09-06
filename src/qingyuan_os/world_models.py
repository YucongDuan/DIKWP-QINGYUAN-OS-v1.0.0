from __future__ import annotations

import math
from typing import Any

from .models import Claim, ContentItem, EvidenceItem
from .utils import clamp


EVIDENCE_BASE = {
    "primary_document": 0.90,
    "official_record": 0.88,
    "peer_reviewed": 0.82,
    "independent_test": 0.80,
    "dataset": 0.75,
    "reputable_secondary": 0.65,
    "expert_analysis": 0.60,
    "self_report": 0.38,
    "testimonial": 0.20,
    "anonymous_post": 0.12,
    "none": 0.0,
}

STAKE_WEIGHT = {"low": 0.20, "medium": 0.50, "high": 0.80, "critical": 1.0}
DOMAIN_WEIGHT = {
    "medical": 0.95,
    "financial": 0.90,
    "legal": 0.72,
    "public_safety": 0.90,
    "scientific": 0.55,
    "historical": 0.45,
    "factual": 0.45,
    "testimonial": 0.35,
    "opinion": 0.10,
    "satire": 0.05,
    "other": 0.35,
}


def _evidence_score(item: EvidenceItem) -> float:
    score = EVIDENCE_BASE.get(item.type, 0.25)
    if item.independent:
        score += 0.08
    if item.verifiable:
        score += 0.07
    if item.direct:
        score += 0.05
    if not item.locator and item.type not in {"none", "testimonial", "self_report"}:
        score -= 0.12
    return clamp(score)


def evaluate_claim(claim: Claim, certainty_signal: float) -> dict[str, Any]:
    if claim.claim_type in {"opinion", "satire"}:
        return {
            "claim_id": claim.claim_id,
            "claim_type": claim.claim_type,
            "status": "VALUE_OR_EXPRESSIVE_CLAIM",
            "evidence_quality": None,
            "evidence_deficit": 0.0,
            "certainty_mismatch": 0.0,
            "stakes": claim.stakes,
            "requested_behavior": claim.requested_behavior,
            "note": "Expressive claims are not treated as factual merely because they are disagreeable.",
        }
    scores = [_evidence_score(item) for item in claim.evidence]
    if scores:
        scores.sort(reverse=True)
        quality = scores[0]
        if len(scores) > 1:
            quality = clamp(quality + 0.06 * math.log2(len(scores)))
    else:
        quality = 0.0
    deficit = 1.0 - quality
    universal_penalty = 0.18 if not claim.bounded else 0.0
    mismatch = clamp(certainty_signal * (deficit + universal_penalty))
    if quality >= 0.78:
        status = "SUPPORTED_WITHIN_DECLARED_SCOPE"
    elif quality >= 0.48:
        status = "PARTIALLY_SUPPORTED_OR_CONTEXT_NEEDED"
    elif quality > 0.0:
        status = "WEAKLY_SUPPORTED"
    else:
        status = "UNSUPPORTED_IN_SUBMITTED_RECORD"
    return {
        "claim_id": claim.claim_id,
        "claim_type": claim.claim_type,
        "status": status,
        "evidence_quality": round(quality, 6),
        "evidence_deficit": round(deficit, 6),
        "certainty_mismatch": round(mismatch, 6),
        "stakes": claim.stakes,
        "requested_behavior": claim.requested_behavior,
        "evidence_items": len(claim.evidence),
    }


def evidence_world_model(item: ContentItem, signals: dict[str, Any]) -> dict[str, Any]:
    certainty = signals["category_scores"].get("absolute_certainty", 0.0)
    claim_results = [evaluate_claim(claim, certainty) for claim in item.claims]
    factual = [result for result in claim_results if result["evidence_quality"] is not None]
    if factual:
        deficit = max(float(result["evidence_deficit"]) for result in factual)
        mismatch = max(float(result["certainty_mismatch"]) for result in factual)
        mean_quality = sum(float(result["evidence_quality"]) for result in factual) / len(factual)
    else:
        deficit = 0.0
        mismatch = 0.0
        mean_quality = 1.0
    source = item.source
    identity_verified = bool(source.get("identity_verified", False))
    provenance_locator = bool(source.get("url") or source.get("document_id") or source.get("publisher"))
    source_trace = bool(source.get("provenance_note") or source.get("origin"))
    provenance_quality = (0.45 if identity_verified else 0.0) + (0.30 if provenance_locator else 0.0) + (0.25 if source_trace else 0.0)
    provenance_deficit = 1.0 - provenance_quality
    outcome_records = item.declared_outcomes.get("independent_verification", [])
    return {
        "model_id": "WM-EVIDENCE",
        "model_family": "provenance-and-verifiability",
        "claim_results": claim_results,
        "mean_evidence_quality": round(mean_quality, 6),
        "max_evidence_deficit": round(deficit, 6),
        "max_certainty_mismatch": round(mismatch, 6),
        "provenance_quality": round(provenance_quality, 6),
        "provenance_deficit": round(provenance_deficit, 6),
        "independent_outcome_records": len(outcome_records) if isinstance(outcome_records, list) else 0,
        "scope_boundary": "Assesses submitted evidence and provenance; it does not infer universal truth from absence of a citation.",
    }


def manipulation_world_model(item: ContentItem, signals: dict[str, Any], evidence_model: dict[str, Any]) -> dict[str, Any]:
    s = signals["category_scores"]
    pressure_categories = [
        "absolute_certainty", "urgency_scarcity", "secrecy_isolation",
        "authority_social_proof", "fear_shame_pressure", "transaction_request",
    ]
    pressure = clamp(sum(s.get(name, 0.0) for name in pressure_categories) / 3.2)
    commercial = item.commercial
    price_signal = 1.0 if float(commercial.get("price", 0) or 0) > 0 else 0.0
    undisclosed_sponsor = bool(commercial.get("sponsor_present")) and not bool(commercial.get("sponsor_disclosed"))
    commercial_conflict = clamp(
        0.30 * price_signal
        + 0.25 * bool(commercial.get("affiliate"))
        + 0.20 * bool(commercial.get("recurring_subscription"))
        + 0.20 * undisclosed_sponsor
        + 0.15 * (not bool(commercial.get("refund_disclosed", True)) and price_signal)
    )
    design_keys = [
        "autoplay", "infinite_scroll", "variable_reward", "streak",
        "push_pressure", "countdown", "intermittent_reward", "social_comparison",
    ]
    active_design = [key for key in design_keys if bool(item.design.get(key))]
    addictive_design = clamp(len(active_design) / 5.0 + 0.18 * s.get("engagement_hook", 0.0))
    vulnerabilities = item.audience.get("vulnerabilities", [])
    if isinstance(vulnerabilities, str):
        vulnerabilities = [vulnerabilities]
    groups = item.audience.get("groups", [])
    if isinstance(groups, str):
        groups = [groups]
    vulnerability_base = 0.18 * len(vulnerabilities)
    if any(group in {"children", "older_adults", "patients", "financially_distressed", "low_literacy"} for group in groups):
        vulnerability_base += 0.30
    targeting = clamp(vulnerability_base + 0.25 * bool(item.audience.get("targeted")) + 0.20 * s.get("fear_shame_pressure", 0.0))
    pseudo_packaging = clamp(
        0.45 * s.get("pseudo_knowledge_packaging", 0.0)
        + 0.35 * evidence_model["max_evidence_deficit"]
        + 0.30 * commercial_conflict
        + 0.25 * s.get("absolute_certainty", 0.0)
    )
    quoted_discount = float(signals.get("context_discount", 1.0))
    if quoted_discount < 1.0:
        pressure *= quoted_discount
        pseudo_packaging *= quoted_discount
    interest_map = {
        "seller_or_creator": item.source.get("publisher") or item.source.get("author") or "unknown",
        "payment_present": bool(price_signal or commercial.get("affiliate") or commercial.get("recurring_subscription")),
        "sponsor_disclosed": bool(commercial.get("sponsor_disclosed", False)),
        "affiliate": bool(commercial.get("affiliate", False)),
        "recommendation_incentive": str(commercial.get("recommendation_incentive", "unknown")),
        "refund_disclosed": bool(commercial.get("refund_disclosed", False)),
    }
    return {
        "model_id": "WM-MANIPULATION",
        "model_family": "pressure-addiction-and-incentive",
        "manipulation_pressure": round(pressure, 6),
        "addictive_design": round(addictive_design, 6),
        "vulnerable_targeting": round(targeting, 6),
        "commercial_conflict": round(commercial_conflict, 6),
        "pseudo_knowledge_packaging": round(pseudo_packaging, 6),
        "active_design_signals": active_design,
        "interest_map": interest_map,
        "scope_boundary": "Signals indicate a need for review or friction; they do not prove malicious intent by themselves.",
    }


def harm_and_rights_world_model(
    item: ContentItem,
    signals: dict[str, Any],
    evidence_model: dict[str, Any],
    manipulation_model: dict[str, Any],
) -> dict[str, Any]:
    claim_harms: list[float] = []
    for claim in item.claims:
        claim_harms.append(max(STAKE_WEIGHT[claim.stakes], DOMAIN_WEIGHT.get(claim.claim_type, 0.35)))
    stakes = max(claim_harms, default=0.20)
    s = signals["category_scores"]
    dangerous_displacement = max(s.get("medical_displacement", 0.0), s.get("financial_guarantee", 0.0))
    potential_harm = clamp(
        0.46 * stakes
        + 0.24 * dangerous_displacement
        + 0.15 * manipulation_model["vulnerable_targeting"]
        + 0.15 * evidence_model["max_evidence_deficit"]
    )
    autonomy_risk = clamp(
        0.45 * manipulation_model["manipulation_pressure"]
        + 0.30 * manipulation_model["addictive_design"]
        + 0.25 * manipulation_model["vulnerable_targeting"]
    )
    context = item.context
    suppression_protection = clamp(
        0.45 * bool(context.get("public_interest"))
        + 0.35 * bool(context.get("criticism_or_dissent"))
        + 0.35 * bool(context.get("whistleblowing"))
        + 0.25 * bool(context.get("minority_view"))
        + 0.25 * bool(context.get("satire"))
    )
    credible_warning = bool(context.get("warning")) and evidence_model["mean_evidence_quality"] >= 0.70
    negative_truth_preservation = clamp(
        0.70 * credible_warning
        + 0.45 * bool(context.get("public_interest")) * evidence_model["mean_evidence_quality"]
        + 0.35 * bool(context.get("criticism_or_dissent")) * evidence_model["mean_evidence_quality"]
    )
    imminent_danger = bool(context.get("imminent_danger"))
    return {
        "model_id": "WM-HARM-RIGHTS",
        "model_family": "harm-autonomy-and-expression-rights",
        "potential_harm": round(potential_harm, 6),
        "autonomy_risk": round(autonomy_risk, 6),
        "suppression_protection": round(suppression_protection, 6),
        "negative_truth_preservation": round(negative_truth_preservation, 6),
        "imminent_danger": imminent_danger,
        "emotional_valence_is_not_truth": True,
        "scope_boundary": "Unpleasant, critical, pessimistic, or dissenting speech is not harmful misinformation merely because it feels negative.",
    }


def build_non_aggregated_profile(
    evidence_model: dict[str, Any], manipulation_model: dict[str, Any], harm_model: dict[str, Any]
) -> dict[str, float]:
    return {
        "evidence_deficit": evidence_model["max_evidence_deficit"],
        "certainty_mismatch": evidence_model["max_certainty_mismatch"],
        "provenance_deficit": evidence_model["provenance_deficit"],
        "manipulation_pressure": manipulation_model["manipulation_pressure"],
        "addictive_design": manipulation_model["addictive_design"],
        "vulnerable_targeting": manipulation_model["vulnerable_targeting"],
        "commercial_conflict": manipulation_model["commercial_conflict"],
        "pseudo_knowledge_packaging": manipulation_model["pseudo_knowledge_packaging"],
        "potential_harm": harm_model["potential_harm"],
        "autonomy_risk": harm_model["autonomy_risk"],
        "suppression_protection": harm_model["suppression_protection"],
        "negative_truth_preservation": harm_model["negative_truth_preservation"],
    }
