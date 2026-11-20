#!/usr/bin/env bash
# ============================================================
#  PLDA web-service launcher (Linux / macOS)
#  Run: ./start.sh   Documentation: docs/service.md
# ============================================================
set -e
cd "$(dirname "$0")"

echo "=== PLDA web-service launcher ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "[!] Python 3 not found. Install it first (python3 --version)."
    exit 1
fi

# Creating a virtual environment (only the first time)
if [ ! -d .venv ]; then
    echo "[*] Creating a virtual environment..."
    python3 -m venv .venv
fi

echo "[*] Checking dependencies (internet needed the first time)..."
.venv/bin/pip install --disable-pip-version-check -q -r requirements.txt

echo
echo "[*] The service: http://localhost:8000"
echo "[*] To STOP the service, press Ctrl+C"
echo
exec .venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8000
