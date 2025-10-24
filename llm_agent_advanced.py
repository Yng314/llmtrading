"""
Advanced LLM-based trading agent with detailed market data and structured output
"""

import openai
from typing import Dict, List, Optional
import json
from datetime import datetime
from config import DASHSCOPE_API_KEY, LLM_MODEL, LLM_TEMPERATURE


class AdvancedTradingAgent:
    """Enhanced LLM-powered trading agent with structured communication"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DASHSCOPE_API_KEY
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        self.decision_count = 0
        self.start_time = datetime.now()
        self.last_decision = None
        
    def create_detailed_market_prompt(self, current_prices: Dict, technical_analysis: Dict,
                                     portfolio_stats: Dict, open_positions: List) -> str:
        """Create detailed market data prompt similar to the reference format"""
        
        elapsed_minutes = int((datetime.now() - self.start_time).total_seconds() / 60)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""It has been {elapsed_minutes} minutes since you started trading. The current time is {current_time} and you've been invoked {self.decision_count} times.

ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

CURRENT MARKET STATE FOR ALL COINS
"""
        
        # Add data for each coin
        for symbol in sorted(technical_analysis.keys()):
            analysis = technical_analysis[symbol]
            series = analysis.get('series', {})
            
            coin_name = symbol.replace('USDT', '')
            prompt += f"\n{'='*60}\nALL {coin_name} DATA\n{'='*60}\n"
            prompt += f"current_price = {analysis['current_price']:.2f}, "
            prompt += f"current_ema20 = {analysis['ema_20']:.3f}, "
            prompt += f"current_macd = {analysis['macd']['macd']:.3f}, "
            prompt += f"current_rsi_7 = {analysis['rsi_7']:.3f}\n\n"
            
            # Intraday series
            if series.get('prices'):
                prompt += "Intraday series (recent data, oldest → latest):\n\n"
                prompt += f"Prices: {[round(p, 2) for p in series['prices']]}\n\n"
                prompt += f"EMA-20: {[round(e, 3) for e in series['ema_20']]}\n\n"
                prompt += f"MACD: {[round(m, 3) for m in series['macd']]}\n\n"
                prompt += f"RSI (7-period): {[round(r, 3) for r in series['rsi_7']]}\n\n"
                prompt += f"RSI (14-period): {[round(r, 3) for r in series['rsi_14']]}\n\n"
            
            # Longer-term context
            prompt += "Longer-term context:\n"
            prompt += f"  20-Period EMA: {analysis['ema_20']:.3f} vs. 50-Period SMA: {analysis['sma_50']:.3f}\n"
            prompt += f"  Current Volume: {analysis['current_volume']:.2f} vs. Avg Volume: {analysis['avg_volume']:.2f}\n"
            prompt += f"  Trend: {analysis['trend']}\n"
            prompt += f"  RSI Signal: {analysis['rsi_signal']}\n"
            prompt += f"  Bollinger Bands: {analysis['bb_signal']}\n\n"
        
        # Account information
        prompt += f"\n{'='*60}\nYOUR ACCOUNT INFORMATION & PERFORMANCE\n{'='*60}\n"
        prompt += f"Current Total Return: {portfolio_stats['roi_percent']:.2f}%\n\n"
        prompt += f"Available Cash: ${portfolio_stats['current_capital']:.2f}\n\n"
        prompt += f"Current Account Value: ${portfolio_stats['total_value']:.2f}\n\n"
        
        if open_positions:
            prompt += "Current live positions & performance:\n"
            for pos in open_positions:
                prompt += f"  - {pos['symbol']}: "
                prompt += f"{pos['type'].upper()} ${pos['size']:.2f} @ ${pos['entry_price']:.2f}, "
                prompt += f"Current: ${pos['current_price']:.2f}, "
                prompt += f"P&L: ${pos['current_pnl']:+.2f} ({pos['pnl_percent']:+.2f}%), "
                prompt += f"Leverage: {pos['leverage']}x\n"
        else:
            prompt += "Current live positions: None\n"
        
        prompt += f"\nTotal Trades: {portfolio_stats['total_trades']}\n"
        prompt += f"Winning Trades: {portfolio_stats['winning_trades']}\n"
        prompt += f"Losing Trades: {portfolio_stats['losing_trades']}\n"
        prompt += f"Win Rate: {portfolio_stats['win_rate']:.2f}%\n"
        
        return prompt
    
    def make_decision(self, market_prompt: str, max_position_size: float) -> Dict:
        """
        Make trading decision with structured output
        
        Returns:
            {
                'summary': 'Natural language summary',
                'chain_of_thought': {...},
                'actions': [...]
            }
        """
        self.decision_count += 1
        
        system_prompt = """You are an AGGRESSIVE cryptocurrency trader with deep knowledge of technical analysis, market dynamics, and leveraged trading.

Your task is to analyze the provided market data and make ACTIVE trading decisions. You should be looking for opportunities to profit from BOTH uptrends and downtrends.

RESPONSE FORMAT:
You must respond with a JSON object containing THREE sections:

1. "summary": A brief natural language summary of your analysis (1-2 sentences)

2. "chain_of_thought": A structured reasoning process with:
   - For each coin you're considering, provide:
     * "signal": "buy_long" | "buy_short" | "hold" | "close"
     * "confidence": 0.0 to 1.0
     * "justification": Brief reasoning
     * "target_price": If opening, your profit target
     * "stop_loss": If opening, your stop loss level
     * "leverage": Recommended leverage (5-20)
     * "risk_usd": Amount willing to risk

3. "actions": Array of concrete actions to take:
   [{
     "action": "open" | "close",
     "symbol": "BTCUSDT",
     "position_type": "long" | "short",
     "size": 100.0,
     "leverage": 10.0,
     "reason": "Brief reason"
   }]

TRADING GUIDELINES:
- BE AGGRESSIVE: Look for opportunities to profit from market movements in BOTH directions
- LONG positions: Open when trend is bullish (RSI rising, MACD positive, price > EMA-20)
- SHORT positions: Open when trend is bearish (RSI falling, MACD negative, price < EMA-20)
- RSI < 30 = oversold (STRONG BUY LONG signal)
- RSI > 70 = overbought (STRONG SELL SHORT signal)
- MACD crossing up = buy long, MACD crossing down = buy short
- Price above EMA-20 = consider long, below EMA-20 = consider short
- Volume analysis: high volume confirms the move

LEVERAGE STRATEGY:
- Use 10-15x leverage for moderate conviction trades
- Use 15-20x leverage for high conviction trades (confidence > 0.8)
- Minimum leverage should be 5x (we want to maximize returns)
- Higher leverage = higher profits (but also higher risk, so be selective)

POSITION SIZING:
- Use 15-25% of available capital per trade
- Can hold multiple positions across different coins
- Diversify between long and short positions

RISK MANAGEMENT:
- Close losing positions if P&L < -8%
- Take profits when positions gain +12-15%
- Trail stop losses on profitable trades

ACTIVE TRADING:
- Don't just hold - actively look for new opportunities
- If market is choppy, use shorter timeframes
- When in doubt between long/short, choose based on momentum
- Empty actions array should be RARE - there's usually an opportunity

IMPORTANT: 
- You MUST consider BOTH long AND short opportunities for each coin
- Respond ONLY with valid JSON, no additional text
- Be decisive and aggressive - we're here to make money!"""

        user_prompt = market_prompt + f"\n\nMax position size available: ${max_position_size:.2f}\n\nProvide your analysis and trading decision in JSON format."
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(content)
            
            # Validate structure
            if not isinstance(decision, dict):
                raise ValueError("Response is not a dictionary")
            
            # Ensure all required fields
            decision.setdefault('summary', 'No summary provided')
            decision.setdefault('chain_of_thought', {})
            decision.setdefault('actions', [])
            
            self.last_decision = {
                'timestamp': datetime.now(),
                'decision': decision,
                'prompt': market_prompt
            }
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response as JSON: {e}")
            return {
                'summary': 'Error: Could not parse LLM response',
                'chain_of_thought': {},
                'actions': []
            }
        except Exception as e:
            print(f"Error getting LLM decision: {e}")
            return {
                'summary': f'Error: {str(e)}',
                'chain_of_thought': {},
                'actions': []
            }
    
    def should_request_decision(self, current_prices: Dict, last_prices: Dict,
                               time_since_last: float, decision_interval: float,
                               open_positions: List = None) -> tuple:
        """
        Multi-level intelligent wake-up mechanism
        
        Returns:
            (should_decide: bool, reason: str)
        """
        from config import (VOLATILITY_THRESHOLD, EMERGENCY_THRESHOLD, 
                          POSITION_RISK_THRESHOLD, MARKET_VOLATILITY_COINS, COOLDOWN_SECONDS)
        
        # ===== Level 0: Cooldown check =====
        # Prevent too frequent LLM calls
        if time_since_last < COOLDOWN_SECONDS:
            return False, "cooldown_active"
        
        # ===== Level 1: Scheduled trigger (lowest priority) =====
        if time_since_last >= decision_interval:
            return True, "scheduled_interval"
        
        # ===== Level 2: Market volatility triggers =====
        if not last_prices:
            return True, "first_run"
        
        # 2a. Single coin emergency volatility (>5%)
        for symbol, current_price in current_prices.items():
            if symbol in last_prices:
                change_pct = abs(current_price - last_prices[symbol]) / last_prices[symbol]
                if change_pct > EMERGENCY_THRESHOLD:
                    return True, f"emergency_volatility_{symbol}_{change_pct:.1%}"
        
        # 2b. Market-wide volatility (multiple coins >2% volatility)
        volatile_coins = []
        for symbol, current_price in current_prices.items():
            if symbol in last_prices:
                change_pct = abs(current_price - last_prices[symbol]) / last_prices[symbol]
                if change_pct > VOLATILITY_THRESHOLD:
                    volatile_coins.append((symbol, change_pct))
        
        if len(volatile_coins) >= MARKET_VOLATILITY_COINS:
            coins_str = ', '.join([f"{s}:{c:.1%}" for s, c in volatile_coins[:3]])
            return True, f"market_volatility_{len(volatile_coins)}_coins_({coins_str})"
        
        # ===== Level 3: Position risk triggers (highest priority) =====
        if open_positions:
            for pos in open_positions:
                symbol = pos['symbol']
                if symbol not in current_prices or symbol not in last_prices:
                    continue
                
                current_price = current_prices[symbol]
                last_price = last_prices[symbol]
                change_pct = (current_price - last_price) / last_price
                
                # Check if price hit LLM-defined targets
                if 'target_price' in pos and pos['target_price']:
                    if pos['type'] == 'long' and current_price >= pos['target_price']:
                        return True, f"target_reached_{symbol}_${current_price:.2f}"
                    elif pos['type'] == 'short' and current_price <= pos['target_price']:
                        return True, f"target_reached_{symbol}_${current_price:.2f}"
                
                if 'stop_loss' in pos and pos['stop_loss']:
                    if pos['type'] == 'long' and current_price <= pos['stop_loss']:
                        return True, f"stop_loss_hit_{symbol}_${current_price:.2f}"
                    elif pos['type'] == 'short' and current_price >= pos['stop_loss']:
                        return True, f"stop_loss_hit_{symbol}_${current_price:.2f}"
                
                # Position risk: price moving against position
                if pos['type'] == 'long' and change_pct < -POSITION_RISK_THRESHOLD:
                    return True, f"position_risk_long_{symbol}_{change_pct:.1%}"
                elif pos['type'] == 'short' and change_pct > POSITION_RISK_THRESHOLD:
                    return True, f"position_risk_short_{symbol}_{change_pct:.1%}"
        
        # ===== Level 4: Time decay trigger =====
        # Lower threshold if significant time passed
        if time_since_last > decision_interval * 0.6:  # After 60% of interval
            decay_threshold = VOLATILITY_THRESHOLD * 0.75  # Lower to 1.5%
            for symbol, current_price in current_prices.items():
                if symbol in last_prices:
                    change_pct = abs(current_price - last_prices[symbol]) / last_prices[symbol]
                    if change_pct > decay_threshold:
                        return True, f"decay_trigger_{symbol}_{change_pct:.1%}"
        
        return False, "no_trigger"


if __name__ == "__main__":
    # Test
    import os
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("Set DASHSCOPE_API_KEY to test")
    else:
        agent = AdvancedTradingAgent()
        
        mock_prompt = """It has been 5 minutes since you started trading.

CURRENT MARKET STATE FOR ALL COINS
============================================================
ALL BTC DATA
============================================================
current_price = 110000.00, current_ema20 = 109800.000, current_macd = 150.000, current_rsi_7 = 65.000

Intraday series (recent data, oldest → latest):

Prices: [109000, 109500, 110000, 110500, 110000]

EMA-20: [109500, 109600, 109700, 109750, 109800]

MACD: [100, 120, 140, 150, 150]

RSI (7-period): [60, 62, 65, 68, 65]

YOUR ACCOUNT INFORMATION & PERFORMANCE
============================================================
Current Total Return: 0.00%
Available Cash: $1000.00
Current Account Value: $1000.00
Current live positions: None
"""
        
        decision = agent.make_decision(mock_prompt, 200)
        print(json.dumps(decision, indent=2))

