# 🚀 快速启动指南 (Restart功能)

## 💡 核心概念

程序现在有**两种启动模式**：

| 模式 | 命令 | 效果 |
|------|------|------|
| **继续模式** | `python main_advanced.py` | 恢复上次状态，图表显示全部历史 |
| **重启模式** | `python main_advanced.py --restart` | 从头开始，清空所有数据 |

---

## 📋 常用命令

### Windows 批处理文件

```bash
# 继续上次运行
START_ADVANCED.bat

# 从头开始
START_ADVANCED.bat --restart
```

### 直接运行Python

```bash
# 继续上次运行
python main_advanced.py

# 从头开始  
python main_advanced.py --restart
```

---

## 🎯 使用场景

### 场景1：日常运行
```bash
# 每天启动
START_ADVANCED.bat
# ✅ 自动恢复昨天的状态和数据
```

### 场景2：测试新策略
```bash
# 清空数据，测试新策略
START_ADVANCED.bat --restart
```

### 场景3：修复问题后
```bash
# 修改代码后，从头测试
python main_advanced.py --restart
```

### 场景4：程序崩溃后
```bash
# 重新启动，自动恢复
python main_advanced.py
# ✅ 持仓、资金、图表数据全部恢复
```

---

## 📊 图表显示说明

### 继续模式 (默认)
```
第一次运行: 0-60分钟数据
关闭程序
第二次运行: 0-90分钟数据 ✅ (包含之前60分钟)
```
**X轴自动扩展，显示从最开始到现在的所有数据！**

### 重启模式 (--restart)
```
重新运行: 0-30分钟数据 🆕 (从零开始)
```
**X轴重置，图表从头开始！**

---

## ✅ 4个问题的解决方案总结

### 1️⃣ 图表时间范围自动拉长
**解决：** 数据持久化，重启后继续累积
```bash
python main_advanced.py  # 图表显示完整历史
```

### 2️⃣ 去掉折线图圆圈
**解决：** 已修改 `dashboard_with_chat.html`
```javascript
pointRadius: 0  // 无圆圈，数据多也清晰
```

### 3️⃣ Open Positions 和 Recent Trades 分成两个卡片
**状态：** 已经是两个独立的卡片 ✅

### 4️⃣ 支持数据持久化和restart参数
**解决：** 新增 `data_persistence.py` + `--restart` 参数
```bash
python main_advanced.py           # 继续
python main_advanced.py --restart # 重新开始
```

---

## 🔄 完整工作流程

### 开发/调试阶段
```bash
# 1. 第一次测试
python main_advanced.py --restart

# 2. 发现问题，Ctrl+C退出
# (数据已自动保存)

# 3. 修改代码

# 4. 重新测试（从头开始）
python main_advanced.py --restart
```

### 生产/长期运行
```bash
# 1. 首次启动
python main_advanced.py

# 2. 需要重启服务器
# Ctrl+C退出 (数据已保存)

# 3. 重新启动
python main_advanced.py
# ✅ 自动恢复持仓、资金、图表
```

---

## 📁 数据文件

### 保存位置
```
D:\workspace\llmtrading\trading_data.json
```

### 保存内容
- 账户资金
- 持仓位置
- 交易历史
- 价格历史（图表数据）
- 账户价值历史（图表数据）

### 手动管理
```bash
# 查看数据
type trading_data.json

# 删除数据（效果等同于 --restart）
del trading_data.json

# 备份数据
copy trading_data.json backup\trading_data_20251024.json
```

---

## ⚡ 快速参考

### 想继续之前的交易？
```bash
python main_advanced.py
```

### 想从头开始？
```bash
python main_advanced.py --restart
```

### 想看图表完整历史？
```bash
python main_advanced.py  # 不要加 --restart
```

### 想清空图表重新记录？
```bash
python main_advanced.py --restart
```

---

## 🎉 完成！

现在你可以：
- ✅ 关闭程序不丢数据
- ✅ 图表显示完整时间线
- ✅ 灵活切换继续/重启模式
- ✅ 折线图更清晰好看

开始交易吧！🚀

