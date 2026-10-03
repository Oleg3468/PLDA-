"""Оценочный движок PLDA: «золотой набор» контрольных вопросов.

Идея перенята у RRSI (google-research/rrsi): изменения промптов, правил и
каталога источников должны подтверждаться измерениями, а не впечатлениями.
Набор работает полностью в оффлайне и проверяет:
  1) RAG-поиск находит ожидаемые официальные источники;
  2) плоскости анализа («физлицо»/«человек») отражаются в ответе;
  3) оффлайн-ответ содержит обязательные элементы и дисклеймер;
  4) записка содержит обязательные элементы и статус проверки юристом.

Запуск: pytest tests/test_golden.py  или  GET /api/eval.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.core import rag
from app.db import seed_if_empty
from app.services import memo as memo_service
from app.services import offline_answer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = PROJECT_ROOT / "tests" / "golden" / "legal_questions.json"

ANSWER_UNIVERSAL = ["не юридическая консультация", "### 1. Краткий ответ"]
MEMO_UNIVERSAL = [
    "Правовая исследовательская записка",
    "ожидает проверки",
    "Не является юридической консультацией",
]


def load_cases() -> List[Dict[str, Any]]:
    payload = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return payload.get("cases", [])


def _check(checks: List[Dict[str, Any]], name: str, passed: bool) -> None:
    checks.append({"name": name, "passed": bool(passed)})


def run_golden_evaluation(limit: int = 8) -> Dict[str, Any]:
    """Прогоняет золотой набор и возвращает отчёт."""
    seed_if_empty()

    checks_total = 0
    checks_passed = 0
    case_results: List[Dict[str, Any]] = []

    for case in load_cases():
        checks: List[Dict[str, Any]] = []
        jurisdiction = case.get("jurisdiction", "UA")
        planes = case.get("planes", [])

        # --- 1. RAG-поиск -------------------------------------------------
        sources = rag.search_sources(
            case["question"], jurisdiction=jurisdiction, limit=limit
        )
        for expected in case.get("expected_sources", []):
            found = any(
                expected.lower() in (source.get("title") or "").lower()
                for source in sources
            )
            _check(checks, f"rag находит «{expected}»", found)

        international_found = [
            source
            for source in sources
            if source.get("jurisdiction") == "international"
        ]
        national_found = [
            source
            for source in sources
            if source.get("jurisdiction") != "international"
        ]

        # --- 2. Плоскости анализа -----------------------------------------
        if "human" in planes:
            _check(
                checks,
                "плоскость «человек»: найден международный источник",
                bool(international_found),
            )
        if "physical_person" in planes:
            _check(
                checks,
                "плоскость «физлицо»: найден национальный источник",
                bool(national_found),
            )

        # --- 3. Оффлайн-ответ ---------------------------------------------
        answer = offline_answer.build_offline_answer(case["question"], jurisdiction)
        markdown = answer["answer_md"]

        for phrase in ANSWER_UNIVERSAL:
            _check(checks, f"ответ содержит «{phrase}»", phrase in markdown)
        for phrase in case.get("answer_must_contain", []):
            _check(checks, f"ответ содержит «{phrase}»", phrase in markdown)
        for phrase in case.get("answer_must_not_contain", []):
            _check(checks, f"ответ НЕ содержит «{phrase}»", phrase not in markdown)

        if "human" in planes and international_found:
            reflected = any(
                (source.get("title") or "") in markdown
                for source in international_found
            )
            _check(
                checks,
                "источник плоскости «человек» отражён в ответе",
                reflected,
            )

        # --- 4. Записка -----------------------------------------------------
        memo_document = memo_service.build_memo(
            question=case["question"], jurisdiction=jurisdiction
        )
        memo_markdown = memo_document["markdown"]
        for phrase in MEMO_UNIVERSAL:
            _check(checks, f"записка содержит «{phrase}»", phrase in memo_markdown)
        for phrase in case.get("memo_must_contain", []):
            _check(checks, f"записка содержит «{phrase}»", phrase in memo_markdown)

        passed = sum(1 for item in checks if item["passed"])
        checks_total += len(checks)
        checks_passed += passed
        case_results.append(
            {
                "id": case.get("id"),
                "question": case.get("question"),
                "jurisdiction": jurisdiction,
                "planes": planes,
                "passed": passed == len(checks),
                "checks_passed": passed,
                "checks_total": len(checks),
                "failed": [
                    item["name"] for item in checks if not item["passed"]
                ],
            }
        )

    return {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "golden_set": str(GOLDEN_PATH.relative_to(PROJECT_ROOT)),
        "cases_total": len(case_results),
        "cases_passed": sum(1 for item in case_results if item["passed"]),
        "checks_total": checks_total,
        "checks_passed": checks_passed,
        "all_passed": checks_total > 0 and checks_passed == checks_total,
        "cases": case_results,
    }
