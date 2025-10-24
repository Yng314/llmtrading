# Quick Start Guide

快速开始指南 - 5分钟搭建你的LLM加密货币交易机器人

## 安装步骤

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

获取阿里云DashScope API密钥（Qwen3 Max）：
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录账号
3. 进入"API-KEY管理"页面
4. 创建新的API密钥

编辑 `.env` 文件，填入你的API密钥：
```
DASHSCOPE_API_KEY=sk-你的密钥
```

### 3. 测试组件

运行测试脚本确保一切正常：

```bash
python test_components.py
```

应该看到所有测试通过 ✓

### 4. 运行交易机器人

```bash
python main.py
```

## 运行效果

机器人启动后会：

1. **获取实时价格** - 从Binance API获取BTC、ETH等主流币种价格
2. **技术分析** - 计算RSI、MACD、布林带等技术指标
3. **LLM决策** - 每5分钟（或市场波动>2%时）请求Qwen3 Max分析市场
4. **执行交易** - 根据LLM建议开/平仓位（模拟交易，无真实资金风险）
5. **记录日志** - 所有交易、决策、P&L都记录在 `logs/` 目录

### 控制台输出示例

```
=== Trading Bot Started ===
Initial Capital: $1,000.00
Trading Pairs: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, ADAUSDT

--- Iteration 1 ---
Current Prices: BTCUSDT: $67,500, ETHUSDT: $3,450, ...

=== Requesting LLM Decision ===
=== LLM DECISION #1 ===
Analysis: Bitcoin shows strong uptrend with RSI at 65. 
          Ethereum consolidating near support...
Actions: 2 proposed

Opening LONG position: BTCUSDT $200.00 (Leverage: 2x)
- Reason: Strong uptrend with bullish MACD crossover

--- Iteration 5 ---
Current Prices: BTCUSDT: $68,200, ...

TRADING SUMMARY
════════════════════════════════════════
Initial Capital:    $1,000.00
Current Value:      $1,029.63
Total P&L:          +$29.63
ROI:                +2.96%
════════════════════════════════════════
```

## 停止机器人

按 `Ctrl+C` 优雅退出，机器人会：
- 平掉所有持仓
- 计算最终盈亏
- 生成完整交易报告

## 查看交易记录

所有日志保存在 `logs/` 目录：

```
logs/
├── trading_20241023_143022.log      # 总日志
├── trades_20241023_143022.csv       # 交易明细（Excel可打开）
├── stats_20241023_143022.json       # 统计数据
├── decisions_20241023_143022.json   # LLM决策记录
└── report_20241023_143022.txt       # 最终报告
```

## 参数调整

编辑 `config.py` 自定义配置：

```python
# 初始资金（美元）
INITIAL_CAPITAL = 1000

# 最大杠杆倍数
MAX_LEVERAGE = 10

# LLM决策间隔（秒）- 增加此值可节省token
DECISION_INTERVAL = 300  # 默认5分钟

# 交易币种 - 可自由增减
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

# 波动率阈值 - 价格变动超过此值时提前触发LLM
VOLATILITY_THRESHOLD = 0.02  # 2%
```

## Token优化策略

为了降低API成本，系统采用了以下优化：

### ✓ 定时触发（默认5分钟）
不是每个价格变动都调用LLM，而是按固定间隔

### ✓ 波动率触发
当价格变动超过2%时，提前触发决策（捕捉重要行情）

### ✓ 批量分析
一次调用分析所有币种，而不是每个币种单独调用

### ✓ 精简上下文
只发送关键技术指标给LLM，压缩输入token

**预估成本**：根据市场波动情况，每小时 $0.01-0.05

## 常见问题

### Q: 是真实交易吗？
A: **不是！** 这是完全模拟的交易，使用虚拟的$1000资金，无任何真实资金风险。

### Q: 为什么机器人不开仓？
A: LLM很保守，如果市场信号不明确，它可能选择观望。这是正常现象。

### Q: 如何提高交易频率？
A: 降低 `DECISION_INTERVAL` 的值，比如设为60秒。但注意这会增加API调用成本。

### Q: 支持哪些交易所？
A: 目前使用Binance的价格数据（公开API，无需账号）。要接入真实交易，需要集成交易所的交易API。

### Q: 可以添加更多技术指标吗？
A: 可以！编辑 `technical_analysis.py` 添加你需要的指标（如KDJ、BOLL、ATR等）。

### Q: LLM决策准确吗？
A: LLM基于技术分析做决策，但**不保证盈利**。加密货币市场波动大，任何策略都有风险。

### Q: VPN导致连接失败？
A: 如果使用VPN，可能干扰DashScope API连接。尝试关闭VPN或配置VPN绕过本地连接。

## 进阶使用

### 仅运行N次迭代（测试用）

编辑 `main.py` 最后一行：
```python
bot.run(iterations=20, sleep_seconds=30)  # 运行20次，每次间隔30秒
```

### 更换LLM模型

编辑 `config.py`：
```python
LLM_MODEL = 'qwen-plus'  # 使用更便宜的模型
# 或
LLM_MODEL = 'qwen-turbo'  # 最便宜，但效果可能不如qwen-max
```

### 添加止损/止盈规则

编辑 `llm_agent.py` 的系统提示词，添加更严格的风险管理规则。

## 安全提示

⚠️ **这是教育/研究项目**
- 用于学习LLM应用和量化交易
- 在考虑真实交易前，请充分测试
- 加密货币投资有风险，可能损失全部本金

⚠️ **API密钥安全**
- 不要将 `.env` 文件提交到Git仓库
- 不要在公开场合分享你的API密钥
- 定期轮换API密钥

## 技术架构

```
main.py                    # 主控制循环
├── crypto_api.py          # Binance价格数据
├── technical_analysis.py  # 技术指标计算
├── llm_agent.py          # Qwen3 Max决策
├── trading_simulator.py   # 交易模拟引擎
└── logger.py             # 日志记录
```

## 下一步

1. ✅ 运行几个小时，观察机器人的决策逻辑
2. ✅ 查看日志文件，分析盈亏原因
3. ✅ 调整参数，优化策略
4. ✅ 阅读 `USAGE.md` 了解更多高级功能

祝交易愉快！🚀

