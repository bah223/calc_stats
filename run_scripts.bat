@echo off
title Scripts Launcher

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not found in PATH. Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo Checking pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip is not available. Please install pip for Python.
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

if exist "%~dp0run_scripts_menu.ps1" (
    echo Starting menu...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_scripts_menu.ps1"
) else (
    echo Error: Menu script not found: run_scripts_menu.ps1
    pause
)

if %ERRORLEVEL% NEQ 0 pause
REM --- Always pause at the end so user can copy output ---
echo.
echo Скрипт завершён. Для выхода нажмите любую клавишу...
pause >nul
