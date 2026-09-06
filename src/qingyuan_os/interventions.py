from __future__ import annotations

from typing import Any

from .models import ContentItem


LEVELS = {
    "L0_OBSERVE": 0,
    "L1_PROVENANCE_RETURN": 1,
    "L2_CONTEXT_AND_COUNTEREVIDENCE": 2,
    "L3_COGNITIVE_FRICTION": 3,
    "L4_AMPLIFICATION_OR_MONETIZATION_BREAK": 4,
    "L5_USER_CONTROLLED_QUARANTINE": 5,
    "L6_AUTHORIZED_HUMAN_REVIEW": 6,
    "L7_URGENT_SAFETY_ESCALATION": 7,
}


def _action(
    action_id: str,
    level: str,
    action_type: str,
    reason_codes: list[str],
    *,
    target: str,
    owner: str,
    expiry_hours: int,
    reversible: bool = True,
    appeal: bool = True,
    requires_human: bool = True,
    detail: str = "",
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "level": level,
        "level_rank": LEVELS[level],
        "action_type": action_type,
        "target": target,
        "reason_codes": reason_codes,
        "owner": owner,
        "expiry_hours": expiry_hours,
        "reversible": reversible,
        "appeal_available": appeal,
        "requires_human_authorization": requires_human,
        "automatic_execution": False,
        "detail": detail,
    }


