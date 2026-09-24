from dataclasses import dataclass, field
from typing import List


OPPORTUNITY_TYPES = {
    "exception",
    "exemption",
    "alternative",
    "special_regime",
    "conflict",
    "ambiguity",
    "procedural_issue",
    "case_law",
    "limitation",
}


@dataclass
class LegalOpportunity:
    opportunity_type: str
    title: str
    description: str
    legal_question: str
    source_layers: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    verification_status: str = "unverified"


def create_opportunity(
    opportunity_type: str,
    title: str,
    description: str,
    legal_question: str,
    source_layers: List[str],
    conditions: List[str] = None,
    risks: List[str] = None,
) -> LegalOpportunity:

    if opportunity_type not in OPPORTUNITY_TYPES:
        raise ValueError(
            f"Unknown opportunity type: {opportunity_type}"
        )

    return LegalOpportunity(
        opportunity_type=opportunity_type,
        title=title,
        description=description,
        legal_question=legal_question,
        source_layers=source_layers,
        conditions=conditions or [],
        risks=risks or [],
    )


def opportunity_checklist() -> List[str]:
    return [
        "exception",
        "exemption",
        "alternative",
        "special_regime",
        "conflict",
        "ambiguity",
        "procedural_issue",
        "case_law",
        "limitation",
    ]


def classify_opportunity(opportunity: LegalOpportunity) -> str:
    if opportunity.verification_status == "verified":
        return "verified_opportunity"

    if opportunity.verification_status == "contradicted":
        return "rejected"

    return "requires_verification"
