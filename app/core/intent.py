from dataclasses import dataclass
from typing import List


@dataclass
class LegalIntent:
    original_request: str
    legal_goal: str
    category: str
    risk_level: str
    research_tasks: List[str]


def analyze_intent(request: str) -> LegalIntent:
    text = request.lower()

    if any(word in text for word in [
        "уклониться",
        "скрыть налог",
        "обмануть налоговую",
    ]):
        return LegalIntent(
            original_request=request,
            legal_goal="Законно уменьшить налоговую нагрузку",
            category="tax_optimization",
            risk_level="high",
            research_tasks=[
                "найти законные налоговые льготы",
                "найти вычеты и допустимые расходы",
                "проверить альтернативные налоговые режимы",
                "проверить ограничения и риски",
            ],
        )

    if any(word in text for word in [
        "обойти закон",
        "обойти запрет",
        "обойти правило",
    ]):
        return LegalIntent(
            original_request=request,
            legal_goal="Найти законный способ достичь цели",
            category="legal_alternative",
            risk_level="medium",
            research_tasks=[
                "найти исключения",
                "найти альтернативные процедуры",
                "проверить основания для обжалования",
                "проверить судебную практику",
            ],
        )

    if any(word in text for word in [
        "полиция",
        "полицейский",
        "остановили",
        "задержали",
    ]):
        return LegalIntent(
            original_request=request,
            legal_goal="Определить права пользователя и законность действий полиции",
            category="police_encounter",
            risk_level="medium",
            research_tasks=[
                "установить юрисдикцию",
                "определить полномочия полиции",
                "проверить обязательную процедуру",
                "проверить права человека",
                "найти доступные средства защиты",
            ],
        )

    return LegalIntent(
        original_request=request,
        legal_goal="Определить законные права, обязанности и средства защиты",
        category="general_legal",
        risk_level="unknown",
        research_tasks=[
            "определить юрисдикцию",
            "определить применимое право",
            "найти нормы в пользу пользователя",
            "найти противоположные нормы",
            "проверить судебную практику",
        ],
    )


def intent_to_dict(intent: LegalIntent) -> dict:
    return {
        "original_request": intent.original_request,
        "legal_goal": intent.legal_goal,
        "category": intent.category,
        "risk_level": intent.risk_level,
        "research_tasks": intent.research_tasks,
    }
