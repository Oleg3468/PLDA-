import os
from pathlib import Path

PROJECT_ROOT = Path(
    os.environ.get("PLDA_ROOT") or Path.home() / "PLDA"
).expanduser().resolve()

DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
CASES_DIR = DATA_DIR / "cases"
DATABASE_DIR = PROJECT_ROOT / "database"
LOGS_DIR = PROJECT_ROOT / "logs"
DATABASE_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

APP_NAME = "Personal Legal Defense AI"
VERSION = "0.1.0"
