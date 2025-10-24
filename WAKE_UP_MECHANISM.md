# 🚨 LLM 多级唤醒机制文档

## 📋 概述

系统不再是固定300秒调用LLM，而是实施了**智能多级唤醒机制**，根据市场情况动态决定何时请求LLM判断。

---

## 🎯 五级触发机制

### ⏰ Level 0: 冷却保护（Cooldown）
**优先级：** 最高（防护机制）
**阈值：** 30秒（可配置）

**作用：**
- 防止过于频繁的LLM调用
- 即使满足其他条件，30秒内不会重复触发

**配置：**
```python
# config.py
COOLDOWN_SECONDS = 30  # 冷却时间
```

---

### 📅 Level 1: 定时触发（Scheduled）
**优先级：** 最低
**默认间隔：** 300秒（5分钟）

**触发条件：**
- 距离上次LLM决策超过300秒

**触发提示：**
```
=== Requesting LLM Decision (Trigger: scheduled_interval) ===
```

**特点：**
- 基础保障，确保定期分析市场
- 即使市场平静，也会定期检查

---

### 📊 Level 2: 市场波动触发（Market Volatility）
**优先级：** 中等

#### 2a. 单币紧急波动
**阈值：** 5%（可配置）

**触发条件：**
- 任意币种价格变化超过5%

**触发提示：**
```
=== Requesting LLM Decision (Trigger: emergency_volatility_BTCUSDT_5.2%) ===
```

**配置：**
```python
# config.py
EMERGENCY_THRESHOLD = 0.05  # 5% 紧急波动
```

#### 2b. 市场联动波动
**阈值：** 3个币同时2%波动（可配置）

**触发条件：**
- 至少3个币种同时出现2%以上波动
- 表示市场整体波动加剧

**触发提示：**
```
=== Requesting LLM Decision (Trigger: market_volatility_4_coins_(BTCUSDT:2.1%, ETHUSDT:2.3%, BNBUSDT:2.0%)) ===
```

**配置：**
```python
# config.py
VOLATILITY_THRESHOLD = 0.02  # 2% 普通波动
MARKET_VOLATILITY_COINS = 3  # 联动币种数
```

---

### 🛡️ Level 3: 持仓风险触发（Position Risk）
**优先级：** 最高

#### 3a. 达到LLM设定的目标价
**触发条件：**
- 持仓币种价格达到LLM设定的target_price

**示例：**
```
做多BTCUSDT:
  Entry: $100,000
  Target: $105,000
  Current: $105,200 ✅ 触发

做空ETHUSDT:
  Entry: $4,000
  Target: $3,800
  Current: $3,790 ✅ 触发
```

**触发提示：**
```
=== Requesting LLM Decision (Trigger: target_reached_BTCUSDT_$105200.00) ===
```

#### 3b. 触及LLM设定的止损价
**触发条件：**
- 持仓币种价格触及LLM设定的stop_loss

**示例：**
```
做多BTCUSDT:
  Entry: $100,000
  Stop Loss: $98,000
  Current: $97,900 ❌ 触发

做空ETHUSDT:
  Entry: $4,000
  Stop Loss: $4,100
  Current: $4,120 ❌ 触发
```

**触发提示：**
```
=== Requesting LLM Decision (Trigger: stop_loss_hit_BTCUSDT_$97900.00) ===
```

#### 3c. 持仓币种逆向波动
**阈值：** 2%（可配置）

**触发条件：**
- 做多持仓：价格下跌2%
- 做空持仓：价格上涨2%

**示例：**
```
做多BTCUSDT:
  Last Price: $100,000
  Current: $97,900 (-2.1%) ⚠️ 触发

做空ETHUSDT:
  Last Price: $4,000
  Current: $4,090 (+2.3%) ⚠️ 触发
```

**触发提示：**
```
=== Requesting LLM Decision (Trigger: position_risk_long_BTCUSDT_-2.1%) ===
```

**配置：**
```python
# config.py
POSITION_RISK_THRESHOLD = 0.02  # 2% 持仓风险阈值
```

---

### ⏳ Level 4: 时间衰减触发（Time Decay）
**优先级：** 低

