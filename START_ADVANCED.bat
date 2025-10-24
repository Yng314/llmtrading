@echo off
echo ========================================
echo Starting Advanced LLM Trading Bot
echo ========================================
echo.

:: Activate conda environment
call conda activate d:\workspace\llmtrading\.conda

:: Check if --restart flag is provided
if "%1"=="--restart" (
    echo Starting in RESTART mode (clearing saved data)...
    echo.
    python main_advanced.py --restart
) else (
    echo Starting in RESUME mode (loading saved data if available)...
    echo.
    echo To start fresh, use: START_ADVANCED.bat --restart
    echo.
    python main_advanced.py
)

pause
