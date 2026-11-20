@echo off
rem ============================================================
rem  PLDA web-service launcher (Windows)
rem  Just double-click this file. Documentation: docs\service.md
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo === PLDA web-service launcher ===

rem --- 1. Checking Python ---
set PY=py
where py >nul 2>nul
if errorlevel 1 (
    set PY=python
    where python >nul 2>nul
    if errorlevel 1 (
        echo [!] Python not found.
        echo [!] Install it from https://www.python.org/downloads/
        echo [!] IMPORTANT: during installation, check the "Add Python to PATH" checkbox
        pause
        exit /b 1
    )
)

rem --- 2. Creating a virtual environment (only the first time) ---
if not exist .venv (
    echo [*] Creating a virtual environment...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [!] Failed to create the environment.
        pause
        exit /b 1
    )
)

rem --- 3. Checking dependencies ---
echo [*] Checking dependencies (internet needed the first time)...
.venv\Scripts\python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo [!] Failed to install dependencies.
    pause
    exit /b 1
)

rem --- 4. Launching ---
echo.
echo [*] The service will open at http://localhost:8000
echo [*] To STOP the service, press Ctrl+C in this window
echo.
rem Open the browser 3 seconds after the server starts
start "" cmd /c "timeout /t 3 >nul & start http://localhost:8000"
.venv\Scripts\python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000

echo.
echo [*] Service stopped.
pause
