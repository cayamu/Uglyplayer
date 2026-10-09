@echo off
title Music Player - DEBUG
cd /d "%~dp0"

python main.py

echo.
echo ============================================
echo Если упало — вот ошибка выше.
echo ============================================
pause