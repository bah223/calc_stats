@echo off
REM Simple helper to install dependencies and run one of the project scripts.
REM Usage: double-click run_scripts.bat or run from cmd/powershell.

REM --- Check if required Python packages are already installed ---
python -c "import importlib,sys,subprocess,os; pkgs=['pandas','openpyxl']; sys.exit(any(importlib.util.find_spec(p) is None for p in pkgs))" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Installing/Updating Python dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r "%~dp0requirements.txt" || goto :end
)

:menu
echo.
echo Select script to run:
echo 1 - angelina_report.py
echo 2 - calc_stats.py
echo 3 - 12oo.py
echo.
set /p choice="Enter choice 1-3: "

if "%choice%"=="1" (
    echo Running angelina_report.py ...
    python "%~dp0angelina_report.py"
    goto :end
) else if "%choice%"=="2" (
    echo Running calc_stats.py ...
    python "%~dp0calc_stats.py"
    goto :end
) else if "%choice%"=="3" (
    echo Running 12oo.py ...
    python "%~dp012oo.py"
    goto :end
) else (
    echo Invalid choice: %choice%
    echo.
    goto :menu
)

:end
pause
