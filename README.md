# 🚀 LLM Crypto Trading Bot

基于大语言模型（LLM）的加密货币自动交易机器人，支持虚拟交易和真实交易两种模式。

---

## 📋 快速开始

### 1. 安装依赖

```bash
conda create -n llmtrading python=3.10
conda activate llmtrading
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# LLM API（必需）
DASHSCOPE_API_KEY=sk-your-api-key

# Trading Config
INITIAL_CAPITAL=1000
MAX_LEVERAGE=20
DECISION_INTERVAL=300

# Binance API（仅真实交易需要）
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true  # true=测试网, false=实盘
```

### 3. 启动程序

```bash
# 使用启动菜单（推荐）
START.bat

# 或直接运行
unreal\START_ADVANCED.bat    # 虚拟交易（模拟器）
real\START_REAL.bat          # 真实交易（测试网/实盘）
```

### 4. 打开Web界面

浏览器访问：http://127.0.0.1:5000

---

## 📁 项目结构

```
llmtrading/
├── unreal/                    # 虚拟交易（模拟器）✅
│   ├── main_advanced.py       # 主程序
│   ├── trading_simulator.py   # 交易模拟器
│   ├── data_persistence.py    # 数据持久化
│   └── START_ADVANCED.bat     # 启动脚本
│
├── real/                      # 真实交易 ⚠️
│   ├── main_real.py           # 主程序
│   ├── binance_real_trader.py # Binance API封装
│   ├── trading_executor_real.py # 真实交易执行器
│   └── START_REAL.bat         # 启动脚本
│
├── 共享模块/
│   ├── config.py              # 配置
│   ├── crypto_api.py          # 价格API
│   ├── technical_analysis.py  # 技术分析
│   ├── llm_agent_advanced.py  # LLM代理
│   ├── logger.py              # 日志
│   └── web_server.py          # Web服务器
│
├── templates/                 # Web模板
├── logs/                      # 日志文件
├── START.bat                  # 启动菜单
└── README.md                  # 本文档
```

---

## 🎯 两种模式

### 虚拟交易（unreal/）

**特点：**
- ✅ 无风险，使用虚拟资金
- ✅ 支持数据持久化
- ✅ 可以快速重启测试
- ✅ 只需要LLM API密钥

**启动：**
```bash
unreal\START_ADVANCED.bat
# 或
python unreal\main_advanced.py
python unreal\main_advanced.py --restart  # 清空数据重新开始
```

**适用场景：** 开发测试、策略验证、学习演示

---

### 真实交易（real/）

**特点：**
- ⚠️  连接真实Binance账户
- ⚠️  发送真实订单到交易所
- ✅ 测试网资金是虚拟的（推荐先用测试网）
- ⚠️  实盘有真实资金风险

**配置：**

1. 获取API密钥：
   - 测试网：https://testnet.binancefuture.com （推荐）
   - 实盘：https://www.binance.com （谨慎）

2. 在 `.env` 中配置：
```env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true  # 先用测试网！
```

3. 启动：
```bash
real\START_REAL.bat
# 或
python real\main_real.py
```

**适用场景：** 测试网验证、实盘交易（谨慎！）

---

## ✨ 主要功能

- 🤖 **LLM决策** - 基于Qwen3 Max分析市场
- 📊 **技术分析** - RSI, MACD, Bollinger Bands等
- 💰 **杠杆交易** - 支持1-20x杠杆
- 📈 **做多做空** - 双向交易
- 🌐 **Web界面** - 实时图表和LLM决策展示
- 🎯 **智能唤醒** - 根据市场波动和持仓风险自动触发决策

---

## 🚦 使用流程

### 新手推荐

```
1. 虚拟交易（unreal/）
   └ 测试几天，验证策略
   
2. 真实交易测试网（real/ + testnet）
   └ 运行1-2周，观察效果
   
3. 实盘（谨慎！）
   └ 确认盈利后，从小额开始（$50-100）
```

---

## ⚙️ 配置说明

### config.py

```python
# 交易对
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

# 交易参数
INITIAL_CAPITAL = 1000        # 初始资金
MAX_LEVERAGE = 20             # 最大杠杆
DECISION_INTERVAL = 300       # LLM决策间隔（秒）

# 唤醒阈值
VOLATILITY_THRESHOLD = 0.02   # 2% 市场波动触发
EMERGENCY_THRESHOLD = 0.05    # 5% 紧急波动触发
POSITION_RISK_THRESHOLD = 0.02 # 2% 持仓风险触发
```

---

## 🌐 Web界面

访问：http://127.0.0.1:5000

**布局：**
- **左侧** - 统计和图表（账户价值、价格变化）
- **中间** - LLM决策历史（思考过程、具体动作）
- **右侧** - 持仓和交易记录

---

## 📝 日志

程序运行时在 `logs/` 目录生成：
- `trading_YYYYMMDD_HHMMSS.log` - 详细日志
- `stats_YYYYMMDD_HHMMSS.json` - 统计数据
- `trades_YYYYMMDD_HHMMSS.csv` - 交易记录

---

## ⚠️ 重要提醒

### 虚拟交易
- ✅ 完全无风险
- ✅ 适合测试和学习

### 真实交易 - 测试网
- ✅ 虚拟资金，无风险
- ✅ 完整功能测试
- ✅ **强烈推荐先用这个！**

### 真实交易 - 实盘
- 🔴 **真实资金，高风险！**
- 🔴 **可能亏损全部资金！**
- 🔴 **必须先在测试网测试至少2周！**
- 🔴 **初期只投入$50-100！**

---

## 🛠️ 技术栈

- Python 3.10+
- LLM: 通义千问（Qwen3 Max）
- Exchange: Binance Futures
- Web: Flask + Chart.js
- Analysis: pandas, numpy, ta

---

## ⚖️ 免责声明

本项目仅供学习和研究使用。

- ❌ 不构成投资建议
- ❌ 不保证盈利
- ❌ 作者不对任何损失负责
- ✅ 使用者需自行承担所有风险
- ✅ 加密货币交易风险极高
- ✅ 请谨慎使用，量力而行

**加密货币交易有风险，投资需谨慎！**

---

## 🎉 开始使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 .env
notepad .env

# 3. 启动（虚拟交易）
unreal\START_ADVANCED.bat

# 4. 打开浏览器
http://127.0.0.1:5000
```

**祝交易顺利！** 🚀
