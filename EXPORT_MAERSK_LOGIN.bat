@echo off
title Export Maersk login
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe backend\scripts\export_maersk_login.py
) else if exist backend\.venv\Scripts\python.exe (
    backend\.venv\Scripts\python.exe backend\scripts\export_maersk_login.py
) else (
    python backend\scripts\export_maersk_login.py
)
pause
