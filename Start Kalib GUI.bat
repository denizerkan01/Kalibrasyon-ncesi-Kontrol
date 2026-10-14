@echo off
setlocal
fltmc >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
cd /d "%~dp0"
set "PYW=%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe"
if not exist "%PYW%" (
  echo Python 3.14 windowless interpreter was not found at "%PYW%".
  pause
  exit /b 1
)
start "" "%PYW%" "%~dp0web_backend.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"
endlocal
