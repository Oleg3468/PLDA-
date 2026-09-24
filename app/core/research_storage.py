from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.research_mode import (
    ResearchMode,
    get_policy,
    should_download,
)
from app.core.document_ingestor import (
    ingest,
    file_hash,
)


ROOT = Path("/storage/sdcard/PLDA")
CASE_DIR = ROOT / "data" / "cases"


@dataclass
class ResearchAction:
    mode: str
    action: str
    saved: bool
    path: Optional[str] = None
    reason: str = ""


def prepare_case(case_id: str) -> Path:
    safe_id = "".join(
        char for char in case_id
        if char.isalnum() or char in "-_"
    )

    if not safe_id:
        raise ValueError("Invalid case ID")

    path = CASE_DIR / safe_id
    path.mkdir(parents=True, exist_ok=True)

    return path


def process_document(
    source_path: str,
    mode: str = "auto",
    case_id: Optional[str] = None,
    user_confirmed: bool = False,
) -> ResearchAction:

    policy = get_policy(mode)

    if not should_download(
        mode,
        user_confirmed=user_confirmed,
    ):
        return ResearchAction(
            mode=policy.mode.value,
            action="online_only",
            saved=False,
            reason=(
                "Документ не сохраняется. "
                "Используется только онлайн-просмотр."
            ),
        )

    if not case_id:
        raise ValueError(
            "case_id is required when saving a case."
        )

    case_path = prepare_case(case_id)

    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(source_path)

    destination = case_path / source.name

    if destination.exists():
        source_digest = file_hash(source)
        stored_digest = file_hash(destination)

        if source_digest == stored_digest:
            return ResearchAction(
                mode=policy.mode.value,
                action="already_saved",
                saved=True,
                path=str(destination),
                reason=(
                    "Документ уже сохранён "
                    "и имеет тот же SHA-256."
                ),
            )

    destination.write_bytes(
        source.read_bytes()
    )

    metadata = ingest(str(destination))

    return ResearchAction(
        mode=policy.mode.value,
        action="saved_and_ingested",
        saved=True,
        path=metadata["source_path"],
        reason=(
            "Документ сохранён на SD, "
            "извлечён и добавлен в локальное хранилище."
        ),
    )


def storage_policy(mode: str) -> dict:
    policy = get_policy(mode)

    return {
        "mode": policy.mode.value,
        "download": policy.download_documents,
        "save_to_sd": policy.save_to_sd,
        "online_only": policy.online_only,
        "preserve_sources": policy.preserve_sources,
    }
