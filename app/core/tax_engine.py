from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class TaxFinding:
    country: str
    topic: str
    legal_basis: str
    type: str
    strength: str
    explanation: str
    risk: str
    source_required: bool = True


class TaxEngine:
    """
    Анализ налоговых вопросов.

    Цель:
    - находить законные способы оптимизации;
    - выявлять льготы и исключения;
    - обнаруживать возможные коллизии;
    - отделять оптимизацию от уклонения;
    - оценивать юридический риск;
    - не выдумывать правовые основания.
    """

    ALLOWED_TYPES = {
        "optimization",
        "exemption",
        "deduction",
        "exception",
        "conflict",
        "risk",
        "no_basis",
    }

    STRENGTHS = {
        "high",
        "medium",
        "low",
        "unknown",
    }

    def analyze(
        self,
        country: str,
        topic: str,
        facts: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        facts = facts or {}

        result = {
            "country": country,
            "topic": topic,
            "facts": facts,
            "findings": [],
            "warning": (
                "Налоговый вывод должен быть подтверждён "
                "актуальным законодательством и официальным источником."
            ),
        }

        # На этом этапе движок не выдумывает нормы.
        # Фактические положения будут поступать из legal research.
        finding = TaxFinding(
            country=country,
            topic=topic,
            legal_basis="NOT_YET_RESEARCHED",
            type="no_basis",
            strength="unknown",
            explanation=(
                "Конкретное правовое основание ещё не проверено "
                "по законодательству данной юрисдикции."
            ),
            risk="Нельзя делать окончательный вывод без проверки источника.",
        )

        result["findings"].append(asdict(finding))
        return result


def analyze_tax(
    country: str,
    topic: str,
    facts: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return TaxEngine().analyze(country, topic, facts)


if __name__ == "__main__":
    import json

    result = analyze_tax(
        "TEST",
        "tax optimization",
        {"example": True},
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
