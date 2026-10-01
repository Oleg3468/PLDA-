"""Поиск по локальной базе официальных источников (простой RAG без векторов).

Оценивает совпадение токенов запроса с названием, статьёй и описанием
источника. Проверенным источникам даётся приоритет. Ничего не выдумывает:
возвращает только реально существующие строки базы с их статусом проверки.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.db import fetch_all, fetch_one

_TOKEN_RE = re.compile(r"[0-9a-zа-яїієґёщ\-]{3,}", re.IGNORECASE)

_STOPWORDS = {
    # русские
    "для", "как", "что", "это", "или", "при", "над", "под", "его", "его",
    "мне", "меня", "быть", "был", "где", "кто", "все", "всё", "могу",
    "нужно", "можно", "хочу", "есть", "какой", "какая", "какие", "чтобы",
    # украинские
    "для", "як", "що", "це", "або", "при", "де", "хто", "всі", "треба",
    # английские
    "the", "and", "for", "with", "how", "what", "can", "you", "are",
}


def _tokens(text: str) -> List[str]:
    return [
        token.lower()
        for token in _TOKEN_RE.findall(text or "")
        if token.lower() not in _STOPWORDS
    ]


def _variants(token: str) -> List[str]:
    """Простая заморфология: для длинного слова добавляем усечённые формы,
    чтобы «полиции» находило «полиция», а «обжаловать» — «обжалование»."""
    if len(token) > 5:
        return [token, token[:-1], token[:-2]]
    return [token]


def _contains_any(field: str, token: str) -> bool:
    return any(variant in field for variant in _variants(token))


def search_sources(
    query: str,
    jurisdiction: Optional[str] = None,
    limit: int = 8,
    include_fallback: bool = False,
) -> List[Dict[str, Any]]:
    """Ищет источники по запросу.

    jurisdiction ограничивает выборку источниками этой юрисдикции
    и международными. include_fallback=True вернёт стартовый набор
    источников юрисдикции, если прямых совпадений нет.
    """
    conditions = []
    params: tuple = ()
    if jurisdiction:
        conditions.append("(jurisdiction = ? OR jurisdiction = 'international')")
        params = (jurisdiction.strip().upper(),)

    sql = "SELECT * FROM legal_sources"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    rows = fetch_all(sql, params)
    if not rows:
        return []

    query_tokens = set(_tokens(query))
    query_lower = (query or "").strip().lower()

    scored: List[tuple] = []
    for row in rows:
        title = (row.get("title") or "").lower()
        article = (row.get("article") or "").lower()
        text = (row.get("text") or "").lower()

        score = 0.0
        for token in query_tokens:
            if _contains_any(title, token):
                score += 3
            if _contains_any(article, token):
                score += 2
            if _contains_any(text, token):
                score += 1

        if query_lower and query_lower in title:
            score += 6

        if score and row.get("verified"):
            score *= 1.5

        if score > 0:
            scored.append((score, row))

    scored.sort(
        key=lambda pair: (
            -pair[0],
            -int(pair[1].get("verified") or 0),
            pair[1].get("id") or 0,
        )
    )

    results = [
        {**row, "match_score": round(score, 2)} for score, row in scored[:limit]
    ]

    if not results and include_fallback:
        fallback = sorted(
            rows,
            key=lambda r: (-int(r.get("verified") or 0), r.get("id") or 0),
        )
        results = [{**row, "match_score": 0.0} for row in fallback[:limit]]

    return results


def get_stats() -> Dict[str, Any]:
    total = fetch_one("SELECT COUNT(*) AS total FROM legal_sources") or {}
    verified = fetch_one(
        "SELECT COUNT(*) AS total FROM legal_sources WHERE verified = 1"
    ) or {}
    jurisdictions = fetch_all(
        "SELECT jurisdiction, COUNT(*) AS total FROM legal_sources"
        " GROUP BY jurisdiction ORDER BY total DESC"
    )
    return {
        "total": total.get("total", 0),
        "verified": verified.get("total", 0),
        "by_jurisdiction": jurisdictions,
    }
