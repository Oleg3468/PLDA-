"""Генерация правовых исследовательских записок.

Заполняет структуру docs/templates/legal-memo.md данными дела и
источниками из локального поиска. Записка всегда создаётся со статусом
«ожидает проверки юриста» и черновым дисклеймером.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Dict, List, Optional

from app.core import rag
from app.core.case_analyzer import analyze_case
from app.db import execute

JURISDICTION_NAMES = {
    "UA": "Украина",
    "DE": "Германия",
    "FR": "Франция",
    "PL": "Польша",
}

DISCLAIMER = (
    "> Черновик для проверки. Не является юридической консультацией "
    "и не подлежит подаче без проверки пользователем и квалифицированным "
    "специалистом."
)

DEFAULT_NEXT_STEPS = [
    "Определить компетентный орган и стадию процедуры.",
    "Найти и зафиксировать применимую норму в официальной редакции (статья, редакция, дата проверки).",
    "Собрать недостающие документы и доказательства по списку из раздела 3.",
    "Проверить сроки и условия допустимости по правилам именно этого органа.",
    "При срочном сроке — проконсультироваться с практикующим юристом.",
]


def build_memo(
    question: str,
    jurisdiction: str,
    facts: Optional[List[str]] = None,
    dates: Optional[List[str]] = None,
    unknowns: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    sources: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Строит записку по шаблону и возвращает {markdown, sources, case_id}."""
    facts = [fact.strip() for fact in (facts or []) if fact and fact.strip()]
    dates = [item.strip() for item in (dates or []) if item and item.strip()]
    unknowns = [item.strip() for item in (unknowns or []) if item and item.strip()]
    steps = [item.strip() for item in (next_steps or []) if item and item.strip()]
    if not steps:
        steps = DEFAULT_NEXT_STEPS

    case = analyze_case(question, jurisdiction, facts=facts)
    if sources is None:
        sources = rag.search_sources(
            question, jurisdiction=jurisdiction, limit=8, include_fallback=True
        )

    case_id = f"case-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    country = JURISDICTION_NAMES.get(jurisdiction, jurisdiction)
    today = date.today().isoformat()

    lines: List[str] = []
    lines.append("# Правовая исследовательская записка (черновик)")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append(
        f"> Статус проверки юристом: **ожидает проверки**. "
        f"Сформировано сервисом PLDA {today}, режим: оффлайн-план "
        f"(выводы по существу не делаются автоматически)."
    )
    lines.append("")

    lines.append("## 1. Вопрос и краткий ответ")
    lines.append("")
    lines.append(f"**Вопрос:** {question}")
    lines.append(
        "**Краткий вывод:** [заполнить после проверки первоисточников — "
        "автоматический вывод по существу не формируется]"
    )
    lines.append(f"**Дата исследования:** {today}")
    lines.append("")

    lines.append("## 2. Юрисдикция, орган и применимые даты")
    lines.append("")
    lines.append(f"- Государство/территория: {country} ({jurisdiction})")
    lines.append("- Компетентный орган: [указать]")
    lines.append("- Процедура и стадия: [указать]")
    if dates:
        lines.append("**Значимые даты:**")
        for item in dates:
            lines.append(f"- {item}")
    else:
        lines.append("- Значимые даты: [не указаны — проверить вручение решений]")
    lines.append("- Дата, на которую определяется применимое право: [указать]")
    lines.append("")

    lines.append("## 3. Материалы и установленные факты")
    lines.append("")
    if facts:
        lines.append("**Сообщено пользователем (не проверено):**")
        for fact in facts:
            lines.append(f"- {fact}")
    else:
        lines.append("- Факты не предоставлены.")
    lines.append("")
    if unknowns:
        lines.append("**Неизвестно / требует доказательства:**")
        for item in unknowns:
            lines.append(f"- {item}")
    else:
        lines.append(
            "- Неизвестные обстоятельства: [перечислить — см. план исследования]"
        )
    lines.append("")

    lines.append("## 4. Применимые источники")
    lines.append("")
    lines.append(
        "| Источник | Тип | Статус проверки | Редакция/действие | Ссылка |"
    )
    lines.append("|---|---|---|---|---|")
    if sources:
        for source in sources:
            status = (
                f"проверено {source['checked_at']}"
                if source.get("verified") and source.get("checked_at")
                else "проверено" if source.get("verified") else "требует проверки"
            )
            period = source.get("effective_from") or "—"
            if source.get("effective_to"):
                period += f" — {source['effective_to']} (утратил силу)"
            url = source.get("source_url") or "—"
            lines.append(
                f"| {source.get('title', '—')} | {source.get('source_type', '—')} "
                f"| {status} | {period} | {url} |"
            )
    else:
        lines.append("| [источники не найдены — ищите в официальной картотеке] | | | | |")
    lines.append("")

    lines.append("## 5. Анализ")
    lines.append("")
    lines.append(
        "Для каждого вопроса: **правило** (точный текст/смысл с первоисточником) → "
        "**применимость** (юрисдикция, участники, предмет, время) → "
        "**факты в поддержку** → **контраргументы** → "
        "**недостающие материалы** → **вывод и уровень неопределённости**."
    )
    lines.append("")
    lines.append("[Раздел заполняется после проверки первоисточников.]")
    lines.append("")

    lines.append("## 6. Процедура и сроки")
    lines.append("")
    lines.append(
        "| Действие | Официальное основание | Событие начала срока | "
        "Расчёт / дедлайн | Что ещё проверить |"
    )
    lines.append("|---|---|---|---|---|")
    lines.append(
        "| [заполнить] | [статья/пункт акта] | [событие] | "
        "[не указывать без подтверждения] | [правила органа] |"
    )
    lines.append("")
    lines.append(
        "Не указывайте окончательную дату, если исходные события, применимая "
        "редакция или правила расчёта не подтверждены."
    )
    lines.append("")

    lines.append("## 7. Следующие шаги")
    lines.append("")
    for index, step in enumerate(steps, start=1):
        lines.append(f"{index}. {step}")
    lines.append("")

    lines.append("## 8. Источники и ограничения")
    lines.append("")
    if sources:
        lines.append("**Первичные официальные источники для проверки:**")
        for source in sources:
            lines.append(f"- {source.get('title')} — {source.get('source_url')}")
    lines.append("")
    lines.append(
        "Записка сформирована автоматически и не содержит выводов по существу. "
        "Ссылки и статусы источников перепроверяются на дату использования; "
        "непроверенные ссылки отмечены. Перед подачей документов — "
        "проверка квалифицированным специалистом."
    )

    return {
        "markdown": "\n".join(lines),
        "sources": sources,
        "case_id": case_id,
        "category": case.category,
    }


def save_memo(
    markdown: str,
    case_id: str,
    title: str,
    anonymized: bool = False,
) -> int:
    """Сохраняет записку в очередь проверки юриста, возвращает id документа."""
    return execute(
        """
        INSERT INTO documents (case_id, doc_type, title, content_md, status, anonymized)
        VALUES (?, 'legal_memo', ?, ?, 'pending_review', ?)
        """,
        (case_id, title, markdown, int(anonymized)),
    )
