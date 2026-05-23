@echo off
REM ---------- Bloated launcher ----------
REM Launches the app, relaunching elevated if the user accepts UAC.

setlocal
cd /d "%~dp0"

REM Detect elevation
net session >nul 2>&1
if %errorLevel% == 0 (
    python main.py
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~dp0run.bat' -Verb RunAs"
)

endlocal