**触发条件：**
- 距离上次决策超过180秒（300秒的60%）
- 且有币种波动超过1.5%（2%的75%）

**作用：**
- 在接近下次定时决策时，降低波动阈值
- 避免错过重要机会

**触发提示：**
```
=== Requesting LLM Decision (Trigger: decay_trigger_ETHUSDT_1.6%) ===
```

---

## 📊 配置参数总览

```python
# config.py

# 定时触发
DECISION_INTERVAL = 300  # 5分钟

# 市场波动
VOLATILITY_THRESHOLD = 0.02          # 2% 普通波动
EMERGENCY_THRESHOLD = 0.05           # 5% 紧急波动
MARKET_VOLATILITY_COINS = 3          # 联动币种数

# 持仓风险
POSITION_RISK_THRESHOLD = 0.02       # 2% 持仓风险阈值

# 冷却保护
COOLDOWN_SECONDS = 30                # 30秒冷却
```

---

## 🎭 工作流程示例

### 场景1：平静市场
```
时间轴：
0s    - 程序启动，first_run触发
30s   - 价格稳定（<2%波动），无触发
60s   - 价格稳定，无触发
...
300s  - scheduled_interval触发 ✅
330s  - 冷却期，即使有波动也不触发
360s  - 价格稳定，无触发
...
600s  - scheduled_interval触发 ✅
```

### 场景2：突发波动
```
时间轴：
0s    - 程序启动
120s  - BTC突然涨6%
→ emergency_volatility触发 ✅
150s  - BTC继续涨
→ 冷却期，不触发
180s  - 冷却结束，但波动<2%，不触发
300s  - scheduled_interval触发 ✅
```

### 场景3：持仓风险
```
持仓状态：
- BTCUSDT long @ $100,000
- Target: $105,000
- Stop Loss: $98,000

时间轴：
0s    - 开仓
30s   - 价格$100,500（+0.5%），无触发
60s   - 价格$97,800（-2.2%）
→ position_risk_long_BTCUSDT触发 ✅
90s   - LLM决定止损
→ 执行关闭持仓
```

### 场景4：达到目标价
```
持仓状态：
- ETHUSDT short @ $4,000
- Target: $3,800
- Stop Loss: $4,100

时间轴：
0s    - 开仓
60s   - 价格$3,950（-1.25%），无触发
120s  - 价格$3,790（-5.25%）
→ target_reached_ETHUSDT触发 ✅
150s  - LLM决定止盈
→ 执行关闭持仓
```

---

## 💰 Token消耗估算

### 平静市场（低消耗）
- 主要触发：scheduled_interval
- 频率：每300秒1次
- **每小时：12次调用**
- **预计成本：¥0.2-0.3/小时**

### 波动市场（中等消耗）
- scheduled_interval: 12次/小时
- market_volatility: 5-8次/小时
- **每小时：17-20次调用**
- **预计成本：¥0.4-0.5/小时**

### 高波动 + 有持仓（高消耗）
- scheduled_interval: 12次/小时
- market_volatility: 8-10次/小时
- position_risk: 5-8次/小时
- **每小时：25-30次调用**
- **预计成本：¥0.6-0.8/小时**

---

## 🔧 调整建议

### 如果觉得触发太频繁

#### 方案1：提高阈值
```python
# config.py
VOLATILITY_THRESHOLD = 0.03          # 2% → 3%
EMERGENCY_THRESHOLD = 0.07           # 5% → 7%
POSITION_RISK_THRESHOLD = 0.03       # 2% → 3%
MARKET_VOLATILITY_COINS = 4          # 3 → 4
```

#### 方案2：延长冷却时间
```python
COOLDOWN_SECONDS = 60  # 30秒 → 60秒
```

#### 方案3：延长定时间隔
```python
DECISION_INTERVAL = 600  # 5分钟 → 10分钟
```

---

### 如果觉得触发不够敏感

#### 方案1：降低阈值
```python
VOLATILITY_THRESHOLD = 0.015         # 2% → 1.5%
EMERGENCY_THRESHOLD = 0.03           # 5% → 3%
POSITION_RISK_THRESHOLD = 0.015      # 2% → 1.5%
MARKET_VOLATILITY_COINS = 2          # 3 → 2
```

