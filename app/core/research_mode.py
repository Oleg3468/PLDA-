from dataclasses import dataclass
from enum import Enum


class ResearchMode(str, Enum):
    AUTO = "auto"
    CONSULTATION = "consultation"
    CASE = "case"


@dataclass
class ResearchPolicy:
    mode: ResearchMode
    download_documents: bool
    save_to_sd: bool
    online_only: bool
    preserve_sources: bool


def consultation_policy() -> ResearchPolicy:
    return ResearchPolicy(
        mode=ResearchMode.CONSULTATION,
        download_documents=False,
        save_to_sd=False,
        online_only=True,
        preserve_sources=False,
    )


def case_policy() -> ResearchPolicy:
    return ResearchPolicy(
        mode=ResearchMode.CASE,
        download_documents=True,
        save_to_sd=True,
        online_only=False,
        preserve_sources=True,
    )


def auto_policy() -> ResearchPolicy:
    return ResearchPolicy(
        mode=ResearchMode.AUTO,
        download_documents=False,
        save_to_sd=False,
        online_only=True,
        preserve_sources=False,
    )


def get_policy(mode: str) -> ResearchPolicy:
    value = mode.lower().strip()

    if value == "consultation":
        return consultation_policy()

    if value == "case":
        return case_policy()

    return auto_policy()


def should_download(
    mode: str,
    user_confirmed: bool = False,
) -> bool:

    policy = get_policy(mode)

    if policy.mode == ResearchMode.CASE:
        return True

    if policy.mode == ResearchMode.CONSULTATION:
        return False

    return user_confirmed


def mode_description(mode: str) -> str:
    policy = get_policy(mode)

    if policy.mode == ResearchMode.CONSULTATION:
        return (
            "Онлайн-консультация: "
            "источники просматриваются онлайн "
            "без постоянного скачивания."
        )

    if policy.mode == ResearchMode.CASE:
        return (
            "Режим дела: важные документы "
            "скачиваются, хешируются и "
            "сохраняются на SD."
        )

    return (
        "Автоматический режим: "
        "скачивание выполняется только "
        "после подтверждения пользователя."
    )
