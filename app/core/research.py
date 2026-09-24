from dataclasses import dataclass, field
from typing import List


@dataclass
class ResearchTask:
    task_id: str
    question: str
    priority: str
    source_layers: List[str] = field(default_factory=list)
    search_terms: List[str] = field(default_factory=list)


@dataclass
class ResearchPlan:
    original_request: str
    jurisdiction: str
    tasks: List[ResearchTask] = field(default_factory=list)


def create_general_tasks() -> List[ResearchTask]:
    return [
        ResearchTask(
            "LAW",
            "Какие нормы непосредственно регулируют ситуацию?",
            "critical",
            ["national_law"],
            ["applicable law", "statute", "regulation"],
        ),
        ResearchTask(
            "RIGHTS",
            "Какие права пользователя затрагиваются?",
            "high",
            ["human_rights", "constitutional_law"],
            ["fundamental rights", "constitutional rights"],
        ),
        ResearchTask(
            "EXCEPTIONS",
            "Существуют ли исключения из общего правила?",
            "high",
            ["national_law"],
            ["exception", "exemption", "special provision"],
        ),
        ResearchTask(
            "ALTERNATIVES",
            "Существуют ли законные альтернативные способы достижения цели?",
            "high",
            ["national_law"],
            ["alternative procedure", "legal alternative"],
        ),
        ResearchTask(
            "CONFLICTS",
            "Существуют ли коллизии или противоречия между нормами?",
            "high",
            ["national_law", "constitutional_law"],
            ["conflict of laws", "inconsistency", "interpretation"],
        ),
        ResearchTask(
            "CASE_LAW",
            "Как суды толкуют применимые нормы?",
            "high",
            ["case_law"],
            ["court decision", "judgment", "case law"],
        ),
        ResearchTask(
            "PROCEDURE",
            "Соблюдена ли установленная процедура?",
            "high",
            ["national_law", "administrative_law"],
            ["procedure", "procedural requirements"],
        ),
        ResearchTask(
            "COUNTERARGUMENT",
            "Какие аргументы могут быть использованы против пользователя?",
            "high",
            ["national_law", "case_law"],
            ["counterargument", "opposing argument"],
        ),
        ResearchTask(
            "REMEDY",
            "Какие реальные средства правовой защиты доступны?",
            "critical",
            ["national_law", "human_rights"],
            ["appeal", "complaint", "judicial remedy"],
        ),
    ]


def create_research_plan(
    request: str,
    jurisdiction: str,
) -> ResearchPlan:
    return ResearchPlan(
        original_request=request,
        jurisdiction=jurisdiction,
        tasks=create_general_tasks(),
    )


def plan_to_dict(plan: ResearchPlan) -> dict:
    return {
        "original_request": plan.original_request,
        "jurisdiction": plan.jurisdiction,
        "tasks": [
            {
                "task_id": task.task_id,
                "question": task.question,
                "priority": task.priority,
                "source_layers": task.source_layers,
                "search_terms": task.search_terms,
            }
            for task in plan.tasks
        ],
    }
