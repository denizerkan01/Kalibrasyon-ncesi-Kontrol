@echo off
setlocal
cd /d "%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PY%" (
  echo Python 3.14 was not found at "%PY%".
  pause
  exit /b 1
)
start "Kalib Web Backend" /min "%PY%" "%~dp0web_backend.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"
endlocal
