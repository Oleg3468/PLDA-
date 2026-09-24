import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("/storage/sdcard/PLDA/database/plda.db")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def add_source(
    title: str,
    source_type: str,
    jurisdiction: str,
    text: str,
    country_code: Optional[str] = None,
    article: Optional[str] = None,
    source_url: Optional[str] = None,
    language: str = "en",
    effective_from: Optional[str] = None,
    effective_to: Optional[str] = None,
    verified: int = 0,
):
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO legal_sources (
                title,
                source_type,
                jurisdiction,
                country_code,
                article,
                text,
                source_url,
                language,
                effective_from,
                effective_to,
                verified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                source_type,
                jurisdiction,
                country_code,
                article,
                text,
                source_url,
                language,
                effective_from,
                effective_to,
                verified,
            ),
        )
        db.commit()
        return cursor.lastrowid


def get_source(source_id: int):
    with connect() as db:
        return db.execute(
            "SELECT * FROM legal_sources WHERE id = ?",
            (source_id,),
        ).fetchone()


def search_sources(
    query: str,
    jurisdiction: Optional[str] = None,
    country_code: Optional[str] = None,
):
    sql = """
        SELECT *
        FROM legal_sources
        WHERE (
            title LIKE ?
            OR article LIKE ?
            OR text LIKE ?
        )
    """

    pattern = f"%{query}%"
    params = [pattern, pattern, pattern]

    if jurisdiction:
        sql += " AND jurisdiction = ?"
        params.append(jurisdiction)

    if country_code:
        sql += " AND country_code = ?"
        params.append(country_code)

    sql += " ORDER BY verified DESC, id DESC"

    with connect() as db:
        return db.execute(sql, params).fetchall()


def count_sources():
    with connect() as db:
        row = db.execute(
            "SELECT COUNT(*) AS total FROM legal_sources"
        ).fetchone()
        return row["total"]
