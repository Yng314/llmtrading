# 💾 数据持久化使用指南

## 🎯 功能概述

系统现在支持自动保存和恢复交易状态，方便调试和测试！

### 自动保存内容
- ✅ 账户资金 (capital)
- ✅ 持仓位置 (open positions)
- ✅ 交易历史 (trade history)
- ✅ 价格历史 (price_history) - **图表数据持续显示**
- ✅ 账户价值历史 (value_history) - **图表数据持续显示**
- ✅ 迭代次数 (iteration_count)

### 保存时机
1. **按 Ctrl+C 退出时** - 自动保存
2. **程序正常关闭时** - 自动保存
3. **程序崩溃时** - ⚠️ 可能丢失最近数据

---

## 🚀 使用方法

### 1. 继续上次运行（默认模式）

```bash
# Windows
START_ADVANCED.bat

# 或直接运行
python main_advanced.py
```

**效果：**
- ✅ 自动加载上次保存的状态
- ✅ 图表显示**完整历史数据**（从最开始到现在）
- ✅ 持仓、资金、交易记录全部恢复
- ✅ 继续之前的交易

**控制台输出示例：**
```
✅ State loaded from trading_data.json
   Saved at: 2025-10-24T15:30:45
   Iteration: 42
   Capital: $1025.50
   Open Positions: 2
   Trade History: 15 trades
✅ Resumed from saved state
```

---

### 2. 重新开始（Restart模式）

```bash
# Windows
START_ADVANCED.bat --restart

# 或直接运行
python main_advanced.py --restart
```

**效果：**
- 🔄 清空所有保存的数据
- 🆕 从$1000初始资金开始
- 📊 图表从零开始
- 📝 交易历史清空

**控制台输出示例：**
```
🔄 Restart mode: Clearing saved state...
✅ Deleted saved state: trading_data.json
🆕 Starting fresh (restart mode)
```

---

## 📊 图表数据持久化

### ✅ 问题1已解决：时间轴自动扩展

之前：图表只显示有限时间范围的数据
现在：**图表自动显示从程序启动到现在的所有数据**

**实现方式：**
- 价格历史保存在 `trading_data.json`
- 账户价值历史保存在 `trading_data.json`
- 重新启动后自动加载并继续追加

**示例场景：**
```
第一次运行 (1小时):
  - 图表显示：0-60分钟的数据

关闭程序，重新启动

第二次运行 (30分钟):
  - 图表显示：0-90分钟的数据 ✅
  - X轴自动扩展，显示完整历史
```

---

## 🎨 图表优化

### ✅ 问题2已解决：去掉数据点圆圈

之前：数据点有圆圈，数据多了看不清
现在：**默认无圆圈，鼠标悬停时显示小圆点**

**效果：**
- 📈 折线更清晰
- 👁️ 视觉更简洁
- 🖱️ 鼠标悬停仍可看到具体数值

**Chart.js配置：**
```javascript
pointRadius: 0,          // 默认无圆圈
pointHoverRadius: 4      // 悬停时显示小圆点
```

---

## 🗂️ 数据文件位置

### 保存文件
```
D:\workspace\llmtrading\trading_data.json
```

### 文件内容示例
```json
{
  "timestamp": "2025-10-24T15:30:45",
  "iteration_count": 42,
  "simulator": {
    "initial_capital": 1000.0,
    "capital": 1025.50,
    "open_positions": [...],
    "trade_history": [...]
  },
  "value_history": [
    {"timestamp": "2025-10-24T14:00:00", "value": 1000.0},
    {"timestamp": "2025-10-24T14:05:00", "value": 1010.5},
    ...
  ],
  "price_history": {
    "BTCUSDT": [
      {"timestamp": "2025-10-24T14:00:00", "price": 100000.0},
      ...
    ],
    ...
  }
}
```

---

## 🛠️ 手动管理

### 查看保存的数据
```python
python
>>> from data_persistence import DataPersistence
>>> dp = DataPersistence()
>>> state = dp.load_state()
>>> print(f"Capital: ${state['simulator']['capital']}")
>>> print(f"Positions: {len(state['simulator']['open_positions'])}")
```

### 手动删除数据
```bash
# Windows
del trading_data.json

# Linux/Mac
rm trading_data.json
```

### 手动备份数据
```bash
# Windows
copy trading_data.json trading_data_backup.json

# Linux/Mac
cp trading_data.json trading_data_backup.json
```

---

## 🧪 测试场景

### 场景1：连续测试多个策略

```bash
# 测试策略A
python main_advanced.py --restart
# ... 运行30分钟，Ctrl+C退出

# 查看结果，继续测试
python main_advanced.py
# ... 再运行30分钟

# 结果：图表显示完整60分钟数据 ✅
```

