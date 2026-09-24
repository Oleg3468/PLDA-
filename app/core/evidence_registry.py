from dataclasses import dataclass, field
from typing import List, Optional


SOURCE_LEVELS = {
    "constitution",
    "statute",
    "regulation",
    "official_authority",
    "national_court",
    "international_court",
    "un",
    "ohchr",
    "council_of_europe",
    "eu",
    "unhcr",
    "euaa",
    "official_investigation",
    "reliable_media",
    "media",
    "social_media",
    "unknown",
}


EVIDENCE_STATUSES = {
    "verified",
    "partially_verified",
    "unverified",
    "contradicted",
    "outdated",
}


@dataclass
class EvidenceRecord:
    title: str
    source_level: str
    publisher: str
    country: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    document_reference: Optional[str] = None
    paragraph: Optional[str] = None
    claim: str = ""
    limitations: List[str] = field(default_factory=list)
    status: str = "unverified"


def validate_record(record: EvidenceRecord) -> None:
    if record.source_level not in SOURCE_LEVELS:
        raise ValueError(
            f"Unknown source level: {record.source_level}"
        )

    if record.status not in EVIDENCE_STATUSES:
        raise ValueError(
            f"Unknown evidence status: {record.status}"
        )


def evidence_weight(source_level: str) -> int:
    weights = {
        "constitution": 100,
        "statute": 100,
        "regulation": 95,
        "official_authority": 90,
        "national_court": 95,
        "international_court": 100,
        "un": 95,
        "ohchr": 95,
        "council_of_europe": 95,
        "eu": 100,
        "unhcr": 90,
        "euaa": 90,
        "official_investigation": 90,
        "reliable_media": 65,
        "media": 50,
        "social_media": 20,
        "unknown": 0,
    }

    return weights.get(source_level, 0)


def can_support_legal_fact(record: EvidenceRecord) -> bool:
    validate_record(record)

    return (
        record.status == "verified"
        and evidence_weight(record.source_level) >= 90
    )


def can_support_event_report(record: EvidenceRecord) -> bool:
    validate_record(record)

    return (
        record.status in {
            "verified",
            "partially_verified",
        }
        and evidence_weight(record.source_level) >= 50
    )


def classify_record(record: EvidenceRecord) -> str:
    validate_record(record)

    if can_support_legal_fact(record):
        return "primary_or_authoritative"

    if can_support_event_report(record):
        return "secondary_or_supporting"

    if record.status == "contradicted":
        return "contradicted"

    if record.status == "outdated":
        return "outdated"

    return "unverified"


def registry_summary(record: EvidenceRecord) -> dict:
    validate_record(record)

    return {
        "title": record.title,
        "source_level": record.source_level,
        "publisher": record.publisher,
        "country": record.country,
        "date": record.date,
        "document_reference": record.document_reference,
        "paragraph": record.paragraph,
        "claim": record.claim,
        "status": record.status,
        "weight": evidence_weight(record.source_level),
        "classification": classify_record(record),
        "can_support_legal_fact":
            can_support_legal_fact(record),
        "limitations": record.limitations,
    }
