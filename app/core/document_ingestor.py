from pathlib import Path
from datetime import datetime, timezone
import hashlib


def file_hash(path) -> str:
    path = Path(path)

    sha256 = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def ingest(path: str) -> dict:
    source = Path(path)

    if not source.exists():
        raise FileNotFoundError(path)

    digest = file_hash(source)

    stat = source.stat()

    return {
        "source_path": str(source),
        "filename": source.name,
        "size": stat.st_size,
        "sha256": digest,
        "ingested_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }
