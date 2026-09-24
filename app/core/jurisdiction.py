from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JurisdictionProfile:
    country: str
    country_code: str
    national_law: bool = True
    regional_law: bool = False
    eu_law: bool = False
    international_law: bool = True
    human_rights: bool = True
    regions: List[str] = field(default_factory=list)


JURISDICTIONS = {
    "DE": JurisdictionProfile(
        country="Germany",
        country_code="DE",
        national_law=True,
        regional_law=True,
        eu_law=True,
        international_law=True,
        human_rights=True,
    ),

    "UA": JurisdictionProfile(
        country="Ukraine",
        country_code="UA",
        national_law=True,
        regional_law=True,
        eu_law=False,
        international_law=True,
        human_rights=True,
    ),

    "FR": JurisdictionProfile(
        country="France",
        country_code="FR",
        national_law=True,
        regional_law=False,
        eu_law=True,
        international_law=True,
        human_rights=True,
    ),

    "PL": JurisdictionProfile(
        country="Poland",
        country_code="PL",
        national_law=True,
        regional_law=True,
        eu_law=True,
        international_law=True,
        human_rights=True,
    ),
}


def get_jurisdiction(country_code: str) -> Optional[JurisdictionProfile]:
    return JURISDICTIONS.get(country_code.upper())


def get_applicable_layers(country_code: str) -> List[str]:
    profile = get_jurisdiction(country_code)

    if not profile:
        return []

    layers = []

    if profile.national_law:
        layers.append("national_law")

    if profile.regional_law:
        layers.append("regional_law")

    if profile.eu_law:
        layers.append("eu_law")

    if profile.international_law:
        layers.append("international_law")

    if profile.human_rights:
        layers.append("human_rights")

    return layers


def describe_jurisdiction(country_code: str) -> dict:
    profile = get_jurisdiction(country_code)

    if not profile:
        return {
            "found": False,
            "country_code": country_code.upper(),
        }

    return {
        "found": True,
        "country": profile.country,
        "country_code": profile.country_code,
        "layers": get_applicable_layers(profile.country_code),
        "regions_required": profile.regional_law,
    }
