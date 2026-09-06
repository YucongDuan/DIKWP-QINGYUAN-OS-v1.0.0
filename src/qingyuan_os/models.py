from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ScenarioError(ValueError):
    pass


_ALLOWED_CHANNELS = {"online", "offline", "hybrid"}
_ALLOWED_STAKES = {"low", "medium", "high", "critical"}
_ALLOWED_CLAIM_TYPES = {
    "factual", "medical", "financial", "legal", "public_safety",
    "scientific", "historical", "testimonial", "opinion", "satire", "other",
}


@dataclass(frozen=True)
class EvidenceItem:
    type: str = "none"
    locator: str = ""
    independent: bool = False
    verifiable: bool = False
    direct: bool = False
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceItem":
        return cls(
            type=str(data.get("type", "none")),
            locator=str(data.get("locator", "")),
            independent=bool(data.get("independent", False)),
            verifiable=bool(data.get("verifiable", False)),
            direct=bool(data.get("direct", False)),
            note=str(data.get("note", "")),
        )


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    claim_type: str = "factual"
    stakes: str = "medium"
    evidence: tuple[EvidenceItem, ...] = field(default_factory=tuple)
    bounded: bool = True
    requested_behavior: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], index: int) -> "Claim":
        claim_id = str(data.get("claim_id") or f"claim-{index + 1}")
        text = str(data.get("text", "")).strip()
        if not text:
            raise ScenarioError(f"claim {claim_id} has no text")
        claim_type = str(data.get("type", "factual"))
        if claim_type not in _ALLOWED_CLAIM_TYPES:
            claim_type = "other"
        stakes = str(data.get("stakes", "medium"))
        if stakes not in _ALLOWED_STAKES:
            stakes = "medium"
        evidence = tuple(EvidenceItem.from_dict(item) for item in data.get("evidence", []) if isinstance(item, dict))
        return cls(
            claim_id=claim_id,
            text=text,
            claim_type=claim_type,
            stakes=stakes,
            evidence=evidence,
            bounded=bool(data.get("bounded", True)),
            requested_behavior=str(data.get("requested_behavior", "")),
        )


@dataclass(frozen=True)
class ContentItem:
    item_id: str
    title: str
    channel: str
    content_type: str
    language: str
    text: str
    source: dict[str, Any]
    audience: dict[str, Any]
    claims: tuple[Claim, ...]
    commercial: dict[str, Any]
    design: dict[str, Any]
    context: dict[str, Any]
    declared_outcomes: dict[str, Any]
    purpose: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentItem":
        item_id = str(data.get("item_id", "")).strip()
        if not item_id:
            raise ScenarioError("item_id is required")
        title = str(data.get("title", item_id)).strip()
        channel = str(data.get("channel", "online"))
        if channel not in _ALLOWED_CHANNELS:
            raise ScenarioError(f"unsupported channel: {channel}")
        text = str(data.get("text", "")).strip()
        if not text:
            raise ScenarioError("text is required")
        claims_raw = data.get("claims", [])
        if not isinstance(claims_raw, list):
            raise ScenarioError("claims must be a list")
        claims = tuple(Claim.from_dict(item, index) for index, item in enumerate(claims_raw) if isinstance(item, dict))
        purpose = dict(data.get("purpose", {}))
        purpose.setdefault("owner", "local_authorized_reviewer")
        purpose.setdefault("objective", "reduce manipulative harm while preserving truth, autonomy, dissent, and appeal")
        purpose.setdefault("automatic_external_action_authority", 0)
        if int(purpose.get("automatic_external_action_authority", 0)) != 0:
            raise ScenarioError("prototype automatic_external_action_authority must remain 0")
        return cls(
            item_id=item_id,
            title=title,
            channel=channel,
            content_type=str(data.get("content_type", "post")),
            language=str(data.get("language", "zh-CN")),
            text=text,
            source=dict(data.get("source", {})),
            audience=dict(data.get("audience", {})),
            claims=claims,
            commercial=dict(data.get("commercial", {})),
            design=dict(data.get("design", {})),
            context=dict(data.get("context", {})),
            declared_outcomes=dict(data.get("declared_outcomes", {})),
            purpose=purpose,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "channel": self.channel,
            "content_type": self.content_type,
            "language": self.language,
            "text": self.text,
            "source": self.source,
            "audience": self.audience,
            "claims": [
                {
                    "claim_id": claim.claim_id,
                    "text": claim.text,
                    "type": claim.claim_type,
                    "stakes": claim.stakes,
                    "bounded": claim.bounded,
                    "requested_behavior": claim.requested_behavior,
                    "evidence": [item.__dict__ for item in claim.evidence],
                }
                for claim in self.claims
            ],
            "commercial": self.commercial,
            "design": self.design,
            "context": self.context,
            "declared_outcomes": self.declared_outcomes,
            "purpose": self.purpose,
        }
