from dataclasses import dataclass, field
from typing import List, Optional


VALID_STATUSES = {
    "verified",
    "partially_verified",
    "unverified",
    "contradicted",
    "outdated",
}

VALID_STRENGTHS = {
    "strong",
    "moderate",
    "weak",
    "unknown",
}


@dataclass
class Evidence:
    source_id: Optional[int]
    source_title: str
    source_type: str
    source_url: Optional[str] = None
    quote: Optional[str] = None
    relevance: str = "unknown"


@dataclass
class VerifiedArgument:
    argument: str
    status: str = "unverified"
    strength: str = "unknown"
    evidence: List[Evidence] = field(default_factory=list)
    reasoning: Optional[str] = None


def validate_status(status: str) -> bool:
    return status in VALID_STATUSES


def validate_strength(strength: str) -> bool:
    return strength in VALID_STRENGTHS


def verify_argument(
    argument: str,
    evidence: List[Evidence],
    status: str,
    strength: str,
    reasoning: Optional[str] = None,
) -> VerifiedArgument:

    if not validate_status(status):
        raise ValueError(
            f"Invalid verification status: {status}"
        )

    if not validate_strength(strength):
        raise ValueError(
            f"Invalid argument strength: {strength}"
        )

    if status == "verified" and not evidence:
        raise ValueError(
            "A verified argument must have evidence."
        )

    return VerifiedArgument(
        argument=argument,
        status=status,
        strength=strength,
        evidence=evidence,
        reasoning=reasoning,
    )


def can_be_presented_as_fact(argument: VerifiedArgument) -> bool:
    return argument.status == "verified"


def verification_summary(argument: VerifiedArgument) -> dict:
    return {
        "argument": argument.argument,
        "status": argument.status,
        "strength": argument.strength,
        "evidence_count": len(argument.evidence),
        "can_be_presented_as_fact": can_be_presented_as_fact(argument),
        "reasoning": argument.reasoning,
    }
