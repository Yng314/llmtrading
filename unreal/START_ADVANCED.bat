@echo off
chcp 65001 > nul
cd ..
echo ========================================
echo   Advanced LLM Crypto Trading Bot
echo   With Model Chat Interface (模拟器版本)
echo ========================================
echo.
echo Features:
echo   - Detailed market data (time series)
echo   - Structured LLM output (Summary + CoT + Actions)
echo   - Model Chat panel (real-time LLM decisions)
echo.
echo Web Dashboard Layout:
echo   Left   : Stats and Charts
echo   Middle : Model Chat (QWEN3 MAX)
echo   Right  : Positions and Trades
echo.
echo Dashboard URL: http://127.0.0.1:5000
echo.
echo Press Ctrl+C ONCE to stop gracefully
echo ========================================
echo.

call conda activate d:\workspace\llmtrading\.conda
if errorlevel 1 (
    echo Error: Could not activate conda environment
    pause
    exit /b 1
)

python unreal\main_advanced.py %*

echo.
echo ========================================
echo Bot stopped. Check logs/ folder.
echo ========================================
pause

