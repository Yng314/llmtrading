@echo off
chcp 65001 > nul
echo ========================================
echo   LLM Crypto Trading - Web Dashboard
echo ========================================
echo.
echo Starting trading bot with web interface...
echo.
echo Web Dashboard will be available at:
echo   http://127.0.0.1:5000
echo.
echo Press Ctrl+C ONCE to stop gracefully
echo (Wait for positions to close)
echo.
echo ========================================
echo.

call conda activate d:\workspace\llmtrading\.conda
if errorlevel 1 (
    echo Error: Could not activate conda environment
    echo Please run manually:
    echo   conda activate d:\workspace\llmtrading\.conda
    echo   python main_with_web.py
    pause
    exit /b 1
)

python main_with_web.py

echo.
echo ========================================
echo Bot stopped. Check logs/ folder for details.
echo ========================================
pause
