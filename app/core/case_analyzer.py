from dataclasses import dataclass, field
from typing import List

from app.core.intent import analyze_intent
from app.core.research import create_research_plan
from app.core.police_engine import get_question_codes
from app.core.opportunity import opportunity_checklist


@dataclass
class CaseAnalysis:
    original_request: str
    jurisdiction: str
    legal_goal: str
    category: str
    facts: List[str] = field(default_factory=list)
    unknown_facts: List[str] = field(default_factory=list)
    research_tasks: List[str] = field(default_factory=list)
    police_questions: List[str] = field(default_factory=list)
    opportunity_checks: List[str] = field(default_factory=list)


def analyze_case(
    request: str,
    jurisdiction: str,
    facts: List[str] = None,
) -> CaseAnalysis:

    intent = analyze_intent(request)
    plan = create_research_plan(request, jurisdiction)

    return CaseAnalysis(
        original_request=request,
        jurisdiction=jurisdiction,
        legal_goal=intent.legal_goal,
        category=intent.category,
        facts=facts or [],
        unknown_facts=[
            "Дата и место события",
            "Конкретные действия другой стороны",
            "Документы или решения, относящиеся к ситуации",
            "Какие требования были предъявлены пользователю",
        ],
        research_tasks=[
            task.task_id for task in plan.tasks
        ],
        police_questions=get_question_codes()
        if intent.category == "police_encounter"
        else [],
        opportunity_checks=opportunity_checklist(),
    )


def analysis_to_dict(analysis: CaseAnalysis) -> dict:
    return {
        "original_request": analysis.original_request,
        "jurisdiction": analysis.jurisdiction,
        "legal_goal": analysis.legal_goal,
        "category": analysis.category,
        "facts": analysis.facts,
        "unknown_facts": analysis.unknown_facts,
        "research_tasks": analysis.research_tasks,
        "police_questions": analysis.police_questions,
        "opportunity_checks": analysis.opportunity_checks,
    }
