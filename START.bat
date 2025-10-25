@echo off
chcp 65001 > nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         LLM Crypto Trading Bot - 启动菜单                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 请选择运行模式：
echo.
echo   1. 虚拟交易（模拟器）- 推荐新手
echo      ├ 无风险，使用虚拟资金
echo      ├ 支持数据持久化
echo      └ 快速测试策略
echo.
echo   2. 真实交易（测试网/实盘）
echo      ├ 连接Binance账户
echo      ├ 测试网虚拟资金（推荐）
echo      └ 实盘真实交易（谨慎！）
echo.
echo   3. 查看项目结构说明
echo.
echo   0. 退出
echo.
echo ════════════════════════════════════════════════════════════
echo.

set /p choice="请输入选项 (0-3): "

if "%choice%"=="1" goto virtual
if "%choice%"=="2" goto real
if "%choice%"=="3" goto docs
if "%choice%"=="0" goto end
echo 无效选项，请重新运行
pause
goto end

:virtual
echo.
echo 启动虚拟交易（模拟器）...
echo.
cd unreal
call START_ADVANCED.bat
goto end

:real
echo.
echo 启动真实交易...
echo.
cd real
call START_REAL.bat
goto end

:docs
echo.
echo 打开项目结构说明...
start PROJECT_STRUCTURE.md
pause
goto end

:end

