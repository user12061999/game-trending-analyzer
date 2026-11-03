@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title Game Market Trending Analyzer

echo ========================================================
echo   GAME MARKET TRENDING ANALYZER (PC ^& MOBILE)
echo ========================================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating Python virtual environment...
    python -m venv .venv
    echo [2/3] Installing dependencies...
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

echo [3/3] Starting Web Server at http://127.0.0.1:8000 ...
.\.venv\Scripts\python.exe run.py
pause
