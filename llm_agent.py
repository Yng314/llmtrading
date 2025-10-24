"""
LLM-based trading decision agent using Qwen3 Max
"""

import openai
from typing import Dict, List, Optional
import json
from config import DASHSCOPE_API_KEY, LLM_MODEL, LLM_TEMPERATURE


class TradingAgent:
    """LLM-powered trading decision maker"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DASHSCOPE_API_KEY
        
        # Configure OpenAI client for DashScope (Qwen)
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        self.conversation_history = []
        self.decision_count = 0
        
    def create_market_summary(self, market_data: Dict, technical_analysis: Dict, 
                            portfolio_stats: Dict, open_positions: List[Dict]) -> str:
        """
        Create a concise market summary for LLM input
        
        Args:
            market_data: Current market prices and stats
            technical_analysis: Technical indicators for each symbol
            portfolio_stats: Current portfolio statistics
            open_positions: List of open positions
            
        Returns:
            Formatted market summary string
        """
        summary = "=== MARKET SUMMARY ===\n\n"
        
        # Portfolio status
        summary += f"Portfolio Status:\n"
        summary += f"- Total Value: ${portfolio_stats['total_value']:.2f}\n"
        summary += f"- Available Capital: ${portfolio_stats['current_capital']:.2f}\n"
        summary += f"- Total P&L: ${portfolio_stats['total_pnl']:.2f} ({portfolio_stats['roi_percent']:.2f}%)\n"
        summary += f"- Open Positions: {portfolio_stats['open_positions']}\n"
        summary += f"- Win Rate: {portfolio_stats['win_rate']:.2f}%\n\n"
        
        # Open positions
        if open_positions:
            summary += "Current Positions:\n"
            for pos in open_positions:
                summary += f"- {pos['symbol']} {pos['type'].upper()}: "
                summary += f"${pos['size']:.2f} @ ${pos['entry_price']:.2f} "
                summary += f"(Leverage: {pos['leverage']}x, "
                summary += f"Current P&L: ${pos['current_pnl']:.2f}, {pos['pnl_percent']:.2f}%)\n"
            summary += "\n"
        
        # Market analysis for each symbol
        summary += "Market Analysis:\n"
        for symbol, analysis in technical_analysis.items():
            summary += f"\n{symbol}:\n"
            summary += f"  Price: ${analysis['current_price']:.2f} "
            summary += f"({analysis['price_change_percent']:+.2f}% change)\n"
            summary += f"  Trend: {analysis['trend']}\n"
            summary += f"  RSI: {analysis['rsi']:.2f} ({analysis['rsi_signal']})\n"
            summary += f"  Bollinger Bands: {analysis['bb_signal']}\n"
            summary += f"  Volume: {analysis['volume_trend']}\n"
            summary += f"  MACD: {analysis['macd']['macd']:.2f} "
            summary += f"(Signal: {analysis['macd']['signal']:.2f})\n"
        
        return summary
    
    def make_decision(self, market_summary: str, max_position_size: float) -> Dict:
        """
        Ask LLM to make trading decision based on market data
        
        Args:
            market_summary: Formatted market summary
            max_position_size: Maximum size for new positions
            
        Returns:
            Dictionary with trading decisions
        """
        self.decision_count += 1
        
        system_prompt = """You are an expert cryptocurrency trading advisor with deep knowledge of:
- Technical analysis (RSI, MACD, Bollinger Bands, moving averages)
- Market trends and momentum
- Risk management and position sizing
- Economic principles affecting crypto markets

Your goal is to maximize returns while managing risk. Analyze the provided market data and make trading decisions.

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{
    "analysis": "Brief market analysis (2-3 sentences)",
    "actions": [
        {
            "action": "open|close",
            "symbol": "BTCUSDT",
            "position_type": "long|short",
            "size": 100.0,
            "leverage": 2.0,
            "reason": "Brief reason for this action"
        }
    ],
    "risk_assessment": "Brief risk assessment"
}

Guidelines:
- Consider technical indicators (RSI overbought/oversold, trend direction, MACD signals)
- Use leverage cautiously (1-3x for safer trades, higher only with strong conviction)
- Don't risk more than 10-20% of available capital per trade
- Close losing positions if P&L drops below -10%
- Take profits when positions show +15-20% gains
- Consider market volatility and volume trends
- If no good opportunities, return empty "actions" array
"""

        user_prompt = f"{market_summary}\n\nMax position size: ${max_position_size:.2f}\n\nProvide your trading decision in JSON format."
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(content)
            
            # Validate decision structure
            if not isinstance(decision, dict) or 'actions' not in decision:
                print("Invalid decision format from LLM")
                return {'analysis': 'Error parsing decision', 'actions': [], 'risk_assessment': 'N/A'}
            
            print(f"\n=== LLM DECISION #{self.decision_count} ===")
            print(f"Analysis: {decision.get('analysis', 'N/A')}")
            print(f"Risk Assessment: {decision.get('risk_assessment', 'N/A')}")
            print(f"Actions: {len(decision.get('actions', []))} proposed")
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response as JSON: {e}")
            print(f"Response content: {content}")
            return {'analysis': 'JSON parse error', 'actions': [], 'risk_assessment': 'N/A'}
        except Exception as e:
            print(f"Error getting LLM decision: {e}")
            return {'analysis': 'Error', 'actions': [], 'risk_assessment': 'N/A'}
    
    def should_request_decision(self, market_data: Dict, last_prices: Dict, 
                               time_since_last_decision: float, decision_interval: float) -> bool:
        """
        Determine if we should request a new LLM decision (token optimization)
        
        Args:
            market_data: Current market data
            last_prices: Previous prices
            time_since_last_decision: Seconds since last decision
            decision_interval: Minimum seconds between decisions
            
        Returns:
            True if should request decision, False otherwise
        """
        # Always decide at regular intervals
        if time_since_last_decision >= decision_interval:
            return True
        
        # Early return if no price history
        if not last_prices:
            return True
        
        # Check for significant price movements (volatility trigger)
        for symbol, current_price in market_data.items():
            if symbol in last_prices:
                price_change = abs(current_price - last_prices[symbol]) / last_prices[symbol]
                if price_change > 0.03:  # 3% change triggers decision
                    print(f"Volatility trigger: {symbol} changed by {price_change*100:.2f}%")
                    return True
        
        return False


if __name__ == "__main__":
    # Test the agent (requires API key)
    import os
    
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("Please set DASHSCOPE_API_KEY environment variable to test")
    else:
        agent = TradingAgent()
        
        # Mock market summary
        mock_summary = """=== MARKET SUMMARY ===

Portfolio Status:
- Total Value: $1000.00
- Available Capital: $1000.00
- Total P&L: $0.00 (0.00%)
- Open Positions: 0
- Win Rate: 0.00%

Market Analysis:

BTCUSDT:
  Price: $67500.00 (+2.50% change)
  Trend: strong_uptrend
  RSI: 65.00 (neutral)
  Bollinger Bands: neutral
  Volume: high
  MACD: 150.00 (Signal: 140.00)
"""
        
        decision = agent.make_decision(mock_summary, 200.0)
        print("\n=== Decision Result ===")
        print(json.dumps(decision, indent=2))

