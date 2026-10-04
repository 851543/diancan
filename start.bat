@echo off
setlocal
cd /d "%~dp0"

set "ROOT=%~dp0"
set "PY=python"
if exist "%ROOT%.venv\Scripts\python.exe" set "PY=%ROOT%.venv\Scripts\python.exe"
if exist "%ROOT%backend\.venv\Scripts\python.exe" set "PY=%ROOT%backend\.venv\Scripts\python.exe"

cd /d "%ROOT%backend"
start "diancan-api" cmd /k "%PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

cd /d "%ROOT%admin"
start "diancan-admin" cmd /k "npm run dev"

cd /d "%ROOT%app"
start "diancan-h5" cmd /k "npm run dev:h5"

echo Started three windows: API http://127.0.0.1:8000 / admin http://127.0.0.1:5173 / H5
echo Close those windows to stop. MySQL 3306 and Redis 6379 must already be running.
endlocal
