"""
Real Trading Bot - 真实交易版本
连接Binance账户进行真实交易
"""

import time
from datetime import datetime
import signal
import sys
import argparse
from typing import Dict
import threading
import os
from dotenv import load_dotenv

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DECISION_INTERVAL, TRADING_PAIRS
from crypto_api import CryptoAPI
from technical_analysis import analyze_market
from llm_agent_advanced import AdvancedTradingAgent
from logger import TradingLogger
from web_server import update_trading_data, update_llm_conversation, run_server

# 导入real文件夹中的模块
from real.binance_real_trader import BinanceRealTrader
from real.trading_executor_real import RealTradingExecutor

# 加载环境变量
load_dotenv()


class RealTradingBot:
    """真实交易机器人"""
    
    def __init__(self):
        # API密钥
        self.api_key = os.getenv('BINANCE_API_KEY', '')
        self.api_secret = os.getenv('BINANCE_API_SECRET', '')
        self.testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            print("\n❌ 错误: 未设置Binance API密钥")
            print("请在 .env 文件中设置:")
            print("  BINANCE_API_KEY=your_key")
            print("  BINANCE_API_SECRET=your_secret")
            print("\n测试网注册: https://testnet.binancefuture.com")
            sys.exit(1)
        
        # 初始化组件
        self.api = CryptoAPI()
        self.agent = AdvancedTradingAgent()
        self.executor = RealTradingExecutor(self.api_key, self.api_secret, self.testnet)
        self.logger = TradingLogger()
        
        self.running = False
        self.last_decision_time = 0
        self.last_prices = {}
        self.iteration_count = 0
        
        # 历史数据
        self.value_history = []
        self.price_history = {}
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理关闭信号"""
        if not self.running:
            sys.exit(0)
        print("\n\n收到关闭信号，正在退出...")
        self.running = False
    
    def execute_actions(self, actions: list, current_prices: Dict[str, float], chain_of_thought: Dict = None):
        """执行LLM决策的交易动作"""
        if not actions:
            self.logger.log("无操作")
            return
        
        cot = chain_of_thought or {}
        
        self.logger.log(f"\n执行 {len(actions)} 个动作:")
        
        for i, action_data in enumerate(actions, 1):
            try:
                action = action_data.get('action', '').lower()
                symbol = action_data.get('symbol', '')
                reason = action_data.get('reason', '')
                
                if action == 'open':
                    position_type = action_data.get('position_type', '').lower()
                    size = float(action_data.get('size', 0))
                    leverage = float(action_data.get('leverage', 1))
                    
                    # 提取目标价和止损价
                    target_price = None
                    stop_loss = None
                    if symbol in cot:
                        target_price = cot[symbol].get('target_price')
                        stop_loss = cot[symbol].get('stop_loss')
                    
                    target_str = f", 目标: ${target_price:.2f}" if target_price else ""
                    stop_str = f", 止损: ${stop_loss:.2f}" if stop_loss else ""
                    
                    self.logger.log(f"  📈 开仓 {position_type.upper()}: {symbol} ${size:.2f} "
                                  f"(杠杆: {leverage}x){target_str}{stop_str}")
                    self.logger.log(f"     原因: {reason}")
                    
                    position = self.executor.open_position(
                        symbol=symbol,
                        position_type=position_type,
                        size=size,
                        current_price=current_prices[symbol],
                        leverage=leverage,
                        target_price=target_price,
                        stop_loss=stop_loss
                    )
                    
                    if position:
                        self.logger.log(f"  ✅ 开仓成功")
                    else:
                        self.logger.log(f"  ❌ 开仓失败")
                        available = self.executor.get_available_capital()
                        margin_needed = size / leverage
                        self.logger.log(f"     可用资金: ${available:.2f}")
                        self.logger.log(f"     需要保证金: ${margin_needed:.2f}")
                        if margin_needed > available:
                            self.logger.log(f"     ⚠️  资金不足 (还需 ${margin_needed - available:.2f})")
                
                elif action == 'close':
                    position_type = action_data.get('position_type', '').lower()
                    
                    self.logger.log(f"  📉 平仓 {position_type.upper()}: {symbol}")
                    self.logger.log(f"     原因: {reason}")
                    
                    success = self.executor.close_position(
                        symbol=symbol,
                        position_type=position_type,
                        current_price=current_prices[symbol]
                    )
                    
                    if success:
                        self.logger.log(f"  ✅ 平仓成功")
                    else:
                        self.logger.log(f"  ❌ 平仓失败")
                
                elif action == 'hold':
                    self.logger.log(f"  ⏸️  保持: {symbol} - {reason}")
                
                else:
                    self.logger.log(f"  ⚠️  未知动作: {action}")
            
            except Exception as e:
                self.logger.log(f"  ❌ 执行动作时出错: {e}")
                import traceback
                traceback.print_exc()
    
    def run_iteration(self):
        """运行一次迭代"""
        self.iteration_count += 1
        current_time = time.time()
        
        self.logger.log(f"\n--- 迭代 {self.iteration_count} ---")
        
        # 1. 获取价格
        current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
        if not current_prices:
            self.logger.log("❌ 获取价格失败")
            return
        
        price_str = ", ".join([f"{s}: ${p:,.2f}" for s, p in current_prices.items()])
        self.logger.log(f"当前价格: {price_str}")
        
        # 2. 获取统计
        stats = self.executor.get_statistics(current_prices)
        open_positions = self.executor.get_open_positions_summary(current_prices)
        
        # 3. 更新历史数据
        timestamp = datetime.now().isoformat()
        
        self.value_history.append({
            'timestamp': timestamp,
            'value': stats['total_value']
        })
        
        for symbol, price in current_prices.items():
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append({
                'timestamp': timestamp,
                'price': price
            })
        
        # 4. 更新Web界面
        closed_trades = self.executor.closed_positions
        update_trading_data(current_prices, open_positions, stats, closed_trades,
                          self.value_history, self.price_history)
        
        # 5. 检查是否需要LLM决策
        time_since_last = current_time - self.last_decision_time
        should_decide, trigger_reason = self.agent.should_request_decision(
            current_prices,
            self.last_prices,
            time_since_last,
            DECISION_INTERVAL,
            open_positions
        )
        
        if should_decide:
            self.logger.log(f"\n=== 请求LLM决策 (触发: {trigger_reason}) ===")
            
            # 获取市场分析
            market_data = {}
            for symbol in TRADING_PAIRS:
                klines = self.api.get_klines(symbol, interval='15m', limit=100)
                if klines:
                    market_data[symbol] = analyze_market(klines)
            
            # 请求LLM决策
            decision = self.agent.make_decision(
                current_prices=current_prices,
                open_positions=open_positions,
                account_balance=stats['current_capital'],
                market_data=market_data
            )
            
            if decision:
                # 记录LLM对话
                self.logger.log(f"🤖 LLM总结: {decision['summary']}")
                update_llm_conversation(decision)
                
                # 执行动作
                self.execute_actions(
                    decision['actions'],
                    current_prices,
                    decision.get('chain_of_thought')
                )
            
            self.last_decision_time = current_time
        
        # 6. 更新上次价格
        self.last_prices = current_prices.copy()
        
        # 7. 定期输出统计
        if self.iteration_count % 10 == 0:
            self.logger.print_summary(stats, current_prices)
    
    def run(self, sleep_seconds: int = 30):
        """运行机器人"""
        self.running = True
        
        mode = "测试网 (虚拟资金)" if self.testnet else "实盘 (真实资金)"
        self.logger.log(f"=== 真实交易机器人启动 ({mode}) ===")
        self.logger.log(f"决策间隔: {DECISION_INTERVAL}秒")
        self.logger.log(f"交易对: {', '.join(TRADING_PAIRS)}")
        self.logger.log(f"迭代间隔: {sleep_seconds}秒")
        self.logger.log(f"Web界面: http://127.0.0.1:5000\n")
        
        # 初始化Web界面
        try:
            current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
            if current_prices:
                stats = self.executor.get_statistics(current_prices)
                open_positions = self.executor.get_open_positions_summary(current_prices)
                closed_trades = self.executor.closed_positions
                
                update_trading_data(current_prices, open_positions, stats, closed_trades,
                                  self.value_history, self.price_history)
                self.logger.log("✅ 初始数据已发送到Web界面")
        except Exception as e:
            self.logger.log(f"⚠️  初始化Web界面失败: {e}")
        
        try:
            while self.running:
                self.run_iteration()
                time.sleep(sleep_seconds)
        
        except KeyboardInterrupt:
            self.logger.log("\n收到键盘中断")
        
        except Exception as e:
            self.logger.log(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """关闭机器人"""
        self.logger.log("\n=== 机器人关闭 ===")
        self.running = False


def run_bot_in_thread(bot: RealTradingBot):
    """在后台线程运行机器人"""
    bot.run(sleep_seconds=10)


def main():
    """主入口"""
    print("""
