from __future__ import annotations

from typing import Any

from .models import ContentItem


def build_real_life_support_plan(
    item: ContentItem,
    profile: dict[str, float],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    context = item.context
    is_relevant = item.channel in {"offline", "hybrid"} or bool(context.get("real_life_support"))
    if not is_relevant:
        return {
            "applicable": False,
            "reason": "The submitted item is not registered as an offline or hybrid support situation.",
        }

    readiness = str(context.get("readiness", "unknown"))
    consent = str(context.get("consent", "unknown"))
    shared_risk = bool(context.get("shared_finance_or_dependents"))
    imminent = bool(context.get("imminent_danger"))
    steps = [
        {
            "step": 1,
            "name": "关系与安全先行",
            "instruction": "先确认是否存在立即人身、医疗、财务或未成年人风险；不要羞辱、围攻或用‘认知低’给人贴标签。",
        },
        {
            "step": 2,
            "name": "请求参与许可",
            "instruction": "用‘我担心这个决定的后果，愿不愿意一起核对一项具体主张？’取得有限同意；不同意时不强行改造信念。",
        },
        {
            "step": 3,
            "name": "拆分人、关系与主张",
            "instruction": "尊重当事人，同时把可核验主张、付款要求、社交隔离、时间压力和承诺后果分别列出。",
        },
        {
            "step": 4,
            "name": "暂停不可逆决定",
            "instruction": "建议24至72小时冷静期、暂缓转账/停药/退学/断联等不可逆行为；使用书面清单而非争吵。",
        },
        {
            "step": 5,
            "name": "做一个小而可逆的检验",
            "instruction": "共同选择一项能区分说法的小测试：核对原始来源、联系独立专业人士、验证退款条款或检查历史预测。",
        },
        {
            "step": 6,
            "name": "恢复替代关系与选择",
            "instruction": "提供非控制性的社交、学习、工作或治疗替代路径，减少对单一群体、导师、产品或平台的依赖。",
        },
        {
            "step": 7,
            "name": "有界升级",
            "instruction": "仅在高风险、欺诈、能力受损或迫近危险时，依法联系有资格的医疗、法律、金融、学校或安全人员；不由本系统诊断。",
        },
    ]
    if (consent in {"none", "refused"} or readiness in {"not_ready", "resistant"}) and not imminent:
        mode = "BOUNDARY_PROTECTION_WITHOUT_FORCED_BELIEF_CHANGE"
        next_action = "Protect shared resources and dependents lawfully; leave a concise evidence packet and an open invitation to review later."
    elif readiness in {"ready", "seeking_help"}:
        mode = "COLLABORATIVE_COGNITIVE_BARRIER_BREAKING"
        next_action = "Run one claim-source-incentive map and one reversible verification experiment together."
    elif imminent:
        mode = "IMMEDIATE_SAFEGUARDING"
        next_action = "Use applicable emergency or safeguarding procedures through authorized humans."
    else:
        mode = "RELATIONSHIP_PRESERVING_MOTIVATIONAL_REVIEW"
        next_action = "Ask permission to examine one concrete decision consequence rather than trying to overturn the whole worldview."

    safeguards = [
        "Do not covertly manipulate, isolate, threaten, humiliate, or impersonate the person.",
        "Do not diagnose mental illness from beliefs alone.",
        "Do not confiscate devices, money, or identity documents without lawful authority.",
        "Preserve dissent and the right to refuse persuasion, except where immediate safety duties legally apply.",
        "Separate support for the person from assessment of the claim or seller.",
    ]
    if shared_risk:
        safeguards.append("Use lawful dual-control or spending limits for shared assets while preserving the person's personal rights and appeal.")

    return {
        "applicable": True,
        "mode": mode,
        "readiness": readiness,
        "consent": consent,
        "shared_risk": shared_risk,
        "imminent_danger": imminent,
        "steps": steps,
        "next_action": next_action,
        "safeguards": safeguards,
        "professional_boundary": "This plan is supportive decision hygiene, not psychotherapy, diagnosis, guardianship, or legal adjudication.",
        "automatic_external_action_authority": 0,
    }


def build_incentive_circuit_map(item: ContentItem, manipulation: dict[str, Any]) -> dict[str, Any]:
    interest = manipulation["interest_map"]
    nodes = [
        {"id": "creator", "type": "content_or_seller", "label": interest["seller_or_creator"]},
        {"id": "claim", "type": "claim_bundle", "label": item.title},
        {"id": "audience", "type": "audience", "label": ", ".join(item.audience.get("groups", [])) if isinstance(item.audience.get("groups", []), list) else str(item.audience.get("groups", "general"))},
    ]
    edges = [
        {"from": "creator", "to": "claim", "relation": "publishes_or_sells"},
        {"from": "claim", "to": "audience", "relation": "targets_or_reaches"},
    ]
    if interest["payment_present"]:
        nodes.append({"id": "payment", "type": "payment_or_subscription", "label": "commercial conversion"})
        edges.extend([
            {"from": "audience", "to": "payment", "relation": "may_convert"},
            {"from": "payment", "to": "creator", "relation": "revenue_return"},
        ])
    if item.design:
        nodes.append({"id": "ranking", "type": "amplification", "label": "ranking / notification / engagement loop"})
        edges.extend([
            {"from": "ranking", "to": "claim", "relation": "amplifies"},
            {"from": "audience", "to": "ranking", "relation": "engagement_signal"},
        ])
    breakpoints = [
        {"target": "claim", "method": "evidence and provenance return", "reversible": True},
        {"target": "ranking", "method": "remove compulsive boosts and add user-controlled friction", "reversible": True},
        {"target": "payment", "method": "sponsor/affiliate disclosure, cooling-off period, refund audit", "reversible": True},
        {"target": "creator", "method": "claim-level accountability rather than permanent person blacklist", "reversible": True},
    ]
    return {
        "nodes": nodes,
        "edges": edges,
        "breakpoints": breakpoints,
        "principle": "Break harmful incentives and amplification loops before trying to erase people or lawful viewpoints.",
    }
