"""PLDA web-сервис: HTTP API + интерфейс.

Запуск из корня репозитория:
    uvicorn app.api.main:app --host 0.0.0.0 --port 8000

Режимы работы:
  - оффлайн (по умолчанию): детерминированные ответы по правилам PLDA
    без внешних вызовов;
  - LLM: если задана переменная окружения PLDA_LLM_API_KEY
    (OpenAI-совместимый API, см. app/services/llm.py).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.core import rag
from app.core.case_analyzer import analyze_case
from app.core.jurisdiction import JURISDICTIONS, normalize_jurisdiction_code
from app.db import db_path, execute, fetch_all, fetch_one, init_db, seed_if_empty
from app.services import anonymizer, llm, memo as memo_service, offline_answer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
PROMPT_FOR_ANY_AI = PROJECT_ROOT / "docs" / "PROMPT_FOR_ANY_AI.md"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seeding = seed_if_empty()
    app.state.seed_info = seeding
    yield


app = FastAPI(
    title="PLDA — правовой исследовательский сервис",
    version="0.2.0",
    description=(
        "Структурированное правовое исследование по правилам базы знаний PLDA. "
        "Не является юридической консультацией."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Модели запросов
# --------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=8000)
    jurisdiction: str = "UA"
    anonymize: bool = True
    session_id: str = Field(default="default", max_length=64)
    history: List[Dict[str, str]] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    request: str = Field(min_length=3, max_length=8000)
    jurisdiction: str = "UA"
    facts: List[str] = Field(default_factory=list)


class MemoRequest(BaseModel):
    question: str = Field(min_length=5, max_length=8000)
    jurisdiction: str = "UA"
    anonymize: bool = True
    facts: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    content_md: Optional[str] = Field(default=None, max_length=100000)
    reviewer_note: Optional[str] = Field(default=None, max_length=4000)


# --------------------------------------------------------------------------
# Вспомогательные функции
# --------------------------------------------------------------------------


def _checked_jurisdiction(value: str) -> str:
    try:
        return normalize_jurisdiction_code(value)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _sources_block(sources: List[Dict[str, Any]]) -> str:
    if not sources:
        return "Локальная база источников пуста — используй официальную картотеку юрисдикции."
    lines = []
    for source in sources:
        status = (
            f"проверено {source['checked_at']}"
            if source.get("verified") and source.get("checked_at")
            else "проверено" if source.get("verified") else "ТРЕБУЕТ ПРОВЕРКИ"
        )
        period = source.get("effective_from") or "—"
        if source.get("effective_to"):
            period += f" — {source['effective_to']} (утратил силу)"
        lines.append(
            f"- {source.get('title')} ({source.get('source_type')}, "
            f"{source.get('jurisdiction')}); статус: {status}; "
            f"действие: {period}; {source.get('source_url')}"
        )
    return "\n".join(lines)


def _system_prompt(sources: List[Dict[str, Any]], jurisdiction: str) -> str:
    base_rules = PROMPT_FOR_ANY_AI.read_text(encoding="utf-8")
    country = JURISDICTIONS[jurisdiction].country
    return (
        f"{base_rules}\n\n"
        "---\n"
        f"Дополнительный контекст сессии: юрисдикция по умолчанию — {country} "
        f"({jurisdiction}).\n"
        "Ниже — источники из локальной проверяемой базы PLDA. Используй их как "
        "стартовые указатели; не описывай их содержание как прочитанное, если "
        "не можешь открыть ссылку. Отмечай статус проверки каждого источника.\n\n"
        f"Источники:\n{_sources_block(sources)}\n\n"
        "Отвечай на языке пользователя."
    )


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------


@app.get("/api/health")
def health() -> Dict[str, Any]:
    settings = llm.llm_settings()
    return {
        "status": "ok",
        "service": "PLDA web-сервис",
        "version": app.version,
        "mode": "llm" if settings["configured"] else "offline",
        "llm_configured": settings["configured"],
        "llm_model": settings["model"] if settings["configured"] else None,
        "jurisdictions": sorted(JURISDICTIONS),
        "sources": rag.get_stats(),
        "database": db_path().name,
    }


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> Dict[str, Any]:
    jurisdiction = _checked_jurisdiction(request.jurisdiction)
    case = analyze_case(
        request.request, jurisdiction, facts=[f for f in request.facts if f.strip()]
    )
    sources = rag.search_sources(
        request.request, jurisdiction=jurisdiction, limit=8, include_fallback=True
    )
    return {
        "jurisdiction": case.jurisdiction,
        "legal_goal": case.legal_goal,
        "category": case.category,
        "facts": case.facts,
        "unknown_facts": case.unknown_facts,
        "research_tasks": case.research_tasks,
        "police_questions": case.police_questions,
        "opportunity_checks": case.opportunity_checks,
        "sources": sources,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    jurisdiction = _checked_jurisdiction(request.jurisdiction)
    user_text = request.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Пустой запрос")

    masked_text, masked_count = (
        anonymizer.anonymize(user_text) if request.anonymize else (user_text, 0)
    )

    sources = rag.search_sources(
        user_text, jurisdiction=jurisdiction, limit=8, include_fallback=True
    )

    mode = "offline"
    llm_error: Optional[str] = None
    settings = llm.llm_settings()

    if settings["configured"]:
        try:
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": _system_prompt(sources, jurisdiction)}
            ]
            for item in request.history[-8:]:
                role = item.get("role")
                content = item.get("content")
                if role in {"user", "assistant"} and content:
                    messages.append(
                        {"role": role, "content": str(content)[:8000]}
                    )
            messages.append({"role": "user", "content": masked_text})

            answer_md = await llm.chat_completion(messages)
            mode = "llm"
        except Exception as error:  # noqa: BLE001 — показываем причину отката
            llm_error = f"{type(error).__name__}: {error}"[:300]
            answer_md = offline_answer.build_offline_answer(
                masked_text, jurisdiction
            )["answer_md"]
    else:
        answer_md = offline_answer.build_offline_answer(masked_text, jurisdiction)[
            "answer_md"
        ]

    execute(
        "INSERT INTO chat_messages (session_id, role, content, mode, anonymized)"
        " VALUES (?, 'user', ?, ?, ?)",
        (request.session_id, masked_text, mode, int(masked_count > 0)),
    )
    execute(
        "INSERT INTO chat_messages (session_id, role, content, mode, anonymized)"
        " VALUES (?, 'assistant', ?, ?, 0)",
        (request.session_id, answer_md, mode),
    )

    return {
        "answer_md": answer_md,
        "mode": mode,
        "jurisdiction": jurisdiction,
        "sources": sources,
        "anonymized": masked_count > 0,
        "masked_count": masked_count,
        "llm_configured": settings["configured"],
        "llm_error": llm_error,
    }


@app.get("/api/sources")
def sources(
    q: str = Query(default="", max_length=300),
    jurisdiction: Optional[str] = None,
    limit: int = Query(default=12, ge=1, le=50),
) -> Dict[str, Any]:
    checked = _checked_jurisdiction(jurisdiction) if jurisdiction else None
    if q.strip():
        results = rag.search_sources(q, jurisdiction=checked, limit=limit)
    else:
        results = rag.search_sources(
            "", jurisdiction=checked, limit=limit, include_fallback=True
        )
    return {"query": q, "jurisdiction": checked, "results": results}


@app.post("/api/memo")
def create_memo(request: MemoRequest) -> Dict[str, Any]:
    jurisdiction = _checked_jurisdiction(request.jurisdiction)

    question = request.question.strip()
    masked_question, masked_count = (
        anonymizer.anonymize(question) if request.anonymize else (question, 0)
    )

    def clean(items: List[str]) -> List[str]:
        return [item.strip() for item in items if item and item.strip()]

    facts = [anonymizer.anonymize(f)[0] for f in clean(request.facts)] if request.anonymize else clean(request.facts)
    dates = clean(request.dates)
    unknowns = clean(request.unknowns)
    next_steps = clean(request.next_steps)

    result = memo_service.build_memo(
        question=masked_question,
        jurisdiction=jurisdiction,
        facts=facts,
        dates=dates,
        unknowns=unknowns,
        next_steps=next_steps,
    )

    title = masked_question[:80] + ("…" if len(masked_question) > 80 else "")
    document_id = memo_service.save_memo(
        markdown=result["markdown"],
        case_id=result["case_id"],
        title=title,
        anonymized=masked_count > 0 or bool(request.anonymize),
    )

    return {
        "id": document_id,
        "case_id": result["case_id"],
        "markdown": result["markdown"],
        "sources": result["sources"],
        "status": "pending_review",
        "anonymized": bool(request.anonymize),
    }


@app.get("/api/documents")
def list_documents(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> Dict[str, Any]:
    if status and status not in {"pending_review", "approved", "rejected"}:
        raise HTTPException(
            status_code=400,
            detail="status должен быть pending_review, approved или rejected",
        )
    if status:
        rows = fetch_all(
            "SELECT id, case_id, doc_type, title, status, reviewer_note,"
            " anonymized, created_at, reviewed_at FROM documents"
            " WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        )
    else:
        rows = fetch_all(
            "SELECT id, case_id, doc_type, title, status, reviewer_note,"
            " anonymized, created_at, reviewed_at FROM documents"
            " ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
    return {"documents": rows}


@app.get("/api/documents/{document_id}")
def get_document(document_id: int) -> Dict[str, Any]:
    row = fetch_one(
        "SELECT id, case_id, doc_type, title, content_md, status, reviewer_note,"
        " anonymized, created_at, reviewed_at FROM documents WHERE id = ?",
        (document_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return row


@app.post("/api/documents/{document_id}/review")
def review_document(document_id: int, request: ReviewRequest) -> Dict[str, Any]:
    existing = fetch_one("SELECT id, status FROM documents WHERE id = ?", (document_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Документ не найден")

    new_status = "approved" if request.action == "approve" else "rejected"

    if request.content_md is not None and request.content_md.strip():
        execute(
            "UPDATE documents SET content_md = ?, status = ?, reviewer_note = ?,"
            " reviewed_at = ? WHERE id = ?",
            (
                request.content_md,
                new_status,
                request.reviewer_note,
                _now(),
                document_id,
            ),
        )
    else:
        execute(
            "UPDATE documents SET status = ?, reviewer_note = ?, reviewed_at = ?"
            " WHERE id = ?",
            (new_status, request.reviewer_note, _now(), document_id),
        )

    return {
        "id": document_id,
        "status": new_status,
        "reviewed_at": _now(),
        "note": request.reviewer_note,
    }


# --------------------------------------------------------------------------
# Статика и интерфейс
# --------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