def choose_interventions(
    item: ContentItem,
    signals: dict[str, Any],
    evidence: dict[str, Any],
    manipulation: dict[str, Any],
    harm: dict[str, Any],
    profile: dict[str, float],
) -> dict[str, Any]:
    """Select a proportional, reversible intervention plan.

    No action is executed. The runtime returns a plan with named authority,
    expiry, evidence return, and appeal. Emotional negativity never triggers
    restriction.
    """

    actions: list[dict[str, Any]] = []
    reasons: list[str] = []
    owner = str(item.purpose.get("owner", "local_authorized_reviewer"))

    strong_public_interest = profile["suppression_protection"] >= 0.55
    well_supported = evidence["mean_evidence_quality"] >= 0.68
    high_evidence_deficit = profile["evidence_deficit"] >= 0.72
    high_harm = profile["potential_harm"] >= 0.68
    high_pressure = profile["manipulation_pressure"] >= 0.48
    high_vulnerability = profile["vulnerable_targeting"] >= 0.50
    high_addiction = profile["addictive_design"] >= 0.58
    commercial_exploitation = (
        profile["commercial_conflict"] >= 0.42
        and (profile["pseudo_knowledge_packaging"] >= 0.48 or high_pressure or high_vulnerability)
    )
    medical_or_financial_displacement = max(
        signals["category_scores"].get("medical_displacement", 0.0),
        signals["category_scores"].get("financial_guarantee", 0.0),
    ) >= 0.30

    # Truth/dissent firewall: negative but evidenced public-interest content is surfaced, not suppressed.
    if profile["negative_truth_preservation"] >= 0.55 and well_supported:
        actions.append(_action(
            "A-PRESERVE-SURFACE",
            "L0_OBSERVE",
            "PRESERVE_AND_SURFACE",
            ["NEGATIVE_OR_CRITICAL_CONTENT_WITH_EVIDENCE", "PUBLIC_INTEREST"],
            target="content_visibility",
            owner=owner,
            expiry_hours=0,
            requires_human=False,
            detail="Do not demote merely because the content is alarming, critical, pessimistic, or emotionally negative.",
        ))
        reasons.extend(["NEGATIVE_TRUTH_PROTECTION", "DISSENT_OR_WARNING_PRESERVATION"])

    if evidence["provenance_deficit"] >= 0.35 or profile["evidence_deficit"] >= 0.35:
        actions.append(_action(
            "A-PROVENANCE-RETURN",
            "L1_PROVENANCE_RETURN",
            "ATTACH_PROVENANCE_AND_EVIDENCE_CARD",
            ["SOURCE_OR_EVIDENCE_INCOMPLETE"],
            target="claim_context",
            owner=owner,
            expiry_hours=168,
            requires_human=False,
            detail="Show source identity, claim-by-claim evidence status, uncertainty, and what evidence would change the assessment.",
        ))
        reasons.append("PROVENANCE_RETURN_REQUIRED")

    if profile["certainty_mismatch"] >= 0.30 or (profile["evidence_deficit"] >= 0.55 and not high_harm):
        actions.append(_action(
            "A-CONTEXT",
            "L2_CONTEXT_AND_COUNTEREVIDENCE",
            "CONTEXTUALIZE_AND_REQUEST_EVIDENCE",
            ["CERTAINTY_EXCEEDS_SUBMITTED_EVIDENCE"],
            target="claim_interpretation",
            owner=owner,
            expiry_hours=168,
            requires_human=False,
            detail="Present plausible alternatives, claim scope, missing tests, and a bounded evidence request; do not label disagreement as pathology.",
        ))
        reasons.append("CONTEXTUAL_REVIEW")

    if high_pressure or high_addiction:
        trigger = "MANIPULATIVE_PRESSURE" if high_pressure else "COMPULSIVE_ENGAGEMENT_DESIGN"
        actions.append(_action(
            "A-FRICTION",
            "L3_COGNITIVE_FRICTION",
            "ADD_USER_CONTROLLED_FRICTION",
            [trigger],
            target="sharing_purchase_or_continuation_flow",
            owner=owner,
            expiry_hours=72,
            requires_human=False,
            detail="Recommend pause prompts, share delay, session break, citation confirmation, autoplay-off, and easy exit. The user may override non-safety friction.",
        ))
        reasons.append(trigger)

    if high_addiction:
        actions.append(_action(
            "A-DEAMPLIFY-ADDICTION",
            "L4_AMPLIFICATION_OR_MONETIZATION_BREAK",
            "DEAMPLIFY_RECOMMENDATION_FEEDBACK_LOOP",
            ["COMPULSIVE_ENGAGEMENT_DESIGN"],
            target="ranking_and_notification_loop",
            owner=owner,
            expiry_hours=72,
            detail="Recommend removing autoplay/variable-reward boosts and ranking incentives, not deleting lawful content.",
        ))
        reasons.append("AMPLIFICATION_CIRCUIT_BREAK")

    if commercial_exploitation:
        actions.append(_action(
            "A-MONETIZATION-BREAK",
            "L4_AMPLIFICATION_OR_MONETIZATION_BREAK",
            "PAUSE_MONETIZATION_AND_REQUIRE_DISCLOSURE",
            ["COMMERCIAL_CONFLICT", "PSEUDO_KNOWLEDGE_OR_PRESSURE"],
            target="affiliate_ads_payment_and_recommendation_incentives",
            owner=owner,
            expiry_hours=168,
            detail="Recommend suspending recommendation-derived monetization pending evidence, sponsorship, outcome-claim, and refund-policy review.",
        ))
        reasons.append("MONETIZATION_CIRCUIT_BREAK")

    # Speech-rights firewall. Public-interest criticism cannot be quarantined solely for disputed truth.
    quarantine_allowed = not strong_public_interest or medical_or_financial_displacement or bool(harm.get("imminent_danger"))

    if high_harm and high_evidence_deficit and (high_pressure or high_vulnerability) and quarantine_allowed:
        actions.append(_action(
            "A-QUARANTINE",
            "L5_USER_CONTROLLED_QUARANTINE",
            "QUARANTINE_PENDING_AUTHORIZED_REVIEW",
            ["HIGH_STAKES", "LOW_EVIDENCE", "MANIPULATION_OR_VULNERABLE_TARGETING"],
            target="high_risk_distribution_or_transaction",
            owner=owner,
            expiry_hours=48,
            detail="Recommend a temporary, reviewable hold on high-risk distribution or transaction. Preserve the item, reasons, and appeal route; do not erase the record.",
        ))
        reasons.append("TEMPORARY_HIGH_RISK_HOLD")

    if medical_or_financial_displacement and high_harm and high_evidence_deficit:
        actions.append(_action(
            "A-HUMAN-REVIEW",
            "L6_AUTHORIZED_HUMAN_REVIEW",
            "ESCALATE_TO_DOMAIN_AND_POLICY_REVIEW",
            ["MEDICAL_OR_FINANCIAL_IRREVERSIBILITY", "UNSUPPORTED_HIGH_STAKES_CLAIM"],
            target="claim_and_transaction",
            owner=owner,
            expiry_hours=24,
            detail="Route to an authorized domain reviewer and, where applicable, platform fraud/safety process. This runtime does not make a legal or clinical determination.",
        ))
        reasons.append("AUTHORIZED_DOMAIN_REVIEW")

    if bool(harm.get("imminent_danger")):
        actions.append(_action(
            "A-URGENT-SAFETY",
            "L7_URGENT_SAFETY_ESCALATION",
            "URGENT_HUMAN_SAFETY_ESCALATION",
            ["DECLARED_IMMINENT_DANGER"],
            target="immediate_harm_prevention",
            owner=owner,
            expiry_hours=1,
            detail="Use applicable emergency or safeguarding procedures. This is a human escalation, not an automated punishment or diagnosis.",
        ))
        reasons.append("IMMINENT_DANGER")

    if not actions:
        actions.append(_action(
            "A-PRESERVE",
            "L0_OBSERVE",
            "PRESERVE_WITH_NO_RESTRICTION",
            ["NO_ACTION_THRESHOLD_REACHED"],
            target="content",
            owner=owner,
            expiry_hours=0,
            requires_human=False,
            detail="No restrictive intervention is recommended. Continue ordinary provenance and outcome monitoring.",
        ))

    # Deduplicate by action_type while preserving order.
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        if action["action_type"] not in seen:
            seen.add(action["action_type"])
            unique.append(action)
    actions = unique

    max_level = max(action["level_rank"] for action in actions)
    if any(action["action_type"] == "URGENT_HUMAN_SAFETY_ESCALATION" for action in actions):
        disposition = "URGENT_HUMAN_SAFETY_ESCALATION"
    elif any(action["action_type"] == "ESCALATE_TO_DOMAIN_AND_POLICY_REVIEW" for action in actions):
        disposition = "HIGH_RISK_AUTHORIZED_REVIEW"
    elif any(action["action_type"] == "QUARANTINE_PENDING_AUTHORIZED_REVIEW" for action in actions):
        disposition = "TEMPORARY_QUARANTINE_PENDING_REVIEW"
    elif any(action["action_type"] in {"DEAMPLIFY_RECOMMENDATION_FEEDBACK_LOOP", "PAUSE_MONETIZATION_AND_REQUIRE_DISCLOSURE"} for action in actions):
        disposition = "FRICTION_AND_CIRCUIT_BREAK_RECOMMENDED"
    elif any(action["action_type"] in {"CONTEXTUALIZE_AND_REQUEST_EVIDENCE", "ATTACH_PROVENANCE_AND_EVIDENCE_CARD"} for action in actions):
        disposition = "PRESERVE_WITH_CONTEXT"
    else:
        disposition = "PRESERVE_AND_SURFACE"

    return {
        "disposition": disposition,
        "highest_level_rank": max_level,
        "actions": actions,
        "reason_codes": sorted(set(reasons)),
        "decision_logic": {
            "aggregate_score_used": False,
            "emotional_valence_used_as_restriction_signal": False,
            "public_interest_and_dissent_firewall": True,
            "automatic_deletion": False,
            "automatic_external_action_authority": 0,
            "temporary_actions_require_expiry": True,
            "appeal_required": True,
        },
        "rights_firewall": {
            "lawful_criticism_is_not_negative_information": True,
            "uncomfortable_truth_is_not_suppressed": True,
            "satire_and_quotation_require_context": True,
            "no_secret_permanent_blacklist": True,
            "no_person_is_classified_as_a_problem": True,
        },
    }
