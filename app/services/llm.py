"""Подключение внешней LLM (OpenAI-совместимый API).

Настраивается переменными окружения:
  PLDA_LLM_API_KEY  — ключ API (обязателен для включения LLM-режима);
  PLDA_LLM_BASE_URL — базовый URL (по умолчанию https://api.openai.com/v1);
  PLDA_LLM_MODEL    — модель (по умолчанию gpt-4o-mini).

Ключи никогда не записываются в базу и в Git. Если ключ не задан,
сервис честно работает в оффлайн-режиме (см. offline_answer.py).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def llm_settings() -> Dict[str, Any]:
    api_key = (os.environ.get("PLDA_LLM_API_KEY") or "").strip()
    base_url = (os.environ.get("PLDA_LLM_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("PLDA_LLM_MODEL") or DEFAULT_MODEL
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "configured": bool(api_key),
    }


async def chat_completion(
    messages: List[Dict[str, str]], timeout: float = 90.0
) -> str:
    """Отправляет запрос в LLM и возвращает текст ответа.

    Бросает исключение при любой ошибке — вызывающий код решает,
    показывать ли её пользователю и переходить ли в оффлайн-режим.
    """
    settings = llm_settings()
    if not settings["configured"]:
        raise RuntimeError("LLM API key is not configured")

    payload = {
        "model": settings["model"],
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {settings['api_key']}"}

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{settings['base_url']}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]
