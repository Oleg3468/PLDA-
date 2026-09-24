from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class InternationalNorm:
    norm_id: str
    instrument: str
    article: str
    right: str
    scope: str
    source_type: str
    legal_weight: str
    keywords: List[str] = field(default_factory=list)


INTERNATIONAL_NORMS = [
    InternationalNorm(
        "ICCPR_6",
        "ICCPR",
        "Article 6",
        "right_to_life",
        "universal",
        "treaty",
        "binding",
        ["life", "death", "right to life"],
    ),
    InternationalNorm(
        "ICCPR_7",
        "ICCPR",
        "Article 7",
        "freedom_from_torture",
        "universal",
        "treaty",
        "binding",
        ["torture", "cruel", "inhuman", "degrading"],
    ),
    InternationalNorm(
        "ICCPR_9",
        "ICCPR",
        "Article 9",
        "liberty_and_security",
        "universal",
        "treaty",
        "binding",
        ["arrest", "detention", "liberty"],
    ),
    InternationalNorm(
        "ICCPR_14",
        "ICCPR",
        "Article 14",
        "fair_trial",
        "universal",
        "treaty",
        "binding",
        ["fair trial", "lawyer", "defence"],
    ),
    InternationalNorm(
        "ICCPR_18",
        "ICCPR",
        "Article 18",
        "freedom_of_conscience",
        "universal",
        "treaty",
        "binding",
        ["conscience", "religion", "belief", "conscientious objection"],
    ),
    InternationalNorm(
        "ICCPR_26",
        "ICCPR",
        "Article 26",
        "equality_and_non_discrimination",
        "universal",
        "treaty",
        "binding",
        ["discrimination", "sex", "gender", "equality"],
    ),
    InternationalNorm(
        "ECHR_2",
        "ECHR",
        "Article 2",
        "right_to_life",
        "europe",
        "treaty",
        "binding",
        ["life", "death"],
    ),
    InternationalNorm(
        "ECHR_3",
        "ECHR",
        "Article 3",
        "freedom_from_torture",
        "europe",
        "treaty",
        "binding",
        ["torture", "inhuman", "degrading"],
    ),
    InternationalNorm(
        "ECHR_5",
        "ECHR",
        "Article 5",
        "liberty_and_security",
        "europe",
        "treaty",
        "binding",
        ["arrest", "detention", "liberty"],
    ),
    InternationalNorm(
        "ECHR_8",
        "ECHR",
        "Article 8",
        "private_and_family_life",
        "europe",
        "treaty",
        "binding",
        ["privacy", "family", "private life"],
    ),
    InternationalNorm(
        "ECHR_9",
        "ECHR",
        "Article 9",
        "freedom_of_conscience",
        "europe",
        "treaty",
        "binding",
        ["conscience", "belief", "religion"],
    ),
    InternationalNorm(
        "ECHR_14",
        "ECHR",
        "Article 14",
        "non_discrimination",
        "europe",
        "treaty",
        "binding",
        ["discrimination", "sex", "gender", "equality"],
    ),
    InternationalNorm(
        "REFUGEE_1A",
        "Refugee Convention",
        "Article 1A",
        "refugee_status",
        "international",
        "treaty",
        "binding",
        ["persecution", "refugee", "protected ground"],
    ),
    InternationalNorm(
        "REFUGEE_33",
        "Refugee Convention",
        "Article 33",
        "non_refoulement",
        "international",
        "treaty",
        "binding",
        ["return", "refoulement", "persecution"],
    ),
]


def all_norms() -> List[InternationalNorm]:
    return INTERNATIONAL_NORMS


def find_norms_by_right(right: str) -> List[InternationalNorm]:
    return [
        norm for norm in INTERNATIONAL_NORMS
        if norm.right == right
    ]


def find_norms_by_keyword(keyword: str) -> List[InternationalNorm]:
    key = keyword.lower()

    return [
        norm for norm in INTERNATIONAL_NORMS
        if key in norm.right.lower()
        or any(key in item.lower() for item in norm.keywords)
    ]


def rights_for_case(rights: List[str]) -> List[InternationalNorm]:
    result = []

    for right in rights:
        result.extend(find_norms_by_right(right))

    return result


def international_review(rights: List[str]) -> dict:
    norms = rights_for_case(rights)

    return {
        "rights_requested": rights,
        "norm_count": len(norms),
        "norms": [
            {
                "id": norm.norm_id,
                "instrument": norm.instrument,
                "article": norm.article,
                "right": norm.right,
                "source_type": norm.source_type,
                "legal_weight": norm.legal_weight,
            }
            for norm in norms
        ],
    }


def mandatory_treaty_review(
    norms: List[InternationalNorm],
) -> List[InternationalNorm]:
    return [
        norm
        for norm in norms
        if norm.source_type == "treaty"
        and norm.legal_weight == "binding"
    ]