╔════════════════════════════════════════════════════════════╗
║    Real Trading Bot - 真实交易版本                         ║
║                                                            ║
║  ⚠️  使用前必读:                                           ║
║                                                            ║
║  1. 确认已在 .env 中设置 BINANCE_API_KEY                   ║
║  2. BINANCE_TESTNET=true 使用测试网（推荐）                ║
║  3. BINANCE_TESTNET=false 使用实盘（谨慎！）               ║
║                                                            ║
║  测试网注册: https://testnet.binancefuture.com            ║
║  Web界面: http://127.0.0.1:5000                           ║
║                                                            ║
║  按 Ctrl+C 退出                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 检查API密钥
    from config import DASHSCOPE_API_KEY
    if not DASHSCOPE_API_KEY:
        print("\n⚠️  警告: DASHSCOPE_API_KEY 未设置")
        print("LLM决策功能将无法使用\n")
    
    # 创建机器人
    bot = RealTradingBot()
    
    # 在后台线程运行
    bot_thread = threading.Thread(target=run_bot_in_thread, args=(bot,), daemon=True)
    bot_thread.start()
    
    # 主线程运行Web服务器
    try:
        run_server(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n关闭中...")
        bot.running = False
        bot_thread.join(timeout=5)


if __name__ == "__main__":
    main()

