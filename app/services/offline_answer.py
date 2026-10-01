"""Оффлайн-ответ PLDA (без LLM).

Строит детерминированный структурированный ответ по правилам
docs/PROMPT_FOR_ANY_AI.md на основе модулей ядра (анализ запроса,
план исследования) и локального поиска источников. Не выдаёт выводов
по существу права — только рамки, план и источники для проверки.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from app.core import rag
from app.core.case_analyzer import analyze_case
from app.core.police_engine import POLICE_QUESTIONS
from app.core.research import create_research_plan

JURISDICTION_NAMES = {
    "UA": "Украина",
    "DE": "Германия",
    "FR": "Франция",
    "PL": "Польша",
}

_POLICE_BY_CODE = {question.code: question for question in POLICE_QUESTIONS}


def build_offline_answer(
    question: str,
    jurisdiction: str,
    facts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Формирует оффлайн-ответ: план исследования + источники из базы."""
    case = analyze_case(question, jurisdiction, facts=facts or [])
    plan = create_research_plan(question, jurisdiction)
    sources = rag.search_sources(
        question, jurisdiction=jurisdiction, limit=8, include_fallback=True
    )

    answer_md = _render(
        case=case, plan=plan, sources=sources, jurisdiction=jurisdiction
    )

    return {
        "answer_md": answer_md,
        "sources": sources,
        "mode": "offline",
        "category": case.category,
        "legal_goal": case.legal_goal,
    }


def _source_line(source: Dict[str, Any]) -> str:
    verified = source.get("verified")
    checked_at = source.get("checked_at")
    status = (
        f"проверено {checked_at}" if verified and checked_at else
        "проверено (дата не указана)" if verified else
        "требует проверки"
    )
    url = source.get("source_url") or "ссылка не указана"
    note = ""
    if source.get("effective_to"):
        note = " · статус: утратил силу, проверьте переходные положения"
    return (
        f"- **{source.get('title', 'Без названия')}** — {status}{note}. "
        f"Официальный источник: {url}"
    )


def _render(case, plan, sources: List[Dict[str, Any]], jurisdiction: str) -> str:
    country = JURISDICTION_NAMES.get(jurisdiction, jurisdiction)
    today = date.today().isoformat()

    lines: List[str] = []
    lines.append("### 1. Краткий ответ и ограничения")
    lines.append("")
    lines.append(
        "Сервис работает в **оффлайн-режиме** (LLM не подключена). "
        "Ниже — структурированные рамки исследования по правилам PLDA, "
        "а не вывод по существу. Это не юридическая консультация."
    )
    lines.append("")
    lines.append(f"- Юрисдикция: **{country}** ({jurisdiction})")
    lines.append(f"- Определённая цель: {case.legal_goal}")
    lines.append(f"- Категория запроса: {case.category}")
    lines.append(f"- Дата: {today}")
    lines.append("")

    lines.append("### 2. Факты: что известно и что неизвестно")
    lines.append("")
    if case.facts:
        lines.append("**Предоставлено пользователем (не проверено):**")
        for fact in case.facts:
            lines.append(f"- {fact}")
    else:
        lines.append("Факты не предоставлены — ответ зависит от обстоятельств дела.")
    lines.append("")
    if case.unknown_facts:
        lines.append("**Неизвестно / требует проверки:**")
        for unknown in case.unknown_facts:
            lines.append(f"- {unknown}")
        lines.append("")

    lines.append("### 3. План исследования (по правилам PLDA)")
    lines.append("")
    for task in case.research_tasks:
        lines.append(f"- {task}")
    if case.police_questions:
        lines.append("")
        lines.append("**Ключевые вопросы по вашей ситуации:**")
        for code in case.police_questions:
            lines.append(f"- {code}")
    lines.append("")

    lines.append("### 4. Источники для первичной проверки")
    lines.append("")
    if sources:
        for source in sources:
            lines.append(_source_line(source))
    else:
        lines.append(
            "В локальной базе нет источников по этому запросу. "
            "Найдите первоисточники через официальный портал юрисдикции."
        )
    lines.append("")

    lines.append("### 5. Следующие шаги")
    lines.append("")
    lines.append("1. Уточните орган, вид процедуры и стадию.")
    lines.append(
        "2. Откройте первоисточник по ссылке выше и проверьте применимую "
        "редакцию, территориальное и временное действие нормы."
    )
    lines.append(
        "3. Зафиксируйте: название акта, статью/пункт, редакцию, дату проверки."
    )
    lines.append(
        "4. Если есть срочный или пропущенный срок — немедленно проверьте "
        "расчёт у практикующего юриста."
    )
    lines.append("")

    lines.append("### 6. Ограничения ответа")
    lines.append("")
    lines.append(
        "Ответ построен детерминированно из правил PLDA и локального каталога "
        "источников. Сроки, условия допустимости и применимость норм "
        "к конкретному делу не проверены и требуют проверки по первоисточникам. "
        "Перед подачей документов — проверка квалифицированным специалистом."
    )

    return "\n".join(lines)
