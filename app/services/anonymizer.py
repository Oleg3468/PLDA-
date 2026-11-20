"""Обезличивание текста перед отправкой во внешнюю LLM.

Удаляет адреса e-mail, номера телефонов, номера дел, номера карт
и IP-адреса. Полное обезличивание имён не гарантируется: не отправляйте
чувствительные данные, если политика конфиденциальности выбранной
LLM-платформы не проверена (см. README и docs/service.md).
"""

from __future__ import annotations

import re
from typing import Tuple

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,15}\d)(?!\d)")
CASE_NUMBER_RE = re.compile(
    r"(?<![\w])№?\s?\d{2,6}\s?/\s?\d{2,6}\s?/\s?\d{2,4}(?![\w])"
)
CARD_RE = re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

_RULES = (
    ("email", EMAIL_RE),
    ("case_number", CASE_NUMBER_RE),
    ("card", CARD_RE),
    ("ip", IP_RE),
    ("phone", PHONE_RE),
)


def anonymize(text: str) -> Tuple[str, int]:
    """Возвращает (обезличенный текст, число замен)."""
    if not text:
        return text, 0

    result = text
    replaced = 0
    for label, pattern in _RULES:
        result, count = pattern.subn(f"[ДАННЫЕ УДАЛЕНЫ:{label}]", result)
        replaced += count

    return result, replaced