### 场景2：调试交易逻辑

```bash
# 第一次运行
python main_advanced.py --restart
# 发现bug，Ctrl+C退出

# 修改代码

# 重新测试（从头开始）
python main_advanced.py --restart
```

### 场景3：长期运行监控

```bash
# 启动
python main_advanced.py

# 24小时后，意外断电

# 重启电脑后
python main_advanced.py
# ✅ 自动恢复到断电前的状态
# ✅ 图表显示完整24小时数据
```

---

## 📋 数据恢复检查清单

程序重启后，应该看到：

- [ ] 控制台显示 "✅ State loaded from trading_data.json"
- [ ] 初始资金显示为上次的最终金额
- [ ] Open Positions显示之前的持仓
- [ ] Recent Trades显示之前的交易记录
- [ ] 图表显示从最开始到现在的所有数据
- [ ] Iteration计数器继续递增（不从0开始）

如果以上都正确，说明数据恢复成功！✅

---

## ⚠️ 注意事项

### 1. 数据不一致问题

**问题：** 如果修改了 `config.py` 中的初始资金
**解决：** 使用 `--restart` 重新开始

```bash
# 修改 config.py: INITIAL_CAPITAL = 2000
python main_advanced.py --restart  # 必须restart
```

### 2. 数据损坏问题

**症状：** 程序启动报错，无法加载数据
**解决：**
```bash
# 删除损坏的数据文件
del trading_data.json
# 重新启动
python main_advanced.py
```

### 3. 持仓价格更新

**说明：** 保存的是持仓信息，不是当前价格
- ✅ Entry Price (开仓价) - 保存并恢复
- ❌ Current Price (当前价) - 重启后重新获取

这是正确的行为，因为市场价格一直在变化。

---

## 🎯 最佳实践

### 开发/调试阶段
```bash
# 每次测试都从头开始
python main_advanced.py --restart
```

### 生产/长期运行
```bash
# 允许自动恢复
python main_advanced.py

# 定期备份
copy trading_data.json backups\trading_data_$(date).json
```

### 测试新功能
```bash
# 1. 备份当前数据
copy trading_data.json trading_data_backup.json

# 2. 测试新功能
python main_advanced.py --restart

# 3. 如果失败，恢复数据
copy trading_data_backup.json trading_data.json
python main_advanced.py
```

---

## 📊 图表显示逻辑

### Account Value 图表
- 显示账户总价值随时间的变化
- 包括现金 + 持仓价值 + 未实现盈亏
- **时间轴：从程序第一次启动到现在**

### Price Change (%) 图表
- 显示各币种价格变化百分比
- 基准：程序第一次运行时的价格
- **时间轴：从程序第一次启动到现在**

### 数据更新频率
- 每30秒（默认）更新一次
- Web界面每2秒刷新显示
- 数据持续累积，不会清空

---

## 🚀 快速开始

### 第一次使用
```bash
python main_advanced.py
# 程序自动检测：没有保存的数据，从头开始
```

### 后续使用（继续）
```bash
python main_advanced.py
# ✅ 自动加载上次的状态
```

### 后续使用（重新开始）
```bash
python main_advanced.py --restart
# 🔄 清空数据，从头开始
```

就这么简单！🎉

---

## 💡 常见问题

### Q1: 图表为什么只显示部分数据？
A: 刷新浏览器页面，确保加载最新的JavaScript代码。

### Q2: Restart后图表还显示旧数据？
A: 图表数据来自服务器，确保使用了 `--restart` 参数。

### Q3: 关闭程序后数据会丢失吗？
A: 不会！按Ctrl+C退出会自动保存。只有强制关闭（kill）可能丢失。

### Q4: 可以查看保存的数据吗？
A: 可以！直接打开 `trading_data.json` 文件查看（JSON格式）。

### Q5: 数据文件会越来越大吗？
A: 会的。可以定期使用 `--restart` 清空，或手动删除 `trading_data.json`。

---

## 📈 总结

### ✅ 已解决的问题

| 问题 | 解决方案 | 状态 |
|------|---------|------|
| 图表时间范围受限 | 数据持久化 + 自动加载 | ✅ 完成 |
| 数据点圆圈太多 | pointRadius: 0 | ✅ 完成 |
| Positions/Trades未分开 | 本来就是分开的卡片 | ✅ 已有 |
| 重启丢失数据 | 自动保存/恢复 + restart参数 | ✅ 完成 |

### 🎉 现在你可以：
- ✅ 关闭程序不丢失数据
- ✅ 图表显示完整历史
- ✅ 灵活选择继续或重新开始
- ✅ 折线图更清晰（无圆圈）
- ✅ 便于连续测试和调试

享受更好的交易体验！🚀

