"""Слой доступа к базе данных сервиса PLDA.

Путь к базе задаётся переменной окружения PLDA_DB_PATH;
по умолчанию — database/plda.db в корне репозитория.
База локальная и не попадает в Git (см. .gitignore).
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def db_path() -> Path:
    override = os.environ.get("PLDA_DB_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return PROJECT_ROOT / "database" / "plda.db"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _ensure_column(connection, "legal_sources", "checked_at", "TEXT")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _ensure_column(
    connection: sqlite3.Connection, table: str, column: str, ddl: str
) -> None:
    """Добавляет колонку, если таблица была создана старой версией схемы."""
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    with connect() as connection:
        row = connection.execute(query, params).fetchone()
        return dict(row) if row is not None else None


def execute(query: str, params: tuple = ()) -> int:
    """Выполняет запрос на запись и возвращает id последней вставленной строки."""
    with connect() as connection:
        cursor = connection.execute(query, params)
        return cursor.lastrowid


def init_db() -> Path:
    """Создаёт схему при необходимости и возвращает путь к базе."""
    with connect():
        pass
    return db_path()


def seed_if_empty() -> Dict[str, Any]:
    """Наполняет базу стартовым набором источников, если она пуста."""
    from database.seed_ukraine import run_seed

    row = fetch_one("SELECT COUNT(*) AS total FROM legal_sources")
    if row and row.get("total"):
        return {"seeded": False, "total": row["total"]}
    return run_seed()
