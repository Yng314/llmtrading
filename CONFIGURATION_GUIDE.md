# ⚙️ 配置指南

## 🕐 调整运行频率

### Sleep Time (迭代间隔)

**位置：** `main_advanced.py` 第254行

```python
# 当前设置
bot.run(sleep_seconds=30)  # 每30秒检查一次
```

**修改方式：**

```python
# 更频繁（每10秒）
bot.run(sleep_seconds=10)

# 更慢（每60秒）
bot.run(sleep_seconds=60)

# 快速测试（每5秒）
bot.run(sleep_seconds=5)
```

**影响：**
- ✅ 更短 = 更快响应市场变化
- ✅ 更短 = 更频繁获取价格数据
- ⚠️ 更短 = 更多API请求（可能被限流）
- ⚠️ 太短可能导致不必要的资源消耗

**推荐值：**
- 生产环境：30-60秒
- 测试环境：10-30秒
- 快速调试：5-10秒

---

### LLM决策间隔

**位置：** `config.py`

```python
DECISION_INTERVAL = 300  # 秒（5分钟）
```

**修改方式：**

```python
# 更频繁的LLM分析（每3分钟）
DECISION_INTERVAL = 180

# 更慢，节省token（每10分钟）
DECISION_INTERVAL = 600

# 仅在波动时决策（设置很大的值）
DECISION_INTERVAL = 3600  # 1小时
```

**影响：**
- ⚠️ 更短 = 更多token消耗
- ✅ 更短 = 更快响应市场机会
- ✅ 更长 = 节省API成本

**Note:** 即使设置较长间隔，如果价格波动超过3%，系统会提前触发LLM决策。

---

## 🎯 常见配置组合

### 1. 激进交易模式
```python
# main_advanced.py
bot.run(sleep_seconds=10)

# config.py
DECISION_INTERVAL = 180  # 3分钟
VOLATILITY_THRESHOLD = 0.02  # 2%波动触发
```
- 快速响应
- 高token消耗
- 适合：波动大的市场

### 2. 稳健交易模式（推荐）
```python
# main_advanced.py
bot.run(sleep_seconds=30)

# config.py
DECISION_INTERVAL = 300  # 5分钟
VOLATILITY_THRESHOLD = 0.02
```
- 平衡速度和成本
- 适合：大多数情况

### 3. 节省Token模式
```python
# main_advanced.py
bot.run(sleep_seconds=60)

# config.py
DECISION_INTERVAL = 600  # 10分钟
VOLATILITY_THRESHOLD = 0.03  # 3%波动才触发
```
- 最低token消耗
- 较慢响应
- 适合：低波动市场或测试

### 4. 快速测试模式
```python
# main_advanced.py
bot.run(sleep_seconds=5)

# config.py
DECISION_INTERVAL = 60  # 1分钟
```
- 快速看到效果
- ⚠️ 不建议长期运行
- 适合：调试和演示

---

## 📊 Web界面刷新频率

**位置：** `templates/dashboard_with_chat.html`

在文件底部：

```javascript
// 当前设置：每2秒刷新
setInterval(fetchData, 2000);
```

**修改方式：**

```javascript
// 更频繁（每1秒）
setInterval(fetchData, 1000);

// 更慢（每5秒）
setInterval(fetchData, 5000);
```

**推荐：** 保持2秒，足够实时且不会造成过多请求。

---

## 🔧 其他重要配置

### config.py 完整配置

```python
# 初始资金
INITIAL_CAPITAL = 1000

# 最大杠杆
MAX_LEVERAGE = 20

# LLM决策间隔（秒）
DECISION_INTERVAL = 300

# 交易币种
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

# LLM模型
LLM_MODEL = 'qwen-max'
LLM_TEMPERATURE = 0.7

# 波动率触发阈值
VOLATILITY_THRESHOLD = 0.02  # 2%
```

### 修改交易币种

```python
# 只交易主流币
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT']

# 添加更多币种
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT']
```

---

## 💰 Token消耗估算

### 当前配置（默认）
- Sleep: 30秒
- Decision Interval: 300秒（5分钟）
- 每小时LLM调用：~12次
- 每次约1200 tokens
- **预计成本：¥0.2-0.4/小时**

### 激进配置
- Sleep: 10秒
- Decision Interval: 180秒（3分钟）
- 每小时LLM调用：~20次
- **预计成本：¥0.4-0.6/小时**

### 节省配置
- Sleep: 60秒
- Decision Interval: 600秒（10分钟）
- 每小时LLM调用：~6次
- **预计成本：¥0.1-0.2/小时**

---

## 🎯 快速修改指南

### 场景1：想更频繁地交易

```python
# main_advanced.py 第254行
bot.run(sleep_seconds=15)  # 改为15秒

# config.py
DECISION_INTERVAL = 180  # 改为3分钟
```

### 场景2：想节省Token

```python
# main_advanced.py 第254行
bot.run(sleep_seconds=60)  # 改为1分钟

# config.py
DECISION_INTERVAL = 600  # 改为10分钟
VOLATILITY_THRESHOLD = 0.03  # 提高触发阈值到3%
```

### 场景3：只想测试看看效果

```python
# main_advanced.py 第254行
bot.run(sleep_seconds=5)  # 改为5秒

# config.py
DECISION_INTERVAL = 30  # 改为30秒（快速看到LLM决策）
```

---

## ⚠️ 注意事项

1. **Binance API限流**
   - 太频繁的请求可能被限流
   - 建议sleep_seconds >= 5秒

2. **Token成本**
   - DECISION_INTERVAL < 60秒 = 高成本
   - 建议 >= 180秒

3. **系统负载**
   - sleep_seconds < 10秒可能占用较多CPU
   - 长期运行建议 >= 30秒

4. **Web刷新频率**
   - 不建议 < 1秒
   - 可能导致浏览器卡顿

---

## 🚀 推荐配置

**生产环境（长期运行）：**
```python
# main_advanced.py
bot.run(sleep_seconds=30)

# config.py
DECISION_INTERVAL = 300
VOLATILITY_THRESHOLD = 0.02
MAX_LEVERAGE = 20
```

**快速测试（短期观察）：**
```python
# main_advanced.py
bot.run(sleep_seconds=10)

# config.py
DECISION_INTERVAL = 120  # 2分钟
VOLATILITY_THRESHOLD = 0.015  # 1.5%
```

立即生效：修改后重启程序即可！