#### 方案2：缩短冷却时间
```python
COOLDOWN_SECONDS = 20  # 30秒 → 20秒
```

#### 方案3：缩短定时间隔
```python
DECISION_INTERVAL = 180  # 5分钟 → 3分钟
```

---

## 📈 优势总结

### ✅ vs 固定300秒触发

| 特性 | 固定触发 | 多级触发 |
|------|---------|---------|
| 平静市场 | 每300秒触发 | 每300秒触发 ✅ |
| 突发波动 | 最多延迟300秒 | 立即触发 ✅✅✅ |
| 持仓风险 | 最多延迟300秒 | 立即触发 ✅✅✅ |
| 达到目标价 | 最多延迟300秒 | 立即触发 ✅✅✅ |
| Token消耗 | 固定 | 市场平静时更低 ✅ |
| 风险控制 | 一般 | 优秀 ✅✅✅ |

### 核心优势

1. **风险保护**
   - 持仓风险实时监控
   - 目标价/止损价立即触发
   - 不会延迟300秒才反应

2. **成本优化**
   - 市场平静时不额外触发
   - 冷却机制防止过度调用
   - 只在必要时增加频率

3. **灵活应变**
   - 紧急情况快速响应
   - 市场联动识别
   - 时间衰减机制避免遗漏

4. **可配置**
   - 所有阈值可调整
   - 适应不同交易风格
   - 平衡成本和敏感度

---

## 🎯 使用建议

### 保守交易者
```python
VOLATILITY_THRESHOLD = 0.03          # 提高到3%
EMERGENCY_THRESHOLD = 0.07           # 提高到7%
POSITION_RISK_THRESHOLD = 0.025      # 提高到2.5%
COOLDOWN_SECONDS = 60                # 延长到60秒
DECISION_INTERVAL = 600              # 延长到10分钟
```
**效果：** 减少触发，节省token，适合长线

### 平衡交易者（推荐）
```python
VOLATILITY_THRESHOLD = 0.02          # 2%
EMERGENCY_THRESHOLD = 0.05           # 5%
POSITION_RISK_THRESHOLD = 0.02       # 2%
COOLDOWN_SECONDS = 30                # 30秒
DECISION_INTERVAL = 300              # 5分钟
```
**效果：** 平衡成本和反应速度

### 激进交易者
```python
VOLATILITY_THRESHOLD = 0.015         # 降低到1.5%
EMERGENCY_THRESHOLD = 0.03           # 降低到3%
POSITION_RISK_THRESHOLD = 0.015      # 降低到1.5%
COOLDOWN_SECONDS = 20                # 缩短到20秒
DECISION_INTERVAL = 180              # 缩短到3分钟
```
**效果：** 快速响应，适合短线，token消耗高

---

## 🔍 日志示例

### 查看触发原因
```bash
tail -f logs/trading_*.log | grep "Trigger:"
```

**输出示例：**
```
=== Requesting LLM Decision (Trigger: scheduled_interval) ===
=== Requesting LLM Decision (Trigger: emergency_volatility_BTCUSDT_5.2%) ===
=== Requesting LLM Decision (Trigger: market_volatility_4_coins_(BTCUSDT:2.1%, ...)) ===
=== Requesting LLM Decision (Trigger: target_reached_ETHUSDT_$3790.00) ===
=== Requesting LLM Decision (Trigger: stop_loss_hit_BTCUSDT_$97900.00) ===
=== Requesting LLM Decision (Trigger: position_risk_long_BNBUSDT_-2.3%) ===
=== Requesting LLM Decision (Trigger: decay_trigger_SOLUSDT_1.7%) ===
```

---

## 🎉 总结

**智能多级唤醒机制**让LLM不再是"定时闹钟"，而是"市场哨兵"：
- ✅ 平静时节省token
- ✅ 波动时快速响应
- ✅ 持仓风险实时保护
- ✅ 目标价/止损价立即触发
- ✅ 完全可配置

不再担心急速市场变化，系统会智能判断何时需要LLM介入！🚀

