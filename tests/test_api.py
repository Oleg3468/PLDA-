import os
import tempfile
from pathlib import Path

# База сервиса изолируется до импорта приложения.
_TEST_DIR = tempfile.TemporaryDirectory()
os.environ["PLDA_DB_PATH"] = str(Path(_TEST_DIR.name) / "api_test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.api.main import app  # noqa: E402
from app.db import init_db, seed_if_empty  # noqa: E402

# Инициализация и наполнение тестовой базы (аналогично lifespan сервиса).
init_db()
seed_if_empty()

client = TestClient(app)


class TestHealth:
    def test_health(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["mode"] == "offline"
        assert payload["llm_configured"] is False
        assert payload["sources"]["total"] >= 20

    def test_index_served(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "PLDA" in response.text


class TestChat:
    def test_offline_chat_answer(self):
        response = client.post(
            "/api/chat",
            json={"message": "Получил штраф от полиции, хочу обжаловать постановление"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["mode"] == "offline"
        assert "### 1. Краткий ответ" in payload["answer_md"]
        assert payload["sources"]
        assert "не юридическая консультация" in payload["answer_md"]

    def test_chat_anonymizes_sensitive_data(self):
        response = client.post(
            "/api/chat",
            json={
                "message": "Меня оштрафовали, пишите на ivan@example.com, дело 520/1356/24",
                "anonymize": True,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["anonymized"] is True
        assert payload["masked_count"] >= 2

    def test_chat_rejects_bad_jurisdiction(self):
        response = client.post("/api/chat", json={"message": "штраф", "jurisdiction": "XX"})
        assert response.status_code == 400
        assert "Unsupported jurisdiction" in response.text

    def test_chat_stores_history(self):
        response = client.post(
            "/api/chat",
            json={"message": "Как обжаловать штраф?", "session_id": "api-test"},
        )
        assert response.status_code == 200
        from app.db import fetch_all

        rows = fetch_all(
            "SELECT role FROM chat_messages WHERE session_id = 'api-test' ORDER BY id"
        )
        assert [row["role"] for row in rows] == ["user", "assistant"]


class TestAnalyze:
    def test_analyze_returns_plan(self):
        response = client.post(
            "/api/analyze",
            json={"request": "Меня остановила полиция без причины", "jurisdiction": "UA"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["jurisdiction"] == "UA"
        assert payload["research_tasks"]
        assert payload["sources"]


class TestSources:
    def test_sources_search(self):
        response = client.get("/api/sources", params={"q": "апелляция обжалование"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["results"]
        titles = " ".join(item["title"] for item in payload["results"])
        assert "Цивільний процесуальний" in titles

    def test_sources_empty_query_returns_catalog(self):
        response = client.get("/api/sources")
        assert response.status_code == 200
        assert len(response.json()["results"]) > 0


class TestMemoFlow:
    def test_memo_created_and_reviewed(self):
        # 1. Создание записки
        response = client.post(
            "/api/memo",
            json={
                "question": "Как обжаловать постановление о штрафе?",
                "jurisdiction": "UA",
                "facts": ["постановление вручено 2026-09-20"],
                "dates": ["2026-09-20 — вручение постановления"],
                "unknowns": ["дата составления протокола"],
            },
        )
        assert response.status_code == 200
        payload = response.json()
        document_id = payload["id"]
        assert payload["status"] == "pending_review"
        assert "Правовая исследовательская записка" in payload["markdown"]
        assert "не является юридической консультацией" in payload["markdown"].lower()
        assert "ожидает проверки" in payload["markdown"]

        # 2. Запись в очереди проверки
        queue = client.get("/api/documents", params={"status": "pending_review"})
        assert queue.status_code == 200
        assert any(doc["id"] == document_id for doc in queue.json()["documents"])

        # 3. Юрист редактирует и одобряет
        review = client.post(
            f"/api/documents/{document_id}/review",
            json={
                "action": "approve",
                "content_md": payload["markdown"] + "\n\nПроверено: тестовый юрист.",
                "reviewer_note": "проверено тестом",
            },
        )
        assert review.status_code == 200
        assert review.json()["status"] == "approved"

        # 4. Итоговый документ содержит правку и статус
        document = client.get(f"/api/documents/{document_id}")
        assert document.status_code == 200
        data = document.json()
        assert data["status"] == "approved"
        assert "Проверено: тестовый юрист." in data["content_md"]
        assert data["reviewer_note"] == "проверено тестом"

    def test_memo_anonymizes_facts(self):
        response = client.post(
            "/api/memo",
            json={
                "question": "Как обжаловать штраф?",
                "facts": ["моя почта user@example.com"],
                "anonymize": True,
            },
        )
        assert response.status_code == 200
        assert "user@example.com" not in response.json()["markdown"]

    def test_review_rejects_unknown_document(self):
        response = client.post(
            "/api/documents/999999/review", json={"action": "approve"}
        )
        assert response.status_code == 404
