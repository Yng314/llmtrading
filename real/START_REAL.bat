@echo off
chcp 65001 > nul
cd ..
echo ========================================
echo   Real Trading Bot - 真实交易版本
echo ========================================
echo.
echo ⚠️  使用前必读：
echo.
echo 1. 确保已在 .env 中设置 BINANCE_API_KEY
echo 2. BINANCE_TESTNET=true  使用测试网（推荐）
echo 3. BINANCE_TESTNET=false 使用实盘（谨慎！）
echo.
echo 测试网注册: https://testnet.binancefuture.com
echo.
echo 按 Ctrl+C 退出
echo ========================================
echo.

call conda activate d:\workspace\llmtrading\.conda
if errorlevel 1 (
    echo Error: 无法激活conda环境
    pause
    exit /b 1
)

python real\main_real.py

echo.
echo ========================================
echo 机器人已停止
echo ========================================
pause

