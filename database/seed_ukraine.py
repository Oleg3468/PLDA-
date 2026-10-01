"""Наполнение базы PLDA стартовым набором украинских официальных источников.

Запуск вручную:  python -m database.seed_ukraine  (из корня репозитория)
Сервис вызывает функцию run_seed автоматически при пустой базе.

Скрипт идемпотентен: источники, уже имеющиеся в базе
(совпадают title + source_url), пропускаются.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SEED_PATH = Path(__file__).resolve().parent / "seed" / "ukraine_core.json"


def load_seed() -> List[Dict[str, Any]]:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    return payload.get("sources", [])


def run_seed() -> Dict[str, int]:
    from app.db import connect  # локальный импорт: избегаем цикла на старте

    inserted = 0
    skipped = 0

    with connect() as connection:
        for item in load_seed():
            existing = connection.execute(
                "SELECT 1 FROM legal_sources WHERE title = ? AND source_url = ?",
                (item["title"], item["source_url"]),
            ).fetchone()
            if existing:
                skipped += 1
                continue

            connection.execute(
                """
                INSERT INTO legal_sources (
                    title, source_type, jurisdiction, country_code, article,
                    text, source_url, language, effective_from, effective_to,
                    verified, checked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["title"],
                    item["source_type"],
                    item["jurisdiction"],
                    item.get("country_code"),
                    item.get("article"),
                    item["text"],
                    item["source_url"],
                    item.get("language", "uk"),
                    item.get("effective_from"),
                    item.get("effective_to"),
                    int(item.get("verified", 0)),
                    item.get("checked_at"),
                ),
            )
            inserted += 1

    return {"inserted": inserted, "skipped": skipped}


if __name__ == "__main__":
    result = run_seed()
    print(
        "PLDA seed: вставлено {inserted}, пропущено (уже есть) {skipped}".format(
            **result
        )
    )
