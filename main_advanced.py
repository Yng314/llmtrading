"""
Advanced trading bot with detailed LLM communication and Model Chat display
"""

import time
from datetime import datetime
import signal
import sys
from typing import Dict
import threading

from config import (
    INITIAL_CAPITAL, MAX_LEVERAGE, DECISION_INTERVAL, 
    TRADING_PAIRS, VOLATILITY_THRESHOLD
)
from crypto_api import CryptoAPI
from trading_simulator import TradingSimulator
from technical_analysis import analyze_market
from llm_agent_advanced import AdvancedTradingAgent
from logger import TradingLogger
from web_server import update_trading_data, update_llm_conversation, run_server


class AdvancedTradingBot:
    """Advanced trading bot with structured LLM communication"""
    
    def __init__(self):
        self.api = CryptoAPI()
        self.simulator = TradingSimulator(INITIAL_CAPITAL, MAX_LEVERAGE)
        self.agent = AdvancedTradingAgent()
        self.logger = TradingLogger()
        
        self.running = False
        self.last_decision_time = 0
        self.last_prices = {}
        self.iteration_count = 0
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        if not self.running:
            sys.exit(0)
        print("\n\nReceived shutdown signal. Closing all positions and exiting...")
        self.running = False
    
    def execute_actions(self, actions: list, current_prices: Dict[str, float]):
        """Execute trading actions from LLM decision"""
        if not actions:
            self.logger.log("No actions to execute")
            return
            
        self.logger.log(f"Processing {len(actions)} action(s)...")
        
        for i, action_data in enumerate(actions, 1):
            try:
                self.logger.log(f"\nAction {i}: {action_data}")
                
                action = action_data.get('action', '').lower()
                symbol = action_data.get('symbol', '')
                
                if not action or not symbol:
                    self.logger.log(f"  ⚠️ Skipping: missing action or symbol")
                    continue
                
                if action == 'open':
                    position_type = action_data.get('position_type', 'long').lower()
                    size = float(action_data.get('size', 0))
                    leverage = float(action_data.get('leverage', 1))
                    reason = action_data.get('reason', 'No reason provided')
                    
                    if size <= 0:
                        self.logger.log(f"  ⚠️ Skipping: invalid size {size}")
                        continue
                    
                    if symbol not in current_prices:
                        self.logger.log(f"  ⚠️ Skipping: {symbol} not in current prices")
                        continue
                    
                    self.logger.log(f"  📈 Opening {position_type.upper()} position: {symbol} ${size:.2f} "
                                  f"(Leverage: {leverage}x) - Reason: {reason}")
                    
                    position = self.simulator.open_position(
                        symbol=symbol,
                        position_type=position_type,
                        size=size,
                        current_price=current_prices[symbol],
                        leverage=leverage
                    )
                    
                    if position:
                        self.logger.log(f"  ✅ Position opened successfully")
                        self.logger.log_trade(self.simulator.trade_history[-1])
                    else:
                        self.logger.log(f"  ❌ Failed to open position")
                
                elif action == 'close':
                    positions_to_close = [
                        pos for pos in self.simulator.open_positions 
                        if pos.symbol == symbol
                    ]
                    
                    if not positions_to_close:
                        self.logger.log(f"  ⚠️ No open position found for {symbol}")
                        continue
                    
                    for position in positions_to_close:
                        reason = action_data.get('reason', 'No reason provided')
                        self.logger.log(f"  📉 Closing position: {symbol} - Reason: {reason}")
                        
                        self.simulator.close_position(position, current_prices[symbol])
                        self.logger.log(f"  ✅ Position closed successfully")
                        self.logger.log_trade(self.simulator.trade_history[-1])
                
                else:
                    self.logger.log(f"  ⚠️ Unknown action: {action}")
                
            except Exception as e:
                self.logger.log(f"  ❌ Error executing action: {e}")
                import traceback
                self.logger.log(traceback.format_exc())
    
    def run_iteration(self):
        """Run one iteration of the trading loop"""
        self.iteration_count += 1
        current_time = time.time()
        
        self.logger.log(f"\n--- Iteration {self.iteration_count} ---")
        
        # 1. Fetch current prices
        current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
        if not current_prices:
            self.logger.log("Failed to fetch prices, skipping iteration")
            return
        
        # Log current prices
        price_str = ", ".join([f"{s}: ${p:,.2f}" for s, p in current_prices.items()])
        self.logger.log(f"Current Prices: {price_str}")
        
        # 2. Fetch technical analysis data
        technical_analysis = {}
        for symbol in TRADING_PAIRS:
            klines = self.api.get_klines(symbol, interval='1h', limit=100)
            if klines:
                technical_analysis[symbol] = analyze_market(klines)
        
        # 3. Get portfolio statistics
        stats = self.simulator.get_statistics(current_prices)
        open_positions = self.simulator.get_open_positions_summary(current_prices)
        
        # 4. Update web dashboard
        closed_trades = [pos.to_dict() for pos in self.simulator.closed_positions]
        update_trading_data(current_prices, open_positions, stats, closed_trades)
        
        # Log periodic statistics
        if self.iteration_count % 5 == 0:
            self.logger.print_summary(stats, current_prices)
            self.logger.log_statistics(stats)
        
        # 5. Check if we should request LLM decision
        time_since_last = current_time - self.last_decision_time
        should_decide = self.agent.should_request_decision(
            current_prices, 
            self.last_prices,
            time_since_last,
            DECISION_INTERVAL
        )
        
        if should_decide:
            self.logger.log("\n=== Requesting LLM Decision ===")
            
            # Create detailed market prompt
            market_prompt = self.agent.create_detailed_market_prompt(
                current_prices,
                technical_analysis,
                stats,
                open_positions
            )
            
            # Get LLM decision
            max_position_size = min(stats['current_capital'] * 0.2, 200)
            decision = self.agent.make_decision(market_prompt, max_position_size)
            
            # Log decision
            summary = decision.get('summary', 'No summary')
            chain_of_thought = decision.get('chain_of_thought', {})
            actions = decision.get('actions', [])
            
            self.logger.log(f"\n🤖 LLM Summary: {summary}")
            self.logger.log(f"📊 Chain of Thought: {chain_of_thought}")
            self.logger.log(f"🎯 Actions: {len(actions)} proposed")
            
            # Update web dashboard with LLM conversation
            update_llm_conversation(summary, market_prompt, chain_of_thought, actions)
            
            # Execute actions
            self.execute_actions(actions, current_prices)
            
            self.last_decision_time = current_time
        
        # 6. Update last prices
        self.last_prices = current_prices.copy()
    
    def run(self, sleep_seconds: int = 30):
        """Run the trading bot"""
        self.running = True
        self.logger.log("=== Advanced Trading Bot Started ===")
        self.logger.log(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
        self.logger.log(f"Max Leverage: {MAX_LEVERAGE}x")
        self.logger.log(f"Decision Interval: {DECISION_INTERVAL}s")
        self.logger.log(f"Trading Pairs: {', '.join(TRADING_PAIRS)}")
        self.logger.log(f"Sleep between iterations: {sleep_seconds}s")
        self.logger.log(f"Web Dashboard: http://127.0.0.1:5000\n")
        
        try:
            while self.running:
                self.run_iteration()
                time.sleep(sleep_seconds)
        
        except KeyboardInterrupt:
            self.logger.log("\nKeyboard interrupt received")
        
        except Exception as e:
            self.logger.log(f"\nUnexpected error: {e}")
            import traceback
            self.logger.log(traceback.format_exc())
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.log("\n=== Shutting Down ===")
        
        # Close all positions
        current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
        if current_prices and self.simulator.open_positions:
            self.logger.log("Closing all open positions...")
            self.simulator.close_all_positions(current_prices)
            
            for trade in self.simulator.trade_history[-len(self.simulator.closed_positions):]:
                self.logger.log_trade(trade)
        
        # Final statistics
        if current_prices:
            self.logger.create_final_report(self.simulator, current_prices)
        
        self.logger.log("=== Trading Bot Stopped ===")


def run_bot_in_thread(bot: AdvancedTradingBot):
    """Run trading bot in a separate thread"""
    bot.run(sleep_seconds=30)


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════════════════════╗
║    Advanced LLM Crypto Trading Bot with Model Chat        ║
║                                                            ║
║  Web Dashboard: http://127.0.0.1:5000                     ║
║  - Left: Stats & Charts                                   ║
║  - Middle: Model Chat (QWEN3 MAX)                         ║
║  - Right: Positions & Trades                              ║
║                                                            ║
║  Press Ctrl+C in terminal to stop                         ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    from config import DASHSCOPE_API_KEY
    if not DASHSCOPE_API_KEY:
        print("\n⚠️  WARNING: DASHSCOPE_API_KEY not set!")
        print("LLM decisions will not work. Set API key in .env file.\n")
    
    # Create bot
    bot = AdvancedTradingBot()
    
    # Run bot in background thread
    bot_thread = threading.Thread(target=run_bot_in_thread, args=(bot,), daemon=True)
    bot_thread.start()
    
    # Run Flask server in main thread (use dashboard_with_chat template)
    print("\n🌐 Starting web dashboard on http://127.0.0.1:5000")
    print("📊 Open this URL in your browser to view the dashboard")
    print("🤖 Model Chat panel shows real-time LLM decision-making\n")
    
    try:
        # Run Flask server (will automatically use dashboard_with_chat.html if available)
        run_server(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        bot.running = False
        bot_thread.join(timeout=5)


if __name__ == "__main__":
    main()

