from dataclasses import dataclass
from urllib.parse import quote_plus
from typing import List


@dataclass(frozen=True)
class LegalSource:
    source_id: str
    name: str
    authority: str
    source_type: str
    base_url: str
    priority: int
    description: str


LEGAL_SOURCES = [
    LegalSource(
        "UN_ODS",
        "UN Official Document System",
        "United Nations",
        "international",
        "https://documents.un.org/",
        1,
        "Official UN documents and resolutions.",
    ),
    LegalSource(
        "UN_DOCS",
        "UN Documents",
        "United Nations",
        "international",
        "https://docs.un.org/",
        1,
        "Official UN document identification.",
    ),
    LegalSource(
        "OHCHR_UHRI",
        "Universal Human Rights Index",
        "OHCHR",
        "human_rights",
        "https://uhri.ohchr.org/",
        1,
        "UN treaty bodies, UPR and Special Procedures.",
    ),
    LegalSource(
        "HUDOC",
        "HUDOC",
        "European Court of Human Rights",
        "case_law",
        "https://hudoc.echr.coe.int/",
        1,
        "ECHR judgments, decisions and related materials.",
    ),
    LegalSource(
        "EURLEX",
        "EUR-Lex",
        "European Union",
        "eu_law",
        "https://eur-lex.europa.eu/",
        1,
        "EU legislation, treaties and CJEU case law.",
    ),
    LegalSource(
        "REFWORLD",
        "Refworld",
        "UNHCR",
        "refugee_law",
        "https://www.refworld.org/",
        1,
        "Refugee law, legislation, case law and UNHCR guidance.",
    ),
]


def get_sources(source_type: str = None) -> List[LegalSource]:
    if source_type is None:
        return LEGAL_SOURCES

    return [
        source for source in LEGAL_SOURCES
        if source.source_type == source_type
    ]


def get_source(source_id: str) -> LegalSource:
    for source in LEGAL_SOURCES:
        if source.source_id == source_id:
            return source

    raise ValueError(f"Unknown legal source: {source_id}")


def build_search_url(source_id: str, query: str) -> str:
    source = get_source(source_id)
    encoded = quote_plus(query)

    if source_id == "UN_DOCS":
        return f"https://docs.un.org/search?q={encoded}"

    if source_id == "UN_ODS":
        return f"https://documents.un.org/search?query={encoded}"

    if source_id == "HUDOC":
        return f"https://hudoc.echr.coe.int/eng#{encoded}"

    if source_id == "EURLEX":
        return f"https://eur-lex.europa.eu/search.html?query={encoded}"

    if source_id == "REFWORLD":
        return f"https://www.refworld.org/search?query={encoded}"

    if source_id == "OHCHR_UHRI":
        return f"https://uhri.ohchr.org/en/search?query={encoded}"

    return f"{source.base_url}?q={encoded}"


def search_plan(
    query: str,
    include_human_rights: bool = True,
    include_refugee_law: bool = True,
) -> list:
    source_ids = [
        "UN_ODS",
        "UN_DOCS",
        "HUDOC",
        "EURLEX",
    ]

    if include_human_rights:
        source_ids.append("OHCHR_UHRI")

    if include_refugee_law:
        source_ids.append("REFWORLD")

    return [
        {
            "source_id": source_id,
            "source": get_source(source_id).name,
            "authority": get_source(source_id).authority,
            "url": build_search_url(source_id, query),
            "priority": get_source(source_id).priority,
        }
        for source_id in source_ids
    ]


def source_ids() -> List[str]:
    return [source.source_id for source in LEGAL_SOURCES]


def source_summary() -> list:
    return [
        {
            "id": source.source_id,
            "name": source.name,
            "authority": source.authority,
            "type": source.source_type,
            "priority": source.priority,
        }
        for source in LEGAL_SOURCES
    ]
