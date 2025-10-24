# 做空功能测试说明

## ✅ 做空功能已实现

系统完全支持做空（SHORT）功能，已在代码中确认：

### 1. Position类型定义
```python
class PositionType(Enum):
    LONG = "long"
    SHORT = "short"
```

### 2. 盈亏计算（支持做空）
```python
def calculate_pnl(self, current_price: float) -> float:
    if self.position_type == PositionType.LONG:
        # 做多：价格上涨赚钱
        price_change_pct = (current_price - self.entry_price) / self.entry_price
    else:  # SHORT
        # 做空：价格下跌赚钱
        price_change_pct = (self.entry_price - current_price) / self.entry_price
    
    # 应用杠杆
    pnl = self.size * price_change_pct * self.leverage
    return pnl
```

### 3. 开仓支持做空
```python
def open_position(self, symbol: str, position_type: str, size: float, 
                 current_price: float, leverage: float = 1.0):
    # position_type 可以是 'long' 或 'short'
    pos_type = PositionType.LONG if position_type.lower() == 'long' else PositionType.SHORT
    ...
```

## 🔧 已做的改进

### 改进1：激进的LLM策略

**之前的问题：**
- LLM太保守，倾向于HOLD
- 杠杆默认1x，太低
- 很少建议做空

**现在的改进：**

#### 1. 更激进的指令
```
You are an AGGRESSIVE cryptocurrency trader
BE AGGRESSIVE: Look for opportunities in BOTH directions
```

#### 2. 做空指引
```
SHORT positions: Open when trend is bearish
RSI > 70 = STRONG SELL SHORT signal
MACD crossing down = buy short
Price below EMA-20 = consider short
```

#### 3. 杠杆策略
```
- Use 10-15x leverage for moderate conviction
- Use 15-20x leverage for high conviction (confidence > 0.8)
- Minimum leverage should be 5x
```

#### 4. 主动交易
```
Empty actions array should be RARE
You MUST consider BOTH long AND short opportunities
Be decisive and aggressive - we're here to make money!
```

### 改进2：提高最大杠杆

```python
# config.py
MAX_LEVERAGE = 20  # 从10提高到20
```

### 改进3：仓位建议

```
- Use 15-25% of available capital per trade
- Can hold multiple positions
- Diversify between long and short
```

## 📊 做空示例

### 场景1：价格下跌，做空盈利

```
开仓：
- Symbol: BTCUSDT
- Position: SHORT (做空)
- Entry Price: $110,000
- Size: $200
- Leverage: 15x

价格下跌到 $108,000 (-1.82%)

盈亏计算：
- 价格变化：($110,000 - $108,000) / $110,000 = +1.82%
- P&L = $200 × 1.82% × 15 = $54.60 ✅ 盈利！
```

### 场景2：价格上涨，做空亏损

```
开仓：
- Symbol: BTCUSDT
- Position: SHORT (做空)
- Entry Price: $110,000
- Size: $200
- Leverage: 15x

价格上涨到 $111,000 (+0.91%)

盈亏计算：
- 价格变化：($110,000 - $111,000) / $110,000 = -0.91%
- P&L = $200 × (-0.91%) × 15 = -$27.30 ❌ 亏损
```

## 🎯 如何触发做空

LLM现在会在这些情况下建议做空：

### 1. RSI超买
```
RSI > 70 → "RSI overbought, open SHORT position"
```

### 2. 下降趋势
```
Price < EMA-20 and MACD < 0 → "Bearish trend, go SHORT"
```

### 3. MACD死叉
```
MACD crossing below signal → "SHORT signal confirmed"
```

### 4. 布林带上轨
```
Price > Bollinger Upper Band → "Potential reversal, SHORT opportunity"
```

## 🚀 测试建议

### 1. 等待市场回调
当你看到某个币种：
- RSI > 70
- 价格在布林带上轨
- MACD开始下降

LLM应该会建议开空单

### 2. 观察Model Chat
在Web界面的Model Chat中，你会看到：
```
Chain of Thought:
{
  "BTC": {
    "signal": "buy_short",
    "confidence": 0.85,
    "justification": "RSI 72 overbought, MACD turning negative",
    "leverage": 15,
    ...
  }
}

Actions:
[BTCUSDT SHORT] 15x leverage
```

### 3. 检查终端日志
```
Action 1: {'action': 'open', 'symbol': 'BTCUSDT', 'position_type': 'short', ...}
  📉 Opening SHORT position: BTCUSDT $200.00 (Leverage: 15.0x)
  ✅ Position opened successfully
```

## 💡 为什么之前没看到做空？

可能原因：
1. **市场处于上涨趋势**：所有币种RSI < 70，MACD正值 → LLM认为不适合做空
2. **LLM太保守**：旧版prompt倾向于HOLD而不是主动交易
3. **杠杆太低**：1-3x杠杆收益不明显，LLM倾向不开仓

现在已经修复，LLM会更激进地寻找机会！

## 📋 检查清单

运行程序后检查：
- ✅ 配置文件MAX_LEVERAGE已改为20
- ✅ LLM prompt已更新为激进策略
- ✅ Action执行逻辑支持SHORT
- ✅ P&L计算正确处理做空
- ✅ Web界面显示SHORT标签

## 🎉 预期效果

重启后，你应该看到：
- 🔴 **更多SHORT仓位**（市场回调时）
- ⚡ **更高杠杆**（10-20x）
- 📈 **更主动的交易**（不再只是HOLD）
- 💰 **更高的收益**（和风险）

准备好了吗？重启程序试试！🚀

