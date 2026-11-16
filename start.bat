@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv || goto :fail
)
if not exist ".venv\.ready" (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
    echo ready>".venv\.ready"
)
echo Open http://127.0.0.1:8514 when the server is ready.
".venv\Scripts\python.exe" run.py
if errorlevel 1 goto :fail
exit /b 0
:fail
echo Setup or startup failed. Check Python and the error above.
pause
exit /b 1
