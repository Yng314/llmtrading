"""
Advanced trading bot with detailed LLM communication and Model Chat display
虚拟交易版本（模拟器）
"""

import time
from datetime import datetime
import signal
import sys
import argparse
from typing import Dict
import threading

# 添加父目录到路径
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from data_persistence import DataPersistence


class AdvancedTradingBot:
    """Advanced trading bot with structured LLM communication"""
    
    def __init__(self, load_saved_state: bool = True):
        self.persistence = DataPersistence()
        self.api = CryptoAPI()
        self.agent = AdvancedTradingAgent()
        self.logger = TradingLogger()
        
        self.running = False
        self.last_decision_time = 0
        self.last_prices = {}
        self.iteration_count = 0
        
        # Price and value history for charts
        self.value_history = []
        self.price_history = {}
        
        # Try to load saved state
        if load_saved_state:
            saved_state = self.persistence.load_state()
            if saved_state:
                self.simulator = self.persistence.restore_simulator(saved_state)
                self.iteration_count = saved_state['iteration_count']
                self.value_history = saved_state.get('value_history', [])
                self.price_history = saved_state.get('price_history', {})
                self.logger.log("✅ Resumed from saved state")
            else:
                self.simulator = TradingSimulator(INITIAL_CAPITAL, MAX_LEVERAGE)
                self.logger.log("ℹ️  Starting fresh (no saved state)")
        else:
            self.simulator = TradingSimulator(INITIAL_CAPITAL, MAX_LEVERAGE)
            self.logger.log("🆕 Starting fresh (restart mode)")
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        if not self.running:
            sys.exit(0)
        print("\n\nReceived shutdown signal. Saving state and exiting...")
        self.running = False
        # Save state before exit
        self._save_state()
    
    def _save_state(self):
        """Save current state to disk"""
        try:
            self.persistence.save_state(
                simulator=self.simulator,
                value_history=self.value_history,
                price_history=self.price_history,
                iteration_count=self.iteration_count
            )
        except Exception as e:
            print(f"❌ Error saving state: {e}")
    
    def execute_actions(self, actions: list, current_prices: Dict[str, float], chain_of_thought: Dict = None):
        """Execute trading actions from LLM decision"""
        if not actions:
            self.logger.log("No actions to execute")
            return

        cot = chain_of_thought or {}
        
        self.logger.log(f"\nExecuting {len(actions)} actions:")
        
        for i, action_data in enumerate(actions, 1):
            try:
                action = action_data.get('action', '').lower()
                symbol = action_data.get('symbol', '')
                reason = action_data.get('reason', '')
                
                if not symbol or symbol not in current_prices:
                    self.logger.log(f"  ⚠️  Action {i}: Invalid symbol '{symbol}' - Skipping")
                    continue
                
                if action == 'open':
                    position_type = action_data.get('position_type', '').lower()
                    size = float(action_data.get('size', 0))
                    leverage = float(action_data.get('leverage', 1))
                    
                    if size <= 0:
                        self.logger.log(f"  ⚠️  Action {i}: Invalid size {size} - Skipping")
                        continue
                    
                    # Extract target_price and stop_loss from chain of thought
                    target_price = None
                    stop_loss = None
                    if symbol in cot:
                        target_price = cot[symbol].get('target_price')
                        stop_loss = cot[symbol].get('stop_loss')
                    
                    target_str = f", Target: ${target_price:.2f}" if target_price else ""
                    stop_str = f", Stop Loss: ${stop_loss:.2f}" if stop_loss else ""
                    
                    self.logger.log(f"  📈 Opening {position_type.upper()} position: {symbol} ${size:.2f} "
                                  f"(Leverage: {leverage}x){target_str}{stop_str} - Reason: {reason}")
                    
                    position = self.simulator.open_position(
                        symbol=symbol,
                        position_type=position_type,
                        size=size,
                        current_price=current_prices[symbol],
                        leverage=leverage,
                        target_price=target_price,
                        stop_loss=stop_loss
                    )
                    
                    if position:
                        self.logger.log(f"  ✅ Position opened successfully")
                        self.logger.log_trade(self.simulator.trade_history[-1])
                    else:
                        self.logger.log(f"  ❌ Failed to open position")
                        # Log why it failed
                        available = self.simulator.get_available_capital()
                        margin_needed = size / leverage
                        self.logger.log(f"     Available capital: ${available:.2f}")
                        self.logger.log(f"     Margin needed: ${margin_needed:.2f}")
                        if margin_needed > available:
                            self.logger.log(f"     ⚠️  Insufficient capital (need ${margin_needed - available:.2f} more)")
                
                elif action == 'close':
                    positions_to_close = [
                        pos for pos in self.simulator.open_positions 
                        if pos.symbol == symbol
                    ]
                    
                    if not positions_to_close:
                        self.logger.log(f"  ⚠️  Action {i}: No open position for {symbol} - Skipping")
                        continue
                    
                    for pos in positions_to_close:
                        self.logger.log(f"  📉 Closing {pos.position_type.value.upper()} position: {symbol} - Reason: {reason}")
                        
                        pnl = self.simulator.close_position(pos, current_prices[symbol])
                        self.logger.log(f"  ✅ Position closed. P&L: ${pnl:+.2f}")
                        self.logger.log_trade(self.simulator.trade_history[-1])
                
                elif action == 'hold':
                    self.logger.log(f"  ⏸️  Hold: {symbol} - {reason}")
                
                else:
                    self.logger.log(f"  ⚠️  Action {i}: Unknown action '{action}' - Skipping")
            
            except Exception as e:
                self.logger.log(f"  ❌ Action {i}: Error executing action: {e}")
                import traceback
                traceback.print_exc()
    
    def run_iteration(self):
        """Run one iteration of the trading loop"""
        self.iteration_count += 1
        current_time = time.time()
        
        self.logger.log(f"\n--- Iteration {self.iteration_count} ---")
        
        # 1. Get current prices
        current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
        if not current_prices:
            self.logger.log("❌ Failed to fetch prices")
            return
        
        price_str = ", ".join([f"{s}: ${p:,.2f}" for s, p in current_prices.items()])
        self.logger.log(f"Current Prices: {price_str}")
        
        # 2. Get trading statistics
        stats = self.simulator.get_statistics(current_prices)
        open_positions = self.simulator.get_open_positions_summary(current_prices)
        
        # 3. Save state periodically
        if self.iteration_count % 10 == 0:
            self._save_state()
        
        # 4. Update history data for charts
        timestamp = datetime.now().isoformat()
        
        # Update value history
        self.value_history.append({
            'timestamp': timestamp,
            'value': stats['total_value']
        })
        
        # Update price history
        for symbol, price in current_prices.items():
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append({
                'timestamp': timestamp,
                'price': price
            })
        
        # 5. Update web dashboard (pass complete history)
        closed_trades = [pos.to_dict() for pos in self.simulator.closed_positions]
        update_trading_data(current_prices, open_positions, stats, closed_trades,
                          self.value_history, self.price_history)
        
        # 6. Check if we should request LLM decision
        time_since_last = current_time - self.last_decision_time
        should_decide, trigger_reason = self.agent.should_request_decision(
            current_prices, 
            self.last_prices,
            time_since_last,
            DECISION_INTERVAL,
            open_positions
        )
        
        if should_decide:
            self.logger.log(f"\n=== Requesting LLM Decision (Trigger: {trigger_reason}) ===")
            
            # Get market analysis for all pairs
            market_data = {}
            for symbol in TRADING_PAIRS:
                klines = self.api.get_klines(symbol, interval='15m', limit=100)
                if klines:
                    market_data[symbol] = analyze_market(klines)
            
            # Request LLM decision
            decision = self.agent.make_decision(
                current_prices=current_prices,
                open_positions=open_positions,
                account_balance=stats['current_capital'],
                market_data=market_data
            )
            
            if decision:
                # Log LLM conversation for web display
                self.logger.log(f"🤖 LLM Summary: {decision['summary']}")
                update_llm_conversation(decision)
                
                # Execute actions
                self.execute_actions(
                    decision['actions'], 
                    current_prices,
                    decision.get('chain_of_thought')
                )
            
            self.last_decision_time = current_time
        
        # 7. Update last prices
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
        
        # Initialize web dashboard with loaded state
        # This ensures the dashboard shows data immediately on startup
        try:
            current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
            if current_prices:
                stats = self.simulator.get_statistics(current_prices)
                open_positions = self.simulator.get_open_positions_summary(current_prices)
                closed_trades = [pos.to_dict() for pos in self.simulator.closed_positions]
                
                # Send initial data to web server (including loaded history)
                update_trading_data(current_prices, open_positions, stats, closed_trades,
                                  self.value_history, self.price_history)
                self.logger.log("✅ Initial state sent to web dashboard")
        except Exception as e:
            self.logger.log(f"⚠️  Failed to initialize web dashboard: {e}")
        
        try:
            while self.running:
                self.run_iteration()
                time.sleep(sleep_seconds)
        
        except KeyboardInterrupt:
            self.logger.log("\nKeyboard interrupt received")
        
        except Exception as e:
            self.logger.log(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self.logger.log("\n=== Bot Shutting Down ===")
        
        # Final save
        self._save_state()
        
        # Close all positions if requested
        # current_prices = self.api.get_multiple_prices(TRADING_PAIRS)
        # if current_prices:
        #     self.simulator.close_all_positions(current_prices)
        
        self.logger.log("Goodbye!")
        self.running = False


def run_bot_in_thread(bot: AdvancedTradingBot):
    """Run trading bot in a separate thread"""
    bot.run(sleep_seconds=10)


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Advanced LLM Crypto Trading Bot (Simulator)')
    parser.add_argument('--restart', action='store_true', 
                       help='Start fresh, ignoring any saved state')
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════════════════════════╗
║    Advanced LLM Crypto Trading Bot (模拟器版本)            ║
║                                                            ║
║  Web Dashboard: http://127.0.0.1:5000                     ║
║  - Left: Stats & Charts                                   ║
║  - Middle: Model Chat (QWEN3 MAX)                         ║
║  - Right: Positions & Trades                              ║
║                                                            ║
║  Press Ctrl+C in terminal to stop                         ║
║                                                            ║
║  Options:                                                  ║
║    --restart    Start fresh, clear saved state            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    from config import DASHSCOPE_API_KEY
    if not DASHSCOPE_API_KEY:
        print("\n⚠️  WARNING: DASHSCOPE_API_KEY not set!")
        print("LLM decisions will not work. Set API key in .env file.\n")
    
    # Delete saved state if restart flag is set
    if args.restart:
        print("🔄 Restart mode: Clearing saved state...\n")
        DataPersistence().delete_state()
    
    # Create bot (will load saved state if available and not in restart mode)
    bot = AdvancedTradingBot(load_saved_state=not args.restart)
    
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

