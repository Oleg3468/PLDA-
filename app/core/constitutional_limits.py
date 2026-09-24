from dataclasses import dataclass, field
from typing import List


@dataclass
class LegalLayer:
    name: str
    jurisdiction: str
    source_types: List[str]
    mandatory: bool = True


@dataclass
class RightsCheck:
    right: str
    national_basis: List[str] = field(default_factory=list)
    international_basis: List[str] = field(default_factory=list)
    regional_basis: List[str] = field(default_factory=list)
    restriction_allowed: str = "unknown"
    proportionality_required: bool = True
    status: str = "requires_research"


@dataclass
class ConstitutionalAnalysis:
    issue: str
    jurisdiction: str
    layers: List[LegalLayer]
    checks: List[RightsCheck] = field(default_factory=list)


def default_ukraine_layers() -> List[LegalLayer]:
    return [
        LegalLayer(
            "Конституционное право Украины",
            "Ukraine",
            [
                "constitution",
                "constitutional_court",
            ],
        ),
        LegalLayer(
            "Национальное законодательство Украины",
            "Ukraine",
            [
                "statute",
                "regulation",
                "official_authority",
                "national_court",
            ],
        ),
        LegalLayer(
            "Международное право ООН",
            "International",
            [
                "un",
                "ohchr",
                "treaty_body",
            ],
        ),
        LegalLayer(
            "Европейская конвенция о правах человека",
            "Europe",
            [
                "echr",
                "hudoc",
                "council_of_europe",
            ],
        ),
        LegalLayer(
            "Право Европейского Союза",
            "European Union",
            [
                "eu",
                "cjeu",
                "eurlex",
            ],
        ),
        LegalLayer(
            "Международная защита",
            "International",
            [
                "unhcr",
                "euaa",
                "refugee_law",
            ],
        ),
    ]


def create_rights_check(right: str) -> RightsCheck:
    return RightsCheck(
        right=right,
        national_basis=[],
        international_basis=[],
        regional_basis=[],
    )


def create_analysis(
    issue: str,
    jurisdiction: str,
    rights: List[str],
) -> ConstitutionalAnalysis:

    checks = [
        create_rights_check(right)
        for right in rights
    ]

    return ConstitutionalAnalysis(
        issue=issue,
        jurisdiction=jurisdiction,
        layers=default_ukraine_layers(),
        checks=checks,
    )


def mandatory_international_review(
    analysis: ConstitutionalAnalysis,
) -> bool:
    return any(
        layer.mandatory
        and layer.jurisdiction == "International"
        for layer in analysis.layers
    )


def missing_research_layers(
    analysis: ConstitutionalAnalysis,
) -> List[str]:

    missing = []

    for layer in analysis.layers:
        if layer.mandatory:
            if not layer.source_types:
                missing.append(layer.name)

    return missing


def analysis_summary(
    analysis: ConstitutionalAnalysis,
) -> dict:

    return {
        "issue": analysis.issue,
        "jurisdiction": analysis.jurisdiction,
        "layers": [
            {
                "name": layer.name,
                "jurisdiction": layer.jurisdiction,
                "mandatory": layer.mandatory,
                "source_types": layer.source_types,
            }
            for layer in analysis.layers
        ],
        "rights": [
            {
                "right": check.right,
                "restriction_allowed":
                    check.restriction_allowed,
                "proportionality_required":
                    check.proportionality_required,
                "status": check.status,
            }
            for check in analysis.checks
        ],
        "international_review_required":
            mandatory_international_review(analysis),
    }
