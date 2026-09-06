from __future__ import annotations

import re
from typing import Any

from .utils import clamp


PATTERNS: dict[str, tuple[str, ...]] = {
    "absolute_certainty": (
        r"\bguaranteed\b", r"\b100%\b", r"\balways works\b", r"\bnever fails\b",
        r"\bscientifically proven\b", r"\bmiracle\b", r"\bcure[- ]?all\b",
        r"保证(?:赚钱|有效|治愈)", r"百分之百", r"100%", r"绝对(?:有效|正确|安全)",
        r"包治百病", r"永不失败", r"科学已经证明", r"奇迹疗法", r"稳赚不赔",
    ),
    "urgency_scarcity": (
        r"\bonly today\b", r"\blast chance\b", r"\blimited slots?\b", r"\bact now\b",
        r"\bcountdown\b", r"\bwithin 24 hours\b",
        r"仅限今天", r"最后机会", r"名额有限", r"立即(?:购买|加入|转账)", r"倒计时", r"24小时内",
    ),
    "secrecy_isolation": (
        r"\bdon['’]?t tell (?:your )?(?:family|doctor|friends?)\b",
        r"\bmainstream (?:media|science) (?:hides|won['’]?t tell)\b",
        r"\bthey don['’]?t want you to know\b", r"\bsecret knowledge\b",
        r"不要告诉(?:家人|医生|朋友)", r"主流(?:媒体|科学)不敢说", r"他们不想让你知道",
        r"内部秘密", r"被封杀的真相", r"只有圈内人才知道",
    ),
    "authority_social_proof": (
        r"\btop experts? agree\b", r"\bmillions? of users?\b", r"\bevery successful person\b",
        r"\bcelebrity endorsed\b", r"\binsider authority\b",
        r"顶级专家都", r"万人验证", r"所有成功人士", r"名人推荐", r"权威内部消息", r"国家级大师",
    ),
    "fear_shame_pressure": (
        r"\byou will regret\b", r"\bonly fools\b", r"\bif you care about your family\b",
        r"\byour life depends on it\b", r"\btoo weak to understand\b",
        r"你会后悔", r"只有傻子才", r"为了家人你必须", r"不买就", r"命运就掌握在", r"认知低的人才不信",
    ),
    "financial_guarantee": (
        r"\bguaranteed returns?\b", r"\brisk[- ]?free profit\b", r"\bdouble your money\b",
        r"\bprincipal guaranteed\b", r"\binsider investment\b",
        r"保本高收益", r"稳赚不赔", r"本金翻倍", r"零风险收益", r"内部投资渠道", r"养老钱翻倍",
    ),
    "medical_displacement": (
        r"\bstop (?:your )?medication\b", r"\bno doctor needed\b", r"\breplaces? treatment\b",
        r"\bdoctors? don['’]?t want you to know\b",
        r"立即停药", r"不用看医生", r"替代正规治疗", r"医生不敢告诉你", r"三天逆转(?:糖尿病|癌症|高血压)",
    ),
    "pseudo_knowledge_packaging": (
        r"\bquantum (?:energy|healing|frequency)\b", r"\bcosmic energy\b", r"\bsecret formula\b",
        r"\bancient frequency\b", r"\bvibrational upgrade\b",
        r"量子(?:能量|疗愈|频率)", r"宇宙能量", r"秘密公式", r"祖传频率", r"能量升级", r"改写基因频率",
    ),
    "engagement_hook": (
        r"\bwatch until the end\b", r"\byou won['’]?t believe\b", r"\bpart two\b", r"\bone more\b",
        r"看到最后", r"你绝对想不到", r"下一集更精彩", r"再刷一个", r"连续签到", r"解锁隐藏内容",
    ),
    "harassment_dehumanization": (
        r"\bvermin\b", r"\bsubhuman\b", r"\bdeserve to suffer\b",
        r"畜生不如", r"不配做人", r"活该受苦", r"应该全部消失",
    ),
    "transaction_request": (
        r"\bwire (?:money|funds)\b", r"\bsend crypto\b", r"\bpay now\b", r"\bborrow money\b",
        r"立即转账", r"扫码付款", r"借钱加入", r"缴纳入门费", r"购买课程", r"付费社群",
    ),
}


def scan_text(text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    matches: dict[str, list[str]] = {}
    for category, patterns in PATTERNS.items():
        found: list[str] = []
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                found.append(match.group(0))
        matches[category] = sorted(set(found))

    quoted_or_reported = bool(context.get("quoted_or_reported") or context.get("news_reporting"))
    satire = bool(context.get("satire"))
    context_discount = 0.25 if quoted_or_reported else (0.35 if satire else 1.0)

    category_scores = {
        category: clamp((len(items) / 3.0) * context_discount)
        for category, items in matches.items()
    }
    return {
        "matches": matches,
        "category_scores": category_scores,
        "quoted_or_reported": quoted_or_reported,
        "satire": satire,
        "context_discount": context_discount,
        "note": "Lexical signals are screening indicators, not proof of falsity or harmful intent.",
    }
